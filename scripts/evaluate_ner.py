# evaluate_ner.py



# run:  python evaluate_ner.py

import json
from sklearn.metrics import classification_report
from seqeval.metrics import precision_score, recall_score, f1_score, classification_report as seqeval_classification_report
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from postprocess import postprocess_entities  # import your function here
from config import LABEL_LIST
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
MODEL_PATH = "./models/clinicalbert-ner"
def plot_confusion_matrix(y_true, y_pred, labels=None, ignore_label="O"):
    # Flatten sequences
    y_true_flat = [label for seq in y_true for label in seq]
    y_pred_flat = [label for seq in y_pred for label in seq]

    # Optional: Filter out "O" labels
    if ignore_label:
        pairs = [(t, p) for t, p in zip(y_true_flat, y_pred_flat) if t != ignore_label]
        y_true_flat, y_pred_flat = zip(*pairs)

    # Get sorted label set
    unique_labels = sorted(set(y_true_flat + y_pred_flat))
    if labels:
        unique_labels = [l for l in labels if l in unique_labels]

    cm = confusion_matrix(y_true_flat, y_pred_flat, labels=unique_labels)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=unique_labels, yticklabels=unique_labels)
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title("NER Confusion Matrix (without 'O')")
    plt.tight_layout()
    plt.show()
def load_pipeline():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForTokenClassification.from_pretrained(MODEL_PATH)
    return pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")

def align_labels(tokens, true_tags, pred_entities):
    """
    Convert token-level true tags and predicted entities into label sequences for evaluation
    """
    pred_tags = ["O"] * len(tokens)

    for ent in pred_entities:
        start_idx = ent["start"]
        end_idx = ent["end"]
        label = ent["entity"]

        for i, token in enumerate(tokens):
            token_start = token['start']
            token_end = token['end']
            if token_start >= start_idx and token_end <= end_idx:
                prefix = "B-" if pred_tags[i] == "O" else "I-"
                pred_tags[i] = f"{prefix}{label}"

    return true_tags, pred_tags

def evaluate_ner(dataset_path, confidence_threshold=0.6):
    # Load examples
    with open(dataset_path, "r", encoding="utf-8") as f:
        examples = json.load(f)

    nlp = load_pipeline()

    all_true = []
    all_pred = []

    for example in examples:
        text = " ".join(example["tokens"])
        true_tags = example["ner_tags"]

        # Token-level alignment for consistent start/end
        tokens = nlp.tokenizer(text, return_offsets_mapping=True, return_tensors="pt", truncation=True)
        token_offsets = tokens["offset_mapping"][0].tolist()
        token_words = nlp.tokenizer.convert_ids_to_tokens(tokens["input_ids"][0])[1:-1]  # skip special tokens

        token_data = [{"start": s, "end": e, "word": w} for (s, e), w in zip(token_offsets, token_words)]

        # Run model
        raw_entities = nlp(text)
        pred_entities = postprocess_entities(raw_entities, confidence_threshold=confidence_threshold)

        true_seq, pred_seq = align_labels(token_data, true_tags, pred_entities)

        all_true.append(true_seq)
        all_pred.append(pred_seq)

    # Evaluation
    print("SeqEval Evaluation:\n")
    print(seqeval_classification_report(all_true, all_pred, digits=3))
    print(f"Precision: {precision_score(all_true, all_pred):.3f}")
    print(f"Recall:    {recall_score(all_true, all_pred):.3f}")
    print(f"F1-score:  {f1_score(all_true, all_pred):.3f}")
    plot_confusion_matrix(all_true, all_pred, labels=LABEL_LIST, ignore_label="O")


from typing import List, Dict, Tuple

def load_entities(file_path: str) -> List[Dict]:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def entity_to_tuple(entity: Dict) -> Tuple[str, int, int, str]:
    """Standardize entity to a comparable tuple format."""
    return (
        entity["entity_group"],
        # entity["start"],
        # entity["end"],
        entity["word"].strip().lower()
    )


def compare_predictions(gold: List[Dict], pred: List[Dict]) -> None:
    gold_set = set(entity_to_tuple(e) for e in gold)
    pred_set = set(entity_to_tuple(e) for e in pred)

    true_positives = gold_set & pred_set
    false_positives = pred_set - gold_set
    false_negatives = gold_set - pred_set

    precision = len(true_positives) / len(pred_set) if pred_set else 0
    recall = len(true_positives) / len(gold_set) if gold_set else 0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0
    )

    print("\n📊 Evaluation Metrics")
    print(f"✔️  True Positives:   {len(true_positives)}")
    print(f"❌  False Positives:  {len(false_positives)}")
    print(f"🔺  False Negatives:  {len(false_negatives)}")
    print(f"\n🔍 Precision: {precision:.2f}")
    print(f"🔍 Recall:    {recall:.2f}")
    print(f"🔍 F1-Score:  {f1:.2f}")

    # Optional: show mismatches
    if false_positives:
        print("\n⚠️  False Positives:")
        for fp in false_positives:
            print(f"  - {fp}")

    if false_negatives:
        print("\n❗ False Negatives:")
        for fn in false_negatives:
            print(f"  - {fn}")
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "true_positives": sorted(true_positives),
        "false_positives": sorted(false_positives),
        "false_negatives": sorted(false_negatives),
    }

def write_html_report(results: Dict, output_path: str):
    from datetime import datetime
    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>NER Evaluation Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 2em; }}
            h1 {{ color: #333; }}
            .metric {{ font-size: 1.2em; margin-bottom: 1em; }}
            .tp {{ background-color: #e0ffe0; }}
            .fp {{ background-color: #ffe0e0; }}
            .fn {{ background-color: #fff0cc; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 1em; }}
            th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
            th {{ background-color: #f0f0f0; }}
        </style>
    </head>
    <body>
        <h1>NER Evaluation Report</h1>
        <p><b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

        <div class="metric">🔍 <b>Precision:</b> {results['precision']:.2f}</div>
        <div class="metric">🔍 <b>Recall:</b> {results['recall']:.2f}</div>
        <div class="metric">🔍 <b>F1 Score:</b> {results['f1']:.2f}</div>

        <h2>✔️ True Positives ({len(results['true_positives'])})</h2>
        {render_table(results['true_positives'], 'tp')}

        <h2>❌ False Positives ({len(results['false_positives'])})</h2>
        {render_table(results['false_positives'], 'fp')}

        <h2>❗ False Negatives ({len(results['false_negatives'])})</h2>
        {render_table(results['false_negatives'], 'fn')}

    </body>
    </html>
    """

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ HTML report saved to: {output_path}")


def render_table(rows: List[Tuple], row_class: str) -> str:
    if not rows:
        return "<p><i>None</i></p>"
    table = "<table><tr><th>Entity Group</th><th>Word</th></tr>"
    for row in rows:
        entity_group,  word = row
        table += f'<tr class="{row_class}"><td>{entity_group}</td><td>{word}</td></tr>'
    table += "</table>"
    return table

OUTPUTDIR = "output"
if __name__ == "__main__":
    import os
    os.makedirs(OUTPUTDIR, exist_ok=True)
    gold_file = "./expected/report_7.json"
    pred_file = "./predictions/report_7.json"
   
    gold_entities = load_entities(gold_file)
    pred_entities = load_entities(pred_file)

    results = compare_predictions(gold_entities, pred_entities)
   
    _, report_file_name = os.path.split(gold_file)  
    report_file_name, _ = os.path.splitext(report_file_name) 
    output_html = os.path.join(OUTPUTDIR,f"evaluation_{report_file_name}.html")
    write_html_report(results, output_html)


  
    # results =evaluate_ner("data/test_ner_data.json")
