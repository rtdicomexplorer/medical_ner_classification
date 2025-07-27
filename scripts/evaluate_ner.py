# evaluate_ner.py

# How to Run
#Save a small set of annotated test data in data/test_ner_data.json, format:
# [
#   {
#     "tokens": ["Patient", "Max", "Müller", "hatte", "Asthma", "."],
#     "ner_tags": ["O", "B-PERSON", "I-PERSON", "O", "B-DIAGNOSIS", "O"]
#   },
#   ...
# ]


# run:  python evaluate_ner.py

import json
from sklearn.metrics import classification_report
from seqeval.metrics import precision_score, recall_score, f1_score, classification_report as seqeval_classification_report
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from postprocess import postprocess_entities  # import your function here
from config import LABEL_LIST

MODEL_PATH = "./models/clinicalbert-ner"

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

if __name__ == "__main__":
    evaluate_ner("data/test_ner_data.json")
