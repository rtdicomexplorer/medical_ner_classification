let allSamples = [];

const fileInput = document.getElementById("fileInput");
const sampleSelector = document.getElementById("sampleSelector");
const selectorContainer = document.getElementById(
    "sampleSelectorContainer"
);
const jsonPreview = document.getElementById("jsonPreview");
const entityViewer = document.getElementById("entityViewer");
const labelLegend = document.getElementById("labelLegend");

fileInput.addEventListener("change", async (e) => {
    const file = e.target.files[0];
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
    sampleSelector.innerHTML = "";
    allSamples.forEach((_, i) => {
        const option = document.createElement("option");
        option.value = i;
        option.textContent = `Sample ${i + 1}`;
        sampleSelector.appendChild(option);
    });

    renderLegend();
    displaySample(0);
});

sampleSelector.addEventListener("change", () => {
    const idx = parseInt(sampleSelector.value, 10);
    displaySample(idx);
});

function renderLegend() {
    const types = extractEntityTypes(ID2LABEL);
    labelLegend.innerHTML = "";
    types.forEach((type) => {
        const color = colorFromString(type);
        const label = document.createElement("span");
        label.textContent = type;
        label.style.background = color;
        label.style.padding = "4px 8px";
        label.style.borderRadius = "4px";
        label.style.fontSize = "0.9rem";
        label.style.color = "#333";
        label.style.border = "1px solid #ccc";
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

function colorFromString(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    const hue = hash % 360;
    return `hsl(${hue}, 65%, 75%)`;
}

function displaySample(index) {
    const data = allSamples[index];
    const { tokens, ner_tags } = data;
    jsonPreview.textContent = JSON.stringify(data, null, 2);
    entityViewer.innerHTML = "";

    const labelData = ner_tags.map((id) => ID2LABEL[id] || "O");
    const container = document.createElement("span");

    let i = 0;
    while (i < tokens.length) {
        const label = labelData[i];
        if (label === "O") {
            container.append(tokens[i] + " ");
            i++;
        } else if (label.startsWith("B-")) {
            const entityType = label.slice(2);
            let phrase = tokens[i];
            let j = i + 1;
            while (j < tokens.length && labelData[j] === `I-${entityType}`) {
                phrase += " " + tokens[j];
                j++;
            }

            const span = document.createElement("span");
            span.className = "entity";
            span.textContent = phrase;
            span.style.background = colorFromString(entityType);
            span.title = entityType;
            container.append(span, " ");
            i = j;
        } else {
            container.append(tokens[i] + " ");
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