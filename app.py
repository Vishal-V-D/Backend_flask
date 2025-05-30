from flask import Flask, request, jsonify, redirect, url_for, session
from functools import wraps
import os
from flask_cors import CORS

# Import orchestrator for content generation
from orchestrator import orchestrator

# Import LinkedIn functions from our new module
from LinkedInAutomation import (
    linkedin_login,
    linkedin_callback,
    post_to_linkedin,
    post_with_image,
    login_required
)

UPLOAD_FOLDER = "uploads"

# Initialize Flask app
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = "your_super_secret_key"  # Required for session
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)
app.config.update(
    SESSION_COOKIE_SAMESITE="None",
    SESSION_COOKIE_SECURE=True
)
# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ----------------------
# 🔁 Content Generation Routes
# ----------------------

@app.route("/upload", methods=["POST"])
def upload_audio():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    audio_file = request.files["file"]
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], audio_file.filename)
    audio_file.save(file_path)

    print(f"[INFO] Audio file saved at: {file_path}")

    # ✅ Run full MCP agent pipeline via orchestrator
    try:
        results = orchestrator(file_path)
        return jsonify(results)
    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({"error": str(e)}), 500


# ----------------------
# 🔗 LinkedIn Integration Routes
# ----------------------

@app.route("/linkedin/login")
def linkedin_login_route():
    return linkedin_login()


@app.route("/linkedin/callback")
def linkedin_callback_route():
    return linkedin_callback()


@app.route("/post-to-linkedin", methods=["POST"])
@login_required
def post_to_linkedin_route():
    data = request.get_json()
    content = data.get("content")
    image_file_name = data.get("imageFile")  # Not used directly here, but you can extend later

    if not content:
        return jsonify({"error": "No content provided"}), 400

    result = post_to_linkedin(content)
    return jsonify(result)


# Optional: If you ever want to support image uploads from React
@app.route("/post-with-image", methods=["POST"])
@login_required
def post_with_image_route():
    content = request.form.get("content")
    image = request.files.get("image")

    if not content or not image:
        return jsonify({"error": "Missing content or image"}), 400

    result = post_with_image(content, image)
    return jsonify(result)


# ----------------------
# 🚀 Run App
# ----------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
