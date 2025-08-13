# NER Named Entitiy Recognition
Named Entity Recognition (NER) is a subtask of Natural Language Processing (NLP) 
that involves identifying and classifying key elements in text into predefined categories.
Fundamentally, NER revolves around two primary steps:
- identifying entities within the text and
- categorizing these entities into distinct groups.

### Entity Detection
Before performing NER, the raw text is cleaned and broken into units.  
At its most basic, a document or sentence is just a long string of characters. 
Tokenization is the process of breaking this string into meaningful pieces called tokens.  
In English, tokens are often equivalent to words but can also represent punctuation or other symbols

### Entity classification:
Involves assigning the identified entities to specific categories or classes based on their semantic significance and context. These categories can range from person and organization to location, date, and myriad other labels depending on the application's requirements.


## ML Approch (Statistical)
In the realm of traditional machine learning methods for NER, models are trained on data where entities are labeled.  
### BERT-based NER
Input: Entire sentence.  
Output: Label for each token  
*example*

>"Apple Inc. was founded by Steve Jobs in Cupertino."

        | Token     | Entity |
        | --------- | ------ |
        | Apple     | B-ORG  |
        | Inc.      | I-ORG  |
        | was       | O      |
        | founded   | O      |
        | by        | O      |
        | Steve     | B-PER  |
        | Jobs      | I-PER  |
        | in        | O      |
        | Cupertino | B-LOC  |
        | .         | O      |

Tags like:

        B-: Beginning of ...

        I-: Inside of ...

        O: Outside any named entity

In our prpject we ara using  **Hugging-Face** with **gbert-base** for Geraman language..


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
              ▼  models/gber-base
        
### Predictions

           report_xxx
              │
              ▼
     ┌────────────────────┐
     │ Inference Pipeline │  <-- infer_ner.py   (Use infer_ner.py to run predictions on unseen reports)
     └────────┬───────────┘
              │
              ▼
      ┌──────────────────────┐
      │ NER Output (Entities)│ --- (Returns detected entity spans and labels. )
      └────────┬─────────────┘
               │
               ▼
predictions/            output/                      
report_xxx.json         compare_postprocessing_report_xxx.html
        



### Evaluation:
 To evaluate the model, we have created expected results (update of previous prediction)  
 and compare those with the new prediction.  
 The results of the evaluation will saved in evaluation_report..

        
        prediction  expected
      ┌──────────────────────┐
      │    evaluate_ner.py   │ --- (Returns detected entity spans and labels. )
      └────────┬─────────────┘
               │
               ▼
        ** evaluation ?



        ------------------------------------------------Not yet ready


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


