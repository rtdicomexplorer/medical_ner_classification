#infer_ner.py
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from ner_to_fhir import map_ner_to_fhir
import json
import os
from config import LABEL_LIST
from text_extractor import extract_text
from postprocess import postprocess_entities

MODEL_PATH = "./models/clinicalbert-ner"

def __infer_text_chunked(nlp_pipeline, text, max_chunk_length=450):
    """
    Runs NER pipeline on text split into smaller chunks.
    Ensures chunks stay under 512 token limit.
    """
    import textwrap

    chunks = textwrap.wrap(text, width=max_chunk_length)
    all_entities = []

    for chunk in chunks:
        try:
            results = nlp_pipeline(chunk)
            for ent in results:
                all_entities.append({
                    "entity": ent["entity_group"],
                    "word": ent["word"],
                    "score": ent["score"],
                    "start": ent["start"],
                    "end": ent["end"]
                })
        except Exception as e:
            print(f"Error processing chunk: {e}")
            continue

    return all_entities

def main(file_path):
    print(f"Extracting text from {file_path} ...")
    text = extract_text(file_path)
    print(f"Text extracted (first 500 chars):\n{text[:500]}")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForTokenClassification.from_pretrained(MODEL_PATH)
    nlp = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")

    entities = __infer_text_chunked(nlp, text)

    print("\nRecognized Entities:")
    for ent in entities:
        print(f"{ent['word']} [{ent['entity']}] ({ent['start']}:{ent['end']}) - confidence: {ent['score']:.3f}")

    clean_entities = postprocess_entities(entities, confidence_threshold=0.6)
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
    file_path = "./documents/artz_brief.txt"
    if os.path.exists(file_path):
        main(file_path)