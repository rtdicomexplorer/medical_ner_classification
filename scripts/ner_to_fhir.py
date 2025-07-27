def map_ner_to_fhir(entities):
    fhir_resources = []

    for ent in entities:
        text = ent["word"]
        label = ent["entity"]

        if label == "PERSON":
            fhir_resources.append({
                "resourceType": "Patient",
                "name": [{"text": text}]
            })

        elif label == "DOCTOR":
            fhir_resources.append({
                "resourceType": "Practitioner",
                "name": [{"text": text}]
            })

        elif label == "ORG":
            fhir_resources.append({
                "resourceType": "Organization",
                "name": text
            })

        elif label == "DEPARTMENT":
            fhir_resources.append({
                "resourceType": "Location",
                "name": text
            })

        elif label == "DIAGNOSIS":
            fhir_resources.append({
                "resourceType": "Condition",
                "code": {"text": text}
            })

        elif label == "MEDICATION":
            fhir_resources.append({
                "resourceType": "MedicationRequest",
                "medicationCodeableConcept": {"text": text}
            })

        elif label == "TREATMENT":
            fhir_resources.append({
                "resourceType": "CarePlan",
                "description": text
            })

        elif label == "PROCEDURE":
            fhir_resources.append({
                "resourceType": "Procedure",
                "code": {"text": text}
            })

        elif label == "DATE":
            fhir_resources.append({
                "resourceType": "Observation",
                "effectiveDateTime": text
            })

        elif label == "LAB_RESULT":
            fhir_resources.append({
                "resourceType": "Observation",
                "valueString": text
            })

        elif label == "ALLERGY":
            fhir_resources.append({
                "resourceType": "AllergyIntolerance",
                "code": {"text": text}
            })

        elif label == "IMMUNIZATION":
            fhir_resources.append({
                "resourceType": "Immunization",
                "vaccineCode": {"text": text}
            })

        elif label == "DEVICE":
            fhir_resources.append({
                "resourceType": "Device",
                "type": {"text": text}
            })

        elif label == "FAMILY_HISTORY":
            fhir_resources.append({
                "resourceType": "FamilyMemberHistory",
                "note": [{"text": text}]
            })

    return fhir_resources
