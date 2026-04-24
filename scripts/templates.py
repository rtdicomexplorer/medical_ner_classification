freib_not_aunahme=(
"{ORG}																							"						
"{DEPARTMENT} + {ADDRESS}                                                                       "
"                                                                                               "
"Herr                                                                                           "
"{DOCTOR}                                                                                       "
"{DEPARTMENT}                                                                                   "
"{ADDRESS}                                                                                      "
"                                                                                               "
"                                                                                               "
"                                                                                               "
"                                        {DATE}                                                 "
"                                                                                               "
"{PATIENT}, {BIRTHDATE}, {PID}                                                                  "
"{ADDRESS_PATIENT}                                                                              "
"                                                                                               "
"Sehr geehrte Frau Kollegin, sehr geehrter Herr Kollege,                                        "
"                                                                                               "
"wir berichten Ihnen nachfolgend über die Behandlung des o.g. Patienten, der sich am            "
"{ADMISSION_DATE} in unserem {DEPARTMENT} befand.                                               "
"                                                                                               "
"DIAGNOSEN                                                                                      "
"                                                                                               "
"{DIAGNOSIS}                                                                                    "
"                                                                                               "
"Allergien/Unvertraglichkeiten: {ALLERGY}                                                       "
"                                                                                               "
"ANAMNESE                                                                                       "
"                                                                                               "
"Es erfolgt die Vorstellung des Patienten in Begleitung seines {FAMILYMEMBER}.                  "
"{ANAMNESE}                                                                                     "
"Keine {SYMPTOM}.                                                                               "
"                                                                                               "
"UNTERSUCHUNGSBEFUND                                                                            "
"                                                                                               "
"                                                                                               "
"In der körperlichen Untersuchung zeigt sich eine endgradig schmerzhafte Pronation des linken   "
"Unterarms sowie ein isolierter Druckschmerz über dem {BODY_PART}.                              "
"{BODY_PART} nicht druckschmerzhaft.                                                            "
"{FINDING}.                                                                                     "
"{FINDING}.                                                                                     "
"                                                                                               "
"MEDICATION BEI AUFNAHME                                                                        "
"                                                                                               "
"{MEDICATION}                                                                                   "
"                                                                                               "
"BILDGEBUNG                                                                                     "
"{PREV_DIAGNOSIS} vom {DATE}.                                                                   "
"                                                                                               "
"{SYMPTOM}.                                                                                     "
"                                                                                               "
"                                                                                               "
"EPIKRISE                                                                                       "
"Anamnese, körperliche Untersuchung, Bildgebung                                                 "
"                                                                                               "
"                                                                                               "
"MEDIKATION BEI ENTLASSUNG BZW. MEDIKATIONSEMPFEHLUNG                                           "
"{MEDICATION}                                                                                   "
"                                                                                               "
"                                                                                               "
"THERAPIEEMPFEHLUNG                                                                             "
"                                                                                               "
"Wir empfehlen{TREATMENT} zusammen mit                                                          "
"{TREATMENT} sowie                                                                              "
"{MEDICATION} bei Bedarf.                                                                       "
                                                                                                
"Eine Schnittbildgebung mittels {DEVICE} kann bei Beschwerdepersistenz erwogen werden.          "
"                                                                                               "
"Mit freundlichen Grüßen                                                                        "
"                                                                                               "
"{DOKTOR},  {DOKTOR},  {DOKTOR}                                                                 "
"            Ärtzlicher Direktor, Oberarzt, Fachärztin                                          "
"			                                                                                    "
"{DOKTOR}"
"Arzt"

)


freib_template = (
"{ORG}																													"
"                                                                                                                       "
"Department {DEPARTMENT}                                                                                                "
"                                                                                                                       "
"Klinik für {DEPARTMENT}                                                                                                "
"Ärztlicher Direktor: {DOCTOR}                                                                                          "
"                                                                                                                       "
"{PATIENT}, * {BIRTHDATE}, PIZ: {PID}                                                                                   "
"{ADDRESS_PATIENT}                                                                                                      "
"                                                                                                                       "
"Sehr geehrte {PATIENT},                                                                                                "
"                                                                                                                       "
"wir bedanken uns für die freundliche Zuweisung von {PATIENT}, die sich am {ADMISSION_DATE} in unserer {DEPARTMENT}     "
"Sprechstunde vorstellte.                                                                                               "
"                                                                                                                       "
"Diagnose:                                                                                                              "
"{DIAGNOSIS}                                                                                                          "
"{DIAGNOSIS}                                                                                                          "
"{DIAGNOSIS}                                                                                                          "
"{DIAGNOSIS}                                                                                                          "
"{DIAGNOSIS}                                                                                                          "
"{DIAGNOSIS}                                                                                                          "
"                                                                                                                       "
"Therapie:                                                                                                              "
"{PROCEDURE}, {TREATMENT}                                                                                           "
"                                                                                                                       "
"Anamnese:                                                                                                              "
"{PATIENT} ist eine in unserer Klinik gut bekannte Patientin mit einer                                                  "
"{DIAGNOSIS} bei {PREV_DIAGNOSIS}. Für die ausführliche Anamnese dürfen wir                                         "
"freundlicherweise auf die alten Arztbriefe verweisen. Die heutige Vorstellung in                                       "
"unserer {DEPARTMENT} Sprechstunde erfolgt aufgrund einer                                                               "
"{DIAGNOSIS} mit {SYMPTOM} und {SYMPTOM}. Im Rahmen einer {PROCEDURE}                                           "
"sowie einer {PROCEDURE} zeigte sich deutlich Hinweise für einen                                                      "
"{DIAGNOSIS}. Außerdem berichtet die {FAMILYMEMBER} wiederholt von {SYMPTOM}                                      "
"sowie {SYMPTOM}, insbesondere in Stresssituationen. Aktuell wünschen sich die                                        "
"{FAMILYMEMBER} bei {SYMPTOM} und starkem {DIAGNOSIS} mit                                                    "
"{SYMPTOM} eine {DEVICE} zur Ernährung.                                                                             "
"                                                                                                                       "
"Procedere:                                                                                                             "
"Aufgrund der ausgeprägten {DIAGNOSIS} mit {SYMPTOM} sowie Nachweis eines                                           "
"{DIAGNOSIS} empfehlen wir eine {PROCEDURE} sowie die Anlage einer                                                  "
"{PROCEDURE} zur Ernährung. Bezüglich eines Operationstermins sowie eines Termins zur                                 "
"{HOSPITAL_STAY} mit {PROCEDURE} sowie {PROCEDURE} werden wir uns telefonisch                                       "
"mit der {FAMILYMEMBER} in Verbindung setzen. Die {FAMILYMEMBER}                                          "
"wünschen im Anschluss an die operative Therapie eine {TREATMENT} in der                                              "
"{ORG}. Diesbezüglich werden wir Kontakt mit {DOCTOR}, {DEPARTMENT} (-{PHONE}) aufnehmen.                                    "
"                                                                                                                       "
"Bei zwischenzeitlichen Fragen oder Problemen stehen wir jederzeit zur Verfügung.                                       "
"                                                                                                                       "
"Mit freundlichen Grüßen                                                                                                "
"{DOCTOR}                                                                                                              "
"Oberarzt                                                                                                                       "
    
)


muster_template =(
"        {ORG}                                                                            "
"                                                                                         "
"                        ZENTRUM FÜR INNERE MEDIZIN                                       "
"                                                                                         "
"                         Internistische Abteilung                                        "
"                                                                                         "
"        {ORG}                                                                            "
"        {ADDRESS}                              ID: {PID}                                "
"                                                Krbl.-Nr.: {INSURANCE_ID}                "
"                                                {DEPARTMENT} {PHONE}                     "
"                                                       {DATE}                                      "
"                                                                                         "
"        Sehr geehrte Frau Kollegin, sehr geehrter Herr Kollege,                          "
"                                                                                         "
"        wir berichten Ihnen über den Patienten                                           "
"           {PATIENT}, geboren am {BIRTHDATE}                                             "
"           wohnhaft in {ADDRESS_PATIENT}                                                 "
"        der sich vom {ADMISSION_DATE} bis {DISCHARGE_DATE} in unserer stationären        "
"        Behandlung befand.                                                               "
"                                                                                         "
"        DIAGNOSE:                                                                     "
"         - {DIAGNOSIS} ({DATE})                                                          "
"           Lokalisation: {BODY_PART}                                      "
"           Klassifikation nach Ann Arbor: 3B                                             "
"         - {PROCEDURE} ({DATE})                                                          "
"         - {TREATMENT} ({DATE})                                                          "
"         - {TREATMENT} ({DATE})                                                          "
"        Begleiterkrankungen:                                                             "
"         - {PREV_DIAGNOSIS} (gebessert)                                   "
"                                                                                         "
"        Folgende wichtige {FINDING} wurden während des                                   "
"        {HOSPITAL_STAY} erhoben:                                                         "
"        BSG (1-Stunden-Wert): {LAB_RESULT}                                               "
"        Körpertemperatur: {VITALSIGNS}                                                   "
"        Becken-Übersichtsaufnahme: {FINDING}                                             "
"                                                                                         "
"        Tumorcharakteristika und Verschlüsselung:                                        "
"        Tumorlokalisation:                                                               "
"         - {BODY_PART} Hauptlokalisation                                                 "
"         - {BODY_PART}                                                                   "
"        Histologie:                                                                      "
"         - {DIAGNOSIS}, NODULÄR-SKLEROSIERENDE FORM.                       "
"                                                                                         "
"        Klassifikation nach Ann Arbor: Stadium 3 Kategorie B                             "
"        (mit {SYMPTOM}),                                                                 "
"        {BODY_PART} Organ nicht befallen, klinische                                      "
"        {FINDING}, {BODY_PART} Organbefall, mikroskopisch bestaetigt,                    "
"        {BODY_PART} Organ nicht befallen, mikroskopisch untersucht,                      "
"        {BODY_PART} Organ nicht befallen, mikroskopisch                                  "
"        untersucht, {BODY_PART} Organ nicht befallen, mikroskopisch                      "
"        untersucht, {BODY_PART} Organ nicht befallen, mikroskopisch                      "
"        untersucht, {BODY_PART} Organ nicht befallen,                                    "
"        mikroskopisch untersucht, {BODY_PART} Organ nicht befallen,                      "
"        mikroskopisch untersucht, Andere Organe Organ nicht                              "
"        befallen, mikroskopisch untersucht                                               "
"                                                                                         "
"        Besonderheiten des Verlaufes waren:                                              "
"        Die Aufnahme des Patienten erfolgte zur {STAY_REASON}. Anlaß der                 "
"        aktuellen Betreuung war die {STAY_REASON}.                                       "
"                                                                                         "
"        Beurteilung des Tumorgeschehens:                                                 "
"        Leistungszustand nach ECOG: {FINDING}                                            "
"        {FINDING} über {DIAGNOSIS}:                                                      "
"        Die Angehörigen des Patienten sind aufgeklärt                                    "
"        Der Patient ist voll aufgeklärt                                                  "
"                                                                                         "
"        Mit kollegialer Hochachtung                                                      "
"                                                                                         "
"                                 {DOCTOR}                                                "
"                                     Chefarzt                                            "
"                                                                                         "
)


arztbrief_template = (
    "Patient: {PATIENT} ({GENDER}), geboren am {BIRTHDATE}, PID: {PID}.\n"
    "Gewicht: {GEWICHT}. Größe: {GROESSE}\n" 
    "Adresse: {ADDRESS_PATIENT}, Telefon: {PATIENT_PHONE}, Familienstand: {FAMILY_STATUS}.\n" # PATIENT_PHONE
    "Beruf: {OCCUPATION}, begleitet von: {FAMILYMEMBER}.\n"
    "Vorstellung wegen: {SYMPTOM}.\n"
    "Diagnose: {DIAGNOSIS}.\n"
    "Vorherige Diagnose: {PREV_DIAGNOSIS}.\n"
    "Labor: {LAB_RESULT}, Vitalzeichen: {VITALSIGNS}.\n"
    "Medikation: {MEDICATION}, Behandlung: {TREATMENT}.\n"
    "Untersuchung durch {DOCTOR}, Abteilung: {DEPARTMENT}, Klinik: {ORG}.\n"
    "Impression: {IMPRESSION}"
)

arztbrief_template2 = (
"{DOCUMENT_TYPE} vom {DATE}\n"
"Patientenname : {PATIENT}\n"
"Geburtsdatum : {BIRTHDATE}\n"
"Große: {GROESSE}\n"
"Gewicht: {GEWICHT}\n"
"Hausarzt : {DOCTOR}\n"
"Der Patient, {PATIENT} , stellte sich mit stark anhaltend dumpfen {SYMPTOM} vor, die er seit gestern habe.\n" 
"{PATIENT} sei auch {SYMPTOM}. Darüber hinaus berichte er über {SYMPTOM}.\n" 
"Er habe auch berichtet, dass er eine {SYMPTOM} und {SYMPTOM} (Wortfindungsstörung und lallende Ansprache) entwickelt habe.\n" 
"Eine {SYMPTOM} wurde auch berichtet.\n"
"Vorerkrankungen : Er habe seit 20 Jahren {PREV_DIAGNOSIS}.IM Jahr 2018 habe er einen {PREV_DIAGNOSIS} gehabt, den konservativ behandelt wurde.\n"
"Vegetative Anamnese {ANAMNESE} ist bis auf eine {PREV_DIAGNOSIS}, die seit 5 jähren bestehe und mit {MEDICATION} eingestellt sei, unauffällig.\n"
"Medikamente Anamnese : {ANAMNESE} Er nehme die obergenannte {MEDICATION} bei bedarf ein und er nehme auch {MEDICATION} {FREQUENCY} ein.\n"
"Noxen : Er habe täglich für {SMOKING_STATUS}, bevor er sich das Rauchen abgewöhnt habe. Alkohol {ALCOHOL_CONSUMPTION}.\n" 
"Die Frage nach {LIFESTYLE} wurde verneint.\n"
"Soziale Anamnese : Er ist {OCCUPATION} von Beruf und ist {FAMILY_STATUS}. {PATIENT} lebe mit seiner {FAMILYMEMBER} und vier {FAMILYMEMBER} zusammen.\n"
"Familiäre Anamnese : {ANAMNESE} {FAMHIST} und {FAMHIST}.\n"
"Die Anamnese,{ANAMNESE} Laborwerte und eine {PROCEDURE} weisen auf einen {DIAGNOSIS} hin. {TREATMENT} wurde nach der CT begonnen.\n"
)

befundbericht_template = (
    "{DOCUMENT_TYPE} erstellt am {DATE} durch {DOCTOR} in der Abteilung {DEPARTMENT} des {ORG}.\n"
    "Patient: {PATIENT}, {GENDER}, geb. {BIRTHDATE}, PID: {PID}.\n"
    "Untersuchung mittels {DEVICE} aufgrund von {SYMPTOM}.\n"
    "Befunde: {FINDING}, Diagnose: {DIAGNOSIS}.\n"
    "Alte Diagnose: {PREV_DIAGNOSIS}.\n"
    "Laborwerte: {LAB_RESULT}, Vitalzeichens: {VITALSIGNS}, {VITALSIGNS}, {VITALSIGNS}.\n"
    "Empfehlung: {TREATMENT}. Impressions: {IMPRESSION}, {IMPRESSION}.\n"
    "Kontakt: {PHONE}, Adresse: {ADDRESS}."
)

operationsbericht_template = (
    "{DOCUMENT_TYPE}\n"
    "Datum der Operation: {DATE}, durchgeführt von {DOCTOR} im {ORG}, Abteilung: {DEPARTMENT}.\n"
    "Patient: {PATIENT}, Geschlecht: {GENDER}, Geburtsdatum: {BIRTHDATE}, PID: {PID}.\n"
    "Indikation: {DIAGNOSIS} – {SYMPTOM}, {SYMPTOM}.\n"
    "Durchgeführte Prozedur: {PROCEDURE} unter Einsatz von {DEVICE}.\n"
    "Anästhesieprotokoll: {VITALSIGNS}.\n"
    "Postoperativer Verlauf: {IMPRESSION}.\n"
    "Empfohlene Medikation: {MEDICATION} {FREQUENCY}  und {MEDICATION} {FREQUENCY} , weitere Behandlung: {TREATMENT}.\n"
    "Kontakt für Rückfragen: {DOCTOR}, Tel: {PHONE}."
)

entlassungsbericht_template = (
    "{DOCUMENT_TYPE} – Entlassung am {DISCHARGE_DATE} aus der Klinik {ORG}, Abteilung: {DEPARTMENT}.\n"
    "Patient: {PATIENT} ({GENDER}), geb. {BIRTHDATE}, PID: {PID}.\n"
    "Aufnahmediagnose: {DIAGNOSIS}, am {ADMISSION_DATE} Symptome: {SYMPTOM}, Risikofaktoren: {RISKFACTOR}.\n"
    "Behandlung: {TREATMENT}, Medikation: {MEDICATION}, Prozedur: {PROCEDURE}.\n"
    "Befunde: {FINDING}, Labordaten: {LAB_RESULT}.\n"
    "Entlassungsdiagnose: {DIAGNOSIS}.\n"
    "Empfohlene Nachsorge: {FOLLOWUP_REQ}, Grund: {FOLLOWUP_REASON}.\n"
    "Impression: {IMPRESSION}.\n"
    "KontaktPATIENT: {DOCTOR}, Tel: {PHONE}."
)

anamnesebogen_template = (
    "{DOCUMENT_TYPE} – Erfasst am {DATE} durch {DOCTOR}.\n"
    "Patient: {PATIENT}, Geschlecht: {GENDER}, Geburtsdatum: {BIRTHDATE}, PID: {PID}.\n"
    "Adresse: {ADDRESS_PATIENT}, Telefon: {PHONE_PATIENT}, Familienstand: {FAMILY_STATUS}.\n"
    "Beruf: {OCCUPATION}, Lebensstil: {LIFESTYLE}, Impfstatus: {IMMUNIZATION}.\n"
    "Allergien: {ALLERGY}.\n"
    "Familiäre Erkrankungen: {FAMHIST}.\n"
    "Vorerkrankungen: {PREV_DIAGNOSIS}, Medikamente: {MEDICATION}.\n"
    "Aktuelle Beschwerden: {SYMPTOM}.\n"
    "Körperdaten: Größe {GROESSE}, Gewicht: {GEWICHT}.\n"
    "Vegetative Anamnese: {ANAMNESE}.\n"
    "Soziale Anamnese: {ANAMNESE}.\n"

)

radiologie_template = (
    "{DOCUMENT_TYPE} – Untersuchung vom {DATE} durchgeführt durch {DOCTOR} in der Abteilung {DEPARTMENT}, {ORG}.\n"
    "Patient: {PATIENT}, {GENDER}, geb. am {BIRTHDATE}, PID: {PID}.\n"
    "Indikation: {SYMPTOM}, Fragestellung: {FINDING}.\n" # FINDING passt hier gut
    "Bildgebung: {PROCEDURE} mit {DEVICE} (Region: {BODY_PART}).\n" # BODY_PART ergänzt
    "Befund: {FINDING}.\n"
    "Impression: {IMPRESSION}.\n"
    "Telefon: {PHONE}, Adresse: {ADDRESS}."
)

laborbericht_template = (
    "{DOCUMENT_TYPE} – erstellt am {DATE}.\n"
    "Patient: {PATIENT} ({GENDER}), geboren am {BIRTHDATE}, PID: {PID}.\n"
    "Untersuchende Einrichtung: {ORG}, Abteilung: {DEPARTMENT}.\n"
    "Soziale Anamnese: {ANAMNESE}.\n"
    "Laborparameter: {LAB_RESULT}, {LAB_RESULT}, {LAB_RESULT}.\n"
    "Diagnosehinweis: {DIAGNOSIS}.\n"
    "Beurteilung: {IMPRESSION}, {IMPRESSION}.\n"
    "Kontakt: {DOCTOR}, Tel: {PHONE}."
)

patho_template = (
    "{DOCUMENT_TYPE} – Befunddatum: {DATE}, Abteilung: {DEPARTMENT}, Klinik: {ORG}.\n"
    "Patient: {PATIENT}, {GENDER}, geb. {BIRTHDATE}, PID: {PID}.\n"
    "Anamnese: {ANAMNESE}.\n"
    "Material: {MATERIAL}.\n" # Geändert von PROCEDURE zu MATERIAL
    "Makroskopie: {FINDING}.\n"
    "Mikroskopie: {DIAGNOSIS}.\n"
    "Zusätzliche Tests: {LAB_RESULT}.\n"
    "Beurteilung: {IMPRESSION}.\n"
    "Arzt: {DOCTOR}, Tel: {PHONE}."
)

ueberweisung_template = (
    "{DOCUMENT_TYPE} – Ausgestellt am {DATE} von {DOCTOR}, {DEPARTMENT}, {ORG}.\n"
    "Patient: {PATIENT}, geb. {BIRTHDATE}, PID: {PID}.\n"
    "Zielabteilung: {DEPARTMENT}.\n"
    "Grund der Überweisung: {FOLLOWUP_REASON}.\n"
    "Vorbefunde: {PREV_DIAGNOSIS}, aktuelle Beschwerden: {SYMPTOM}.\n"
    "Medikamente Anamnese : {ANAMNESE}\n"
    "Aktuelle Medikation: {MEDICATION}.\n"
    "Telefon: {PHONE}, Adresse: {ADDRESS}."
)

einwilligung_template = (
    "{DOCUMENT_TYPE} – Ausgefüllt am {DATE}.\n"
    "Patient: {PATIENT} ({GENDER}), geb. am {BIRTHDATE}, PID: {PID}.\n"
    "Für das folgende Verfahren: {PROCEDURE}.\n"
    "Behandelnder Arzt: {DOCTOR}, Abteilung: {DEPARTMENT}, Klinik: {ORG}.\n"
    "Risiken und Alternativen wurden erklärt.\n"
    "Diagnose/Indikation: {DIAGNOSIS}, Symptome: {SYMPTOM}.\n"
    "Patient gibt Einwilligung zur Behandlung mit {TREATMENT}.\n"
    "Telefon: {PHONE}, Adresse: {ADDRESS}."
)

impfpass_template = (
    "{DOCUMENT_TYPE} – Stand: {DATE}.\n"
    "Patient: {PATIENT}, geboren am {BIRTHDATE}, Geschlecht: {GENDER}, PID: {PID}.\n"
    "Erfasste Impfungen: {IMMUNIZATION}.\n"
    "Hausarzt: {DOCTOR}, Einrichtung: {ORG}, Abteilung: {DEPARTMENT}.\n"
    "Bemerkung: {IMPRESSION}.\n"
    "Adresse: {ADDRESS}, Telefon: {PHONE}."
)

rezept_template = (
    "{DOCUMENT_TYPE} – Ausgestellt am {DATE} durch {DOCTOR} ({DEPARTMENT}, {ORG}).\n"
    "Patient: {PATIENT}, geboren am {BIRTHDATE}, PID: {PID}.\n"
    "Verschriebene Medikation: {MEDICATION}.\n"
    "Diagnosebezug: {DIAGNOSIS}.\n"
    "Bemerkung: {IMPRESSION}.\n"
    "Telefon: {PHONE}, Adresse: {ADDRESS}."
)

therapieplan_template = (
    "{DOCUMENT_TYPE} – Erstellt am {DATE} durch {DOCTOR} in der Abteilung {DEPARTMENT}, Klinik: {ORG}.\n"
    "Patient: {PATIENT}, {GENDER}, geb. {BIRTHDATE}, PID: {PID}.\n"
    "Diagnose: {DIAGNOSIS}.\n"
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
    "Patient: {PATIENT}, geboren am {BIRTHDATE}, Geschlecht: {GENDER}, PID: {PID}.\n"
    "Aktueller Zustand: {FINDING}, Vitalwerte: {VITALSIGNS}.\n"
    "Pflegemaßnahmen: {TREATMENT}, Medikation: {MEDICATION}.\n"
    "Auffälligkeiten: {SYMPTOM}, Allergien: {ALLERGY}.\n"
    "Pflegekraft: {DOCTOR}, Station: {DEPARTMENT}, Klinik: {ORG}.\n"
    "Adresse: {ADDRESS}, Telefon: {PHONE}."
)

opfreigabe_template = (
    "{DOCUMENT_TYPE} – Freigegeben am {DATE} durch {DOCTOR}, Abteilung: {DEPARTMENT}.\n"
    "Patient: {PATIENT}, geb. am {BIRTHDATE}, PID: {PID}, {GENDER}.\n"
    "Geplante Prozedur: {PROCEDURE}.\n"
    "Indikation: {DIAGNOSIS}, Symptome: {SYMPTOM}.\n"
    "Vitalzeichen stabil: {VITALSIGNS}.\n"
    "Keine Kontraindikationen festgestellt.\n"
    "Medikation vor OP: {MEDICATION}.\n"
    "Einrichtung: {ORG}, Adresse: {ADDRESS}, Tel: {PHONE}."
)

aufnahmebogen_template = (
    "{DOCUMENT_TYPE} – Aufnahme am {ADMISSION_DATE} in {ORG}, Abteilung: {DEPARTMENT}.\n"
    "Patient: {PATIENT}, {GENDER}, geboren am {BIRTHDATE}, PID: {PID}.\n"
    "Adresse: {ADDRESS_PATIENT}, Tel: {PHONE_PATIENT}, Familienstand: {FAMILY_STATUS}.\n"
    "Beschwerden: {SYMPTOM}, Vorbefunde: {PREV_DIAGNOSIS}.\n"
    "Soziale Ananmnese: {ANAMNESE}\n"
    "Aktuelle Medikation: {MEDICATION}, Allergien: {ALLERGY}, {ALLERGY}, {ALLERGY}.\n"
    "Größe: {GROESSE}, Gewicht: {GEWICHT}, Vitalwerte: {VITALSIGNS}, {VITALSIGNS}.\n"
    "Begleitung durch: {FAMILYMEMBER}.\n"
    "Untersuchender Arzt: {DOCTOR}.\n"
    "Verlegt auf Staion 7 Zimmer {ROOM_NUMBER}"
)

hkp_template = (
    "{DOCUMENT_TYPE} – Erstellt am {DATE} durch {DOCTOR}, {ORG}.\n"
    "Patient: {PATIENT}, PID: {PID}, geboren am {BIRTHDATE}.\n"
    "Diagnose: {DIAGNOSIS}.\n"
    "Geplante Behandlung: {TREATMENT}, Prozeduren: {PROCEDURE}.\n"
    "Medikamente: {MEDICATION}.\n"
    "Kostenaufstellung gemäß Krankenkasse.\n"
    "Kontakt: {PHONE}, Adresse: {ADDRESS}."
)

attest_template = (
    "{DOCUMENT_TYPE} – Ausgestellt am {DATE}.\n"
    "Patient: {PATIENT}, geb. am {BIRTHDATE}, PID: {PID}, Beruf: {OCCUPATION}.\n"
    "Diagnose: {DIAGNOSIS}, Beschwerden: {SYMPTOM}.\n"
    "Der Patient ist derzeit {FOLLOWUP_REASON}.\n"
    "Dauer der Arbeitsunfähigkeit: {FOLLOWUP_REQ}.\n"
    "Unterschrift: {DOCTOR}, Abteilung: {DEPARTMENT}, {ORG}."
)

notfall_template = (
    "{DOCUMENT_TYPE} – Datum: {ADMISSION_DATE}, ausgestellt durch {DOCTOR}, Klinik: {ORG}.\n"
    "Patient: {PATIENT}, {GENDER}, geb. am {BIRTHDATE}, PID: {PID}.\n"
    "Telefon: {PHONE_PATIENT}, Adresse: {ADDRESS_PATIENT}.\n"
    "Begleitet von {FAMILYMEMBER}.\n"
    "Symptome: {SYMPTOM}, Vitalwerte: {VITALSIGNS}, Risikofaktoren: {RISKFACTOR}.\n"
    "Durchgeführte Maßnahmen: {TREATMENT}, verabreichte Medikation: {MEDICATION}.\n"
    "Diagnose: {DIAGNOSIS}.\n"
    "Patient wurde stationär auf die Station Escherich Zimmer {ROOM_NUMBER} aufgenommen.\n"

)

ekg_template = (
    "{DOCUMENT_TYPE} – Befunddatum: {DATE}, erstellt durch {DOCTOR}, Abteilung: {DEPARTMENT}, {ORG}.\n"
    "Patient: {PATIENT}, geb. am {BIRTHDATE}, PID: {PID}.\n"
    "Indikation: {SYMPTOM}.\n"
    "Ergebnisse: {FINDING}, Vitalzeichen: {VITALSIGNS}.\n"
    "Diagnose: {DIAGNOSIS}, Beurteilung: {IMPRESSION}.\n"
    "Telefon: {PHONE}, Adresse: {ADDRESS}."
)

roentgen_template = (
    "{DOCUMENT_TYPE} – Untersuchung am {DATE}, Klinik: {ORG}, Abteilung: {DEPARTMENT}.\n"
    "Patient: {PATIENT}, PID: {PID}, geboren am {BIRTHDATE}.\n"
    "Bildgebung mittels {DEVICE} bei {SYMPTOM}.\n"
    "Befunde: {FINDING}, Impression: {IMPRESSION}.\n"
    "Diagnose: {DIAGNOSIS}.\n"
    "Untersuchender Arzt: {DOCTOR}, Kontakt: {PHONE}."
)

ct_mrt_template = (
    "{DOCUMENT_TYPE} – {DATE}, erstellt durch {DOCTOR}, {ORG}, Abteilung: {DEPARTMENT}.\n"
    "Patient: {PATIENT}, geb. {BIRTHDATE}, PID: {PID}.\n"
    "Verfahren: {PROCEDURE} mit {DEVICE}.\n"
    "Indikation: {SYMPTOM}, Befunde: {FINDING}.\n"
    "Diagnose: {DIAGNOSIS}, Impression: {IMPRESSION}.\n"
    "Empfohlene Nachsorge: {FOLLOWUP_REQ}, Grund: {FOLLOWUP_REASON}."
)

pflegeueberleitung_template = (
    "{DOCUMENT_TYPE} – Erstellt am {DATE} durch {DOCTOR}, {ORG}, Abteilung: {DEPARTMENT}.\n"
    "Patient: {PATIENT}, geboren am {BIRTHDATE}, PID: {PID}.\n"
    "Pflegebedürfnisse: {TREATMENT}, Medikation: {MEDICATION}, Vitalzeichen: {VITALSIGNS}.\n"
    "Diagnose: {DIAGNOSIS}, Vorerkrankungen: {PREV_DIAGNOSIS}.\n"
    "Pflegehinweise: {IMPRESSION}.\n"
    "Telefon: {PHONE}, Adresse: {ADDRESS}."
)

reha_gutachten_template = (
    "{DOCUMENT_TYPE} – Antrag vom {DATE}.\n"
    "Patient: {PATIENT}, geb. am {BIRTHDATE}, PID: {PID}, Beruf: {OCCUPATION}.\n"
    "Erkrankung: {DIAGNOSIS} , Symptome: {SYMPTOM}.\n"
    "Familiäre Anamnese: {ANAMNESE}\n"
    "Behandlung bisher: {TREATMENT}, Medikamente: {MEDICATION}.\n"
    "Familiäre Vorbelastung: {FAMHIST}.\n"
    "Sozialmedizinische Bewertung: {IMPRESSION}.\n"
    "Empfohlene Maßnahmen: {FOLLOWUP_REQ}, Grund: {FOLLOWUP_REASON}.\n"
    "Kontaktarzt: {DOCTOR}, Klinik: {ORG}, Tel: {PHONE}. \n"
    "Stationäre befindet sich der Patient im Zimmer {ROOM_NUMBER}.\n"
)

complete_template = (

    "{DOCUMENT_TYPE}:\n Am {DATE} stellte sich der Patient {PATIENT} ({GENDER}), {GROESSE} per {GEWICHT} geboren am {BIRTHDATE},PID: {PID}.\n"
    "Symptome: {SYMPTOM}, Diagnose: {DIAGNOSIS}\n "
    "Beruf: {OCCUPATION}, Medikament: {MEDICATION}, Behandlung: {TREATMENT}, "
    "Durchgeführt von {DOCTOR} in der Abteilung {DEPARTMENT}  zimmer {ROOM_NUMBER}.\n"
    "Krankenhaus: {ORG}, {ADDRESS}, Tel: {PHONE}.\n"
    "Adresse: {ADDRESS_PATIENT}, Telefon: {PHONE_PATIENT}.\n"
    "Familienstand: {FAMILY_STATUS}, Familienmitglied: {FAMILYMEMBER}, familiäre Vorgeschichte: {FAMHIST}.\n"
    "Vegetatite Anamnese: {ANAMNESE}\n"
    "Abteilung: {DEPARTMENT}, Krankenhaus: {ORG}.\n"
    "Untersuchung durchgeführt mit {DEVICE}.\n"
    "Diagnose: {DIAGNOSIS}.\n"
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
    "Gewicht : {GEWICHT}, Größe: {GROESSE}.\n"
)


TEMPLATES_LIST =[complete_template ,reha_gutachten_template,pflegeueberleitung_template,ct_mrt_template,roentgen_template,ekg_template,
                 notfall_template,attest_template,hkp_template,aufnahmebogen_template,opfreigabe_template,pflegedoku_template,
                 therapieplan_template,rezept_template,impfpass_template,einwilligung_template,ueberweisung_template,patho_template,
                 radiologie_template,laborbericht_template,anamnesebogen_template,entlassungsbericht_template, operationsbericht_template,
                 befundbericht_template,arztbrief_template,arztbrief_template2, muster_template, freib_template,freib_not_aunahme]


#reduced labels and template

# 1. Arztbrief (Bleibt wie von dir oben gepostet)
arztbrief_template_red =(
    "Patient: {PATIENT} ({GENDER}), geboren am {DATE}, PID: {PID}.\n"
    "Gewicht: {GEWICHT}. Größe: {GRöESSE}\n" # Tippfehler 'Große' korrigiert
    "Adresse: {ADDRESS_PATIENT}, Telefon: {PATIENT_PHONE}, Familienstand: {FAMILY_STATUS}.\n" # PATIENT_PHONE
    "Beruf: {OCCUPATION}, begleitet von: {FAMILYMEMBER}.\n"
    "Vorstellung wegen: {SYMPTOM}.\n"
    "Impression: {IMPRESSION}.\n"
    "Diagnose: {DIAGNOSIS}.\n"
    "Vorherige Diagnose: {PREV_DIAGNOSIS}.\n"
    "Medikation: {MEDICATION}, Behandlung: {TREATMENT}.\n"
    "Untersuchung durch {DOCTOR}, Abteilung: {DEPARTMENT}, Klinik: {ORG}.\n"
    "Datum: {DATE}."
)

# 2. Laborbericht
laborbericht_template_red = (
    "{DOCUMENT_TYPE} – erstellt am {DATE}.\n"
    "Patient: {PATIENT} ({GENDER}), PID: {PID}.\n"
    "Einrichtung: {ORG}, Abteilung: {DEPARTMENT}.\n"
    "Symptom: {SYMPTOM}.\n"
    "Diagnose: {DIAGNOSIS}.\n"
    "Kontakt: {DOCTOR}."
)

# 3. Pathologiebericht (Wichtig: {MATERIAL} hier drin!)
patho_template_red = (
    "{DOCUMENT_TYPE} – Befunddatum: {DATE}, Abteilung: {DEPARTMENT}, Klinik: {ORG}.\n"
    "Patient: {PATIENT}, {GENDER},({DATE}). PID: {PID}.\n"
    "Diagnose: {DIAGNOSIS}.\n"
    "Symptom: {SYMPTOM}.\n"
    "Arzt: {DOCTOR}."
)

# 4. Radiologiebefund
radiologie_template_red = (
    "{DOCUMENT_TYPE} – Untersuchung vom {DATE} durchgeführt durch {DOCTOR} in der Abteilung {DEPARTMENT}, {ORG}.\n"
    "Patient: {PATIENT}, {GENDER}, PID: {PID}. Geburtsdatum: {DATE}.\n"
    "Indikation: {SYMPTOM}.\n"
    "Befund: {DIAGNOSIS}."
)






# Wir organisieren die Templates mit ihrem festen Dokumententyp
TEMPLATE_CONFIG = {
    "Kardiologie": {
        "template": arztbrief_template_red,
        "doc_type": "Arztbrief"
    },
    "Onkologie": {
        "template": arztbrief_template_red,
        "doc_type": "Arztbrief"
    },
    "Labor": {
        "template": laborbericht_template_red,
        "doc_type": "Laborbericht"
    },
    "Pathologie": {
        "template": patho_template_red,
        "doc_type": "Pathologiebericht"
    },
    "Radiologie": {
        "template": radiologie_template_red,
        "doc_type": "Radiologiebefund"
    }
}