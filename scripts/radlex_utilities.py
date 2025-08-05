#Generate BIO-Formatted NER Dataset from Raw Reports
import pandas as pd
import re
from pathlib import Path
from transformers import AutoTokenizer
from collections import defaultdict

# === SETTINGS ===
REPORTS_CSV = "./documents/ReportsDATASET.csv"  # Raw reports CSV
RADLEX_CSV = "./documents/core-playbook-dev.csv"  # Vocabulary for pattern-based NER
OUTPUT_FILE = "ner_dataset.txt"  # BIO-formatted output
MODEL_NAME = "./models/gbert-base"  # or any BERT tokenizer


# Load the file and print lines to understand the separator
def extract_reports_from_raw_file(file_path):
    reports = []
    current_report = []

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            # Strip leading/trailing whitespace
            line = line.strip()

            # Skip empty lines
            if line == "":
                continue

            # If line is only a double quote and we have a report, it’s a separator
            if line == '"' and current_report:
                full_report = " ".join(current_report).strip()
                reports.append(full_report)
                current_report = []
            elif line != '"':
                current_report.append(line)

    # Catch any final report not ended with a quote
    if current_report:
        full_report = " ".join(current_report).strip()
        reports.append(full_report)

    return reports



def save_reports_to_individual_files(reports, output_dir):
    import os
    # Create the directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    for idx, report in enumerate(reports, start=1):
        # Clean up the report (optional)
        clean = report.strip()

        # Define the filename
        filename = f"report_{idx:04d}.txt"  # e.g., report_0001.txt

        # Full path
        file_path = os.path.join(output_dir, filename)

        # Write to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(clean)



def basic_cleanup(reports):
    cleaned = []
    for report in reports:

        text = report.replace('"', '') 
        if text.lower() == "text" or len(text) < 100:
            continue
        cleaned.append(text)
    return cleaned



# === STEP 1: Load data ===
def load_reports(path):
    df = pd.read_csv(path, sep=None, engine='python')
    df.columns = [c.strip() for c in df.columns]
    if "Text" in df.columns:
        df = df[df["Text"].notna()]
        return df["Text"].tolist()
    else:
        return df.iloc[:, 0].dropna().tolist()

# === STEP 2: Load pattern terms from RadLex ===
def load_radlex_terms(path):
    df = pd.read_csv(path)
    terms = set()
    for col in df.columns:
        col_values = df[col].dropna().astype(str).tolist()
        for val in col_values:
            val = val.strip()
            if len(val.split()) <= 6:  # avoid very long patterns
                terms.add(val.lower())
    return sorted(list(terms), key=lambda x: -len(x))  # longer first

# === STEP 3: Generate BIO labels from patterns ===
def tag_text_with_patterns(text, patterns):
    entities = []
    lowered = text.lower()
    for pattern in patterns:
        for match in re.finditer(re.escape(pattern), lowered):
            start, end = match.span()
            entities.append((start, end, pattern))
    return entities

# === STEP 4: Tokenize + Convert to BIO format ===
def tokenize_and_label(text, entities, tokenizer):
    labels = ["O"] * len(text)

    # Assign BIO labels to character-level positions
    for start, end, _ in entities:
        if start < len(labels):
            labels[start] = "B-ENT"
            for i in range(start + 1, min(end, len(labels))):
                labels[i] = "I-ENT"

    tokens = tokenizer.tokenize(text)
    aligned_labels = []

    i = 0  # pointer in original text
    for token in tokens:
        subword = token.replace("##", "")
        sub_len = len(subword)

        # skip spaces and control characters
        while i < len(text) and text[i].isspace():
            i += 1

        if i < len(labels):
            token_label = labels[i]
        else:
            token_label = "O"  # fallback if pointer goes out of range

        aligned_labels.append((token, token_label))
        i += sub_len

    return aligned_labels

# === STEP 5: Process all reports ===
def build_bio_dataset(reports, patterns, tokenizer):
    all_examples = []
    for report in reports:
        report = str(report).strip()
        if not report:
            continue
        entities = tag_text_with_patterns(report, patterns)
        tokens_with_labels = tokenize_and_label(report, entities, tokenizer)

        sentence = ""
        for token, label in tokens_with_labels:
            sentence += f"{token} {label}\n"
        all_examples.append(sentence + "\n")
    return all_examples

# === MAIN ===
def main():
    print("Loading reports...")
    
    raw_reports = extract_reports_from_raw_file(REPORTS_CSV)

    print(f"Extracted {len(raw_reports)} reports.")
    reports = basic_cleanup(raw_reports)
    print(f"Cleaned total: {len(reports)} reports")
    assert(len(reports)==1982)


    print("Loading vocabulary patterns...")
    patterns = load_radlex_terms(RADLEX_CSV)

    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    print("Generating BIO examples...")
    dataset = build_bio_dataset(reports, patterns, tokenizer)

    print(f"Saving to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.writelines(dataset)

    print("Done! You can now train a NER model with this file.")

if __name__ == "__main__":
    main()
