import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from ner_to_fhir import map_ner_to_fhir
import json

MODEL_PATH = "./models/clinicalbert-ner"

# Your extended label list, must match training labels order!
LABEL_LIST = [
    "O",
    "B-PERSON", "I-PERSON",
    "B-DOCTOR", "I-DOCTOR",
    "B-ORG", "I-ORG",
    "B-DEPARTMENT", "I-DEPARTMENT",
    "B-DATE", "I-DATE",
    "B-DIAGNOSIS", "I-DIAGNOSIS",
    "B-PROCEDURE", "I-PROCEDURE",
    "B-MEDICATION", "I-MEDICATION",
    "B-TREATMENT", "I-TREATMENT",
    "B-LAB_RESULT", "I-LAB_RESULT",
    "B-ALLERGY", "I-ALLERGY",
    "B-IMMUNIZATION", "I-IMMUNIZATION",
    "B-DEVICE", "I-DEVICE",
    "B-FAMILY_HISTORY", "I-FAMILY_HISTORY",
]

def load_model():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForTokenClassification.from_pretrained(MODEL_PATH)
    nlp = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")
    return nlp

def infer_text(nlp, text):
    results = nlp(text)
    # results is a list of dicts with keys: entity_group, score, word, start, end
    entities = []
    for ent in results:
        entities.append({
            "entity": ent["entity_group"],
            "word": ent["word"],
            "score": ent["score"],
            "start": ent["start"],
            "end": ent["end"]
        })
    return entities

if __name__ == "__main__":
    nlp = load_model()

    sample_text = (
        "Am 10. März 2023 stellte sich Patient Max Müller mit Asthma vor. "
        "Der Arzt war Dr. Becker im Kardiologie der St. Marien Krankenhaus. "
        "Das Verfahren war Angioplastie. Der Patient wurde mit Albuterol behandelt."
    )

    entities = infer_text(nlp, sample_text)
    for ent in entities:
        print(f"{ent['word']} [{ent['entity']}] ({ent['start']}:{ent['end']}) - confidence: {ent['score']:.3f}")
#     [
#   {'word': 'Max Müller', 'entity': 'PERSON', 'start': 31, 'end': 42},
#   {'word': 'Asthma', 'entity': 'DIAGNOSIS', 'start': 48, 'end': 54},
#   {'word': 'Dr. Becker', 'entity': 'DOCTOR', ...},
#   {'word': 'Albuterol', 'entity': 'MEDICATION', ...},
#   ...
# ]

#Map those entities to FHIR resources

    fhir_output = map_ner_to_fhir(entities)

    # Step 3: Save as JSON
    with open("fhir_output.json", "w", encoding="utf-8") as f:
        json.dump(fhir_output, f, indent=2, ensure_ascii=False)

    print("FHIR resources saved to fhir_output.json")

