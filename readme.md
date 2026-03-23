

<p align="center">
  <img src="frontend/clinical_data_extractor.png" alt="Projekt Logo" width="200"/>
</p>


# NER Named Entitiy Recognition
Named Entity Recognition (NER) is a subtask of Natural Language Processing (NLP) 
that involves identifying and classifying key elements in text into predefined categories.
Fundamentally, NER revolves around two primary steps:
- identifying entities within the text and
- categorizing these entities into distinct groups.

### Entity Detection
Before performing NER, the raw text is cleaned and broken into units (token).  
In English, tokens are often equivalent to words but can also represent punctuation or other symbols.

### Entity classification:
Involves assigning the identified entities to specific categories or classes based on their semantic significance and context.
<br>These categories can range from person and organization to location, date, and myriad other labels depending on the application's requirements.


## ML Approch (Statistical)
In the realm of traditional machine learning methods for NER, models are trained on data where entities are labeled.  


In our project we are using  **Hugging-Face** with **gbert-base** for German language..
### GBERT-based NER
Input: Entire sentence.  
Output: Label for each token  
*example*

>"Apple Inc. was founded on April 1, 1976 by Steve Jobs in Cupertino."

        | Token     | Entity |
        | --------- | ------ |
        | Apple     | B-ORG  |
        | Inc.      | I-ORG  |
        | was       | O      |
        | founded   | O      |
        | on        | O      |
        | April     | B-DATE |
        | 1         | I-DATE |
        | ,         | I-DATE |
        | 1976      | I-DATE |
        | by        | O      |
        | Steve     | B-PER  |
        | Jobs      | I-PER  |
        | in        | O      |
        | Cupertino | B-LOC  |
        | .         | O      |
The Entities, defined by **LABEL** are in this case: 

        ORG
        PER
        LOC
        DATE

Tags like:

        B-: Beginning of ...
        I-: Inside of ...
        O: Outside any named entity


### TRAININGS DATA
To train the model, a significant amount of data consisting of tokens and their positions in a json structure is needed.

       [
                {
                "tokens": [
                                "Apple", "Inc.", "was", "founded", "on", "April", "1", ",", "1976",
                                "by", "Steve", "Jobs", "in", "Cupertino", "."
                        ],
                "ner_tags": [
                                1, 2, 0, 0, 0, 6, 7, 7, 7,
                                0, 3, 4, 0, 5, 0
                        ]
                }
        ]


The program includes a script that can generate synthetic data based on templates and paraphrases.

### OUTPUT DATA
For the sentece: 
> "Microsoft Inc. was founded on April 4, 1975 by Bill Gates in Albuquerque."


        [
                {
                        "entity_group": "ORG",
                        "word": "Microsoft Inc.",
                        "start": 0,
                        "end": 15,
                        "score": 1.0
                },
                {
                        "entity_group": "DATE",
                        "word": "April 4, 1975",
                        "start": 26,
                        "end": 40,
                        "score": 1.0
                },
                {
                        "entity_group": "PERSON",
                        "word": "Bill Gates",
                        "start": 44,
                        "end": 54,
                        "score": 1.0
                },
                {
                        "entity_group": "LOC",
                        "word": "Albuquerque",
                        "start": 58,
                        "end": 69,
                        "score": 1.0
                }
        ]




## Overview

### Trainings PIPELINE

> 1 - Generate synthetic data: python .\scripts\generate_new_data.py -nr-data(int)  -save-reports(bool) it generates nr data splitted in tran.json, test.json, val.json in **./data/**; if you decide to save the reports, then all rports will be saved in **./txt_reports/** and the entities in **./entities/** it will be saved also all.json in ./data
<br> 2 - Train the model:  python .\scrips\training_model.py
<br> 3 - After the training the new model has been saved into models/gbert-base   


### Prediction PIPELINE
The pipeline processes extracted texts from clinical documents (PDFs, DOCX, images, TXT, Scans). 

let run: python ./scripts/predictions_ner.py -filename

the prediction will be saved in ./prediction/filename.json
in ./output/ is also saved the ner_tag.json and a compare.html, that display the differences after a postprocessing process (**not yet testet** )


  



## TO DO

### 1- Evaluation (to be updated....):
 To evaluate the model, we have created expected results (update of previous prediction)  
 and compare those with the new prediction.  
 The results of the evaluation will saved in evaluation_report..

        
        prediction  expected
      ┌──────────────────────┐
      │    validate_prediction.py   │ --- (Returns detected entity spans and labels. )
      └────────┬─────────────┘
               │
               ▼
        ** evaluation ?



### 2- Entities to FHIR 

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









## Usage

### Prerequisite
python -m venv venv
- venv\Scripts\activate (win)
- source venv/bin/activate  (linux)

install tesseract: 
 Windows: 
 download https://github.com/UB-Mannheim/tesseract/wiki (also GERMAN Language)

 UBUNTU:  
> sudo apt update
> sudo apt install tesseract-ocr
> sudo apt install tesseract-ocr-deu

pip install -r requirements.txt


### WEB APP

The project contains also a small flask/app to manage the predictions:

> python ./backend/app.py





---

## Citation

```tex
@misc{doccano,
  title={{MEDICAL_NER_CLASSIFICATION}: Clinical data extractor.},
  url={https://github.com/rtdicomexplorer/medical_ner_classification},
  note={Software available from https://github.com/rtdicomexplorer/medical_ner_classification},
  author={
    Michele Bufano},
    year={2025},
}
```





## Contaact
For questions or collaboration, please contact [the author](https://github.com/rtdicomexplorer)



### related works
- https://medium.com/one-medical-technology/rapid-prototyping-and-deployment-of-clinical-nlp-models-e4096e3ce833

- https://www.youtube.com/watch?v=tk4ykvAvV7w

- https://www.mdpi.com/2076-3417/15/6/3379




