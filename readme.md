# Clinical NER to FHIR Pipeline

This repository contains a complete pipeline for extracting clinical entities from documents and mapping them to FHIR resources.

---

## Overview

The pipeline processes clinical documents (PDFs, DOCX, images, TXT), extracts text, runs Named Entity Recognition (NER) using a fine-tuned ClinicalBERT model, and maps recognized entities to FHIR standard resources.

---

       ┌────────────────────┐
       │ Synthetic Data Gen │  <-- generate_data.py  (Inject labeled entities: PERSON, DOCTOR, ORG, DIAGNOSIS, etc.)
       └────────┬───────────┘
                │
                ▼
        ┌──────────────┐
        │ Token Labeler│  (BIO tags) (Convert text and labeled spans to token-level BIO format.) z.B. "Max" → B-PERSON, "Müller" → I-PERSON
        └─────┬────────┘
              │
              ▼
     ┌─────────────────────┐
     │ Model Training (NER)│  <-- train_ner.py (Fine-tune a transformer (e.g. ClinicalBERT or DeBERTa) using Hugging Face Trainer)
     └────────┬────────────┘
              │
              ▼
      ┌──────────────────┐
      │ Trained NER Model│  (e.g., fine-tuned BERT)
      └────────┬─────────┘
               │
               ▼
     ┌────────────────────┐
     │ Inference Pipeline │  <-- infer_ner.py   (Use infer_ner.py to run predictions on unseen reports)
     └────────┬───────────┘
              │
              ▼
      ┌──────────────────────┐
      │ NER Output (Entities)│ --- (Returns detected entity spans and labels.)
      └────────┬─────────────┘
               │
               ▼
     ┌──────────────────────────┐
     │ FHIR Mapping Logic       │  <-- fhir_mapper.py (DOCTOR → Practitioner, DIAGNOSIS → Condition,MEDICATION → MedicationRequest)
     └────────┬─────────────────┘
              │
              ▼
     ┌──────────────────────────┐
     │ FHIR Resources (JSON)    │  --> Output (fhir_output.json)
     └──────────────────────────┘



## Prediction Pipeline Steps

1. **Text Extraction**  
   Handles different file types:
   - PDFs (normal and scanned via OCR)  
   - DOCX documents  
   - Images (PNG, JPG, TIFF, etc.)  
   - Plain text files (TXT)  

2. **NER Inference**  
   Uses a fine-tuned ClinicalBERT model for token classification to extract entities such as PERSON, DOCTOR, DIAGNOSIS, MEDICATION, etc.

3. **Mapping to FHIR**  
   Converts detected entities into appropriate FHIR resource JSON structures, e.g., Patient, Condition, MedicationRequest.

---
## File Structure

- `text_extractor.py`  
  Extracts raw text from various document formats.

- `generate_data.py`  
  Generates synthetic labeled clinical text data for training.

- `train_ner.py`  
  Fine-tunes the ClinicalBERT model on synthetic data.

- `infer_ner.py`  
  Loads the trained model and runs inference on extracted text.

- `ner_to_fhir.py`  
  Maps NER entities to FHIR resources.

- `config.py`  
  Configuration and label mappings.

---

## Usage

### Training:

- python generate_data.py
- python train_ner.py

--- 


### Extract text from a file:

from text_extractor import extract_text_from_file
text = extract_text_from_file("path/to/document.pdf")
print(text)

---

### Run NER inference on extracted text:
from infer_ner import load_model, infer_text

nlp = load_model()
entities = infer_text(nlp, text)
print(entities)

---
### Map NER results to FHIR:

from ner_to_fhir import map_ner_to_fhir

fhir_resources = map_ner_to_fhir(entities)
print(fhir_resources)

---
## Contaact
For questions or collaboration, please contact [Your Name] at [michele.bufano@uniklinik-freiburg.de].

Want me to help you save this as a file or customize it?




### Mapping Clinical Label to FHIR

| NER Label       | Example Entities       | Corresponding FHIR Resource                 |
| --------------- | ---------------------- | ------------------------------------------- |
| PERSON          | Patient, Family member | `Patient`, `RelatedPerson`                  |
| DOCTOR          | Physician, Specialist  | `Practitioner`                              |
| ORGANIZATION    | Hospital, Clinic       | `Organization`                              |
| DATE            | Admission date, DOB    | Date fields in many resources               |
| DIAGNOSIS       | Disease names          | `Condition`                                 |
| SYMPTOM         | Clinical findings      | `Observation` (with symptom codes)          |
| MEDICATION      | Drugs, prescriptions   | `MedicationRequest`, `Medication`           |
| PROCEDURE       | Surgeries, exams       | `Procedure`                                 |
| TREATMENT       | Therapies, care plans  | `CarePlan`, `Procedure`                     |
| DEPARTMENT      | Hospital units         | Can be part of `Location` or `Organization` |
| LAB\_RESULT     | Blood test values      | `Observation`                               |
| ALLERGY         | Allergies              | `AllergyIntolerance`                        |
| IMMUNIZATION    | Vaccines               | `Immunization`                              |
| DEVICE          | Medical devices        | `Device`                                    |
| FAMILY\_HISTORY | Family medical history | `FamilyMemberHistory`                       |






### question
I'd like to train a model that can recovery medical information, name date diagnosis etc from medical report. How can I proced


### https://medium.com/one-medical-technology/rapid-prototyping-and-deployment-of-clinical-nlp-models-e4096e3ce833

#### links
- https://github.com/doccano/doccano



-git remote add origin REMOTE-URL
