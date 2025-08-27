import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, request, jsonify, send_from_directory,send_file
from scripts.predictions_ner import execute_predictions
from scripts.text_extractor import extract_text

# Use absolute path for frontend directory
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend"))

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')

@app.route("/")
def index():
    return send_file(os.path.join(FRONTEND_DIR, "index.html"))


import os

@app.route("/upload", methods=["POST"])
def upload_file():
    print('upload called')
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

    raw_predictions = execute_predictions(text)
    # Convert numpy types to Python types for JSON
    for ent in raw_predictions:
        ent['score'] = float(ent['score'])

    return jsonify({'entities': raw_predictions})

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("frontend", path)

if __name__ == "__main__":
    app.run(debug=True, port=8000)
