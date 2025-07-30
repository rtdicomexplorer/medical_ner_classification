import uuid
from dateutil.parser import parse
from normalizer import search_cui

CONFIDENCE_THRESHOLD = 0.5

def normalize_entity_mock(text, label):
    mock_db = {
        ("Asthma", "DIAGNOSIS"): {"code": "J45", "source": "ICD10CM", "name": "Asthma"},
        ("Ramipril", "MEDICATION"): {"code": "161", "source": "RXNORM", "name": "Ramipril"},
        ("Schlaganfall", "DIAGNOSIS"): {"code": "I63", "source": "ICD10CM", "name": "Schlaganfall"}
    }
    return mock_db.get((text, label), None)

def normalize_entity(text, label):
    return normalize_entity_mock(text, label)

def normalize_text(text, label):
    text = text.strip()
    for prefix in ["dr.", "dr", "herr", "frau", "prof.", "prof"]:
        if text.lower().startswith(prefix + " "):
            text = text[len(prefix) + 1:]
    return text.lower()

def fix_labels(entities):
    fixed = []
    for ent in entities:
        label = ent["entity_group"] if "entity_group" in ent else ent["entity"]
        word = ent["word"]
        if label == "PERSON" and word.lower().startswith("dr"):
            label = "DOCTOR"
        fixed.append({"word": word, "entity": label, "score": ent.get("score", 1.0)})
    return fixed

def merge_entities(entities):
    merged = []
    buffer = None

    for ent in entities:
        if ent["score"] < CONFIDENCE_THRESHOLD:
            continue

        if buffer and ent["entity"] == buffer["entity"] and ent["start"] == buffer["end"]:
            buffer["word"] += ent["word"].replace("##", "")
            buffer["end"] = ent["end"]
            buffer["score"] = min(buffer["score"], ent["score"])
        else:
            if buffer:
                merged.append(buffer)
            buffer = ent.copy()

    if buffer:
        merged.append(buffer)

    return merged

def map_ner_to_fhir(raw_entities):
    entities = fix_labels(raw_entities)
    # entities = merge_entities(entities)

    bundle_entries = []
    seen = set()

    patient_cache = {}
    practitioner_cache = {}
    current_patient_id = None
    last_doctor_id = None

    def make_id():
        return str(uuid.uuid4())[:8]

    for ent in entities:
        label = ent["entity"]
        text = ent["word"].strip()
        norm_text = normalize_text(text, label)

        if (norm_text, label) in seen:
            continue
        seen.add((norm_text, label))

        if label == "PERSON":
            pid = patient_cache.get(norm_text)
            if not pid:
                pid = make_id()
                parts = text.split()
                patient = {
                    "resourceType": "Patient",
                    "id": pid,
                    "name": [{"given": parts[:-1], "family": parts[-1] if parts else ""}]
                }
                bundle_entries.append(patient)
                patient_cache[norm_text] = pid
            current_patient_id = pid

        elif label == "DOCTOR":
            doc_id = practitioner_cache.get(norm_text)
            if not doc_id:
                doc_id = make_id()
                parts = text.split()
                practitioner = {
                    "resourceType": "Practitioner",
                    "id": doc_id,
                    "name": [{"given": parts[:-1], "family": parts[-1] if parts else ""}]
                }
                bundle_entries.append(practitioner)
                practitioner_cache[norm_text] = doc_id
            last_doctor_id = doc_id

        elif label == "DIAGNOSIS":
            norm = normalize_entity(text, label)
            resource = {
                "resourceType": "Condition",
                "id": make_id(),
                "code": {"text": text},
                "subject": {"reference": f"Patient/{current_patient_id}"} if current_patient_id else {}
            }
            if norm:
                resource["code"]["coding"] = [{
                    "system": f"http://hl7.org/fhir/sid/{norm['source']}",
                    "code": norm["code"],
                    "display": norm["name"]
                }]
            bundle_entries.append(resource)

        elif label == "FAMILY_HISTORY":
            bundle_entries.append({
                "resourceType": "FamilyMemberHistory",
                "id": make_id(),
                "note": [{"text": text}],
                "patient": {"reference": f"Patient/{current_patient_id}"} if current_patient_id else {}
            })

        elif label == "MEDICATION":
            norm = normalize_entity(text, label)
            med = {
                "resourceType": "MedicationRequest",
                "id": make_id(),
                "medicationCodeableConcept": {"text": text},
                "subject": {"reference": f"Patient/{current_patient_id}"} if current_patient_id else {}
            }
            if norm:
                med["medicationCodeableConcept"]["coding"] = [{
                    "system": f"http://hl7.org/fhir/sid/{norm['source']}",
                    "code": norm["code"],
                    "display": norm["name"]
                }]
            bundle_entries.append(med)

        elif label == "LAB_RESULT":
            bundle_entries.append({
                "resourceType": "Observation",
                "id": make_id(),
                "valueString": text,
                "subject": {"reference": f"Patient/{current_patient_id}"} if current_patient_id else {}
            })

        elif label == "PROCEDURE":
            procedure = {
                "resourceType": "Procedure",
                "id": make_id(),
                "code": {"text": text},
                "subject": {"reference": f"Patient/{current_patient_id}"} if current_patient_id else {}
            }
            if last_doctor_id:
                procedure["performer"] = [{"actor": {"reference": f"Practitioner/{last_doctor_id}"}}]
            bundle_entries.append(procedure)

        elif label == "TREATMENT":
            bundle_entries.append({
                "resourceType": "CarePlan",
                "id": make_id(),
                "description": text,
                "subject": {"reference": f"Patient/{current_patient_id}"} if current_patient_id else {}
            })

        elif label == "DATE":
            try:
                date_str = parse(text).isoformat()
            except Exception:
                date_str = text
            bundle_entries.append({
                "resourceType": "Observation",
                "id": make_id(),
                "effectiveDateTime": date_str,
                "subject": {"reference": f"Patient/{current_patient_id}"} if current_patient_id else {}
            })

        elif label == "ALLERGY":
            bundle_entries.append({
                "resourceType": "AllergyIntolerance",
                "id": make_id(),
                "code": {"text": text},
                "patient": {"reference": f"Patient/{current_patient_id}"} if current_patient_id else {}
            })

        elif label == "IMMUNIZATION":
            bundle_entries.append({
                "resourceType": "Immunization",
                "id": make_id(),
                "vaccineCode": {"text": text},
                "patient": {"reference": f"Patient/{current_patient_id}"} if current_patient_id else {}
            })

        elif label == "DEVICE":
            bundle_entries.append({
                "resourceType": "Device",
                "id": make_id(),
                "type": {"text": text},
                "patient": {"reference": f"Patient/{current_patient_id}"} if current_patient_id else {}
            })

    return {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [{"resource": r} for r in bundle_entries]
    }
