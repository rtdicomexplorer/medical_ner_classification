#train_ner.py
import json
import os
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForTokenClassification, TrainingArguments, Trainer
import numpy as np
from sklearn.metrics import precision_recall_fscore_support
from config import LABEL_LIST, LABEL2ID, ID2LABEL, MODEL_NAME


# Config (could be moved to config.py)
MODEL_NAME = "emilyalsentzer/Bio_ClinicalBERT"
DATA_PATH = "./data/synthetic_ner_data.json"
OUTPUT_DIR = "./models/clinicalbert-ner"
DATA_FILES = {
    "train": "./data/train.json",
    "test": "./data/val.json"
}

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

def tokenize_and_align_labels(examples):
    tokenized_inputs = tokenizer(examples["tokens"], truncation=True, is_split_into_words=True)

    labels = []
    for i, label in enumerate(examples["ner_tags"]):
        word_ids = tokenized_inputs.word_ids(batch_index=i)
        previous_word_idx = None
        label_ids = []
        for word_idx in word_ids:
            if word_idx is None:
                label_ids.append(-100)
            elif word_idx != previous_word_idx:
                label_ids.append(label[word_idx])
            else:
                # For word pieces inside a word
                # use I- prefix if label is B-
                if label[word_idx] % 2 == 1:  # odd labels are I- labels
                    label_ids.append(label[word_idx])
                else:
                    # convert B- to I- for subsequent tokens
                    label_ids.append(label[word_idx] + 1)
            previous_word_idx = word_idx
        labels.append(label_ids)

    tokenized_inputs["labels"] = labels
    return tokenized_inputs

def compute_metrics(p):
    predictions, labels = p
    predictions = np.argmax(predictions, axis=2)

    true_labels = [[ID2LABEL[l] for l in label if l != -100] for label in labels]
    true_preds = [[LABEL2ID[p] for (p, l) in zip(pred, lab) if l != -100] for pred, lab in zip(predictions, labels)]

    all_preds = []
    all_labels = []
    for preds, labs in zip(true_preds, true_labels):
        all_preds.extend(preds)
        all_labels.extend(labs)

    precision, recall, f1, _ = precision_recall_fscore_support(all_labels, all_preds, average="weighted")
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }

def main():
    # # Load data from json
    # with open(DATA_PATH, "r") as f:
    #     data = json.load(f)  # Load dataset with DatasetDict
    datasets = load_dataset("json", data_files=DATA_FILES)

    # Align labels & tokenize
    tokenized_datasets = datasets.map(tokenize_and_align_labels, batched=True)
    model = AutoModelForTokenClassification.from_pretrained(MODEL_NAME, num_labels=len(LABEL_LIST))
    
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        evaluation_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=3,
        weight_decay=0.01,
        save_strategy="epoch",
        logging_dir="./logs",
        logging_steps=10,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        save_total_limit=2,
        seed=42,
        dataloader_drop_last=True,
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["test"],
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
    )
    trainer.train()
    trainer.save_model(OUTPUT_DIR)
   

if __name__ == "__main__":
    main()
