import random
import json
from utils import *
from sklearn.model_selection import train_test_split
from config import LABEL2ID, ENTITY_LIST
from templates import TEMPLATES_LIST
# from transformers import AutoTokenizer
# tokenizer = AutoTokenizer.from_pretrained("bert-base-german-cased")
#region templates
entity_values = {                       
    "ALCOHOL_CONSUMPTION": 	alcohol_consumptions,	
    "ADDRESS": 				hospital_addresses,	
    "ADMISSION_DATE": 		generate_dates(), 	
    "ALLERGY": 				allergies,           
    "BIRTHDATE":           	generate_dates(start_year=1900,end_year=2024),	
    "BLOOD_TYPE" :         	blood_types,	
    "BODY_PART":           	body_parts,	
    'COURSE' :             	courses,	
    "DATE":                	generate_dates(),	
    "DOCUMENT_TYPE":       	document_types,	
    "DOSAGE":              	dosages,	
    "DEPARTMENT":          	departments,	
    "DEVICE":              	devices,	
    "DIAGNOSIS":           	list(diagnosis_icd10_map.values()),	
    "DISCHARGE_DATE":		generate_dates(),
    "DOCTOR":              	doctors,	
    "DURATION":            	durations,	
    "FAMILY_STATUS":       	family_status,	
    "FAMILYMEMBER":        	family_members,	
    "FAMHIST":             	family_histories,	
    "FINDING":             	findings,	
    "FOLLOWUP_REASON":     	followup_reasons,	
    "FOLLOWUP_REQ":        	["CT-Thorax", "Blutbild", "EKG"],	
    "FREQUENCY":           	frequencies,	
    "GENDER":              	["männlich", "weiblich", "divers"],	
    "GEWICHT":             	generate_random_weights(),	
    "GROESSE":             	generate_random_heights(),	
    "HOSPITAL_STAY":		["1","5","10","20","30"],		
    "ICD10_CODE":          	list(diagnosis_icd10_map.keys()),	
    "ICD10_DESC":          	list(diagnosis_icd10_map.values()),	
    "IMMUNIZATION":        	immunizations,	
    "IMPRESSION":          	impressions,	
    "INSURANCE_ID":        	insurance_ids,	
    "LAB_RESULT":          	lab_results,	
    "LIFESTYLE":           	lifestyles,	
    "MEDICATION":          	medications,	
    "OCCUPATION":          	occupations,	
    "ORG":                 	hospital_names,	
    "PERSON":              	names,	
    "PHONE":               	hospital_phones,	
    "PID":                 	generate_patint_ids(),	
    "PREV_DIAGNOSIS":      	prev_diagnoses,	
    "PROCEDURE":           	procedures,	
    "RISKFACTOR":          	risk_factors,	
    "ROOM_NUMBER":         	room_numbers,	
    "ROUTE":               	routes,	
    "SMOKING_STATUS" :     	smoking_status,  	
    "STAY_REASON":         	stay_reasons,	
    "SYMPTOM":             	symptoms,	
    "TREATMENT":			treatments,		        
    "VITALSIGNS":          	vitalsigns
}


def __create_bio_tags_from_offsets(tokens, entities, text):
    tags = ["O"] * len(tokens)

    # Baue eine Zuordnung von Zeichen-Offsets zu Token-Indices
    char_to_token = {}
    current_char = 0
    for idx, token in enumerate(tokens):
        while current_char < len(text) and text[current_char].isspace():
            current_char += 1  # Leerzeichen überspringen
        for _ in token:
            char_to_token[current_char] = idx
            current_char += 1

    for ent in entities:
        ent_start = ent["START"]
        ent_end = ent["END"]
        ent_label = ent["ENTITY"]

        # Finde die Token-Indices für Start und Ende
        token_indices = set()
        for i in range(ent_start, ent_end):
            if i in char_to_token:
                token_indices.add(char_to_token[i])

        if not token_indices:
            continue  # keine Token gefunden → skip

        token_indices = sorted(token_indices)
        tags[token_indices[0]] = f"B-{ent_label}"
        for idx in token_indices[1:]:
            tags[idx] = f"I-{ent_label}"

    return tags


def __create_bio_tags(tokens, entities, text):

    tags = ["O"] * len(tokens)

    for ent_name, ent_val in entities.items():
        if not ent_val:
            continue
        ent_tokens = smart_tokenize(ent_val)
        len_ent = len(ent_tokens)

        for i in range(len(tokens) - len_ent + 1):
            if tokens[i:i+len_ent] == ent_tokens:
                tags[i] = f"B-{ent_name}"
                for j in range(i+1, i+len_ent):
                    tags[j] = f"I-{ent_name}"
    return tags



def __extract_entities(text, values):
    ents = []
    for label, value in values.items():
        start = text.find(value)
        if start != -1:
            end = start + len(value)
            ents.append({"ENTITY": label,"START":start, "END":end, "VALUE":value})
    return ents

# def __bio_tags_to_ids_smart(tags, label2id):
#     tag_ids = []
#     for tag in tags[0]:
#         if tag not in label2id:
#             raise ValueError(f"Unbekannter Tag '{tag}' – fehlt im label2id?")
#         tag_ids.append(label2id[tag])
#     return tag_ids

# def __create_bio_tags_smart(text, entities):
#     encoding = tokenizer(text, return_offsets_mapping=True, return_attention_mask=False, add_special_tokens=False)
#     tags = ["O"] * len(encoding["offset_mapping"])
    
#     for ent in entities:
#         start_char = ent["START"]
#         end_char = ent["END"]
#         label = ent["ENTITY"]
        
#         for i, (start, end) in enumerate(encoding["offset_mapping"]):
#             if start >= end_char or end <= start_char:
#                 continue
#             if start >= start_char and end <= end_char:
#                 if tags[i] == "O":
#                     tags[i] = f"B-{label}" if start == start_char else f"I-{label}"
#     return tags, encoding.tokens()




def __create_sample():
    return {ent: random.choice(entity_values[ent]) for ent in ENTITY_LIST if ent in entity_values}


def __extract_entities_smart(text, values):
    ents = []
    used_spans = set()

    for label, value in values.items():
        # Verwende re.finditer für mehrere Vorkommen
        for match in re.finditer(re.escape(value), text):
            start, end = match.span()
            if (start, end) not in used_spans:
                ents.append({"ENTITY": label, "START": start, "END": end, "VALUE": value})
                used_spans.add((start, end))
                break  # Nur erstes Vorkommen pro Label
    return ents

def __bio_tags_to_ids(tags, label2id):
    return [label2id.get(tag, 0) for tag in tags]

def __generate_paraphrase_text(values):
    phrases = []
    temp_values = values.copy()
    hospital_phrase = paraphrase_hospital_stay(temp_values)
    if hospital_phrase:
        phrases.append(hospital_phrase)
        # Optional: remove single Keys
        for key in ["ADMISSION_DATE", "DISCHARGE_DATE", "STAY_REASON"]:
            temp_values.pop(key, None)
    # Medication special
    medication_phrase = paraphrase_medication_combination(temp_values)
    if medication_phrase:
        phrases.append(medication_phrase)
        for key in ["MEDICATION", "DOSAGE", "FREQUENCY", "DURATION"]:
            temp_values.pop(key, None)

    for ent_type in ENTITY_LIST:
        if ent_type in temp_values:
            phrase = paraphrase_entity(ent_type, temp_values[ent_type])
            phrases.append(phrase)

    # Shuffle the phrases and join
    random.shuffle(phrases)
    return " ".join(phrases)

def __generate_dataset(n_samples,save_reports):
    import os
    dataset = []
    count_template = 0
    count_paraphrase = 0
    for i in range(n_samples):
        try:
            template = random.choice(TEMPLATES_LIST)
            values = __create_sample()
            if random.random() < 0.5:            
                text = template.format(**values)
                # text = Template(template).safe_substitute(values) just with preformatted string f" vvava {value}"
                count_template +=1
            else:
                text = __generate_paraphrase_text(values)
                count_paraphrase += 1

            entities = __extract_entities_smart(text, values)

            matched_entities = {e["ENTITY"]: e["VALUE"] for e in entities}
            # print(f"Entities:\n {entities}")
            tokens = smart_tokenize(text)
            #tags_bio = __create_bio_tags(tokens, matched_entities, text)
            tags = __create_bio_tags_from_offsets(tokens=tokens,entities=entities, text=text)
            tag_ids = __bio_tags_to_ids(tags, LABEL2ID)

            if save_reports:
                filename = f"./txt_reports/report_{i+1}.txt"
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(text)


                entity_filename = f"./entities/entity_{i+1}.json"
                os.makedirs(os.path.dirname(entity_filename), exist_ok=True)
                with open(entity_filename, 'w',encoding="utf-8") as f:
                    json.dump(entities, f,ensure_ascii=False, indent=4) 

            dataset.append( {
                "tokens": tokens,
                "ner_tags": tag_ids
            })
        except Exception as e:
            print(f"{e}" , {i})

    trains, validations = train_test_split(dataset, test_size=0.1, random_state=42)
    trains, tests = train_test_split(trains, test_size=0.1, random_state=42)

    os.makedirs("./data", exist_ok=True)
    with open("./data/all_data.json", "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
        print(f"saved all data  ./data/all_data.json ")


    with open("./data/train.json", "w", encoding="utf-8") as f:
        json.dump(trains, f, indent=2, ensure_ascii=False)
    with open("./data/val.json", "w", encoding="utf-8") as f:
        json.dump(validations, f, indent=2, ensure_ascii=False)
    with open("./data/test.json", "w", encoding="utf-8") as f:
        json.dump(tests, f, indent=2, ensure_ascii=False)
    print("✅ Synthetic dataset generated:")
    print(f"→ ./data/train.json ({len(trains)} samples)")
    print(f"→ ./data/val.json ({len(validations)} samples)")
    print(f"→ ./data/test.json ({len(tests)} samples)")
    if save_reports:
        print(f"→ ./txt_reports/ ({n_samples} samples)")


    print(f"From template {count_template}, from paraphrase {count_paraphrase}")

# Run as script
if __name__ == "__main__":
    import sys
    n_samples = 100
    save_reports = False
    clean_data = False
    if len(sys.argv) > 1:
        n_samples = int(sys.argv[1])
    if len(sys.argv) > 2:
        save_reports = sys.argv[2].lower() == 'true'
    if len(sys.argv) > 3:
        clean_data = sys.argv[3].lower() == 'true'
    print(f"Starting generation of {n_samples} data!\n Saving reports is {save_reports}!\n Cleaning data option {clean_data}!")
    __generate_dataset(n_samples=n_samples, save_reports=save_reports,)


