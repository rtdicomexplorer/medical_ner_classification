import os
import json
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from text_extractor import extract_text   # Your custom text extractor
from postprocess import postprocess_entities  # Your custom postprocessing
from ner_to_fhir import map_ner_to_fhir    # Your mapping from NER to FHIR
from config import ID2LABEL,LABEL2ID
from pathlib import Path
import html
MODEL_PATH = "./models/gbert-base"
OUTPUTDIR = "output"

def save_entity_comparison_html(raw_entities, post_entities, filename="ner_comparison.html"):
    def render_entities(entities):
        rows = ""
        for ent in sorted(entities, key=lambda x: x["start"]):
            word = html.escape(ent["word"])
            group = html.escape(ent["entity_group"])
            score = f'{ent["score"]:.3f}'
            span = f'{ent["start"]}, {ent["end"]}'
            rows += f"<tr><td>{word}</td><td>{group}</td><td>{score}</td><td>{span}</td></tr>\n"
        return rows

    html_content = f"""
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <title>NER Vergleich</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            table {{ border-collapse: collapse; width: 48%; margin: 1%; float: left; }}
            th, td {{ border: 1px solid #ccc; padding: 6px 10px; text-align: left; }}
            th {{ background-color: #f0f0f0; }}
            h2 {{ clear: both; }}
            .container {{ display: flex; gap: 2%; }}
        </style>
    </head>
    <body>
        <h1>NER Entity Vergleich</h1>
        <div class="container">
            <div>
                <h2>Raw Entities</h2>
                <table>
                    <tr><th>Text</th><th>Label</th><th>Score</th><th>Span</th></tr>
                    {render_entities(raw_entities)}
                </table>
            </div>
            <div>
                <h2>Postprozessierte Entities</h2>
                <table>
                    <tr><th>Text</th><th>Label</th><th>Score</th><th>Span</th></tr>
                    {render_entities(post_entities)}
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    Path(filename).write_text(html_content, encoding="utf-8")
    print(f"Vergleich gespeichert unter: {filename}")
def main(file_path):
    print(f"Extracting text from {file_path} ...")
    text = extract_text(file_path)
    print(f"Text extracted (first 500 chars):\n{text[:500]}")
    print(f"\n=============================================\n")
    # text = "Patient Otto Kromberger leidet an Kopfschmerzen."
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForTokenClassification.from_pretrained(MODEL_PATH)

    model.config.id2label = ID2LABEL
    model.config.label2id = LABEL2ID
    nlp = pipeline("ner", model=model, 
                   tokenizer=tokenizer, 
                   aggregation_strategy="simple",
                   device=0 if torch.cuda.is_available() else -1  # 0 = CUDA, -1 = CPU
                   )# or simple aggregation_straty=> Entity_group

    entities = nlp(text)
    for ent in entities:
        entity_type = ent.get("entity_group", ent.get("entity"))
        # print(ent)
        print(f"Entity: '{ent['word']}'  |  Type: {entity_type}  |  Score: {ent['score']:.3f}")
    clean_entities = postprocess_entities(entities)

    print("\n--- After postprocessing ---")
    for ent in clean_entities:
        entity_type = ent.get("entity_group", ent.get("entity"))
        print(f"Entity: '{ent['word']}'  |  Type: {entity_type}  |  Score: {ent['score']:.3f}  |  Span: ({ent['start']}, {ent['end']})")



    save_entity_comparison_html(entities, clean_entities)

    # fhir_output = map_ner_to_fhir(clean_entities)

    # output_json = os.path.join(OUTPUTDIR, "fhir_output.json")
    # if os.path.exists(output_json):
    #     os.remove(output_json)
    # os.makedirs(OUTPUTDIR, exist_ok=True)
    
    # with open(output_json, "w", encoding="utf-8") as f:
    #     json.dump(fhir_output, f, indent=2, ensure_ascii=False)

    # print(f"\nFHIR resources saved to {output_json}")

if __name__ == "__main__":
    import sys
    file_path = './documents/artz_brief.txt'
    if len(sys.argv) == 2:
        print("Usage: python infer_ner.py <path_to_file>")
    
        file_path = sys.argv[1]
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            exit(1)
    
    main(file_path)
