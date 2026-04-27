import re
import datetime
import random

import uuid
from typing import List, Tuple, Dict
import pytesseract
import platform
from pathlib import Path
import numpy as np
import os
import sys
import string
# Add project root to sys.path if needed
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from scripts.config import LABEL2ID, ID2LABEL, REDUCED_ENTITIES
from scripts.definitions import *
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

def __generate_patient_id():

    id = random.choice(string.ascii_uppercase)
    for _ in range(0,8):
        id += str(random.randint(0,9))
    return id

def generate_patient_ids(count=10):
    result = []
    for _ in range(count):
        result.append(__generate_patient_id())
    return result

def __generate_insurance_id():
    id = ""
    for _ in range(0,8):
        id += str(random.randint(0,9))
        id += random.choice(string.ascii_letters)
    return id

def generate_insurance_ids(count=10):
    result = []
    for _ in range(count):
        result.append(__generate_insurance_id())
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

def get_fake_hospitals(count = 10):
    hospitals = []
    for _ in range(count):
        hospitals.append(get_fake_hospital())
    return hospitals

def generate_room_number(count = 10):
    import string
    rooms = []
    for _ in range(count):
        rooms.append(str(random.randint(1,900)) + random.choice(string.ascii_letters))
        rooms.append(str(random.randint(1,100)))
    return rooms


def __get_random_elements(data_list, min_items=1, max_items=None):
    if max_items is None:
        max_items = len(data_list)
    count = random.randint(min_items, max_items)
    return random.sample(data_list, count)

#just for testing
def generate_patient_record():
    record = {
        "Anamnese": __get_random_elements(anamneses, 1, 2),
        "Symptome": __get_random_elements(symptoms, 1, 3),
        "Impressionen": __get_random_elements(impressions, 1, 2),
        "Befunde": __get_random_elements(findings, 1, 3)
    }
    return record

def sanitize_template(template):


    FALLBACK_VALUES = {
        "ADDRESS": "Musterstraße 12, Berlin",
        "PHONE": "030-123456",
        "TREATMENT": "konservative Therapie",
        "PROCEDURE": "klinische Untersuchung",
        "ROOM_NUMBER": "Zimmer 204",
        "INSURANCE_ID": "AOK-12345",
        "BODY_PART": "Thorax",
        "LAB_RESULT": "12.5 mg/dl",
        "FAMILY_STATUS": "verheiratet",
        "OCCUPATION": "Angestellter",
    }

    placeholders = re.findall(r"{(.*?)}", template)

    for ph in placeholders:
        if ph not in REDUCED_ENTITIES:
            replacement = FALLBACK_VALUES.get(
                ph,
                f"UNKNOWN_{ph}"
            )
            template = template.replace(f"{{{ph}}}", replacement)

    return template



# def main():
    # # Lade Daten
    # data_path = "./data/train.json"
    # output_path = "dein_datensatz_cleaned2.json"
    # with open(data_path, "r", encoding="utf-8") as f:
    #     data = json.load(f)
    # cleardata = refresh_and_clean_ner_labels(data,ID2LABEL, 0.95)
    # with open(output_path, "w", encoding="utf-8") as f:
    #     json.dump(cleardata, f, indent=2, ensure_ascii=False)
    # print(f"✔ Bereinigt und gespeichert unter: {output_path}")


# if __name__ == "__main__":
    # for i in range(3):
    #     patient = generate_patient_record()
    #     print(f"Patient {i+1}:")
    #     for key, values in patient.items():
    #         print(f"{key}:")
    #         for v in values:
    #             print(f" - {v}")
    #     print("\n" + "-"*40 + "\n")


   