# Named Entity Recognition NER

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
