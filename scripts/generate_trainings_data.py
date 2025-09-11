import os
import sys
# Add project root to sys.path if needed
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import random
import json
from scripts.utils import *
from sklearn.model_selection import train_test_split
from scripts.config import LABEL2ID, ENTITY_LIST, MORE_VAL_ENTITIES
from templates import TEMPLATES_LIST, muster_template
from collections import defaultdict


entity_values = {                       
    "ADDRESS": 				hospital_addresses,	
    "ADDRESS_PATIENT":      patient_addresses,
    "ADMISSION_DATE": 		generate_dates(), 	
    "ALCOHOL_CONSUMPTION": 	alcohol_consumptions,	
    "ALLERGY": 				allergies, 
    "ANAMNESE":             anamneses,          
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
    "HOSPITAL_STAY":		generate_random_hospital_stay(),		
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
    "PATIENT":              names,	
    "PHONE":               	hospital_phones,
    "PATIENT_PHONE":        patient_phones,	
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
def __extract_entities__(text, values):
    ents = []
    for label, value in values.items():
        start = text.find(value)
        if start != -1:
            end = start + len(value)
            ents.append({"ENTITY": label,"START":start, "END":end, "VALUE":value})
    return ents

def __create_sample_more_text():
    sample = {}
    # once Entities - random a value
    for ent in ENTITY_LIST:
        if ent in entity_values:
            sample[ent] = random.choice(entity_values[ent])
    # more time Entities - random value list
    for ent in MORE_VAL_ENTITIES:
        if ent in entity_values:
            sample[ent] = random.sample(entity_values[ent], 
                                       k=random.randint(1, min(3, len(entity_values[ent]))))
    return sample

def __normalize_text(text):
    return re.sub(r"\s+", " ", text.lower().strip())

def __extract_entities_generalized(text, values):
    """ To catch more details around prev_diagnosis or symptoms  maybe later..."""
    ENTITY_SYNONYMS = {
        "PREV_DIAGNOSIS": {
            "Herzinfarkt": ["status post Herzinfarkt", "Infarkt", "früherer Herzinfarkt"],
            "Fraktur": ["alte Fraktur", "Knochenbruch", "frühere Fraktur"],
            "Arthrose": ["bekannte Arthrose", "Arthrose", "Gelenkverschleiß"],
        },
        "SYMPTOM": {
            "Zyanose": ["bläuliche Verfärbung", "Zyanose"],
            "Taubheitsgefühl": ["Gefühllosigkeit", "Taubheit", "Taubheitsgefühl"],
            "Lähmung": ["Bewegungseinschränkung", "Lähmungen", "Paralyse"],
        },
        # Weitere ENTITY-Typen hier eintragen...
    }

    ents = []
    used_spans = set()
    text_norm = __normalize_text(text)

    for label, value in values.items():
        value_list = value if isinstance(value, list) else [value]
        synonyms = ENTITY_SYNONYMS.get(label, {})

        for val in value_list:
            val_str = str(val).strip()
            if not val_str:
                continue

            # 1. Alle möglichen Suchbegriffe (Original + Synonyme)
            search_terms = [val_str]
            if isinstance(synonyms, dict) and val_str in synonyms:
                search_terms.extend(synonyms[val_str])

            # 2. Überprüfe jeden Suchbegriff
            found = False
            for term in search_terms:
                term_norm = __normalize_text(term)
                matches = list(re.finditer(re.escape(term_norm), text_norm))
                for match in matches:
                    # Finde tatsächliche Position im Originaltext (unsicher bei Normalisierung!)
                    span_start = text.lower().find(term_norm, match.start())
                    if span_start == -1:
                        continue
                    span_end = span_start + len(term_norm)
                    
                    if (span_start, span_end) not in used_spans:
                        ents.append({
                            "entity_group": label,
                            "start": span_start,
                            "end": span_end,
                            "word": val_str
                        })
                        used_spans.add((span_start, span_end))
                        found = True
                        break
                if found:
                    break  # gehe zur nächsten Value
    return ents

def __generate_paraphrase_more_text(values):
    phrases = []

    # Paraphrase für Mehrfachwerte-Entities (alle Werte)
    for ent in MORE_VAL_ENTITIES:
        if ent in values:
            # values[ent] ist Liste → paraphrasiere alle und füge hinzu
            for val in values[ent]:
                paraphrase = paraphrase_entity(ent, val)
                phrases.append(paraphrase)

    # Paraphrase für Einmal-Entities
    for ent in ENTITY_LIST:
        if ent in values and ent not in MORE_VAL_ENTITIES:
            paraphrase = paraphrase_entity(ent, values[ent])
            phrases.append(paraphrase)
    
    random.shuffle(phrases)
    return " ".join(phrases)

def __count_entity_placeholders(template):
   
    pattern = r"{(\w+)}"
    counts = defaultdict(int)
    for match in re.findall(pattern, template):
        counts[match] += 1
    return counts

def __generate_values(entity_values, more_val_entities, placeholder_counts):
    values_for_template = {}

    for entity, count in placeholder_counts.items():
        if entity not in entity_values:
            continue

        val_list = entity_values[entity]
        if isinstance(val_list, str):
            val_list = [val_list]

        if entity in more_val_entities:
            # Mehrfach vorkommende Entitäten → zufällige Auswahl, ggf. mit Duplikaten
            sampled = random.choices(val_list, k=count)
            values_for_template[entity] = sampled
        else:
            # Nur ein Wert benötigt → denselben zufälligen Wert mehrfach einsetzen
            value = random.choice(val_list)
            values_for_template[entity] = [value] * count

    return values_for_template


def __fill_template(template, values_dict):
    pattern = r"{(\w+)}"
    output = template
    counters = defaultdict(int)

    def replacement(match):
        entity = match.group(1)
        val_list = values_dict.get(entity, [""])
        val = val_list[counters[entity]] if counters[entity] < len(val_list) else val_list[-1]
        counters[entity] += 1
        return val

    filled = re.sub(pattern, replacement, output)
    return filled

def __generate_dataset(n_samples,save_reports):
    dataset = []
    count_template = 0
    count_paraphrase = 0
    for i in range(n_samples):
        try:
            if random.random() < 0.5:     
                template = random.choice(TEMPLATES_LIST)
                placeholder_counts = __count_entity_placeholders(template)
                values_dict = __generate_values(entity_values, MORE_VAL_ENTITIES, placeholder_counts)
                text =  __fill_template(template, values_dict)
                entities = __extract_entities_generalized(text, values_dict)   
                count_template +=1
            else:
                values = __create_sample_more_text()  
                text = __generate_paraphrase_more_text(values)             
                entities = __extract_entities_generalized(text, values)  
                count_paraphrase += 1
            if save_reports:
                filename = f"./txt_reports/report_{i+1}.txt"
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(text)

                entity_filename = f"./entities/entity_{i+1}.json"
                os.makedirs(os.path.dirname(entity_filename), exist_ok=True)
                with open(entity_filename, 'w',encoding="utf-8") as f:
                    json.dump(entities, f,ensure_ascii=False, indent=4) 

            ner_data = generate_ner_data(text, entities)
            dataset.append( ner_data)
        except Exception as e:
            print(f"{e}" , {i})

    trains, validations = train_test_split(dataset, test_size=0.1, random_state=42)
    trains, tests = train_test_split(trains, test_size=0.1, random_state=42)
    
    print(f"💡 From template {count_template}, 🔁 from paraphrase {count_paraphrase}")

    #saving the json data created
    os.makedirs("./data", exist_ok=True)   
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
        with open("./data/all_data.json", "w", encoding="utf-8") as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        print(f"saved all data  ./data/all_data.json ")
        print(f"→ ./txt_reports/ ({n_samples} samples)")

   
# Run as script
if __name__ == "__main__":
    n_samples = 10
    save_reports = False
    clean_data = False
    if len(sys.argv) > 1:
        n_samples = int(sys.argv[1])
    if len(sys.argv) > 2:
        save_reports = sys.argv[2].lower() == 'true'
    print(f"Starting generation of {n_samples} data!\n Saving reports is {save_reports}!\n !")
    __generate_dataset(n_samples=n_samples, save_reports=save_reports,)


