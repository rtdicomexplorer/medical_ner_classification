def postprocess_entities(entities, confidence_threshold=0.6):
    """
    Filters and merges NER entities:
    - Removes entities below confidence threshold
    - Merges overlapping or adjacent entities with the same label
    """
    # Step 1: Filter by confidence
    filtered = [e for e in entities if e['score'] >= confidence_threshold]

    # Step 2: Sort by start index
    filtered.sort(key=lambda x: x['start'])

    merged = []
    for ent in filtered:
        if not merged:
            merged.append(ent)
            continue

        last = merged[-1]

        # Check if same label and overlapping or adjacent
        if ent['entity'] == last['entity'] and ent['start'] <= last['end'] + 1:
            merged[-1] = {
                'entity': last['entity'],
                'start': min(last['start'], ent['start']),
                'end': max(last['end'], ent['end']),
                'word': (last['word'].strip() + " " + ent['word'].strip()).strip(),
                'score': (last['score'] + ent['score']) / 2,
            }
        else:
            merged.append(ent)

    return merged
