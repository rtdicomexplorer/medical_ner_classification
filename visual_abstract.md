╔════════════════════════════════════════════════════════════╗
║     Clinical Data Extraction from Medical Reports          ║
║     using GBERT-based Named Entity Recognition             ║
╚════════════════════════════════════════════════════════════╝

🎯 PURPOSE  
Extract structured data (e.g., diagnoses, medications, dates) from unstructured German clinical text using a GBERT-based NER model.

📊 KEY RESULTS  
✔ High performance on structured fields:
   - DATE: F1 ≈ 0.90  
   - ORG, DOCTOR: F1 ≈ 0.85  
⚠ Lower performance on complex terms:
   - DIAGNOSIS, MEDICATION: F1 ≈ 0.60  

🔬 METHOD OVERVIEW  
1. Input: Clinical text (PDF, DOCX, image, plain text)  
2. OCR & Preprocessing  
3. GBERT model for token-level NER  
4. Post-processing into structured outputs (JSON, HTML)  
5. Synthetic data used for training and validation

🔍 EVALUATION  
- Precision, Recall, F1-score (per entity type)  
- Confusion heatmaps (common misclassifications)

🚀 FUTURE WORK  
- Map extracted entities to HL7 FHIR  
- Embed in DICOM Structured Reports  
- Evaluate on real clinical datasets

🔗 CODE  
[github.com/rtdicomexplorer/medical_ner_classification](https://github.com/rtdicomexplorer/medical_ner_classification)
