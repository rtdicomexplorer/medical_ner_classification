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
from scripts.paraphrases import *
from scripts.definitions import *
from sklearn.model_selection import train_test_split
from scripts.config import  ENTITY_LIST,  SINGLE_VAL_ENTITIES
from templates import TEMPLATES_LIST, freib_template, muster_template
from collections import defaultdict

OUTPUT_NER_PATH = './data'
OUTPUT_REPORTS_PATH = './txt_reports'

ENTITY_RANDOM_VALUES = {                       
    "ADDRESS": 				hospital_addresses,	
    "ADDRESS_PATIENT":      get_fake_address(100),# patient_addresses,
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
    "DIAGNOSIS":           	list(format_diagnoses(diagnoses)),	
    "DISCHARGE_DATE":		generate_dates(),
    "DOCTOR":              	doctors,	
    "DURATION":            	durations,	
    "FAMILY_STATUS":       	family_status,	
    "FAMILYMEMBER":        	family_members,	
    "FAMHIST":             	family_history,	
    "FINDING":             	findings,	
    "FOLLOWUP_REASON":     	followup_reasons,	
    "FOLLOWUP_REQ":        	["CT-Thorax", "Blutbild", "EKG"],	
    "FREQUENCY":           	frequencies,	
    "GENDER":              	["männlich", "weiblich", "divers"],	
    "GEWICHT":             	generate_random_weights(),	
    "GROESSE":             	generate_random_heights(),	
    "HOSPITAL_STAY":		generate_random_hospital_stay(),		
    # "ICD10_CODE":          	list(diagnosis_icd10_map.keys()),	
    # "ICD10_DESC":          	list(diagnosis_icd10_map.values()),	
    "IMMUNIZATION":        	immunizations,	
    "IMPRESSION":          	impressions,	
    "INSURANCE_ID":        	generate_insurance_ids(),	
    "LAB_RESULT":          	lab_results,	
    "LIFESTYLE":           	lifestyles,	
    "MEDICATION":          	medications,	
    "OCCUPATION":          	occupations,	
    "ORG":                 	get_fake_hospitals(100),# hospital_names,	
    "PATIENT":              get_fake_names(100),#names	
    "PHONE":               	hospital_phones,
    "PATIENT_PHONE":        get_fake_phone(100),# patient_phones,	
    "PID":                 	generate_patient_ids(),	
    "PREV_DIAGNOSIS":      	list(format_prev_diagnoses(diagnoses)),	
    "PROCEDURE":           	procedures,	
    "RISKFACTOR":          	risk_factors,	
    "ROOM_NUMBER":         	generate_room_number(),	
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

def __create_sample_more_text(single_entity_values):
    sample = {}
    # more time Entities - random value list
    for ent in ENTITY_LIST:# the order must be realistic....
        if ent in ENTITY_RANDOM_VALUES:
            if ent in single_entity_values:
                sample[ent] = random.choice(ENTITY_RANDOM_VALUES[ent])
            else:
                sample[ent] = random.sample(ENTITY_RANDOM_VALUES[ent], 
                                       k=random.randint(1, min(3, len(ENTITY_RANDOM_VALUES[ent]))))
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
                
                matches = list(re.finditer(re.escape(term), text))
                
                for match in matches:
                    # Finde tatsächliche Position im Originaltext, die Normalisierung funktioniert nicht mit '\n'
                    span_start = match.start() 
                    if span_start == -1:
                        continue
                    span_end = match.end()
                    
                    if (span_start, span_end) not in used_spans:
                        ents.append({
                            "entity_group": label,
                            "word": val_str,
                            "start": span_start,
                            "end": span_end,
                            
                        })
                        used_spans.add((span_start, span_end))
                        found = True
                        break
                
                if found:
                    break 
    return ents

def __generate_paraphrase_more_text(values, single_val_entities):
    
    header_list = ['DOCUMENT_TYPE', 'ORG', 'ADDRESS', 'DEPARTMENT' ]#they stay always on top
    phrases_body = []
    phrases_header = []
    capitalize_next = False
    for ent,valu in values.items():
        if ent in single_val_entities: #just once
            paraphrase = paraphrase_entity(ent, values[ent])
            if capitalize_next:    
                paraphrase = paraphrase[0].upper() + paraphrase[1:]

            if ent in header_list:
                phrases_header.append(paraphrase)
            else:
                phrases_body.append(paraphrase)
            capitalize_next =  paraphrase.strip()[-1] in ['.','!','?']
        else:
            paraphrases =[]
            for val in valu: # more
                paraphrase = paraphrase_entity(ent, val)
                if capitalize_next:    
                    paraphrase = paraphrase[0].upper() + paraphrase[1:]
                paraphrases.append(paraphrase)
                
                capitalize_next =  paraphrase.strip()[-1] in ['.','!','?']

            paraphrase = random.choice(paraphrases)
            if ent in header_list:
                phrases_header.append(paraphrase)
            else:
                phrases_body.append(paraphrase)       
    
    random.shuffle(phrases_body)

    return "\n".join(phrases_header+phrases_body)

def __count_entity_placeholders(template):
   
    pattern = r"{(\w+)}"
    counts = defaultdict(int)
    for match in re.findall(pattern, template):
        counts[match] += 1
    return counts

def __generate_values(entity_values, single_val_entities, placeholder_counts):
    values_for_template = {}

    for entity, count in placeholder_counts.items():
        if entity not in entity_values:
            continue

        val_list = entity_values[entity]
        if isinstance(val_list, str):
            val_list = [val_list]

        if entity in single_val_entities:
            # Nur ein Wert benötigt → denselben zufälligen Wert mehrfach einsetzen
            value = random.choice(val_list)
            values_for_template[entity] = [value] * count
        else:
            # Mehrfach vorkommende Entitäten → zufällige Auswahl, ggf. mit Duplikaten
            sampled = random.choices(val_list, k=count)
            values_for_template[entity] = sampled
       

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
    from tqdm import tqdm
    dataset = []
    entities_list = []
    count_template = 0
    count_paraphrase = 0
    for i in tqdm(range(n_samples), desc="Generating syntetic data"):
        try:
            if random.random() < 0.5:     
                template = random.choice(TEMPLATES_LIST)
                placeholder_counts = __count_entity_placeholders(template)
                values_dict = __generate_values(ENTITY_RANDOM_VALUES, SINGLE_VAL_ENTITIES, placeholder_counts)
                text =  __fill_template(template, values_dict)
                entities = __extract_entities_generalized(text, values_dict)   
                count_template +=1
            else:
                values = __create_sample_more_text(SINGLE_VAL_ENTITIES)  
                text = __generate_paraphrase_more_text(values,SINGLE_VAL_ENTITIES)             
                entities = __extract_entities_generalized(text, values)  
                count_paraphrase += 1
            if save_reports:
                filename = f"report_{i+1:06}.txt"
                filepath = os.path.join(OUTPUT_REPORTS_PATH,filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(text)
                entities_list.append(entities)

            ner_data = generate_ner_data(text, entities)
            dataset.append( ner_data)
        except Exception as e:
            print(f"{e}" , {i})

    trains, validations = train_test_split(dataset, test_size=0.1, random_state=42)
    trains, tests = train_test_split(trains, test_size=0.1, random_state=42)
    
    print(f"💡 From template {count_template}, 🔁 from paraphrase {count_paraphrase}")


    os.makedirs(OUTPUT_NER_PATH, exist_ok=True)   
    
    with open(os.path.join(OUTPUT_NER_PATH,"train.json"), "w", encoding="utf-8") as f:
        json.dump(trains, f, indent=2, ensure_ascii=False)
    with open(os.path.join(OUTPUT_NER_PATH,"val.json"), "w", encoding="utf-8") as f:
        json.dump(validations, f, indent=2, ensure_ascii=False)
    with open(os.path.join(OUTPUT_NER_PATH,"test.json"), "w", encoding="utf-8") as f:
        json.dump(tests, f, indent=2, ensure_ascii=False)
    print(f"✅ Synthetic dataset generated in {OUTPUT_NER_PATH}")
    print(f"→ {len(trains)} trains, {len(validations)} validations), {len(tests)} tests)")
    if save_reports:
        os.makedirs(OUTPUT_REPORTS_PATH, exist_ok=True)   
        with open(os.path.join(OUTPUT_NER_PATH,"all_data.json"), "w", encoding="utf-8") as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        with open(os.path.join(OUTPUT_NER_PATH,"all_entities.json"), 'w',encoding="utf-8") as f:
            json.dump(entities_list, f,ensure_ascii=False, indent=4) 
        print(f"📊 saved also all data, all-ner, all-entities")
        print(f"📄 saved also the reports {OUTPUT_REPORTS_PATH} ({n_samples} samples)")


def __remove_existing_data():
    remove_folder(OUTPUT_NER_PATH)
    remove_folder(OUTPUT_REPORTS_PATH)
   
# Run as script
if __name__ == "__main__":
    n_samples = 10
    save_reports = True
    clean_data = False
    if len(sys.argv) > 1:
        n_samples = int(sys.argv[1])
    if len(sys.argv) > 2:
        save_reports = sys.argv[2].lower() == 'true'
    print(f"Starting generation of {n_samples} data!\n Saving reports is {save_reports}!\n !")
    __remove_existing_data()
    __generate_dataset(n_samples=n_samples, save_reports=save_reports)


