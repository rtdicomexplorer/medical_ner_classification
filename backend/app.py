import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, request, jsonify, send_from_directory,send_file
from scripts.predictions_ner import ner_model
from scripts.text_extractor import extract_text_from_image, extract_text
from werkzeug.utils import secure_filename
from scripts.utils import validate_ner_sample_smart, generate_ner_data, remove_folder
from pdf2image import convert_from_path
# Use absolute path for frontend directory
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend"))

TEMP_FOLDER = 'tmp'


from flask_cors import CORS

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)

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

    os.makedirs(TEMP_FOLDER, exist_ok=True)
    filename = secure_filename(uploaded_file.filename)
    temp_path = os.path.join(TEMP_FOLDER, uploaded_file.filename)
    uploaded_file.save(temp_path)

    text = extract_text(temp_path)

    if text and len(text.strip()) >= 20:
        os.remove(temp_path)
        return jsonify({"text": text})

# Fallback: to "upload_image_logic" jumping
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
            image_path = os.path.join(TEMP_FOLDER, f"{image_name}")
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

    os.makedirs(TEMP_FOLDER, exist_ok=True)
    temp_path = os.path.join(TEMP_FOLDER, uploaded_file.filename)
    uploaded_file.save(temp_path)

    ext = os.path.splitext(temp_path)[1].lower()
    image_urls = []
    if ext == ".pdf":
        images = convert_from_path(temp_path, dpi=150)
        for i, img in enumerate(images):
            image_path = os.path.join(TEMP_FOLDER, f"{uploaded_file.filename}_page{i+1}.jpg")
            img.save(image_path)
            print(f"Saved {image_path}!")
            image_urls.append(f"/uploads/{os.path.basename(image_path)}")
        os.remove(temp_path)
    elif ext in ['.jpg', '.jpeg', '.bmp','.png']:
        image_urls.append(f"/uploads/{uploaded_file.filename}")

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

    try:
        predictions =  ner_model.predict(text)
    except Exception as e:
        return jsonify({"error": e}), 500


    ner_data = generate_ner_data(text, predictions)
    for ent in predictions:
        ent['score'] = float(ent['score'])

    return jsonify({'entities': predictions, 'ner_data':ner_data})


@app.route("/predict-text", methods=["POST"])
def predict_text_from_rois():  
    data = request.get_json()  
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400

    return jsonify({
            "text": text,
            "fallback": True  # Signal an Frontend, dass es kein Text war
        })

#layout editor
@app.route("/layout_editor")
def layout_editor_page():
    return send_file(os.path.join(FRONTEND_DIR, "layout_editor.html"))

def build_text_by_rows_with_columns(rois, logical_width=1000, y_threshold=25):
    from collections import defaultdict

    # Group ROIs into rows based on Y position (within y_threshold)
    rows = defaultdict(list)
    for roi in rois:
        y = roi['y']
        assigned = False
        for row_y in rows:
            if abs(y - row_y) < y_threshold:
                rows[row_y].append(roi)
                assigned = True
                break
        if not assigned:
            rows[y].append(roi)

    # Sort rows by Y
    sorted_rows = sorted(rows.items(), key=lambda r: r[0])
    all_lines = []

    for _, row_rois in sorted_rows:
        # Sort ROIs left to right
        row_rois_sorted = sorted(row_rois, key=lambda r: r['x'])

        # Track text fragments to be merged for this row
        row_fragments = []

        for roi in row_rois_sorted:
            x_start = roi['x']
            indent_level = int((x_start / logical_width) * 80)
            indent = ' ' * indent_level

            # Preserve multiline text
            text_lines = roi['text'].splitlines()
            for line in text_lines:
                if line.strip():
                    row_fragments.append(f"{indent}{line.strip()}")
                else:
                    row_fragments.append("")

        # Add the row's lines to the full output
        all_lines.extend(row_fragments)
        all_lines.append("")  # Extra newline between rows for clarity

    return '\n'.join(all_lines)

# extract text from image defined by roi tracing
@app.route("/extract-text", methods=["POST"])
def extract_text_from_rois():
    from PIL import Image
    data = request.get_json()
    image_url = data.get("image_url")
    zones = data.get("zones")
    if not image_url or not zones:
        return jsonify({"error": "Parameters missed: image_url or zones"}), 400
    filename = os.path.basename(image_url)
    local_image_path = os.path.join(TEMP_FOLDER, filename)
    if not os.path.exists(local_image_path):
        return jsonify({"error": "Image not found"}), 404
    img = Image.open(local_image_path)

    results = []
    for zone in zones:
        x, y, w, h = map(int, (zone["x"], zone["y"], zone["width"], zone["height"]))
        roi_img = img.crop((x, y, x + w, y + h))
        temp_roi_path = os.path.join(TEMP_FOLDER, f"roi_{zone['name']}.png")
        roi_img.save(temp_roi_path)
        text = extract_text_from_image(temp_roi_path)
        try:
            os.remove(temp_roi_path)
        except Exception as e:
            print(f"Error, unable to delete temp image: {e}")
        results.append({
            "name": zone["name"],
            "text": text.strip(),
            "x": x,
            "y": y,
            "width": w,
            "height": h
        })
    formatted_text = build_text_by_rows_with_columns(results, logical_width=img.width)
    if not ner_model.is_ready():
        ner_model.load()
    return jsonify(formatted_text)
    #return jsonify(results)




@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("frontend", path)

@app.route("/uploads/<path:filename>")
def uploaded_files(filename):
    tmp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../tmp"))
    return send_from_directory(tmp_dir, filename)



if __name__ == "__main__":
    
    remove_folder(TEMP_FOLDER)
    app.run(host='0.0.0.0', port=8000, debug=True)
   
    #app.run(debug=True, port=8000)
