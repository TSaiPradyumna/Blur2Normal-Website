from flask import Flask, request, jsonify
import cv2
import numpy as np
import fitz  # PyMuPDF
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)

def enhance_image(image_path):
    image = cv2.imread(image_path, 0)  # Load in grayscale
    enhanced = cv2.equalizeHist(image)  # Apply histogram equalization
    output_path = image_path.replace("uploads", "processed")
    cv2.imwrite(output_path, enhanced)
    return output_path

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    # Convert PDF pages to images & enhance
    doc = fitz.open(file_path)
    for i in range(len(doc)):
        img = doc[i].get_pixmap()
        img_path = os.path.join(app.config["UPLOAD_FOLDER"], f"page_{i}.png")
        img.save(img_path)
        enhanced_path = enhance_image(img_path)

    return jsonify({"message": "Processing complete", "url": enhanced_path})

if __name__ == "__main__":
    app.run(debug=True)
