import uuid
from dateutil.parser import parse
from normalizer import search_cui


def normalize_entity_mock(text, label):
    mock_db = {
        ("Asthma", "DIAGNOSIS"): {"code": "J45", "source": "ICD10CM", "name": "Asthma"},
        ("Paracetamol", "MEDICATION"): {"code": "161", "source": "RXNORM", "name": "Paracetamol"},
    }
    return mock_db.get((text, label), None)


def normalize_entity(text, label):
    '''Waiting for access key'''
    # Use mock or real search_cui when available
    return normalize_entity_mock(text, label)
    if label == "DIAGNOSIS":
        return search_cui(text, source="ICD10CM") or search_cui(text, source="SNOMEDCT_US")
    elif label == "MEDICATION":
        return search_cui(text, source="RXNORM")
    return None


def normalize_text(text, label):
    text = text.strip()
    if label in ("PERSON", "DOCTOR"):
        for prefix in ["dr.", "dr", "herr", "frau"]:
            if text.lower().startswith(prefix + " "):
                text = text[len(prefix) + 1 :]
    return text.lower()

def fix_labels(entities):
    """Post-process entities to fix labels based on heuristics."""
    fixed_entities = []
    for ent in entities:
        text = ent["word"]
        label = ent["entity"]
        # Fix PERSON with 'Dr.' or 'Dr ' prefix to DOCTOR
        if label == "PERSON" and (text.lower().startswith("dr.") or text.lower().startswith("dr ")):
            ent["entity"] = "DOCTOR"
        fixed_entities.append(ent)
    return fixed_entities

def map_ner_to_fhir(entities):

    entities = fix_labels(entities) 
    fhir_resources = []
    seen_text_label = set()

    # Caches for deduplication keyed by normalized text
    patient_cache = {}
    practitioner_cache = {}
    org_cache = {}
    department_cache = {}
    medication_cache = {}

    # Default references
    patient_id = None
    practitioner_id = None

    for ent in entities:
        text = ent["word"]
        label = ent["entity"]

        # Skip very short or noisy tokens
        if len(text) < 3 or text.startswith("##") or text.isspace():
            continue

        norm_text = normalize_text(text, label)
        if (norm_text, label) in seen_text_label:
            continue
        seen_text_label.add((norm_text, label))

        if label == "PERSON":
            if norm_text not in patient_cache:
                resource_id = str(uuid.uuid4())[:8]
                parts = text.split()
                given_names = parts[:-1] if len(parts) > 1 else []
                family_name = parts[-1] if len(parts) > 1 else parts[0]
                patient = {
                    "resourceType": "Patient",
                    "id": resource_id,
                    "name": [{"given": given_names, "family": family_name}],
                }
                fhir_resources.append(patient)
                patient_cache[norm_text] = resource_id
            patient_id = patient_cache[norm_text]

        elif label == "DOCTOR":
            if norm_text not in practitioner_cache:
                resource_id = str(uuid.uuid4())[:8]
                parts = text.split()
                given_names = parts[:-1] if len(parts) > 1 else []
                family_name = parts[-1] if len(parts) > 1 else parts[0]
                practitioner = {
                    "resourceType": "Practitioner",
                    "id": resource_id,
                    "name": [{"given": given_names, "family": family_name}],
                }
                fhir_resources.append(practitioner)
                practitioner_cache[norm_text] = resource_id
            practitioner_id = practitioner_cache[norm_text]

        elif label == "ORG":
            if norm_text not in org_cache:
                resource_id = str(uuid.uuid4())[:8]
                org = {
                    "resourceType": "Organization",
                    "id": resource_id,
                    "name": text,
                }
                fhir_resources.append(org)
                org_cache[norm_text] = resource_id

        elif label == "DEPARTMENT":
            if norm_text not in department_cache:
                resource_id = str(uuid.uuid4())[:8]
                dept = {
                    "resourceType": "Location",
                    "id": resource_id,
                    "name": text,
                }
                fhir_resources.append(dept)
                department_cache[norm_text] = resource_id

        elif label == "DIAGNOSIS":
            resource_id = str(uuid.uuid4())[:8]
            norm = normalize_entity(text, label)
            condition = {
                "resourceType": "Condition",
                "id": resource_id,
                "code": {"text": text},
            }
            if norm:
                condition["code"]["coding"] = [
                    {
                        "system": f"http://hl7.org/fhir/sid/{norm['source']}",
                        "code": norm["code"],
                        "display": norm["name"],
                    }
                ]
            if patient_id:
                condition["subject"] = {"reference": f"Patient/{patient_id}"}
            fhir_resources.append(condition)

        elif label == "MEDICATION":
            if norm_text not in medication_cache:
                resource_id = str(uuid.uuid4())[:8]
                norm = normalize_entity(text, label)
                med_req = {
                    "resourceType": "MedicationRequest",
                    "id": resource_id,
                    "medicationCodeableConcept": {"text": text},
                }
                if norm:
                    med_req["medicationCodeableConcept"]["coding"] = [
                        {
                            "system": f"http://hl7.org/fhir/sid/{norm['source']}",
                            "code": norm["code"],
                            "display": norm["name"],
                        }
                    ]
                if patient_id:
                    med_req["subject"] = {"reference": f"Patient/{patient_id}"}
                fhir_resources.append(med_req)
                medication_cache[norm_text] = resource_id

        elif label == "TREATMENT":
            resource_id = str(uuid.uuid4())[:8]
            care_plan = {
                "resourceType": "CarePlan",
                "id": resource_id,
                "description": text,
            }
            if patient_id:
                care_plan["subject"] = {"reference": f"Patient/{patient_id}"}
            fhir_resources.append(care_plan)

        elif label == "PROCEDURE":
            resource_id = str(uuid.uuid4())[:8]
            procedure = {
                "resourceType": "Procedure",
                "id": resource_id,
                "code": {"text": text},
            }
            if patient_id:
                procedure["subject"] = {"reference": f"Patient/{patient_id}"}
            if practitioner_id:
                procedure["performer"] = [
                    {"actor": {"reference": f"Practitioner/{practitioner_id}"}}
                ]
            fhir_resources.append(procedure)

        elif label == "DATE":
            resource_id = str(uuid.uuid4())[:8]
            try:
                iso_date = parse(text).isoformat()
            except Exception:
                iso_date = text
            observation = {
                "resourceType": "Observation",
                "id": resource_id,
                "effectiveDateTime": iso_date,
            }
            if patient_id:
                observation["subject"] = {"reference": f"Patient/{patient_id}"}
            fhir_resources.append(observation)

        elif label == "LAB_RESULT":
            resource_id = str(uuid.uuid4())[:8]
            lab_obs = {
                "resourceType": "Observation",
                "id": resource_id,
                "valueString": text,
            }
            if patient_id:
                lab_obs["subject"] = {"reference": f"Patient/{patient_id}"}
            fhir_resources.append(lab_obs)

        elif label == "ALLERGY":
            resource_id = str(uuid.uuid4())[:8]
            allergy = {
                "resourceType": "AllergyIntolerance",
                "id": resource_id,
                "code": {"text": text},
            }
            if patient_id:
                allergy["patient"] = {"reference": f"Patient/{patient_id}"}
            fhir_resources.append(allergy)

        elif label == "IMMUNIZATION":
            resource_id = str(uuid.uuid4())[:8]
            immunization = {
                "resourceType": "Immunization",
                "id": resource_id,
                "vaccineCode": {"text": text},
            }
            if patient_id:
                immunization["patient"] = {"reference": f"Patient/{patient_id}"}
            fhir_resources.append(immunization)

        elif label == "DEVICE":
            resource_id = str(uuid.uuid4())[:8]
            device = {
                "resourceType": "Device",
                "id": resource_id,
                "type": {"text": text},
            }
            if patient_id:
                device["patient"] = {"reference": f"Patient/{patient_id}"}
            fhir_resources.append(device)

        elif label == "FAMILY_HISTORY":
            resource_id = str(uuid.uuid4())[:8]
            family_history = {
                "resourceType": "FamilyMemberHistory",
                "id": resource_id,
                "note": [{"text": text}],
            }
            if patient_id:
                family_history["patient"] = {"reference": f"Patient/{patient_id}"}
            fhir_resources.append(family_history)

    return {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [{"resource": r} for r in fhir_resources],
    }
