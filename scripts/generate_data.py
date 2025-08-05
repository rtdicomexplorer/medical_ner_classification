# generate_data.py
import random
import json
import os
import re
import datetime
from config import LABEL2ID, ID2LABEL, ENTITY_LIST
from utils import refresh_and_clean_ner_labels
from sklearn.model_selection import train_test_split
import simple_icd_10 as icd
from idc_api import fetch_icd_description,get_token

def generate_random_weight_height():
    # Gewicht zwischen 45 und 120 kg, auf 1 Dezimalstelle
    weight = round(random.uniform(45, 120), 1)
    # Größe zwischen 150 und 200 cm
    height = random.randint(150, 200)
    return f"{weight} kg",f"{height} cm"

# Beispielnutzung
weight, height = generate_random_weight_height()
print(f"Gewicht: {weight} kg")
print(f"Größe: {height} cm")
def add_random_dose(med_name):
    doses = [
        "5mg", "10mg", "20mg", "50mg", "100mg",
        "5ml", "10ml", "15ml", "100ml",
        "1g", "2g", "500mcg"
    ]
    dose = random.choice(doses)
    return f"{med_name} {dose}"

diagnosis_icd10_map = {
    "Hypertonie": "I10",
    "Diabetes Mellitus": "E11.9",
    "Asthma": "J45",
    "Pneumonie": "J18.9"
}

vitalsigns = [
    "Blutdruck 120/80 mmHg", 
    "Puls 72/min", 
    "Temperatur 37,2 °C",
    "Sauerstoffsättigung 98 %",
    "Atemfrequenz 16/min",
    "Taillenumfang 90 cm",
    "BMI 23.1 kg/m²",
    "Blutzucker (BZ) 110 mg/dL",
    "Temperatur rektal / tympanisch 38.2 °C",
    "Laktatwert 1.8 mmol/L",
    "Zentralvenöser Druck (ZVD) 5 mmHg"
]

lifestyles = [
    "Nichtraucher", "Raucher (5 Zigaretten/Tag)", "gelegentlicher Alkoholgenuss",
    "regelmäßige Bewegung","Drogenmissbrauch", "trinkt Bier täglich",
]

risk_factors = [
    "familiäre Vorbelastung Diabetes", "Adipositas BMI 32","Nikotinabusus"
    "Hyperlipidämie", "Schlafapnoe","Hypercholesterinämie", "RR erhöht","höheres Lebensalter"
]

# Names and other data
names = ["Herr. Max Müller", "Patientin: Anna Schmidt", "L. Weber", "Frau Sophie Fischer","Otto Kromberger",
         "John Smith", "Mary Jones", "Robert Lee", "Emily Davis"]
doctors = ["Dr. Müller", "Dr. Schneider", "Dr. Becker", "Dr. Weber","Dr. Suhle Nikolas", "Dr. Lehmann", "Dr. Fischer", "Dr. Weber",
           "Dr. Adams", "Dr. Lee", "Dr. Patel", "Dr. Chen"]


symptoms = [

    # 🧠 Neurologische Symptome
    "Kopfschmerzen",
    "Schwindel",
    "Sprachstörung",
    "Sehstörung",
    "Kribbeln",
    "Taubheitsgefühl",
    "Gangunsicherheit",
    "Lähmungen",
    "Bewusstseinsstörung",
    "Verwirrtheit",
    "Gedächtnisstörung",
    "Tremor",
    "Epileptischer Anfall",

    # ❤️ Kardiopulmonale Symptome
    "Brustschmerzen",
    "Atemnot",
    "Palpitationen",
    "Orthopnoe",
    "Husten",
    "Zyanose",
    "Druckgefühl in der Brust",
    "Kaltschweißigkeit",
    "Synkope",

    # 🧬 Allgemeine Symptome
    "Fieber",
    "Müdigkeit",
    "Appetitlosigkeit",
    "Gewichtsverlust",
    "Nachtschweiß",
    "Abgeschlagenheit",
    "Schlafstörung",
    "Konzentrationsstörung",
    "Gliederschmerzen",
    "Unwohlsein",

    # 🧑‍⚕️ Gastrointestinale Symptome
    "Übelkeit",
    "Erbrechen",
    "Bauchschmerzen",
    "Durchfall",
    "Verstopfung",
    "Blut im Stuhl",
    "Blähungen",
    "Appetitverlust",
    "Reflux",
    "Völlegefühl",

    # 🧪 Urologische Symptome
    "Schmerzen beim Wasserlassen",
    "Häufiger Harndrang",
    "Nykturie",
    "Harnverhalt",
    "Blut im Urin",
    "Inkontinenz",

    # 🔬 Dermatologische Symptome
    "Hautausschlag",
    "Juckreiz",
    "Schwellung",
    "Rötung",
    "Hautveränderungen"
]
medications = [

    # 💊 Blutdruckmedikamente (Antihypertensiva)
    "Ramipril",
    "Amlodipin",
    "Bisoprolol",
    "Lisinopril",
    "Valsartan",
    "Metoprolol",
    "Hydrochlorothiazid",
    "Candesartan",
    "Enalapril",

    # 💉 Antidiabetika
    "Metformin",
    "Insulin",
    "Empagliflozin",
    "Glimepirid",
    "Sitagliptin",
    "Dapagliflozin",

    # ❤️ Cholesterinsenker
    "Atorvastatin",
    "Simvastatin",
    "Rosuvastatin",
    "Pravastatin",

    # 🧠 Psychopharmaka & Schlafmittel
    "Diazepam",
    "Lorazepam",
    "Zolpidem",
    "Amitriptylin",
    "Mirtazapin",
    "Sertralin",
    "Citalopram",

    # 🩺 Schmerzmittel / NSAR
    "Ibuprofen",
    "Paracetamol",
    "ASS",
    "Diclofenac",
    "Naproxen",
    "Novalgin",
    "Metamizol",

    # 🦠 Antibiotika
    "Amoxicillin",
    "Ciprofloxacin",
    "Azithromycin",
    "Doxycyclin",
    "Clarithromycin",

    # 🫁 Asthma / COPD
    "Salbutamol",
    "Formoterol",
    "Budesonid",
    "Tiotropium",
    "Beclometason",

    # 🩸 Blutverdünner / Antikoagulantien
    "Marcumar",
    "Xarelto",
    "Eliquis",
    "Pradaxa",
    "Heparin",
    "Clopidogrel",

    # 🦴 Rheuma / Immunsuppressiva
    "Methotrexat",
    "Prednisolon",
    "Cortison",
    "Adalimumab",
    "Infliximab"
]

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
hospital_addresses = ["Hauptstraße 12, 80331 München", "Berliner Allee 45, 40212 Düsseldorf","Lindenstraße 8, 10115 Berlin", "Goetheplatz 9, 50674 Köln"]
hospital_phones = ["089 123456", "0211 987654", "030 234567", "0221 456789"]

followup_reasons = [
    "zur Blutdruckkontrolle", "wegen anhaltender Schmerzen", "zur Verlaufskontrolle"
]

impressions = [
    "Hinweis auf Pneumonie", "wahrscheinlich virale Ursache", "unklares Abdomen"
]

prev_diagnoses = [
    "frühere Appendizitis", "bekannte Arthrose", "chronische Bronchitis"
]
occupations = [
  "Gärtner", "Bäcker", "Metzger", "Professor", "Student", "Arbeitslose",
  "Händler", "Kaufmann", "Kauffrau", "Studentin", "Verkäuferin",
  "Lehrer", "Ärztin", "Ingenieur", "Friseur", "Journalist", "Sekretärin"
]

family_members = [
  "Bruder", "Schwester", "Mutter", "Vater", "Großvater", "Großmutter",
  "Onkel", "Kind", "Kinder", "Sohn", "Tochter", "Cousine", "Neffe", "Nichte"
]


def __random_gender():
    return random.choice(["männlich", "weiblich", "divers"])

def calculate_age(birthdate_str):
    birthdate = datetime.datetime.strptime(birthdate_str, "%d.%m.%Y").date()
    today = datetime.date.today()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))


def __random_birthdate(min_age=18, max_age=90):
    today = datetime.date.today()
    birth_year = today.year - random.randint(min_age, max_age)
    birth_month = random.randint(1, 12)
    birth_day = random.randint(1, 28)  # für Sicherheit
    birthdate = datetime.date(birth_year, birth_month, birth_day)
    return birthdate.strftime("%d.%m.%Y")  # z. B. 14.03.1975


def __random_family_status():
    return random.choice(["ledig", "verheiratet", "geschieden", "verwitwet"])


def __random_date(start_year=2015, end_year=2024):
    start = datetime.date(start_year, 1, 1)
    end = datetime.date(end_year, 12, 31)
    delta = end - start
    random_days = random.randint(0, delta.days)
    date = start + datetime.timedelta(days=random_days)
    return date.strftime("%d.%m.%Y")  # z. B. 27.06.2024


def random_optional_field(value_list):
    return random.choice(value_list) if random.choice([True, False]) else None

def random_choice_or_default(value_list, default="keine bekannt"):
    return random.choice(value_list) if random.random() < 0.5 else default

def generate_report(token=None):
    # Select core patient data
    name = random.choice(names)
    doctor = random.choice(doctors)
    diagnosis = random.choice(list(diagnosis_icd10_map.keys()))
    icd10_code = diagnosis_icd10_map[diagnosis]

    icd_description = icd.get_description(icd10_code) if not token else fetch_icd_description(icd10_code, token) or icd.get_description(icd10_code)

    date = __random_date(start_year=1980,end_year=2024)
    idx = random.randint(0, len(hospital_names) - 1)
    hospital_name, hospital_address, hospital_phone = hospital_names[idx], hospital_addresses[idx], hospital_phones[idx]
    gender = __random_gender()
    birthdate = __random_birthdate(min_age=1, max_age=95)
    family_status = __random_family_status()
    weight, height = generate_random_weight_height()

    symptom = random.choice(symptoms)
    medication = add_random_dose(random.choice(medications))
    treatment = random.choice(treatments)
    procedure = random.choice(procedures)
    department = random.choice(departments)
    lab_result = random.choice(lab_results)

    occupation = random.choice(occupations)
    family_member = random.choice(family_members)

    followup_times = ["in 2 Wochen", "in 4 Wochen", "in einem Monat", "in 10 Tagen", "in drei Wochen"]
    followup_phrases = ["empfohlen", "dringend empfohlen", "zur weiteren Abklärung empfohlen"]
    followup_sentence = f"Eine erneute Kontrolluntersuchung wird {random.choice(followup_times)} {random.choice(followup_phrases)}."

    allergy = random_optional_field(allergies)
    immunization = random_optional_field(immunizations)
    device = random_optional_field(devices)
    family_history = random_optional_field(family_histories)
    vital = random_optional_field(vitalsigns)
    lifestyle = random_optional_field(lifestyles)
    riskfactor = random_optional_field(risk_factors)

    impression = random_choice_or_default(impressions, "nicht dokumentiert")
    followup_reason = random_choice_or_default(followup_reasons, "keine Angabe")
    prev_diagnosis = random_choice_or_default(prev_diagnoses, "keine bekannt")

    # Build entity dictionary
    entities = {
        name: "PERSON",
        weight:"GEWICHT",
        height:"GROESSE",
        doctor: "DOCTOR",
        occupation: "OCCUPATION",
        family_member: "FAMILYMEMBER",
        date: "DATE",
        diagnosis: "DIAGNOSIS",
        symptom: "SYMPTOM",
        medication: "MEDICATION",
        treatment: "TREATMENT",
        procedure: "PROCEDURE",
        department: "DEPARTMENT",
        hospital_name: "ORG",
        hospital_address: "ADDRESS",
        hospital_phone: "PHONE",
        gender: "GENDER",
        birthdate: "BIRTHDATE",
        family_status: "FAMILY_STATUS",
        icd10_code: "ICD10_CODE",
        icd_description: "ICD10_DESC",
    }
    def add_entity_safe(key, label):
        if key and key not in entities:
            entities[key] = label


    add_entity_safe(allergy, "ALLERGY")
    add_entity_safe(immunization, "IMMUNIZATION")
    add_entity_safe(device, "DEVICE")
    add_entity_safe(family_history, "FAMHIS")
    add_entity_safe(vital, "VITALSIGNS")
    add_entity_safe(lifestyle, "LIFESTYLE")
    add_entity_safe(riskfactor, "RISKFACTOR")
    add_entity_safe(followup_sentence, "FlWUREC")
    add_entity_safe(followup_reason, "FlWUREASON")
  

    templates = [
        f"Am {date} stellte sich Patient {name} ({gender}), {height} per {weight} geboren am {birthdate}, Familienstand: {family_status} mit {symptom} vor, beschäftigt als {occupation} "
        f"Der {occupation} wurde mit starken Beschwerden von seiner {family_member} in die Klinik begleitet."
        f"Diagnose: {diagnosis}. "
        f"Vorherige Diagnose: {prev_diagnosis or 'keine bekannt'}. "
        f"Impression: {impression or 'nicht dokumentiert'}. "
        f"Behandlung: {medication} und {treatment}. Verfahren: {procedure}. "
        f"Untersuchung durch {doctor} in der Abteilung {department}. "
        f"Krankenhaus: {hospital_name}, {hospital_address}, Tel: {hospital_phone}. "
        f"Labor: {lab_result}. "
        f"Folgegrund: {followup_reason or 'keine Angabe'}. "
        f"{followup_sentence}",
        
        f"{name} kam am {date} ins {hospital_name}, {hospital_address} mit {family_member} Beschwerden: {symptom}. "
        f"Gewicht {weight} für eine Größe von {height} "
        f"Untersuchung durch {doctor}. Diagnose: {diagnosis} (ICD‑10: {icd10_code} – {icd_description}). "
        f"Vorherige Diagnose: {prev_diagnosis or 'keine bekannt'}. "
        f"Impression: {impression or 'nicht dokumentiert'}. "
        f"Verabreichtes Medikament: {medication}. Eingriff: {procedure}. "
        f"Laborbefund: {lab_result}. Tel: {hospital_phone}. "
        f"Folgegrund: {followup_reason or 'keine Angabe'}. {followup_sentence}",
        
        f"Bei der Untersuchung am {date} im {hospital_name} wurde bei {name} {diagnosis} festgestellt. "
        f"Symptome: {symptom}. Behandelt mit {medication} und {treatment}. "
        f"Durchgeführt von {doctor} in der {department}. Labor: {lab_result}. "
        f"Adresse: {hospital_address}, Kontakt: {hospital_phone}. "
        f"Vorherige Diagnose: {prev_diagnosis or 'keine bekannt'}. "
        f"Impression: {impression or 'nicht dokumentiert'}. "
        f"Folgegrund: {followup_reason or 'keine Angabe'}. {followup_sentence}",
        f"Die {family_member} des Patienten brachte ihn zur Untersuchung, da sie über anhaltende Beschwerden berichtete. "
        f"Der Patient wiegt {weight} für eine Größe von {height}"
        ,

        f"Der Patient arbeitet als {occupation} und lebt mit seiner {family_member} in einem gemeinsamen Haushalt. "
        f"Aufgrund seiner Tätigkeit als {occupation} ist der Patient häufig körperlich belastet, "
        f"was möglicherweise zur aktuellen Symptomatik beiträgt. "
        f"Der Patient gibt an, seine Arbeit als {occupation} derzeit nicht ausüben zu können. "
        f"In der Familie bestehen Vorerkrankungen: Die {family_member} des Patienten litt ebenfalls an {diagnosis}. "
        f"Der Patient wurde von seiner {family_member} wegen zunehmender {symptom} in die Klinik gebracht. "
        f"Der Patient wiegt {weight} für eine Größe von {height}"
        
       f"--- RADIOLOGY REPORT ---\n\n\nPatient: {name} ({gender}),  "
       f"geboren am {birthdate}\nDatum: {date}\nVerfahren: {procedure}\n  Beruf:{occupation}\n Gewicht: {weight} \n Größe: {height}\n"
        f"Begleitet von {family_member}\n"
        f"Indikation: {symptom}\nBefund: Zeichen einer {diagnosis}\nEmpfehlung: {treatment}\n"
        f"Radiologe: {doctor}\nAbteilung: {department}\n{hospital_name}, {hospital_address}\nTelefon: {hospital_phone}\n"
        f"Vorherige Diagnose: {prev_diagnosis or 'keine bekannt'}\nImpression: {impression or 'nicht dokumentiert'}\n"
        f"Folgegrund: {followup_reason or 'keine Angabe'}\n{followup_sentence}",

        f"--- FOLLOW-UP VISIT ---\n\n\nDatum: {date}\nPatient: {name} ({gender}), geboren am {birthdate} Gewicht: {weight} \n Größe: {height}\n"
        f"Arbeitet als {occupation}\n Grund: Nachuntersuchung wegen {symptom}\n "
        f"Vorherige Diagnose: {prev_diagnosis or 'keine bekannt'}\nImpression: {impression or 'nicht dokumentiert'}\n"
        f"Diagnose: {diagnosis} (ICD‑10: {icd10_code} – {icd_description})..\nAktueller Zustand stabil\n"
        f"Medikation: {medication}\nTherapie: {treatment}\nBehandelnder Arzt: {doctor}\n"
        f"Abteilung: {department}\nKlinik: {hospital_name}\nAdresse: {hospital_address}\nTelefon: {hospital_phone}\n"
        f"Folgegrund: {followup_reason or 'keine Angabe'}\n{followup_sentence}",

        f"--- Entlassungsbrief---\nPatient: {name} geboren am {birthdate}\nAufnahme: {date}\nKlinik: {hospital_name}\n"
        f"Abteilung: {department}\n"
        f"Hauptdiagnose: {diagnosis}\nBeschwerden bei Aufnahme: {symptom}\nBehandlung: {medication} und {treatment}\n"
        f"Eingriff: {procedure}\nVerantwortlicher Arzt: {doctor}\nEntlassung in stabilem Zustand\n"
        f"Kontrolluntersuchung empfohlen\nVorherige Diagnose: {prev_diagnosis or 'keine bekannt'}\n"
        f"Impression: {impression or 'nicht dokumentiert'}\nFolgegrund: {followup_reason or 'keine Angabe'}\n"
        f"Kontakt: {hospital_phone}\n{followup_sentence}",

        f"--- FOLLOW-UP RECOMMENDATION ---\nPatient: {name} ({gender}), geboren am {birthdate}, Familienstand: {family_status}."
        f"Im moment arbeitet er/sie als {occupation} \n"
        f"Er/sie muss begleitet werden mit {family_member} "
        f"Datum der letzten Untersuchung: {date}.\nBeschwerden: {symptom}. Diagnose: {diagnosis}.\n"
        f"Behandlung: {treatment} mit {medication}. Durchgeführt von {doctor}.\n"
        f"Empfehlung: {followup_sentence}\nBitte melden Sie sich bei der Abteilung {department} im {hospital_name}.\n"
        f"Adresse: {hospital_address}. Tel: {hospital_phone}.\n"
        f"Vorherige Diagnose: {prev_diagnosis or 'keine bekannt'}\nImpression: {impression or 'nicht dokumentiert'}\n"
        f"Folgegrund: {followup_reason or 'keine Angabe'}",
        f"--- Artzbrief\n\n\n\n"
        f"Patientenname : {name}\n\n"
        f"Geburtsdatum : {birthdate}\n\n"
        f"Gewicht: {weight}\n\n"
        f"Größe: {height} cm\n\n\n"
        f"Hausarzt : {doctor}.\n\n\n"
        f"Der Patient, {name} , stellte sich mit stark anhaltend dumpfen {symptom} vor, die er seit gestern habe."
        f"Herr {name} sei auch niedergeschlagen. Darüber hinaus berichte er über Kribbeln auf der linke Arm."
        f"Er habe auch berichtet, dass er eine Sehstörung und Sprachstörung (Wortfindungsstörung und lallende Ansprache) entwickelt "
        f"habe. Eine Schluckstörung wurde auch berichtet.\n"
        f"Vorerkrankungen : Er habe seit 20 Jahren Bluthochdruck.IM Jahr 2018 habe er einen Rippenbruch gehabt, "
        f"den konservativ behandelt wurde.\n"
        f"Vegetative Anamnese ist bis auf eine Schlafstörung, die seit 5 jähren bestehe und mit Schlafmedikamente eingestellt sei, "
        f"unauffällig.\n"
        f"Medikamente Anamnese : Er nehme die obergenannte Schlafmedikamente bei bedarf ein und er nehme auch {lab_result} "
        f"einmal morgens ein.\n"
        f"Noxen : Er habe täglich für 10 Jahren zehn Zigaretten geraucht , bevor er sich das Rauchen abgewöhnt habe. " 
        f"Alkohol trinke er nicht. Die Frage nach einem Drogenmissbrauch wurde verneint.\n"
        f"Soziale Anamnese : Er ist {occupation} von Beruf und ist verheiratet. Herr {name} lebe mit seiner {family_member} "
        f"und vier Kinder zusammen.\n"
        f"Familiäre Anamnese : Die Mutter des Patienten leide an Zuckerkrankheit und der {family_member} habe einen Schlaganfall"
        f"hinter sich.\n"
        f"Die Anamnese, Laborwerte und eine CT Kopf weisen auf einen Schlaganfall hin. Lyse-therapie wurde nach der CT begonnen.\n"

    ]


    # Generate text from template or augmented sentence
    if random.random() < 0.5:
        # Paraphrased version
        text, spans = __generate_augmented_sentence_with_spans(entities)
        # spans2 = build_spans(text, entities)
        tokens, labels = __char_spans_to_bio_labels(text, spans, LABEL2ID)
    else:
        # Use structured template
        template = random.choice(templates )


        # Optional field appending
        optional_fields = []
        if allergy: optional_fields.append(f"Allergien: {allergy}.")
        if immunization: optional_fields.append(f"Impfung: {immunization}.")
        if device: optional_fields.append(f"Gerät: {device}.")
        if family_history: optional_fields.append(f"Familienanamnese: {family_history}.")
        if vital: optional_fields.append(f"Vitalzeichen: {vital}.")
        if lifestyle: optional_fields.append(f"Lebensstil: {lifestyle}.")
        if riskfactor: optional_fields.append(f"Risikofaktor: {riskfactor}.")
        if optional_fields:
            template += "\n" + " ".join(optional_fields)

        text = template

        # spans = __find_entity_spans(text, entities)

        # bio_labels = __char_spans_to_bio_labels(text, spans, LABEL2ID)
        tokens, labels = __tokenize_and_label(text, entities)# before  entities
        labels = clean_ner_tags_generic(tokens, labels)
    return text, entities, tokens, labels

def clean_ner_tags_generic(tokens, ner_tags):
    clean_tags = ner_tags.copy()
    n = len(tokens)
    punctuation = {".", ",", ":", ";", "-", "(", ")", "?"}

    # Erweiterte Liste medizinischer Stoppwörter
   
    for i in range(n):
        token = tokens[i]
        label_id = clean_tags[i]
        label = ID2LABEL[label_id]

        # Satzzeichen immer O
        if token in punctuation:
            clean_tags[i] = LABEL2ID["O"]
            continue

        # Stoppwörter immer O
        if token.lower() in medical_stop_words:
            clean_tags[i] = LABEL2ID["O"]
            continue

    # BIO-Konsistenz prüfen und korrigieren (wie gehabt) ...
    for i in range(n):
        label_id = clean_tags[i]
        label = ID2LABEL[label_id]

        if label.startswith("I-"):
            entity_type = label.split("-", 1)[1]
            if i == 0:
                clean_tags[i] = LABEL2ID.get("B-" + entity_type, label_id)
            else:
                prev_label = ID2LABEL[clean_tags[i - 1]]
                prev_entity_type = prev_label.split("-", 1)[1] if "-" in prev_label else None
                if not (prev_entity_type == entity_type and prev_label.startswith(("B-", "I-"))):
                    clean_tags[i] = LABEL2ID.get("B-" + entity_type, label_id)

        if label.startswith("B-") and i > 0:
            entity_type = label.split("-", 1)[1]
            prev_label = ID2LABEL[clean_tags[i - 1]]
            prev_entity_type = prev_label.split("-", 1)[1] if "-" in prev_label else None
            if prev_label.startswith(("B-", "I-")) and prev_entity_type == entity_type:
                clean_tags[i] = LABEL2ID.get("I-" + entity_type, label_id)

    return clean_tags

medical_stop_words = {
    # Allgemeine Funktionswörter
    "und", "oder", "aber", "weil", "dass", "wenn", "während", "obwohl", "sowie",
    "nicht", "kein", "keine", "ohne", "mit", "von", "zu", "für", "über", "unter",
    "zwischen", "an", "bei", "in", "auf", "aus", "nach", "vor", "seit", "gegen",
    "wurde", "wird", "ist", "sind", "hat", "haben", "war", "waren", "sein",
    "der", "die", "das", "ein", "eine", "einer", "eines", "einem", "dem", "den",
    "des", "dieser", "dieses", "jener", "jenes",

    # Häufige medizinische Füllwörter / Verben
    "diagnostiziert", "festgestellt", "behandelt", "therapiert", "verabreicht",
    "geführt", "untersucht", "festgestellt", "bericht", "berichtet", "angaben",
    "auffällig", "normal", "nicht", "wurde", "wurden", "zeigt", "klagt",
    "beschreibt", "leidet", "auftreten", "auftreten", "kommt", "besteht", "zeigt",
    "beinhaltet", "bedeutet", "notwendig", "erforderlich", "empfohlen",

    # Allgemeine zeitliche und organisatorische Begriffe
    "datum", "zeitpunkt", "vorherige", "frühere", "aktuelle", "derzeitige",
    "patient", "person", "patientin", "patienten", "bericht", "berichtet",
    "einrichtung", "klinik", "abteilung", "station", "arzt", "ärztin", "dr",
    "prof", "professor", "untersuchung", "verfahren", "befund", "impression",
    "diagnose", "therapie", "medikation", "medikament", "allergie", "risikofaktor",
    "symptom", "zeichen",

    # Häufige Messwerte und Vitalparameter
    "temperatur", "puls", "blutdruck", "atemfrequenz", "gewicht", "größe", "größe",
    "werte", "parameter",

    # Weitere allgemeine Wörter
    "es", "er", "sie", "wir", "ich", "man", "sich"
}

def __simple_tokenize(text):
    return re.findall(r"\w+|[^\w\s]", text, re.UNICODE)

def __inject_noise(text, typo_prob=0.05, punctuation_prob=0.05):
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


def __char_spans_to_bio_labels(text, spans, label_map):
    """
    Convert character spans to BIO labels aligned with tokenized text.
    
    Args:
        text (str): The generated sentence.
        spans (list): List of tuples (start_char, end_char, entity_type).
        label_map (dict): Mapping from BIO labels (like 'B-DIAGNOSIS') to IDs.
        
    Returns:
        tokens (list of str)
        bio_labels (list of int)  # label IDs aligned with tokens
    """

    # Simple tokenization (keep punctuation separate)
    tokens = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)
    
    # Track char position for each token
    token_positions = []
    pos = 0
    for token in tokens:
        start = text.find(token, pos)
        end = start + len(token)
        token_positions.append((start, end))
        pos = end

    # Initialize labels to "O"
    bio_labels = ["O"] * len(tokens)

    for start_char, end_char, ent_type in spans:
        # Assign B- and I- labels for tokens within the span
        # Find all tokens that fall inside this char span
        inside_tokens = []
        for i, (tok_start, tok_end) in enumerate(token_positions):
            # Check if token overlaps with entity span
            if not (tok_end <= start_char or tok_start >= end_char):
                inside_tokens.append(i)

        if not inside_tokens:
            continue  # no tokens matched? skip

        # Assign labels
        bio_labels[inside_tokens[0]] = f"B-{ent_type}"
        for idx in inside_tokens[1:]:
            bio_labels[idx] = f"I-{ent_type}"

    # Convert label strings to IDs
    label_ids = [label_map.get(lbl, 0) for lbl in bio_labels]

    return tokens, label_ids

def __paraphrase_entity(entity_type, value):
    variations = {
        "PERSON": [
            f"Patient: {value}",
            f"Name: {value}",
            f"{value} stellte sich vor",
            f"Betroffene Person: {value}"
        ],
        "BIRTHDATE":[
            f"geboren am: {value}",
            f"Geburtsdatum: {value}",
        ],
        "FAMILY_STATUS":[
           f"begleitet von {value}",
           f"bei sich hat {value}" 
        ],
        "VITALSIGNS":[
            f"{value}",
        ],

        "IMMUNIZATION":[
            f"Impfungen: {value}",
            f"geimpft gegen {value}"
        ],
        "OCCUPATION":[
            f"aktueller Beruf: {value}",
            f"is {value} von Beruf",
            f"er ist {value}",
            f"arbeitet als {value}",
            f"keine Beschäftigung",
        ],
        "ALLERGY":[
            f"allergisch auf: {value}",
            f"bekannte Allergien: {value}"
            f"Allergien: {value}"
            ],
        "DIAGNOSIS": [
            f"es wurde {value} diagnostiziert",
            f"Diagnose: {value}",
            f"leidet an {value}",
            f"{value} wurde festgestellt"
        ],
        "MEDICATION": [
            f"bekommt {value}",
            f"Therapie mit {value}",
            f"{value} wurde verabreicht",
            f"Medikation: {value}"
        ],
        "SYMPTOM": [
            f"klagt über {value}",
            f"hat {value}",
            f"{value} wurde berichtet",
            f"zeigt Symptome von {value}"
        ],
        "DOCTOR": [
            f"behandelt durch {value}",
            f"untersucht von {value}",
            f"{value} führte die Untersuchung durch",
            f"Arzt: {value}"
        ],

        "ORG": [
            f"im Krankenhaus {value}",
            f"Einrichtung: {value}",
            f"im {value}",
            f"Klinik: {value}"
        ],
        "DATE": [
            f"am {value}",
            f"Datum: {value}",
            f"am Untersuchungsdatum {value}",
            f"Datum des Berichts: {value}"
        ],
        "DEVICE":[
            "es wird empfohlen {value} zu verwenden",
            "{value} wird verwendet",
        ],
        "FAMHIST":[
            f"in der Familie gab es schon fälle mit {value}",
        ],

        "RISKFACTOR":[
            f"mögliche Risikofaktoren: {value}",
            f"es sind {value} möglich",
            f"es bestehen {value}"
        ]
        # add more as needed
    }
    if entity_type in variations:
        return random.choice(variations[entity_type])
    return value
import re
def __get_random_filler():
    fillers = [
        "Der Patient befindet sich in einem stabilen Allgemeinzustand.",
        "Weitere Angaben folgen im Verlauf.",
        "Keine Auffälligkeiten im aktuellen Befund.",
        "Es wurde ein Gespräch zur weiteren Aufklärung geführt.",
        "Die Patientin äußerte keine zusätzlichen Beschwerden.",
        "Untersuchungsergebnisse stehen noch aus.",
    ]
    return random.choice(fillers)

def __generate_augmented_sentence_with_spans(entities, inject_noise_flag=True):
    """
    Generate a coherent sentence from entities, return text and entity spans.
    
    entities: dict of {entity_text: entity_type}
    
    Returns:
        text: generated sentence (string)
        spans: list of tuples (start_char, end_char, entity_type)
    """

    # Define a logical order for entity types for better flow
   # order = ['PERSON', 'SYMPTOM', 'DIAGNOSIS', 'MEDICATION', 'TREATMENT', 'DOCTOR', 'ORG', 'DATE']

    pieces = []
    spans = []
    current_pos = 0

    def safe_inject_noise(text):
        return __inject_noise(text) if inject_noise_flag else text

    # Helper to add phrase and track span
    def add_phrase(phrase, ent_type):
        nonlocal current_pos
        start = current_pos
        pieces.append(phrase)
        current_pos += len(phrase)
        end = current_pos
        spans.append((start, end, ent_type))
        # add space after phrase except last
        pieces.append(" ")
        current_pos += 1
        if random.random() < 0.3:
            filler = __get_random_filler()
            pieces.append(filler)
            pieces.append(" ")
            current_pos += len(filler) + 1

    # Compose sentence piecewise in order
    for ent_type in ENTITY_LIST:

        ent_items = list(entities.items())
        random.shuffle(ent_items)
        for value, etype in entities.items():
            if etype == ent_type:
                phrase = __paraphrase_entity(ent_type, value)
                add_phrase(phrase, ent_type)
            

    text = "".join(pieces).strip()

    # Fix trailing punctuation (optional)
    if not text.endswith("."):
        text += "."
    text = safe_inject_noise(text)# the length could be change 

    return text, spans


def __tokenize_and_label(text, entities):
    tokens = __simple_tokenize(text)
    labels = ["O"] * len(tokens)

    for entity_text, ent_type in entities.items():
        ent_tokens = __simple_tokenize(entity_text)
        n = len(ent_tokens)
        for i in range(len(tokens) - n + 1):
            if [t.lower() for t in tokens[i:i+n]] == [t.lower() for t in ent_tokens]:
                if all(label == "O" for label in labels[i:i+n]):
                    labels[i] = f"B-{ent_type}"
                    for j in range(1, n):
                        labels[i+j] = f"I-{ent_type}"

    label_ids = [LABEL2ID.get(label, 0) for label in labels]
    return tokens, label_ids


def __simple_tokenize(text):
    # Token: Wörter, Zahlen mit Punkt oder Slash, oder einzelne Satzzeichen
    pattern = r"\d+[\./]?\d*|\w+|[^\w\s]"
    return re.findall(pattern, text, re.UNICODE)



def __save_reports_as_txt(text, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)

def __validate_bio_sequence(tokens, tags):
    for i, tag in enumerate(tags):
        label = ID2LABEL[tag]
        if label.startswith("I-"):
            if i == 0 or ID2LABEL[tags[i-1]][2:] != label[2:]:
                print(f"❌ Ungültiger I-Tag ohne vorheriges B-Tag bei Token {i}: '{tokens[i]}' → {label}")
        if label == "O" and tokens[i] in [".", ",", ":", ";"]:
            continue  # OK

def generate_dataset(n_samples=1000, save_reports=False):

    ClientId = "db7c330e-8d75-450c-976c-e891ea61cf6a_8ba7953b-b758-4b5c-9f11-82eeff251802"
    ClientSecret = "3jf/LfXf6qsEE9la9/q8Hm3Jt4GAaVh2Vth06qQeSaY="
    #token = get_token(client_id= ClientId, client_secret= ClientSecret)
    data = []
    for i in range(n_samples):
        text, entities, tokens, labels = generate_report(token=None)

        # we need to validate if the results, it they match with LABEL...
        __validate_bio_sequence(tokens,labels)

        if save_reports:
            filename = f"./txt_reports/report_{i+1}.txt"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            __save_reports_as_txt(text, filename)

        data.append({
            "tokens": tokens,
            "ner_tags": labels
        })

    from collections import Counter
    clean_data = refresh_and_clean_ner_labels(data= data, id2label= ID2LABEL, threshold= 0.95)
    all_labels = [label for sample in clean_data for label in sample["ner_tags"]]
    print(Counter(all_labels))



    # Split train/val
    trains, validations = train_test_split(clean_data, test_size=0.1, random_state=42)
    trains, tests = train_test_split(trains, test_size=0.1, random_state=42)
    
    os.makedirs("./data", exist_ok=True)

    with open("./data/train.json", "w", encoding="utf-8") as f:
        json.dump(trains, f, indent=2, ensure_ascii=False)
    with open("./data/val.json", "w", encoding="utf-8") as f:
        json.dump(validations, f, indent=2, ensure_ascii=False)
    with open("./data/test.json", "w", encoding="utf-8") as f:
        json.dump(tests, f, indent=2, ensure_ascii=False)
    print("✅ Synthetic dataset generated:")
    print(f"→ ./data/train.json ({len(trains)} samples)")
    print(f"→ ./data/val.json ({len(validations)} samples)")
    print(f"→ ./data/test.json ({len(tests)} samples)")
    if save_reports:
        print(f"→ ./txt_reports/ ({n_samples} samples)")


# Run as script
if __name__ == "__main__":
    import sys
    n_samples = 1000
    save_reports = False
    if len(sys.argv) > 1:
        n_samples = int(sys.argv[1])
    if len(sys.argv) > 2:
        save_reports = sys.argv[2].lower() == 'true'
    print(f"Starting generation of {n_samples} data. Saving reports is {save_reports}!")
    generate_dataset(n_samples=n_samples, save_reports=save_reports)

