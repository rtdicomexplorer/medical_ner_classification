import uuid


import uuid

def create_patient(name):
    return {
        "resourceType": "Patient",
        "id": str(uuid.uuid4()),
        "name": [{"text": name}],
    }

def create_practitioner(name):
    return {
        "resourceType": "Practitioner",
        "id": str(uuid.uuid4()),
        "name": [{"text": name}],
    }

def create_family_history(name):
    return {
        "resourceType": "FamilyMemberHistory",
        "id": str(uuid.uuid4()),
        "relationship": {"text": name},
    }

def create_condition(description):
    return {
        "resourceType": "Condition",
        "id": str(uuid.uuid4()),
        "code": {"text": description},
    }

def create_medication_statement(med_name):
    return {
        "resourceType": "MedicationStatement",
        "id": str(uuid.uuid4()),
        "medicationCodeableConcept": {"text": med_name},
    }

def create_symptom_observation(text):
    return {
        "resourceType": "Observation",
        "id": str(uuid.uuid4()),
        "code": {"text": "Symptom"},
        "valueString": text,
    }

def map_ner_to_fhir(entities):
    fhir_resources = []

    for ent in entities:
        label = ent["label"]
        text = ent["text"]
        role = ent.get("role", None)

        if label == "PERSON" and role == "Patient":
            fhir_resources.append(create_patient(text))

        elif label == "PERSON" and role == "Practitioner":
            fhir_resources.append(create_practitioner(text))

        elif label == "PERSON" and role == "FamilyMember":
            fhir_resources.append(create_family_history(text))

        elif label in ["DIAGNOSIS", "FINDING", "IMPRESSION", "PREV_DIAGNOSIS"]:
            fhir_resources.append(create_condition(text))

        elif label in ["SYMPTOM"]:
            fhir_resources.append(create_symptom_observation(text))

        elif label in ["MEDICATION"]:
            fhir_resources.append(create_medication_statement(text))

        # You can extend this for PROCEDURE, TREATMENT, VITALSIGNS, etc.

    return {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [{"resource": r} for r in fhir_resources]
    }


