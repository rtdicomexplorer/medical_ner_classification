import os
import sys
import json
import torch
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
# Add project root to sys.path if needed
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.text_extractor import extract_text 
from scripts.utils import generate_ner_data, init_tesseract, replace_entities_with_labels, np_encoder

from scripts.postprocess import postprocess_entities  # Your custom postprocessing
from scripts.ner_to_fhir import map_ner_to_fhir    # Your mapping from NER to FHIR
from scripts.config import ID2LABEL,LABEL2ID
MODEL_PATH = "./models/gbert-base"
OUTPUT_DIR = "output"
PREDICTIONS_DIR ="predictions"
class NERModel:
    def __init__(self):
        self.pipeline = None
        self.tokenizer = None  # Add this line

    def load(self):
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        model = AutoModelForTokenClassification.from_pretrained(MODEL_PATH)

        model.config.id2label = ID2LABEL
        model.config.label2id = LABEL2ID

        self.pipeline = pipeline(
            "ner",
            model=model,
            tokenizer=self.tokenizer,
            aggregation_strategy="first",
            device=0 if torch.cuda.is_available() else -1
        )
        print(f"Loaded model {MODEL_PATH}")

    def predict(self, text, max_chars=1500):
        if not self.pipeline:
            raise RuntimeError("Model not loaded.")             
        if len(text) <= max_chars:
            print(f"Simple prediction {len(text)} ")
            return self.pipeline(text)
        else:
            print(f"Long text prediction {len(text)} ")
            return self.__predict_long_text(text, max_chars=max_chars)
    

    def __predict_long_text(self, text, max_chars=1500):
        if not self.pipeline:
            raise RuntimeError("Model not loaded.")

        chunks = smart_chunk_text(text, max_chars=max_chars)

        all_entities = []
        offset = 0

        for chunk in chunks:
            entities = self.pipeline(chunk)

            for entity in entities:
                # Adjust start and end character positions to global text
                entity["start"] += offset
                entity["end"] += offset

            all_entities.extend(entities)

            offset += len(chunk)  # Move offset for next chunk

        return all_entities


    def is_ready(self):
        return self.pipeline is not None

def smart_chunk_text(text, max_chars=1500):
    """
    Splits text into pieces of roughly max_chars.
    """

    return __smart_chunk_text(text=text, max_chars=max_chars)

def __smart_chunk_text(text, max_chars=1500):
    chunks = []
    elements = text.splitlines(keepends=True)  # Keeps '\n' in each element!
    chunk = ''
    
    for element in elements:
        if len(chunk) + len(element) <= max_chars:
            chunk += element
        else:
            chunks.append(chunk)
            chunk = element  # Start new chunk with this line

    if chunk:
        chunks.append(chunk)  # Add the last chunk

    print(len(''.join(chunks)), len(text))  # Should now match exactly
    return chunks

ner_model = NERModel()

init_tesseract()

def __save_entity_comparison_html(predictions, post_predictions, filename="ner_comparison.html"):
    from pathlib import Path
    import html

    # Build lookups by span
    raw_by_span = {(e["start"], e["end"]): e for e in predictions}
    post_by_span = {(e["start"], e["end"]): e for e in post_predictions}
    all_spans = sorted(set(raw_by_span.keys()).union(post_by_span.keys()))

    rows = ""
    for span in all_spans:
        raw = raw_by_span.get(span)
        post = post_by_span.get(span)

        # Prepare fields with safe defaults
        entity_type = html.escape(raw["entity_group"] if raw else post["entity_group"])
        raw_word = html.escape(raw["word"]) if raw else "(missing)"
        post_word = html.escape(post["word"]) if post else "(missing)"
        raw_score = f'{raw["score"]:.3f}' if raw else "-"
        post_score = f'{post["score"]:.3f}' if post else "-"
        span_str = f'{span[0]}, {span[1]}'

        # Detect changes
        row_class = ""
        if not raw:
            row_class = "added"
        elif not post:
            row_class = "removed"
        elif raw["word"] != post["word"] or raw["entity_group"] != post["entity_group"]:
            row_class = "changed"

        rows += (
            f"<tr class='{row_class}'>"
            f"<td>{entity_type}</td>"
            f"<td>{raw_word}</td>"
            f"<td>{post_word}</td>"
            f"<td>{raw_score}</td>"
            f"<td>{post_score}</td>"
            f"<td>{span_str}</td>"
            f"</tr>\n"
        )

    html_content = f"""
                    <!DOCTYPE html>
                    <html lang="de">
                    <head>
                        <meta charset="UTF-8">
                        <title>Compare entities (Merged View)</title>
                        <style>
                            body {{
                                font-family: Arial, sans-serif;
                                margin: 20px;
                                background-color: #f9f9f9;
                                color: #333;
                            }}
                            h1 {{
                                text-align: center;
                                margin-bottom: 30px;
                            }}
                            table {{
                                border-collapse: collapse;
                                width: 100%;
                            }}
                            th, td {{
                                border: 1px solid #ccc;
                                padding: 8px 12px;
                                text-align: left;
                                white-space: nowrap;
                            }}
                            th {{
                                background-color: #eaeaea;
                                position: sticky;
                                top: 0;
                            }}
                            tr:hover {{
                                background-color: #f1f1f1;
                            }}
                            .changed {{
                                background-color: #ffe0e0;
                                font-weight: bold;
                            }}
                            .added {{
                                background-color: #e0ffe0;
                                font-style: italic;
                            }}
                            .removed {{
                                background-color: #fce5cd;
                                font-style: italic;
                            }}
                        </style>
                    </head>
                    <body>
                        <h1>Compare NER-Entities (RAW vs. Postpprocessing)</h1>
                        <table>
                            <thead>
                                <tr>
                                    <th>Typ</th>
                                    <th>Entity (Raw)</th>
                                    <th>Entity (Post)</th>
                                    <th>Score (Raw)</th>
                                    <th>Score (Post)</th>
                                    <th>Span</th>
                                </tr>
                            </thead>
                            <tbody>
                                {rows}
                            </tbody>
                        </table>
                    </body>
                    </html>
                    """
    Path(filename).write_text(html_content, encoding="utf-8")



def __save_predictions(predictions, file_name):
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(predictions, f, indent=2, ensure_ascii=False)
    


def __execute_predictions(text):
    # MODEL_PATH = 'deepset/gbert-base'
    if not  ner_model.is_ready():
        ner_model.load()
    return ner_model.predict(text)



def main(file_path,post_process_predictions, save_as_template):

    _, report_file_name = os.path.split(file_path)
    
    report_file_name, _ = os.path.splitext(report_file_name) 
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(PREDICTIONS_DIR, exist_ok=True)
    
    print(f"step1 - Extracting text from {file_path} ...")
    text = extract_text(file_path)
    print(f"step2 - Executing prediction ...")
    predictions = __execute_predictions(text)
    print(f"step3 - Generating ner data {file_path} ...")
    ner_data = generate_ner_data(text, predictions)
    dataset = []   
    dataset.append(ner_data)


    # for ent in predictions:
    #     entity_type = ent.get("entity_group", ent.get("entity"))
    #     print(f"Entity: '{ent['word']}'  |  Type: {entity_type}  |  Score: {ent['score']:.3f}")
    

    
    #postprocess the entities to make them clean...to be tested and updated, not called via WEB
    if post_process_predictions:# just for testing
        post_predictions = postprocess_entities(predictions)
        post_preditctions_file = os.path.join(PREDICTIONS_DIR, f"postprediction_{report_file_name}.json")
        __save_predictions(post_predictions,post_preditctions_file)
        print(f"✅ Post Predictions saved to {post_preditctions_file}")

        #saving compare between prediction and post_predictions    
        output_html = os.path.join(OUTPUT_DIR, f"compare_postprocessing_{report_file_name}.html")  
        if os.path.exists(output_html):
            os.remove(output_html)
        __save_entity_comparison_html(predictions, post_predictions,output_html)
        print(f"✅ HTML merged comparison saved to {output_html}")
    else:
        preditctions_file = os.path.join(PREDICTIONS_DIR, f"prediction_{report_file_name}.json")
        __save_predictions(predictions,preditctions_file)
        print(f"✅ Predictions saved to {preditctions_file}")

        
    #saving the predictions as ner data in bio format
    output_ner_file = os.path.join(OUTPUT_DIR,f"ner_{report_file_name}.json")
    with open(output_ner_file, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Ner data as bio format saved {output_ner_file}")

    if save_as_template: 
        #the idea is to use the report as new template    
        text_as_template = replace_entities_with_labels(text,predictions)
        #saving the predictions as txt for a new template
        output_text_template =  os.path.join(OUTPUT_DIR,f"template_{report_file_name}.txt")
        with open(output_text_template, "w", encoding="utf-8") as f:
            f.write(text_as_template)
        print(f"✅ Prediction as ttxt report for template saved {output_text_template}")

    print(f"All result files have been saved in {OUTPUT_DIR}")


def main_multiple(folder_path):

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(PREDICTIONS_DIR, exist_ok=True)

    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    print(f"step0 - Reading files from {folder_path}. Found {len(files)} files.")
    ner_dataset = [] 
    prediction_dataset=[]
    for file_name in tqdm(files, desc="Processing files"):
        full_path = os.path.join(folder_path, file_name)
        text = extract_text(full_path)
        predictions = __execute_predictions(text)
        prediction_dataset.append(predictions)
        ner_data = generate_ner_data(text, predictions)
        ner_dataset.append(ner_data)
        
    #saving the predictions as ner data in bio format
    output_ner_file = os.path.join(OUTPUT_DIR,f"ner_predictions.json")
    with open(output_ner_file, "w", encoding="utf-8") as f:
        json.dump(ner_dataset, f, indent=2, ensure_ascii=False)
    print(f"✅ Ner data as bio format saved {output_ner_file}")
    
    output_prediction_file = os.path.join(PREDICTIONS_DIR,f"entities_predictions.json")
    with open(output_prediction_file, "w", encoding="utf-8") as f:
        json.dump(prediction_dataset, f, indent=2, ensure_ascii=False, default=np_encoder)

    print(f"✅ Entities predictef saved {output_prediction_file}")
    


if __name__ == "__main__":
    import sys
    file_path = './documents/artz_brief.txt'
    #file_path = './txt_reports/report_30.txt'
    file_path = './temp/real_report.txt'     
    post_process_predictions = False
    save_as_template = False
    if len(sys.argv) == 2:   
        file_path = sys.argv[1]   
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        exit(1)
    if len(sys.argv) == 3:
        post_process_predictions = sys.argv[2].lower() == 'true'
    if len(sys.argv) == 4:
        save_as_template = sys.argv[3].lower() == 'true'
 
    #main(file_path=file_path, post_process_predictions=post_process_predictions,save_as_template=save_as_template)

    main_multiple(folder_path='txt_reports')