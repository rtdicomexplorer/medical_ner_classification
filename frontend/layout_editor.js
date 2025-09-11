
const hamburger = document.getElementById('hamburger');
const navLinks = document.getElementById('navLinks');

hamburger.addEventListener('click', () => {
    navLinks.classList.toggle('show');
});

const fileInput = document.getElementById("fileInput");
const canvas = document.getElementById("drawCanvas");
const ctx = canvas.getContext("2d");

const zoomInBtn = document.getElementById("zoomInBtn");
const zoomOutBtn = document.getElementById("zoomOutBtn");
const resetViewBtn = document.getElementById("resetViewBtn");

const prevPageBtn = document.getElementById("prevPageBtn");
const nextPageBtn = document.getElementById("nextPageBtn");
const pageInfo = document.getElementById("pageInfo");

const saveBtn = document.getElementById("saveBtn");
const extractTextBtn = document.getElementById("extractTextBtn");

const extractedTextsDiv = document.getElementById("extractedTexts");
const splitter = document.getElementById("splitter");
const canvasContainer = document.getElementById("canvas-container");
const fileNameDisplay = document.getElementById("fileNameDisplay");

const spinnerOverlay = document.getElementById("loadingOverlay");//.style.display = "flex";
const clearBtn = document.getElementById("clearBtn");
const predictBtn = document.getElementById("predictBtn");
const renameBtn = document.getElementById("renameBtn");

predictBtn.addEventListener("click", async () => {

    const text = extractedTextsDiv.innerText;
    if (!text.trim()) {
        alert("Please load a report or insert a text!");
        return;
    }

    const response = await fetch("/predict-text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text })
    });


    const data = await response.json();
    console.log(data)
    if (data.fallback && data.text) {
        // redirect the text to prediction page
        sessionStorage.setItem("text_extracted", JSON.stringify(data.text));
        window.location.href = "/predictor";
    } else {

        alert("No text could be extracted.");
    }
    const entities = data.entities || [];

    console.log("retun from predict text", entities)

});


clearBtn.addEventListener("click", () => {
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    canvas.width = 0;
    canvas.height = 0;

    // Clear extracted text
    extractedTextsDiv.innerHTML = "<em>text preview</em>";

    // Reset zones
    zonesByPage = {};
    imagePages = [];
    currentPage = 0;
    totalPages = 0;

    // Hide UI parts
    document.getElementById("main-split-container").style.display = "none";
    document.getElementById("footerbar").style.display = "none";
    extractTextBtn.style.display = "none";
    clearBtn.style.display = "none";
    saveBtn.style.display = "none";
    deleteBtn.style.display = "none";
    renameBtn.style.display = "none";

    // Reset file name display
    fileNameDisplay.textContent = "No file selected";
    fileInput.value = "";
    // Optional: Reset zoom, transforms, etc.
    scale = 1;
    originX = 0,
        originY = 0;
});


let isResizing = false;
// State
let currentPage = 0;
let totalPages = 0;
let imagePages = [];
let zonesByPage = {};
let scale = 1,
    originX = 0,
    originY = 0;

let isDrawing = false,
    startX = 0,
    startY = 0,
    currentX = 0,
    currentY = 0;
let isPanning = false,
    panStartX = 0,
    panStartY = 0;
let selectedZoneIndex = -1;
const image = new Image();


function updateZoomDisplay() {
    const zoomLabel = document.getElementById("zoomLevel");
    zoomLabel.textContent = `Zoom: ${Math.round(scale * 100)}%`;
}

splitter.addEventListener("mousedown", (e) => {
    isResizing = true;
    document.body.style.cursor = "col-resize";
    e.preventDefault(); // prevent text selection
});


const storedImageUrls = sessionStorage.getItem("image_urls");
const storedFileName = sessionStorage.getItem("file_name");

if (storedImageUrls && storedFileName) {
    // Reuse file upload flow without needing a file
    const parsedImageUrls = JSON.parse(storedImageUrls);
    if (parsedImageUrls.length === 0) {
        alert("Keine Bilder gefunden.");
    } else {
        imagePages = parsedImageUrls;
        totalPages = imagePages.length;
        currentPage = 0;
        zonesByPage = {};
        fileNameDisplay.textContent = storedFileName;
        document.getElementById("main-split-container").style.display = "flex";
        document.getElementById("footerbar").style.display = "block";
        extractTextBtn.style.display = "inline-block";
        clearBtn.style.display = "inline-block";

        loadCurrentPage();
    }

    // Clean up sessionStorage
    sessionStorage.clear();
}



fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];
    if (!file) return;

    spinnerOverlay.style.display = "flex";
    fileNameDisplay.textContent = file ? file.name : "no file selected";
    const formData = new FormData();
    formData.append("file", file);

    fetch("/upload-image", { method: "POST", body: formData })
        .then((res) => res.json())
        .then((data) => {
            if (!data.image_urls?.length)
                return alert("Keine Seiten gefunden.");
            imagePages = data.image_urls;
            totalPages = imagePages.length;
            currentPage = 0;
            zonesByPage = {};
            document.getElementById("main-split-container").style.display =
                "flex";
            document.getElementById("footerbar").style.display = "block";
            extractTextBtn.style.display = "inline-block"; // ← NEU!
            clearBtn.style.display = "inline-block";
            loadCurrentPage();
            spinnerOverlay.style.display = "none";
        });


});

function loadCurrentPage() {
    extractTextBtn.style.display = "inline-block";
    clearBtn.style.display = "inline-block";

    image.onload = () => {
        canvas.style.display = "block";
        // scale = 1;
        originX = 0;
        originY = 0;

        canvas.width = image.width;
        canvas.height = image.height;
        if (!zonesByPage[currentPage]) zonesByPage[currentPage] = [];
        selectedZoneIndex = -1;
        updatePageInfo();
        redraw();
    };
    image.src = imagePages[currentPage];
}

prevPageBtn.addEventListener("click", () => {
    if (currentPage > 0) loadCurrentPage(--currentPage);
});
nextPageBtn.addEventListener("click", () => {
    if (currentPage < totalPages - 1) loadCurrentPage(++currentPage);
});

function updatePageInfo() {
    pageInfo.textContent = `Page ${currentPage + 1}/${totalPages}`;
}

function getTransformedPoint(cx, cy) {
    const rect = canvas.getBoundingClientRect();
    return {
        x: (cx - rect.left - originX) / scale,
        y: (cy - rect.top - originY) / scale,
    };
}

function redraw(preview = false) {
    ctx.setTransform(scale, 0, 0, scale, originX, originY);
    ctx.clearRect(
        -originX / scale,
        -originY / scale,
        canvas.width / scale,
        canvas.height / scale
    );
    ctx.drawImage(image, 0, 0);

    const zones = zonesByPage[currentPage] || [];
    zones.forEach((z, i) => {
        ctx.strokeStyle = i === selectedZoneIndex ? "red" : "blue";
        ctx.lineWidth = 2 / scale;
        ctx.strokeRect(z.x, z.y, z.width, z.height);
        ctx.font = `${12 / scale}px Arial`;
        ctx.fillStyle = ctx.strokeStyle;
        ctx.fillText(z.name, z.x + 2, z.y - 5 / scale);
    });

    if (isDrawing && preview) {
        const x = Math.min(startX, currentX),
            y = Math.min(startY, currentY);
        const w = Math.abs(currentX - startX),
            h = Math.abs(currentY - startY);
        ctx.fillStyle = "rgba(0,0,255,0.2)";
        ctx.strokeStyle = "blue";
        ctx.fillRect(x, y, w, h);
        ctx.strokeRect(x, y, w, h);
    }

    updateZoomDisplay();
}

// ROI tracing
canvas.addEventListener("mousedown", (e) => {
    if (e.button === 0) {
        const p = getTransformedPoint(e.clientX, e.clientY);
        startX = p.x;
        startY = p.y;
        isDrawing = true;
        selectedZoneIndex = -1;
    } else if (e.button === 2) {
        // Pan
        isPanning = true;
        panStartX = e.clientX - originX;
        panStartY = e.clientY - originY;
        canvas.style.cursor = "grab";
    }
});

canvas.addEventListener("mousemove", (e) => {
    if (isDrawing) {
        const p = getTransformedPoint(e.clientX, e.clientY);
        currentX = p.x;
        currentY = p.y;
        redraw(true);
    } else if (isPanning) {
        originX = e.clientX - panStartX;
        originY = e.clientY - panStartY;
        redraw();
    }
});

canvas.addEventListener("mouseup", (e) => {
    if (isDrawing) {
        isDrawing = false;
        const x = Math.min(startX, currentX),
            y = Math.min(startY, currentY);
        const w = Math.abs(currentX - startX),
            h = Math.abs(currentY - startY);
        if (w > 5 && h > 5) {
            let zArr = zonesByPage[currentPage];
            let name = `zone_${zArr.length + 1}`,
                idx = 1;
            while (zArr.some((z) => z.name === name))
                name = `zone_${zArr.length + 1}_${idx++}`;
            zArr.push({ name, x, y, width: w, height: h });
            selectedZoneIndex = zArr.length - 1;
            if (zArr.length > 1) {
                zArr = zArr.sort((a, b) => {
                    if (a.y !== b.y) {
                        return a.y - b.y; // Primary sort by y
                    } else {
                        return a.x - b.x; // Secondary sort by x
                    }
                });
            }

            redraw();
            updateZoneButtons();
        }
    } else {
        isPanning = false;
        canvas.style.cursor = "crosshair";
    }
});

canvas.addEventListener("contextmenu", (e) => {
    e.preventDefault();
    const p = getTransformedPoint(e.clientX, e.clientY);
    const zArr = zonesByPage[currentPage];
    selectedZoneIndex = -1;
    for (let i = zArr.length - 1; i >= 0; i--) {
        const z = zArr[i];
        if (
            p.x >= z.x &&
            p.x <= z.x + z.width &&
            p.y >= z.y &&
            p.y <= z.y + z.height
        ) {
            selectedZoneIndex = i;
            break;
        }
    }
    redraw();
    updateZoneButtons();
});

// Zoom Buttons
zoomInBtn.onclick = () => {
    scale = Math.min(scale * 1.2, 10);
    redraw();
};
zoomOutBtn.onclick = () => {
    scale = Math.max(scale / 1.2, 0.1);
    redraw();
};
resetViewBtn.onclick = () => {
    scale = 1;
    originX = 0;
    originY = 0;
    redraw();

};

// Text extraction
extractTextBtn.addEventListener("click", async () => {
    if (!Object.values(zonesByPage).some((zs) => zs.length)) {
        alert("No ROIs");
        return;
    }

    extractedTextsDiv.textContent = "";
    spinnerOverlay.style.display = "flex";
    for (let page = 0; page < imagePages.length; page++) {
        const zs = zonesByPage[page] || [];
        if (!zs.length) continue;

        const res = await fetch("/extract-text", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ image_url: imagePages[page], zones: zs }),
        });
        if (!res.ok) {
            alert(`Error on page ${page + 1}`);
            break;
        }
        const data = await res.json();
        extractedTextsDiv.textContent += `=== Seite ${page + 1} ===\n`;
    //    extractedTextsDiv.textContent+= `${data}\n`;    
        data.forEach(
            (el) =>
                (extractedTextsDiv.textContent += `${el.name}:\n${el.text}\n\n`)
        );
    }

    predictBtn.style.display = extractedTextsDiv.innerText !== "" ? 'inline-block' : 'none';
    spinnerOverlay.style.display = "none";
});

function updateZoneButtons() {
    const visible = selectedZoneIndex >= 0;
    saveBtn.style.display = visible ? "inline-block" : "none";
    deleteBtn.style.display = visible ? "inline-block" : "none";
    //renameBtn.style.display = visible ? "inline-block" : "none";
}

saveBtn.addEventListener("click", () => {
    if (selectedZoneIndex >= 0) {
        alert("Zone gespeichert.");
    }
});

deleteBtn.addEventListener("click", () => {
    if (selectedZoneIndex >= 0) {
        const zones = zonesByPage[currentPage];
        zones.splice(selectedZoneIndex, 1);
        selectedZoneIndex = -1;
        redraw();
        updateZoneButtons();
    }
});

renameBtn.addEventListener("click", () => {
    if (selectedZoneIndex >= 0) {
        const zones = zonesByPage[currentPage];
        const currentName = zones[selectedZoneIndex].name;
        const newName = prompt("Neuer Name der Zone:", currentName);
        if (newName && !zones.some((z) => z.name === newName)) {
            zones[selectedZoneIndex].name = newName;
            redraw();
        } else {
            alert("Ungültiger oder bereits vorhandener Name.");
        }
    }
});

window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
        selectedZoneIndex = -1;
        redraw();
        updateZoneButtons();
    }
});

window.addEventListener("mousemove", (e) => {
    if (!isResizing) return;

    // Calculate new width for left panel (canvasContainer)
    // based on mouse X relative to the parent container
    const container = document.getElementById("main-split-container");
    const containerRect = container.getBoundingClientRect();

    let newWidth = e.clientX - containerRect.left;

    // Optional: set min and max widths to avoid panels collapsing
    const minWidth = 100;
    const maxWidth = containerRect.width - 150; // leave room for right panel

    if (newWidth < minWidth) newWidth = minWidth;
    if (newWidth > maxWidth) newWidth = maxWidth;

    canvasContainer.style.flex = "none";
    canvasContainer.style.width = newWidth + "px";

    extractedTextsDiv.style.width = (containerRect.width - newWidth - splitter.offsetWidth) + "px";

    // Optional: redraw canvas if needed after resizing
    redraw();
});

window.addEventListener("mouseup", () => {
    if (isResizing) {
        isResizing = false;
        document.body.style.cursor = "default";
    }
});
