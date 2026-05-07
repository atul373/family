#!/usr/bin/env python3

import json, os, time, threading, socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from datetime import datetime

PORT = 8765

# 👉 IMPORTANT: apna folder path yaha daalo
BASE_DIR = r"D:\Users\Atul\Desktop\New folder (7)"

DATA_FILE = os.path.join(BASE_DIR, "parivar_data.json")

# ── Default Data ─────────────────────────
def default_data():
    return {
        "members": [],
        "media": [],
        "auditLog": [],
        "settings": {}
    }

lock = threading.Lock()

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

# ── Handler ─────────────────────────────
class Handler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}]", fmt % args)

    def send_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # 👉 ROOT → index.html
        if path == "/" or path == "/index.html":
            return self.serve_file("index.html")

        # 👉 API
        elif path == "/api/data":
            return self.send_json(load_db())

        # 👉 STATIC FILES (css/js/images)
        else:
            return self.serve_file(path.lstrip("/"))

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length > 0 else b"{}"

        try:
            data = json.loads(body)
        except:
            data = {}

        if path == "/api/save":
            save_db(data)
            return self.send_json({"status": "saved"})
        else:
            self.send_response(404)
            self.end_headers()

    # ── File Serve ──────────────────────
    def serve_file(self, filename):
        file_path = os.path.join(BASE_DIR, filename)

        if not os.path.exists(file_path):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")
            return

        # 👉 Content type detect
        if filename.endswith(".html"):
            ctype = "text/html"
        elif filename.endswith(".css"):
            ctype = "text/css"
        elif filename.endswith(".js"):
            ctype = "application/javascript"
        elif filename.endswith(".png"):
            ctype = "image/png"
        elif filename.endswith(".jpg") or filename.endswith(".jpeg"):
            ctype = "image/jpeg"
        else:
            ctype = "application/octet-stream"

        with open(file_path, "rb") as f:
            content = f.read()

        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", len(content))
        self.send_cors()
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.send_cors()
        self.end_headers()
        self.wfile.write(body)


# ── START SERVER ────────────────────────
if __name__ == "__main__":
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        lan_ip = s.getsockname()[0]
        s.close()
    except:
        lan_ip = "127.0.0.1"

    server = HTTPServer(("0.0.0.0", PORT), Handler)

    print("=" * 50)
    print("🚀 PARIVAR SERVER RUNNING")
    print("=" * 50)
    print(f"💻 Laptop: http://localhost:{PORT}")
    print(f"📱 Mobile: http://{lan_ip}:{PORT}")
    print("=" * 50)

    server.serve_forever()