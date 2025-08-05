# config.py


LABEL_LIST = [
    "O",
    "B-PERSON", "I-PERSON",
    "B-DOCTOR", "I-DOCTOR",
    "B-ORG", "I-ORG",
    "B-DATE", "I-DATE",
    "B-DIAGNOSIS", "I-DIAGNOSIS",
    "B-SYMPTOM", "I-SYMPTOM",
    "B-MEDICATION", "I-MEDICATION",
    "B-PROCEDURE", "I-PROCEDURE",
    "B-TREATMENT", "I-TREATMENT",
    "B-DEPARTMENT", "I-DEPARTMENT",
    "B-LAB_RESULT", "I-LAB_RESULT",
    "B-ALLERGY", "I-ALLERGY",
    "B-IMMUNIZATION", "I-IMMUNIZATION",
    "B-DEVICE", "I-DEVICE",
    "B-FAMHIST", "I-FAMHIST",
    "B-ADDRESS", "I-ADDRESS",
    "B-PHONE", "I-PHONE",
    "B-IMPRESSION", "I-IMPRESSION",
    "B-FINDING", "I-FINDING",
    "B-FlWUREASON", "I-FlWUREASON",
    "B-PREV_DIAGNOSIS", "I-PREV_DIAGNOSIS",
    "B-GENDER", "I-GENDER",
    "B-BIRTHDATE", "I-BIRTHDATE",
    "B-FAMILY_STATUS", "I-FAMILY_STATUS",
    "B-FlWUREC", "I-FlWUREC",
    "B-VITALSIGNS", "I-VITALSIGNS",
    "B-LIFESTYLE", "I-LIFESTYLE",
    "B-RISKFACTOR", "I-RISKFACTOR",
    "B-ICD10_CODE", "I-ICD10_CODE",
    "B-ICD10_DESC", "I-ICD10_DESC",
    "B-OCCUPATION", "I-OCCUPATION",
    "B-FAMILYMEMBER", "I-FAMILYMEMBER",
    "B-GEWICHT", "I-GEWICHT",
    "B-GROESSE", "I-GROESSE"
]


#[the order follows a logic to create dynthetic data]
ENTITY_LIST = [
    "PERSON",
    "GENDER", 
    "BIRTHDATE",
    "FAMILYMEMBER",
    "FAMILY_STATUS", 
    "DATE",
    "SYMPTOM",
    "VITALSIGNS", 
    "ALLERGY", 
    "IMMUNIZATION",
    "IMPRESSION", 
    "LAB_RESULT",
    "FINDING", 
    "PREV_DIAGNOSIS",
    "LIFESTYLE",
    "OCCUPATION",
    "FAMHIST",
    "DIAGNOSIS",
    "RISKFACTOR",
    "MEDICATION",
    "ICD10_CODE",
    "ICD10_DESC",
    "PROCEDURE", 
    "TREATMENT",     
    "DEVICE", 
    "FlWUREASON",
    "FlWUREC", 
    "DOCTOR", 
    "DEPARTMENT",
    "ORG", 
    "ADDRESS",
    "PHONE", 
    "GEWICHT",
    "GROESSE"
]


LABEL2ID = {label: idx for idx, label in enumerate(LABEL_LIST)}
ID2LABEL = {idx: label for label, idx in LABEL2ID.items()}
