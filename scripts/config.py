
#[the order follows a logic to create dynthetic data]
ENTITY_LIST =[
    "ADDRESS",
    "ALLERGY",
    "BIRTHDATE",
    "DATE",
    "DOCUMENT_TYPE",
    "DEPARTMENT",
    "DEVICE",
    "DIAGNOSIS",
    "DOCTOR",
    "FAMILY_STATUS",
    "FAMILYMEMBER",
    "FAMHIST",
    "FINDING",
    "FOLLOWUP_REASON",
    "FOLLOWUP_REQ",
    "GENDER",
    "GEWICHT",
    "GROESSE",
    "ICD10_CODE",
    "ICD10_DESC",
    "IMMUNIZATION",
    "IMPRESSION",
    "LAB_RESULT",
    "LIFESTYLE",
    "MEDICATION",
    "OCCUPATION",
    "ORG",
    "PERSON",
    "PHONE",
    "PID",
    "PREV_DIAGNOSIS",
    "PROCEDURE",
    "RISKFACTOR",
    "SYMPTOM",
    "TREATMENT",
    "VITALSIGNS"
]


NEW_ENTITIES =[
                       
'COURSE'                                        
'SMOKING_STATUS',                  
'ALCOHOL_CONSUMPTION',             
'BLOOD_TYPE',                      
'ADMISSION_DATE',
'DISCHARGE_DATE',
'DOSAGE',   
'DURATION', 
'FREQUENCY',
'ROUTE',    
'BODY_PART',
'INSURANCE_ID', 
'HOSPITAL_STAY',
'ROOM_NUMBER'  


]

def generate_bio_labels(entity_list):
    label_list = ["O"]  # O "Outside" the first one
    for entity in entity_list:
        label_list.append(f"B-{entity}")# begin
        label_list.append(f"I-{entity}")# inside
    return label_list

LABEL_LIST = generate_bio_labels(entity_list=ENTITY_LIST)
LABEL2ID = {label: idx for idx, label in enumerate(LABEL_LIST)}
ID2LABEL = {idx: label for label, idx in LABEL2ID.items()}


def save_to_jscript_snippet(id2label):
    # Write to JavaScript file
    with open("id2label.js", "w", encoding="utf-8") as f:
        f.write("const ID2LABEL = {\n")
        for idx, label in id2label.items():
            f.write(f"  {idx}: \"{label}\",\n")
        f.write("};\n")



if __name__ == "__main__":
    save_to_jscript_snippet(ID2LABEL)