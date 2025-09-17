The NER model extracts medical entities like:

"Asthma" (Diagnosis)
"Paracetamol" (Medication)
"Prof. Dr. Meier" (Doctor)
"CT scan" (Procedure)

but these are free-text terms, and may vary in wording, spelling, or language (especially in German).
To make your extracted data standardized and interoperable, you normalize it — meaning:

Convert text entities into standard codes (e.g. ICD-10, SNOMED CT, RxNorm) used in electronic health records and medical systems.
How Normalization Fits in the Pipeline
Here's the step-by-step in your pipeline:

🗂 Input: PDF / DOCX / HTML → Extracted text

🔍 NER: Extract "Asthma" → {"entity": "DIAGNOSIS", "word": "Asthma"}

🧠 Normalizer: "Asthma" → {"code": "J45", "system": "ICD-10", "display": "Asthma"}

🏥 FHIR Mapping: Use normalized code to create valid FHIR Condition resource:

Benefits of Normalization
💡 Semantic clarity — “Asthma” always means ICD-10 J45.

🔄 Interoperability — Share data across hospitals or systems.

📊 Analytics-ready — You can count, group, and analyze by code.

🌐 Language-agnostic — E.g., “Asthma” in German is “Asthma bronchiale” → still maps to the same ICD-10 code.




#### to remember
- git remote add origin REMOTE-URL
