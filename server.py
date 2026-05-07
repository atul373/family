from flask import Flask, request, jsonify, send_from_directory
import os, json, threading

app = Flask(__name__)

# 👉 IMPORTANT: apna folder path yaha daalo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "parivar_data.json")

lock = threading.Lock()

def default_data():
    return {
        "members": [],
        "media": [],
        "auditLog": [],
        "settings": {}
    }

def load_db():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    d = default_data()
    save_db(d)
    return d

def save_db(data):
    with lock:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)

# ── Routes ─────────────────────────────
@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")

@app.route("/api/data", methods=["GET"])
def get_data():
    return jsonify(load_db())

@app.route("/api/save", methods=["POST"])
def save_data():
    data = request.get_json(force=True)
    save_db(data)
    return jsonify({"status": "saved"})

# ── Static files (css/js/images) ───────
@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(BASE_DIR, filename)

# ── Start server ───────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8765)
