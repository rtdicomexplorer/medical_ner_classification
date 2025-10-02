
#Das ist die Krankengeschichte, also alle Infos, 
#die der Patient (oder dessen Angehörige) über seine bisherigen und aktuellen Beschwerden, 
#Vorerkrankungen, familiäre Krankheiten, Lebensstil usw. erzählt.
#Beispiel: „Patient berichtet über seit 2 Wochen anhaltenden Husten und Fieber.“
#Ist subjektiv und basiert auf der Erzählung des Patienten.


anamneses = [
    "nächtliche Schweißausbrüche",
    "Schlafstörungen",
    "verminderter Appetit",
    "gesteigerter Appetit",
    "vermehrter Durst",
    "unfreiwilliger Gewichtsverlust",
    "regelmäßige Übelkeit am Morgen",
    "Erbrechen nach Mahlzeiten",
    "Fieber seit drei Tagen",
    "Schüttelfrost in der Nacht",
    "häufiger Harndrang",
    "Schmerzen beim Wasserlassen",
    "Verstopfung",
    "Durchfall",
    "Kurzatmigkeit beim Treppensteigen",
    "anhaltender Husten",
    "nächtliche Atemnot",
    "unerklärliche Hitzegefühle",
    "regelmäßiger Schwindel",
    "Kältegefühl in den Extremitäten",
    "Blähungen und Völlegefühl",
    "nächtliches Wasserlassen",
    "Unruhe während der Nacht",
    "plötzlicher Appetitverlust",
    "kein Durstgefühl",
    "unregelmäßiger Stuhlgang",
    "nächtlicher Harndrang",
    "unruhiger Schlaf mit häufigem Erwachen",
    "Patient klagt über seit 3 Tagen anhaltenden Husten.",
    "Bekanntes Asthma bronchiale seit der Kindheit.",
    "Keine bekannten Vorerkrankungen.",
    "Raucher seit 20 Jahren, ca. 10 Zigaretten täglich."
]


courses = [
    "Der Verlauf ist stabil.",
    "Der Krankheitsverlauf ist progressiv.",
    "Die Symptome besserten sich im Verlauf.",
    "Klinische Besserung im Verlauf beobachtet.",
    "Keine signifikante Veränderung im Verlauf.",
    "Rezidivierende Symptome im Verlauf.",
    "Komplikationen traten im Verlauf auf.",
    "Verbesserung nach Therapieeinleitung.",
    "Patient zeigte keine Besserung.",
    "Verlauf durch Sekundärinfektion erschwert."
]

smoking_status = [
    "Nichtraucher",
    "Raucht gelegentlich",
    "Aktiver Raucher",
    "Ex-Raucher seit 5 Jahren",
    "täglich für 10 Jahren zehn Zigaretten geraucht"
]

alcohol_consumptions = [
    "kein Alkoholkonsum",
    "gelegentlicher Alkoholkonsum",
    "regelmäßiger Alkoholkonsum",
    "starker Alkoholkonsum"
]

blood_types = [
    "A+",
    "A-",
    "B+",
    "B-",
    "AB+",
    "AB-",
    "0+",
    "0-"
]



dosages = [
    "5 mg täglich",
    "10 mg zweimal täglich",
    "20 mg einmal wöchentlich"
]

durations = [
    "2 Wochen",
    "1 Monat",
    "3 Monate"
]

frequencies = [
    "einmal täglich",
    "zweimal täglich",
    "alle 8 Stunden"
]

routes = [
    "oral",
    "intravenös",
    "subkutan",
    "intramuskulär",
    "rektal",
    "inhalativ",
    "transdermal"
]


body_parts = [
    "rechter Arm",
    "linkes Bein",
    "linker Arm",
    "rechtes Bein",
    "linke Lunge",
    "rechter Oberschenkel",
    "Kopf",
    "Hals",
    "Gesicht",
    "rechte Hand",
    "linke Hand",
    "Hufte"
]


hospital_stays = [
    "aufgenommen am 01.04.2023, entlassen am 10.04.2023",
    "Krankenhausaufenthalt vom 15.06.2023 bis 25.06.2023",
    "stationär vom 20.01.2024 bis 30.01.2024",
    "aufgenommen am 05.03.2023, entlassen am 15.03.2023",
    "stationärer Aufenthalt vom 10.07.2023 bis 20.07.2023",
    "Krankenhausaufenthalt vom 01.08.2023 bis 12.08.2023",
    "aufgenommen am 18.09.2023, entlassen am 28.09.2023"
]


stay_reasons = [
    "Kontrolle",
    "Operation (OP)",
    "Unklare Beschwerden (varia)",
    "Krankheitsbehandlung",
    "Gesundheits-Checkup",
    "Rehabilitation",
    "Notfallaufnahme",
    "Chronische Erkrankung",
    "Therapieeinleitung",
    "Diagnostik"
]



station_names = [
    "Station Escherich",
    "Station 7",
    "Station Moro",
    "Station 2A",
    "Station B1",
    "Station C3",
    "Intensivstation",
    "Neonatologie",
    "Kardiologie",
    "Chirurgie 1",
    "Orthopädie",
    "Palliativstation",
    "Neurologie",
    "Onkologie",
    "Endoskopie",
    "Notaufnahme"
]



diagnoses = {
    "Appendizitis": "K37",
    "Spastisch-dystone Zerebralparese GMFCS °IV": "G80.3",
    "Arthrose": "M15-M19",
    "Peripartaler Asphyxie": "P21.9",
    "Herzinfarkt": "I25.2",
    "Fraktur": "Z87.81",
    "COPD": "J44",
    "Bronchitis": "J42",
    "Hypertonie": "I10",
    "Diabetes Mellitus": "E11.9",
    "Asthma": "J45",
    "Pneumonie": "J18.9",
    "arterielle Hypertonie": "I10",  # Essential hypertension
    "Diabetes mellitus Typ 2": "E11",  # Type 2 diabetes
    "Hyperlipidämie": "E78.5",  # Elevated lipids (unspecified)
    "chronische Niereninsuffizienz": "N18.9",  # Chronic kidney disease, unspecified
    "status post Schlaganfall": "I69.3",  # Sequelae of cerebral infarction
    "chronisches Schmerzsyndrom": "R52.2",  # Chronic pain, not elsewhere classified
    "epileptische Anfälle in der Vorgeschichte": "Z86.6",  # Personal history of epilepsy
    "bekannte Demenz": "F03.9",  # Unspecified dementia
    "chronische Hepatitis C": "B18.2",  # Chronic viral hepatitis C
    "Asthma bronchiale": "J45.9",  # Asthma, unspecified
    "koronare Herzkrankheit": "I25.1",  # Atherosclerotic heart disease
    "Vorhofflimmern": "I48.0",  # Paroxysmal atrial fibrillation
    "Adipositas": "E66.9",  # Obesity, unspecified
    "Zustand nach Bypass-Operation": "Z95.1",  # Presence of aortocoronary bypass graft
    "Zustand nach Endoprothese Hüfte": "Z96.64",  # Presence of hip implant
    "Zustand nach Endoprothese Knie": "Z96.65",  # Presence of knee implant
    "Osteoporose": "M81.0",  # Age-related osteoporosis without fracture
    "Rheumatoide Arthritis": "M06.9",  # Rheumatoid arthritis, unspecified
    "Parkinson-Krankheit": "G20",  # Parkinson’s disease
    "Multiple Sklerose": "G35",  # Multiple sclerosis
    "Gastroösophagealer Reflux":"K21.9",
    "gastroösophagealer Reflux mit Ösophagitis": "K21.0",
    "mangelnde Gewichtszunahme (Kind)": "R62.8",
    "mangelnde Gewichtszunahme (Neugeborenes)": "P92.6",
    "mangelnde Gewichtszunahme (Erwachsener, unspezifisch)": "R63.4",
    "Spastisch-dystone Zerebralparese":"G80.8",
    "Spastisch-dystone Zerebralparese (dyskinetisch betont)": "G80.3",  # Dyskinetic cerebral palsy
    "Spastisch-dystone Zerebralparese (gemischt)": "G80.8",  # Mixed type / Other cerebral palsy

}


vitalsigns = [
    "Blutdruck 120/80 mmHg", 
    "Puls 72/min", 
    "Temperatur 37,2 °C",
    "Sauerstoffsättigung 98 %",
    "Atemfrequenz 16/min",
    "Taillenumfang 90 cm",
    "BMI 23.1 kg/m²",
    "Blutzucker (BZ) 110 mg/dL",
    "Temperatur rektal / tympanisch 38.2 °C",
    "Laktatwert 1.8 mmol/L",
    "Zentralvenöser Druck (ZVD) 5 mmHg"
]

lifestyles = [
    "Nichtraucher",
    "Raucher (5 Zigaretten/Tag)",
    "Gelegentlicher Alkoholgenuss",
    "Regelmäßige Bewegung",
    "Drogenmissbrauch",
    "Trinkt Bier täglich",
    "Keine Drogen, kein Alkohol",
    "Vegetarische Ernährung",
    "Vegane Ernährung",
    "Überwiegend sitzende Lebensweise",
    "Täglicher Ausdauersport",
    "Meditationspraxis / Achtsamkeitstraining",
    "Stressreicher Alltag",
    "Chronischer Schlafmangel",
    "Gesunder Schlafrhythmus",
    "Konsumiert regelmäßig Cannabis",
    "E-Zigarettennutzung statt Tabak",
    "Häufige Nutzung sozialer Medien (>4h/Tag)",
    "Arbeitet in der Nachtschicht",
    "Keine körperliche Bewegung / sportlich inaktiv"
]


risk_factors = [
    "Familiäre Vorbelastung Diabetes",
    "Adipositas (BMI > 30)",
    "Nikotinabusus",
    "Hyperlipidämie",
    "Schlafapnoe",
    "Hypercholesterinämie",
    "Bluthochdruck (RR erhöht)",
    "Höheres Lebensalter",
    "Familiäre Vorbelastung KHK",
    "Bewegungsmangel",
    "Ungesunde Ernährung",
    "Chronischer Stress",
    "Diabetes mellitus Typ 2",
    "Gestationsdiabetes in der Anamnese",
    "Metabolisches Syndrom",
    "Alkoholkonsum (übermäßig)",
    "Männliches Geschlecht",
    "Postmenopausaler Status",
    "Erhöhtes LDL-Cholesterin",
    "Erniedrigtes HDL-Cholesterin"
]




doctors = ["Dr. Müller", "Dr. Schneider", "Dr. Becker", "Dr. Weber","Dr. Suhle Nikolas", "Dr. Lehmann", "Dr. Fischer", "Dr. Weber",
           "Dr. Adams", "Dr. Lee", "Dr. Patel", "Dr. Chen", "Prof. A. Passero","Frau Moller", "Herr Moller", "Prof. Dr. Armani", 
           "PD. Dr. Artze Andreas", "Herr Dr. Decainai Rolf"]


#Das sind die Beschwerden oder Auffälligkeiten, die der Patient spürt oder die beobachtet werden.
#Beispiel: Schmerzen, Schwindel, Atemnot, Übelkeit
#Können aus der Anamnese stammen (Patient sagt, was er fühlt) oder auch vom Arzt beobachtet werden.
#Symptome sind subjektiv (vom Patienten erlebt).
symptoms = [

    #Neurologische Symptome
    "Kopfschmerzen",
    "Schwindel",
    "Sprachstörung",
    "Sehstörung",
    "Kribbeln",
    "Taubheitsgefühl",
    "Gangunsicherheit",
    "Lähmungen",
    "Bewusstseinsstörung",
    "Verwirrtheit",
    "Gedächtnisstörung",
    "Tremor",
    "Epileptischer Anfall",
    "niedergeschlagen",
    "Bluthochdruck",

    #Kardiopulmonale Symptome
    "Brustschmerzen",
    "Atemnot",
    "Palpitationen",
    "Orthopnoe",
    "Husten",
    "Zyanose",
    "Druckgefühl in der Brust",
    "Kaltschweißigkeit",
    "Synkope",

    #Allgemeine Symptome
    "Fieber",
    "Müdigkeit",
    "Appetitlosigkeit",
    "Gewichtsverlust",
    "Nachtschweiß",
    "Abgeschlagenheit",
    "Schlafstörung",
    "Konzentrationsstörung",
    "Gliederschmerzen",
    "Unwohlsein",
    "Kribbeln auf der linke Arm",

    #Gastrointestinale Symptome
    "Übelkeit",
    "Erbrechen",
    "Bauchschmerzen",
    "Durchfall",
    "Verstopfung",
    "Blut im Stuhl",
    "Blähungen",
    "Appetitverlust",
    "Reflux",
    "Völlegefühl",

    #Urologische Symptome
    "Schmerzen beim Wasserlassen",
    "Häufiger Harndrang",
    "Nykturie",
    "Harnverhalt",
    "Blut im Urin",
    "Inkontinenz",

    #Dermatologische Symptome
    "Hautausschlag",
    "Juckreiz",
    "Schwellung",
    "Rötung",
    "Hautveränderungen",
    "Gewichtszunahme",
    "gastroösophagealen Reflux",
    "Mundgeruch",
    "wiederholtem Spucken",
    "starkem ösophagalen Reflux",
    "Erbrechen",
    "erschwerter Nahrungszufuhr ",
    "Dyspnoe bei Belastung",
    "Fieber bis 38,5 °C",
    "Nächtliches Schwitzen",
    "Thoraxschmerzen rechtsseitig",
    "Appetitlosigkeit"


]

medications = [

    #Blutdruckmedikamente (Antihypertensiva)
    "Ramipril",
    "Amlodipin",
    "Bisoprolol",
    "Lisinopril",
    "Valsartan",
    "Metoprolol",
    "Hydrochlorothiazid",
    "Candesartan",
    "Enalapril",

    #Antidiabetika
    "Metformin",
    "Insulin",
    "Empagliflozin",
    "Glimepirid",
    "Sitagliptin",
    "Dapagliflozin",

    #Cholesterinsenker
    "Atorvastatin",
    "Simvastatin",
    "Rosuvastatin",
    "Pravastatin",

    #Psychopharmaka & Schlafmittel
    "Diazepam",
    "Lorazepam",
    "Zolpidem",
    "Amitriptylin",
    "Mirtazapin",
    "Sertralin",
    "Citalopram",

    #Schmerzmittel / NSAR
    "Ibuprofen",
    "Paracetamol",
    "ASS",
    "Diclofenac",
    "Naproxen",
    "Novalgin",
    "Metamizol",

    #Antibiotika
    "Amoxicillin",
    "Ciprofloxacin",
    "Azithromycin",
    "Doxycyclin",
    "Clarithromycin",

    #Asthma / COPD
    "Salbutamol",
    "Formoterol",
    "Budesonid",
    "Tiotropium",
    "Beclometason",

    #Blutverdünner / Antikoagulantien
    "Marcumar",
    "Xarelto",
    "Eliquis",
    "Pradaxa",
    "Heparin",
    "Clopidogrel",

    #Rheuma / Immunsuppressiva
    "Methotrexat",
    "Prednisolon",
    "Cortison",
    "Adalimumab",
    "Infliximab"
]

treatments = [
    "Sauerstofftherapie",
    "Operation",
    "Chemotherapie",
    "Physiotherapie",
    "Reha",
    "Medikamentöse Therapie",
    "Strahlentherapie",
    "Dialyse",
    "Psychotherapie",
    "Ernährungstherapie",
    "Insulintherapie",
    "Impfung",
    "Bluttransfusion",
    "Palliative Therapie",
    "Verhaltenstherapie"
]

lab_results = [
    "Hb 13.5 g/dL",
    "Blutzucker 110 mg/dL",
    "Cholesterin 200 mg/dL",
    "Glukose 110 mg/dL",
    "CRP 5 mg/L",
    "Triglyzeride 150 mg/dL",
    "LDL-Cholesterin 130 mg/dL",
    "HDL-Cholesterin 50 mg/dL",
    "Creatinin 1.1 mg/dL",
    "HbA1c 5.8 %"
]


#Befunde
#Das sind die objektiven Untersuchungsergebnisse, die der Arzt oder die Pflegekraft durch körperliche Untersuchung, Laborwerte, Bildgebung etc. erhoben hat.
#Beispiel: „Auskultation: Rasselgeräusche über der linken Lunge“, „Blutdruck 140/90“, „Röntgen zeigt Infiltrate im rechten Lungenflügel“
#Sind objektiv messbar und überprüfbar.

findings =[ "Infiltrat in der rechten Lunge"  , 
            "Herzvergrößerung", 
            "Pleuraerguss"    , 
            "Leukozytose"     , 
            "Erhöhte Leberwerte"              , 
            "Positive Bakterienkultur"        , 
            "Nicht verschobene Radiusfraktur" , 
            "Normaler EEG-Befund" , 
            "Glatte Hirnhaut"     , 
            "Kein Nachweis von Metastasen"    , 
            "Verdickte Darmwand im Colon"     , 
            "Beidseitige Pneumonie"           , 
            "Erhöhte Blutsenkungsgeschwindigkeit" , 
            "Hyperglykämie"             , 
            "Reduzierte Nierenfunktion" , 
            "Pathologisches EKG"        , 
            "Hämaturie"                 , 
            "Albuminurie"               , 
            "Hautausschlag an den Extremitäten"   , 
            "Geringe Beweglichkeit im rechten Kniegelenk",
            "Auskultation: Giemen beidseits.",
            "Blutbild zeigt Leukozytose.",
            "Röntgen Thorax: Infiltrate im rechten Unterlappen.",
            "Sauerstoffsättigung 92% (bei Raumluft)."]

allergies = [
    "Penicillin",
    "Pollen",
    "Nüsse",
    "Hausstaubmilben",
    "Tierhaar",
    "Soja",
    "Gluten",
    "Laktose",
    "Nickel",
    "Insektengift",
    "Schimmelpilze",
    "Keine bekannt"
]


immunizations = [
    "Masern-Impfung",
    "Grippeimpfung",
    "Covid-19-Impfung",
    "Tetanus-Impfung",
    "Hepatitis B-Impfung",
    "Hepatitis A-Impfung",
    "HPV-Impfung",
    "Pneumokokken-Impfung",
    "FSME-Impfung",
    "Keuchhusten-Impfung",
    "Windpocken-Impfung",
    "Kein Impfstatus bekannt"
]


devices = [
    "Herzschrittmacher",
    "Insulinpumpe",
    "Schlafmaske",
    "Blutdruckgerät",
    "Katheter",
    "PEG-Sonde",
    "Hörgerät",
    "Prothese",
    "Rollator",
    "CPAP-Gerät",
    "Infusionspumpe",
    "Stoma",
    "Defibrillator (ICD)",
    "Zugangsport (Port-a-Cath)"
]



family_history = [
    "Vater mit Diabetes mellitus Typ 2",
    "Mutter mit Hypertonie",
    "Bruder mit Asthma bronchiale",
    "Großvater mütterlicherseits verstorben an Myokardinfarkt mit 60 Jahren",
    "Keine familiären Vorerkrankungen bekannt",
    "Mutter hatte Brustkrebs im Alter von 45",
    "Vater mit bekanntem Nikotinabusus",
    "Familiäre Häufung von Schlaganfällen",
    "Schwester mit Depression in Behandlung",
    "Eltern beide mit Hypercholesterinämie",
    "Großmutter väterlicherseits mit Alzheimer-Demenz",
    "Unklarer Gesundheitsstatus der Familie (Patient adoptiert)"
]
procedures = ["Angioplastie", "MRT-Scan", "Biopsie", "Ultraschall","CT Kopf", "Lyse-Therapie",
              "Ösophagogastroduodenoskopie", "ÖGD", "Röntgen MDP","laparoskopische Fundoplicatio", "assistierten Gastrostomie"]
departments = ["Kardiologie", "Notaufnahme", "Onkologie", "Radiologie","Neurologie", "Innere Medizin", "Sozialdienst"]


hospital_addresses = ["Hauptstraße 12, 80331 München", "Berliner Allee 45, 40212 Düsseldorf",
                      "Lindenstraße 8, 10115 Berlin", "Goetheplatz 9, 50674 Köln",
                      "Hugstetterstr. 7 79106 Freiburg", "Kamphausenstr. 23, 79666 Reute"]

hospital_phones = ["089 123456", "0211 987654", "030 234567", "0221 456789", "0761 2720298", "3456", "112", "+4912120120"]


followup_reasons = [
    "zur Blutdruckkontrolle",
    "wegen anhaltender Schmerzen",
    "zur Verlaufskontrolle",
    "zur weiteren Abklärung",
    "zur Nachsorge",
    "zur Wundkontrolle",
    "zur Laborüberprüfung",
    "zur Medikamentenanpassung",
    "zur Impfstatusüberprüfung",
    "zur Physiotherapie-Evaluation",
    "zur Diabeteskontrolle",
    "zur Überprüfung der Therapieeffekte",
    "zur Abklärung von Symptomen",
    "zur Vorsorgeuntersuchung",
    "zur Kontrolle chronischer Erkrankungen",
    # Radiologie-spezifische Ergänzungen
    "zur Röntgenkontrolle",
    "zur MRT-Untersuchung",
    "zur CT-Diagnostik",
    "zur Ultraschallkontrolle",
    "zur Beurteilung von Frakturen",
    "zur Verlaufskontrolle von Tumoren",
    "zur radiologischen Abklärung"
]

#Das ist der erste Eindruck oder die vorläufige Einschätzung des Arztes, basierend auf Anamnese,
#Symptomen und ersten Untersuchungen.
#Beispiel: „Verdacht auf Lungenentzündung“ oder „klinischer Eindruck eines Asthmaanfalls“
#Ist also eine vorläufige Diagnose oder ein Verdachtsmoment.

impressions = [
    "Hinweis auf Pneumonie", "wahrscheinlich virale Ursache", "unklares im Abdomen",
    "mögliche Fraktur", "Verdacht auf Infekt", "Hinweis auf Tumor",
    "Verdacht auf Pneumonie.",
    "Klinischer Eindruck eines akuten Asthmaanfalls.",
    "Wahrscheinlich virale Infektion.",
    "Verdacht auf chronisch obstruktive Lungenerkrankung (COPD)."
]



occupations = [
  "Gärtner", "Bäcker", "Metzger", "Professor", "Student", "Arbeitslose",
  "Händler", "Kaufmann", "Kauffrau", "Studentin", "Verkäuferin",
  "Lehrer", "Ärztin", "Ingenieur", "Friseur", "Journalist", "Sekretärin",
  "Arzt", "Ingenieur", "Polizist", "Koch", "Pfleger", "Krankenschwester", 
  "Techniker", "Elektriker", "Kaufmann","Kauffrau", "Projektmanager"
]

family_members = [
  "Familie","Bruder", "Schwester", "Mutter", "Vater", "Großvater", "Großmutter", "Enkel", "Enkelin","Schwiegertöchter",
  "Onkel", "Kind", "Kinder", "Sohn", "Tochter", "Cousine", "Neffe", "Nichte", "Witwe", "Eltern","Schwiegersohn", "Angehörige"
]

Arztbrief=					   "Arztbrief"
Befundbericht=                 "Befundbericht"
Operationsbericht=             "Operationsbericht"
Entlassungsbericht=            "Entlassungsbericht"
Anamnesebogen=                 "Anamnesebogen"
Radiologischer_Befund=         "Radiologischer Befund"
Laborbericht=                  "Laborbericht"
Pathologischer_Befund=         "Pathologischer Befund"
Überweisungsschein=            "Überweisungsschein"
Einwilligungserklärung=        "Einwilligungserklärung"
Impfpass=                      "Impfpass"
Rezept=                        "Rezept"
Therapieplan=                  "Therapieplan"
Pflegedokumentation=           "Pflegedokumentation"
OP_Freigabe=                   "OP-Freigabe"
Krankenhausaufnahmebogen=      "Krankenhausaufnahmebogen"
Heil_und_Kostenplan=          "Heil- und Kostenplan (HKP)"
Attest=                        "Attest"
Notfallbericht=                "Notfallbericht"
EKG_Befund=                    "EKG-Befund"
Roentgenbericht=               "Röntgenbericht"
CT_MRT_Befund=                 "CT-/MRT-Befund"
Pflegeüberleitungsbogen=       "Pflegeüberleitungsbogen"
RehaAntrag=                   "Reha-Antrag"
SozialmedizinischesGutachten= "Sozialmedizinisches Gutachten"

document_types = [
    Arztbrief,					
    Befundbericht,              
    Operationsbericht,          
    Entlassungsbericht,         
    Anamnesebogen,              
    Radiologischer_Befund,      
    Laborbericht,               
    Pathologischer_Befund,      
    Überweisungsschein,         
    Einwilligungserklärung,     
    Impfpass,                   
    Rezept,                     
    Therapieplan,               
    Pflegedokumentation,        
    OP_Freigabe,                
    Krankenhausaufnahmebogen,   
    Heil_und_Kostenplan,       
    Attest,                     
    Notfallbericht,             
    EKG_Befund,                 
    Roentgenbericht,            
    CT_MRT_Befund,              
    Pflegeüberleitungsbogen,    
    RehaAntrag,                 
    SozialmedizinischesGutachten
]

family_status = ["verheiratet", "geschieden", "verwitwet", "ledig", "getrennt", "in einer Beziehung", "alleinstehend"]

