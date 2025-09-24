import random
import re
def paraphrase_hospital_stay(entities):
    admission = entities.get("ADMISSION_DATE")
    discharge = entities.get("DISCHARGE_DATE")
    stay_reason = entities.get("STAY_REASON")
    if not (admission or discharge or stay_reason):
        return ""
    
    templates = [
        "Aufenthalt im Krankenhaus vom {admission} bis {discharge}.",
        "Der Krankenhausaufenthalt dauerte vom {admission} bis {discharge}.",
        "Patient wurde am {admission} aufgenommen und am {discharge} entlassen.",
        "Grund des Krankenhausaufenthalts: {stay_reason}.",
        "Er/Sie wird staionär wegen {stay_reason} bis {discharge}",
        "Krankenhausaufenthalt wegen {stay_reason} vom {admission} bis {discharge}.",
        "Aufgenommen am {admission}, entlassen am {discharge} aufgrund von {stay_reason}.",
    ]

    possible_templates = []

    if admission and discharge and stay_reason:
        possible_templates = [
            "Krankenhausaufenthalt wegen {stay_reason} vom {admission} bis {discharge}.",
            "Aufgenommen am {admission}, entlassen am {discharge} aufgrund von {stay_reason}.",
        ]
    elif admission and discharge:
        possible_templates = [
            "Aufenthalt im Krankenhaus vom {admission} bis {discharge}.",
            "Der Krankenhausaufenthalt dauerte vom {admission} bis {discharge}.",
            "Patient wurde am {admission} aufgenommen und am {discharge} entlassen.",
        ]
    elif stay_reason:
        possible_templates = [
            "Grund des Krankenhausaufenthalts: {stay_reason}.",
        ]
    else:
        possible_templates = templates

    template = random.choice(possible_templates)

    return template.format(
        admission=admission or "",
        discharge=discharge or "",
        stay_reason=stay_reason or "",
    ).strip()


def paraphrase_medication_combination(entities):
    """
    Combine MEDICATION + DOSAGE + ROUTE + FREQUENCY + DURATION 
    
    """
    medication = entities.get("MEDICATION")
    dosage = entities.get("DOSAGE")
    route = entities.get("ROUTE")
    frequency = entities.get("FREQUENCY")
    duration = entities.get("DURATION")

    if not medication:
        return None

    # Simplke sentence if only medication is present
    if not any([dosage, route, frequency, duration]):
        return f"Behandlung mit {medication}"

    templates = [
        "Therapie mit {medication}, {dosage}, {route}, {frequency} für {duration}.",
        "{medication} wurde {route} in einer Dosis von {dosage} verabreicht – {frequency} über {duration}.",
        "Verordnung: {medication} {dosage}, {frequency}, Applikation: {route}, Dauer: {duration}.",
        "Behandlung mit {medication} ({dosage}), {route}, {frequency}, geplant für {duration}.",
    ]

    
    template = random.choice(templates)
    phrase = template.format(
        medication=medication or "",
        dosage=dosage or "",
        route=route or "",
        frequency=frequency or "",
        duration=duration or "",
    )

    # remove commas if not necessary (z.B. ", ,", ", .", "  ")
    phrase = re.sub(r'\s+,', ',', phrase)  # Leerzeichen vor Komma entfernen
    phrase = re.sub(r',\s*,', ',', phrase) # Mehrfache Komma reduzieren
    phrase = re.sub(r',\s*\.', '.', phrase) # Komma vor Punkt entfernen
    phrase = re.sub(r'\s{2,}', ' ', phrase) # Mehrfache Leerzeichen auf eins reduzieren
    phrase = phrase.strip()

    if phrase.endswith(','):
        phrase = phrase[:-1] + '.'
    return phrase

def paraphrase_entity(entity_type, value):
    """
    Create a paraphrase by given entity, with given value
    Neetds to be checked... 
    """
    variations = {      
        "ADDRESS": [
            f"Anschrift: {value}",
            f"Adresse: {value}",
            ],

       "ADDRESS_PATIENT": [
            f"wohnhaft in {value}",
            f"Adresse: {value}",
            f"anschriftlich erreichbar unter {value}",
            f"Wohnadresse: {value}",
            f"zu finden in {value}",
            f"gemeldet unter {value}"
            ],


        "ADMISSION_DATE": [
            f"Aufnahme am {value}",
            f"Patient wurde aufgenommen am {value}",
            f"Datum der Einweisung: {value}"
            ],

        "ALCOHOL_CONSUMPTION": [
            f"Alkoholkonsum: {value}",
            f"er/sie konsumiert {value}",
            f"Trinkverhalten: {value}"
            ],

        "ALLERGY":[
            f"allergisch auf: {value}",
            f"bekannte Allergien: {value}",
            f"Allergien: {value}",
            f"verträgt {value} nicht",
            f"zeigt Allergien gegen {value}",
            f"Allergische Reaktion auf {value} dokumentiert"
            ],

        "ANAMNESE": [
            f"Anamnese: {value}",
            f"Vegetative Anamnese zeigt: {value}",
            f"Aus der Anamnese geht hervor: {value}",
            f"Der Patient berichtet über {value}",
            f"Vorgeschichte des Patienten: {value}",
            f"Anamnestisch auffällig: {value}",
            f"In der medizinischen Anamnese: {value}",
            f"{value} wurde anamnestisch erhoben",
            f"Anamnestisch wurden {value} beschrieben",
            f"Anamnestisch relevante Angabe: {value}",
            f"Medikamente Anamnese : {value}",
            f"Soziale Anamnese: {value}",
            f"Familiäre Anamnese: {value}"
            ],


        "BIRTHDATE":[
            f"geboren am: {value}",
            f"Geburtsdatum: {value}",
            f"Der Geburtstag ist der {value}",
            f"Geboren wurde am {value}"
            ],

        "BLOOD_TYPE": [
            f"Blutgruppe: {value}",
            f"hat Blutgruppe {value}",
            f"Bluttyp: {value}"
            ],

        "BODY_PART": [
            f"betroffene Region: {value}",
            f"lokalisiert an: {value}",
            f"Körperteil: {value}"
            ],

        "COURSE": [
            f"Verlauf: {value}",
            f"klinischer Verlauf war {value}",
            f"der Krankheitsverlauf zeigt {value}"
            ],

        "DATE": [
            f"am {value}",
            f"Datum: {value}",
            f"am Untersuchungsdatum {value}",
            f"Datum des Berichts: {value}"
            ],

        "DEVICE":[
            f"es wird empfohlen {value} zu verwenden",
            f"{value} wird verwendet",
            f"eingesetzt wird {value}",
            f"als Gerät kommt {value} zum Einsatz",
            f"verwendetes Gerät: {value}",
            f"zur Anwendung gelangt {value}",
            f"{value} kam zum Einsatz",
            f"benutzt wurde {value}",
            f"eingesetztes Gerät: {value}",
            f"verwendetes medizinisches Gerät: {value}",
            f"technisch unterstützt durch {value}",
            f"{value} wurde zur Untersuchung verwendet"
            ],

        "DEPARTMENT": [
            f"Abteilung: {value}",
            f"Fachbereich: {value}",
            f"medizinische Einheit: {value}",
            f"zugewiesen an die Abteilung {value}",
            f"{value}-Abteilung"
            ],

        "DIAGNOSIS": [
            f"es wurde {value} diagnostiziert",
            f"Diagnose: {value}",
            f"leidet an {value}",
            f"{value} wurde festgestellt",
            f"klinischer Befund: {value}",
            f"es besteht der Verdacht auf {value}",
            f"diagnostischer Hinweis: {value}",
            f"festgestellt wurde {value}",
            f"es handelt sich um {value}",
            f"medizinische Diagnose: {value}"
            ],
       
        "DISCHARGE_DATE": [
            f"Entlassen am {value}",
            f"Entlassdatum: {value}",
            f"Datum der Entlassung: {value}"
            ],

        "DOCTOR": [
            f"behandelt durch {value}",
            f"untersucht von {value}",
            f"{value} führte die Untersuchung durch",
            f"Arzt: {value}",
            f"medizinisch betreut von {value}",
            f"{value} als behandelnder Arzt",
            f"unter der Aufsicht von {value} ",
            f"{value} hat die Behandlung übernommen"
            ],

        "DOCUMENT_TYPE": [
            f"Berichtstyp: {value}",
            f"Dokument: {value}",
            f"Art des Dokuments: {value}",
            f"{value} liegt vor",
            f"Typ: {value}",
            f"es handelt sich um einen {value}"
            ],

        "DOSAGE": [
            f"Dosierung: {value}",
            f"verabreichte Menge: {value}",
            f"{value} wurde gegeben"
            ],

        "DURATION": [
            f"über einen Zeitraum von {value}",
            f"Dauer: {value}",
            f"Behandlungsdauer betrug {value}"
            ],

        "FAMILY_STATUS":[
                f"Familienstand: {value}",
                f"Er ist {value}",
                f"Der Familienstatus lautet {value}",
                f"Status in der Familie: {value}",
                f"Familienverhältnis: {value}"
                ],

        "FAMILYMEMBER":[
                f"begleitet von {value}",
                f"bei sich hat {value}",
                f"{value} ist als Begleitung dabei",
                f"Anwesend ist {value}",
                f"Mit dabei: {value}"
                ],

        "FAMHIST":[
                f"in der Familie gab es schon Fälle mit {value}",
                f"Familienanamnese: {value}",
                f"familiäre Häufung von {value} bekannt",
                f"familiäre Vorbelastung mit {value}",
                f"es liegen familiäre Fälle von {value} vor",
                f"familiäre Erkrankung: {value}",
                f"in der Verwandtschaft tritt {value} auf"
                ],

        "FINDING": [
                f"Befund: {value}",
                f"es zeigte sich {value}",
                f"untersucht wurde: {value}",
                f"beobachtet wurde {value}",
                f"{value} trat auf",
                f"nachgewiesen: {value}",
                f"diagnostischer Befund: {value}"
                ],

        "FOLLOWUP_REASON": [
                f"Grund für die Nachsorge: {value}",
                f"Folgegrund: {value}",
                f"Nachsorge erforderlich wegen {value}",
                f"{value} als Anlass für Nachkontrolle",
                f"{value} wurde als Folgegrund angegeben"
                ],

        "FOLLOWUP_REQ": [
                f"Folgeanforderung: {value}",
                f"weiteres Vorgehen: {value}",
                f"empfohlene Maßnahme: {value}",
                f"{value} soll durchgeführt werden",
                f"{value} wurde als nächste Maßnahme geplant"
                ],

        "FREQUENCY": [
                f"Häufigkeit: {value}",
                f"{value} verabreicht",
                f"Verabreichung {value}"
                ],

        "GEWICHT":[
                f"wiegt: {value}",
                f"er/sie wiegt {value}",
                f"das Gewicht beträgt {value}",
                f"das Körpergewicht liegt bei {value}",
                f"Gewicht: {value}",
                f"Gewicht : {value}"
                ],

        "GROESSE":[
                f"Größe: {value}",
                f"Größe : {value}",
                f"er/sie ist {value} groß",
                f"die Körpergröße beträgt {value}",
                f"die Größe ist {value}",
                f"die Körpergröße liegt bei {value}"
                ],

        "HOSPITAL_STAY": [
                f"Aufenthaltsdauer: {value}",
                f"stationär für {value}",
                f"Krankenhausaufenthalt von {value}"
                ],        
        "IMMUNIZATION":[
                f"Impfungen: {value}",
                f"geimpft gegen {value}",
                f"Impfstatus: {value}",
                f"Der Patient wurde immunisiert gegen {value}",
                f"Impfungen liegen vor für {value}"
                ],

        "IMPRESSION": [
                f"Einschätzung: {value}",
                f"Beurteilung: {value}",
                f"Zusammenfassend ergibt sich: {value}",
                f"klinische Impression: {value}",
                f"Schlussfolgerung: {value}",
                f"abschließende Einschätzung: {value}",
                f"Interpretation: {value}",
                f"{value} als zusammenfassender Befund"
                ],

        "INSURANCE_ID": [
                f"Versicherungsnummer: {value}",
                f"Vers.-ID: {value}",
                f"Versicherten-ID: {value}"
                ],
    
        "LAB_RESULT": [
                f"Laborergebnisse: {value}",
                f"Im Labor zeigte sich: {value}",
                f"Blutwerte: {value}",
                f"Laborbefund: {value}",
                f"Ergebnisse der Laboruntersuchung: {value}",
                f"diagnostisch relevante Werte: {value}",
                f"Laborparameter: {value}",
                f"{value} wurden im Labor festgestellt"
                ],

        "LIFESTYLE": [
                f"Lebensstil: {value}",
                f"führt einen {value} Lebensstil",
                f"Verhaltensmuster: {value}",
                f"Lebensgewohnheiten: {value}",
                f"Lebensweise: {value}"
                ],

        "MEDICATION": [
                f"bekommt {value}",
                f"Therapie mit {value}",
                f"{value} wurde verabreicht",
                f"Medikation: {value}",
                f"wird behandelt mit {value}",
                f"Medikamentöse Behandlung mit {value}",
                f"erhält {value} als Medikament"
                ],

        "OCCUPATION":[
                f"aktueller Beruf: {value}",
                f"is {value} von Beruf",
                f"er ist {value}",
                f"arbeitet als {value}",
                f"keine Beschäftigung",
                f"arbeitet als {value}",
                f"{value} ist sein/ihr Beruf",
                f"Beruflich tätig als {value}",
                f"Zurzeit ohne Beschäftigung" if random.random() < 0.2 else f"Er/Sie ist {value}",
                ],

        "ORG": [
                f"im Krankenhaus {value}",
                f"Einrichtung: {value}",
                f"im {value}",
                f"Klinik: {value}",
                f"stationiert in {value}",
                f"zugehörig zu {value}",
                f"behandelt im {value}",
                f"Arbeitsort: {value}"
            ],

        "PATIENT": [
                f"Patient: {value}",
                f"Name: {value}",
                f"{value} stellte sich vor",
                f"Betroffene Person: {value}",
                f"{value} wurde aufgenommen",
                f"Es handelt sich um {value}",
                f"Die Person namens {value}",
                f"{value} wurde eingewiesen"
            ],
            
        "PHONE": [
                f"Telefonnummer: {value}",
                f"Kontakt: {value}",
                f"Telefon: {value}",
                f"erreichbar unter: {value}",
                f"Rufnummer: {value}"
                ],

        "PHONE_PATIENT": [
                f"Telefonnummer: {value}",
                f"Kontakt: {value}",
                f"Telefon: {value}",
                f"erreichbar unter: {value}",
                f"Rufnummer: {value}"
                ],

        "PID":[
                f"patient-id {value}",
                f"ID: {value}",
                f"PID: {value}",
                f"PIZ: {value}",
                f"Patientenkennzeichen: {value}",
                f"Identifikationsnummer: {value}"
                ],

        "PREV_DIAGNOSIS": [
                f"frühere Diagnose: {value}",
                f"Vordiagnose: {value}",
                f"zuvor diagnostiziert mit {value}",
                f"es lag bereits {value} vor",
                f"bekannte Vorerkrankung: {value}",
                f"bisherige Diagnose: {value}",
                f"medizinische Vorgeschichte zeigt {value}",
                f"diagnostiziert in der Vergangenheit: {value}",
                f"Vorerkrankungen: {value}"
                ],

        "PROCEDURE": [
                f"durchgeführte Prozedur: {value}",
                f"eingesetztes Verfahren: {value}",
                f"Untersuchung mittels {value}",
                f"{value} wurde angewendet",
                f"{value} wurde durchgeführt",
                f"diagnostisches Verfahren: {value}"
                ],

        "RISKFACTOR": [
                f"mögliche Risikofaktoren: {value}",
                f"es bestehen folgende Risiken: {value}",
                f"Risikoaspekte: {value}",
                f"bekannte Risikofaktoren: {value}",
                f"{value} gelten als Risikofaktoren",
                f"erhöhtes Risiko durch: {value}",
                f"relevante Risiken: {value}"
                ],

        "ROOM_NUMBER": [
                f"Zimmernummer: {value}",
                f"untergebracht ins Zimmer {value}",
                f"Raum: {value}"
                ],

        "ROUTE": [
                f"Applikationsweg: {value}",
                f"wurde {value} verabreicht",
                f"Verabreichungsform: {value}"
                ]   ,
        
        "SMOKING_STATUS": [
                f"Raucherstatus: {value}",
                f"er/sie ist {value}",
                f"Tabakkonsum: {value}"
                ],
    
        "STAY_REASON":[
                f"Grund des Krankenhausaufenthalts: {value}",
                f"Aufgrund von {value}",
                f"muss noch stationär wegen {value}",
                f"wegen {value} muss stationäre"
                ],

        "SYMPTOM": [
                f"klagt über {value}",
                f"zeigt Symptome wie {value}",
                f"Symptomatik: {value}",
                f"hat {value}",
                f"es wurden {value} beobachtet",
                f"{value} wurde berichtet",
                f"leidet unter {value}",
                f"stark anhaltend dumpfen {value}",
                f"fühlt sich {value}",
                ],

        "TREATMENT": [
                f"erhält Behandlung mit {value}",
                f"Therapieansatz: {value}",
                f"{value} wurde eingeleitet",
                f"Behandlungsform: {value}",
                f"es erfolgte eine Behandlung mittels {value}",
                f"Therapie: {value}",
                f"therapeutische Maßnahme: {value}"
                ],

        "VITALSIGNS":[
                f"{value}",
                f"Vitalparameter: {value}",
                f"Die Vitalzeichen zeigen: {value}",
                f"Gemessene Werte: {value}"
                ],
        # add more as needed
    }

    end_char = random.choice(['. ',', ','; ','! '])
    phrase = f"{entity_type}: {value}{end_char}"# default value
    if entity_type in variations:
        phrase =f" {random.choice(variations[entity_type])}{end_char}"
        
    return phrase

