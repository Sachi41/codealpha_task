"""Chatbot backend: serves the frontend and a JSON API at POST /api/chat.

Run:  python app.py   then open http://localhost:8000
"""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from chatbot import get_reply, is_exit

STATIC = Path(__file__).parent / "static"
TYPES = {".html": "text/html", ".css": "text/css", ".js": "text/javascript"}


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        name = "index.html" if self.path in ("/", "") else self.path.lstrip("/").split("?")[0]
        file = (STATIC / name).resolve()
        if STATIC.resolve() not in file.parents or not file.is_file():
            return self._send(404, {"error": "Not found"})
        self._send(200, file.read_bytes(), TYPES.get(file.suffix, "application/octet-stream"))

    def do_POST(self):
        if self.path != "/api/chat":
            return self._send(404, {"error": "Not found"})
        try:
            length = int(self.headers.get("Content-Length", 0))
            message = str(json.loads(self.rfile.read(length) or "{}").get("message", ""))
        except (ValueError, json.JSONDecodeError):
            return self._send(400, {"error": "Invalid JSON"})
        if not message.strip():
            return self._send(400, {"error": "Message is empty"})
        self._send(200, {"reply": get_reply(message), "end": is_exit(message)})

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Chatbot running at http://localhost:{port}  (Ctrl+C to stop)")
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
