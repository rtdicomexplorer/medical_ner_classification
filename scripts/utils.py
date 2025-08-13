import unicodedata
import re
import json

from config import LABEL2ID, ID2LABEL


diagnosis_icd10_map = {
    "Hypertonie": "I10",
    "Diabetes Mellitus": "E11.9",
    "Asthma": "J45",
    "Pneumonie": "J18.9"
}

vitalsigns = [
    "Blutdruck 120/80 mmHg", 
    "Puls 72/min", 
    "Temperatur 37,2 °C",
    "Sauerstoffsättigung 98 %",
    "Atemfrequenz 16/min",
    "Taillenumfang 90 cm",
    "BMI 23.1 kg/m²",
    "Blutzucker (BZ) 110 mg/dL",
    "Temperatur rektal / tympanisch 38.2 °C",
    "Laktatwert 1.8 mmol/L",
    "Zentralvenöser Druck (ZVD) 5 mmHg"
]

lifestyles = [
    "Nichtraucher", "Raucher (5 Zigaretten/Tag)", "gelegentlicher Alkoholgenuss",
    "regelmäßige Bewegung","Drogenmissbrauch", "trinkt Bier täglich",
]

risk_factors = [
    "familiäre Vorbelastung Diabetes", "Adipositas BMI 32","Nikotinabusus",
    "Hyperlipidämie", "Schlafapnoe","Hypercholesterinämie", "RR erhöht","höheres Lebensalter"
]

# Names and other data
names = ["Herr. Max Müller", "Patientin: Anna Schmidt", "L. Weber", "Frau Sophie Fischer","Otto Kromberger",
         "John Smith", "Mary Jones", "Robert Lee", "Emily Davis"]
doctors = ["Dr. Müller", "Dr. Schneider", "Dr. Becker", "Dr. Weber","Dr. Suhle Nikolas", "Dr. Lehmann", "Dr. Fischer", "Dr. Weber",
           "Dr. Adams", "Dr. Lee", "Dr. Patel", "Dr. Chen"]


symptoms = [

    #Neurologische Symptome
    "Kopfschmerzen",
    "Schwindel",
    "Sprachstörung",
    "Sehstörung",
    "Kribbeln",
    "Taubheitsgefühl",
    "Gangunsicherheit",
    "Lähmungen",
    "Bewusstseinsstörung",
    "Verwirrtheit",
    "Gedächtnisstörung",
    "Tremor",
    "Epileptischer Anfall",

    #Kardiopulmonale Symptome
    "Brustschmerzen",
    "Atemnot",
    "Palpitationen",
    "Orthopnoe",
    "Husten",
    "Zyanose",
    "Druckgefühl in der Brust",
    "Kaltschweißigkeit",
    "Synkope",

    #Allgemeine Symptome
    "Fieber",
    "Müdigkeit",
    "Appetitlosigkeit",
    "Gewichtsverlust",
    "Nachtschweiß",
    "Abgeschlagenheit",
    "Schlafstörung",
    "Konzentrationsstörung",
    "Gliederschmerzen",
    "Unwohlsein",

    #Gastrointestinale Symptome
    "Übelkeit",
    "Erbrechen",
    "Bauchschmerzen",
    "Durchfall",
    "Verstopfung",
    "Blut im Stuhl",
    "Blähungen",
    "Appetitverlust",
    "Reflux",
    "Völlegefühl",

    #Urologische Symptome
    "Schmerzen beim Wasserlassen",
    "Häufiger Harndrang",
    "Nykturie",
    "Harnverhalt",
    "Blut im Urin",
    "Inkontinenz",

    #Dermatologische Symptome
    "Hautausschlag",
    "Juckreiz",
    "Schwellung",
    "Rötung",
    "Hautveränderungen"
]
medications = [

    #Blutdruckmedikamente (Antihypertensiva)
    "Ramipril",
    "Amlodipin",
    "Bisoprolol",
    "Lisinopril",
    "Valsartan",
    "Metoprolol",
    "Hydrochlorothiazid",
    "Candesartan",
    "Enalapril",

    #Antidiabetika
    "Metformin",
    "Insulin",
    "Empagliflozin",
    "Glimepirid",
    "Sitagliptin",
    "Dapagliflozin",

    #Cholesterinsenker
    "Atorvastatin",
    "Simvastatin",
    "Rosuvastatin",
    "Pravastatin",

    #Psychopharmaka & Schlafmittel
    "Diazepam",
    "Lorazepam",
    "Zolpidem",
    "Amitriptylin",
    "Mirtazapin",
    "Sertralin",
    "Citalopram",

    #Schmerzmittel / NSAR
    "Ibuprofen",
    "Paracetamol",
    "ASS",
    "Diclofenac",
    "Naproxen",
    "Novalgin",
    "Metamizol",

    #Antibiotika
    "Amoxicillin",
    "Ciprofloxacin",
    "Azithromycin",
    "Doxycyclin",
    "Clarithromycin",

    #Asthma / COPD
    "Salbutamol",
    "Formoterol",
    "Budesonid",
    "Tiotropium",
    "Beclometason",

    #Blutverdünner / Antikoagulantien
    "Marcumar",
    "Xarelto",
    "Eliquis",
    "Pradaxa",
    "Heparin",
    "Clopidogrel",

    #Rheuma / Immunsuppressiva
    "Methotrexat",
    "Prednisolon",
    "Cortison",
    "Adalimumab",
    "Infliximab"
]

treatments = ["Sauerstofftherapie", "Operation", "Chemotherapie", "Physiotherapie"]
lab_results = ["Hb 13.5 g/dL", "Blutzucker 110 mg/dL", "Cholesterin 200 mg/dL","Glukose: 110 mg/dL"]
allergies = ["Penicillin", "Pollen", "Nüsse","Hausstaubmilben","Tierhaar", "Soia"]
immunizations = ["Masern-Impfung", "Grippeimpfung", "Covid 19"]
devices = ["Herzschrittmacher", "Insulinpumpe","Schlafmaske", "Blutdruckgerät", "Kateter"]
family_histories = ["Mutter mit Diabetes", "Vater mit Bluthochdruck"]
procedures = ["Angioplastie", "MRT-Scan", "Biopsie", "Ultraschall","CT Kopf", "Lyse-Therapie"]
departments = ["Kardiologie", "Notaufnahme", "Onkologie", "Radiologie","Neurologie", "Innere Medizin"]

hospital_names = ["St. Marien Krankenhaus", "Allgemeine Gesundheitsklinik",
                  "Städtisches Medizinzentrum", "Universitätsklinikum München", "Kinderklinik Freiburg"]
hospital_addresses = ["Hauptstraße 12, 80331 München", "Berliner Allee 45, 40212 Düsseldorf","Lindenstraße 8, 10115 Berlin", "Goetheplatz 9, 50674 Köln",
                      "Hugstetterstr. 7 79106 Freiburg"]
hospital_phones = ["089 123456", "0211 987654", "030 234567", "0221 456789", "0761 2720298"]

followup_reasons = [
    "zur Blutdruckkontrolle", "wegen anhaltender Schmerzen", "zur Verlaufskontrolle",
    "zur weiteren Abklärung", "zur Nachsorge", "zur Wundkontrolle", "zur Laborüberprüfung"
]

impressions = [
    "Hinweis auf Pneumonie", "wahrscheinlich virale Ursache", "unklares Abdomen",
    "mögliche Fraktur", "Verdacht auf Infekt", "Hinweis auf Tumor"
]

prev_diagnoses = [
    "frühere Appendizitis", "bekannte Arthrose", "chronische Bronchitis",
    "status post Herzinfarkt", "durchgemachte Pneumonie", "alte Fraktur", "bekannte COPD"
]


occupations = [
  "Gärtner", "Bäcker", "Metzger", "Professor", "Student", "Arbeitslose",
  "Händler", "Kaufmann", "Kauffrau", "Studentin", "Verkäuferin",
  "Lehrer", "Ärztin", "Ingenieur", "Friseur", "Journalist", "Sekretärin",
  "Arzt", "Ingenieur", "Polizist", "Koch", "Pfleger", "Krankenschwester", 
  "Techniker", "Elektriker", "Kaufmann","Kauffrau", "Projektmanager"


]

family_members = [
  "Bruder", "Schwester", "Mutter", "Vater", "Großvater", "Großmutter", "Enkel", "Enkelin",
  "Onkel", "Kind", "Kinder", "Sohn", "Tochter", "Cousine", "Neffe", "Nichte", "Witwe"
]

family_status = ["verheiratet", "geschieden", "verwitwet", "ledig", "getrennt", "in einer Beziehung", "alleinstehend"]


def normalize_token(token):
    return unicodedata.normalize("NFKC", token.lower())

def __merge_date_tokens(tokens, tags):
    merged_tokens = []
    merged_tags = []
    i = 0
    while i < len(tokens):
        # Datum: 18 . 10 . 2007
        if (
            i + 4 < len(tokens)
            and re.fullmatch(r"\d{1,2}", tokens[i])
            and tokens[i+1] == "."
            and re.fullmatch(r"\d{1,2}", tokens[i+2])
            and tokens[i+3] == "."
            and re.fullmatch(r"\d{4}", tokens[i+4])
        ):
            merged_tokens.append(f"{tokens[i]}.{tokens[i+2]}.{tokens[i+4]}")
            merged_tags.append(tags[i])  # Nimm Tag des ersten Tokens
            i += 5
            continue

        # Uhrzeit: 18 : 24 [: 33 optional]
        if (
            i + 2 < len(tokens)
            and re.fullmatch(r"\d{1,2}", tokens[i])
            and tokens[i+1] == ":"
            and re.fullmatch(r"\d{1,2}", tokens[i+2])
        ):
            if (
                i + 4 < len(tokens)
                and tokens[i+3] == ":"
                and re.fullmatch(r"\d{1,2}", tokens[i+4])
            ):
                # Format: hh:mm:ss
                merged_tokens.append(f"{tokens[i]}:{tokens[i+2]}:{tokens[i+4]}")
                merged_tags.append(tags[i])
                i += 5
                continue
            else:
                # Format: hh:mm
                merged_tokens.append(f"{tokens[i]}:{tokens[i+2]}")
                merged_tags.append(tags[i])
                i += 3
                continue

        # Kein spezielles Format → Standard übernehmen
        merged_tokens.append(tokens[i])
        merged_tags.append(tags[i])
        i += 1

    return merged_tokens, merged_tags

def is_numeric_or_code(token):
    return re.fullmatch(r"[\d.]+", token) or re.fullmatch(r"[A-Z]\d{2}", token)



def __generate_filtered_stopwords(data, id2label, threshold=0.95):
    from collections import defaultdict
    import unicodedata

    def normalize(token):
        return unicodedata.normalize("NFKC", token.lower())

    token_counts = defaultdict(int)
    token_non_entity_counts = defaultdict(int)
    entity_token_set = set()

    for entry in data:
        tokens = entry["tokens"]
        tags = entry["ner_tags"]
        for token, tag_id in zip(tokens, tags):
            token_n = normalize(token)
            token_counts[token_n] += 1
            label = id2label[tag_id]
            if label != "O":
                entity_token_set.add(token_n)
            else:
                token_non_entity_counts[token_n] += 1
  # Substring-Matching Liste
    substring_whitelist = [
        "schmerz", "befund", "messung", "anamnese", "symptom", "diagnose", "therapie", "entzündung","untersuchung", "aufnahme", 
        "fall", "arzt", "krank", "blut"
    ]
    manual_whitelist = {
        "impression",

        "puls", 
        "risikofaktor", "medikament", 
         "untersuchung", "beschwerden",  "verabreichtes",
        "icd", "ursache", "folgegrund", "wahrscheinlich", "virale",
       "kam", "ihn", "über", "empfohlen","patienten", "gerät",
        "anhaltende", "vorherige", "frühere", "brachte", "wird",
         # Symptome
        "atemnot", "fieber", "husten", "kribbeln", "schwindel", "übelkeit",
        "erbrechen", "lallende",  "schluckstörung", "blutdruck", "taubheit", "sehstörung",
         "atemprobleme", "müdigkeit", "erschöpfung", "gewichtverlust",
    
        # Diagnosen
        "diabetes", "hypertonie", "hypotonie", "epilepsie", "tumor", "appendizitis", "schlaganfall",
        "infarkt", "bronchitis", "asthma", "adipositas", "depression", "herzinsuffizienz",

        # Medikamente
        "metformin", "lisinopril", "insulin", "paracetamol", "ibuprofen", "antibiotika", "aspirin",
        "glucose", "cholesterin",

        # Maßnahmen
        "eingriff", "operation", "behandlung",
        "lyse", "injektion", "aufnahme", "entlassung",

        # Geräte
        "schlafmaske", "rollstuhl", "insulinpumpe", "beatmungsgerät", "infusionspumpe", "monitor",

        # Labor
       "puls", "blutdruck", "temperatur", "sauerstoffsättigung", "herzfrequenz",
        "mg", "dl", "bmi", "gewicht", "größe",

        # Familie
        "vater", "mutter", "geschwister",  "cousine", "bruder", "familienmitglied"
    }
    manual_stopwords = {
        "-", ":", ".", ",", "berichtete", "telefon", "tel", "/", "–", "(", ")", "„", "“",
        "eine", "ein", "der", "die", "das", "am", "an", "im", "für", "mit", "von",
        "es", "da", "und", "auch", "nicht", "bekannt", "zuvor", "wurde", "ist", "war", "sich",
        "durch", "bei", "zu", "als", "in", "auf", "unter", "nach", "vor", "mehr", "weniger"
    }
    MIN_TOKEN_FREQ = 3 
    whitelist = entity_token_set.union(manual_whitelist)
    stop_words = set()
    review_false_positives = []

    for token, total_count in token_counts.items():
        if total_count == 0:
            continue

        o_ratio = token_non_entity_counts[token] / total_count
        if  any(substr in token for substr in substring_whitelist):
            continue
        elif token in manual_stopwords:
            stop_words.add(token)
        elif token in whitelist:
            continue
        elif is_numeric_or_code(token):
            continue  # Zahlen und Codes nie stoppen
        elif  total_count >= MIN_TOKEN_FREQ and o_ratio >= threshold:
            stop_words.add(token)
            if re.match(r"[a-zäöüß]+", token):  # keine reinen Zahlen/Punktuation
                review_false_positives.append((token, o_ratio))

    # Logging
    if review_false_positives:
        print("\n⚠️  Potenziell falsch gestoppte relevante Tokens:")
        for token, ratio in sorted(review_false_positives, key=lambda x: -x[1]):
            print(f"[Stopword] {token} → {ratio:.2f}")

    return stop_words

def __clean_ner_tags(oldtokens, ner_tags, stop_words):
    #clean_tags = ner_tags.copy()

    tokens, clean_tags = __merge_date_tokens(oldtokens, ner_tags)

    n = len(tokens)

    for i in range(n):
        label_id = clean_tags[i]
        label = ID2LABEL[label_id]
        token = normalize_token(tokens[i])  # <- normalize hier auch

   
       

        if token in stop_words:
            clean_tags[i] = LABEL2ID["O"]
            continue

        # I-Tag ohne voriges B- oder I- → B machen
        if label.startswith("I-"):
            entity = label[2:]
            if i == 0 or not ID2LABEL[clean_tags[i - 1]].endswith(entity):
                clean_tags[i] = LABEL2ID.get("B-" + entity, label_id)

        # Zwei B- direkt nacheinander mit gleicher Entität → zweites wird I-
        if label.startswith("B-") and i > 0:
            entity = label[2:]
            prev_label = ID2LABEL[clean_tags[i - 1]]
            if prev_label.startswith(("B-", "I-")) and prev_label.endswith(entity):
                clean_tags[i] = LABEL2ID.get("I-" + entity, label_id)

    return tokens,clean_tags



def refresh_and_clean_ner_labels(data, id2label, threshold = 0.95):

    stopwords = __generate_filtered_stopwords(data, id2label,threshold)
    for entry in data:
        entry["tokens"],entry["ner_tags"] = __clean_ner_tags(entry["tokens"], entry["ner_tags"], stopwords)

    return data




def main():
    # Lade Daten
    data_path = "./data/train.json"
    output_path = "dein_datensatz_cleaned2.json"

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    cleardata = refresh_and_clean_ner_labels(data,ID2LABEL, 0.95)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cleardata, f, indent=2, ensure_ascii=False)

    print(f"✔ Bereinigt und gespeichert unter: {output_path}")


if __name__ == "__main__":
    main()


   