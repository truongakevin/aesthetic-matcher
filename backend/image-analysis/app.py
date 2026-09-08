import base64
import binascii
import os
from datetime import datetime
from io import BytesIO
from threading import Lock

import torch
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from PIL import Image, ImageOps, UnidentifiedImageError
from transformers import CLIPModel, CLIPProcessor
from werkzeug.exceptions import RequestEntityTooLarge

from feedback import feedback_blueprint
from genrelist import genres
from summarized_aesthetics import aesthetics


load_dotenv()
FLASK_PORT = int(os.getenv("FLASK_PORT", "5555"))
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(25 * 1024 * 1024)))
MAX_IMAGES = int(os.getenv("MAX_IMAGES", "5"))
MAX_IMAGE_PIXELS = int(os.getenv("MAX_IMAGE_PIXELS", "25000000"))

Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS

app = Flask(__name__)
app.config["DEBUG"] = os.getenv("FLASK_DEBUG", "").lower() in ("1", "true", "yes")
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES
CORS(app)
app.register_blueprint(feedback_blueprint)
inference_lock = Lock()

processor_name = "openai/clip-vit-large-patch14-336"
model_name = "kevinoli/clip-finetuned-csu-p14-336-e3l57-l"
processor = CLIPProcessor.from_pretrained(processor_name)
model = CLIPModel.from_pretrained(model_name)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

if app.config["DEBUG"]:
    print("CUDA Availability: ", torch.cuda.is_available(), flush=True)


def error_response(message, status):
    return jsonify({"error": message}), status


@app.errorhandler(RequestEntityTooLarge)
def handle_too_large(_error):
    max_mb = MAX_UPLOAD_BYTES // (1024 * 1024)
    return error_response(f"Upload is too large. The request limit is {max_mb} MB.", 413)


def normalize_image(source):
    image = ImageOps.exif_transpose(source)
    image.load()
    if image.width * image.height > MAX_IMAGE_PIXELS:
        raise ValueError("An image exceeds the decoded pixel limit.")
    return image.convert("RGB").copy()


def read_uploaded_images():
    files = request.files.getlist("images")
    if not files or all(not uploaded_file.filename for uploaded_file in files):
        raise ValueError("Choose at least one image.")
    if len(files) > MAX_IMAGES:
        raise ValueError(f"Choose no more than {MAX_IMAGES} images at a time.")

    images = []
    for uploaded_file in files:
        try:
            with Image.open(uploaded_file.stream) as source:
                images.append(normalize_image(source))
        except (Image.DecompressionBombError, UnidentifiedImageError, OSError) as error:
            raise ValueError("One of the uploaded files is not a supported image.") from error
    return images


def read_base64_image():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get("image"), str):
        raise ValueError("Request JSON must contain a base64 image string.")
    try:
        image_bytes = base64.b64decode(data["image"], validate=True)
        with Image.open(BytesIO(image_bytes)) as source:
            return normalize_image(source)
    except (binascii.Error, Image.DecompressionBombError, UnidentifiedImageError, OSError) as error:
        raise ValueError("The request does not contain a supported image.") from error


@app.post("/image-analysis/am")
def analyze_image_am():
    try:
        images = read_uploaded_images()
        with inference_lock:
            probabilities = process_images(images, aesthetics, 25, 1)
    except ValueError as error:
        return error_response(str(error), 400)

    current_time = datetime.now().strftime("%m-%d-%Y_%H-%M")
    save_dir = os.path.join("./uploads", current_time)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    for index, image in enumerate(images):
        save_path = os.path.join(save_dir, f"image{index}.jpg")
        new_width = 500
        width_percent = new_width / float(image.size[0])
        new_height = int(float(image.size[1]) * float(width_percent))
        image.resize((new_width, new_height)).save(save_path)
    with open(os.path.join(save_dir, "probabilities.txt"), "w", encoding="utf-8") as output:
        for feature, probability in probabilities:
            output.write(f"{feature.split(',')[0]}: {probability}\n")

    return jsonify([
        {"feature": feature.split(",")[0], "probability": probability}
        for feature, probability in probabilities
    ])


@app.post("/image-analysis/ptp")
def analyze_image_ptp():
    try:
        image = read_base64_image()
        with inference_lock:
            probabilities = process_images([image], genres, 7, 5)
    except ValueError as error:
        return error_response(str(error), 400)

    return jsonify([
        {"feature": feature, "probability": probability}
        for feature, probability in probabilities
    ])


def process_images(images, features, num_features=7, batch_splits=1):
    def process_batches(batch_features_source, batch_size):
        probabilities = []
        for start in range(0, len(batch_features_source), batch_size):
            batch_features = batch_features_source[start:start + batch_size]
            inputs = processor(text=batch_features, images=images, return_tensors="pt", padding=True)
            inputs = {key: value.to(device) for key, value in inputs.items()}
            with torch.no_grad():
                outputs = model(**inputs)

            batch_probabilities = outputs.logits_per_image.softmax(dim=1).cpu().mean(dim=0)
            probabilities.append(batch_probabilities)
        return torch.cat(probabilities, dim=0)

    feature_list = list(features)
    if not feature_list:
        raise ValueError("No matching labels are configured.")
    batch_size = max(1, len(feature_list) // batch_splits)

    all_probabilities = process_batches(feature_list, batch_size)
    top_indices = torch.argsort(all_probabilities, descending=True)[:num_features * 10]
    top_features = [feature_list[index.item()] for index in top_indices]

    top_probabilities = process_batches(top_features, batch_size)
    final_indices = torch.argsort(top_probabilities, descending=True)[:num_features]
    top_categories = [
        (top_features[index.item()], round(top_probabilities[index].item() * 100, 2))
        for index in final_indices
    ]

    if device.type == "cuda":
        torch.cuda.empty_cache()
    return top_categories


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=FLASK_PORT, use_reloader=False)
