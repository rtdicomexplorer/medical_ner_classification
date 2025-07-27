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