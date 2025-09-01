
let currentlyHighlightedType = null;
let allSamples = [];
const ENTITY_COLORS = {
    ADDRESS: "#bdd1c2ff",
    ADMISSION_DATE: "#c0c70a",
    ALCOHOL_CONSUMPTION: "#b1a3dfff",
    ALLERGY: "#b5c4ecff",
    ANAMNESE: "#d1cdbdff",
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


const saveAllBtn = document.getElementById("saveFile");
const validateBtn = document.getElementById("validateButton");

const saveSampleAsTextBtn = document.getElementById("save-sample-text")

saveSampleAsTextBtn.addEventListener("click", async () => {


    if (currentSampleAsText !== '') {
        const blob = new Blob([currentSampleAsText], { type: "text/plain" });

        // Create a temporary link element
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = "sample.txt"; // File name

        // Trigger the download
        document.body.appendChild(link);
        link.click();

        // Cleanup
        document.body.removeChild(link);
        URL.revokeObjectURL(link.href);
    }


});


validateBtn.addEventListener("click", async () => {


    const index = parseInt(sampleSelector.value, 10);
    const sample = allSamples[index];

    const response = await fetch("/validate_sample", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(sample),
    });

    const result = await response.json();
    const resultSpan = document.getElementById("validationResult");

    if (response.ok && result.valid) {
        resultSpan.textContent = "✅ Sample is valid!";
        resultSpan.style.color = "green";
    } else {
        resultSpan.textContent = "❌ " + (result.errors || []).join(" | ");
        resultSpan.style.color = "red";
    }

});

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


    saveAllBtn.style.display = "block";
    displaySample(0);
});

sampleSelector.addEventListener("change", () => {
    const idx = parseInt(sampleSelector.value, 10);
    displaySample(idx);
});
function removeEntityHighlights() {
    console.log('removeEntityHighlights')
    document.querySelectorAll(".entity").forEach((el) => {
        el.classList.remove("highlighted-entity");
    });
}

function highlightEntitiesOfType(type) {
    console.log('highlightEntitiesOfType', type)
    removeEntityHighlights(); // Clear previous highlights

    document.querySelectorAll(".entity").forEach((el) => {
        if (el.dataset.entityType === type) {
            el.classList.add("highlighted-entity");
        }
    });
}

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
            label.classList.add("active-legend");
            //label.style.fontWeight = "bold";
            label.style.border = "2px solid black";

            label.addEventListener("click", () => {
                if (currentlyHighlightedType === type) {
                    // Unselect if already selected
                    removeEntityHighlights();
                    label.style.fontWeight = "";
                    currentlyHighlightedType = null;
                } else {
                    // Highlight new type
                    highlightEntitiesOfType(type);
                    currentlyHighlightedType = type;
                    label.classList.add("active-legend");
                    label.style.fontWeight = "bold";
                }
            });

        } else {
            label.classList.add("inactive-legend");
        }

        labelLegend.appendChild(label);
    });
}

function highlightEntitiesByType(entityType) {
    document.querySelectorAll(".entity").forEach(span => {
        const type = span.getAttribute("data-entity");
        if (!entityType || type === entityType) {
            span.classList.add("highlighted");
        } else {
            span.classList.remove("highlighted");
        }
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

    var text = [];
    currentSampleAsText = "";
    // Reset validation output
    const resultSpan = document.getElementById("validationResult");
    if (resultSpan) {
        resultSpan.textContent = "🧪 validation state";
        //resultSpan.className = "";
        resultSpan.style.color = "gray";
    }
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

    updateJsonPreview(data);
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
            span.dataset.entityType = entityType;
            span.className = "entity";
            span.textContent = phrase;
            span.style.background = ENTITY_COLORS[entityType] || "#d3d3d3";
            span.setAttribute("data-entity", entityType);

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
        text.push(tokens[i]);
        const tr = document.createElement("tr");

        const tdIndex = document.createElement("td");
        tdIndex.textContent = '' + i;

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
            const type = label.split('-')[1];
            if (label === currentLabel) option.selected = true;
            option.style.backgroundColor = ENTITY_COLORS[type] || "#ddd";
            select.appendChild(option);
        });
        const selectedOption = select.options[select.selectedIndex];
        select.style.backgroundColor = selectedOption.style.backgroundColor;

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
            const selectedOption = select.options[select.selectedIndex];
            select.style.backgroundColor = selectedOption.style.backgroundColor;
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

        tr.append(tdIndex, tdToken, tdId, tdLabel, tdDelete);
        tokenTableBody.appendChild(tr);
    });
    currentSampleAsText = text.join(' ');
    console.log(currentSampleAsText);
    currentlyHighlightedType = null;
    removeEntityHighlights();

}

let currentSampleAsText = "";


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



function downloadCurrentSample() {
    const selectedIndex = parseInt(sampleSelector.value, 10);
    const sample = allSamples[selectedIndex];

    const blob = new Blob([JSON.stringify(sample, null, 2)], {
        type: "application/json",
    });

    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `sample_${selectedIndex + 1}.json`;
    a.click();
    URL.revokeObjectURL(url);
}



function updateJsonPreview(data) {
    const formatted = JSON.stringify(data, null, 2);
    const lines = formatted.split("\n");

    const preview = document.getElementById("jsonPreview");
    const lineNumbers = document.getElementById("jsonLineNumbers");

    preview.textContent = formatted;
    lineNumbers.textContent = lines.map((_, i) => (i + 1)).join("\n");
}


document.getElementById("jsonPreview").addEventListener("scroll", (e) => {
    document.getElementById("jsonLineNumbers").scrollTop = e.target.scrollTop;
});
