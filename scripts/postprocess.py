def postprocess_entities(entities, confidence_threshold=0.6):
    """
    Filters and merges NER entities:
    - Removes entities below confidence threshold
    - Merges overlapping or adjacent entities with the same label
    """
    filtered = [e for e in entities if e['score'] >= confidence_threshold]
    filtered.sort(key=lambda x: x['start'])

    merged = []
    for ent in filtered:
        if not merged:
            merged.append(ent)
            continue

        last = merged[-1]

        # Same label & overlapping/adjacent
        if ent['entity'] == last['entity'] and ent['start'] <= last['end'] + 1:
            # Join words with space if needed
            joined_word = last['word'].rstrip() + (" " if not last['word'].endswith(" ") and not ent['word'].startswith(" ") else "") + ent['word'].lstrip()
            merged[-1] = {
                'entity': last['entity'],
                'start': min(last['start'], ent['start']),
                'end': max(last['end'], ent['end']),
                'word': joined_word,
                'score': (last['score'] + ent['score']) / 2,
            }
        else:
            merged.append(ent)

    return merged
