import json
import numpy as np
from datasets import load_dataset
import evaluate
from transformers import AutoTokenizer, AutoModelForTokenClassification, TrainingArguments, Trainer
from config import LABEL2ID  # Must include LABEL_LIST and LABEL2ID

# Invert LABEL2ID
ID2LABEL = {v: k for k, v in LABEL2ID.items()}
LABEL_LIST = list(LABEL2ID.keys())

# Load model and tokenizer from your previously trained checkpoint
model_path = "./models/gbert-base"
model = AutoModelForTokenClassification.from_pretrained(
    model_path,
    num_labels=len(LABEL_LIST),
    id2label=ID2LABEL,
    label2id=LABEL2ID
)
tokenizer = AutoTokenizer.from_pretrained(model_path)

# Load dataset
dataset = load_dataset("json", data_files={
    "train": "./data/train.json",
    "validation": "./data/val.json"
})

# Rename `ner_tags` to `labels` to match Trainer expectations
def rename(example):
    example["labels"] = example["ner_tags"]
    return example

dataset = dataset.map(rename)

# Tokenization + alignment
def tokenize_and_align_labels(examples):
    tokenized_inputs = tokenizer(
        examples["tokens"],
        truncation=True,
        is_split_into_words=True,
        padding="max_length",
        max_length=128
    )

    labels = []
    for i, label in enumerate(examples["labels"]):
        word_ids = tokenized_inputs.word_ids(batch_index=i)
        previous_word_idx = None
        label_ids = []
        for word_idx in word_ids:
            if word_idx is None:
                label_ids.append(-100)
            elif word_idx != previous_word_idx:
                label_ids.append(label[word_idx])
            else:
                label_ids.append(label[word_idx] if LABEL_LIST[label[word_idx]].startswith("I-") else -100)
            previous_word_idx = word_idx
        labels.append(label_ids)

    tokenized_inputs["labels"] = labels
    return tokenized_inputs

tokenized_dataset = dataset.map(tokenize_and_align_labels, batched=True)

# Load evaluation metric
metric = evaluate.load("seqeval")

def compute_metrics(p):
    predictions, labels = p
    predictions = np.argmax(predictions, axis=2)

    true_labels = [[LABEL_LIST[l] for l in label if l != -100] for label in labels]
    true_preds = [
        [LABEL_LIST[p] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]
    results = metric.compute(predictions=true_preds, references=true_labels)
    return {
        "precision": results["overall_precision"],
        "recall": results["overall_recall"],
        "f1": results["overall_f1"],
        "accuracy": results["overall_accuracy"],
    }

# Set training arguments
training_args = TrainingArguments(
    output_dir="./ner-model-finetuned",
    eval_strategy="epoch",
    save_strategy="epoch",
    learning_rate=5e-5,
    per_device_train_batch_size=16,
    num_train_epochs=5,
    weight_decay=0.01,
)

# Initialize Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["validation"],
    tokenizer=tokenizer,
    compute_metrics=compute_metrics
)

# Train
trainer.train()

# Save the final model
trainer.save_model("./ner-model-finetuned")
tokenizer.save_pretrained("./ner-model-finetuned")
