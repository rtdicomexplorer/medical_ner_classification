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
    # Build lookup by span
    raw_by_span = {(e["start"], e["end"]): e for e in raw_entities}
    post_by_span = {(e["start"], e["end"]): e for e in post_entities}

    all_spans = sorted(set(raw_by_span.keys()).union(post_by_span.keys()))

    def render_table(entities_by_span, compare_to, direction):
        rows = ""
        for span in all_spans:
            ent = entities_by_span.get(span)
            other = compare_to.get(span)

            if not ent:
                # Entity missing in this version = added/removed
                continue

            word = html.escape(ent["word"])
            label = html.escape(ent["entity_group"])
            score = f'{ent["score"]:.3f}'
            span_str = f'{span[0]}, {span[1]}'

            # Defaults
            word_class = label_class = score_class = row_class = ""

            if not other:
                row_class = "added" if direction == "post" else "removed"
            else:
                # Compare fields
                if ent["word"] != other["word"]:
                    word_class = "changed"
                if ent["entity_group"] != other["entity_group"]:
                    label_class = "changed"
                if round(ent["score"], 3) != round(other["score"], 3):
                    score_class = "changed"

            rows += (
                f"<tr class='{row_class}'>"
                f"<td class='{word_class}'>{word}</td>"
                f"<td class='{label_class}'>{label}</td>"
                f"<td class='{score_class}'>{score}</td>"
                f"<td>{span_str}</td>"
                f"</tr>\n"
            )
        return rows

    html_content = f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>NER Vergleich</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f9f9f9;
            color: #333;
        }}
        h1 {{
            text-align: center;
            margin-bottom: 40px;
        }}
        .container {{
            display: flex;
            gap: 2%;
            justify-content: space-between;
        }}
        .table-wrapper {{
            width: 48%;
            background: #fff;
            padding: 15px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow-x: auto;
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
            z-index: 1;
        }}
        tr:hover {{
            background-color: #f1f1f1;
        }}
        h2 {{
            margin-top: 0;
            font-size: 1.2em;
            border-bottom: 1px solid #ccc;
            padding-bottom: 5px;
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
    <h1>NER Entity Vergleich</h1>
    <div class="container">
        <div class="table-wrapper">
            <h2>Raw Entities</h2>
            <table>
                <thead>
                    <tr><th>Text</th><th>Label</th><th>Score</th><th>Span</th></tr>
                </thead>
                <tbody>
                    {render_table(raw_by_span, post_by_span, direction="raw")}
                </tbody>
            </table>
        </div>
        <div class="table-wrapper">
            <h2>Postprozessierte Entities</h2>
            <table>
                <thead>
                    <tr><th>Text</th><th>Label</th><th>Score</th><th>Span</th></tr>
                </thead>
                <tbody>
                    {render_table(post_by_span, raw_by_span, direction="post")}
                </tbody>
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


    output_html = os.path.join(OUTPUTDIR, "compare_entities.json")
    save_entity_comparison_html(entities, clean_entities,output_html)

    fhir_output = map_ner_to_fhir(clean_entities)

    output_json = os.path.join(OUTPUTDIR, "fhir_output.json")
    if os.path.exists(output_json):
        os.remove(output_json)
    os.makedirs(OUTPUTDIR, exist_ok=True)
    
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(fhir_output, f, indent=2, ensure_ascii=False)

    print(f"\nFHIR resources saved to {output_json}")

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
