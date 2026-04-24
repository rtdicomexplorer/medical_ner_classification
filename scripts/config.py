
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




REDUCED_ENTITIES = [
    "DATE",
    "DEPARTMENT",
    "DIAGNOSIS",
    "DOCTOR",
    "DOCUMENT_TYPE",
    "GENDER",
    "MEDICATION",
    "ORG",
    "PATIENT",
    "PID",
    "SYMPTOM"
]


ENTITY_COLORS = {
  "ANAMNESE": "#d1cdbdff",
  "ADDRESS": "#bdd1c2ff",
  "ADDRESS_PATIENT": "#bdd1c2ff",
  "ADMISSION_DATE": "#c0c70a",
  "ALCOHOL_CONSUMPTION": "#b1a3dfff",
  "ALLERGY": "#b5c4ecff",
  "BIRTHDATE": "#c359cc",
  "BLOOD_TYPE": "#d029a4",
  "BODY_PART": "#add0e7",
  "COURSE": "#e98788",
  "DATE": "#ca143a",
  "DEPARTMENT": "#199aef",
  "DEVICE": "#d2231e",
  "DIAGNOSIS": "#d15d27ff",
  "DISCHARGE_DATE": "#9fe7e4ff",
  "DOCTOR": "#57e665",
  "DOCUMENT_TYPE": "#f5716f",
  "DOSAGE": "#f6bf96",
  "DURATION": "#269323",
  "FAMILY_STATUS": "#03d080",
  "FAMILYMEMBER": "#8facdfff",
  "FAMHIST": "#1ca2fcff",
  "FINDING": "#e5a6b4ff",
  "FOLLOWUP_REASON": "#f556ad",
  "FOLLOWUP_REQ": "#56cb78",
  "FREQUENCY": "#e31919",
  "GENDER": "#d0d17e",
  "GEWICHT": "#519451",
  "GROESSE": "#40bb55",
  "HOSPITAL_STAY": "#5a8b08",
  "ICD10_CODE": "#c76f07",
  "ICD10_DESC": "#d381c2ff",
  "IMMUNIZATION": "#3066ed",
  "IMPRESSION": "#d44cbe",
  "INSURANCE_ID": "#b46e98",
  "LAB_RESULT": "#466af6",
  "LIFESTYLE": "#7882b6",
  "MEDICATION": "#e2ec82ff",
  "OCCUPATION": "#c0a0db",
  "ORG": "#f52243",
  "PATIENT": "#b1de4c",
  "PERSON": "#b1de4c",
  "PHONE": "#dab744ff",
  "PHONE_PATIENT": "#dab744ff",
  "PID": "#48d112",
  "PREV_DIAGNOSIS": "#09f5eb",
  "PROCEDURE": "#c1defa",
  "RISKFACTOR": "#d3d678ff",
  "ROOM_NUMBER": "#b52f3d",
  "ROUTE": "#b390c7ff",
  "SMOKING_STATUS": "#9182fa",
  "STAY_REASON": "#adec71ff",
  "SYMPTOM": "#08e843",
  "TREATMENT": "#c1d89aff",
  "VITALSIGNS": "#24d332",
};
     

LABEL_LIST = __generate_bio_labels_list(entity_list=REDUCED_ENTITIES)#__generate_bio_labels_list(entity_list=ENTITY_LIST) #
LABEL2ID = {label: idx for idx, label in enumerate(LABEL_LIST)}
ID2LABEL = {idx: label for label, idx in LABEL2ID.items()}


def save_to_jscript_snippet(id2label=ID2LABEL, entity_colors=ENTITY_COLORS):
    # Write to JavaScript file
    import os
    out_dir = 'frontend'
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "id2label.js"), "w", encoding="utf-8") as f:
        f.write("const ID2LABEL = {\n")
        for idx, label in id2label.items():
            f.write(f"  {idx}: \"{label}\",\n")
        f.write("};\n\n")
        f.write("const ENTITY_COLORS = {\n")
        for entity, color in entity_colors.items():
            f.write(f'  "{entity}": "{color}",\n')
        f.write("};\n")

if __name__ == "__main__":
    save_to_jscript_snippet(ID2LABEL, ENTITY_COLORS)