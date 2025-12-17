# scriptum.py
import json
import os
from datetime import datetime
from typing import List, Optional
import argparse
import sys

class Scriptum:
    def __init__(self, log_file: str = "scriptum_log.json"):
        self.log_file = log_file
        self.entries: List[dict] = []
        self._load_entries()

    # ---------- Core API ----------
    def add_entry(self, note: str, timestamp: Optional[datetime] = None):
        entry = {
            "timestamp": (timestamp or datetime.now()).isoformat(timespec="seconds"),
            "note": note,
            "mood": self._infer_mood(note),
        }
        self.entries.append(entry)
        self._save()

    def add_entries(self, notes: List[str]):
        # Uses one timestamp for the batch for easy grouping
        now = datetime.now()
        for n in notes:
            n = n.strip()
            if n:
                self.add_entry(n, timestamp=now)

    def reset(self):
        self.entries = []
        self._save()

    def generate_report(self, group_by_mood: bool = False) -> str:
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

        order = ["positive", "neutral", "negative"]
        title_map = {"positive": "🌤️ Positive", "neutral": "🪶 Neutral", "negative": "🌧️ Negative"}
        out = ["Scriptum’s Chronicle (Grouped):"]
        for key in order:
            if buckets.get(key):
                out.append(f"\n{title_map.get(key, key.title())}")
                out.append("-" * 32)
                for e in buckets[key]:
                    out.append(f"[{e['timestamp']}] {e['note']}")
        return "\n".join(out)

    # ---------- Internals ----------
    def _infer_mood(self, note: str) -> str:
        positive = ['happy', 'good', 'love', 'win', 'peace', 'calm', 'joy', 'proud']
        negative = ['sad', 'stress', 'hard', 'angry', 'hurt', 'anxious', 'tired', 'afraid']
        note_lower = note.lower()
        if any(w in note_lower for w in positive):
            return 'positive'
        if any(w in note_lower for w in negative):
            return 'negative'
        return 'neutral'

    def _load_entries(self):
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.entries = data
            except json.JSONDecodeError:
                # Corrupt/empty file -> start fresh; keep file as-is until next save
                self.entries = []

    def _save(self):
        try:
            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump(self.entries, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Failed to save log: {e}", file=sys.stderr)


# ---------- CLI ----------
def _parse_args(argv: List[str]):
    p = argparse.ArgumentParser(description="Scriptum — a quiet, non-interactive chronicler.")
    p.add_argument("--log-file", default="scriptum_log.json",
                   help="Path to the JSON log file (default: scriptum_log.json)")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="Add one or more notes")
    a.add_argument("note", nargs="+", help="Note text (quote each note)")

    af = sub.add_parser("add-file", help="Add notes from a UTF-8 text file (one per line)")
    af.add_argument("path", help="Path to a text file")

    r = sub.add_parser("report", help="Print a report")
    r.add_argument("--group-by-mood", action="store_true", help="Group entries by mood")

    sub.add_parser("reset", help="Clear the log")
    return p.parse_args(argv)


def _main(argv: List[str]) -> int:
    args = _parse_args(argv)
    s = Scriptum(log_file=args.log_file)

    if args.cmd == "add":
        s.add_entries(args.note)
        return 0

    if args.cmd == "add-file":
        try:
            with open(args.path, "r", encoding="utf-8") as f:
                notes = [line.rstrip("\n") for line in f]
            s.add_entries(notes)
        except Exception as e:
            print(f"⚠️ Could not read {args.path}: {e}", file=sys.stderr)
            return 1
        return 0

    if args.cmd == "report":
        print(s.generate_report(group_by_mood=args.group_by_mood))
        return 0

    if args.cmd == "reset":
        s.reset()
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
