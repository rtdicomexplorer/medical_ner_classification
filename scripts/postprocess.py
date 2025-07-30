# def postprocess_entities(entities, confidence_threshold=0.6):
#     merged = []
#     buffer = None

#     for ent in entities:
#         if ent["score"] < confidence_threshold:
#             continue

#         text = ent["word"].replace("##", "").strip()
#         if not text:
#             continue

#         if buffer and ent["entity"] == buffer["label"] and ent["start"] == buffer["end"]:
#             buffer["text"] += text
#             buffer["end"] = ent["end"]
#             buffer["score"] = max(buffer["score"], ent["score"])
#         else:
#             if buffer:
#                 merged.append(buffer)
#             buffer = {
#                 "text": text,
#                 "label": ent["entity"],
#                 "start": ent["start"],
#                 "end": ent["end"],
#                 "score": ent["score"],
#             }

#     if buffer:
#         merged.append(buffer)

#     return merged


import numpy as np
from collections import defaultdict
LABEL_THRESHOLDS = {
    "PERSON": 0.2,
    "DOCTOR": 0.2,
    "FAMILY_HISTORY": 0.15,
    "FAMILY_STATUS": 0.15,
    "FOLLOWUP_RECOMMENDATION": 0.2,
    "LIFESTYLE": 0.2,
    "RISKFACTOR": 0.2,
    "VITALSIGNS": 0.2,
    "SYMPTOM": 0.4,
    "DIAGNOSIS": 0.4,
    "MEDICATION": 0.4,
    "TREATMENT": 0.4,
    "PROCEDURE": 0.4,
    "ORG": 0.3,
    "DATE": 0.3,
    "ADDRESS": 0.3,
    "PHONE": 0.3,
    "DEVICE": 0.3,
    "DEPARTMENT": 0.3,
    "ICD10_CODE": 0.3,
    "ICD10_DESC": 0.3,
    "BIRTHDATE": 0.3,
    "GENDER": 0.3,
    "IMPRESSION": 0.3,
    "FINDING": 0.3,
    "PREV_DIAGNOSIS": 0.3,
    "_default": 0.3
}
def classify_person(text):
    """Heuristically classify a PERSON entity by role."""
    text = text.lower()

    if any(keyword in text for keyword in ["arzt", "dr", "doktor", "suhle"]):
        return "Practitioner"
    elif text in ["mutter", "vater", "bruder", "schwester", "tochter", "sohn"]:
        return "FamilyMember"
    elif len(text) <= 2 or not text.isalpha() or text in ["name", "datum", "amnese"]:
        return "Ignore"
    else:
        return "Patient"

def postprocess_entities(entities):
    """Clean and enhance the entity list."""
    seen = set()
    clean_entities = []

    for ent in entities:
        # Convert np.float32 to float
        score = float(ent["score"]) if isinstance(ent["score"], np.generic) else ent["score"]
        label = ent['entity']

        confidence_threshold = LABEL_THRESHOLDS.get(label, LABEL_THRESHOLDS["_default"]) 
        if score < confidence_threshold:
            print(f"⚠️ Entity filtered out: {ent['word']} [{label}] - score: {ent['score']:.2f}")
            continue

        text = ent["word"].strip(".,:;()[]{}")

        key = (text.lower(), ent["entity"])
        if key in seen:
            continue
        seen.add(key)

        processed = {
            "text": text,
            "label": label,
            "start": ent["start"],
            "end": ent["end"],
            "score": score
        }

        # Handle PERSON classification
        if ent["entity"] == "PERSON":
            role = classify_person(text)
            if role == "Ignore":
                continue
            processed["role"] = role

        clean_entities.append(processed)

    return clean_entities
