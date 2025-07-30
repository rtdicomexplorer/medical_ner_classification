import os
import json
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from text_extractor import extract_text   # Your custom text extractor
from postprocess import postprocess_entities  # Your custom postprocessing
from ner_to_fhir import map_ner_to_fhir    # Your mapping from NER to FHIR

MODEL_PATH = "./models/gbert-base"
OUTPUTDIR = "output"


def main(file_path):
    print(f"Extracting text from {file_path} ...")
    text = extract_text(file_path)
    print(f"Text extracted (first 500 chars):\n{text[:500]}")
    print(f"\n=============================================\n")
    # text = "Patient Otto Kromberger leidet an Kopfschmerzen."
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForTokenClassification.from_pretrained(MODEL_PATH)
    nlp = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")

    entities = nlp(text)
    for ent in entities:
        print(ent)
    clean_entities = postprocess_entities(entities, confidence_threshold=0.1)
    fhir_output = map_ner_to_fhir(clean_entities)

    output_json = os.path.join(OUTPUTDIR, "fhir_output.json")
    if os.path.exists(output_json):
        os.remove(output_json)
    os.makedirs(OUTPUTDIR, exist_ok=True)
    
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(fhir_output, f, indent=2, ensure_ascii=False)

    print(f"\nFHIR resources saved to {output_json}")

if __name__ == "__main__":
    import sys
    file_path = './documents/artz_brief.txt'
    if len(sys.argv) == 2:
        print("Usage: python infer_ner.py <path_to_file>")
    
        file_path = sys.argv[1]
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            exit(1)
    
    main(file_path)
