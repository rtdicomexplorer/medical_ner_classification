
from scripts.utils import family_members, occupations, family_status, prev_diagnoses, followup_reasons,impressions
import re
import spacy
from spacy.matcher import PhraseMatcher

nlp = spacy.load("de_core_news_md")

def extract_occupation(entity_text):
    doc = nlp(entity_text)
    for token in doc:
        if token.pos_ == "NOUN":
            lemma = token.lemma_.capitalize()
            if lemma in occupations:
                return lemma
    return entity_text


def __resolve_conflicts(entities):
    """
    If the same span has multiple labels, pick the highest priority one.
    """
    LABEL_PRIORITY = {
    "DIAGNOSIS": 1,
    "SYMPTOM": 2,
    "MEDICATION": 3,
    "TREATMENT": 4,
    "PROCEDURE": 5,
    "LIFESTYLE": 6,
    "FAMILY_HISTORY": 7,
    "PERSON": 8,
    "FAMILY_STATUS": 9,
    "RISKFACTOR": 10,
    "FOLLOWUP_RECOMMENDATION": 11,
    "VITALSIGNS": 12,
}

    grouped = {}
    for ent in entities:
        key = (ent["start"], ent["end"])
        if key not in grouped:
            grouped[key] = ent
        else:
            existing = grouped[key]
            existing_priority = LABEL_PRIORITY.get(existing["entity_group"], 100)
            new_priority = LABEL_PRIORITY.get(ent["entity_group"], 100)
            if new_priority < existing_priority:
                grouped[key] = ent  # replace with higher-priority entity

    return list(grouped.values())



def clean_medication(text):
    """
    Keep medication name and dose, remove trailing verbs or instructions.
    Example: "Diazepam 1g wurde verabreicht" -> "Diazepam 1g"
    """
    # Remove common trailing phrases
    text = re.sub(r'\b(wurde|wird|wird noch|soll|sollte|kann|konnte|erhielt|erhalten|verabreicht|gegeben|eingenommen)\b.*', '', text)
    return text.strip()

def clean_person_name(name):
    # Remove leading non-letter characters
    name = re.sub(r'^[^a-zA-ZäöüÄÖÜß]+', '', name.strip())
    return name

def clean_entity_text(entity_text, entity_type):
    # Remove common labels (e.g., "Name:", "Geburtsdatum:")
    entity_text = re.sub(r'^[A-Za-zäöüÄÖÜß\s]+:\s*', '', entity_text)

    # Clean up PERSON, DOCTOR, ORG by removing prepositions
    if entity_type in ["PERSON", "DOCTOR", "ORG"]:
        prepositions = ["im ", "auf ", "mit ", "zu ", "bei ", "von ", "am ", "untersucht von ", "untersucht "]
        lowered = entity_text.lower()
        for prefix in prepositions:
            if lowered.startswith(prefix):
                entity_text = entity_text[len(prefix):].strip()
                break

    if entity_type in ["PERSON", "DOCTOR"]:
        prefixes = ["herr", "frau"]
        lowered = entity_text.lower()
        for prefix in prefixes:
            if lowered.startswith(prefix):
                entity_text = clean_person_name (entity_text[len(prefix):])
                break

    # FAMILY_STATUS cleanup
    if entity_type == "FAMILY_STATUS":
        for prefix in ["bei sich hat ", "hat ", "ist ", "begleitet von"]:
            if entity_text.lower().startswith(prefix):
                entity_text = entity_text[len(prefix):].strip()
                break
    if entity_type == "MEDICATION":
        entity_text= clean_medication(entity_text)

    # ALLERGY: remove duplicates (e.g., "NüsseAllergien : Nüsse")
    if entity_type == "ALLERGY":
        parts = entity_text.split()
        half = len(parts) // 2
        if len(parts) > 1 and parts[:half] == parts[half:]:
            entity_text = " ".join(parts[:half])

    # DIAGNOSIS, RISKFACTOR, SYMPTOM: remove leading/trailing fillers
    if entity_type in ["DIAGNOSIS", "RISKFACTOR", "SYMPTOM"]:
        start_patterns = [
            r"^(es wurde|es sind|hat|hatte|zeigt sich|zeigt|liegt|liegen|besteht|bestehen|vorliegt|vorhanden|wurde|wird|wurde eine|wird eine)\s+",
            r"^(am|zum|zur|im|bei|mit|auf|in)\s+"
        ]
        for pattern in start_patterns:
            entity_text = re.sub(pattern, '', entity_text, flags=re.IGNORECASE).strip()

        # Remove trailing descriptive fillers
        end_patterns = [
            r"\s+(diagnostiziert|möglich|empfohlen|vorhanden|bestehend|gegeben|festgestellt)$"
        ]
        for pattern in end_patterns:
            entity_text = re.sub(pattern, '', entity_text, flags=re.IGNORECASE).strip()

    # DATE: Remove prefix phrases
    if entity_type == "DATE":
        entity_text = re.sub(r'^(am Untersuchungsdatum|am Datum|am|zum|bei)\s+', '', entity_text, flags=re.IGNORECASE).strip()

    # DEVICE: extract what's inside braces or remove filler
    if entity_type == "DEVICE":
        brace_match = re.search(r"\{(.*?)\}", entity_text)
        if brace_match:
            entity_text = brace_match.group(1).strip()
        else:
            # Fallback if no braces
            entity_text = re.sub(r"^(es wird|es wurde|wird)?\s*empfohlen\s*", '', entity_text, flags=re.IGNORECASE)
            entity_text = re.sub(r"zu verwenden$", '', entity_text, flags=re.IGNORECASE).strip()

    if entity_type == "OCCUPATION":
        entity_text = extract_occupation(entity_text)


    return entity_text

#################SPACY
def create_matcher(label, phrase_list):
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = [nlp.make_doc(p) for p in phrase_list]
    matcher.add(label, patterns)
    return matcher

matcher_list ={
"FOLLOWUP_REASON" : create_matcher("FOLLOWUP_REASON", followup_reasons),
"IMPRESSION" : create_matcher("IMPRESSION", impressions),
"PREV_DIAGNOSIS" : create_matcher("PREV_DIAGNOSIS", prev_diagnoses),
"FAMILYMEMBER" :create_matcher("FAMILYMEMBER", family_members),
"FAMILY_STATUS" : create_matcher("FAMILY_STATUS", family_status)
}

def extract_name_spacy(text):
    doc = nlp(text)
    # Alle Entitäten der Klasse PERSON extrahieren
    persons = [ent.text for ent in doc.ents if ent.label_ == "PER" or ent.label_ == "PERSON"]
    if persons:
        # Nimm die längste Person-Entität (falls mehrere)
        return max(persons, key=len).strip()
    else:
        # Fallback: alle PROPN (Eigennamen) und NOUN in Folge zusammenfügen
        tokens = [token.text for token in doc if token.pos_ in {"PROPN", "NOUN"}]
        return " ".join(tokens).strip()
    

def normalize_dates(text):
    # Replace 'dd. mm. yyyy' or 'dd. mm.yyyy' with 'dd.mm.yyyy'
    normalized_text = re.sub(r"(\d{2})\.\s*(\d{2})\.\s*(\d{4})", r"\1.\2.\3", text)
    return normalized_text

def extract_date_spacy(text):
    normalized_text = normalize_dates(text)
    doc = nlp(normalized_text)

    spacy_dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
    if spacy_dates:
        return max(spacy_dates, key=len).strip()

    # fallback regex for dd.mm.yyyy
    match = re.search(r"\b\d{2}\.\d{2}\.\d{4}\b", normalized_text)
    if match:
        return match.group(0)
    return None
    
    # Kein Datum gefunden
    return None
def extract_phrases(text, matcher):
    doc = nlp(text)
    result =  [doc[start:end].text for _, start, end in matcher(doc)]
    return " ".join(result)

def clean_medical_text_spacy(entity_text):
    start_stopphrases = [
        r"es wurde", r"es sind", r"hat", r"hatte", r"zeigt sich", r"zeigt", r"liegt", r"liegen",
        r"besteht", r"bestehen", r"vorliegt", r"vorhanden", r"wurde", r"wird", r"wurde eine", r"wird eine",
        r"am", r"zum", r"zur", r"im", r"bei", r"mit", r"auf", r"in"
    ]
    
    # Kombiniere Phrasen zu einem Regex Pattern, ^ = Anfang des Strings
    pattern = r"^(?:" + "|".join(start_stopphrases) + r")\s+"
    
    # Entferne die Startphrase am Anfang, wenn vorhanden (case-insensitive)
    entity_text = re.sub(pattern, "", entity_text, flags=re.IGNORECASE).strip()
    
    # Entferne trailing Wörter
    entity_text = re.sub(r'\s+(diagnostiziert|möglich|empfohlen|vorhanden|bestehend|gegeben|festgestellt)$', '', entity_text, flags=re.IGNORECASE).strip()
    
    # Lemmatisieren: nur NOUN, ADJ, PROPN behalten
    doc = nlp(entity_text)
    lemmas = [token.lemma_ for token in doc if token.pos_ in {"NOUN", "ADJ", "PROPN"}]
    
    # Falls nichts übrig bleibt, gebe den Originaltext zurück (Fallback)
    cleaned = " ".join(lemmas)
    return cleaned if cleaned else entity_text
def extract_occupation_spacy(entity_text):
    doc = nlp(entity_text)
    for token in doc:
        if token.pos_ == "NOUN" or token.pos_ == "PROPN":
            lemma = token.lemma_.capitalize()
            if lemma in occupations:
                return lemma
    return entity_text

def clean_entity_text_spacy(entity_text, entity_type):
    # 1. Allgemeines Trimmen & Label-Entfernung (z.B. "Name:", "Geburtsdatum:")
    entity_text = entity_text.strip()
    entity_text = re.sub(r'^[A-Za-zäöüÄÖÜß\s]+:\s*', '', entity_text)

    if entity_type in ["PERSON", "DOCTOR", "ORG"]:
        entity_text = extract_name_spacy(entity_text)
  
    elif entity_type == "OCCUPATION":
        entity_text = extract_occupation_spacy(entity_text)
    elif "DATE" in entity_type:
        entity_text =extract_date_spacy( entity_text)

    elif entity_type in ["FAMILY_STATUS","FAMILYMEMBER"]:
        entity_text = extract_phrases(entity_text, matcher_list[entity_type])


    elif entity_type == "MEDICATION":
        # Regex Cleanup für Verben entfernen
        entity_text = re.sub(r'\b(wurde|wird|wird noch|soll|sollte|kann|konnte|erhielt|erhalten|verabreicht|gegeben|eingenommen)\b.*', '', entity_text)
        entity_text = entity_text.strip()


    elif entity_type in ["DIAGNOSIS", "RISKFACTOR","SYMPTOM"]:
        entity_text = clean_medical_text_spacy(entity_text) 

    elif entity_type == "DEVICE":
        brace_match = re.search(r"\{(.*?)\}", entity_text)
        if brace_match:
            entity_text = brace_match.group(1).strip()
        else:
            entity_text = re.sub(r"^(es wird|es wurde|wird)?\s*empfohlen\s*", '', entity_text, flags=re.IGNORECASE)
            entity_text = re.sub(r"zu verwenden$", '', entity_text, flags=re.IGNORECASE).strip()

    # Optional: Immer erst Recht nochmal trimmen
    entity_text = entity_text.strip()

    return entity_text


##############END SPACY



def normalize_text(text):
    # Lowercase and remove extra colons/spaces
    text = text.lower().replace(":", "").strip()
    
    # Fix decimal numbers with space after dot, e.g., "97. 8" -> "97.8"
    text = re.sub(r'(\d)\.\s+(\d)', r'\1.\2', text)
    
    # Ensure space between number and unit (e.g., "97.8kg" -> "97.8 kg")
    text = re.sub(r'(\d)([a-zA-Z]+)', r'\1 \2', text)
    
    # Clean extra spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def postprocess_entities(entities):
    merged = []
    buffer = None

    LABEL_THRESHOLDS = {
        "PERSON": 0.15,
        "PID": 0.15,
        "DOCTOR": 0.15,
        "SYMPTOM": 0.3,
        "MEDICATION": 0.3,
        "DIAGNOSIS": 0.3,
        "RISKFACTOR": 0.25,
        "DEFAULT": 0.2
    }

    def get_threshold(label):
        return LABEL_THRESHOLDS.get(label, LABEL_THRESHOLDS["DEFAULT"])

    def should_merge(e1, e2):
        gap = e2["start"] - e1["end"]
        same_label = e1["entity_group"] == e2["entity_group"]
        
        # Prüfen, ob e2 ein Subwort ist (mit "##" Tokenisierung)
        is_subword = e2["word"].startswith("##")
        
        # Nur Subwörter direkt anfügen oder Wörter, die direkt angrenzen (gap=0)
        return same_label and (gap == 0 or is_subword)

    # Step 1: Filter + Merge subwords
    for ent in entities:
        entity_type = ent.get("entity_group", ent.get("entity"))
        if ent["score"] < get_threshold(entity_type):
            continue

        ent_clean = {
            "entity_group": entity_type,
            "word": ent["word"].lstrip("##"),
            "score": float(ent["score"]),
            "start": ent["start"],
            "end": ent["end"],
        }

        if buffer is None:
            buffer = ent_clean
        elif should_merge(buffer, ent_clean):
            buffer["word"] += ent_clean["word"]
            buffer["end"] = ent_clean["end"]
            buffer["score"] = max(buffer["score"], ent_clean["score"])
        else:
            merged.append(buffer)
            buffer = ent_clean

    if buffer:
        merged.append(buffer)

    # Step 2: Merge multi-token entities for selected labels
    MULTI_TOKEN_LABELS = {"PERSON", "MEDICATION", "DIAGNOSIS", "OCCUPATION", "FAMILYMEMBER", "BIRTHDATE", "DATE", "ORG", "ADDRESS"}

    final = []
    buffer = None
    for ent in merged:
        if buffer is None:
            buffer = ent
            continue

        same_label_and_multi_token = (
            buffer["entity_group"] == ent["entity_group"] 
            and buffer["entity_group"] in MULTI_TOKEN_LABELS
            and 0 <= ent["start"] - buffer["end"] <= 2
        )

        if same_label_and_multi_token:
            separator = " "
            if "DATE" in ent["entity_group"] :
                separator = "."
            buffer["word"] += separator + ent["word"]
            buffer["end"] = ent["end"]
            buffer["score"] = max(buffer["score"], ent["score"])
        else:
            final.append(buffer)
            buffer = ent
        if "DATE" in ent["entity_group"] or "GEWICHT" in ent["entity_group"]:
            buffer['word'] = normalize_text(buffer['word'])

    if buffer:
        final.append(buffer)

    # Step 3: De-duplicate by content
    unique = []
    seen = set()
    for ent in final:
        key = (ent["word"].lower(), ent["entity_group"], ent["start"], ent["end"])
        if key not in seen:
            seen.add(key)
            unique.append(ent)

    # Step 4: Heuristic Cleanup for FHIR usability
    clean = []
    for ent in unique:
        word = ent["word"].strip()
        group = ent["entity_group"]

        # Drop junk
        if word in [",", ".", "und", "oder","im", "zu", "auf", "bei", "mit"]:
            continue

        # Remove short PERSON or FAMILY_STATUS
        if group in ["PERSON", "FAMILY_STATUS"] and len(word) < 3:
            continue

        # Filter known misclassifications
        if group == "PERSON" and word.lower() in ["arm", "bein", "auge", "ehefrau", "kinder"]:
            continue


        # Normalize or add context hints
        if word.lower() == "schlafmedikamente":
            ent["context_hint"] = "medication_or_symptom"
        if "rauch" in word.lower():
            ent["context_hint"] = "lifestyle_smoking"


        ent["word"] = clean_entity_text_spacy(word, group)

        clean.append(ent)

    return __resolve_conflicts(clean)
