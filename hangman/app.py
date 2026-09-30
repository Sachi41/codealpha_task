"""Hangman - Python backend (standard library only, no pip install needed).

Run:  python app.py   then open http://localhost:8000
"""
import json
import os
import random
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

WORDS = {  # 5 predefined words, each with a hint
    "python": "A popular programming language",
    "hangman": "The game you are playing",
    "computer": "You are using one right now",
    "keyboard": "Used to type letters",
    "program": "A set of instructions for a computer",
}
MAX_WRONG = 6
STATIC = Path(__file__).parent / "static"
TYPES = {".html": "text/html", ".css": "text/css", ".js": "text/javascript"}
GAMES = {}  # game_id -> Game (kept in memory)


class Game:
    def __init__(self):
        self.word = random.choice(list(WORDS))
        self.guessed = []
        self.wrong = 0

    @property
    def status(self):
        if all(c in self.guessed for c in self.word):
            return "won"
        return "lost" if self.wrong >= MAX_WRONG else "playing"

    def guess(self, letter):
        if letter not in self.guessed:
            self.guessed.append(letter)
            if letter not in self.word:
                self.wrong += 1

    def state(self, game_id):
        over = self.status != "playing"
        return {
            "id": game_id,
            "masked": [c if c in self.guessed else "_" for c in self.word],
            "guessed": sorted(self.guessed),
            "wrong": self.wrong,
            "max_wrong": MAX_WRONG,
            "hint": WORDS[self.word],
            "status": self.status,
            "word": self.word if over else None,  # reveal only when game ends
        }


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
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length) or "{}")
        except (ValueError, json.JSONDecodeError):
            return self._send(400, {"error": "Invalid JSON"})

        if self.path == "/api/new":
            gid = uuid.uuid4().hex
            GAMES[gid] = Game()
            return self._send(200, GAMES[gid].state(gid))

        if self.path == "/api/guess":
            game = GAMES.get(data.get("id"))
            letter = str(data.get("letter", "")).lower()
            if game is None:
                return self._send(404, {"error": "Game not found. Start a new game."})
            if len(letter) != 1 or not letter.isalpha():
                return self._send(400, {"error": "Send a single letter."})
            if game.status == "playing":
                game.guess(letter)
            return self._send(200, game.state(data["id"]))

        self._send(404, {"error": "Not found"})

    def log_message(self, fmt, *args):
        pass  # keep the console quiet


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Hangman running at http://localhost:{port}  (Ctrl+C to stop)")
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
