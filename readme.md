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



## Usage
python -m venv venv
- venv\Scripts\activate (win)
- source venv/bin/activate  (linux)

pip install -r requirements.txt

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


### related works
- https://medium.com/one-medical-technology/rapid-prototyping-and-deployment-of-clinical-nlp-models-e4096e3ce833

- https://www.youtube.com/watch?v=tk4ykvAvV7w

- https://www.mdpi.com/2076-3417/15/6/3379

#### tools
- https://github.com/doccano/doccano



-git remote add origin REMOTE-URL



## High-Level Diagram Outline
🧾 Input: Clinical Text (e.g., patient history, discharge summary, etc.)
⬇️
1. Preprocessing

Clean text

Sentence/token split (optional)

Handle encoding, OCR artifacts, etc.

⬇️
2. NER Model Inference

Model: fine-tuned ClinicalBERT

Output: list of labeled entities (with confidence, spans)

⬇️
3. Postprocessing

Filter low-confidence entities

Resolve overlaps/conflicts

Merge fragmented spans

⬇️
4. Normalization (UMLS API)

Map entities to:

ICD-10 / SNOMED CT (Diagnosis)

RxNorm (Medications)

Adds standard codes and names

⬇️
5. FHIR Mapping

Convert entities to:

Patient, Condition, MedicationRequest, etc.

Use normalization output when available

⬇️
6. Output: FHIR Bundle (JSON)

A full structured representation of the medical information

⬇️
7. (Optional) Evaluation

Compare model output against labeled data

Use seqeval, classification_report, etc.


