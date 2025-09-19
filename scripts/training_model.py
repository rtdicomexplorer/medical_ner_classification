#train_ner.py
import torch
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForTokenClassification, TrainingArguments, Trainer, DataCollatorForTokenClassification
import numpy as np
from sklearn.metrics import precision_recall_fscore_support,classification_report
import os
import sys
# Add project root to sys.path if needed
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from  scripts.config import LABEL_LIST, ID2LABEL,LABEL2ID
import random

# Config (could be moved to config.py)

# "bert-base-german-cased"             # Reliable baseline
# "xlm-roberta-base"                   # Multilingual, works well
# "deepset/gbert-base"                 # Better for downstream German tasks
# "Charité/Medbert-Deutsch"           # Specifically trained on German medical data


MODEL_NAME = 'deepset/gbert-base'#"emilyalsentzer/Bio_ClinicalBERT" #medgpt/gbert-medical-ner
DATA_PATH = "./data/synthetic_ner_data.json"
OUTPUT_DIR = "./models/gbert-base"
DATA_FILES = {
    "train": "./data/train.json",
    "validation": "./data/val.json",
    "test": "./data/test.json"
}


 
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
data_collator = DataCollatorForTokenClassification(tokenizer)


def __tokenize_and_align_labels(examples):
    tokenized_inputs = tokenizer(
        examples["tokens"], 
        truncation=True, 
        is_split_into_words=True,
        max_length=128,
        padding="max_length",
    )

    all_labels = []
    for i, labels in enumerate(examples["ner_tags"]):
        word_ids = tokenized_inputs.word_ids(batch_index=i)
        previous_word_idx = None
        label_ids = []
        for word_idx in word_ids:
            if word_idx is None:
                label_ids.append(-100)
            elif word_idx != previous_word_idx:
                label_ids.append(labels[word_idx])
            else:
                # convert B- to I- for subword tokens
                label_str = ID2LABEL[labels[word_idx]]
                if label_str.startswith("B-"):
                    label_str = label_str.replace("B-", "I-")
                label_ids.append(LABEL2ID.get(label_str, LABEL2ID["O"]))
            previous_word_idx = word_idx
        all_labels.append(label_ids)

    tokenized_inputs["labels"] = all_labels
    return tokenized_inputs

def __compute_metrics(p):
    predictions, labels = p
    predictions = np.argmax(predictions, axis=2)

    true_labels = [[ID2LABEL[l] for l in label if l != -100] for label in labels]
    true_preds  = [[ID2LABEL[p] for (p, l) in zip(pred, lab) if l != -100] for pred, lab in zip(predictions, labels)]

    all_preds = [p for seq in true_preds for p in seq]
    all_labels = [l for seq in true_labels for l in seq]

    precision, recall, f1, _ = precision_recall_fscore_support(all_labels, all_preds, average="weighted")
        # Print per-label report for debugging or analysis
    print("\n🔍 Classification Report (per label):")
    print(classification_report(all_labels, all_preds, digits=3))
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }

def __set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def main(print_examples= False):
    print(f"Starting  print example options is: {print_examples} !")
    datasets = load_dataset("json", data_files=DATA_FILES)
    batch_size = 4
    learning_rate = 3e-5
    device = "cuda" if torch.cuda.is_available() else "cpu"
    batch_size = 8 if device == "cuda" else 4
    learning_rate = 1e-5 if device == "cuda" else 3e-5

    print(f"💻 Using device: {device}")
    # Align labels & tokenize
    tokenized_datasets = datasets.map(__tokenize_and_align_labels, batched=True)
    model = AutoModelForTokenClassification.from_pretrained(MODEL_NAME, num_labels=len(LABEL_LIST))

    model.to(device)
    model.config.id2label = ID2LABEL
    model.config.label2id = LABEL2ID

    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        do_eval=True,
        eval_strategy ="epoch",
        learning_rate=learning_rate,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        num_train_epochs=3,
        weight_decay=0.01,
        save_strategy="epoch",
        logging_dir="./logs",
        logging_steps=10,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        save_total_limit=2,
        seed=42,
        dataloader_drop_last=False,
        label_smoothing_factor = 0.1
    )

  
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["validation"],
        # processing_class=tokenizer,
        data_collator=data_collator,
        compute_metrics=__compute_metrics,
    )
    trainer.train()
    print("\nEvaluating on test dataset...")
    test_metrics = trainer.evaluate(eval_dataset=tokenized_datasets["test"])
    print(f"Test metrics: {test_metrics}")
    trainer.save_model(OUTPUT_DIR)
    print(f"\nModel saved {OUTPUT_DIR}")

    if print_examples: 
        # === Generate predictions on test set ===
        print("\n📝 Generating predictions on test set:")
        test_predictions, test_labels, _ = trainer.predict(tokenized_datasets["test"])
        preds = np.argmax(test_predictions, axis=2)

        # Convert preds and labels back to tag strings
        true_labels = [[ID2LABEL[l] for l in label if l != -100] for label in test_labels]
        true_preds = [[ID2LABEL[p] for (p, l) in zip(pred, lab) if l != -100] for pred, lab in zip(preds, test_labels)]

        # Example: print first 3 samples with tokens, true tags, predicted tags
        n_samples = min(3, len(tokenized_datasets["test"]))
        for i in range(n_samples):
            print(f"\nSample {i + 1}:")
            print("\nTrue tags:  ", true_labels[i])
            print("\nPred tags:  ", true_preds[i])
  

if __name__ == "__main__":
    __set_seed(42)
    print_examples = False
    if len(sys.argv) > 1:
         print_examples = sys.argv[1].lower() == 'true'
    
    main(print_examples)

