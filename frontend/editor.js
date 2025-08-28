let allSamples = [];
const ENTITY_COLORS = {
    ADDRESS: "#bdd1c2ff",
    ADMISSION_DATE: "#c0c70a",
    ALCOHOL_CONSUMPTION: "#b1a3dfff",
    ALLERGY: "#b5c4ecff",
    ANAMNESE:"#d1cdbdff",
    BIRTHDATE: "#c359cc",
    BLOOD_TYPE: "#d029a4",
    BODY_PART: "#add0e7",
    COURSE: "#e98788",
    DATE: "#ca143a",
    DEPARTMENT: "#199aef",
    DEVICE: "#d2231e",
    DIAGNOSIS: "#911593",
    DISCHARGE_DATE: "#9fe7e4ff",
    DOCTOR: "#57e665",
    DOCUMENT_TYPE: "#f5716f",
    DOSAGE: "#f6bf96",
    DURATION: "#269323",
    FAMILY_STATUS: "#03d080",
    FAMILYMEMBER: "#8facdfff",
    FAMHIST: "#1ca2fcff",
    FINDING: "#e5a6b4ff",
    FOLLOWUP_REASON: "#f556ad",
    FOLLOWUP_REQ: "#56cb78",
    FREQUENCY: "#e31919",
    GENDER: "#d0d17e",
    GEWICHT: "#519451",
    GROESSE: "#40bb55",
    HOSPITAL_STAY: "#5a8b08",
    ICD10_CODE: "#c76f07",
    ICD10_DESC: "#d381c2ff",
    IMMUNIZATION: "#3066ed",
    IMPRESSION: "#d44cbe",
    INSURANCE_ID: "#b46e98",
    LAB_RESULT: "#466af6",
    LIFESTYLE: "#7882b6",
    MEDICATION: "#e2ec82ff",
    OCCUPATION: "#c0a0db",
    ORG: "#f52243",
    PERSON: "#b1de4c",
    PHONE: "#dab744ff",
    PID: "#9da5b2",
    PREV_DIAGNOSIS: "#09f5eb",
    PROCEDURE: "#c1defa",
    RISKFACTOR: "#d3d678ff",
    ROOM_NUMBER: "#b52f3d",
    ROUTE: "#b390c7ff",
    SMOKING_STATUS: "#9182fa",
    STAY_REASON: "#adec71ff",
    SYMPTOM: "#08e843",
    TREATMENT: "#c1d89aff",
    VITALSIGNS: "#24d332",
};

function RgbToHex(r, g, b) {
    return '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
}


const fileInput = document.getElementById("fileInput");
const sampleSelector = document.getElementById("sampleSelector");
const selectorContainer = document.getElementById(
    "sampleSelectorContainer"
);
const jsonPreview = document.getElementById("jsonPreview");
const entityViewer = document.getElementById("entityViewer");
const labelLegend = document.getElementById("labelLegend");
const fileNameDisplay = document.getElementById("fileNameDisplay");


fileInput.addEventListener("change", async (e) => {
    const file = e.target.files[0];
    fileNameDisplay.textContent = file ? file.name : "No file selected";
    if (!file) return;
  
    const text = await file.text();
    try {
        allSamples = JSON.parse(text);
    } catch (err) {
        jsonPreview.textContent = "❌ Invalid JSON format.";
        return;
    }

    if (
        !Array.isArray(allSamples) ||
        !allSamples[0]?.tokens ||
        !allSamples[0]?.ner_tags
    ) {
        jsonPreview.textContent =
            "❌ Expected a list of objects with `tokens` and `ner_tags`.";
        return;
    }

    selectorContainer.style.display = "block";
    document.getElementById("mainPanel").style.display = "block";

    sampleSelector.innerHTML = "";
    allSamples.forEach((_, i) => {
        const option = document.createElement("option");
        option.value = i;
        option.textContent = `Sample ${i + 1}`;
        sampleSelector.appendChild(option);
    });
    console.log("change event")
    displaySample(0);
});

sampleSelector.addEventListener("change", () => {
    const idx = parseInt(sampleSelector.value, 10);
    displaySample(idx);
});


function renderLegend(activeEntityTypes = []) {
    const types = extractEntityTypes(ID2LABEL);
    labelLegend.innerHTML = "";

    types.forEach((type) => {
        const color = ENTITY_COLORS[type] || "#ddd";
        const label = document.createElement("span");

        label.textContent = type;
        label.style.background = color;
        label.style.padding = "4px 8px";
        label.style.borderRadius = "4px";
        label.style.fontSize = "0.9rem";
        label.style.color = "#333";
        label.style.border = "1px solid #ccc";
        label.style.marginRight = "6px";
        label.style.display = "inline-block";

        if (activeEntityTypes.includes(type)) {
            label.style.fontWeight = "bold";
            label.style.border = "2px solid black";  // oder z. B. "#444"
        }

        labelLegend.appendChild(label);
    });
}



function extractEntityTypes(labelMap) {
    const types = new Set();
    Object.values(labelMap).forEach((label) => {
        if (label.startsWith("B-") || label.startsWith("I-")) {
            types.add(label.slice(2));
        }
    });
    return Array.from(types).sort();
}


function displaySample(index) {
    const data = allSamples[index];
    const { tokens, ner_tags } = data;
    const activeTypes = new Set();
    ner_tags.forEach((id) => {
        const label = ID2LABEL[id];
        if (label && (label.startsWith("B-") || label.startsWith("I-"))) {
            activeTypes.add(label.slice(2));
        }
    });
    renderLegend(Array.from(activeTypes));

    jsonPreview.textContent = JSON.stringify(data, null, 2);

    entityViewer.innerHTML = "";

    const labelData = ner_tags.map((id) => ID2LABEL[id] || "O");
    const container = document.createElement("span");

    let i = 0;
    while (i < tokens.length) {
        const label = labelData[i];

        if (label === "O") {
            container.append(document.createTextNode(tokens[i] + " "));
            i++;
            continue;
        }

        if (label.startsWith("B-")) {
            const entityType = label.slice(2);
            let phrase = tokens[i];
            let j = i + 1;
            let tooltipLabels = [`B-${entityType}`];

            while (j < tokens.length && labelData[j] === `I-${entityType}`) {
                phrase += " " + tokens[j];
                tooltipLabels.push(`I-${entityType}`);
                j++;
            }

            // Sichtbarer Text
            // ... im while-Block, wenn ein Entity erkannt wird
            const span = document.createElement("span");
            span.className = "entity";
            span.textContent = phrase;
            span.style.background = ENTITY_COLORS[entityType] || "#d3d3d3";

            // Tooltip Text (Option 2)
            const tooltip = document.createElement("span");
            tooltip.className = "tooltip-text";
            tooltip.textContent = `${entityType} (${tooltipLabels.length} token${tooltipLabels.length > 1 ? "s" : ""})`;

            // Wrapper mit Tooltip-Klasse
            const wrapper = document.createElement("span");
            wrapper.className = "tooltip";
            wrapper.style.position = "relative";
            wrapper.style.display = "inline-block";

            wrapper.appendChild(span);
            wrapper.appendChild(tooltip);

            container.append(wrapper, " ");
            i = j;

        }
        else {
            container.append(document.createTextNode(tokens[i] + " "));
            i++;
        }
    }

    entityViewer.appendChild(container);

    const tokenTableBody = document.getElementById("tokenTableBody");
    tokenTableBody.innerHTML = "";

    tokens.forEach((token, i) => {
        const tr = document.createElement("tr");

        const tdToken = document.createElement("td");
        tdToken.textContent = token;

        const tdId = document.createElement("td");
        tdId.textContent = ner_tags[i];

        const tdLabel = document.createElement("td");
        const select = document.createElement("select");

        const currentLabel = ID2LABEL[ner_tags[i]] || "O";

        Object.entries(ID2LABEL).forEach(([id, label]) => {
            const option = document.createElement("option");
            option.value = id;
            option.textContent = label;
            if (label === currentLabel) option.selected = true;
            select.appendChild(option);
        });

        select.addEventListener("change", () => {
            const oldTag = data.ner_tags[i];
            const oldLabel = ID2LABEL[oldTag];
            const newTag = parseInt(select.value, 10);
            const newLabel = ID2LABEL[newTag];

            data.ner_tags[i] = newTag;

            if (oldLabel.startsWith("B-")) {
                const oldEntity = oldLabel.slice(2);

                if (newLabel === "O") {
                    // Changed B-XXX to O, so all consecutive I-XXX become O
                    let j = i + 1;
                    while (
                        j < data.tokens.length &&
                        ID2LABEL[data.ner_tags[j]] === `I-${oldEntity}`
                    ) {
                        data.ner_tags[j] =
                            parseInt(getKeyByValue(ID2LABEL, "O")) || 0;
                        j++;
                    }
                } else if (newLabel.startsWith("B-")) {
                    // Changed B-OLD to B-NEW, update all I-OLD to I-NEW
                    const newEntity = newLabel.slice(2);
                    let j = i + 1;
                    while (
                        j < data.tokens.length &&
                        ID2LABEL[data.ner_tags[j]] === `I-${oldEntity}`
                    ) {
                        data.ner_tags[j] =
                            parseInt(getKeyByValue(ID2LABEL, `I-${newEntity}`)) ||
                            data.ner_tags[j];
                        j++;
                    }
                }
            } else if (oldLabel === "O" && newLabel.startsWith("B-")) {
                // Changed O to B-ENTITY, extend entity span by turning following O's into I-ENTITY
                const newEntity = newLabel.slice(2);
                let j = i + 1;
                while (
                    j < data.tokens.length &&
                    ID2LABEL[data.ner_tags[j]] === "O"
                ) {
                    data.ner_tags[j] =
                        parseInt(getKeyByValue(ID2LABEL, `I-${newEntity}`)) ||
                        data.ner_tags[j];
                    j++;
                }
            }

            displaySample(index);
        });

        tdLabel.appendChild(select);

        // DELETE BUTTON COLUMN
        const tdDelete = document.createElement("td");
        const btnDelete = document.createElement("button");
        btnDelete.textContent = "Delete";
        btnDelete.style.cursor = "pointer";
        btnDelete.addEventListener("click", () => {
            data.tokens.splice(i, 1);
            data.ner_tags.splice(i, 1);
            displaySample(index);
        });
        tdDelete.appendChild(btnDelete);

        tr.append(tdToken, tdId, tdLabel, tdDelete);
        tokenTableBody.appendChild(tr);
    });
}

function getKeyByValue(obj, value) {
    return Object.keys(obj).find((key) => obj[key] === value);
}

function downloadCurrentState() {
    const blob = new Blob([JSON.stringify(allSamples, null, 2)], {
        type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "updated_ner_data.json";
    a.click();
    URL.revokeObjectURL(url);
}

// Tab functionality
document.querySelectorAll(".tab-button").forEach((btn) => {
    btn.addEventListener("click", () => {
        document
            .querySelectorAll(".tab-button")
            .forEach((b) => b.classList.remove("active"));
        document
            .querySelectorAll(".tab-content")
            .forEach((tab) => (tab.style.display = "none"));

        btn.classList.add("active");
        document.getElementById(btn.dataset.tab).style.display = "block";
    });
});