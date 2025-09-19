
#[the order follows a logic to create dynthetic data]
ENTITY_LIST =[ 
    "ADDRESS",
    "ADDRESS_PATIENT",
    'ADMISSION_DATE',
    "ALCOHOL_CONSUMPTION",
    "ALLERGY",
    "ANAMNESE",
    "BIRTHDATE",
    "BLOOD_TYPE",
    "BODY_PART",
    'COURSE',
    "DATE",   
    "DEPARTMENT",
    "DEVICE",
    "DIAGNOSIS",
    'DISCHARGE_DATE',
    "DOCTOR",
    "DOCUMENT_TYPE",
    "DOSAGE",
    "DURATION",
    "FAMILY_STATUS",
    "FAMILYMEMBER",
    "FAMHIST",
    "FINDING",
    "FOLLOWUP_REASON",
    "FOLLOWUP_REQ",
    "FREQUENCY",
    "GENDER",
    "GEWICHT",
    "GROESSE",
    'HOSPITAL_STAY',
    "ICD10_CODE",
    "ICD10_DESC",
    "IMMUNIZATION",
    "IMPRESSION",
    "INSURANCE_ID",
    "LAB_RESULT",
    "LIFESTYLE",
    "MEDICATION",
    "OCCUPATION",
    "ORG",
    "PATIENT",
    "PHONE",
    "PHONE_PATIENT",
    "PID",
    "PREV_DIAGNOSIS",
    "PROCEDURE",
    "RISKFACTOR",
    "ROOM_NUMBER",
    "ROUTE",
    "SMOKING_STATUS",  
    "STAY_REASON",
    "SYMPTOM",
    "TREATMENT",
    "VITALSIGNS",
]

# #these entties could appear more times 
# MORE_VAL_ENTITIES = {
#     "ANAMNESE","ALLERGY", "SYMPTOM", "MEDICATION", "VITALSIGNS", "TREATMENT", "FAMILYMEMBER", "FAMHIST", "ICD10_CODE","ICD10_DESC","DATE",
#     "PREV_DIAGNOSIS", "IMPRESSION", "LAB_RESULT", "LIFESTYLE", "RISKFAKTOR", "IMMUNIZATION", "DIAGNOSIS", "BODY_PART","STAY_REASON","FINDING"
# }

#should appear just once in the template
SINGLE_VAL_ENTITIES = {
    "PATIENT","BIRTHDATE", "GENDER", "PID", "INSURANCE_ID", "BLOOD_TYPE",
}


def __generate_bio_labels_list(entity_list):
    label_list = ["O"]  # O "Outside" the first one
    for entity in entity_list:
        label_list.append(f"B-{entity}")# begin
        label_list.append(f"I-{entity}")# inside
    return label_list

LABEL_LIST = __generate_bio_labels_list(entity_list=ENTITY_LIST)
LABEL2ID = {label: idx for idx, label in enumerate(LABEL_LIST)}
ID2LABEL = {idx: label for label, idx in LABEL2ID.items()}


def save_to_jscript_snippet(id2label):
    # Write to JavaScript file
    import os
    out_dir = 'frontend'
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "id2label.js"), "w", encoding="utf-8") as f:
        f.write("const ID2LABEL = {\n")
        for idx, label in id2label.items():
            f.write(f"  {idx}: \"{label}\",\n")
        f.write("};\n")



if __name__ == "__main__":
    save_to_jscript_snippet(ID2LABEL)