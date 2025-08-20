import random
import json
import re
from utils import *
from sklearn.model_selection import train_test_split
from config import LABEL2ID, ID2LABEL, ENTITY_LIST


entity_values = {
    "ADDRESS": hospital_addresses,
    "ALLERGY": allergies,
    "BIRTHDATE": generate_dates(start_year=1900,end_year=2024),
    "DATE": generate_dates(),
    "DOCUMENT_TYPE": document_types,
    "DEPARTMENT": departments,
    "DEVICE": devices,
    "DIAGNOSIS": list(diagnosis_icd10_map.values()),
    "DOCTOR": doctors,
    "FAMILY_STATUS": family_status,
    "FAMILYMEMBER": family_members,
    "FAMHIST": family_histories,
    "FINDING": findings,
    "FOLLOWUP_REASON": followup_reasons,
    "FOLLOWUP_REQ": ["CT-Thorax", "Blutbild", "EKG"],
    "GENDER": ["männlich", "weiblich", "divers"],
    "GEWICHT": generate_random_weights(),
    "GROESSE": generate_random_heights(),
    "ICD10_CODE": list(diagnosis_icd10_map.keys()),
    "ICD10_DESC": list(diagnosis_icd10_map.values()),
    "IMMUNIZATION": immunizations,
    "IMPRESSION": impressions,
    "LAB_RESULT": lab_results,
    "LIFESTYLE": lifestyles,
    "MEDICATION": medications,
    "OCCUPATION": occupations,
    "ORG": hospital_names,
    "PERSON": names,
    "PHONE": hospital_phones,
    "PID": generate_patint_ids(),
    "PREV_DIAGNOSIS": prev_diagnoses,
    "PROCEDURE": procedures,
    "RISKFACTOR": risk_factors,
    "SYMPTOM": symptoms,
    "TREATMENT":treatments,
    "VITALSIGNS": vitalsigns
}

arztbrief_template = (
    "{DOCUMENT_TYPE} vom {DATE}:\n"
    "Patient: {PERSON} ({GENDER}), geboren am {BIRTHDATE}, PID: {PID}.\n"
    "Adresse: {ADDRESS}, Telefon: {PHONE}, Familienstand: {FAMILY_STATUS}.\n"
    "Beruf: {OCCUPATION}, begleitet von: {FAMILYMEMBER}.\n"
    "Vorstellung wegen: {SYMPTOM}.\n"
    "Diagnose: {DIAGNOSIS} (ICD-10: {ICD10_CODE} – {ICD10_DESC}).\n"
    "Vorherige Diagnose: {PREV_DIAGNOSIS}.\n"
    "Familiäre Vorbelastung: {FAMHIST}.\n"
    "Medikation: {MEDICATION}, Behandlung: {TREATMENT}, Prozedur: {PROCEDURE}.\n"
    "Labor: {LAB_RESULT}, Vitalzeichen: {VITALSIGNS}.\n"
    "Empfehlung: {FOLLOWUP_REQ} bei {FOLLOWUP_REASON}.\n"
    "Untersuchung durch {DOCTOR}, Abteilung: {DEPARTMENT}, Klinik: {ORG}.\n"
    "Adresse: {ADDRESS}, Tel: {PHONE}.\n"
    "Impression: {IMPRESSION}."
)
befundbericht_template = (
    "{DOCUMENT_TYPE} erstellt am {DATE} durch {DOCTOR} in der Abteilung {DEPARTMENT} des {ORG}.\n"
    "Patient: {PERSON}, {GENDER}, geb. {BIRTHDATE}, PID: {PID}.\n"
    "Untersuchung mittels {DEVICE} aufgrund von {SYMPTOM}.\n"
    "Befunde: {FINDING}, Diagnose: {DIAGNOSIS}.\n"
    "ICD-10-Code: {ICD10_CODE} – {ICD10_DESC}.\n"
    "Laborwerte: {LAB_RESULT}, Vitalzeichen: {VITALSIGNS}.\n"
    "Empfehlung: {TREATMENT}. Impression: {IMPRESSION}.\n"
    "Kontakt: {PHONE}, Adresse: {ADDRESS}."
)

operationsbericht_template = (
    "{DOCUMENT_TYPE}\n"
    "Datum der Operation: {DATE}, durchgeführt von {DOCTOR} im {ORG}, Abteilung: {DEPARTMENT}.\n"
    "Patient: {PERSON}, Geschlecht: {GENDER}, Geburtsdatum: {BIRTHDATE}, PID: {PID}.\n"
    "Indikation: {DIAGNOSIS} – {SYMPTOM}.\n"
    "Durchgeführte Prozedur: {PROCEDURE} unter Einsatz von {DEVICE}.\n"
    "Anästhesieprotokoll: {VITALSIGNS}.\n"
    "Postoperativer Verlauf: {IMPRESSION}.\n"
    "Empfohlene Medikation: {MEDICATION}, weitere Behandlung: {TREATMENT}.\n"
    "Kontakt für Rückfragen: {DOCTOR}, Tel: {PHONE}."
)

entlassungsbericht_template = (
    "{DOCUMENT_TYPE} – Entlassung am {DATE} aus der Klinik {ORG}, Abteilung: {DEPARTMENT}.\n"
    "Patient: {PERSON} ({GENDER}), geb. {BIRTHDATE}, PID: {PID}.\n"
    "Aufnahmediagnose: {DIAGNOSIS}, Symptome: {SYMPTOM}, Risikofaktoren: {RISKFACTOR}.\n"
    "Behandlung: {TREATMENT}, Medikation: {MEDICATION}, Prozedur: {PROCEDURE}.\n"
    "Befunde: {FINDING}, Labordaten: {LAB_RESULT}.\n"
    "Entlassungsdiagnose: {DIAGNOSIS} ({ICD10_CODE} – {ICD10_DESC}).\n"
    "Empfohlene Nachsorge: {FOLLOWUP_REQ}, Grund: {FOLLOWUP_REASON}.\n"
    "Impression: {IMPRESSION}.\n"
    "Kontaktperson: {DOCTOR}, Tel: {PHONE}."
)
anamnesebogen_template = (
    "{DOCUMENT_TYPE} – Erfasst am {DATE} durch {DOCTOR}.\n"
    "Patient: {PERSON}, Geschlecht: {GENDER}, Geburtsdatum: {BIRTHDATE}, PID: {PID}.\n"
    "Adresse: {ADDRESS}, Telefon: {PHONE}, Familienstand: {FAMILY_STATUS}.\n"
    "Beruf: {OCCUPATION}, Lebensstil: {LIFESTYLE}, Impfstatus: {IMMUNIZATION}.\n"
    "Allergien: {ALLERGY}.\n"
    "Familiäre Erkrankungen: {FAMHIST}.\n"
    "Vorerkrankungen: {PREV_DIAGNOSIS}, Medikamente: {MEDICATION}.\n"
    "Aktuelle Beschwerden: {SYMPTOM}.\n"
    "Körperdaten: Größe {GROESSE}, Gewicht {GEWICHT}."
)
radiologie_template = (
    "{DOCUMENT_TYPE} – Untersuchung vom {DATE} durchgeführt durch {DOCTOR} in der Abteilung {DEPARTMENT}, {ORG}.\n"
    "Patient: {PERSON}, {GENDER}, geb. am {BIRTHDATE}, PID: {PID}.\n"
    "Indikation: {SYMPTOM}, Fragestellung: {FINDING}.\n"
    "Durchgeführte Bildgebung: {PROCEDURE} mit {DEVICE}.\n"
    "Befund: {FINDING}.\n"
    "Impression: {IMPRESSION}.\n"
    "Telefon: {PHONE}, Adresse: {ADDRESS}."
)
laborbericht_template = (
    "{DOCUMENT_TYPE} – erstellt am {DATE}.\n"
    "Patient: {PERSON} ({GENDER}), geboren am {BIRTHDATE}, PID: {PID}.\n"
    "Untersuchende Einrichtung: {ORG}, Abteilung: {DEPARTMENT}.\n"
    "Laborparameter: {LAB_RESULT}.\n"
    "Diagnosehinweis: {DIAGNOSIS} ({ICD10_CODE} – {ICD10_DESC}).\n"
    "Beurteilung: {IMPRESSION}.\n"
    "Kontakt: {DOCTOR}, Tel: {PHONE}."
)
patho_template = (
    "{DOCUMENT_TYPE} – Befunddatum: {DATE}, Pathologieabteilung: {DEPARTMENT}, Klinik: {ORG}.\n"
    "Patient: {PERSON}, {GENDER}, geb. {BIRTHDATE}, PID: {PID}.\n"
    "Material: {PROCEDURE}.\n"
    "Makroskopie: {FINDING}.\n"
    "Mikroskopie: {DIAGNOSIS}, ICD-10: {ICD10_CODE} – {ICD10_DESC}.\n"
    "Zusätzliche Tests: {LAB_RESULT}.\n"
    "Beurteilung: {IMPRESSION}.\n"
    "Arzt: {DOCTOR}, Tel: {PHONE}."
)

ueberweisung_template = (
    "{DOCUMENT_TYPE} – Ausgestellt am {DATE} von {DOCTOR}, {DEPARTMENT}, {ORG}.\n"
    "Patient: {PERSON}, geb. {BIRTHDATE}, PID: {PID}.\n"
    "Zielabteilung: {DEPARTMENT}.\n"
    "Grund der Überweisung: {FOLLOWUP_REASON}.\n"
    "Vorbefunde: {PREV_DIAGNOSIS}, aktuelle Beschwerden: {SYMPTOM}.\n"
    "Aktuelle Medikation: {MEDICATION}.\n"
    "Telefon: {PHONE}, Adresse: {ADDRESS}."
)

einwilligung_template = (
    "{DOCUMENT_TYPE} – Ausgefüllt am {DATE}.\n"
    "Patient: {PERSON} ({GENDER}), geb. am {BIRTHDATE}, PID: {PID}.\n"
    "Für das folgende Verfahren: {PROCEDURE}.\n"
    "Behandelnder Arzt: {DOCTOR}, Abteilung: {DEPARTMENT}, Klinik: {ORG}.\n"
    "Risiken und Alternativen wurden erklärt.\n"
    "Diagnose/Indikation: {DIAGNOSIS}, Symptome: {SYMPTOM}.\n"
    "Patient gibt Einwilligung zur Behandlung mit {TREATMENT}.\n"
    "Telefon: {PHONE}, Adresse: {ADDRESS}."
)

impfpass_template = (
    "{DOCUMENT_TYPE} – Stand: {DATE}.\n"
    "Patient: {PERSON}, geboren am {BIRTHDATE}, Geschlecht: {GENDER}, PID: {PID}.\n"
    "Erfasste Impfungen: {IMMUNIZATION}.\n"
    "Hausarzt: {DOCTOR}, Einrichtung: {ORG}, Abteilung: {DEPARTMENT}.\n"
    "Bemerkung: {IMPRESSION}.\n"
    "Adresse: {ADDRESS}, Telefon: {PHONE}."
)
rezept_template = (
    "{DOCUMENT_TYPE} – Ausgestellt am {DATE} durch {DOCTOR} ({DEPARTMENT}, {ORG}).\n"
    "Patient: {PERSON}, geboren am {BIRTHDATE}, PID: {PID}.\n"
    "Verschriebene Medikation: {MEDICATION}.\n"
    "Diagnosebezug: {DIAGNOSIS} ({ICD10_CODE} – {ICD10_DESC}).\n"
    "Bemerkung: {IMPRESSION}.\n"
    "Telefon: {PHONE}, Adresse: {ADDRESS}."
)

therapieplan_template = (
    "{DOCUMENT_TYPE} – Erstellt am {DATE} durch {DOCTOR} in der Abteilung {DEPARTMENT}, Klinik: {ORG}.\n"
    "Patient: {PERSON}, {GENDER}, geb. {BIRTHDATE}, PID: {PID}.\n"
    "Diagnose: {DIAGNOSIS} ({ICD10_CODE} – {ICD10_DESC}).\n"
    "Ziel der Therapie: {FOLLOWUP_REASON}.\n"
    "Empfohlene Maßnahmen:\n"
    "- Behandlung: {TREATMENT}\n"
    "- Medikation: {MEDICATION}\n"
    "- Nachsorge: {FOLLOWUP_REQ}\n"
    "Impression: {IMPRESSION}.\n"
    "Adresse: {ADDRESS}, Tel: {PHONE}."
)
pflegedoku_template = (
    "{DOCUMENT_TYPE} – Eintrag vom {DATE}.\n"
    "Patient: {PERSON}, geboren am {BIRTHDATE}, Geschlecht: {GENDER}, PID: {PID}.\n"
    "Aktueller Zustand: {FINDING}, Vitalwerte: {VITALSIGNS}.\n"
    "Pflegemaßnahmen: {TREATMENT}, Medikation: {MEDICATION}.\n"
    "Auffälligkeiten: {SYMPTOM}, Allergien: {ALLERGY}.\n"
    "Pflegekraft: {DOCTOR}, Station: {DEPARTMENT}, Klinik: {ORG}.\n"
    "Adresse: {ADDRESS}, Telefon: {PHONE}."
)
opfreigabe_template = (
    "{DOCUMENT_TYPE} – Freigegeben am {DATE} durch {DOCTOR}, Abteilung: {DEPARTMENT}.\n"
    "Patient: {PERSON}, geb. am {BIRTHDATE}, PID: {PID}, {GENDER}.\n"
    "Geplante Prozedur: {PROCEDURE}.\n"
    "Indikation: {DIAGNOSIS}, Symptome: {SYMPTOM}.\n"
    "Vitalzeichen stabil: {VITALSIGNS}.\n"
    "Keine Kontraindikationen festgestellt.\n"
    "Medikation vor OP: {MEDICATION}.\n"
    "Einrichtung: {ORG}, Adresse: {ADDRESS}, Tel: {PHONE}."
)

aufnahmebogen_template = (
    "{DOCUMENT_TYPE} – Aufnahme am {DATE} in {ORG}, Abteilung: {DEPARTMENT}.\n"
    "Patient: {PERSON}, {GENDER}, geboren am {BIRTHDATE}, PID: {PID}.\n"
    "Adresse: {ADDRESS}, Tel: {PHONE}, Familienstand: {FAMILY_STATUS}.\n"
    "Beschwerden: {SYMPTOM}, Vorbefunde: {PREV_DIAGNOSIS}.\n"
    "Aktuelle Medikation: {MEDICATION}, Allergien: {ALLERGY}.\n"
    "Größe: {GROESSE}, Gewicht: {GEWICHT}, Vitalwerte: {VITALSIGNS}.\n"
    "Begleitung durch: {FAMILYMEMBER}.\n"
    "Untersuchender Arzt: {DOCTOR}."
)

hkp_template = (
    "{DOCUMENT_TYPE} – Erstellt am {DATE} durch {DOCTOR}, {ORG}.\n"
    "Patient: {PERSON}, PID: {PID}, geboren am {BIRTHDATE}.\n"
    "Diagnose: {DIAGNOSIS} ({ICD10_CODE} – {ICD10_DESC}).\n"
    "Geplante Behandlung: {TREATMENT}, Prozeduren: {PROCEDURE}.\n"
    "Medikamente: {MEDICATION}.\n"
    "Kostenaufstellung gemäß Krankenkasse.\n"
    "Kontakt: {PHONE}, Adresse: {ADDRESS}."
)

attest_template = (
    "{DOCUMENT_TYPE} – Ausgestellt am {DATE}.\n"
    "Patient: {PERSON}, geb. am {BIRTHDATE}, PID: {PID}, Beruf: {OCCUPATION}.\n"
    "Diagnose: {DIAGNOSIS}, Beschwerden: {SYMPTOM}.\n"
    "Der Patient ist derzeit {FOLLOWUP_REASON}.\n"
    "Dauer der Arbeitsunfähigkeit: {FOLLOWUP_REQ}.\n"
    "Unterschrift: {DOCTOR}, Abteilung: {DEPARTMENT}, {ORG}."
)

notfall_template = (
    "{DOCUMENT_TYPE} – Datum: {DATE}, ausgestellt durch {DOCTOR}, Klinik: {ORG}.\n"
    "Patient: {PERSON}, {GENDER}, geb. am {BIRTHDATE}, PID: {PID}.\n"
    "Begleitet von {FAMILYMEMBER}.\n"
    "Symptome: {SYMPTOM}, Vitalwerte: {VITALSIGNS}, Risikofaktoren: {RISKFACTOR}.\n"
    "Durchgeführte Maßnahmen: {TREATMENT}, verabreichte Medikation: {MEDICATION}.\n"
    "Diagnose: {DIAGNOSIS} ({ICD10_CODE} – {ICD10_DESC}).\n"
    "Telefon: {PHONE}, Adresse: {ADDRESS}."
)

ekg_template = (
    "{DOCUMENT_TYPE} – Befunddatum: {DATE}, erstellt durch {DOCTOR}, Abteilung: {DEPARTMENT}, {ORG}.\n"
    "Patient: {PERSON}, geb. am {BIRTHDATE}, PID: {PID}.\n"
    "Indikation: {SYMPTOM}.\n"
    "Ergebnisse: {FINDING}, Vitalzeichen: {VITALSIGNS}.\n"
    "Diagnose: {DIAGNOSIS}, Beurteilung: {IMPRESSION}.\n"
    "Telefon: {PHONE}, Adresse: {ADDRESS}."
)

roentgen_template = (
    "{DOCUMENT_TYPE} – Untersuchung am {DATE}, Klinik: {ORG}, Abteilung: {DEPARTMENT}.\n"
    "Patient: {PERSON}, PID: {PID}, geboren am {BIRTHDATE}.\n"
    "Bildgebung mittels {DEVICE} bei {SYMPTOM}.\n"
    "Befunde: {FINDING}, Impression: {IMPRESSION}.\n"
    "Diagnose: {DIAGNOSIS}.\n"
    "Untersuchender Arzt: {DOCTOR}, Kontakt: {PHONE}."
)
ct_mrt_template = (
    "{DOCUMENT_TYPE} – {DATE}, erstellt durch {DOCTOR}, {ORG}, Abteilung: {DEPARTMENT}.\n"
    "Patient: {PERSON}, geb. {BIRTHDATE}, PID: {PID}.\n"
    "Verfahren: {PROCEDURE} mit {DEVICE}.\n"
    "Indikation: {SYMPTOM}, Befunde: {FINDING}.\n"
    "Diagnose: {DIAGNOSIS} ({ICD10_CODE} – {ICD10_DESC}), Impression: {IMPRESSION}.\n"
    "Empfohlene Nachsorge: {FOLLOWUP_REQ}, Grund: {FOLLOWUP_REASON}."
)
pflegeueberleitung_template = (
    "{DOCUMENT_TYPE} – Erstellt am {DATE} durch {DOCTOR}, {ORG}, Abteilung: {DEPARTMENT}.\n"
    "Patient: {PERSON}, geboren am {BIRTHDATE}, PID: {PID}.\n"
    "Pflegebedürfnisse: {TREATMENT}, Medikation: {MEDICATION}, Vitalzeichen: {VITALSIGNS}.\n"
    "Diagnose: {DIAGNOSIS}, Vorerkrankungen: {PREV_DIAGNOSIS}.\n"
    "Pflegehinweise: {IMPRESSION}.\n"
    "Telefon: {PHONE}, Adresse: {ADDRESS}."
)
reha_gutachten_template = (
    "{DOCUMENT_TYPE} – Antrag vom {DATE}.\n"
    "Patient: {PERSON}, geb. am {BIRTHDATE}, PID: {PID}, Beruf: {OCCUPATION}.\n"
    "Erkrankung: {DIAGNOSIS} ({ICD10_CODE} – {ICD10_DESC}), Symptome: {SYMPTOM}.\n"
    "Behandlung bisher: {TREATMENT}, Medikamente: {MEDICATION}.\n"
    "Familiäre Vorbelastung: {FAMHIST}.\n"
    "Sozialmedizinische Bewertung: {IMPRESSION}.\n"
    "Empfohlene Maßnahmen: {FOLLOWUP_REQ}, Grund: {FOLLOWUP_REASON}.\n"
    "Kontaktarzt: {DOCTOR}, Klinik: {ORG}, Tel: {PHONE}."
)

# Einfaches Template
complete_template = (

    "{DOCUMENT_TYPE}:\n Am {DATE} stellte sich der Patient {PERSON} ({GENDER}), {GROESSE} per {GEWICHT} geboren am {BIRTHDATE}\n"
    "Familienstand: {FAMILY_STATUS}, Symptome: {SYMPTOM}, Diagnose: {DIAGNOSIS}\n "
    "Beruf: {OCCUPATION}, Medikament: {MEDICATION}, Behandlung: {TREATMENT}, "
    "Durchgeführt von {DOCTOR} in der Abteilung {DEPARTMENT}.\n"
    "Krankenhaus: {ORG}, {ADDRESS}, Tel: {PHONE}.\n"
    "{DOCUMENT_TYPE} vom {DATE}:\n"
    "Patient: {PERSON} ({GENDER}), geboren am {BIRTHDATE}, PID: {PID}.\n"
    "Adresse: {ADDRESS}, Telefon: {PHONE}.\n"
    "Familienstand: {FAMILY_STATUS}, Familienmitglied: {FAMILYMEMBER}, familiäre Vorgeschichte: {FAMHIST}.\n"
    "Abteilung: {DEPARTMENT}, Krankenhaus: {ORG}.\n"
    "Untersuchung durchgeführt von {DOCTOR} mit {DEVICE}.\n"
    "Diagnose: {DIAGNOSIS} (ICD-10: {ICD10_CODE} - {ICD10_DESC}).\n"
    "Vorherige Diagnose: {PREV_DIAGNOSIS}.\n"
    "Symptome: {SYMPTOM}.\n"
    "Befund: {FINDING}.\n"
    "Labordiagnostik: {LAB_RESULT}.\n"
    "Impression: {IMPRESSION}.\n"
    "Medikation: {MEDICATION}, Behandlung: {TREATMENT}.\n"
    "Verfahren/Prozedur: {PROCEDURE}.\n"
    "Risikofaktoren: {RISKFACTOR}.\n"
    "Impfungen: {IMMUNIZATION}.\n"
    "Lebensstil: {LIFESTYLE}.\n"
    "Vitalparameter: {VITALSIGNS}.\n"
    "Folgegrund: {FOLLOWUP_REASON}, Folgeanforderung: {FOLLOWUP_REQ}.\n"
    "Gewicht: {GEWICHT}, Größe: {GROESSE}.\n"
)


templates_list =[complete_template ,reha_gutachten_template,ct_mrt_template,roentgen_template,ekg_template,
                 notfall_template,attest_template,hkp_template,aufnahmebogen_template,opfreigabe_template,pflegedoku_template,
                 therapieplan_template,rezept_template,impfpass_template,einwilligung_template,ueberweisung_template,patho_template,
                 radiologie_template,laborbericht_template,anamnesebogen_template,entlassungsbericht_template, operationsbericht_template,
                 befundbericht_template,arztbrief_template]
def tokenize(text):
    # einfache Tokenisierung nach Leerzeichen und Satzzeichen
    tokens = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)
    return tokens




def create_sample():
    return {ent: random.choice(entity_values[ent]) for ent in ENTITY_LIST if ent in entity_values}

def extract_entities(text, values):
    ents = []
    for label, value in values.items():
        start = text.find(value)
        if start != -1:
            end = start + len(value)
            ents.append((start, end, label))
    return ents






def create_bio_tags(tokens, entities, text):
    """
    entities: dict mit Entity-Name -> Wert
    text: originaler Text mit den ersetzten Werten
    erzeugt BIO-Tags basierend auf den Entity-Werten
    """
    tags = ["O"] * len(tokens)

    # Für jedes Entity Value alle Vorkommen finden und taggen
    for ent_name, ent_val in entities.items():
        if not ent_val:
            continue
        ent_tokens = tokenize(ent_val)
        len_ent = len(ent_tokens)

        # Suche nach Entität im tokenisierten Text
        # Wir tokenisieren originalen Text und vergleichen Token-Abschnitte
        for i in range(len(tokens) - len_ent + 1):
            if tokens[i:i+len_ent] == ent_tokens:
                tags[i] = f"B-{ent_name}"
                for j in range(i+1, i+len_ent):
                    tags[j] = f"I-{ent_name}"

    return tags

def bio_tags_to_ids(tags, label2id):
    return [label2id.get(tag, 0) for tag in tags]


def generate_paraphrase_text(values):
    phrases = []
        # Beispiel: zuerst Hospital Stay zusammenfassen
    hospital_phrase = paraphrase_hospital_stay(values)
    if hospital_phrase:
        phrases.append(hospital_phrase)
        # Optional: entferne die einzelnen Keys, wenn du sie nicht nochmal extra willst
        for key in ["ADMISSION_DATE", "DISCHARGE_DATE", "HOSPITAL_STAY"]:
            values.pop(key, None)
      # Medication speziell
    medication_phrase = paraphrase_medication_combination(values)
    if medication_phrase:
        phrases.append(medication_phrase)
        for key in ["MEDICATION", "DOSAGE", "FREQUENCY", "DURATION"]:
            values.pop(key, None)

    for ent_type in ENTITY_LIST:
        if ent_type in values:
            phrase = paraphrase_entity(ent_type, values[ent_type])
            phrases.append(phrase)

# Shuffle the phrases and join
    random.shuffle(phrases)
    return " ".join(phrases)


def generate_dataset(n_samples,save_reports):
    from string import Template
    import os
    dataset = []

    count_template = 0
    count_paraphrase = 0
    for i in range(n_samples):
        try:

            template = random.choice(templates_list)
            values = create_sample()


            if random.random() < 0.5:    
         
                text = template.format(**values)
                # text = Template(template).safe_substitute(values) just with preformatted string f" vvava {value}"
                count_template +=1
            else:
                text = generate_paraphrase_text(values)
                count_paraphrase += 1
            # text = template.format(**values)
            tokens = tokenize(text)
            tags = create_bio_tags(tokens, values, text)
            tag_ids = bio_tags_to_ids(tags, LABEL2ID)

            if save_reports:
                filename = f"./txt_reports/report_{i+1}.txt"
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(text)

            dataset.append( {
                "tokens": tokens,
                "ner_tags": tag_ids
            })
        except Exception as e:
            print(f"{e}" , {i})

    trains, validations = train_test_split(dataset, test_size=0.1, random_state=42)
    trains, tests = train_test_split(trains, test_size=0.1, random_state=42)

    os.makedirs("./data", exist_ok=True)
    with open("./data/all_data.json", "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
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


    print(f"From template {count_template}, from paraphrase {count_paraphrase}")

# Run as script
if __name__ == "__main__":
    import sys
    n_samples = 100
    save_reports = False
    clean_data = False
    if len(sys.argv) > 1:
        n_samples = int(sys.argv[1])
    if len(sys.argv) > 2:
        save_reports = sys.argv[2].lower() == 'true'
    if len(sys.argv) > 3:
        clean_data = sys.argv[3].lower() == 'true'
    print(f"Starting generation of {n_samples} data!\n Saving reports is {save_reports}!\n Cleaning data option {clean_data}!")
    generate_dataset(n_samples=n_samples, save_reports=save_reports,)


