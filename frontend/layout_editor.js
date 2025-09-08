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

      fileInput.addEventListener("change", () => {
        const file = fileInput.files[0];
        if (!file) return;
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
            loadCurrentPage();
          });
      });

      function loadCurrentPage() {
        extractTextBtn.style.display = "inline-block";

        image.onload = () => {
          canvas.style.display = "block";
          scale = 1;
          originX = 0;
          originY = 0;

          canvas.width = image.width;
          canvas.height = image.height;
          if (!zonesByPage[currentPage]) zonesByPage[currentPage] = [];
          selectedZoneIndex = -1;
          updatePageInfo();
          updateZoneButtons();
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
        pageInfo.textContent = `Seite ${currentPage + 1}/${totalPages}`;
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
          ctx.font = `${16 / scale}px Arial`;
          ctx.fillStyle = ctx.strokeStyle;
          ctx.fillText(z.name, z.x + 5, z.y + 20 / scale);
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
      }

      // ROI zeichnen
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
            const zArr = zonesByPage[currentPage];
            let name = `zone_${zArr.length + 1}`,
              idx = 1;
            while (zArr.some((z) => z.name === name))
              name = `zone_${zArr.length + 1}_${idx++}`;
            zArr.push({ name, x, y, width: w, height: h });
            selectedZoneIndex = zArr.length - 1;
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

      // Text Extrahieren
      extractTextBtn.addEventListener("click", async () => {
        if (!Object.values(zonesByPage).some((zs) => zs.length)) {
          alert("Keine ROIs definiert");
          return;
        }

        extractedTextsDiv.textContent = "";
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
          data.forEach(
            (el) =>
              (extractedTextsDiv.textContent += `${el.name}:\n${el.text}\n\n`)
          );
        }
      });

      function updateZoneButtons() {
        const visible = selectedZoneIndex >= 0;
        saveBtn.style.display = visible ? "inline-block" : "none";
        deleteBtn.style.display = visible ? "inline-block" : "none";
        renameBtn.style.display = visible ? "inline-block" : "none";
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