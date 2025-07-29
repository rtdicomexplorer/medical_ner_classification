import os
import json
import random
import re
import datetime
from config import LABEL2ID
from sklearn.model_selection import train_test_split
import simple_icd_10 as icd

# === Static data ===
diagnosis_icd10_map = {
    "Hypertonie": "I10",
    "Diabetes Mellitus": "E11.9",
    "Asthma": "J45",
    "Pneumonie": "J18.9"
}

names = ["Herr. Max Müller", "Anna Schmidt", "L. Weber", "Sophie Fischer", "Otto Kromberger"]
doctors = ["Dr. Müller-Eberd ", "Dr.  Schneider", "Dr Becker", "Dr Weber", "PD Dr. Suhle Nikolas", "dr. Michail Igor", "Pro. Maximilian Max", "professor Leo Metger" ]
symptoms = ["Brustschmerzen", "Atemnot", "Fieber", "Müdigkeit", "Kopfschmerzen", "Sehstörung"]
medications = ["Metformin", "Lisinopril", "Albuterol", "Amoxicillin"]
treatments = ["Sauerstofftherapie", "Operation", "Chemotherapie", "Physiotherapie"]
procedures = ["Angioplastie", "MRT", "Biopsie", "CT"]
departments = ["Kardiologie", "Notaufnahme", "Onkologie", "Radiologie"]
lab_results = ["Hb 13.5 g/dL", "Blutzucker 110 mg/dL", "Cholesterin 200 mg/dL"]
allergies = ["Penicillin", "Pollen", "Nüsse"]
immunizations = ["Masern-Impfung", "Grippeimpfung"]
devices = ["Herzschrittmacher", "Insulinpumpe"]
family_histories = ["Mutter mit Diabetes", "Vater mit Bluthochdruck"]
hospital_names = ["St. Marien Krankenhaus", "Universitätsklinikum München"]
hospital_addresses = ["Hauptstraße 12, 80331 München", "Goetheplatz 9, 50674 Köln"]
hospital_phones = ["089 123456", "0221 456789"]
genders = ["männlich", "weiblich", "divers"]
family_statuses = ["ledig", "verheiratet", "geschieden", "verwitwet"]

# === Utility functions ===
def random_date(start_year=2022, end_year=2024):
    start = datetime.date(start_year, 1, 1)
    end = datetime.date(end_year, 12, 31)
    return (start + datetime.timedelta(days=random.randint(0, (end - start).days))).strftime("%d.%m.%Y")

def random_birthdate():
    return random_date(1930, 2005)

def simple_tokenize(text):
    return re.findall(r"\w+|[^\w\s]", text, re.UNICODE)

def generate_entities():
    name = random.choice(names)
    doctor = random.choice(doctors)
    diagnosis = random.choice(list(diagnosis_icd10_map.keys()))
    icd10 = diagnosis_icd10_map[diagnosis]
    icd_desc = icd.get_description(icd10)

    entities = {
        name: "PERSON",
        doctor: "DOCTOR",
        diagnosis: "DIAGNOSIS",
        icd10: "ICD10_CODE",
        icd_desc: "ICD10_DESC",
        random.choice(symptoms): "SYMPTOM",
        random.choice(medications): "MEDICATION",
        random.choice(treatments): "TREATMENT",
        random.choice(procedures): "PROCEDURE",
        random.choice(departments): "DEPARTMENT",
        random.choice(hospital_names): "ORG",
        random.choice(hospital_addresses): "ADDRESS",
        random.choice(hospital_phones): "PHONE",
        random.choice(genders): "GENDER",
        random_birthdate(): "BIRTHDATE",
        random.choice(family_statuses): "FAMILY_STATUS",
        random_date(): "DATE",
        random.choice(lab_results): "LAB_RESULT",
    }

    # Optional entries
    if random.random() < 0.5:
        entities[random.choice(allergies)] = "ALLERGY"
    if random.random() < 0.5:
        entities[random.choice(immunizations)] = "IMMUNIZATION"
    if random.random() < 0.5:
        entities[random.choice(devices)] = "DEVICE"
    if random.random() < 0.5:
        entities[random.choice(family_histories)] = "FAMILY_HISTORY"

    return entities

def generate_text_from_entities(entities):
    pieces = []
    for val, ent_type in entities.items():
        if ent_type == "PERSON":
            pieces.append(f"Patient: {val}")
        elif ent_type == "DOCTOR":
            pieces.append(f"behandelt durch {val}")
        elif ent_type == "DIAGNOSIS":
            pieces.append(f"Diagnose: {val}")
        elif ent_type == "DATE":
            pieces.append(f"Datum: {val}")
        else:
            pieces.append(val)
    return ". ".join(pieces) + "."

def tokenize_and_label(text, entities):
    tokens = simple_tokenize(text)
    labels = ["O"] * len(tokens)

    for entity_text, entity_type in entities.items():
        ent_tokens = simple_tokenize(entity_text)
        for i in range(len(tokens) - len(ent_tokens) + 1):
            if tokens[i:i+len(ent_tokens)] == ent_tokens:
                labels[i] = f"B-{entity_type}"
                for j in range(1, len(ent_tokens)):
                    labels[i + j] = f"I-{entity_type}"
                break
    label_ids = [LABEL2ID.get(label, 0) for label in labels]
    return tokens, label_ids

def generate_dataset(n_samples=1000, save_path="./data", save_reports=False):
    data = []
    for i in range(n_samples):
        entities = generate_entities()
        text = generate_text_from_entities(entities)
        tokens, labels = tokenize_and_label(text, entities)

        data.append({
            "tokens": tokens,
            "ner_tags": labels
        })

        if save_reports:
            os.makedirs("./txt_reports", exist_ok=True)
            with open(f"./txt_reports/report_{i+1}.txt", "w", encoding="utf-8") as f:
                f.write(text)

    train, val = train_test_split(data, test_size=0.1, random_state=42)
    os.makedirs(save_path, exist_ok=True)

    with open(f"{save_path}/train.json", "w", encoding="utf-8") as f:
        json.dump(train, f, indent=2, ensure_ascii=False)
    with open(f"{save_path}/val.json", "w", encoding="utf-8") as f:
        json.dump(val, f, indent=2, ensure_ascii=False)

    print(f"✅ Generated {n_samples} samples")
    print(f"→ Training: {len(train)} | Validation: {len(val)}")
    print(f"→ Saved to {save_path}/train.json and val.json")

# Run as script
if __name__ == "__main__":
    generate_dataset(n_samples=2000, save_reports=True)
