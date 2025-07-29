# generate_data.py
import random
import json
import os
import re
import datetime
from config import LABEL2ID
from sklearn.model_selection import train_test_split
import simple_icd_10 as icd
from idc_api import fetch_icd_description,get_token

diagnosis_icd10_map = {
    "Hypertonie": "I10",
    "Diabetes Mellitus": "E11.9",
    "Asthma": "J45",
    "Pneumonie": "J18.9"
}

vitalsigns = [
    "Blutdruck 120/80 mmHg", "Puls 72/min", "Temperatur 37,2 °C",
    "Sauerstoffsättigung 98 %"
]

lifestyles = [
    "Nichtraucher", "Raucher (5 Zigaretten/Tag)", "gelegentlicher Alkoholgenuss",
    "regelmäßige Bewegung"
]

risk_factors = [
    "familiäre Vorbelastung Diabetes", "Adipositas BMI 32",
    "Hyperlipidämie", "Schlafapnoe"
]

# Names and other data
names = ["Herr. Max Müller", "Patientin: Anna Schmidt", "L. Weber", "Frau Sophie Fischer","Otto Kromberger",
         "John Smith", "Mary Jones", "Robert Lee", "Emily Davis"]
doctors = ["Dr. Müller", "Dr. Schneider", "Dr. Becker", "Dr. Weber","Dr. Suhle Nikolas", "Dr. Lehmann", "Dr. Fischer", "Dr. Weber"
           "Dr. Adams", "Dr. Lee", "Dr. Patel", "Dr. Chen"]


symptoms = ["Brustschmerzen", "Atemnot", "Fieber", "Müdigkeit","dumpfe Kopfschmerzen", "Sehstörung", "Sprachstörung", "Kribbeln im linken Arm"],
medications = ["Metformin", "Lisinopril", "Albuterol", "Amoxicillin","Ramipril 5mg", "Metformin", "Schlafmedikamente"]
treatments = ["Sauerstofftherapie", "Operation", "Chemotherapie", "Physiotherapie"]
lab_results = ["Hb 13.5 g/dL", "Blutzucker 110 mg/dL", "Cholesterin 200 mg/dL","Glukose: 110 mg/dL"]
allergies = ["Penicillin", "Pollen", "Nüsse"]
immunizations = ["Masern-Impfung", "Grippeimpfung"]
devices = ["Herzschrittmacher", "Insulinpumpe","Schlafmaske", "Blutdruckgerät"]
family_histories = ["Mutter mit Diabetes", "Vater mit Bluthochdruck"]
procedures = ["Angioplastie", "MRT-Scan", "Biopsie", "Ultraschall","CT Kopf", "Lyse-Therapie"]
departments = ["Kardiologie", "Notaufnahme", "Onkologie", "Radiologie","Neurologie", "Innere Medizin"]

hospital_names = ["St. Marien Krankenhaus", "Allgemeine Gesundheitsklinik",
                  "Städtisches Medizinzentrum", "Universitätsklinikum München"]
hospital_addresses = ["Hauptstraße 12, 80331 München", "Berliner Allee 45, 40212 Düsseldorf",
                      "Lindenstraße 8, 10115 Berlin", "Goetheplatz 9, 50674 Köln"]
hospital_phones = ["089 123456", "0211 987654", "030 234567", "0221 456789"]


def __random_gender():
    return random.choice(["männlich", "weiblich", "divers"])


def __random_birthdate():
    start = datetime.date(1920, 1, 1)
    end = datetime.date(2025, 5, 31)
    rand_day = start + datetime.timedelta(days=random.randint(0, (end - start).days))
    return rand_day.strftime("%d.%m.%Y")


def __random_family_status():
    return random.choice(["ledig", "verheiratet", "geschieden", "verwitwet"])


def __random_date():
    start = datetime.date(2022, 1, 1)
    end = datetime.date(2024, 12, 31)
    rand_day = start + datetime.timedelta(days=random.randint(0, (end - start).days))
    return rand_day.strftime("%d. %B %Y")


def generate_report(token =  None):
    name = random.choice(names)
    doctor = random.choice(doctors)
    diagnosis = random.choice(list(diagnosis_icd10_map.keys()))
    icd10_code = diagnosis_icd10_map[diagnosis]

    icd_description = "Beschreibung unbekannt"
    if token : 
        icd_description = fetch_icd_description(icd10_code, token)
        if not icd_description:
            icd_description = icd.get_description(icd10_code)

    else : 
        icd_description = icd.get_description(icd10_code)
    


    date = __random_date()
    # Hospital
    idx  = random.randint(0, len(hospital_names) - 1)
    hospital_name, hospital_address, hospital_phone = hospital_names[idx ], hospital_addresses[idx ], hospital_phones[idx ]
    gender = __random_gender()
    birthdate = __random_birthdate()
    family_status = __random_family_status()

    vital = random.choice(vitalsigns) if random.choice([True, False]) else None
    lifestyle = random.choice(lifestyles) if random.choice([True, False]) else None
    riskfactor = random.choice(risk_factors) if random.choice([True, False]) else None




    # Follow-up
    followup_times = ["in 2 Wochen", "in 4 Wochen", "in einem Monat", "in 10 Tagen", "in drei Wochen"]
    followup_phrases = ["empfohlen", "dringend empfohlen", "zur weiteren Abklärung empfohlen"]
    followup_sentence = f"Eine erneute Kontrolluntersuchung wird {random.choice(followup_times)} {random.choice(followup_phrases)}."

    # Optional fields
    allergy = random.choice(allergies) if random.choice([True, False]) else None
    immunization = random.choice(immunizations) if random.choice([True, False]) else None
    device = random.choice(devices) if random.choice([True, False]) else None
    family_history = random.choice(family_histories) if random.choice([True, False]) else None


    general_templates = [
        f"Am {date} stellte sich Patient {name} ({gender}), geboren am {birthdate}, Familienstand: {family_status} mit {symptom} vor. Diagnose: {diagnosis}. "
        f"Behandlung: {medication} und {treatment}. Verfahren: {procedure}. "
        f"Untersuchung durch {doctor} in der Abteilung {department}. "
        f"Krankenhaus: {hospital_name}, {hospital_address}, Tel: {hospital_phone}. "
        f"Labor: {lab_result}. {followup_sentence}",

        f"{name} kam am {date} ins {hospital_name}, {hospital_address}. Beschwerden: {symptom}. "
        f"Untersuchung durch {doctor}. Diagnose: {diagnosis} (ICD‑10: {icd10_code} – {icd_description}). "
        f"Verabreichtes Medikament: {medication}. Eingriff: {procedure}. "
        f"Laborbefund: {lab_result}. Tel: {hospital_phone}.",

        f"Bei der Untersuchung am {date} im {hospital_name} wurde bei {name} {diagnosis} festgestellt. "
        f"Symptome: {symptom}. Behandelt mit {medication} und {treatment}. "
        f"Durchgeführt von {doctor} in der {department}. Labor: {lab_result}. "
        f"Adresse: {hospital_address}, Kontakt: {hospital_phone}.",
    ]

    structured_templates = [
        f"--- RADIOLOGY REPORT ---\nPatient: {name}\nDatum: {date}\nVerfahren: {procedure}\n"
        f"Indikation: {symptom}\nBefund: Zeichen einer {diagnosis}\nEmpfehlung: {treatment}\n"
        f"Radiologe: {doctor}\nAbteilung: {department}\n{hospital_name}, {hospital_address}\nTelefon: {hospital_phone}",

        f"--- FOLLOW-UP VISIT ---\nDatum: {date}\nPatient: {name}\nGrund: Nachuntersuchung wegen {symptom}\n"
        f"Vorherige Diagnose: {diagnosis} (ICD‑10: {icd10_code} – {icd_description})..\nAktueller Zustand stabil\n"
        f"Medikation: {medication}\nTherapie: {treatment}\nBehandelnder Arzt: {doctor}\n"
        f"Abteilung: {department}\nKlinik: {hospital_name}\nAdresse: {hospital_address}\nTelefon: {hospital_phone}",

        f"--- Entlassungsbrief---\nPatient: {name}\nAufnahme: {date}\nKlinik: {hospital_name}\nAbteilung: {department}\n"
        f"Hauptdiagnose: {diagnosis}\nBeschwerden bei Aufnahme: {symptom}\nBehandlung: {medication} und {treatment}\n"
        f"Eingriff: {procedure}\nVerantwortlicher Arzt: {doctor}\nEntlassung in stabilem Zustand\n"
        f"Kontrolluntersuchung empfohlen\nKontakt: {hospital_phone}",

        f"--- FOLLOW-UP RECOMMENDATION ---\nPatient: {name} ({gender}), geboren am {birthdate}, Familienstand: {family_status}.\n"
        f"Datum der letzten Untersuchung: {date}.\nBeschwerden: {symptom}. Diagnose: {diagnosis}.\n"
        f"Behandlung: {treatment} mit {medication}. Durchgeführt von {doctor}.\n"
        f"Empfehlung: {followup_sentence}\nBitte melden Sie sich bei der Abteilung {department} im {hospital_name}.\n"
        f"Adresse: {hospital_address}. Tel: {hospital_phone}."
    ]

    def add_optionals(tmpl_list):
        new_list = []
        for t in tmpl_list:
            if allergy:
                t += f"\nAllergien: {allergy}."
            if immunization:
                t += f"\nImpfungen: {immunization}."
            if device:
                t += f"\nMedizinisches Gerät: {device}."
            if family_history:
                t += f"\nFamilienanamnese: {family_history}."

            if vital:
                t += f"\nVitalzeichen: {vital}."
            if lifestyle:
                t += f"\nLebensstil: {lifestyle}."
            if riskfactor:
                t += f"\nRisikofaktor: {riskfactor}."

            new_list.append(t)
        return new_list

    # templates = add_optionals(general_templates + structured_templates)
    # text = random.choice(templates)


    # Generate synthetic sentence using paraphrasing + noise
    augmented_sentence = generate_augmented_sentence(entities)

    # Optional: blend with one of the structured templates
    templates = add_optionals(general_templates + structured_templates)
    fallback_sentence = random.choice(templates)

    # Mix structured and augmented text 50/50
    if random.random() < 0.5:
        text = fallback_sentence
    else:
        text = augmented_sentence


    symptom = random.choice(symptoms)
    medication = random.choice(medications)
    treatment = random.choice(treatments)
    procedure = random.choice(procedures)
    department = random.choice(departments)
    lab_result = random.choice(lab_results)



    # Entity dictionary
    entities = {
        name: "PERSON",
        doctor: "DOCTOR",
        date: "DATE",
        diagnosis: "DIAGNOSIS",
        random.choice(symptoms): "SYMPTOM",
        random.choice(medications): "MEDICATION",
        random.choice(treatments): "TREATMENT",
        random.choice(procedures): "PROCEDURE",
        random.choice(departments): "DEPARTMENT",
        hospital_name: "ORG",
        hospital_address: "ADDRESS",
        hospital_phone: "PHONE",
        gender: "GENDER",
        birthdate: "BIRTHDATE",
        family_status: "FAMILY_STATUS",
        icd10_code: "ICD10_CODE",
        icd_description: "ICD10_DESC",
    }
    if allergy: entities[allergy] = "ALLERGY"
    if immunization: entities[immunization] = "IMMUNIZATION"
    if device: entities[device] = "DEVICE"
    if family_history: entities[family_history] = "FAMILY_HISTORY"
    if vital:
        entities[vital] = "VITALSIGNS"
    if lifestyle:
        entities[lifestyle] = "LIFESTYLE"
    if riskfactor:
        entities[riskfactor] = "RISKFACTOR"


    match = re.search(r"(Eine erneute Kontrolluntersuchung wird .*? empfohlen)", text)
    if match:
        entities[match.group(1)] = "FOLLOWUP_RECOMMENDATION"

    return text, entities


def __simple_tokenize(text):
    return re.findall(r"\w+|[^\w\s]", text, re.UNICODE)

def inject_noise(text, typo_prob=0.05, punctuation_prob=0.05):
    def random_typo(word):
        if len(word) > 3 and random.random() < typo_prob:
            i = random.randint(1, len(word) - 2)
            return word[:i] + word[i+1] + word[i] + word[i+2:]
        return word

    def corrupt_punctuation(t):
        if random.random() < punctuation_prob:
            return t.replace(".", "") if "." in t else t + "."
        return t

    words = text.split()
    noisy_words = [random_typo(word) for word in words]
    noisy_text = " ".join(noisy_words)
    noisy_text = corrupt_punctuation(noisy_text)
    return noisy_text
def paraphrase_entity(entity_type, value):
    variations = {
        "DIAGNOSIS": [f"es wurde {value} diagnostiziert", f"Diagnose: {value}", f"leidet an {value}"],
        "MEDICATION": [f"bekommt {value}", f"Therapie mit {value}", f"{value} wurde verabreicht"],
        "SYMPTOM": [f"klagt über {value}", f"hat {value}", f"{value} wurde berichtet"],
        "DOCTOR": [f"behandelt durch {value}", f"untersucht von {value}", f"{value} führte die Untersuchung durch"],
        "PERSON": [f"Patient: {value}", f"Name: {value}", f"{value} stellte sich vor"],
        "ORG": [f"im Krankenhaus {value}", f"Einrichtung: {value}"],
        # Add more as needed...
    }
    if entity_type in variations:
        return random.choice(variations[entity_type])
    return value

def generate_augmented_sentence(entities, inject_noise_flag=True):
    pieces = []

    for value, ent_type in entities.items():
        phrase = paraphrase_entity(ent_type, value)
        if inject_noise_flag:
            phrase = inject_noise(phrase)
        pieces.append(phrase)

    random.shuffle(pieces)
    return ". ".join(pieces) + "."

def tokenize_and_label(text, entities):
    tokens = __simple_tokenize(text)
    labels = ["O"] * len(tokens)
    for entity_text, ent_type in entities.items():
        ent_tokens = entity_text.split()
        for i in range(len(tokens) - len(ent_tokens) + 1):
            if tokens[i:i+len(ent_tokens)] == ent_tokens:
                labels[i] = f"B-{ent_type}"
                for j in range(1, len(ent_tokens)):
                    labels[i+j] = f"I-{ent_type}"
                break
    label_ids = [LABEL2ID.get(l, 0) for l in labels]
    return tokens, label_ids




def __simple_tokenize(text):
    return re.findall(r"\w+|[^\w\s]", text, re.UNICODE)

def tokenize_and_label_improved(text, entities):
    tokens = __simple_tokenize(text)
    labels = ["O"] * len(tokens)

    for entity_text, entity_type in entities.items():
        entity_tokens = __simple_tokenize(entity_text)
        for i in range(len(tokens) - len(entity_tokens) + 1):
            if tokens[i:i+len(entity_tokens)] == entity_tokens:
                labels[i] = f"B-{entity_type}"
                for j in range(1, len(entity_tokens)):
                    labels[i+j] = f"I-{entity_type}"
                break

    return tokens, [LABEL2ID.get(label, 0) for label in labels]


def save_reports_as_txt(text, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)


def generate_dataset(n_samples=1000, save_report=False):

    ClientId = "db7c330e-8d75-450c-976c-e891ea61cf6a_8ba7953b-b758-4b5c-9f11-82eeff251802"
    ClientSecret = "3jf/LfXf6qsEE9la9/q8Hm3Jt4GAaVh2Vth06qQeSaY="
    #token = get_token(client_id= ClientId, client_secret= ClientSecret)
    data = []
    for i in range(n_samples):
        text, entities = generate_report(token = None)
        if save_report:
            filename = f"./txt_reports/report_{i+1}.txt"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            save_reports_as_txt(text, filename)
        tokens, labels = tokenize_and_label(text, entities)
        data.append({"tokens": tokens, "ner_tags": labels})

    train, val = train_test_split(data, test_size=0.1, random_state=42)
    os.makedirs("./data", exist_ok=True)
    with open("./data/train.json", "w", encoding="utf-8") as f:
        json.dump(train, f, indent=2, ensure_ascii=False)
    with open("./data/val.json", "w", encoding="utf-8") as f:
        json.dump(val, f, indent=2, ensure_ascii=False)

    print("✅ Synthetic dataset generated:")
    print(f"→ ./data/train.json ({len(train)} samples)")
    print(f"→ ./data/val.json ({len(val)} samples)")
    if save_report:
        print(f"→ ./txt_reports/reports ({i+1} samples)")


if __name__ == "__main__":
    generate_dataset(n_samples=1000)
