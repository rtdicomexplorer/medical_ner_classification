
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


import re

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
    
    # Check if first character is a letter
    return name and name[0].isalpha()
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

    return entity_text

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


        ent["word"] = clean_entity_text(word, group)

        clean.append(ent)

    return __resolve_conflicts(clean)
