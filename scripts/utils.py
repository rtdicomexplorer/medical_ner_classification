import unicodedata
import re
import json
import datetime
import random
from scripts.config import LABEL2ID, ID2LABEL
import uuid
from typing import List, Tuple, Dict
import pytesseract
import platform
from pathlib import Path
import numpy as np
import os

def np_encoder(obj):
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def remove_folder(folder_path):
    import shutil
    try:
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
    except Exception as e:
        print(f"Error by deleting {folder_path}: {e}")

def init_tesseract():
    system = platform.system()

    if system == "Windows":
        # Standardpfad unter Windows
        tesseract_path = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
        if tesseract_path.exists():
            pytesseract.pytesseract.tesseract_cmd = str(tesseract_path)
            print("✅ Tesseract unter Windows initialisiert.")
        else:
            raise FileNotFoundError(f"❌ Tesseract was not found: {tesseract_path}")
    
    elif system == "Linux":
        # Optional: prüfen, ob Tesseract installiert ist
        from shutil import which
        if which("tesseract") is None:
            raise EnvironmentError("❌ Tesseract is not installed. Please do that: sudo apt install tesseract-ocr")

    elif system == "Darwin":  # macOS
        from shutil import which
        if which("tesseract") is None:
            raise EnvironmentError("❌ Tesseract is not installed. Please do that: brew install tesseract")
    
    else:
        raise EnvironmentError(f"❌ OS unjknown: {system}")


def format_diagnoses(diagnosis_icd10_map):
    entries=[]
    for diagnosis, code in diagnosis_icd10_map.items():
        entry = f"{diagnosis} ({code})" if code else f"{diagnosis}"         
        entries.append(entry)
    return entries


def format_prev_diagnoses(diagnosis_icd10_map):
    entries=[]
    for diagnosis, code in diagnosis_icd10_map.items():
        prev_entries =  [
            f"frühere {diagnosis}",
            f"Zustand nach  {diagnosis}",
            f"{diagnosis} in der Vorgeschichte",
            f"vor {random.randint(1,30)} {random.choice(['Monate', 'Jahre'])} diagnostiziert: {diagnosis}"]
        prev_diagnosis = random.choice(prev_entries) 
        entry = f"{prev_diagnosis} ({code})" if code else f"{prev_diagnosis}"         
        entries.append(entry)
    return entries





def replace_entities_with_labels(text, entities):
    """
    Replaces detected entity spans in the text with their label name, e.g., {PATIENT}.
    The replacement is done in reverse order of entity start index to avoid index shifting.
    """
    # Sort entities in reverse by start index to avoid messing up indices when replacing
    entities_sorted = sorted(entities, key=lambda x: x['start'], reverse=True)
    
    for ent in entities_sorted:
        label = ent['entity_group'].upper()
        start = ent['start']
        end = ent['end']
        text = text[:start] + f"{{{label}}}" + text[end:]

    return text

def generate_ner_data(text,entities):
    tokens, offsets = smart_tokenize_with_offsets(text)          
    tags =  create_bio_tags_from_offsets(tokens=tokens,offsets=offsets,entities= entities)
    tag_ids = bio_tags_to_ids(tags, LABEL2ID)
    dataset = {
        "tokens": tokens,
        "ner_tags": tag_ids
    }
    return dataset


def bio_tags_to_ids(tags, label2id):
    return [label2id.get(tag, 0) for tag in tags]

def smart_tokenize_with_offsets(text: str) -> Tuple[List[str], List[Tuple[int, int]]]:
    pattern = r"""
        \b\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4}\b      # Dates
        |\b\d+\.\d+\b                            # Decimal numbers
        |\b\w+\b                                 # Words
        |[^\w\s]                                 # Punctuation
    """
    tokens = []
    offsets = []
    for match in re.finditer(pattern, text, re.UNICODE | re.VERBOSE):
        tokens.append(match.group())
        offsets.append((match.start(), match.end()))
    return tokens, offsets

def create_bio_tags_from_offsets(tokens: List[str], offsets: List[Tuple[int, int]], entities: List[Dict]) -> List[str]:
    tags = ["O"] * len(tokens)

    # Entities nach Länge sortieren (längste zuerst)
    entities = sorted(entities, key=lambda x: -(x["end"] - x["start"]))

    for ent in entities:
        ent_start = ent["start"]
        ent_end = ent["end"]
        ent_label = ent["entity_group"]

        matched_indices = []

        for i, (tok_start, tok_end) in enumerate(offsets):
            if tok_start >= ent_end:
                break
            if tok_end <= ent_start:
                continue
            if tok_start < ent_end and tok_end > ent_start:
                # Nur markieren, wenn noch nicht markiert
                if tags[i] == "O":
                    matched_indices.append(i)

        if not matched_indices:
            continue

        tags[matched_indices[0]] = f"B-{ent_label}"
        for i in matched_indices[1:]:
            tags[i] = f"I-{ent_label}"

    return tags

def smart_tokenize(text):
    # Regex to match:
    # - Full dates like 10.08.2024, 10/08/2024, 2024-08-10
    # - Decimal numbers
    # - Words
    # - Individual punctuation
    pattern = r"""
        \b\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4}\b      # Dates like 10.08.2024 or 2024-08-10
        |\b\d+\.\d+\b                            # Decimal numbers
        |\b\w+\b                                 # Words
        |[^\w\s]                                 # Punctuation
    """
    return re.findall(pattern, text, re.UNICODE | re.VERBOSE)

def validate_ner_sample_smart(tokens, ner_tags):
    issues = []

    if len(tokens) != len(ner_tags):
        issues.append(f"Length mismatch: {len(tokens)} tokens vs {len(ner_tags)} tags")
        return issues  

    prev_tag = "O"

    for i, tag_id in enumerate(ner_tags):
        tag = ID2LABEL.get(tag_id, "O")

        if tag.startswith("I-"):
            label = tag[2:]

            if not prev_tag.endswith(label) or prev_tag.startswith("O"):
                issues.append(f"Inconsistent I- tag at position {i}: {tag} without preceding B- or I- of same entity")

        elif tag.startswith("B-") or tag == "O":
            pass  # allowed

        else:
            issues.append(f"Invalid tag at position {i}: {tag}")

        prev_tag = tag

    return issues



def generate_patint_id():
    import string
    return  f"{random.choice(string.ascii_uppercase)}{str(uuid.uuid4())[:8]}"

def generate_patint_ids(count=10):
    result = []
    for _ in range(count):
        result.append(generate_patint_id())
    return result

def random_date(start_year=2015, end_year=2024):
    start = datetime.date(start_year, 1, 1)
    end = datetime.date(end_year, 12, 31)
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + datetime.timedelta(days=random_days)


def generate_dates(count=10,start_year=2015, end_year=2024):
    result = []
    for _ in range(count):
        date  = random_date(start_year, end_year)       
        result.append(date.strftime('%Y%m%d'))#"YYYYMMDD"
        date  = random_date(start_year-1, end_year)    
        result.append(date.strftime('%d-%m-%Y'))#"DD-MM-YYYY:"
        date  = random_date(start_year-2, end_year)    
        result.append(date.strftime('%d-%B-%Y'))#"DD-Month-YYYY:"
        date  = random_date(start_year-3, end_year)    
        result.append(date.strftime("%d.%m.%Y"))#"dd.mm.yyyy"
        result.append(date.strftime("%d. %B %Y")) 
    return result


def generate_random_hospital_stay(count = 20):
    result = []
    for _ in range(count):
        num = random.randint(2,30)
        typ = random.choice([ f"für {num} Tage", f" bis {num} Woche", f"max {num} Monate", f"{num} Tage", f" {num} Woche", f"{num} Monate"])    
        result.append(f"{typ}")
    return result

def generate_random_weight():
    weight = round(random.uniform(19, 150), 1)
    return f"{weight} kg"

def generate_random_height():
    height_cm = random.randint(120, 210)   
    # Randomly choose format: cm or m
    if random.choice([True, False]):
        return f"{height_cm} cm"
    else:
        height_m = height_cm / 100
        # Format with comma as decimal separator
        return f"{height_m:.2f}".replace('.', ',') + " m"

def generate_random_weights(count = 10):
    result = []
    for _ in range(count):
        result.append(generate_random_weight())
    return result

def generate_random_heights(count = 10):
    result = []
    for _ in range(count):
        result.append(generate_random_height())
    return result


def paraphrase_hospital_stay(entities):
    admission = entities.get("ADMISSION_DATE")
    discharge = entities.get("DISCHARGE_DATE")
    stay_reason = entities.get("STAY_REASON")
    if not (admission or discharge or stay_reason):
        return ""
    
    templates = [
        "Aufenthalt im Krankenhaus vom {admission} bis {discharge}.",
        "Der Krankenhausaufenthalt dauerte vom {admission} bis {discharge}.",
        "Patient wurde am {admission} aufgenommen und am {discharge} entlassen.",
        "Grund des Krankenhausaufenthalts: {stay_reason}.",
        "Er/Sie wird staionär wegen {stay_reason} bis {discharge}",
        "Krankenhausaufenthalt wegen {stay_reason} vom {admission} bis {discharge}.",
        "Aufgenommen am {admission}, entlassen am {discharge} aufgrund von {stay_reason}.",
    ]

    possible_templates = []

    if admission and discharge and stay_reason:
        possible_templates = [
            "Krankenhausaufenthalt wegen {stay_reason} vom {admission} bis {discharge}.",
            "Aufgenommen am {admission}, entlassen am {discharge} aufgrund von {stay_reason}.",
        ]
    elif admission and discharge:
        possible_templates = [
            "Aufenthalt im Krankenhaus vom {admission} bis {discharge}.",
            "Der Krankenhausaufenthalt dauerte vom {admission} bis {discharge}.",
            "Patient wurde am {admission} aufgenommen und am {discharge} entlassen.",
        ]
    elif stay_reason:
        possible_templates = [
            "Grund des Krankenhausaufenthalts: {stay_reason}.",
        ]
    else:
        possible_templates = templates

    template = random.choice(possible_templates)

    return template.format(
        admission=admission or "",
        discharge=discharge or "",
        stay_reason=stay_reason or "",
    ).strip()


def paraphrase_medication_combination(entities):
    """
    Combine MEDICATION + DOSAGE + ROUTE + FREQUENCY + DURATION 
    
    """
    medication = entities.get("MEDICATION")
    dosage = entities.get("DOSAGE")
    route = entities.get("ROUTE")
    frequency = entities.get("FREQUENCY")
    duration = entities.get("DURATION")

    if not medication:
        return None

    # Simplke sentence if only medication is present
    if not any([dosage, route, frequency, duration]):
        return f"Behandlung mit {medication}"

    templates = [
        "Therapie mit {medication}, {dosage}, {route}, {frequency} für {duration}.",
        "{medication} wurde {route} in einer Dosis von {dosage} verabreicht – {frequency} über {duration}.",
        "Verordnung: {medication} {dosage}, {frequency}, Applikation: {route}, Dauer: {duration}.",
        "Behandlung mit {medication} ({dosage}), {route}, {frequency}, geplant für {duration}.",
    ]

    
    template = random.choice(templates)
    phrase = template.format(
        medication=medication or "",
        dosage=dosage or "",
        route=route or "",
        frequency=frequency or "",
        duration=duration or "",
    )

    # remove commas if not necessary (z.B. ", ,", ", .", "  ")
    phrase = re.sub(r'\s+,', ',', phrase)  # Leerzeichen vor Komma entfernen
    phrase = re.sub(r',\s*,', ',', phrase) # Mehrfache Komma reduzieren
    phrase = re.sub(r',\s*\.', '.', phrase) # Komma vor Punkt entfernen
    phrase = re.sub(r'\s{2,}', ' ', phrase) # Mehrfache Leerzeichen auf eins reduzieren
    phrase = phrase.strip()

    if phrase.endswith(','):
        phrase = phrase[:-1] + '.'
    return phrase

def paraphrase_entity(entity_type, value):
    """
    Create a paraphrase by given entity, with given value
    Neetds to be checked... 
    """
    variations = {      
        "ADDRESS": [
            f"Standort: {value}",
            f"Adresse: {value}",
            ],

       "ADDRESS_PATIENT": [
            f"wohnhaft in {value}",
            f"Adresse: {value}",
            f"anschriftlich erreichbar unter {value}",
            f"Wohnadresse: {value}",
            f"zu finden in {value}",
            f"gemeldet unter {value}"
            ],


        "ADMISSION_DATE": [
            f"Aufnahme am {value}",
            f"Patient wurde aufgenommen am {value}",
            f"Datum der Einweisung: {value}"
            ],

        "ALCOHOL_CONSUMPTION": [
            f"Alkoholkonsum: {value}",
            f"er/sie konsumiert {value}",
            f"Trinkverhalten: {value}"
            ],

        "ALLERGY":[
            f"allergisch auf: {value}",
            f"bekannte Allergien: {value}",
            f"Allergien: {value}",
            f"verträgt {value} nicht",
            f"zeigt Allergien gegen {value}",
            f"Allergische Reaktion auf {value} dokumentiert"
            ],

        "ANAMNESE": [
            f"Anamnese: {value}",
            f"Vegetative Anamnese zeigt: {value}",
            f"Aus der Anamnese geht hervor: {value}",
            f"Der Patient berichtet über {value}",
            f"Vorgeschichte des Patienten: {value}",
            f"Anamnestisch auffällig: {value}",
            f"In der medizinischen Anamnese: {value}",
            f"{value} wurde anamnestisch erhoben",
            f"Anamnestisch wurden {value} beschrieben",
            f"Anamnestisch relevante Angabe: {value}",
            f"Medikamente Anamnese : {value}",
            f"Soziale Anamnese: {value}",
            f"Familiäre Anamnese: {value}"
            ],


        "BIRTHDATE":[
            f"geboren am: {value}",
            f"Geburtsdatum: {value}",
            f"Der Geburtstag ist der {value}",
            f"Geboren wurde am {value}"
            ],

        "BLOOD_TYPE": [
            f"Blutgruppe: {value}",
            f"hat Blutgruppe {value}",
            f"Bluttyp: {value}"
            ],

        "BODY_PART": [
            f"betroffene Region: {value}",
            f"lokalisiert an: {value}",
            f"Körperteil: {value}"
            ],

        "COURSE": [
            f"Verlauf: {value}",
            f"klinischer Verlauf war {value}",
            f"der Krankheitsverlauf zeigt {value}"
            ],

        "DATE": [
            f"am {value}",
            f"Datum: {value}",
            f"am Untersuchungsdatum {value}",
            f"Datum des Berichts: {value}"
            ],

        "DEVICE":[
            f"es wird empfohlen {value} zu verwenden",
            f"{value} wird verwendet",
            f"eingesetzt wird {value}",
            f"als Gerät kommt {value} zum Einsatz",
            f"verwendetes Gerät: {value}",
            f"zur Anwendung gelangt {value}",
            f"{value} kam zum Einsatz",
            f"benutzt wurde {value}",
            f"eingesetztes Gerät: {value}",
            f"verwendetes medizinisches Gerät: {value}",
            f"technisch unterstützt durch {value}",
            f"{value} wurde zur Untersuchung verwendet"
            ],

        "DEPARTMENT": [
            f"Abteilung: {value}",
            f"Fachbereich: {value}",
            f"medizinische Einheit: {value}",
            f"zugewiesen an die Abteilung {value}",
            f"{value}-Abteilung"
            ],

        "DIAGNOSIS": [
            f"es wurde {value} diagnostiziert",
            f"Diagnose: {value}",
            f"leidet an {value}",
            f"{value} wurde festgestellt",
            f"klinischer Befund: {value}",
            f"es besteht der Verdacht auf {value}",
            f"diagnostischer Hinweis: {value}",
            f"festgestellt wurde {value}",
            f"es handelt sich um {value}",
            f"medizinische Diagnose: {value}"
            ],
       
        "DISCHARGE_DATE": [
            f"Entlassen am {value}",
            f"Entlassdatum: {value}",
            f"Datum der Entlassung: {value}"
            ],

        "DOCTOR": [
            f"behandelt durch {value}",
            f"untersucht von {value}",
            f"{value} führte die Untersuchung durch",
            f"Arzt: {value}",
            f"medizinisch betreut von {value}",
            f"{value} als behandelnder Arzt",
            f"unter der Aufsicht von {value} ",
            f"{value} hat die Behandlung übernommen"
            ],

        "DOCUMENT_TYPE": [
            f"Berichtstyp: {value}",
            f"Dokument: {value}",
            f"Art des Dokuments: {value}",
            f"{value} liegt vor",
            f"Typ: {value}",
            f"es handelt sich um einen {value}"
            ],

        "DOSAGE": [
            f"Dosierung: {value}",
            f"verabreichte Menge: {value}",
            f"{value} wurde gegeben"
            ],

        "DURATION": [
            f"über einen Zeitraum von {value}",
            f"Dauer: {value}",
            f"Behandlungsdauer betrug {value}"
            ],

        "FAMILY_STATUS":[
                f"Familienstand: {value}",
                f"Er ist {value}",
                f"Der Familienstatus lautet {value}",
                f"Status in der Familie: {value}",
                f"Familienverhältnis: {value}"
                ],

        "FAMILYMEMBER":[
                f"begleitet von {value}",
                f"bei sich hat {value}",
                f"{value} ist als Begleitung dabei",
                f"Anwesend ist {value}",
                f"Mit dabei: {value}"
                ],

        "FAMHIST":[
                f"in der Familie gab es schon Fälle mit {value}",
                f"Familienanamnese: {value}",
                f"familiäre Häufung von {value} bekannt",
                f"familiäre Vorbelastung mit {value}",
                f"es liegen familiäre Fälle von {value} vor",
                f"familiäre Erkrankung: {value}",
                f"in der Verwandtschaft tritt {value} auf"
                ],

        "FINDING": [
                f"Befund: {value}",
                f"es zeigte sich {value}",
                f"untersucht wurde: {value}",
                f"beobachtet wurde {value}",
                f"{value} trat auf",
                f"nachgewiesen: {value}",
                f"diagnostischer Befund: {value}"
                ],

        "FOLLOWUP_REASON": [
                f"Grund für die Nachsorge: {value}",
                f"Folgegrund: {value}",
                f"Nachsorge erforderlich wegen {value}",
                f"{value} als Anlass für Nachkontrolle",
                f"{value} wurde als Folgegrund angegeben"
                ],

        "FOLLOWUP_REQ": [
                f"Folgeanforderung: {value}",
                f"weiteres Vorgehen: {value}",
                f"empfohlene Maßnahme: {value}",
                f"{value} soll durchgeführt werden",
                f"{value} wurde als nächste Maßnahme geplant"
                ],

        "FREQUENCY": [
                f"Häufigkeit: {value}",
                f"{value} verabreicht",
                f"Verabreichung {value}"
                ],

        "GEWICHT":[
                f"wiegt: {value}",
                f"er/sie wiegt {value}",
                f"das Gewicht beträgt {value}",
                f"das Körpergewicht liegt bei {value}",
                f"Gewicht: {value}",
                f"Gewicht : {value}"
                ],

        "GROESSE":[
                f"Größe: {value}",
                f"Größe : {value}",
                f"er/sie ist {value} groß",
                f"die Körpergröße beträgt {value}",
                f"die Größe ist {value}",
                f"die Körpergröße liegt bei {value}"
                ],

        "HOSPITAL_STAY": [
                f"Aufenthaltsdauer: {value}",
                f"stationär für {value}",
                f"Krankenhausaufenthalt von {value}"
                ],        
        "IMMUNIZATION":[
                f"Impfungen: {value}",
                f"geimpft gegen {value}",
                f"Impfstatus: {value}",
                f"Der Patient wurde immunisiert gegen {value}",
                f"Impfungen liegen vor für {value}"
                ],

        "IMPRESSION": [
                f"Einschätzung: {value}",
                f"Beurteilung: {value}",
                f"Zusammenfassend ergibt sich: {value}",
                f"klinische Impression: {value}",
                f"Schlussfolgerung: {value}",
                f"abschließende Einschätzung: {value}",
                f"Interpretation: {value}",
                f"{value} als zusammenfassender Befund"
                ],

        "INSURANCE_ID": [
                f"Versicherungsnummer: {value}",
                f"Vers.-ID: {value}",
                f"Versicherten-ID: {value}"
                ],
    
        "LAB_RESULT": [
                f"Laborergebnisse: {value}",
                f"Im Labor zeigte sich: {value}",
                f"Blutwerte: {value}",
                f"Laborbefund: {value}",
                f"Ergebnisse der Laboruntersuchung: {value}",
                f"diagnostisch relevante Werte: {value}",
                f"Laborparameter: {value}",
                f"{value} wurden im Labor festgestellt"
                ],

        "LIFESTYLE": [
                f"Lebensstil: {value}",
                f"führt einen {value} Lebensstil",
                f"Verhaltensmuster: {value}",
                f"Lebensgewohnheiten: {value}",
                f"Lebensweise: {value}"
                ],

        "MEDICATION": [
                f"bekommt {value}",
                f"Therapie mit {value}",
                f"{value} wurde verabreicht",
                f"Medikation: {value}",
                f"wird behandelt mit {value}",
                f"Medikamentöse Behandlung mit {value}",
                f"erhält {value} als Medikament"
                ],

        "OCCUPATION":[
                f"aktueller Beruf: {value}",
                f"is {value} von Beruf",
                f"er ist {value}",
                f"arbeitet als {value}",
                f"keine Beschäftigung",
                f"arbeitet als {value}",
                f"{value} ist sein/ihr Beruf",
                f"Beruflich tätig als {value}",
                f"Zurzeit ohne Beschäftigung" if random.random() < 0.2 else f"Er/Sie ist {value}",
                ],

        "ORG": [
                f"im Krankenhaus {value}",
                f"Einrichtung: {value}",
                f"im {value}",
                f"Klinik: {value}",
                f"stationiert in {value}",
                f"zugehörig zu {value}",
                f"behandelt im {value}",
                f"Arbeitsort: {value}"
            ],

        "PATIENT": [
                f"Patient: {value}",
                f"Name: {value}",
                f"{value} stellte sich vor",
                f"Betroffene Person: {value}",
                f"{value} wurde aufgenommen",
                f"Es handelt sich um {value}",
                f"Die Person namens {value}",
                f"{value} wurde eingewiesen"
            ],
            
        "PHONE": [
                f"Telefonnummer: {value}",
                f"Kontakt: {value}",
                f"Telefon: {value}",
                f"erreichbar unter: {value}",
                f"Rufnummer: {value}"
                ],

        "PHONE_PATIENT": [
                f"Telefonnummer: {value}",
                f"Kontakt: {value}",
                f"Telefon: {value}",
                f"erreichbar unter: {value}",
                f"Rufnummer: {value}"
                ],

        "PID":[
                f"patient-id {value}",
                f"ID: {value}",
                f"PID: {value}",
                f"PIZ: {value}",
                f"Patientenkennzeichen: {value}",
                f"Identifikationsnummer: {value}"
                ],

        "PREV_DIAGNOSIS": [
                f"frühere Diagnose: {value}",
                f"Vordiagnose: {value}",
                f"zuvor diagnostiziert mit {value}",
                f"es lag bereits {value} vor",
                f"bekannte Vorerkrankung: {value}",
                f"bisherige Diagnose: {value}",
                f"medizinische Vorgeschichte zeigt {value}",
                f"diagnostiziert in der Vergangenheit: {value}",
                f"Vorerkrankungen: {value}"
                ],

        "PROCEDURE": [
                f"durchgeführte Prozedur: {value}",
                f"eingesetztes Verfahren: {value}",
                f"Untersuchung mittels {value}",
                f"{value} wurde angewendet",
                f"{value} wurde durchgeführt",
                f"diagnostisches Verfahren: {value}"
                ],

        "RISKFACTOR": [
                f"mögliche Risikofaktoren: {value}",
                f"es bestehen folgende Risiken: {value}",
                f"Risikoaspekte: {value}",
                f"bekannte Risikofaktoren: {value}",
                f"{value} gelten als Risikofaktoren",
                f"erhöhtes Risiko durch: {value}",
                f"relevante Risiken: {value}"
                ],

        "ROOM_NUMBER": [
                f"Zimmernummer: {value}",
                f"untergebracht ins Zimmer {value}",
                f"Raum: {value}"
                ],

        "ROUTE": [
                f"Applikationsweg: {value}",
                f"wurde {value} verabreicht",
                f"Verabreichungsform: {value}"
                ]   ,
        
        "SMOKING_STATUS": [
                f"Raucherstatus: {value}",
                f"er/sie ist {value}",
                f"Tabakkonsum: {value}"
                ],
    
        "STAY_REASON":[
                f"Grund des Krankenhausaufenthalts: {value}",
                f"Aufgrund von {value}",
                f"muss noch stationär wegen {value}",
                f"wegen {value} muss stationäre"
                ],

        "SYMPTOM": [
                f"klagt über {value}",
                f"zeigt Symptome wie {value}",
                f"Symptomatik: {value}",
                f"hat {value}",
                f"es wurden {value} beobachtet",
                f"{value} wurde berichtet",
                f"leidet unter {value}",
                f"stark anhaltend dumpfen {value}",
                f"fühlt sich {value}",
                ],

        "TREATMENT": [
                f"erhält Behandlung mit {value}",
                f"Therapieansatz: {value}",
                f"{value} wurde eingeleitet",
                f"Behandlungsform: {value}",
                f"es erfolgte eine Behandlung mittels {value}",
                f"Therapie: {value}",
                f"therapeutische Maßnahme: {value}"
                ],

        "VITALSIGNS":[
                f"{value}",
                f"Vitalparameter: {value}",
                f"Die Vitalzeichen zeigen: {value}",
                f"Gemessene Werte: {value}"
                ],
        # add more as needed
    }

    end_char = random.choice(['. ',', ','; ','! '])
    phrase = f"{entity_type}: {value}{end_char}"# default value
    if entity_type in variations:
        phrase =f" {random.choice(variations[entity_type])}{end_char}"
        
    return phrase


anamneses = [
    "nächtliche Schweißausbrüche",
    "Schlafstörungen",
    "verminderter Appetit",
    "gesteigerter Appetit",
    "vermehrter Durst",
    "unfreiwilliger Gewichtsverlust",
    "regelmäßige Übelkeit am Morgen",
    "Erbrechen nach Mahlzeiten",
    "Fieber seit drei Tagen",
    "Schüttelfrost in der Nacht",
    "häufiger Harndrang",
    "Schmerzen beim Wasserlassen",
    "Verstopfung",
    "Durchfall",
    "Kurzatmigkeit beim Treppensteigen",
    "anhaltender Husten",
    "nächtliche Atemnot",
    "unerklärliche Hitzegefühle",
    "regelmäßiger Schwindel",
    "Kältegefühl in den Extremitäten",
    "Blähungen und Völlegefühl",
    "nächtliches Wasserlassen",
    "Unruhe während der Nacht",
    "plötzlicher Appetitverlust",
    "kein Durstgefühl",
    "unregelmäßiger Stuhlgang",
    "nächtlicher Harndrang",
    "unruhiger Schlaf mit häufigem Erwachen"
]


courses = [
    "Der Verlauf ist stabil.",
    "Der Krankheitsverlauf ist progressiv.",
    "Die Symptome besserten sich im Verlauf.",
    "Klinische Besserung im Verlauf beobachtet."
]

smoking_status = [
    "Nichtraucher",
    "Raucht gelegentlich",
    "Aktiver Raucher",
    "Ex-Raucher seit 5 Jahren",
    "täglich für 10 Jahren zehn Zigaretten geraucht"
]

alcohol_consumptions = [
    "kein Alkoholkonsum",
    "gelegentlicher Alkoholkonsum",
    "regelmäßiger Alkoholkonsum",
    "starker Alkoholkonsum"
]

blood_types = [
    "A+",
    "A-",
    "B+",
    "B-",
    "AB+",
    "AB-",
    "0+",
    "0-"
]

admission_dates = [
    "2023-04-01",
    "2023-06-15",
    "2024-01-20"
]

discharge_dates = [
    "2023-04-10",
    "2023-06-25",
    "2024-01-30"
]

dosages = [
    "5 mg täglich",
    "10 mg zweimal täglich",
    "20 mg einmal wöchentlich"
]

durations = [
    "2 Wochen",
    "1 Monat",
    "3 Monate"
]

frequencies = [
    "einmal täglich",
    "zweimal täglich",
    "alle 8 Stunden"
]

routes = [
    "oral",
    "intravenös",
    "subkutan"
]

body_parts = [
    "rechter Arm",
    "linkes Bein",
    "linker Arm",
    "rechtes Bein",
    "linke Lunge",
    "rechter Oberschenkel",
    "Kopf",
    "Hals",
    "Gesicht",
    "rechte Hand",
    "linke Hand",
    "Hufte"
]

insurance_ids = [
    "1234567890",
    "9876543210",
    "A1234567B"
]

hospital_stays = [
    "aufgenommen am 01.04.2023, entlassen am 10.04.2023",
    "Krankenhausaufenthalt vom 15.06.2023 bis 25.06.2023",
    "stationär vom 20.01.2024 bis 30.01.2024"
]

stay_reasons=[
    "Kontrolle",
    "OP",
    "varia",
    "krank",
    "gesund"
]

room_numbers = [
    "101",
    "3B",
    "45",
    "12A"
]

station_names=[
    "Station escherich",
    "Station 7",
    "Station Moro",
    "Station 2A"
]


diagnoses = {
    "Appendizitis": "K37",
    "Spastisch-dystone Zerebralparese GMFCS °IV": "G80.3",
    "Arthrose": "M15-M19",
    "Peripartaler Asphyxie": "P21.9",
    "Herzinfarkt": "I25.2",
    "Fraktur": "Z87.81",
    "COPD": "J44",
    "Bronchitis": "J42",
    "Hypertonie": "I10",
    "Diabetes Mellitus": "E11.9",
    "Asthma": "J45",
    "Pneumonie": "J18.9",
    "arterielle Hypertonie": "I10",  # Essential hypertension
    "Diabetes mellitus Typ 2": "E11",  # Type 2 diabetes
    "Hyperlipidämie": "E78.5",  # Elevated lipids (unspecified)
    "chronische Niereninsuffizienz": "N18.9",  # Chronic kidney disease, unspecified
    "status post Schlaganfall": "I69.3",  # Sequelae of cerebral infarction
    "chronisches Schmerzsyndrom": "R52.2",  # Chronic pain, not elsewhere classified
    "epileptische Anfälle in der Vorgeschichte": "Z86.6",  # Personal history of epilepsy
    "bekannte Demenz": "F03.9",  # Unspecified dementia
    "chronische Hepatitis C": "B18.2",  # Chronic viral hepatitis C
    "Asthma bronchiale": "J45.9",  # Asthma, unspecified
    "koronare Herzkrankheit": "I25.1",  # Atherosclerotic heart disease
    "Vorhofflimmern": "I48.0",  # Paroxysmal atrial fibrillation
    "Adipositas": "E66.9",  # Obesity, unspecified
    "Zustand nach Bypass-Operation": "Z95.1",  # Presence of aortocoronary bypass graft
    "Zustand nach Endoprothese Hüfte": "Z96.64",  # Presence of hip implant
    "Zustand nach Endoprothese Knie": "Z96.65",  # Presence of knee implant
    "Osteoporose": "M81.0",  # Age-related osteoporosis without fracture
    "Rheumatoide Arthritis": "M06.9",  # Rheumatoid arthritis, unspecified
    "Parkinson-Krankheit": "G20",  # Parkinson’s disease
    "Multiple Sklerose": "G35",  # Multiple sclerosis
    "Gastroösophagealer Reflux":"K21.9",
    "gastroösophagealer Reflux mit Ösophagitis": "K21.0",
    "mangelnde Gewichtszunahme (Kind)": "R62.8",
    "mangelnde Gewichtszunahme (Neugeborenes)": "P92.6",
    "mangelnde Gewichtszunahme (Erwachsener, unspezifisch)": "R63.4",
    "Spastisch-dystone Zerebralparese":"G80.8",
    "Spastisch-dystone Zerebralparese (dyskinetisch betont)": "G80.3",  # Dyskinetic cerebral palsy
    "Spastisch-dystone Zerebralparese (gemischt)": "G80.8",  # Mixed type / Other cerebral palsy

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
    "Keine Droge, keine Alcool"
]

risk_factors = [
    "familiäre Vorbelastung Diabetes", "Adipositas BMI 32","Nikotinabusus",
    "Hyperlipidämie", "Schlafapnoe","Hypercholesterinämie", "RR erhöht","höheres Lebensalter"
]

# Names and other data
names = ["Herr. Max Müller", "Patientin: Anna Schmidt", "L. Weber", "Frau Sophie Fischer","Otto Kromberger","Irina, Klose"
         "John Smith", "Mary Jones", "Robert Lee", "Emily Davis"]
doctors = ["Dr. Müller", "Dr. Schneider", "Dr. Becker", "Dr. Weber","Dr. Suhle Nikolas", "Dr. Lehmann", "Dr. Fischer", "Dr. Weber",
           "Dr. Adams", "Dr. Lee", "Dr. Patel", "Dr. Chen", "Prof. A. Passero","Frau Moller", "Herr Moller"]


symptoms = [

    #Neurologische Symptome
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
    "niedergeschlagen",
    "Bluthochdruck",

    #Kardiopulmonale Symptome
    "Brustschmerzen",
    "Atemnot",
    "Palpitationen",
    "Orthopnoe",
    "Husten",
    "Zyanose",
    "Druckgefühl in der Brust",
    "Kaltschweißigkeit",
    "Synkope",

    #Allgemeine Symptome
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
    "Kribbeln auf der linke Arm",

    #Gastrointestinale Symptome
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

    #Urologische Symptome
    "Schmerzen beim Wasserlassen",
    "Häufiger Harndrang",
    "Nykturie",
    "Harnverhalt",
    "Blut im Urin",
    "Inkontinenz",

    #Dermatologische Symptome
    "Hautausschlag",
    "Juckreiz",
    "Schwellung",
    "Rötung",
    "Hautveränderungen",
    "Gewichtszunahme",
    "gastroösophagealen Reflux",
    "Mundgeruch",
    "wiederholtem Spucken",
    "starkem ösophagalen Reflux",
    "Erbrechen",
    "erschwerter Nahrungszufuhr "


]
medications = [

    #Blutdruckmedikamente (Antihypertensiva)
    "Ramipril",
    "Amlodipin",
    "Bisoprolol",
    "Lisinopril",
    "Valsartan",
    "Metoprolol",
    "Hydrochlorothiazid",
    "Candesartan",
    "Enalapril",

    #Antidiabetika
    "Metformin",
    "Insulin",
    "Empagliflozin",
    "Glimepirid",
    "Sitagliptin",
    "Dapagliflozin",

    #Cholesterinsenker
    "Atorvastatin",
    "Simvastatin",
    "Rosuvastatin",
    "Pravastatin",

    #Psychopharmaka & Schlafmittel
    "Diazepam",
    "Lorazepam",
    "Zolpidem",
    "Amitriptylin",
    "Mirtazapin",
    "Sertralin",
    "Citalopram",

    #Schmerzmittel / NSAR
    "Ibuprofen",
    "Paracetamol",
    "ASS",
    "Diclofenac",
    "Naproxen",
    "Novalgin",
    "Metamizol",

    #Antibiotika
    "Amoxicillin",
    "Ciprofloxacin",
    "Azithromycin",
    "Doxycyclin",
    "Clarithromycin",

    #Asthma / COPD
    "Salbutamol",
    "Formoterol",
    "Budesonid",
    "Tiotropium",
    "Beclometason",

    #Blutverdünner / Antikoagulantien
    "Marcumar",
    "Xarelto",
    "Eliquis",
    "Pradaxa",
    "Heparin",
    "Clopidogrel",

    #Rheuma / Immunsuppressiva
    "Methotrexat",
    "Prednisolon",
    "Cortison",
    "Adalimumab",
    "Infliximab"
]

treatments = ["Sauerstofftherapie", "Operation", "Chemotherapie", "Physiotherapie", "Reha"]
lab_results = ["Hb 13.5 g/dL", "Blutzucker 110 mg/dL", "Cholesterin 200 mg/dL","Glukose: 110 mg/dL"]
findings =[ "Infiltrat in der rechten Lunge"  , 
            "Herzvergrößerung", 
            "Pleuraerguss"    , 
            "Leukozytose"     , 
            "Erhöhte Leberwerte"              , 
            "Positive Bakterienkultur"        , 
            "Nicht verschobene Radiusfraktur" , 
            "Normaler EEG-Befund" , 
            "Glatte Hirnhaut"     , 
            "Kein Nachweis von Metastasen"    , 
            "Verdickte Darmwand im Colon"     , 
            "Beidseitige Pneumonie"           , 
            "Erhöhte Blutsenkungsgeschwindigkeit" , 
            "Hyperglykämie"             , 
            "Reduzierte Nierenfunktion" , 
            "Pathologisches EKG"        , 
            "Hämaturie"                 , 
            "Albuminurie"               , 
            "Hautausschlag an den Extremitäten"   , 
            "Geringe Beweglichkeit im rechten Kniegelenk"]
allergies = ["Penicillin", "Pollen", "Nüsse","Hausstaubmilben","Tierhaar", "Soia", "keine Bekannt"]
immunizations = ["Masern-Impfung", "Grippeimpfung", "Covid 19"]
devices = ["Herzschrittmacher", "Insulinpumpe","Schlafmaske", "Blutdruckgerät", "Kateter","PEG-Sonde"]
family_histories = ["Mutter mit Diabetes", "Vater mit Bluthochdruck","Herzinfarkte beim Vater", "Krebs bei der Mutter",
                    "Diabetes in der Familie", "Vater hatte einen Schlaganfall", "Bruder mit Zuckerkrakheit"]
procedures = ["Angioplastie", "MRT-Scan", "Biopsie", "Ultraschall","CT Kopf", "Lyse-Therapie",
              "Ösophagogastroduodenoskopie", "ÖGD", "Röntgen MDP","laparoskopische Fundoplicatio", "assistierten Gastrostomie"]
departments = ["Kardiologie", "Notaufnahme", "Onkologie", "Radiologie","Neurologie", "Innere Medizin", "Sozialdienst"]

hospital_names = ["St. Marien Krankenhaus", "Allgemeine Gesundheitsklinik","Fachklinik Gailingen", "Rehaklinik Schönberg",
                  "Städtisches Medizinzentrum", "Universitätsklinikum München", "Kinderklinik Freiburg"]
hospital_addresses = ["Hauptstraße 12, 80331 München", "Berliner Allee 45, 40212 Düsseldorf",
                      "Lindenstraße 8, 10115 Berlin", "Goetheplatz 9, 50674 Köln",
                      "Hugstetterstr. 7 79106 Freiburg", "Kamphausenstr. 23, 79666 Reute"]
hospital_phones = ["089 123456", "0211 987654", "030 234567", "0221 456789", "0761 2720298", "3456", "112", "+4912120120"]
patient_phones = ["089 123456", "0211 987654", "030 234567", "0221 456789", "0761 2720298", "+491873446456"]

patient_addresses = ["Hauptstraße 12, 80331 München", "Berliner Allee 45, 40212 Düsseldorf","Lindenstraße 8, 10115 Berlin", "Goetheplatz 9, 50674 Köln",
                      "Hugstetterstr. 7 79106 Freiburg", "Kamphausenstr. 23, 79666 Reute"]
followup_reasons = [
    "zur Blutdruckkontrolle", "wegen anhaltender Schmerzen", "zur Verlaufskontrolle",
    "zur weiteren Abklärung", "zur Nachsorge", "zur Wundkontrolle", "zur Laborüberprüfung"
]

impressions = [
    "Hinweis auf Pneumonie", "wahrscheinlich virale Ursache", "unklares Abdomen",
    "mögliche Fraktur", "Verdacht auf Infekt", "Hinweis auf Tumor"
]



occupations = [
  "Gärtner", "Bäcker", "Metzger", "Professor", "Student", "Arbeitslose",
  "Händler", "Kaufmann", "Kauffrau", "Studentin", "Verkäuferin",
  "Lehrer", "Ärztin", "Ingenieur", "Friseur", "Journalist", "Sekretärin",
  "Arzt", "Ingenieur", "Polizist", "Koch", "Pfleger", "Krankenschwester", 
  "Techniker", "Elektriker", "Kaufmann","Kauffrau", "Projektmanager"
]

family_members = [
  "Familie","Bruder", "Schwester", "Mutter", "Vater", "Großvater", "Großmutter", "Enkel", "Enkelin","Schwiegertöchter",
  "Onkel", "Kind", "Kinder", "Sohn", "Tochter", "Cousine", "Neffe", "Nichte", "Witwe", "Eltern","Schwiegersohn", "Angehörige"
]

Arztbrief=					   "Arztbrief"
Befundbericht=                 "Befundbericht"
Operationsbericht=             "Operationsbericht"
Entlassungsbericht=            "Entlassungsbericht"
Anamnesebogen=                 "Anamnesebogen"
Radiologischer_Befund=         "Radiologischer Befund"
Laborbericht=                  "Laborbericht"
Pathologischer_Befund=         "Pathologischer Befund"
Überweisungsschein=            "Überweisungsschein"
Einwilligungserklärung=        "Einwilligungserklärung"
Impfpass=                      "Impfpass"
Rezept=                        "Rezept"
Therapieplan=                  "Therapieplan"
Pflegedokumentation=           "Pflegedokumentation"
OP_Freigabe=                   "OP-Freigabe"
Krankenhausaufnahmebogen=      "Krankenhausaufnahmebogen"
Heil_und_Kostenplan=          "Heil- und Kostenplan (HKP)"
Attest=                        "Attest"
Notfallbericht=                "Notfallbericht"
EKG_Befund=                    "EKG-Befund"
Roentgenbericht=               "Röntgenbericht"
CT_MRT_Befund=                 "CT-/MRT-Befund"
Pflegeüberleitungsbogen=       "Pflegeüberleitungsbogen"
RehaAntrag=                   "Reha-Antrag"
SozialmedizinischesGutachten= "Sozialmedizinisches Gutachten"

document_types = [
    Arztbrief,					
    Befundbericht,              
    Operationsbericht,          
    Entlassungsbericht,         
    Anamnesebogen,              
    Radiologischer_Befund,      
    Laborbericht,               
    Pathologischer_Befund,      
    Überweisungsschein,         
    Einwilligungserklärung,     
    Impfpass,                   
    Rezept,                     
    Therapieplan,               
    Pflegedokumentation,        
    OP_Freigabe,                
    Krankenhausaufnahmebogen,   
    Heil_und_Kostenplan,       
    Attest,                     
    Notfallbericht,             
    EKG_Befund,                 
    Roentgenbericht,            
    CT_MRT_Befund,              
    Pflegeüberleitungsbogen,    
    RehaAntrag,                 
    SozialmedizinischesGutachten
]

family_status = ["verheiratet", "geschieden", "verwitwet", "ledig", "getrennt", "in einer Beziehung", "alleinstehend"]







def __normalize_token(token):
    return unicodedata.normalize("NFKC", token.lower())

def __merge_date_tokens(tokens, tags):
    merged_tokens = []
    merged_tags = []
    i = 0
    while i < len(tokens):
        if (
            i + 4 < len(tokens)
            and re.fullmatch(r"\d{1,2}", tokens[i])
            and tokens[i+1] == "."
            and re.fullmatch(r"\d{1,2}", tokens[i+2])
            and tokens[i+3] == "."
            and re.fullmatch(r"\d{4}", tokens[i+4])
        ):
            merged_tokens.append(f"{tokens[i]}.{tokens[i+2]}.{tokens[i+4]}")
            merged_tags.append(tags[i])  # Nimm Tag des ersten Tokens
            i += 5
            continue

        # Uhrzeit: 18 : 24 [: 33 optional]
        if (
            i + 2 < len(tokens)
            and re.fullmatch(r"\d{1,2}", tokens[i])
            and tokens[i+1] == ":"
            and re.fullmatch(r"\d{1,2}", tokens[i+2])
        ):
            if (
                i + 4 < len(tokens)
                and tokens[i+3] == ":"
                and re.fullmatch(r"\d{1,2}", tokens[i+4])
            ):
                # Format: hh:mm:ss
                merged_tokens.append(f"{tokens[i]}:{tokens[i+2]}:{tokens[i+4]}")
                merged_tags.append(tags[i])
                i += 5
                continue
            else:
                # Format: hh:mm
                merged_tokens.append(f"{tokens[i]}:{tokens[i+2]}")
                merged_tags.append(tags[i])
                i += 3
                continue
        # Kein spezielles Format → Standard übernehmen
        merged_tokens.append(tokens[i])
        merged_tags.append(tags[i])
        i += 1
    return merged_tokens, merged_tags

# def is_numeric_or_code(token):
#     return re.fullmatch(r"[\d.]+", token) or re.fullmatch(r"[A-Z]\d{2}", token)



# def __generate_filtered_stopwords(data, id2label, threshold=0.95):
#     from collections import defaultdict
#     import unicodedata

#     def normalize(token):
#         return unicodedata.normalize("NFKC", token.lower())

#     token_counts = defaultdict(int)
#     token_non_entity_counts = defaultdict(int)
#     entity_token_set = set()

#     for entry in data:
#         tokens = entry["tokens"]
#         tags = entry["ner_tags"]
#         for token, tag_id in zip(tokens, tags):
#             token_n = normalize(token)
#             token_counts[token_n] += 1
#             label = id2label[tag_id]
#             if label != "O":
#                 entity_token_set.add(token_n)
#             else:
#                 token_non_entity_counts[token_n] += 1
#   # Substring-Matching Liste
#     substring_whitelist = [
#         "schmerz", "befund", "messung", "anamnese", "symptom", "diagnose", "therapie", "entzündung","untersuchung", "aufnahme", 
#         "fall", "arzt", "krank", "blut"
#     ]
#     manual_whitelist = {
#         "impression",

#         "puls", 
#         "risikofaktor", "medikament", 
#          "untersuchung", "beschwerden",  "verabreichtes",
#         "icd", "ursache", "folgegrund", "wahrscheinlich", "virale",
#        "kam", "ihn", "über", "empfohlen","patienten", "gerät",
#         "anhaltende", "vorherige", "frühere", "brachte", "wird",
#          # Symptome
#         "atemnot", "fieber", "husten", "kribbeln", "schwindel", "übelkeit",
#         "erbrechen", "lallende",  "schluckstörung", "blutdruck", "taubheit", "sehstörung",
#          "atemprobleme", "müdigkeit", "erschöpfung", "gewichtverlust",
    
#         # Diagnosen
#         "diabetes", "hypertonie", "hypotonie", "epilepsie", "tumor", "appendizitis", "schlaganfall",
#         "infarkt", "bronchitis", "asthma", "adipositas", "depression", "herzinsuffizienz",

#         # Medikamente
#         "metformin", "lisinopril", "insulin", "paracetamol", "ibuprofen", "antibiotika", "aspirin",
#         "glucose", "cholesterin",

#         # Maßnahmen
#         "eingriff", "operation", "behandlung",
#         "lyse", "injektion", "aufnahme", "entlassung",

#         # Geräte
#         "schlafmaske", "rollstuhl", "insulinpumpe", "beatmungsgerät", "infusionspumpe", "monitor",

#         # Labor
#        "puls", "blutdruck", "temperatur", "sauerstoffsättigung", "herzfrequenz",
#         "mg", "dl", "bmi", "gewicht", "größe",

#         # Familie
#         "vater", "mutter", "geschwister",  "cousine", "bruder", "familienmitglied"
#     }
#     manual_stopwords = {
#         "-", ":", ".", ",", "berichtete", "telefon", "tel", "/", "–", "(", ")", "„", "“",
#         "eine", "ein", "der", "die", "das", "am", "an", "im", "für", "mit", "von",
#         "es", "da", "und", "auch", "nicht", "bekannt", "zuvor", "wurde", "ist", "war", "sich",
#         "durch", "bei", "zu", "als", "in", "auf", "unter", "nach", "vor", "mehr", "weniger"
#     }
#     MIN_TOKEN_FREQ = 3 
#     whitelist = entity_token_set.union(manual_whitelist)
#     stop_words = set()
#     review_false_positives = []

#     for token, total_count in token_counts.items():
#         if total_count == 0:
#             continue

#         o_ratio = token_non_entity_counts[token] / total_count
#         if  any(substr in token for substr in substring_whitelist):
#             continue
#         elif token in manual_stopwords:
#             stop_words.add(token)
#         elif token in whitelist:
#             continue
#         elif is_numeric_or_code(token):
#             continue  # Zahlen und Codes nie stoppen
#         elif  total_count >= MIN_TOKEN_FREQ and o_ratio >= threshold:
#             stop_words.add(token)
#             if re.match(r"[a-zäöüß]+", token):  # keine reinen Zahlen/Punktuation
#                 review_false_positives.append((token, o_ratio))

#     # Logging
#     if review_false_positives:
#         print("\n⚠️  Potenziell falsch gestoppte relevante Tokens:")
#         for token, ratio in sorted(review_false_positives, key=lambda x: -x[1]):
#             print(f"[Stopword] {token} → {ratio:.2f}")

#     return stop_words

# def __clean_ner_tags(oldtokens, ner_tags, stop_words):
#     #clean_tags = ner_tags.copy()
#     tokens, clean_tags = __merge_date_tokens(oldtokens, ner_tags)
#     n = len(tokens)

#     for i in range(n):
#         label_id = clean_tags[i]
#         label = ID2LABEL[label_id]
#         token = normalize_token(tokens[i])  # <- normalize hier auch
       
#         if token in stop_words:
#             clean_tags[i] = LABEL2ID["O"]
#             continue

#         # I-Tag ohne voriges B- oder I- → B machen
#         if label.startswith("I-"):
#             entity = label[2:]
#             if i == 0 or not ID2LABEL[clean_tags[i - 1]].endswith(entity):
#                 clean_tags[i] = LABEL2ID.get("B-" + entity, label_id)

#         # Zwei B- direkt nacheinander mit gleicher Entität → zweites wird I-
#         if label.startswith("B-") and i > 0:
#             entity = label[2:]
#             prev_label = ID2LABEL[clean_tags[i - 1]]
#             if prev_label.startswith(("B-", "I-")) and prev_label.endswith(entity):
#                 clean_tags[i] = LABEL2ID.get("I-" + entity, label_id)
#     return tokens,clean_tags

# def refresh_and_clean_ner_labels(data, id2label, threshold = 0.95):

#     stopwords = __generate_filtered_stopwords(data, id2label,threshold)
#     for entry in data:
#         entry["tokens"],entry["ner_tags"] = __clean_ner_tags(entry["tokens"], entry["ner_tags"], stopwords)

#     return data




def get_fake_names(count =10):
    from faker import Faker
    fake = Faker('de_DE')  # German locale
    names = []
    for _ in range(count):

        names.append(fake.name())

    return names


def get_fake_address(count =10):
    from faker import Faker
    fake = Faker('de_DE')  # German locale
    address = []
    for _ in range(count):
        address.append(fake.address())
    return address

def get_fake_phone(count =10):
    from faker import Faker
    fake = Faker('de_DE')  # German locale
    phone_numbers = []
    for _ in range(count):
        phone_numbers.append(fake.phone_number())
    return phone_numbers

def get_fake_email(count =10):
    from faker import Faker
    fake = Faker('de_DE')  # German locale
    emails = []
    for _ in range(count):
        emails.append(fake.email())
    return emails


def get_fake_hospital():
    cities = ["Berlin", "Hamburg", "München", "Stuttgart", "Frankfurt"]
    types = ["Klinik", "Krankenhaus", "Medizinisches Zentrum", "Gesundheitszentrum"]
    saints = ["St. Nikolaus", "St. Elisabeth", "St. Johannes", "St. Marien"]
    specialties = ["Onkologie", "Herz", "Orthopädie", "Neurologie", "Reha"]

    style = random.choice(["city", "saint", "specialty", "generic"])
    if style == "city":
        return f"{random.choice(cities)} {random.choice(types)}"
    elif style == "saint":
        return f"{random.choice(saints)} {random.choice(types)}"
    elif style == "specialty":
        return f"Zentrum für {random.choice(specialties)}"
    else:
        return f"{random.choice(['Zentral', 'Modern', 'Premium'])} {random.choice(types)}"

def get_fake_hospitals(count =10):
    hospitals = []
    for _ in range(count):
        hospitals.append(get_fake_hospital())
    return hospitals


# def main():
#     # Lade Daten
#     data_path = "./data/train.json"
#     output_path = "dein_datensatz_cleaned2.json"
#     with open(data_path, "r", encoding="utf-8") as f:
#         data = json.load(f)
#     cleardata = refresh_and_clean_ner_labels(data,ID2LABEL, 0.95)
#     with open(output_path, "w", encoding="utf-8") as f:
#         json.dump(cleardata, f, indent=2, ensure_ascii=False)
#     print(f"✔ Bereinigt und gespeichert unter: {output_path}")


# # if __name__ == "__main__":
# #     main()


   