# EchoThread — aesthetic logging for Shamir
# Colorful, symbolic logs driven by emotions.json and archetypes.json.

import time
import sys

ANSI = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
}

def colorize(s, color):
    # Most modern terminals (including Windows Terminal) support ANSI.
    return ANSI.get(color, "") + s + ANSI["reset"]

class Echo:
    def __init__(self, arch: dict, emo: dict):
        self.arch = arch
        self.emo = emo

    def _emit(self, key: str, msg: str, level: str):
        e = self.emo.get(key) or self.emo.get(level) or {}
        glyph = e.get("glyph", "•")
        color = e.get("color", "white")
        tone = e.get("tone", "dim")
        t = time.strftime("%H:%M:%S")
        line = f"{glyph} {msg}"
        if tone == "bold":
            line = ANSI["bold"] + colorize(line, color) + ANSI["reset"]
        elif tone == "dim":
            line = ANSI["dim"] + colorize(line, color) + ANSI["reset"]
        else:
            line = colorize(line, color)
        sys.stdout.write(f"{t} {line}\n")
        sys.stdout.flush()

    # Semantic helpers
    def summon(self, key, msg): self._emit(key, msg, "info")
    def bloom(self, key, msg): self._emit(key, msg, "success")
    def warn(self, key, msg): self._emit(key, msg, "warn")
    def fade(self, key, msg): self._emit(key, msg, "info")
    def note(self, key, msg): self._emit(key, msg, "info")
    def tell(self, key, msg): self._emit(key, msg, "info")
    def invoke(self, key, msg): self._emit(key, msg, "ritual")
