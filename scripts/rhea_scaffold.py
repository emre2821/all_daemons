#!/usr/bin/env python3
r"""
rhea_scaffold.py — scaffold EdenOS Rhea directory structure safely.

- Creates directories only if missing (idempotent).
- Writes starter files only if missing (or if --overwrite given).
- Uses EDEN_ROOT from env or defaults to the current working directory.
- Places Rhea under: <EDEN_ROOT>/daemons/Rhea
- Places Scriptum log under: <EDEN_ROOT>/logs/scriptum_log.json (empty list)

Usage:
  python rhea_scaffold.py
  python rhea_scaffold.py --eden-root "C:\\EdenOS_Origin" --overwrite
"""

import os, sys, json
from pathlib import Path
import argparse
from datetime import datetime

DEFAULT_ROOT = Path(os.environ.get("EDEN_ROOT", Path.cwd()))

RHEA_GUI_PY = r"""# rheagui.py (scaffolded minimal launcher)
from PyQt5 import QtWidgets
import sys
try:
    from rhea import Rhea
except Exception as e:
    print(f"[rheagui] Warning: could not import rhea.py: {e}")
    Rhea = None

def main():
    app = QtWidgets.QApplication(sys.argv)
    w = QtWidgets.QWidget()
    w.setWindowTitle("Rhea Control Panel — EdenOS (Scaffold)")
    w.resize(640, 360)
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
"""

RHEA_CORE_PY = r"""# rhea.py (scaffolded)
from pathlib import Path
import subprocess

class Rhea:
    def __init__(self, eden_root: Path):
        self.eden_root = Path(eden_root)
        self.logs_dir = self.eden_root / "logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        # simple placeholders; your real impl may differ
        self.teams = {}
        self.pairs = {}
        self.procs = {}

    def reload(self):
        # load configs here (scaffold placeholder)
        return True

    def status_rows(self):
        # (tier, name, state, path)
        return []

    def start_daemon(self, name: str):
        return

    def stop_daemon(self, name: str):
        return
"""

SCRIPTUM_PY = r"""# scriptum.py (scaffolded non-interactive)
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
"""

RHEA_SETTINGS_JSON = {
    "eden_root": "",  # filled at runtime
}

RHEA_THEME_APPEND = {
  "name": "Rhea",
  "role": "Cataloguing Daemon",
  "theme": {
    "palette": {
      "primary": "#5A6A8B",
      "secondary": "#AFC1D6",
      "accent": "#E5E1D1",
      "highlight": "#C8D87A",
      "shadow": "#2F2F38"
    },
    "tone": {
      "voice": "calm",
      "style": "precise",
      "tempo": "measured",
      "keywords": ["archival","classification","clarity","diligence","quiet insight"]
    },
    "resonance": {
      "element": "air",
      "motion": "weave",
      "essence": "pattern-seeker"
    }
  }
}

README_TXT = """Rhea — EdenOS Daemon (Scaffold)
================================
This scaffold creates a minimal, safe folder layout for Rhea.

Folders (created if not present):
- daemons/Rhea : Rhea daemon home
- logs             : shared logs (Scriptum lives here)
- config           : place any .yaml/.json configs here
- bin              : helpers / launchers

Key files (created only if missing):
- daemons/Rhea/rheagui.py      : minimal GUI launcher (replace with your full GUI)
- daemons/Rhea/rhea.py         : minimal core class
- daemons/Rhea/scriptum.py     : non-interactive journaling lib
- daemons/Rhea/rhea_gui_settings.json : settings w/ eden_root and theme stub
- logs/scriptum_log.json           : initialized as [] (JSON array)
- README_RHEA.txt                  : this file
"""

BAT_HELPER = r"""@echo off
REM rhea_make_dirs.bat — idempotent helper (Windows)
setlocal
set ROOT=%~1
if "%ROOT%"=="" set ROOT=%CD%

if not exist "%ROOT%" mkdir "%ROOT%"
if not exist "%ROOT%\daemons" mkdir "%ROOT%\daemons"
if not exist "%ROOT%\daemons\Rhea" mkdir "%ROOT%\daemons\Rhea"
if not exist "%ROOT%\logs" mkdir "%ROOT%\logs"
if not exist "%ROOT%\config" mkdir "%ROOT%\config"
if not exist "%ROOT%\bin" mkdir "%ROOT%\bin"

echo Dirs ensured under %ROOT%.
endlocal
"""

SH_HELPER = r"""#!/usr/bin/env bash
# rhea_make_dirs.sh — idempotent helper (Unix)
ROOT="${1:-$(pwd)}"
mkdir -p "$ROOT" \
         "$ROOT/daemons/Rhea" \
         "$ROOT/logs" \
         "$ROOT/config" \
         "$ROOT/bin"
echo "Dirs ensured under $ROOT"
"""

def write_text(path: Path, content: str, overwrite=False):
    if path.exists() and not overwrite:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True

def write_json(path: Path, data, overwrite=False):
    if path.exists() and not overwrite:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return True

def ensure_dirs(root: Path):
    # “if exist=true ok” semantics via exist_ok=True
    (root).mkdir(parents=True, exist_ok=True)
    (root / "daemons").mkdir(parents=True, exist_ok=True)
    (root / "daemons" / "Rhea").mkdir(parents=True, exist_ok=True)
    (root / "logs").mkdir(parents=True, exist_ok=True)
    (root / "config").mkdir(parents=True, exist_ok=True)
    (root / "bin").mkdir(parents=True, exist_ok=True)

def main():
    parser = argparse.ArgumentParser(description="Scaffold Rhea folder safely (idempotent).")
    parser.add_argument("--eden-root", default=str(DEFAULT_ROOT),
                        help="Base Eden root directory.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files.")
    args = parser.parse_args()

    eden_root = Path(args.eden_root)
    ensure_dirs(eden_root)

    rhea_dir = eden_root / "daemons" / "Rhea"
    logs_dir = eden_root / "logs"

    # Files
    wrote = []
    skipped = []

    def do(p: Path, content: str):
        if write_text(p, content, overwrite=args.overwrite):
            wrote.append(p)
        else:
            skipped.append(p)

    def do_json(p: Path, data):
        if write_json(p, data, overwrite=args.overwrite):
            wrote.append(p)
        else:
            skipped.append(p)

    # Core files
    do(rhea_dir / "rheagui.py", RHEA_GUI_PY)
    do(rhea_dir / "rhea.py", RHEA_CORE_PY)
    do(rhea_dir / "scriptum.py", SCRIPTUM_PY)

    # Settings: eden_root + theme stub (merge if exists & not overwrite)
    settings_path = rhea_dir / "rhea_gui_settings.json"
    settings = {"eden_root": str(eden_root)}
    try:
        if settings_path.exists() and not args.overwrite:
            # merge minimal eden_root if missing; keep user content
            current = json.loads(settings_path.read_text(encoding="utf-8"))
            if "eden_root" not in current:
                current["eden_root"] = str(eden_root)
                write_json(settings_path, current, overwrite=True)
                wrote.append(settings_path)
            else:
                skipped.append(settings_path)
        else:
            do_json(settings_path, settings)
    except Exception:
        # fallback: write fresh
        do_json(settings_path, settings)

    # Theme companion file (optional): rhea_theme.json
    theme_path = rhea_dir / "rhea_theme.json"
    do_json(theme_path, RHEA_THEME_APPEND)

    # Logs
    scriptum_log = logs_dir / "scriptum_log.json"
    if not scriptum_log.exists() or args.overwrite:
        write_json(scriptum_log, [])

    # README + helpers
    do(eden_root / "README_RHEA.txt", README_TXT)
    do(eden_root / "bin" / "rhea_make_dirs.bat", BAT_HELPER)
    do(eden_root / "bin" / "rhea_make_dirs.sh", SH_HELPER)

    # Report
    print("✅ Rhea scaffold completed.")
    if wrote:
        print("\nCreated:")
        for p in wrote:
            print(f"  + {p}")
    if skipped:
        print("\nSkipped (already exists):")
        for p in skipped:
            print(f"  = {p}")

    print(f"\nEden root: {eden_root}")
    print("\nNext:")
    print("  1) Put your full-featured rheagui.py in daemons/Rhea (replace scaffold).")
    print("  2) Run GUI:  python daemons/Rhea/rheagui.py")
    print("  3) Logs at:  ", logs_dir)

if __name__ == "__main__":
    main()
