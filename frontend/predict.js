const ENTITY_COLORS = {
  ALCOHOL_CONSUMPTION: "#b1a3df",
  ADDRESS: "#bdd1c2",
  ADMISSION_DATE: "#c0c70a",
  ANAMNESE: "#d1cdbdff",
  ALLERGY: "#b5c4ec",
  BIRTHDATE: "#c359cc",
  BLOOD_TYPE: "#d029a4",
  BODY_PART: "#add0e7",
  COURSE: "#e98788",
  DATE: "#ca143a",
  DEPARTMENT: "#199aef",
  DEVICE: "#d2231e",
  DIAGNOSIS: "#911593",
  DISCHARGE_DATE: "#9fe7e4",
  DOCTOR: "#57e665",
  DOCUMENT_TYPE: "#f5716f",
  DOSAGE: "#f6bf96",
  DURATION: "#269323",
  FAMILY_STATUS: "#03d080",
  FAMILYMEMBER: "#8facdf",
  FAMHIST: "#1ca2fc",
  FINDING: "#e5a6b4",
  FOLLOWUP_REASON: "#f556ad",
  FOLLOWUP_REQ: "#56cb78",
  FREQUENCY: "#e31919",
  GENDER: "#d0d17e",
  GEWICHT: "#519451",
  GROESSE: "#40bb55",
  HOSPITAL_STAY: "#5a8b08",
  ICD10_CODE: "#c76f07",
  ICD10_DESC: "#d381c2",
  IMMUNIZATION: "#3066ed",
  IMPRESSION: "#d44cbe",
  INSURANCE_ID: "#b46e98",
  LAB_RESULT: "#466af6",
  LIFESTYLE: "#7882b6",
  MEDICATION: "#e2ec82",
  OCCUPATION: "#c0a0db",
  ORG: "#f52243",
  PERSON: "#b1de4c",
  PHONE: "#dab744",
  PID: "#9da5b2",
  PREV_DIAGNOSIS: "#09f5eb",
  PROCEDURE: "#c1defa",
  RISKFACTOR: "#d3d678",
  ROOM_NUMBER: "#b52f3d",
  ROUTE: "#b390c7",
  SMOKING_STATUS: "#9182fa",
  STAY_REASON: "#adec71",
  SYMPTOM: "#08e843",
  TREATMENT: "#c1d89a",
  VITALSIGNS: "#24d332"
};

const loadBtn = document.getElementById("load-btn");
const predictBtn = document.getElementById("predict-btn");
const clearBtn = document.getElementById("clear-btn");
const fileInput = document.getElementById("fileInput");
const fileNameDisplay = document.getElementById("fileNameDisplay");

loadBtn.addEventListener("click", async () => {
  loadBtn.disabled = true;
  loadBtn.innerText = "Loading...";

  try {
    const response = await fetch("/load_model", { method: "POST" });
    const result = await response.json();

    if (result.status.includes("loaded")) {
      // Modell geladen → Predict zeigen
      predictBtn.style.display = "inline-block";
      loadBtn.innerText = "Model Loaded";
      loadBtn.disabled = true;
      predictBtn.disabled = true;


    }
  } catch (err) {
    alert("Fehler beim Laden des Modells");
    loadBtn.disabled = false;
    loadBtn.innerText = "Load Model";

  }
});

// ============ Predict ============
predictBtn.addEventListener("click", async () => {
  const inputText = document.getElementById("input-text").innerText;

  if (!inputText.trim()) {
    alert("Bitte Text eingeben oder hochladen.");
    return;
  }

  predictBtn.innerText = "Predicting...";
  predictBtn.disabled = true;

  const response = await fetch("/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: inputText })
  });

  const data = await response.json();
  const entities = data.entities || [];

  renderHighlights(inputText, entities);
  renderTable(entities);

  // Nach Prediction → Clear-Button anzeigen
  clearBtn.style.display = "inline-block";

  predictBtn.innerText = "Predicted";
  
});

// ============ Clear ============
clearBtn.addEventListener("click", () => {
  document.getElementById("input-text").innerText = "";
  document.getElementById("annotated-text").innerHTML = "";
  document.querySelector("#results-table tbody").innerHTML = "";

  clearBtn.style.display = "none";
});






fileInput.addEventListener('change', async function () {
  const file = this.files[0];
  fileNameDisplay.textContent = file ? file.name : "No file selected";
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("/upload", {
    method: "POST",
    body: formData
  });

  const data = await response.json();
  if (data.text) {
    document.getElementById('input-text').innerText = data.text;

    predictBtn.disabled = false
    predictBtn.innerText = "Predict"
  } else {
    alert("Failed to extract text");
  }
});



function renderHighlights(text, entities) {
  // Sort entities by start to process in order
  entities.sort((a, b) => a.start - b.start);

  let result = "";
  let currentIndex = 0;

  for (const ent of entities) {
    // Append plain text before the entity
    result += escapeHTML(text.slice(currentIndex, ent.start));

    const color = ENTITY_COLORS[ent.entity_group] || "#ccc";
    const entityText = escapeHTML(text.slice(ent.start, ent.end));

    result += `<span class="highlight" style="background-color: ${color}" title="${ent.entity_group}">${entityText}</span>`;

    currentIndex = ent.end;
  }

  // Add remaining text after last entity
  result += escapeHTML(text.slice(currentIndex));

  //document.getElementById("input-text").innerHTML = result;
  document.getElementById("annotated-text").innerHTML = result;
}

function renderTable(entities) {
  const tbody = document.getElementById("results-table").querySelector("tbody");
  tbody.innerHTML = "";

  entities.forEach(ent => {
    const color = ENTITY_COLORS[ent.entity_group] || "#ccc";

    const row = document.createElement("tr");
    row.style.backgroundColor = color;
    const cellGroup = document.createElement("td");
    const cellWord = document.createElement("td");

    cellGroup.textContent = ent.entity_group;
    cellWord.textContent = ent.word;

    row.appendChild(cellGroup);
    row.appendChild(cellWord);
    tbody.appendChild(row);
  });
}

function escapeHTML(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}