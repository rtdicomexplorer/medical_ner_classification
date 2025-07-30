def postprocess_entities(entities, confidence_threshold=0.1):
    merged = []
    buffer = None

    for ent in entities:
        # Skip low-confidence predictions
        if ent['score'] < confidence_threshold:
            continue

        # Normalize keys
        entity = {
            'entity_group': ent['entity_group'],
            'word': ent['word'],
            'score': float(ent['score']),
            'start': ent['start'],
            'end': ent['end'],
        }

        # Start or merge
        if buffer is None:
            buffer = entity
        elif (
            entity['entity_group'] == buffer['entity_group']
            and entity['start'] == buffer['end']
        ):
            # Merge with buffer
            buffer['word'] += entity['word'].lstrip('##')  # strip subword prefix
            buffer['end'] = entity['end']
            buffer['score'] = max(buffer['score'], entity['score'])  # or average
        else:
            merged.append(buffer)
            buffer = entity

    if buffer:
        merged.append(buffer)

    return merged
