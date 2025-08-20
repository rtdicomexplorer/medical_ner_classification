# generate_data.py
import random
import json
import os
import re
import datetime
from config import LABEL2ID, ID2LABEL, ENTITY_LIST
from utils import *
from sklearn.model_selection import train_test_split
import simple_icd_10 as icd
from idc_api import fetch_icd_description,get_token
import uuid



def __add_random_dose(med_name):
    doses = [
        "5mg", "10mg", "20mg", "50mg", "100mg",
        "5ml", "10ml", "15ml", "100ml",
        "1g", "2g", "500mcg"
    ]
    dose = random.choice(doses)
    return f"{med_name} {dose}"
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
    return random.choice(family_status)





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

    date = random_date(start_year=1980,end_year=2024)
    idx = random.randint(0, len(hospital_names) - 1)
    hospital_name, hospital_address, hospital_phone = hospital_names[idx], hospital_addresses[idx], hospital_phones[idx]
    gender = __random_gender()
    birthdate = __random_birthdate(min_age=1, max_age=95)
    family_status = __random_family_status()
    weight = generate_random_weight
    height = generate_random_height()
    pid = generate_patint_id()

    symptom = random.choice(symptoms)
    medication = __add_random_dose(random.choice(medications))
    treatment = random.choice(treatments)
    procedure = random.choice(procedures)
    department = random.choice(departments)
    lab_result = random.choice(lab_results)
    finding = random.choice(findings)
    occupation = random.choice(occupations)
    family_member = random.choice(family_members)
    document_type = random.choice(document_types)
  
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
        hospital_address: "ADDRESS",
        birthdate: "BIRTHDATE",
        date: "DATE",
        department: "DEPARTMENT",
        diagnosis: "DIAGNOSIS",
        doctor: "DOCTOR",
        document_type:'DOCUMENT_TYPE',
        family_member: "FAMILYMEMBER",
        family_status: "FAMILY_STATUS",
        finding: "FINDING",
        gender: "GENDER",
        weight: "GEWICHT",
        height: "GROESSE",
        icd10_code: "ICD10_CODE",
        icd_description: "ICD10_DESC",
        impression: "IMPRESSION",
        lab_result: "LAB_RESULT",
        medication: "MEDICATION",
        name: "PERSON",
        occupation: "OCCUPATION",
        pid: "PID",
        prev_diagnosis: "PREV_DIAGNOSIS",
        procedure: "PROCEDURE",
        symptom: "SYMPTOM",
        treatment: "TREATMENT",
        hospital_name: "ORG",
        hospital_phone: "PHONE"
    }
    def add_entity_safe(key, label):
        if key and key not in entities:
            entities[key] = label
        add_entity_safe(allergy, "ALLERGY")
        add_entity_safe(device, "DEVICE")
        add_entity_safe(family_history, "FAMHIST")
        add_entity_safe(followup_sentence, "FOLLOWUP_REQ")
        add_entity_safe(followup_reason, "FOLLOWUP_REASON")
        add_entity_safe(immunization, "IMMUNIZATION")
        add_entity_safe(lifestyle, "LIFESTYLE")
        add_entity_safe(riskfactor, "RISKFACTOR")
        add_entity_safe(vital, "VITALSIGNS")
   
        
    
  

    templates = [
        
        f"{document_type}:\n  Am {date} stellte sich der Patient {name} (männlich), {height} per {weight} geboren am {birthdate}, Familienstand: {family_status}, "
        f"der Patient stellt folgenden Symptome  {symptom} vor, beschäftigt als {occupation} "
        f"Der Patient wurde mit starken Beschwerden von seiner {family_member} in die Klinik begleitet."
        f"Diagnose: {diagnosis}. \n"
        f"Familienanamnese: {family_history}. \n" 
        f"Vorherige Diagnose: {prev_diagnosis or 'keine bekannt'}. \n"
        f"Impression: {impression or 'nicht dokumentiert'}. \n"
        f"Behandlung: {medication} und {treatment}. Verfahren: {procedure}. \n"
        f"Untersuchung durch {doctor} in der Abteilung {department}. \n"
        f"Krankenhaus: {hospital_name}, {hospital_address}, Tel: {hospital_phone}. \n"
        f"Labor: {lab_result}. \n"
        f"Folgegrund: {followup_reason or 'keine Angabe'}. "
        f"{followup_sentence}",
        

        f"{document_type}:\n Am {date} stellte sich die Patientin {name} (weiblich), {height} per {weight} geboren am {birthdate} vor, "
        f"Familienstand: {family_status}, die Patientin stellt folgenden Symptome  {symptom} vor, sie beschäftigt sich als {occupation} "
        f"Sie wurde mit starken Beschwerden von ihren {family_member} in die Klinik begleitet.\n"
        f"Diagnose: {diagnosis}. \n"
        f"Familienanamnese: {family_history}. \n" 
        f"Vorherige Diagnose: {prev_diagnosis or 'keine bekannt'}. \n"
        f"Impression: {impression or 'nicht dokumentiert'}. \n"
        f"Behandlung: {medication} und {treatment}.\n Verfahren: {procedure}. \n"
        f"Untersuchung durch {doctor} in der Abteilung {department}. \n"
        f"Krankenhaus: {hospital_name}, {hospital_address}, Tel: {hospital_phone}. \n"
        f"Labor: {lab_result}. \n"
        f"Folgegrund: {followup_reason or 'keine Angabe'}. "
        f"{followup_sentence}",
        
        
        f"{document_type}:\n {name} ({gender}) id: {pid}, kam am {date} ins {hospital_name}, {hospital_address} mit {family_member}. \n"
        f"Beschwerden: {symptom}.  \n"
        f"Gewicht {weight} für eine Größe von {height} \n"
        f"Untersucht von {doctor}. Diagnose: {diagnosis} (ICD‑10: {icd10_code} – {icd_description}). \n"
        f"Vorherige Diagnose: {prev_diagnosis or 'keine bekannt'}. \n"
        f"Impression: {impression or 'nicht dokumentiert'}. \n"
        f"Familiäre Häufung: {family_history}. \n"
        f"Verabreichtes Medikament: {medication}. Eingriff: {procedure}. \n"
        f"Laborbefund: {lab_result}. Tel: {hospital_phone}. \n"
        f"Folgegrund: {followup_reason or 'keine Angabe'}. {followup_sentence} \n",
        


        f"{document_type}:\n Finding: Brustpa-lat-XR-Bildgebungsstudie Xray Chest PA und laterale Untersuchung: 2 Ansichten der Brust left/lat."
        f"Vergleich: Keine."
        f"Indikation: Positive TB -Testbefunde: Die Herz -Silhouette- und Mediastinumgröße liegt innerhalb der normalen Grenzen. "
        f"Es gibt kein Lungenödem. Es gibt keine fokale Konsolidierung. Es gibt keine Hinweise eines Pleura -Ergusss. "
        f"Es gibt keine Hinweise auf Pneumothorax. Eindruck: Normale Brust. Diese Prüfung und die gemeldeten Ergebnisse wurden vom Unterzeichneten überprüft und bestätigt."
        f"{doctor} {department} {hospital_name}  {hospital_address}, Kontakt: {hospital_phone}. ",

        f"{document_type}:\n Prüfung am {date} der Radiologiebericht PA und laterale Ansichten der Brust {name} bei 12 Stunden Historie: 19-Jähriger mädchen mit {family_history}. Vergleich: Keine verfügbaren Ergebnisse: Es gibt diffuse bilaterale interstitielle und alveoläre Opazitäten, die mit chronisch obstruktiven Lungenerkrankungen und Bullous -Emphysem übereinstimmen. Es gibt unregelmäßige Opaces in der linken Lungenspitze, die eine kavitäre Läsion in der linken Lungenspitze darstellen könnten. In der rechten oberen Lappen, XXXX -Narben, befinden sich streikige Opaces. Die kardiomediastinale Silhouette ist normal in Größe und Kontur. Es gibt keinen Pneumothorax oder keinen großen Pleura -Erguss. Transkribiert durch - PSC -Transkriptionsdatum - XXXX -Eindruck 1. Bullous Emphysem und Interstitial -Fibrose. 2. Wahrscheinlich Narben in der linken Spitze, obwohl es schwierig ist, eine kavitäre Läsion auszuschließen. 3. Opacities in den bilateralen oberen Lappen könnten Narben darstellen. Das Fehlen einer Vergleichsprüfung empfiehlt jedoch kurze Intervall -Followup Röntgenaufnahme oder CT -Thorax, um die Auflösung zu dokumentieren. Signatur {doctor},"
        f"{hospital_name}  Adresse: {hospital_address}, Kontakt: {hospital_phone} {department} ",

        f"{document_type}:\n Bei der Untersuchung am {date} im {hospital_name} wurde bei {name} {gender} id: {pid}  folgend {diagnosis} festgestellt. "
        f"Symptome: {symptom}. Behandelt mit {medication} und {treatment}. "
        f"Durchgeführt von {doctor} in der {department}. Labor: {lab_result}. "
        f"Adresse: {hospital_address}, Kontakt: {hospital_phone}. "
        f"Vorherige Diagnose: {prev_diagnosis or 'keine bekannt'}. "
        f"Impression: {impression or 'nicht dokumentiert'}. "
        f"Genetische Vorbelastung: {family_history}. "
        f"Folgegrund: {followup_reason or 'keine Angabe'}. {followup_sentence}"
        f"Die {family_member} des Patienten brachte ihn zur Untersuchung, da sie über anhaltende Beschwerden berichtete. "
        f"Der Patient wiegt {weight} für eine Größe von {height}",

        f"{document_type}:\n Der Patient arbeitet als {occupation} und lebt mit seiner {family_member} in einem gemeinsamen Haushalt. "
        f"Aufgrund seiner Tätigkeit als {occupation} ist der Patient häufig körperlich belastet, "
        f"was möglicherweise zur aktuellen Symptomatik beiträgt. Als familiäre Disposition {family_history} "
        f"Der Patient gibt an, seine Arbeit als {occupation} derzeit nicht ausüben zu können. "
        f"In der Familie bestehen Vorerkrankungen: Die {family_member} des Patienten litt ebenfalls an {diagnosis}. "
        f"Der Patient wurde von seiner {family_member} wegen zunehmender {symptom} in die Klinik gebracht. "
        f"Der Patient wiegt {weight} für eine Größe von {height}."
        f"Familienanamnese: {family_history}. " 
        f"Patient ist {gender} und hat eine: {pid}",
        
       f"{document_type}:\n Patient: {name} ({gender}) "
       f"geboren am {birthdate}\nDatum: {date}\nVerfahren: {procedure}\n  Beruf:{occupation}\n Gewicht: {weight} \n Größe: {height}\n"
        f"Begleitet von {family_member},\n"
        f"Es stellt sich eine genetische Vorbelastung {family_history} vor. "
        f"Indikation: {symptom}\nBefund: Zeichen einer {diagnosis}\nEmpfehlung: {treatment}\n"
        f"Radiologe: {doctor}\nAbteilung: {department}\n{hospital_name}, {hospital_address}\nTelefon: {hospital_phone}\n"
        f"Vorherige Diagnose: {prev_diagnosis or 'keine bekannt'}\nImpression: {impression or 'nicht dokumentiert'}\n"
        f"Folgegrund: {followup_reason or 'keine Angabe'}\n{followup_sentence}",

        f"--- FOLLOW-UP VISIT ---\n\n{document_type}:\n \nDatum: {date}\nPatient: {name} ({gender}), id:{pid}, geboren am {birthdate} Gewicht: {weight} \n Größe: {height}\n"
        f"Arbeitet als {occupation}\n Grund: Nachuntersuchung wegen {symptom}\n "
        f"Vorherige Diagnose: {prev_diagnosis or 'keine bekannt'}\nImpression: {impression or 'nicht dokumentiert'}\n"
        f"Diagnose: {diagnosis} (ICD‑10: {icd10_code} – {icd_description})..\nAktueller Zustand stabil\n"
        f"Medikation: {medication}\nTherapie: {treatment}\nBehandelnder Arzt: {doctor}\n"
        f"Abteilung: {department}\nKlinik: {hospital_name}\nAdresse: {hospital_address}\nTelefon: {hospital_phone}\n"
        f"Folgegrund: {followup_reason or 'keine Angabe'}\n{followup_sentence}",

        f"---- {document_type} ----:\nPatient: {name} geboren am {birthdate}\nAufnahme: {date}\nKlinik: {hospital_name}\n Patient id:: {pid} .\n"
        f"Abteilung: {department}\n"
        f"Hauptdiagnose: {diagnosis}\nBeschwerden bei Aufnahme: {symptom}\nBehandlung: {medication} und {treatment}\n"
        f"Eingriff: {procedure}\nVerantwortlicher Arzt: {doctor}\nEntlassung in stabilem Zustand\n"
        f"Kontrolluntersuchung empfohlen\nVorherige Diagnose: {prev_diagnosis or 'keine bekannt'}\n"
        f"Impression: {impression or 'nicht dokumentiert'}\nFolgegrund: {followup_reason or 'keine Angabe'}\n"
        f"Kontakt: {hospital_phone}\n{followup_sentence}",

        f"{document_type}:\n \nPatient: {name} ({gender}), geboren am {birthdate}, Familienstand: {family_status}."
        f"Im moment arbeitet er/sie als {occupation} \n"
        f"Er/sie muss begleitet werden mit {family_member} "
        f"Datum der letzten Untersuchung: {date}.\nBeschwerden: {symptom}. Diagnose: {diagnosis}.\n"
        f"Behandlung: {treatment} mit {medication}. Durchgeführt von {doctor}.\n"
        f"Empfehlung: {followup_sentence}\nBitte melden Sie sich bei der Abteilung {department} im {hospital_name}.\n"
        f"Adresse: {hospital_address}. Tel: {hospital_phone}.\n"
        f"Vorherige Diagnose: {prev_diagnosis or 'keine bekannt'}\nImpression: {impression or 'nicht dokumentiert'}\n"
        f"Folgegrund: {followup_reason or 'keine Angabe'}\n"
        f"Familiäre Anamnese : {family_history}",
        f"--- {document_type}:\n \n\n"
        f"Patientenname : {name}\n"
        f"Geschlecht: {gender}\n"
        f"Geburtsdatum : {birthdate}\n"
        f"Gewicht: {weight}\n"
        f"Größe: {height} cm\n"
        f"Hausarzt : {doctor}.\n"
        f"ID: {pid}.\n\n"
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
        if vital: optional_fields.append(f"Vitalzeichen: {vital}.")
        if lifestyle: optional_fields.append(f"Lebensstil: {lifestyle}.")
        if riskfactor: optional_fields.append(f"Risikofaktor: {riskfactor}.")
        if optional_fields:
            template += "\n" + " ".join(optional_fields)
        text = template
        tokens, labels = __tokenize_and_label2(text, entities)# before  entities

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
                phrase = paraphrase_entity(ent_type, value)
                add_phrase(phrase, ent_type)
            

    text = "".join(pieces).strip()

    # Fix trailing punctuation (optional)
    if not text.endswith("."):
        text += "."
    text = safe_inject_noise(text)# the length could be change 

    return text, spans



def __tokenize_and_label2(text, entities_dict):
    tokens = __simple_tokenize(text)
    labels = ["O"] * len(tokens)

    # Sortiere Entitäten nach Länge (damit lange zuerst gematcht werden)
    sorted_entities = sorted(entities_dict.items(), key=lambda x: len(__simple_tokenize(x[0])), reverse=True)

    for entity_text, ent_type in sorted_entities:
        ent_tokens = __simple_tokenize(entity_text)
        n = len(ent_tokens)
        if n == 0:
            continue

        for i in range(len(tokens) - n + 1):
            # Lowercase-Vergleich
            token_slice = tokens[i:i+n]
            if [t.lower() for t in token_slice] == [t.lower() for t in ent_tokens]:
                # Stelle sicher, dass wir keine Labels überschreiben
                if all(label == "O" for label in labels[i:i+n]):
                    labels[i] = f"B-{ent_type}"
                    for j in range(1, n):
                        labels[i+j] = f"I-{ent_type}"

    return tokens, [LABEL2ID.get(label, 0) for label in labels]


def __simple_tokenize(text):
    # Token: Wörter, Zahlen mit Punkt oder Slash, oder einzelne Satzzeichen
    pattern = r"\d+[\./]?\d*|\w+|[^\w\s]"
    return re.findall(pattern, text, re.UNICODE)


def __validate_bio_sequence(tokens, tags):
    for i, tag in enumerate(tags):
        label = ID2LABEL[tag]
        if label.startswith("I-"):
            if i == 0 or ID2LABEL[tags[i-1]][2:] != label[2:]:
                print(f"❌ Ungültiger I-Tag ohne vorheriges B-Tag bei Token {i}: '{tokens[i]}' → {label}")
        if label == "O" and tokens[i] in [".", ",", ":", ";"]:
            continue  # OK


from tqdm import tqdm
def generate_dataset(n_samples=1000, save_reports=False, clean_data = False):

    ClientId = "db7c330e-8d75-450c-976c-e891ea61cf6a_8ba7953b-b758-4b5c-9f11-82eeff251802"
    ClientSecret = "3jf/LfXf6qsEE9la9/q8Hm3Jt4GAaVh2Vth06qQeSaY="
    #token = get_token(client_id= ClientId, client_secret= ClientSecret)
    data = []
    #for i in range(n_samples):
    for i in tqdm(range(n_samples), desc="Generating dataset", ncols=80):
        text, entities, tokens, labels = generate_report(token=None)

        # we need to validate if the results, it they match with LABEL...
        __validate_bio_sequence(tokens,labels)

        if save_reports:
            filename = f"./txt_reports/report_{i+1}.txt"
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            with open(filename, "w", encoding="utf-8") as f:
                f.write(text)


            entity_filename = f"./entities/entity_{i+1}.json"
            os.makedirs(os.path.dirname(entity_filename), exist_ok=True)
            with open(entity_filename, 'w',encoding="utf-8") as f:
                json.dump(entities, f,ensure_ascii=False, indent=4)  # `indent=4` makes it nicely formatted


        data.append({
            "tokens": tokens,
            "ner_tags": labels
        })

    from collections import Counter
    if clean_data:
        data = refresh_and_clean_ner_labels( data = data, id2label= ID2LABEL, threshold= 0.95)
        all_labels = [label for sample in data for label in sample["ner_tags"]]
        print(Counter(all_labels))



    # Split train/val
    trains, validations = train_test_split(data, test_size=0.1, random_state=42)
    trains, tests = train_test_split(trains, test_size=0.1, random_state=42)
    
    os.makedirs("./data", exist_ok=True)
    with open("./data/all_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"saved all data  ./data/all_data.json ")


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
    n_samples = 10
    save_reports = False
    clean_data = False
    if len(sys.argv) > 1:
        n_samples = int(sys.argv[1])
    if len(sys.argv) > 2:
        save_reports = sys.argv[2].lower() == 'true'
    if len(sys.argv) > 3:
        clean_data = sys.argv[3].lower() == 'true'
    print(f"Starting generation of {n_samples} data!\n Saving reports is {save_reports}!\n Cleaning data option {clean_data}!")
    generate_dataset(n_samples=n_samples, save_reports=save_reports, clean_data= clean_data)

