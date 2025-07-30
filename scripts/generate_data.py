# generate_data.py
import random
import json
import os
import re
import datetime
from config import LABEL2ID
from sklearn.model_selection import train_test_split
import simple_icd_10 as icd
from idc_api import fetch_icd_description,get_token

diagnosis_icd10_map = {
    "Hypertonie": "I10",
    "Diabetes Mellitus": "E11.9",
    "Asthma": "J45",
    "Pneumonie": "J18.9"
}

vitalsigns = [
    "Blutdruck 120/80 mmHg", "Puls 72/min", "Temperatur 37,2 °C",
    "Sauerstoffsättigung 98 %"
]

lifestyles = [
    "Nichtraucher", "Raucher (5 Zigaretten/Tag)", "gelegentlicher Alkoholgenuss",
    "regelmäßige Bewegung"
]

risk_factors = [
    "familiäre Vorbelastung Diabetes", "Adipositas BMI 32",
    "Hyperlipidämie", "Schlafapnoe"
]

# Names and other data
names = ["Herr. Max Müller", "Patientin: Anna Schmidt", "L. Weber", "Frau Sophie Fischer","Otto Kromberger",
         "John Smith", "Mary Jones", "Robert Lee", "Emily Davis"]
doctors = ["Dr. Müller", "Dr. Schneider", "Dr. Becker", "Dr. Weber","Dr. Suhle Nikolas", "Dr. Lehmann", "Dr. Fischer", "Dr. Weber"
           "Dr. Adams", "Dr. Lee", "Dr. Patel", "Dr. Chen"]


symptoms = ["Brustschmerzen", "Atemnot", "Fieber", "Müdigkeit","dumpfe Kopfschmerzen", "Sehstörung", "Sprachstörung", "Kribbeln im linken Arm"]
medications = ["Metformin", "Lisinopril", "Albuterol", "Amoxicillin","Ramipril 5mg", "Metformin", "Schlafmedikamente"]
treatments = ["Sauerstofftherapie", "Operation", "Chemotherapie", "Physiotherapie"]
lab_results = ["Hb 13.5 g/dL", "Blutzucker 110 mg/dL", "Cholesterin 200 mg/dL","Glukose: 110 mg/dL"]
allergies = ["Penicillin", "Pollen", "Nüsse"]
immunizations = ["Masern-Impfung", "Grippeimpfung"]
devices = ["Herzschrittmacher", "Insulinpumpe","Schlafmaske", "Blutdruckgerät"]
family_histories = ["Mutter mit Diabetes", "Vater mit Bluthochdruck"]
procedures = ["Angioplastie", "MRT-Scan", "Biopsie", "Ultraschall","CT Kopf", "Lyse-Therapie"]
departments = ["Kardiologie", "Notaufnahme", "Onkologie", "Radiologie","Neurologie", "Innere Medizin"]

hospital_names = ["St. Marien Krankenhaus", "Allgemeine Gesundheitsklinik",
                  "Städtisches Medizinzentrum", "Universitätsklinikum München"]
hospital_addresses = ["Hauptstraße 12, 80331 München", "Berliner Allee 45, 40212 Düsseldorf","Lindenstraße 8, 10115 Berlin", "Goetheplatz 9, 50674 Köln"]
hospital_phones = ["089 123456", "0211 987654", "030 234567", "0221 456789"]

followup_reasons = [
    "zur Blutdruckkontrolle", "wegen anhaltender Schmerzen", "zur Verlaufskontrolle"
]

impressions = [
    "Hinweis auf Pneumonie", "wahrscheinlich virale Ursache", "unklares Abdomen"
]

prev_diagnoses = [
    "frühere Appendizitis", "bekannte Arthrose", "chronische Bronchitis"
]
def __random_gender():
    return random.choice(["männlich", "weiblich", "divers"])


def __random_birthdate():
    start = datetime.date(1920, 1, 1)
    end = datetime.date(2025, 5, 31)
    rand_day = start + datetime.timedelta(days=random.randint(0, (end - start).days))
    return rand_day.strftime("%d.%m.%Y")


def __random_family_status():
    return random.choice(["ledig", "verheiratet", "geschieden", "verwitwet"])


def __random_date():
    start = datetime.date(2022, 1, 1)
    end = datetime.date(2024, 12, 31)
    rand_day = start + datetime.timedelta(days=random.randint(0, (end - start).days))
    return rand_day.strftime("%d. %B %Y")


# def generate_report(token =  None):
#     name = random.choice(names)
#     doctor = random.choice(doctors)
#     diagnosis = random.choice(list(diagnosis_icd10_map.keys()))
#     icd10_code = diagnosis_icd10_map[diagnosis]

#     icd_description = "Beschreibung unbekannt"
#     if token : 
#         icd_description = fetch_icd_description(icd10_code, token)
#         if not icd_description:
#             icd_description = icd.get_description(icd10_code)

#     else : 
#         icd_description = icd.get_description(icd10_code)
    


#     date = __random_date()
#     # Hospital
#     idx  = random.randint(0, len(hospital_names) - 1)
#     hospital_name, hospital_address, hospital_phone = hospital_names[idx ], hospital_addresses[idx ], hospital_phones[idx ]
#     gender = __random_gender()
#     birthdate = __random_birthdate()
#     family_status = __random_family_status()

#     vital = random.choice(vitalsigns) if random.choice([True, False]) else None
#     lifestyle = random.choice(lifestyles) if random.choice([True, False]) else None
#     riskfactor = random.choice(risk_factors) if random.choice([True, False]) else None

#     followup_reason = random.choice(followup_reasons) if random.random() < 0.5 else None
#     impression = random.choice(impressions) if random.random() < 0.5 else None
#     prev_diagnosis = random.choice(prev_diagnoses) if random.random() < 0.5 else None

#     # Add to entities if present
#     if followup_reason:
#         entities[followup_reason] = "FOLLOWUP_REASON"
#     if impression:
#         entities[impression] = "IMPRESSION"
#     if prev_diagnosis:
#         entities[prev_diagnosis] = "PREV_DIAGNOSIS"



#     # Follow-up
#     followup_times = ["in 2 Wochen", "in 4 Wochen", "in einem Monat", "in 10 Tagen", "in drei Wochen"]
#     followup_phrases = ["empfohlen", "dringend empfohlen", "zur weiteren Abklärung empfohlen"]
#     followup_sentence = f"Eine erneute Kontrolluntersuchung wird {random.choice(followup_times)} {random.choice(followup_phrases)}."

#     symptom = random.choice(symptoms)
#     medication = random.choice(medications)
#     treatment = random.choice(treatments)
#     procedure = random.choice(procedures)
#     department = random.choice(departments)
#     lab_result = random.choice(lab_results)
#     allergy = random.choice(allergies) if random.choice([True, False]) else None
#     immunization = random.choice(immunizations) if random.choice([True, False]) else None
#     device = random.choice(devices) if random.choice([True, False]) else None
#     family_history = random.choice(family_histories) if random.choice([True, False]) else None

#     # Entity dictionary
#     entities = {
#         name: "PERSON",
#         doctor: "DOCTOR",
#         date: "DATE",
#         diagnosis: "DIAGNOSIS",
#         symptom: "SYMPTOM",
#         medication: "MEDICATION",
#         treatment: "TREATMENT",
#         procedure: "PROCEDURE",
#         department: "DEPARTMENT",
#         hospital_name: "ORG",
#         hospital_address: "ADDRESS",
#         hospital_phone: "PHONE",
#         gender: "GENDER",
#         birthdate: "BIRTHDATE",
#         family_status: "FAMILY_STATUS",
#         icd10_code: "ICD10_CODE",
#         icd_description: "ICD10_DESC",
#     }


#   # Generate augmented sentence with spans
#     text, spans = generate_augmented_sentence_with_spans(entities, inject_noise_flag=True)
#     tokens, labels = __char_spans_to_bio_labels(text, spans, LABEL2ID)


#     general_templates = [
#          f"Am {date} stellte sich Patient {name} ({gender}), geboren am {birthdate}, Familienstand: {family_status} mit {symptom} vor. "
#         f"Diagnose: {diagnosis}. "
#         f"Vorherige Diagnose: {prev_diagnosis or 'keine bekannt'}. "
#         f"Impression: {impression or 'nicht dokumentiert'}. "
#         f"Behandlung: {medication} und {treatment}. Verfahren: {procedure}. "
#         f"Untersuchung durch {doctor} in der Abteilung {department}. "
#         f"Krankenhaus: {hospital_name}, {hospital_address}, Tel: {hospital_phone}. "
#         f"Labor: {lab_result}. "
#         f"Folgegrund: {followup_reason or 'keine Angabe'}. "
#         f"{followup_sentence}",
        
#         f"{name} kam am {date} ins {hospital_name}, {hospital_address}. Beschwerden: {symptom}. "
#         f"Untersuchung durch {doctor}. Diagnose: {diagnosis} (ICD‑10: {icd10_code} – {icd_description}). "
#         f"Vorherige Diagnose: {prev_diagnosis or 'keine bekannt'}. "
#         f"Impression: {impression or 'nicht dokumentiert'}. "
#         f"Verabreichtes Medikament: {medication}. Eingriff: {procedure}. "
#         f"Laborbefund: {lab_result}. Tel: {hospital_phone}. "
#         f"Folgegrund: {followup_reason or 'keine Angabe'}. {followup_sentence}",
        
#         f"Bei der Untersuchung am {date} im {hospital_name} wurde bei {name} {diagnosis} festgestellt. "
#         f"Symptome: {symptom}. Behandelt mit {medication} und {treatment}. "
#         f"Durchgeführt von {doctor} in der {department}. Labor: {lab_result}. "
#         f"Adresse: {hospital_address}, Kontakt: {hospital_phone}. "
#         f"Vorherige Diagnose: {prev_diagnosis or 'keine bekannt'}. "
#         f"Impression: {impression or 'nicht dokumentiert'}. "
#         f"Folgegrund: {followup_reason or 'keine Angabe'}. {followup_sentence}",
#     ]

#     structured_templates = [
#        f"--- RADIOLOGY REPORT ---\nPatient: {name}\nDatum: {date}\nVerfahren: {procedure}\n"
#         f"Indikation: {symptom}\nBefund: Zeichen einer {diagnosis}\nEmpfehlung: {treatment}\n"
#         f"Radiologe: {doctor}\nAbteilung: {department}\n{hospital_name}, {hospital_address}\nTelefon: {hospital_phone}\n"
#         f"Vorherige Diagnose: {prev_diagnosis or 'keine bekannt'}\nImpression: {impression or 'nicht dokumentiert'}\n"
#         f"Folgegrund: {followup_reason or 'keine Angabe'}\n{followup_sentence}",

#         f"--- FOLLOW-UP VISIT ---\nDatum: {date}\nPatient: {name}\nGrund: Nachuntersuchung wegen {symptom}\n"
#         f"Vorherige Diagnose: {prev_diagnosis or 'keine bekannt'}\nImpression: {impression or 'nicht dokumentiert'}\n"
#         f"Diagnose: {diagnosis} (ICD‑10: {icd10_code} – {icd_description})..\nAktueller Zustand stabil\n"
#         f"Medikation: {medication}\nTherapie: {treatment}\nBehandelnder Arzt: {doctor}\n"
#         f"Abteilung: {department}\nKlinik: {hospital_name}\nAdresse: {hospital_address}\nTelefon: {hospital_phone}\n"
#         f"Folgegrund: {followup_reason or 'keine Angabe'}\n{followup_sentence}",

#         f"--- Entlassungsbrief---\nPatient: {name}\nAufnahme: {date}\nKlinik: {hospital_name}\nAbteilung: {department}\n"
#         f"Hauptdiagnose: {diagnosis}\nBeschwerden bei Aufnahme: {symptom}\nBehandlung: {medication} und {treatment}\n"
#         f"Eingriff: {procedure}\nVerantwortlicher Arzt: {doctor}\nEntlassung in stabilem Zustand\n"
#         f"Kontrolluntersuchung empfohlen\nVorherige Diagnose: {prev_diagnosis or 'keine bekannt'}\n"
#         f"Impression: {impression or 'nicht dokumentiert'}\nFolgegrund: {followup_reason or 'keine Angabe'}\n"
#         f"Kontakt: {hospital_phone}\n{followup_sentence}",

#         f"--- FOLLOW-UP RECOMMENDATION ---\nPatient: {name} ({gender}), geboren am {birthdate}, Familienstand: {family_status}.\n"
#         f"Datum der letzten Untersuchung: {date}.\nBeschwerden: {symptom}. Diagnose: {diagnosis}.\n"
#         f"Behandlung: {treatment} mit {medication}. Durchgeführt von {doctor}.\n"
#         f"Empfehlung: {followup_sentence}\nBitte melden Sie sich bei der Abteilung {department} im {hospital_name}.\n"
#         f"Adresse: {hospital_address}. Tel: {hospital_phone}.\n"
#         f"Vorherige Diagnose: {prev_diagnosis or 'keine bekannt'}\nImpression: {impression or 'nicht dokumentiert'}\n"
#         f"Folgegrund: {followup_reason or 'keine Angabe'}"
#     ]

#     def add_optionals(tmpl_list):
#         new_list = []
#         for t in tmpl_list:
#             if allergy:
#                 t += f"\nAllergien: {allergy}."
#             if immunization:
#                 t += f"\nImpfungen: {immunization}."
#             if device:
#                 t += f"\nMedizinisches Gerät: {device}."
#             if family_history:
#                 t += f"\nFamilienanamnese: {family_history}."

#             if vital:
#                 t += f"\nVitalzeichen: {vital}."
#             if lifestyle:
#                 t += f"\nLebensstil: {lifestyle}."
#             if riskfactor:
#                 t += f"\nRisikofaktor: {riskfactor}."

#             new_list.append(t)
#         return new_list

#     # templates = add_optionals(general_templates + structured_templates)
#     # text = random.choice(templates)



   
#     # Optional: blend with one of the structured templates
#     templates = add_optionals(general_templates + structured_templates)
#     fallback_sentence = random.choice(templates)

#     # Mix structured and augmented text 50/50
#     if random.random() < 0.5:
#         text = fallback_sentence
#     else:
#         text = augmented_sentence






#     if allergy: entities[allergy] = "ALLERGY"
#     if immunization: entities[immunization] = "IMMUNIZATION"
#     if device: entities[device] = "DEVICE"
#     if family_history: entities[family_history] = "FAMILY_HISTORY"
#     if vital:
#         entities[vital] = "VITALSIGNS"
#     if lifestyle:
#         entities[lifestyle] = "LIFESTYLE"
#     if riskfactor:
#         entities[riskfactor] = "RISKFACTOR"
#     if followup_reason:
#         entities[followup_reason] = "FOLLOWUP_REASON"
#     if impression:
#         entities[impression] = "IMPRESSION"
#     if prev_diagnosis:
#         entities[prev_diagnosis] = "PREV_DIAGNOSIS"


#     match = re.search(r"(Eine erneute Kontrolluntersuchung wird .*? empfohlen)", text)
#     if match:
#         entities[match.group(1)] = "FOLLOWUP_RECOMMENDATION"

#     return text, entities


def generate_report(token=None):
    # Select core patient data
    name = random.choice(names)
    doctor = random.choice(doctors)
    diagnosis = random.choice(list(diagnosis_icd10_map.keys()))
    icd10_code = diagnosis_icd10_map[diagnosis]

    icd_description = icd.get_description(icd10_code) if not token else fetch_icd_description(icd10_code, token) or icd.get_description(icd10_code)

    date = __random_date()
    idx = random.randint(0, len(hospital_names) - 1)
    hospital_name, hospital_address, hospital_phone = hospital_names[idx], hospital_addresses[idx], hospital_phones[idx]
    gender = __random_gender()
    birthdate = __random_birthdate()
    family_status = __random_family_status()

    symptom = random.choice(symptoms)
    medication = random.choice(medications)
    treatment = random.choice(treatments)
    procedure = random.choice(procedures)
    department = random.choice(departments)
    lab_result = random.choice(lab_results)

    followup_times = ["in 2 Wochen", "in 4 Wochen", "in einem Monat", "in 10 Tagen", "in drei Wochen"]
    followup_phrases = ["empfohlen", "dringend empfohlen", "zur weiteren Abklärung empfohlen"]
    followup_sentence = f"Eine erneute Kontrolluntersuchung wird {random.choice(followup_times)} {random.choice(followup_phrases)}."

    allergy = random.choice(allergies) if random.choice([True, False]) else None
    immunization = random.choice(immunizations) if random.choice([True, False]) else None
    device = random.choice(devices) if random.choice([True, False]) else None
    family_history = random.choice(family_histories) if random.choice([True, False]) else None
    vital = random.choice(vitalsigns) if random.choice([True, False]) else None
    lifestyle = random.choice(lifestyles) if random.choice([True, False]) else None
    riskfactor = random.choice(risk_factors) if random.choice([True, False]) else None

    # Build entity dictionary
    entities = {
        name: "PERSON",
        doctor: "DOCTOR",
        date: "DATE",
        diagnosis: "DIAGNOSIS",
        symptom: "SYMPTOM",
        medication: "MEDICATION",
        treatment: "TREATMENT",
        procedure: "PROCEDURE",
        department: "DEPARTMENT",
        hospital_name: "ORG",
        hospital_address: "ADDRESS",
        hospital_phone: "PHONE",
        gender: "GENDER",
        birthdate: "BIRTHDATE",
        family_status: "FAMILY_STATUS",
        icd10_code: "ICD10_CODE",
        icd_description: "ICD10_DESC",
    }

    if allergy: entities[allergy] = "ALLERGY"
    if immunization: entities[immunization] = "IMMUNIZATION"
    if device: entities[device] = "DEVICE"
    if family_history: entities[family_history] = "FAMILY_HISTORY"
    if vital: entities[vital] = "VITALSIGNS"
    if lifestyle: entities[lifestyle] = "LIFESTYLE"
    if riskfactor: entities[riskfactor] = "RISKFACTOR"
    if followup_sentence: entities[followup_sentence] = "FOLLOWUP_RECOMMENDATION"

    # Define your templates
    general_templates = [
        f"Am {date} stellte sich Patient {name} ({gender}), geboren am {birthdate}, Familienstand: {family_status} mit {symptom} vor. Diagnose: {diagnosis}. "
        f"Behandlung: {medication} und {treatment}. Verfahren: {procedure}. "
        f"Untersuchung durch {doctor} in der Abteilung {department}. "
        f"Krankenhaus: {hospital_name}, {hospital_address}, Tel: {hospital_phone}. "
        f"Labor: {lab_result}. {followup_sentence}"
    ]

    structured_templates = [
        f"--- FOLLOW-UP ---\nDatum: {date}\nPatient: {name}\nGrund: Nachuntersuchung wegen {symptom}\n"
        f"Diagnose: {diagnosis} (ICD-10: {icd10_code} – {icd_description})\n"
        f"Medikation: {medication}\nBehandlung: {treatment}\n"
        f"Abteilung: {department}, Arzt: {doctor}\n"
        f"Ort: {hospital_name}, {hospital_address}, Tel: {hospital_phone}.\n{followup_sentence}"
    ]
    followup_reason = random.choice(followup_reasons) if random.random() < 0.5 else None
    impression = random.choice(impressions) if random.random() < 0.5 else None
    prev_diagnosis = random.choice(prev_diagnoses) if random.random() < 0.5 else None
    general_templates = [
         f"Am {date} stellte sich Patient {name} ({gender}), geboren am {birthdate}, Familienstand: {family_status} mit {symptom} vor. "
        f"Diagnose: {diagnosis}. "
        f"Vorherige Diagnose: {prev_diagnosis or 'keine bekannt'}. "
        f"Impression: {impression or 'nicht dokumentiert'}. "
        f"Behandlung: {medication} und {treatment}. Verfahren: {procedure}. "
        f"Untersuchung durch {doctor} in der Abteilung {department}. "
        f"Krankenhaus: {hospital_name}, {hospital_address}, Tel: {hospital_phone}. "
        f"Labor: {lab_result}. "
        f"Folgegrund: {followup_reason or 'keine Angabe'}. "
        f"{followup_sentence}",
        
        f"{name} kam am {date} ins {hospital_name}, {hospital_address}. Beschwerden: {symptom}. "
        f"Untersuchung durch {doctor}. Diagnose: {diagnosis} (ICD‑10: {icd10_code} – {icd_description}). "
        f"Vorherige Diagnose: {prev_diagnosis or 'keine bekannt'}. "
        f"Impression: {impression or 'nicht dokumentiert'}. "
        f"Verabreichtes Medikament: {medication}. Eingriff: {procedure}. "
        f"Laborbefund: {lab_result}. Tel: {hospital_phone}. "
        f"Folgegrund: {followup_reason or 'keine Angabe'}. {followup_sentence}",
        
        f"Bei der Untersuchung am {date} im {hospital_name} wurde bei {name} {diagnosis} festgestellt. "
        f"Symptome: {symptom}. Behandelt mit {medication} und {treatment}. "
        f"Durchgeführt von {doctor} in der {department}. Labor: {lab_result}. "
        f"Adresse: {hospital_address}, Kontakt: {hospital_phone}. "
        f"Vorherige Diagnose: {prev_diagnosis or 'keine bekannt'}. "
        f"Impression: {impression or 'nicht dokumentiert'}. "
        f"Folgegrund: {followup_reason or 'keine Angabe'}. {followup_sentence}",
    ]

    structured_templates = [
       f"--- RADIOLOGY REPORT ---\nPatient: {name}\nDatum: {date}\nVerfahren: {procedure}\n"
        f"Indikation: {symptom}\nBefund: Zeichen einer {diagnosis}\nEmpfehlung: {treatment}\n"
        f"Radiologe: {doctor}\nAbteilung: {department}\n{hospital_name}, {hospital_address}\nTelefon: {hospital_phone}\n"
        f"Vorherige Diagnose: {prev_diagnosis or 'keine bekannt'}\nImpression: {impression or 'nicht dokumentiert'}\n"
        f"Folgegrund: {followup_reason or 'keine Angabe'}\n{followup_sentence}",

        f"--- FOLLOW-UP VISIT ---\nDatum: {date}\nPatient: {name}\nGrund: Nachuntersuchung wegen {symptom}\n"
        f"Vorherige Diagnose: {prev_diagnosis or 'keine bekannt'}\nImpression: {impression or 'nicht dokumentiert'}\n"
        f"Diagnose: {diagnosis} (ICD‑10: {icd10_code} – {icd_description})..\nAktueller Zustand stabil\n"
        f"Medikation: {medication}\nTherapie: {treatment}\nBehandelnder Arzt: {doctor}\n"
        f"Abteilung: {department}\nKlinik: {hospital_name}\nAdresse: {hospital_address}\nTelefon: {hospital_phone}\n"
        f"Folgegrund: {followup_reason or 'keine Angabe'}\n{followup_sentence}",

        f"--- Entlassungsbrief---\nPatient: {name}\nAufnahme: {date}\nKlinik: {hospital_name}\nAbteilung: {department}\n"
        f"Hauptdiagnose: {diagnosis}\nBeschwerden bei Aufnahme: {symptom}\nBehandlung: {medication} und {treatment}\n"
        f"Eingriff: {procedure}\nVerantwortlicher Arzt: {doctor}\nEntlassung in stabilem Zustand\n"
        f"Kontrolluntersuchung empfohlen\nVorherige Diagnose: {prev_diagnosis or 'keine bekannt'}\n"
        f"Impression: {impression or 'nicht dokumentiert'}\nFolgegrund: {followup_reason or 'keine Angabe'}\n"
        f"Kontakt: {hospital_phone}\n{followup_sentence}",

        f"--- FOLLOW-UP RECOMMENDATION ---\nPatient: {name} ({gender}), geboren am {birthdate}, Familienstand: {family_status}.\n"
        f"Datum der letzten Untersuchung: {date}.\nBeschwerden: {symptom}. Diagnose: {diagnosis}.\n"
        f"Behandlung: {treatment} mit {medication}. Durchgeführt von {doctor}.\n"
        f"Empfehlung: {followup_sentence}\nBitte melden Sie sich bei der Abteilung {department} im {hospital_name}.\n"
        f"Adresse: {hospital_address}. Tel: {hospital_phone}.\n"
        f"Vorherige Diagnose: {prev_diagnosis or 'keine bekannt'}\nImpression: {impression or 'nicht dokumentiert'}\n"
        f"Folgegrund: {followup_reason or 'keine Angabe'}"
    ]


    real_template =[
            f"Patientenname : {name}\n\n"

            f"Geburtsdatum : {birthdate}\n\n"

            f"Gewicht: {random.choice([30, 140])} Kg\n\n"

            f"Große: {random.choice([120, 200])} cm\n\n\n"

            f"Hausarzt : {doctor}.\n\n\n"

            f"Der Patient, {name} , stellte sich mit stark anhaltend dumpfen {symptom} vor, die er seit gestern habe. Herr {name} sei auch niedergeschlagen. Darüber hinaus berichte er über Kribbeln auf der linke Arm. Er habe auch berichtet, dass er eine Sehstörung und Sprachstörung (Wortfindungsstörung und lallende Ansprache) entwickelt habe. Eine Schluckstörung wurde auch berichtet.\n"

            f"Vorerkrankungen : Er habe seit 20 Jahren Bluthochdruck.IM Jahr 2018 habe er einen Rippenbruch gehabt, den konservativ behandelt wurde.\n"

            f"Vegetative Anamnese ist bis auf eine Schlafstörung, die seit 5 jähren bestehe und mit Schlafmedikamente eingestellt sei, unauffällig.\n"

            f"Medikamente Anamnese : Er nehme die obergenannte Schlafmedikamente bei bedarf ein und er nehme auch Ramipril 5mg einmal morgens ein.\n"

            f"Noxen : Er habe täglich für 10 Jahren zehn Zigaretten geraucht , bevor er sich das Rauchen abgewöhnt habe. Alkohol trinke er nicht. Die Frage nach einem Drogenmissbrauch wurde verneint.\n"

            f"Soziale Anamnese : Er ist Gärtner von Beruf und ist verheiratet. Herr {name} lebe mit seiner Ehefrau und vier Kinder zusammen.\n"

            f"Familiäre Anamnese : Die Mutter des Patienten leide an Zuckerkrankheit und der Vater habe einen Schlaganfall hinter sich.\n"

            f"Die Anamnese, Laborwerte und eine CT Kopf weisen auf einen Schlaganfall hin. Lyse-therapie wurde nach der CT begonnen.\n"


    ]




    # Generate text from template or augmented sentence
    if random.random() < 0.5:
        # Paraphrased version
        text, spans = __generate_augmented_sentence_with_spans(entities)
        tokens, labels = __char_spans_to_bio_labels(text, spans, LABEL2ID)
    else:
        # Use structured template
        template = random.choice(general_templates + structured_templates + real_template)
        # Optional field appending
        optional_fields = []
        if allergy: optional_fields.append(f"Allergien: {allergy}.")
        if immunization: optional_fields.append(f"Impfung: {immunization}.")
        if device: optional_fields.append(f"Gerät: {device}.")
        if family_history: optional_fields.append(f"Familienanamnese: {family_history}.")
        if vital: optional_fields.append(f"Vitalzeichen: {vital}.")
        if lifestyle: optional_fields.append(f"Lebensstil: {lifestyle}.")
        if riskfactor: optional_fields.append(f"Risikofaktor: {riskfactor}.")
        if optional_fields:
            template += "\n" + " ".join(optional_fields)

        text = template
        tokens, labels = __tokenize_and_label(text, entities)

    return text, entities, tokens, labels


def __simple_tokenize(text):
    return re.findall(r"\w+|[^\w\s]", text, re.UNICODE)

def __inject_noise(text, typo_prob=0.05, punctuation_prob=0.05):
    def random_typo(word):
        if len(word) > 3 and random.random() < typo_prob:
            i = random.randint(1, len(word) - 2)
            return word[:i] + word[i+1] + word[i] + word[i+2:]
        return word

    def corrupt_punctuation(t):
        if random.random() < punctuation_prob:
            return t.replace(".", "") if "." in t else t + "."
        return t

    words = text.split()
    noisy_words = [random_typo(word) for word in words]
    noisy_text = " ".join(noisy_words)
    noisy_text = corrupt_punctuation(noisy_text)
    return noisy_text

def __char_spans_to_bio_labels(text, spans, label_map):
    """
    Convert character spans to BIO labels aligned with tokenized text.
    
    Args:
        text (str): The generated sentence.
        spans (list): List of tuples (start_char, end_char, entity_type).
        label_map (dict): Mapping from BIO labels (like 'B-DIAGNOSIS') to IDs.
        
    Returns:
        tokens (list of str)
        bio_labels (list of int)  # label IDs aligned with tokens
    """

    # Simple tokenization (keep punctuation separate)
    tokens = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)
    
    # Track char position for each token
    token_positions = []
    pos = 0
    for token in tokens:
        start = text.find(token, pos)
        end = start + len(token)
        token_positions.append((start, end))
        pos = end

    # Initialize labels to "O"
    bio_labels = ["O"] * len(tokens)

    for start_char, end_char, ent_type in spans:
        # Assign B- and I- labels for tokens within the span
        # Find all tokens that fall inside this char span
        inside_tokens = []
        for i, (tok_start, tok_end) in enumerate(token_positions):
            # Check if token overlaps with entity span
            if tok_start >= start_char and tok_end <= end_char:
                inside_tokens.append(i)

        if not inside_tokens:
            continue  # no tokens matched? skip

        # Assign labels
        bio_labels[inside_tokens[0]] = f"B-{ent_type}"
        for idx in inside_tokens[1:]:
            bio_labels[idx] = f"I-{ent_type}"

    # Convert label strings to IDs
    label_ids = [label_map.get(lbl, 0) for lbl in bio_labels]

    return tokens, label_ids

def __paraphrase_entity(entity_type, value):
    variations = {
        "DIAGNOSIS": [
            f"es wurde {value} diagnostiziert",
            f"Diagnose: {value}",
            f"leidet an {value}",
            f"{value} wurde festgestellt"
        ],
        "MEDICATION": [
            f"bekommt {value}",
            f"Therapie mit {value}",
            f"{value} wurde verabreicht",
            f"Medikation: {value}"
        ],
        "SYMPTOM": [
            f"klagt über {value}",
            f"hat {value}",
            f"{value} wurde berichtet",
            f"zeigt Symptome von {value}"
        ],
        "DOCTOR": [
            f"behandelt durch {value}",
            f"untersucht von {value}",
            f"{value} führte die Untersuchung durch",
            f"Arzt: {value}"
        ],
        "PERSON": [
            f"Patient: {value}",
            f"Name: {value}",
            f"{value} stellte sich vor",
            f"Betroffene Person: {value}"
        ],
        "ORG": [
            f"im Krankenhaus {value}",
            f"Einrichtung: {value}",
            f"im {value}",
            f"Klinik: {value}"
        ],
        "DATE": [
            f"am {value}",
            f"Datum: {value}",
            f"am Untersuchungsdatum {value}",
            f"Datum des Berichts: {value}"
        ],
        # add more as needed
    }
    if entity_type in variations:
        return random.choice(variations[entity_type])
    return value
import re

def __generate_augmented_sentence_with_spans(entities, inject_noise_flag=True):
    """
    Generate a coherent sentence from entities, return text and entity spans.
    
    entities: dict of {entity_text: entity_type}
    
    Returns:
        text: generated sentence (string)
        spans: list of tuples (start_char, end_char, entity_type)
    """

    # Define a logical order for entity types for better flow
    order = ['PERSON', 'SYMPTOM', 'DIAGNOSIS', 'MEDICATION', 'TREATMENT', 'DOCTOR', 'ORG', 'DATE']

    pieces = []
    spans = []
    current_pos = 0

    def safe_inject_noise(text):
        if inject_noise_flag:
            return __inject_noise(text)
        return text

    # Helper to add phrase and track span
    def add_phrase(phrase, ent_type):
        nonlocal current_pos
        start = current_pos
        pieces.append(phrase)
        current_pos += len(phrase)
        end = current_pos
        spans.append((start, end, ent_type))
        # add space after phrase except last
        pieces.append(" ")
        current_pos += 1

    # Compose sentence piecewise in order
    for ent_type in order:
        for value, etype in entities.items():
            if etype == ent_type:
                phrase = __paraphrase_entity(ent_type, value)
                phrase = safe_inject_noise(phrase)
                add_phrase(phrase, ent_type)

    # Join pieces, strip trailing space
    text = "".join(pieces).strip()

    # Fix trailing punctuation (optional)
    if not text.endswith("."):
        text += "."

    return text, spans


def __tokenize_and_label(text, entities):
    tokens = __simple_tokenize(text)
    labels = ["O"] * len(tokens)

    for entity_text, ent_type in entities.items():
        ent_tokens = __simple_tokenize(entity_text)
        n = len(ent_tokens)
        for i in range(len(tokens) - n + 1):
            # Case-insensitive check
            if [t.lower() for t in tokens[i:i+n]] == [t.lower() for t in ent_tokens]:
                # Avoid overwriting existing labels if needed:
                if labels[i] == "O":
                    labels[i] = f"B-{ent_type}"
                    for j in range(1, n):
                        labels[i+j] = f"I-{ent_type}"
                # Remove 'break' to label all occurrences
                # break  

    label_ids = [LABEL2ID.get(label, 0) for label in labels]
    return tokens, label_ids

def __simple_tokenize(text):
    return re.findall(r"\w+|[^\w\s]", text, re.UNICODE)


def __save_reports_as_txt(text, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)

def __analyze_labels(dataset):
    from collections import Counter
    all_labels = [LABEL2ID[label] for item in dataset for label in item["ner_tags"] if label != 0]
    inv = {v: k for k, v in LABEL2ID.items()}
    counts = Counter(all_labels)
    print("\n📊 Label distribution:")
    for label_id, count in counts.most_common():
        print(f"{inv[label_id]:<30} {count}")
def generate_dataset(n_samples=1000, save_report=False):

    ClientId = "db7c330e-8d75-450c-976c-e891ea61cf6a_8ba7953b-b758-4b5c-9f11-82eeff251802"
    ClientSecret = "3jf/LfXf6qsEE9la9/q8Hm3Jt4GAaVh2Vth06qQeSaY="
    #token = get_token(client_id= ClientId, client_secret= ClientSecret)
    data = []
    for i in range(n_samples):
        text, entities, tokens, labels = generate_report(token=None)

        if save_report:
            filename = f"./txt_reports/report_{i+1}.txt"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            __save_reports_as_txt(text, filename)

        data.append({
            "tokens": tokens,
            "ner_tags": labels
        })

    # Split train/val
    train, val = train_test_split(data, test_size=0.1, random_state=42)
    
    os.makedirs("./data", exist_ok=True)

    with open("./data/train.json", "w", encoding="utf-8") as f:
        json.dump(train, f, indent=2, ensure_ascii=False)
    with open("./data/val.json", "w", encoding="utf-8") as f:
        json.dump(val, f, indent=2, ensure_ascii=False)

    print("✅ Synthetic dataset generated:")
    print(f"→ ./data/train.json ({len(train)} samples)")
    print(f"→ ./data/val.json ({len(val)} samples)")
    if save_report:
        print(f"→ ./txt_reports/ ({n_samples} samples)")



if __name__ == "__main__":
    generate_dataset(n_samples=10,save_report=True)
