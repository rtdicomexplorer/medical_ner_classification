import json
import os
import sys
from sklearn.metrics import precision_recall_fscore_support
from typing import List, Dict, Tuple
from collections import defaultdict
 
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from scripts.config import LABEL_LIST, ID2LABEL



def evaluate_ner_data_predicted(expected,prediction):
    # Load JSON files
    with open(expected) as f:
        expected = json.load(f)
    with open(prediction) as f:
        predicted = json.load(f)
    # Extract true and predicted labels
    true_labels, pred_labels = [], []
    for exp, pred in zip(expected, predicted):
        # align by token (assuming same tokens in both)
        for t, p in zip(exp["ner_tags"], pred["ner_tags"]):
            true_labels.append(t)
            pred_labels.append(p)

    # Compute per-class metrics
    labels = sorted(set(true_labels) | set(pred_labels))
    prec, rec, f1, _ = precision_recall_fscore_support(true_labels, pred_labels, labels=labels, zero_division=0)

    # Collect results
    results = {ID2LABEL[label]: {"precision": p, "recall": r, "f1": f}
            for label, p, r, f in zip(labels, prec, rec, f1)}


    entity_metrics = defaultdict(lambda: {"precision": [], "recall": [], "f1": []})

    for label, metrics in results.items():
        if label == "O":  # skip non-entities
            continue
        entity = label.split("-")[-1]  # e.g. "ORG" from "B-ORG"
        for m in ["precision", "recall", "f1"]:
            entity_metrics[entity][m].append(metrics[m])

    # Average over B-/I-
    entity_scores = {}
    for ent, metrics in entity_metrics.items():
        entity_scores[ent] = {
            m: (sum(values) / len(values)) if values else 0.0
            for m, values in metrics.items()
        }
    print(entity_scores)



if __name__ == "__main__":

    expected_file = "./expected/report.json"
    pred_file = "./predictions/report.json"
    evaluate_ner_data_predicted(expected=expected_file, prediction=pred_file)
  
