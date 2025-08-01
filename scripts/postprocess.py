
def resolve_conflicts(entities):
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
        key = (ent["word"].lower(), ent["start"], ent["end"])
        if key not in grouped:
            grouped[key] = ent
        else:
            existing = grouped[key]
            existing_priority = LABEL_PRIORITY.get(existing["entity_group"], 100)
            new_priority = LABEL_PRIORITY.get(ent["entity_group"], 100)
            if new_priority < existing_priority:
                grouped[key] = ent  # replace with higher-priority entity

    return list(grouped.values())


def postprocess_entities(entities):
    merged = []
    buffer = None

    LABEL_THRESHOLDS = {
        "PERSON": 0.15,
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
        continuation = e2["word"][0].isupper()
        return same_label and (0 <= gap <= 1 or continuation)

    # Step 1: Filter + Merge subwords
    for ent in entities:
        if ent["score"] < get_threshold():
            continue

        ent_clean = {
            "entity_group": ent["entity_group"],
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

    # Step 2: Merge multi-token PERSON names (e.g. "Otto Kromberger")
    final = []
    buffer = None
    for ent in merged:
        if buffer is None:
            buffer = ent
            continue

        same_person = (
            buffer["entity_group"] == ent["entity_group"] == "PERSON"
            and 0 <= ent["start"] - buffer["end"] <= 2
        )

        if same_person:
            buffer["word"] += " " + ent["word"]
            buffer["end"] = ent["end"]
            buffer["score"] = max(buffer["score"], ent["score"])
        else:
            final.append(buffer)
            buffer = ent

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
        if word in [",", ".", "und", "oder"]:
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

        clean.append(ent)

    return resolve_conflicts(clean)
    return clean
