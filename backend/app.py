import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, request, jsonify, send_from_directory,send_file
from scripts.predictions_ner import ner_model
from scripts.text_extractor import extract_text_from_image, extract_text
from werkzeug.utils import secure_filename
from scripts.utils import validate_ner_sample_smart
from pdf2image import convert_from_path
# Use absolute path for frontend directory
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend"))

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')


@app.route("/")
def home_page():
    return send_file(os.path.join(FRONTEND_DIR, "home.html"))

#editor

@app.route("/editor")
def editor_page():
    return send_file(os.path.join(FRONTEND_DIR, "editor.html"))

@app.route("/validate_sample", methods=["POST"])
def validate_sample():
    data = request.get_json()
    tokens = data.get("tokens", [])
    ner_tags = data.get("ner_tags", [])

    errors = validate_ner_sample_smart(tokens, ner_tags)

    return jsonify({"valid": len(errors) == 0, "errors": errors})


#predictor
@app.route("/predictor")
def predictor_page():
    return send_file(os.path.join(FRONTEND_DIR, "predictor.html"))

@app.route("/load_model", methods=["POST"])
def load_model_route():   
    if not ner_model.is_ready():
        ner_model.load()
        return jsonify({"status": "Model loaded"}), 200
    return jsonify({"status": "Model already loaded"}), 200



@app.route("/upload-text", methods=["POST"])
def upload_text_file():
    uploaded_file = request.files.get("file")
    if not uploaded_file:
        return jsonify({"error": "No file uploaded"}), 400

    os.makedirs("tmp", exist_ok=True)
    filename = secure_filename(uploaded_file.filename)
    temp_path = os.path.join("tmp", uploaded_file.filename)
    uploaded_file.save(temp_path)

    text = extract_text(temp_path)

    if text and len(text.strip()) >= 20:
        os.remove(temp_path)
        return jsonify({"text": text})

# Fallback: zu "upload_image_logic" springen
    if filename.lower().endswith(".pdf"):
        return process_pdf_as_images(temp_path, filename)
    
    os.remove(temp_path)
    return jsonify({"error": "No extractable text or image fallback available"}), 400

def process_pdf_as_images(pdf_path, original_filename):
    """Gemeinsame Funktion zum Konvertieren von PDFs in Bilder"""
    image_urls = []
    try:
        images = convert_from_path(pdf_path, dpi=150)
        for i, img in enumerate(images):
            image_name = f"{original_filename}_page{i+1}.jpg"
            image_path = os.path.join("tmp", f"{image_name}")
            img.save(image_path)
            image_urls.append(f"/uploads/{os.path.basename(image_path)}")
    except Exception as e:
        print(f"Fehler bei PDF → Bild Konvertierung: {e}")
        return jsonify({"error": "PDF to image conversion failed"}), 500
    finally:
        os.remove(pdf_path)

    return jsonify({
        "image_urls": image_urls,
        "num_pages": len(image_urls),
        "fallback": True  # Signal an Frontend, dass es kein Text war
    })



@app.route("/upload-image", methods=["POST"])
def upload_image_file():
    uploaded_file = request.files.get("file")
    if not uploaded_file:
        return jsonify({"error": "No file uploaded"}), 400

    os.makedirs("tmp", exist_ok=True)
    temp_path = os.path.join("tmp", uploaded_file.filename)
    uploaded_file.save(temp_path)

    ext = os.path.splitext(temp_path)[1].lower()
    image_urls = []
    if ext == ".pdf":
        images = convert_from_path(temp_path, dpi=150)
        for i, img in enumerate(images):
            image_path = os.path.join("tmp", f"{uploaded_file.filename}_page{i+1}.jpg")
            img.save(image_path)
            image_urls.append(f"/uploads/{os.path.basename(image_path)}")

    os.remove(temp_path)

    return jsonify({
        "image_urls": image_urls,
        "num_pages": len(image_urls)
    })

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400

    raw_predictions =  ner_model.predict(text)


    for ent in raw_predictions:
        ent['score'] = float(ent['score'])

    return jsonify({'entities': raw_predictions})



#layout editor
@app.route("/layout_editor")
def layout_editor_page():
    return send_file(os.path.join(FRONTEND_DIR, "layout_editor.html"))


@app.route("/extract-text", methods=["POST"])
def extract_text_from_rois():
    from PIL import Image
    data = request.get_json()
    image_url = data.get("image_url")
    zones = data.get("zones")

    if not image_url or not zones:
        return jsonify({"error": "Fehlende Parameter: image_url oder zones"}), 400

    filename = os.path.basename(image_url)
    local_image_path = os.path.join("tmp", filename)

    if not os.path.exists(local_image_path):
        return jsonify({"error": "Bild nicht gefunden"}), 404

    img = Image.open(local_image_path)

    results = []
    for zone in zones:
        x, y, w, h = map(int, (zone["x"], zone["y"], zone["width"], zone["height"]))
        roi_img = img.crop((x, y, x + w, y + h))

        # Da extract_text_from_image expects a path, wir machen hier einen Workaround:
        # Speichern temporär die ROI als Bild in den tmp-Ordner und dann auslesen
        temp_roi_path = os.path.join("tmp", f"roi_{zone['name']}.png")
        roi_img.save(temp_roi_path)

        text = extract_text_from_image(temp_roi_path)

        try:
            os.remove(temp_roi_path)
        except Exception as e:
            print(f"Fehler beim Löschen temporärer ROI-Datei: {e}")

        results.append({"name": zone["name"], "text": text.strip()})

    return jsonify(results)




@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("frontend", path)

@app.route("/uploads/<path:filename>")
def uploaded_files(filename):
    tmp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../tmp"))
    return send_from_directory(tmp_dir, filename)



if __name__ == "__main__":
    app.run(debug=True, port=8000)
