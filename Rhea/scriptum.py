# scriptum.py (scaffolded non-interactive)
import json, os, sys
from datetime import datetime
from typing import List, Optional

class Scriptum:
    def __init__(self, log_file: str = "scriptum_log.json"):
        self.log_file = log_file
        self.entries = []
        self._load()

    def add_entry(self, note: str, ts: Optional[datetime]=None):
        e = {
            "timestamp": (ts or datetime.now()).isoformat(timespec="seconds"),
            "note": note,
            "mood": self._mood(note),
        }
        self.entries.append(e)
        self._save()

    def add_entries(self, notes: List[str]):
        now = datetime.now()
        for n in notes:
            n = n.strip()
            if n:
                self.add_entry(n, ts=now)

    def generate_report(self, group_by_mood: bool=False) -> str:
        if not self.entries:
            return "Scriptum’s scroll is blank. Share your tale."
        if not group_by_mood:
            lines = ["Scriptum’s Chronicle:"]
            for e in self.entries:
                lines.append(f"[{e['timestamp']}] {e['mood'].capitalize()}: {e['note']}")
            return "\n".join(lines)
        buckets = {"positive": [], "neutral": [], "negative": []}
        for e in self.entries:
            buckets.setdefault(e["mood"], []).append(e)
        title = {"positive": "🌤️ Positive", "neutral": "🪶 Neutral", "negative": "🌧️ Negative"}
        out = ["Scriptum’s Chronicle (Grouped):"]
        for key in ["positive","neutral","negative"]:
            if buckets.get(key):
                out.append(f"\n{title[key]}")
                out.append("-"*32)
                for e in buckets[key]:
                    out.append(f"[{e['timestamp']}] {e['note']}")
        return "\n".join(out)

    def reset(self):
        self.entries = []
        self._save()

    def _mood(self, note: str) -> str:
        pos = ["happy","good","love","win","peace","calm","joy","proud"]
        neg = ["sad","stress","hard","angry","hurt","anxious","tired","afraid"]
        s = note.lower()
        if any(w in s for w in pos): return "positive"
        if any(w in s for w in neg): return "negative"
        return "neutral"

    def _load(self):
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.entries = data
            except Exception:
                self.entries = []

    def _save(self):
        try:
            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump(self.entries, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Failed to save log: {e}", file=sys.stderr)
