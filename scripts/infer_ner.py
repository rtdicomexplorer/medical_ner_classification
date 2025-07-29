import os
import json
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline, TokenClassificationPipeline
from collections import defaultdict
from text_extractor import extract_text   # Your custom text extractor
from postprocess import postprocess_entities  # Your custom postprocessing
from ner_to_fhir import map_ner_to_fhir    # Your mapping from NER to FHIR

MODEL_PATH = "./models/gbert-base"

def deduplicate_entities(entities):
    seen = set()
    deduped = []
    for ent in entities:
        key = (ent["start"], ent["end"], ent["entity"])
        if key not in seen:
            deduped.append(ent)
            seen.add(key)
    return deduped

import math

def infer_text_chunked_safe(nlp_pipeline: TokenClassificationPipeline, text: str, tokenizer, max_length: int = 512, stride: int = 128):
    tokens = tokenizer(text, return_offsets_mapping=True)
    offset_mapping = tokens["offset_mapping"]

    # Total number of tokens
    total_tokens = len(offset_mapping)
    step = max_length - stride
    all_entities = []

    for i in range(0, total_tokens, step):
        end = min(i + max_length, total_tokens)

        # Get char-level start/end
        chunk_start_char = offset_mapping[i][0]
        chunk_end_char = offset_mapping[end - 1][1]
        text_chunk = text[chunk_start_char:chunk_end_char]

        try:
            results = nlp_pipeline(text_chunk)
            for ent in results:
                adjusted_start = ent["start"] + chunk_start_char
                adjusted_end = ent["end"] + chunk_start_char
                all_entities.append({
                    "entity": ent["entity_group"],
                    "word": ent["word"],
                    "score": ent["score"],
                    "start": adjusted_start,
                    "end": adjusted_end
                })
        except Exception as e:
            print(f"❌ Error in chunk [{i}:{end}]: {e}")

    return deduplicate_entities(all_entities)

def main(file_path):
    print(f"Extracting text from {file_path} ...")
    text = extract_text(file_path)
    print(f"Text extracted (first 500 chars):\n{text[:500]}")
    # text = "Patient Otto Kromberger leidet an Kopfschmerzen."
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForTokenClassification.from_pretrained(MODEL_PATH)
    nlp = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")
    entities = nlp(text)

    entities = [
        {
            "entity": ent["entity_group"],
            "word": ent["word"],
            "score": ent["score"],
            "start": ent["start"],
            "end": ent["end"]
        }
        for ent in nlp(text)
    ]


    print("Raw entities:", entities)
    # entities = infer_text_chunked(nlp, text, tokenizer, max_length=512, stride=128)

    # print("\nRecognized Entities:")
    # for ent in entities:
    #     print(f"{ent['word']} [{ent['entity']}] ({ent['start']}:{ent['end']}) - confidence: {ent['score']:.3f}")

    clean_entities = postprocess_entities(entities, confidence_threshold=0.1)
    fhir_output = map_ner_to_fhir(clean_entities)

    output_json = "fhir_output.json"
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(fhir_output, f, indent=2, ensure_ascii=False)

    print(f"\nFHIR resources saved to {output_json}")

if __name__ == "__main__":
    # import sys
    # if len(sys.argv) != 2:
    #     print("Usage: python infer_ner.py <path_to_file>")
    #     exit(1)
    # file_path = sys.argv[1]
    # if not os.path.exists(file_path):
    #     print(f"File not found: {file_path}")
    #     exit(1)
    file_path = './documents/artz_brief.txt'
    main(file_path)
