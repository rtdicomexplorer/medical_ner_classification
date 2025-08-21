arztbrief_template = (
    "{DOCUMENT_TYPE} vom {DATE}:\n"
    "Patient: {PERSON} ({GENDER}), geboren am {BIRTHDATE}, PID: {PID}.\n"
    "Adresse: {ADDRESS}, Telefon: {PHONE}, Familienstand: {FAMILY_STATUS}.\n"
    "Beruf: {OCCUPATION}, begleitet von: {FAMILYMEMBER}.\n"
    "Vorstellung wegen: {SYMPTOM}.\n"
    "Diagnose: {DIAGNOSIS} (ICD-10: {ICD10_CODE} – {ICD10_DESC}).\n"
    "Vorherige Diagnose: {PREV_DIAGNOSIS}.\n"
    "Familiäre Vorbelastung: {FAMHIST}.\n"
    "Medikation: {MEDICATION}, Behandlung: {TREATMENT}, Prozedur: {PROCEDURE}.\n"
    "Labor: {LAB_RESULT}, Vitalzeichen: {VITALSIGNS}.\n"
    "Empfehlung: {FOLLOWUP_REQ} bei {FOLLOWUP_REASON}.\n"
    "Untersuchung durch {DOCTOR}, Abteilung: {DEPARTMENT}, Klinik: {ORG}.\n"
    "Adresse: {ADDRESS}, Tel: {PHONE}.\n"
    "Impression: {IMPRESSION}."
)

befundbericht_template = (
    "{DOCUMENT_TYPE} erstellt am {DATE} durch {DOCTOR} in der Abteilung {DEPARTMENT} des {ORG}.\n"
    "Patient: {PERSON}, {GENDER}, geb. {BIRTHDATE}, PID: {PID}.\n"
    "Untersuchung mittels {DEVICE} aufgrund von {SYMPTOM}.\n"
    "Befunde: {FINDING}, Diagnose: {DIAGNOSIS}.\n"
    "ICD-10-Code: {ICD10_CODE} – {ICD10_DESC}.\n"
    "Laborwerte: {LAB_RESULT}, Vitalzeichen: {VITALSIGNS}.\n"
    "Empfehlung: {TREATMENT}. Impression: {IMPRESSION}.\n"
    "Kontakt: {PHONE}, Adresse: {ADDRESS}."
)

operationsbericht_template = (
    "{DOCUMENT_TYPE}\n"
    "Datum der Operation: {DATE}, durchgeführt von {DOCTOR} im {ORG}, Abteilung: {DEPARTMENT}.\n"
    "Patient: {PERSON}, Geschlecht: {GENDER}, Geburtsdatum: {BIRTHDATE}, PID: {PID}.\n"
    "Indikation: {DIAGNOSIS} – {SYMPTOM}.\n"
    "Durchgeführte Prozedur: {PROCEDURE} unter Einsatz von {DEVICE}.\n"
    "Anästhesieprotokoll: {VITALSIGNS}.\n"
    "Postoperativer Verlauf: {IMPRESSION}.\n"
    "Empfohlene Medikation: {MEDICATION}, weitere Behandlung: {TREATMENT}.\n"
    "Kontakt für Rückfragen: {DOCTOR}, Tel: {PHONE}."
)

entlassungsbericht_template = (
    "{DOCUMENT_TYPE} – Entlassung am {DISCHARGE_DATE} aus der Klinik {ORG}, Abteilung: {DEPARTMENT}.\n"
    "Patient: {PERSON} ({GENDER}), geb. {BIRTHDATE}, PID: {PID}.\n"
    "Aufnahmediagnose: {DIAGNOSIS}, am {ADMISSION_DATE} Symptome: {SYMPTOM}, Risikofaktoren: {RISKFACTOR}.\n"
    "Behandlung: {TREATMENT}, Medikation: {MEDICATION}, Prozedur: {PROCEDURE}.\n"
    "Befunde: {FINDING}, Labordaten: {LAB_RESULT}.\n"
    "Entlassungsdiagnose: {DIAGNOSIS} ({ICD10_CODE} – {ICD10_DESC}).\n"
    "Empfohlene Nachsorge: {FOLLOWUP_REQ}, Grund: {FOLLOWUP_REASON}.\n"
    "Impression: {IMPRESSION}.\n"
    "Kontaktperson: {DOCTOR}, Tel: {PHONE}."
)

anamnesebogen_template = (
    "{DOCUMENT_TYPE} – Erfasst am {DATE} durch {DOCTOR}.\n"
    "Patient: {PERSON}, Geschlecht: {GENDER}, Geburtsdatum: {BIRTHDATE}, PID: {PID}.\n"
    "Adresse: {ADDRESS}, Telefon: {PHONE}, Familienstand: {FAMILY_STATUS}.\n"
    "Beruf: {OCCUPATION}, Lebensstil: {LIFESTYLE}, Impfstatus: {IMMUNIZATION}.\n"
    "Allergien: {ALLERGY}.\n"
    "Familiäre Erkrankungen: {FAMHIST}.\n"
    "Vorerkrankungen: {PREV_DIAGNOSIS}, Medikamente: {MEDICATION}.\n"
    "Aktuelle Beschwerden: {SYMPTOM}.\n"
    "Körperdaten: Größe {GROESSE}, Gewicht {GEWICHT}."
)

radiologie_template = (
    "{DOCUMENT_TYPE} – Untersuchung vom {DATE} durchgeführt durch {DOCTOR} in der Abteilung {DEPARTMENT}, {ORG}.\n"
    "Patient: {PERSON}, {GENDER}, geb. am {BIRTHDATE}, PID: {PID}.\n"
    "Indikation: {SYMPTOM}, Fragestellung: {FINDING}.\n"
    "Durchgeführte Bildgebung: {PROCEDURE} mit {DEVICE}.\n"
    "Befund: {FINDING}.\n"
    "Impression: {IMPRESSION}.\n"
    "Telefon: {PHONE}, Adresse: {ADDRESS}."
)

laborbericht_template = (
    "{DOCUMENT_TYPE} – erstellt am {DATE}.\n"
    "Patient: {PERSON} ({GENDER}), geboren am {BIRTHDATE}, PID: {PID}.\n"
    "Untersuchende Einrichtung: {ORG}, Abteilung: {DEPARTMENT}.\n"
    "Laborparameter: {LAB_RESULT}.\n"
    "Diagnosehinweis: {DIAGNOSIS} ({ICD10_CODE} – {ICD10_DESC}).\n"
    "Beurteilung: {IMPRESSION}.\n"
    "Kontakt: {DOCTOR}, Tel: {PHONE}."
)

patho_template = (
    "{DOCUMENT_TYPE} – Befunddatum: {DATE}, Pathologieabteilung: {DEPARTMENT}, Klinik: {ORG}.\n"
    "Patient: {PERSON}, {GENDER}, geb. {BIRTHDATE}, PID: {PID}.\n"
    "Material: {PROCEDURE}.\n"
    "Makroskopie: {FINDING}.\n"
    "Mikroskopie: {DIAGNOSIS}, ICD-10: {ICD10_CODE} – {ICD10_DESC}.\n"
    "Zusätzliche Tests: {LAB_RESULT}.\n"
    "Beurteilung: {IMPRESSION}.\n"
    "Arzt: {DOCTOR}, Tel: {PHONE}, der Abteilung {DEPARTMENT}."
)

ueberweisung_template = (
    "{DOCUMENT_TYPE} – Ausgestellt am {DATE} von {DOCTOR}, {DEPARTMENT}, {ORG}.\n"
    "Patient: {PERSON}, geb. {BIRTHDATE}, PID: {PID}.\n"
    "Zielabteilung: {DEPARTMENT}.\n"
    "Grund der Überweisung: {FOLLOWUP_REASON}.\n"
    "Vorbefunde: {PREV_DIAGNOSIS}, aktuelle Beschwerden: {SYMPTOM}.\n"
    "Aktuelle Medikation: {MEDICATION}.\n"
    "Telefon: {PHONE}, Adresse: {ADDRESS}."
)

einwilligung_template = (
    "{DOCUMENT_TYPE} – Ausgefüllt am {DATE}.\n"
    "Patient: {PERSON} ({GENDER}), geb. am {BIRTHDATE}, PID: {PID}.\n"
    "Für das folgende Verfahren: {PROCEDURE}.\n"
    "Behandelnder Arzt: {DOCTOR}, Abteilung: {DEPARTMENT}, Klinik: {ORG}.\n"
    "Risiken und Alternativen wurden erklärt.\n"
    "Diagnose/Indikation: {DIAGNOSIS}, Symptome: {SYMPTOM}.\n"
    "Patient gibt Einwilligung zur Behandlung mit {TREATMENT}.\n"
    "Telefon: {PHONE}, Adresse: {ADDRESS}."
)

impfpass_template = (
    "{DOCUMENT_TYPE} – Stand: {DATE}.\n"
    "Patient: {PERSON}, geboren am {BIRTHDATE}, Geschlecht: {GENDER}, PID: {PID}.\n"
    "Erfasste Impfungen: {IMMUNIZATION}.\n"
    "Hausarzt: {DOCTOR}, Einrichtung: {ORG}, Abteilung: {DEPARTMENT}.\n"
    "Bemerkung: {IMPRESSION}.\n"
    "Adresse: {ADDRESS}, Telefon: {PHONE}."
)

rezept_template = (
    "{DOCUMENT_TYPE} – Ausgestellt am {DATE} durch {DOCTOR} ({DEPARTMENT}, {ORG}).\n"
    "Patient: {PERSON}, geboren am {BIRTHDATE}, PID: {PID}.\n"
    "Verschriebene Medikation: {MEDICATION}.\n"
    "Diagnosebezug: {DIAGNOSIS} ({ICD10_CODE} – {ICD10_DESC}).\n"
    "Bemerkung: {IMPRESSION}.\n"
    "Telefon: {PHONE}, Adresse: {ADDRESS}."
)

therapieplan_template = (
    "{DOCUMENT_TYPE} – Erstellt am {DATE} durch {DOCTOR} in der Abteilung {DEPARTMENT}, Klinik: {ORG}.\n"
    "Patient: {PERSON}, {GENDER}, geb. {BIRTHDATE}, PID: {PID}.\n"
    "Diagnose: {DIAGNOSIS} ({ICD10_CODE} – {ICD10_DESC}).\n"
    "Ziel der Therapie: {FOLLOWUP_REASON}.\n"
    "Empfohlene Maßnahmen:\n"
    "- Behandlung: {TREATMENT}\n"
    "- Medikation: {MEDICATION}\n"
    "- Nachsorge: {FOLLOWUP_REQ}\n"
    "Impression: {IMPRESSION}.\n"
    "Adresse: {ADDRESS}, Tel: {PHONE}."
)

pflegedoku_template = (
    "{DOCUMENT_TYPE} – Eintrag vom {DATE}.\n"
    "Patient: {PERSON}, geboren am {BIRTHDATE}, Geschlecht: {GENDER}, PID: {PID}.\n"
    "Aktueller Zustand: {FINDING}, Vitalwerte: {VITALSIGNS}.\n"
    "Pflegemaßnahmen: {TREATMENT}, Medikation: {MEDICATION}.\n"
    "Auffälligkeiten: {SYMPTOM}, Allergien: {ALLERGY}.\n"
    "Pflegekraft: {DOCTOR}, Station: {DEPARTMENT}, Klinik: {ORG}.\n"
    "Adresse: {ADDRESS}, Telefon: {PHONE}."
)

opfreigabe_template = (
    "{DOCUMENT_TYPE} – Freigegeben am {DATE} durch {DOCTOR}, Abteilung: {DEPARTMENT}.\n"
    "Patient: {PERSON}, geb. am {BIRTHDATE}, PID: {PID}, {GENDER}.\n"
    "Geplante Prozedur: {PROCEDURE}.\n"
    "Indikation: {DIAGNOSIS}, Symptome: {SYMPTOM}.\n"
    "Vitalzeichen stabil: {VITALSIGNS}.\n"
    "Keine Kontraindikationen festgestellt.\n"
    "Medikation vor OP: {MEDICATION}.\n"
    "Einrichtung: {ORG}, Adresse: {ADDRESS}, Tel: {PHONE}."
)

aufnahmebogen_template = (
    "{DOCUMENT_TYPE} – Aufnahme am {ADMISSION_DATE} in {ORG}, Abteilung: {DEPARTMENT}.\n"
    "Patient: {PERSON}, {GENDER}, geboren am {BIRTHDATE}, PID: {PID}.\n"
    "Adresse: {ADDRESS}, Tel: {PHONE}, Familienstand: {FAMILY_STATUS}.\n"
    "Beschwerden: {SYMPTOM}, Vorbefunde: {PREV_DIAGNOSIS}.\n"
    "Aktuelle Medikation: {MEDICATION}, Allergien: {ALLERGY}.\n"
    "Größe: {GROESSE}, Gewicht: {GEWICHT}, Vitalwerte: {VITALSIGNS}.\n"
    "Begleitung durch: {FAMILYMEMBER}.\n"
    "Untersuchender Arzt: {DOCTOR}.\n"
    "Verlegt auf Staion 7 Zimmer {ROOM_NUMBER}"
)

hkp_template = (
    "{DOCUMENT_TYPE} – Erstellt am {DATE} durch {DOCTOR}, {ORG}.\n"
    "Patient: {PERSON}, PID: {PID}, geboren am {BIRTHDATE}.\n"
    "Diagnose: {DIAGNOSIS} ({ICD10_CODE} – {ICD10_DESC}).\n"
    "Geplante Behandlung: {TREATMENT}, Prozeduren: {PROCEDURE}.\n"
    "Medikamente: {MEDICATION}.\n"
    "Kostenaufstellung gemäß Krankenkasse.\n"
    "Kontakt: {PHONE}, Adresse: {ADDRESS}."
)

attest_template = (
    "{DOCUMENT_TYPE} – Ausgestellt am {DATE}.\n"
    "Patient: {PERSON}, geb. am {BIRTHDATE}, PID: {PID}, Beruf: {OCCUPATION}.\n"
    "Diagnose: {DIAGNOSIS}, Beschwerden: {SYMPTOM}.\n"
    "Der Patient ist derzeit {FOLLOWUP_REASON}.\n"
    "Dauer der Arbeitsunfähigkeit: {FOLLOWUP_REQ}.\n"
    "Unterschrift: {DOCTOR}, Abteilung: {DEPARTMENT}, {ORG}."
)

notfall_template = (
    "{DOCUMENT_TYPE} – Datum: {ADMISSION_DATE}, ausgestellt durch {DOCTOR}, Klinik: {ORG}.\n"
    "Patient: {PERSON}, {GENDER}, geb. am {BIRTHDATE}, PID: {PID}.\n"
    "Telefon: {PHONE}, Adresse: {ADDRESS}.\n"
    "Begleitet von {FAMILYMEMBER}.\n"
    "Symptome: {SYMPTOM}, Vitalwerte: {VITALSIGNS}, Risikofaktoren: {RISKFACTOR}.\n"
    "Durchgeführte Maßnahmen: {TREATMENT}, verabreichte Medikation: {MEDICATION}.\n"
    "Diagnose: {DIAGNOSIS} ({ICD10_CODE} – {ICD10_DESC}).\n"
    "Patient wurde stationär auf die Station Escherich Zimmer {ROOM_NUMBER} aufgenommen.\n"

)

ekg_template = (
    "{DOCUMENT_TYPE} – Befunddatum: {DATE}, erstellt durch {DOCTOR}, Abteilung: {DEPARTMENT}, {ORG}.\n"
    "Patient: {PERSON}, geb. am {BIRTHDATE}, PID: {PID}.\n"
    "Indikation: {SYMPTOM}.\n"
    "Ergebnisse: {FINDING}, Vitalzeichen: {VITALSIGNS}.\n"
    "Diagnose: {DIAGNOSIS}, Beurteilung: {IMPRESSION}.\n"
    "Telefon: {PHONE}, Adresse: {ADDRESS}."
)

roentgen_template = (
    "{DOCUMENT_TYPE} – Untersuchung am {DATE}, Klinik: {ORG}, Abteilung: {DEPARTMENT}.\n"
    "Patient: {PERSON}, PID: {PID}, geboren am {BIRTHDATE}.\n"
    "Bildgebung mittels {DEVICE} bei {SYMPTOM}.\n"
    "Befunde: {FINDING}, Impression: {IMPRESSION}.\n"
    "Diagnose: {DIAGNOSIS}.\n"
    "Untersuchender Arzt: {DOCTOR}, Kontakt: {PHONE}."
)

ct_mrt_template = (
    "{DOCUMENT_TYPE} – {DATE}, erstellt durch {DOCTOR}, {ORG}, Abteilung: {DEPARTMENT}.\n"
    "Patient: {PERSON}, geb. {BIRTHDATE}, PID: {PID}.\n"
    "Verfahren: {PROCEDURE} mit {DEVICE}.\n"
    "Indikation: {SYMPTOM}, Befunde: {FINDING}.\n"
    "Diagnose: {DIAGNOSIS} ({ICD10_CODE} – {ICD10_DESC}), Impression: {IMPRESSION}.\n"
    "Empfohlene Nachsorge: {FOLLOWUP_REQ}, Grund: {FOLLOWUP_REASON}."
)

pflegeueberleitung_template = (
    "{DOCUMENT_TYPE} – Erstellt am {DATE} durch {DOCTOR}, {ORG}, Abteilung: {DEPARTMENT}.\n"
    "Patient: {PERSON}, geboren am {BIRTHDATE}, PID: {PID}.\n"
    "Pflegebedürfnisse: {TREATMENT}, Medikation: {MEDICATION}, Vitalzeichen: {VITALSIGNS}.\n"
    "Diagnose: {DIAGNOSIS}, Vorerkrankungen: {PREV_DIAGNOSIS}.\n"
    "Pflegehinweise: {IMPRESSION}.\n"
    "Telefon: {PHONE}, Adresse: {ADDRESS}."
)

reha_gutachten_template = (
    "{DOCUMENT_TYPE} – Antrag vom {DATE}.\n"
    "Patient: {PERSON}, geb. am {BIRTHDATE}, PID: {PID}, Beruf: {OCCUPATION}.\n"
    "Erkrankung: {DIAGNOSIS} ({ICD10_CODE} – {ICD10_DESC}), Symptome: {SYMPTOM}.\n"
    "Behandlung bisher: {TREATMENT}, Medikamente: {MEDICATION}.\n"
    "Familiäre Vorbelastung: {FAMHIST}.\n"
    "Sozialmedizinische Bewertung: {IMPRESSION}.\n"
    "Empfohlene Maßnahmen: {FOLLOWUP_REQ}, Grund: {FOLLOWUP_REASON}.\n"
    "Kontaktarzt: {DOCTOR}, Klinik: {ORG}, Tel: {PHONE}. \n"
    "Stationäre befindet sich der Patient im Zimmer {ROOM_NUMBER}."
)

complete_template = (

    "{DOCUMENT_TYPE}:\n Am {DATE} stellte sich der Patient {PERSON} ({GENDER}), {GROESSE} per {GEWICHT} geboren am {BIRTHDATE}\n"
    "Familienstand: {FAMILY_STATUS}, Symptome: {SYMPTOM}, Diagnose: {DIAGNOSIS}\n "
    "Beruf: {OCCUPATION}, Medikament: {MEDICATION}, Behandlung: {TREATMENT}, "
    "Durchgeführt von {DOCTOR} in der Abteilung {DEPARTMENT}  zimmer {ROOM_NUMBER}.\n"
    "Krankenhaus: {ORG}, {ADDRESS}, Tel: {PHONE}.\n"
    "{DOCUMENT_TYPE} vom {DATE}:\n"
    "Patient: {PERSON} ({GENDER}), geboren am {BIRTHDATE}, PID: {PID}.\n"
    "Adresse: {ADDRESS}, Telefon: {PHONE}.\n"
    "Familienstand: {FAMILY_STATUS}, Familienmitglied: {FAMILYMEMBER}, familiäre Vorgeschichte: {FAMHIST}.\n"
    "Abteilung: {DEPARTMENT}, Krankenhaus: {ORG}.\n"
    "Untersuchung durchgeführt von {DOCTOR} mit {DEVICE}.\n"
    "Diagnose: {DIAGNOSIS} (ICD-10: {ICD10_CODE} - {ICD10_DESC}).\n"
    "Vorherige Diagnose: {PREV_DIAGNOSIS}.\n"
    "Symptome: {SYMPTOM}.\n"
    "Befund: {FINDING}.\n"
    "Labordiagnostik: {LAB_RESULT}.\n"
    "Impression: {IMPRESSION}.\n"
    "Medikation: {MEDICATION}, Behandlung: {TREATMENT}.\n"
    "Verfahren/Prozedur: {PROCEDURE}.\n"
    "Risikofaktoren: {RISKFACTOR}.\n"
    "Impfungen: {IMMUNIZATION}.\n"
    "Lebensstil: {LIFESTYLE}.\n"
    "Vitalparameter: {VITALSIGNS}.\n"
    "Folgegrund: {FOLLOWUP_REASON}, Folgeanforderung: {FOLLOWUP_REQ}.\n"
    "Gewicht: {GEWICHT}, Größe: {GROESSE}.\n"
)


TEMPLATES_LIST =[complete_template ,reha_gutachten_template,ct_mrt_template,roentgen_template,ekg_template,
                 notfall_template,attest_template,hkp_template,aufnahmebogen_template,opfreigabe_template,pflegedoku_template,
                 therapieplan_template,rezept_template,impfpass_template,einwilligung_template,ueberweisung_template,patho_template,
                 radiologie_template,laborbericht_template,anamnesebogen_template,entlassungsbericht_template, operationsbericht_template,
                 befundbericht_template,arztbrief_template]