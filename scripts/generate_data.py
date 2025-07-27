import random
import json
import os
import datetime
from config import LABEL2ID

# German and international style names for PERSON and DOCTOR
names = [
    "Max Müller", "Anna Schmidt", "Lukas Weber", "Sophie Fischer",
    "John Smith", "Mary Jones", "Robert Lee", "Emily Davis"
]
first_names = ["Max", "Anna", "Lukas", "Marie", "Felix", "Laura"]
last_names = ["Müller", "Schmidt", "Schneider", "Fischer", "Weber", "Becker"]
doctors = [
    "Dr. Müller", "Dr. Schneider", "Dr. Becker", "Dr. Weber",
    "Dr. Adams", "Dr. Lee", "Dr. Patel", "Dr. Chen"
]

diagnoses = ["Hypertonie", "Diabetes Mellitus", "Asthma", "Pneumonie"]
symptoms = ["Brustschmerzen", "Atemnot", "Fieber", "Müdigkeit"]
medications = ["Metformin", "Lisinopril", "Albuterol", "Amoxicillin"]
treatments = ["Sauerstofftherapie", "Operation", "Chemotherapie", "Physiotherapie"]
lab_results = ["Hb 13.5 g/dL", "Blutzucker 110 mg/dL", "Cholesterin 200 mg/dL"]
allergies = ["Penicillin", "Pollen", "Nüsse"]
immunizations = ["Masern-Impfung", "Grippeimpfung"]
devices = ["Herzschrittmacher", "Insulinpumpe"]
family_histories = ["Mutter mit Diabetes", "Vater mit Bluthochdruck"]

procedures = ["Angioplastie", "MRT-Scan", "Biopsie", "Ultraschall"]
organizations = [
    "St. Marien Krankenhaus", "Allgemeine Gesundheitsklinik", 
    "Städtisches Medizinzentrum", "Universitätsklinikum"
]
departments = ["Kardiologie", "Notaufnahme", "Onkologie", "Radiologie"]

months = [
    "Januar", "Februar", "März", "April", "Mai", "Juni", "Juli",
    "August", "September", "Oktober", "November", "Dezember"
]

dates = ["10. März 2023", "15. Januar 2022", "28. Februar 2024"]
def random_date():
    start = datetime.date(2022, 1, 1)
    end = datetime.date(2024, 12, 31)
    delta = end - start
    rand_day = start + datetime.timedelta(days=random.randint(0, delta.days))
    return rand_day.strftime("%d. %B %Y")  # German date format like '10. März 2023'

def generate_report():
    name = random.choice(names)
    first = random.choice(first_names)
    last = random.choice(last_names)
    doctor = random.choice(doctors)
    diagnosis = random.choice(diagnoses)
    symptom = random.choice(symptoms)
    medication = random.choice(medications)
    treatment = random.choice(treatments)
    procedure = random.choice(procedures)
    organization = random.choice(organizations)
    department = random.choice(departments)
    lab_result = random.choice(lab_results)
    allergy = random.choice(allergies)
    immunization = random.choice(immunizations)
    device = random.choice(devices)
    family_history = random.choice(family_histories)
    date = random.choice(dates)

    text = (
        f"Am {date} stellte sich Patient {name} mit {symptom} vor. "
        f"Die Diagnose lautete {diagnosis}. "
        f"Der Patient wurde mit {medication} behandelt und erhielt {treatment}. "
        f"Das Verfahren war {procedure}. "
        f"Untersuchung durchgeführt von {doctor} im {department} der {organization}."
        f" Laborwerte: {lab_result}. "
        f" Allergien: {allergy}. "
        f" Impfungen: {immunization}. "
        f" Medizinisches Gerät: {device}. "
        f" Familienanamnese: {family_history}."
    )

    entities = {
        name: "PERSON",
        doctor: "DOCTOR",
        date: "DATE",
        diagnosis: "DIAGNOSIS",
        symptom: "SYMPTOM",
        medication: "MEDICATION",
        treatment: "TREATMENT",
        procedure: "PROCEDURE",
        organization: "ORG",
        department: "DEPARTMENT",
        lab_result: "LAB_RESULT",
        allergy: "ALLERGY",
        immunization: "IMMUNIZATION",
        device: "DEVICE",
        family_history: "FAMILY_HISTORY",
    }
    return text, entities

def tokenize_and_label(text, entities):
    tokens = text.split()
    labels = ["O"] * len(tokens)

    for entity_text, ent_type in entities.items():
        ent_tokens = entity_text.split()
        for i in range(len(tokens) - len(ent_tokens) + 1):
            if tokens[i:i+len(ent_tokens)] == ent_tokens:
                labels[i] = f"B-{ent_type}"
                for j in range(1, len(ent_tokens)):
                    labels[i+j] = f"I-{ent_type}"
                break
    return tokens, labels

def generate_dataset(n_samples=1000):
    data = []
    for _ in range(n_samples):
        text, entities = generate_report()
        tokens, labels = tokenize_and_label(text, entities)
        data.append({"tokens": tokens, "ner_tags": [LABEL2ID[l] for l in labels]})

    os.makedirs("./data", exist_ok=True)
    with open("./data/synthetic_ner_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    generate_dataset(n_samples=1000)
    print("✅ Enhanced synthetic dataset generated and saved to ./data/synthetic_ner_data.json")
