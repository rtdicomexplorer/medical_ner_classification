import os
import sys
import json
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
# Add project root to sys.path if needed
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.text_extractor import extract_text 
from scripts.utils import generate_ner_data, init_tesseract, replace_entities_with_labels

from scripts.postprocess import postprocess_entities  # Your custom postprocessing
from scripts.ner_to_fhir import map_ner_to_fhir    # Your mapping from NER to FHIR
from scripts.config import ID2LABEL,LABEL2ID
MODEL_PATH = "./models/gbert-base"
OUTPUTDIR = "output"
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

def __save_entity_comparison_html(raw_entities, post_entities, filename="ner_comparison.html"):
    from pathlib import Path
    import html

    # Build lookups by span
    raw_by_span = {(e["start"], e["end"]): e for e in raw_entities}
    post_by_span = {(e["start"], e["end"]): e for e in post_entities}
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
    print(f"\nHTML merged comparison saved to {filename}")


def __save_predictions(predictions, file_name, output_dir="predictions"):
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"{file_name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(predictions, f, indent=2, ensure_ascii=False)
    print(f"✅ Predictions saved to {path}")


def __execute_predictions(text):
    # MODEL_PATH = 'deepset/gbert-base'
    if not  ner_model.is_ready():
        ner_model.load()
    return ner_model.predict(text)



def main(file_path):

    _, report_file_name = os.path.split(file_path)
    
    report_file_name, _ = os.path.splitext(report_file_name) 

    print(f"Extracting text from {file_path} ...")
    text = extract_text(file_path)
    predictions = __execute_predictions(text)
    ner_data = generate_ner_data(text, predictions)
    dataset = []   
    dataset.append(ner_data)

    # for ent in predictions:
    #     entity_type = ent.get("entity_group", ent.get("entity"))
    #     print(f"Entity: '{ent['word']}'  |  Type: {entity_type}  |  Score: {ent['score']:.3f}")
    
    #the idea is to use the report as new template    
    text_as_template = replace_entities_with_labels(text,predictions)
    
    #postprocess the entities to make them clean...to be tested and updated, not called via WEB
    cleaned_entities = postprocess_entities(predictions)

    __save_predictions(cleaned_entities,report_file_name)

    os.makedirs(OUTPUTDIR, exist_ok=True)
    
    output_html = os.path.join(OUTPUTDIR, f"compare_postprocessing_{report_file_name}.html")  
    if os.path.exists(output_html):
        os.remove(output_html)
    __save_entity_comparison_html(predictions, cleaned_entities,output_html)

    output_ner_file = os.path.join(OUTPUTDIR,f"ner_{report_file_name}.json")
    with open(output_ner_file, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)

    output_text_template =  os.path.join(OUTPUTDIR,f"template_{report_file_name}.txt")
    with open(output_text_template, "w", encoding="utf-8") as f:
        f.write(text_as_template)

    print(f"All result files have been saved in {OUTPUTDIR}")

if __name__ == "__main__":
    import sys
    file_path = './documents/artz_brief.txt'
    #file_path = './txt_reports/report_30.txt'
    file_path = './temp/real_report.txt'
    if len(sys.argv) == 2:   
        file_path = sys.argv[1]           
    if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            exit(1)
    main(file_path)
