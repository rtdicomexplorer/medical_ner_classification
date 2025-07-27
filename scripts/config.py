# config.py

LABEL_LIST = [
    "O",
    "B-PERSON", "I-PERSON",
    "B-DOCTOR", "I-DOCTOR",
    "B-ORG", "I-ORG",
    "B-DATE", "I-DATE",
    "B-DIAGNOSIS", "I-DIAGNOSIS",
    "B-SYMPTOM", "I-SYMPTOM",
    "B-MEDICATION", "I-MEDICATION",
    "B-PROCEDURE", "I-PROCEDURE",
    "B-TREATMENT", "I-TREATMENT",
    "B-DEPARTMENT", "I-DEPARTMENT",
    "B-LAB_RESULT", "I-LAB_RESULT",
    "B-ALLERGY", "I-ALLERGY",
    "B-IMMUNIZATION", "I-IMMUNIZATION",
    "B-DEVICE", "I-DEVICE",
    "B-FAMILY_HISTORY", "I-FAMILY_HISTORY",
]

LABEL2ID = {label: idx for idx, label in enumerate(LABEL_LIST)}
ID2LABEL = {idx: label for label, idx in LABEL2ID.items()}

MODEL_NAME = "emilyalsentzer/Bio_ClinicalBERT"

TRAINING_ARGS = {
    "output_dir": "./models/clinical_ner_model",
    "num_train_epochs": 3,
    "per_device_train_batch_size": 8,
    "per_device_eval_batch_size": 8,
    "warmup_steps": 100,
    "weight_decay": 0.01,
    "logging_dir": "./logs",
    "logging_steps": 10,
    "evaluation_strategy": "epoch",
    "save_strategy": "epoch",
    "load_best_model_at_end": True,
    "fp16": False,  # Set True if using GPU with mixed precision
}

MAX_LENGTH = 128
