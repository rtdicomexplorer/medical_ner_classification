#infer_ner.py
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from ner_to_fhir import map_ner_to_fhir
import json
import os
from config import LABEL_LIST
from text_extractor import extract_text
from postprocess import postprocess_entities
from collections import defaultdict

MODEL_PATH = "./models/clinicalbert-ner"
from transformers import TokenClassificationPipeline
def deduplicate_entities(entities):
    seen = set()
    deduped = []
    for ent in entities:
        key = (ent["start"], ent["end"], ent["entity"])
        if key not in seen:
            deduped.append(ent)
            seen.add(key)
    return deduped

def __infer_text_chunked(nlp_pipeline: TokenClassificationPipeline, text: str, tokenizer, max_length: int = 512, stride: int = 128):
    inputs = tokenizer(
        text,
        return_overflowing_tokens=True,
        max_length=max_length,
        stride=stride,
        truncation=True,
        return_offsets_mapping=True,
        return_tensors="pt"
    )

    all_entities = []

    for i in range(len(inputs['input_ids'])):
        offset_mapping = inputs['offset_mapping'][i]
        chunk_start = offset_mapping[0][0]  # start of chunk in original text

        tokens = inputs['input_ids'][i]
        decoded_text = tokenizer.decode(tokens, skip_special_tokens=True)

        try:
            results = nlp_pipeline(decoded_text)
            for ent in results:
             adjusted_start = ent['start'] + chunk_start
            adjusted_end = ent['end'] + chunk_start
            all_entities.append({
            "entity": ent["entity_group"],
            "word": ent["word"],
            "score": ent["score"],
            "start": adjusted_start,
            "end": adjusted_end
            })
        except Exception as e:
            print(f"❌ Error processing chunk {i}: {e}")
            continue

    entities = deduplicate_entities(all_entities)
    return entities


def main(file_path):
    print(f"Extracting text from {file_path} ...")
    text = extract_text(file_path)
    print(f"Text extracted (first 500 chars):\n{text[:500]}")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForTokenClassification.from_pretrained(MODEL_PATH)
    nlp = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")

    

    entities = __infer_text_chunked(nlp, text, tokenizer, max_length=512, stride=128)

    print(entities)

    print("\nRecognized Entities:")
    for ent in entities:
        print(f"{ent['word']} [{ent['entity']}] ({ent['start']}:{ent['end']}) - confidence: {ent['score']:.3f}")

    clean_entities = postprocess_entities(entities, confidence_threshold=0.3)
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