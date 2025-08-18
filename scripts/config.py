
#[the order follows a logic to create dynthetic data]
ENTITY_LIST = [
    "PERSON",
    "PID",
    "GENDER", 
    "BIRTHDATE",
    "FAMILYMEMBER",
    "FAMILY_STATUS", 
    "DATE",
    "SYMPTOM",
    "IMPRESSION", 
    "LAB_RESULT",
    "FINDING", 
    "PREV_DIAGNOSIS",
    "OCCUPATION",
    "DIAGNOSIS",
    "MEDICATION",
    "ICD10_CODE",
    "ICD10_DESC",
    "PROCEDURE", 
    "TREATMENT",     
    "DOCTOR", 
    "DEPARTMENT",
    "ORG", 
    "ADDRESS",
    "PHONE", 
    "GEWICHT",
    "GROESSE",
    "ALLERGY", 
    "IMMUNIZATION",
    "DEVICE", 
    "FAMHIST",
    "VITALSIGNS", 
    "LIFESTYLE",
    "RISKFACTOR",
    "FlWUREC",
    "FlWUREASON", 
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