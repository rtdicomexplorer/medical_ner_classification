import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, request, jsonify, send_from_directory,send_file
from scripts.predictions_ner import ner_model
from scripts.text_extractor import extract_text

from scripts.utils import validate_ner_sample_smart

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


@app.route("/predictor")
def predictor_page():
    return send_file(os.path.join(FRONTEND_DIR, "predictor.html"))




@app.route("/load_model", methods=["POST"])
def load_model_route():   
    if not ner_model.is_ready():
        ner_model.load()
        return jsonify({"status": "Model loaded"}), 200
    return jsonify({"status": "Model already loaded"}), 200


@app.route("/upload", methods=["POST"])
def upload_file():
    uploaded_file = request.files.get("file")
    if not uploaded_file:
        return jsonify({"error": "No file uploaded"}), 400
    # Ensure local ./tmp folder exists
    os.makedirs("tmp", exist_ok=True)

    # Save in local ./tmp folder (not /tmp)
    temp_path = os.path.join("tmp", uploaded_file.filename)
    uploaded_file.save(temp_path)

    # Extract text
    text = extract_text(temp_path)

    # Optionally delete file after processing
    os.remove(temp_path)

    return jsonify({"text": text})


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

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("frontend", path)

if __name__ == "__main__":
    app.run(debug=True, port=8000)
