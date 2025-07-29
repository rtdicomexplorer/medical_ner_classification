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

    return normalize_entity_mock(text, label)
    if label == "DIAGNOSIS":
        return search_cui(text, source="ICD10CM") or search_cui(text, source="SNOMEDCT_US")
    elif label == "MEDICATION":
        return search_cui(text, source="RXNORM")
    return None

def map_ner_to_fhir(entities):
    fhir_resources = []
    seen_text_label = set()

    patient_id = None
    practitioner_id = None

    for ent in entities:
        text = ent["word"]
        label = ent["entity"]

        if (text, label) in seen_text_label:
            continue
        seen_text_label.add((text, label))

        resource_id = str(uuid.uuid4())[:8]

        if label == "PERSON":
            parts = text.split()
            patient = {
                "resourceType": "Patient",
                "id": resource_id,
                "name": [{
                    "given": parts[:-1],
                    "family": parts[-1] if len(parts) > 1 else parts[0]
                }]
            }
            fhir_resources.append(patient)
            patient_id = resource_id

        elif label == "DOCTOR":
            parts = text.split()
            practitioner = {
                "resourceType": "Practitioner",
                "id": resource_id,
                "name": [{
                    "given": parts[:-1],
                    "family": parts[-1] if len(parts) > 1 else parts[0]
                }]
            }
            fhir_resources.append(practitioner)
            practitioner_id = resource_id

        elif label == "ORG":
            fhir_resources.append({
                "resourceType": "Organization",
                "id": resource_id,
                "name": text
            })

        elif label == "DEPARTMENT":
            fhir_resources.append({
                "resourceType": "Location",
                "id": resource_id,
                "name": text
            })

        elif label == "DIAGNOSIS":
            norm = normalize_entity(text, label)
            condition = {
                "resourceType": "Condition",
                "id": resource_id,
                "code": {
                    "text": text
                }
            }
            if norm:
                condition["code"]["coding"] = [{
                    "system": f"http://hl7.org/fhir/sid/{norm['source']}",
                    "code": norm["code"],
                    "display": norm["name"]
                }]
            if patient_id:
                condition["subject"] = {"reference": f"Patient/{patient_id}"}
            fhir_resources.append(condition)

        elif label == "MEDICATION":
            norm = normalize_entity(text, label)
            med_req = {
                "resourceType": "MedicationRequest",
                "id": resource_id,
                "medicationCodeableConcept": {
                    "text": text
                }
            }
            if norm:
                med_req["medicationCodeableConcept"]["coding"] = [{
                    "system": f"http://hl7.org/fhir/sid/{norm['source']}",
                    "code": norm["code"],
                    "display": norm["name"]
                }]
            if patient_id:
                med_req["subject"] = {"reference": f"Patient/{patient_id}"}
            fhir_resources.append(med_req)

        elif label == "TREATMENT":
            care_plan = {
                "resourceType": "CarePlan",
                "id": resource_id,
                "description": text
            }
            if patient_id:
                care_plan["subject"] = {"reference": f"Patient/{patient_id}"}
            fhir_resources.append(care_plan)

        elif label == "PROCEDURE":
            procedure = {
                "resourceType": "Procedure",
                "id": resource_id,
                "code": {"text": text}
            }
            if patient_id:
                procedure["subject"] = {"reference": f"Patient/{patient_id}"}
            if practitioner_id:
                procedure["performer"] = [{"actor": {"reference": f"Practitioner/{practitioner_id}"}}]
            fhir_resources.append(procedure)

        elif label == "DATE":
            try:
                iso_date = parse(text).isoformat()
            except Exception:
                iso_date = text
            observation = {
                "resourceType": "Observation",
                "id": resource_id,
                "effectiveDateTime": iso_date
            }
            if patient_id:
                observation["subject"] = {"reference": f"Patient/{patient_id}"}
            fhir_resources.append(observation)

        elif label == "LAB_RESULT":
            lab_obs = {
                "resourceType": "Observation",
                "id": resource_id,
                "valueString": text
            }
            if patient_id:
                lab_obs["subject"] = {"reference": f"Patient/{patient_id}"}
            fhir_resources.append(lab_obs)

        elif label == "ALLERGY":
            allergy = {
                "resourceType": "AllergyIntolerance",
                "id": resource_id,
                "code": {"text": text}
            }
            if patient_id:
                allergy["patient"] = {"reference": f"Patient/{patient_id}"}
            fhir_resources.append(allergy)

        elif label == "IMMUNIZATION":
            immunization = {
                "resourceType": "Immunization",
                "id": resource_id,
                "vaccineCode": {"text": text}
            }
            if patient_id:
                immunization["patient"] = {"reference": f"Patient/{patient_id}"}
            fhir_resources.append(immunization)

        elif label == "DEVICE":
            device = {
                "resourceType": "Device",
                "id": resource_id,
                "type": {"text": text}
            }
            if patient_id:
                device["patient"] = {"reference": f"Patient/{patient_id}"}
            fhir_resources.append(device)

        elif label == "FAMILY_HISTORY":
            family_history = {
                "resourceType": "FamilyMemberHistory",
                "id": resource_id,
                "note": [{"text": text}]
            }
            if patient_id:
                family_history["patient"] = {"reference": f"Patient/{patient_id}"}
            fhir_resources.append(family_history)

    return {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [{"resource": r} for r in fhir_resources]
    }
