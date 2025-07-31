def postprocess_entities(entities, confidence_threshold=0.2):
    merged = []
    buffer = None

    def should_merge(e1, e2):
        return (
            e1["entity_group"] == e2["entity_group"]
            and e1["end"] == e2["start"]
        )

    # Step 1: Filter + Merge subwords
    for ent in entities:
        if ent["score"] < confidence_threshold:
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

    # Step 2: De-duplicate by word and span
    unique = []
    seen = set()
    for ent in merged:
        key = (ent["word"].lower(), ent["entity_group"], ent["start"], ent["end"])
        if key not in seen:
            seen.add(key)
            unique.append(ent)

    # Step 3: Heuristic Cleanup for FHIR usability
    clean = []
    for ent in unique:
        word = ent["word"].strip()
        group = ent["entity_group"]

        # Drop junk
        if word in [",", ".", "und", "oder"]:
            continue

        # Remove too generic or noisy terms
        if group in ["PERSON", "FAMILY_STATUS"] and len(word) < 3:
            continue

        # Remove single-word body parts misclassified as PERSON
        if group == "PERSON" and word.lower() in ["arm", "bein", "auge", "ehefrau", "kinder"]:
            continue

        # Normalize and annotate ambiguous tokens
        if word.lower() == "schlafmedikamente":
            ent["context_hint"] = "medication_or_symptom"
        if "rauch" in word.lower():
            ent["context_hint"] = "lifestyle_smoking"

        clean.append(ent)

    return clean
