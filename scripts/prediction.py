# prediction.py

import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from config import ID2LABEL
import argparse

MODEL_PATH = "./models/gbert-base"
def load_model(model_path: str):
    print(f"🔄 Lade Modell von: {model_path}")
    model = AutoModelForTokenClassification.from_pretrained(model_path)
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    return model, tokenizer

def predict_entities(text: str, model, tokenizer, aggregation_strategy="simple"):
    device = 0 if torch.cuda.is_available() else -1
    ner_pipeline = pipeline(
        "ner",
        model=model,
        tokenizer=tokenizer,
        aggregation_strategy=aggregation_strategy,  # "simple" = zusammengefasste Spans
        device=device
    )
    predictions = ner_pipeline(text)
    return predictions

def pretty_print(predictions, text):
    print("\n🧾 Erkannte Entitäten:\n")
    for pred in predictions:
        entity = pred['entity_group']
        word = pred['word']
        score = round(pred['score'], 3)
        print(f"{entity:25} | {word:40} | {score}")

def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--text", type=str, help="Zu analysierender medizinischer Text")
    # parser.add_argument("--model_path", type=str, default="./models/gbert-base", help="Pfad zum trainierten Modell")
    # args = parser.parse_args()

    # if not args.text:
    #     print("❌ Kein Text angegeben. Nutze --text \"Ihr Text hier\"")
    #     return

    model, tokenizer = load_model(MODEL_PATH)
    text_input = (f"Patientenname : Otto Kromberger \n"

    f"Geburtsdatum : 01.07.1950\n"

    f"Gewicht: 1,72 m\n"

    f"Große: 110Kg\n"

    f"Hausarzt : Dr. Suhle Nikolas.\n" 
    f"Der Patient erhält Ramipril 5mg gegen Hypertonie.\n")
    predictions = predict_entities(text_input, model, tokenizer)
    pretty_print(predictions, text_input)

if __name__ == "__main__":
    main()
