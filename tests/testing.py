
from transformers import AutoTokenizer

LABEL_LIST = [
    "O",
    "B-PERSON", "I-PERSON",
    "B-DOCTOR", "I-DOCTOR",
    "B-ORG", "I-ORG",
    "B-DATE", "I-DATE",
    "B-DIAGNOSIS", "I-DIAGNOSIS",
    "B-SYMPTOM", "I-SYMPTOM",
    "B-MEDICATION", "I-MEDICATION",
    "B-PROCEDURE", "I-PROCEDURE",
    "B-TREATMENT", "I-TREATMENT",
    "B-DEPARTMENT", "I-DEPARTMENT",
    "B-LAB_RESULT", "I-LAB_RESULT",
    "B-ALLERGY", "I-ALLERGY",
    "B-IMMUNIZATION", "I-IMMUNIZATION",
    "B-DEVICE", "I-DEVICE",
    "B-FAMILY_HISTORY", "I-FAMILY_HISTORY",
    "B-ADDRESS", "I-ADDRESS",
    "B-PHONE", "I-PHONE",
    "B-IMPRESSION", "I-IMPRESSION",
    "B-FINDING", "I-FINDING",
    "B-FOLLOWUP_REASON", "I-FOLLOWUP_REASON",
    "B-PREV_DIAGNOSIS", "I-PREV_DIAGNOSIS",
    "B-GENDER", "I-GENDER",
    "B-BIRTHDATE", "I-BIRTHDATE",
    "B-FAMILY_STATUS", "I-FAMILY_STATUS",
    "B-FOLLOWUP_RECOMMENDATION", "I-FOLLOWUP_RECOMMENDATION",
    "B-VITALSIGNS", "I-VITALSIGNS",
    "B-LIFESTYLE", "I-LIFESTYLE",
    "B-RISKFACTOR", "I-RISKFACTOR",
    "B-ICD10_CODE", "I-ICD10_CODE",
    "B-ICD10_DESC", "I-ICD10_DESC",
    "B-OCCUPATION", "I-OCCUPATION",
    "B-FAMILYMEMBER", "I-FAMILYMEMBER"
]

LABEL2ID = {label: idx for idx, label in enumerate(LABEL_LIST)}
ID2LABEL = {idx: label for label, idx in LABEL2ID.items()}


def tokenize_and_align_labels(tokenizer, words, word_labels):
    """
    Args:
        tokenizer: ein HuggingFace Tokenizer (z.B. AutoTokenizer)
        words: z.B. ["Herr", "Kromberger", "hat", "Kopfschmerzen"]
        word_labels: z.B. ["O", "B-PERSON", "O", "B-SYMPTOM"]
    
    Returns:
        dict mit tokenisierten Inputs + aligned Labels als IDs
    """
    tokenized_inputs = tokenizer(words, is_split_into_words=True, truncation=True, return_offsets_mapping=True, return_tensors="pt")
    
    labels = []
    word_ids = tokenized_inputs.word_ids(batch_index=0)

    previous_word_idx = None
    for word_idx in word_ids:
        if word_idx is None:
            labels.append(-100)  # ignorieren (CLS, SEP, etc.)
        elif word_idx != previous_word_idx:
            labels.append(LABEL2ID.get(word_labels[word_idx], 0))  # B- oder O
        else:
            current_label = word_labels[word_idx]
            if current_label.startswith("B-"):
                inside_label = "I-" + current_label[2:]
            else:
                inside_label = current_label
            labels.append(LABEL2ID.get(inside_label, 0))
        previous_word_idx = word_idx

    tokenized_inputs["labels"] = labels
    return tokenized_inputs


def __align_labels_with_subtokens(words, labels, tokenizer):
    """
    words: Liste von Original-Wörtern, z.B. ["Herr", "Kromberger", "hat", "Kopfschmerzen"]
    labels: Liste von Labels pro Wort, z.B. ["O", "B-PERSON", "O", "B-SYMPTOM"]
    tokenizer: Ein Huggingface Tokenizer mit Subword-Tokenisierung
    
    Rückgabe:
    tokenized_input: Token-IDs
    aligned_labels: Labels passend zu jedem Subtoken
    """
    tokenized_input = []
    aligned_labels = []

    for word, label in zip(words, labels):
        # Tokenize das Wort in Subtokens
        subtokens = tokenizer.tokenize(word)
        
        # Falls Label O ist: alle Subtokens O
        if label == "O":
            aligned_labels.extend(["O"] * len(subtokens))
        else:
            # Erster Subtoken bekommt das B-Label (oder wie das Originallabel heißt)
            # Alle weiteren Subtokens bekommen I-Label (ersetze B- durch I- falls nötig)
            aligned_labels.append(label)
            if label.startswith("B-"):
                i_label = "I-" + label[2:]
            else:
                i_label = label  # falls es schon I-Label ist oder sonst was
            
            aligned_labels.extend([i_label] * (len(subtokens) - 1))
        
        # Speichere die Token
        tokenized_input.extend(subtokens)
    
    return tokenized_input, aligned_labels


tokenizer = AutoTokenizer.from_pretrained("bert-base-german-cased")

words = ["Herr", "Kromberger", "hat", "Kopfschmerzen", "."]
word_labels = ["PREFIX", "B-PERSON", "VERB", "B-SYMPTOM", "POINT"]

result = tokenize_and_align_labels(tokenizer, words, word_labels)
print("Input IDs:", result["input_ids"])
print("Tokens:", tokenizer.convert_ids_to_tokens(result["input_ids"][0]))
print("Labels:", result["labels"])
print("Labels (Text):", [ID2LABEL[label] if label != -100 else "IGN" for label in result["labels"]])

# Tokenisierung mit Rückgabe der Wort-IDs
tokenized = tokenizer(words, is_split_into_words=True, return_offsets_mapping=True, return_tensors="pt")
# Word-IDs: zeigt für jeden Subtoken zu welchem Wort er gehört
word_ids = tokenized.word_ids()


aligned_labels = []
previous_word_id = None

for idx, word_id in enumerate(word_ids):
    if word_id is None:
        aligned_labels.append("O")  # z. B. für [CLS], [SEP]
    elif word_id != previous_word_id:
        aligned_labels.append(LABEL_LIST[word_id])  # erstes Subtoken
    else:
        label = LABEL_LIST[word_id]
        # Konvertiere B- zu I-
        if label.startswith("B-"):
            label = "I-" + label[2:]
        aligned_labels.append(label)
    previous_word_id = word_id

tokens = tokenizer.convert_ids_to_tokens(tokenized["input_ids"][0])
for token, label in zip(tokens, aligned_labels):
    print(f"{token:15} → {label}")



# tokens = []
# labels = []

# for word, label in zip(words, word_labels):
#     word_tokens = tokenizer.tokenize(word)
#     tokens.extend(word_tokens)
    
#     # Erstes Subtoken bekommt das Originallabel
#     labels.append(label)
#     # Für alle weiteren Subtokens das I-Label oder O, je nachdem
#     if label.startswith("B-"):
#         i_label = "I-" + label[2:]
#     else:
#         i_label = label
    
#     labels.extend([i_label] * (len(word_tokens) - 1))

# print("Tokens:", tokens)
# print("Labels:", labels)


# tokens, aligned_labels = align_labels_with_subtokens(words, word_labels, tokenizer)


# print("aligned :\n")
# print("Tokens:", tokens)
# print("Labels:", aligned_labels)