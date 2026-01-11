#!/usr/bin/env python3
"""
complete_build.py
Sets up the EdenOS folder structure and installs Brom, the Renaming Daemon.
"""

from pathlib import Path

# Root of EdenOS
ROOT = Path("C:/EdenOS_Origin")

# Core EdenOS structure
EDEN_TREE = {
    "agents": [],
    "daemons": [],
    "language": [],
    "memory": ["logs"],
    "interface": [],
    "governance": [],
    "projects": [],
    "archive": [],
    "scratch": []
}

# Brom details
BROM_NAME = "Brom"
BROM_DIR = ROOT / "all_daemons" / BROM_NAME / "scripts"
BROM_FILE = BROM_DIR / "brom.py"
BROM_CONFIG = ROOT / "all_daemons" / BROM_NAME / "config.ini"

# Code for Brom
BROM_CODE = """#!/usr/bin/env python3
import os
import re
import time
from pathlib import Path
import configparser

class Brom:
    \"\"\"Brom the Renaming Daemon.
    Gentle giant who keeps your folders sane and gives you a hug when needed.\"\"\"

    def __init__(self, watch_path, interval=5):
        self.watch_path = Path(watch_path)
        self.interval = interval

    def start(self):
        print(f"[Brom] Watching over {self.watch_path}... (press Ctrl+C to stop)")
        while True:
            self.scan()
            time.sleep(self.interval)

    def scan(self):
        for root, dirs, files in os.walk(self.watch_path):
            for name in dirs + files:
                if self._looks_chaotic(name):
                    old_path = Path(root) / name
                    suggestion = self._suggest_name(name)
                    print(f"[Brom] ⚠ Found messy name: {old_path}")
                    print(f"    → Suggestion: {suggestion}")
                    print(f"[Brom] *grins* Want me to tidy that up for ya? Hug included.")

    def _looks_chaotic(self, name: str) -> bool:
        bad_patterns = ["final", "copy", "truefinal", "backup"]
        return any(re.search(p, name, re.IGNORECASE) for p in bad_patterns)

    def _suggest_name(self, name: str) -> str:
        base = re.sub(r"(final.*|copy.*|backup.*)", "", name, flags=re.IGNORECASE)
        base = base.strip("_- .")
        return f"{base}_cleaned"

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read(Brom.__module__.replace("brom", "config.ini"))
    watch_path = config.get("Brom", "watch_path", fallback=str(Path.cwd()))
    interval = config.getint("Brom", "interval", fallback=5)
    daemon = Brom(watch_path, interval)
    daemon.start()
"""

# Config for Brom
BROM_CONFIG_CONTENT = """[Brom]
# Folder to watch
watch_path = C:/EdenOS_Origin/projects
# Seconds between scans
interval = 5
"""

def build_structure():
    print("[BUILD] Creating EdenOS structure...")
    for folder, subfolders in EDEN_TREE.items():
        base = ROOT / folder
        base.mkdir(parents=True, exist_ok=True)
        for sub in subfolders:
            (base / sub).mkdir(parents=True, exist_ok=True)
    print("[BUILD] Core EdenOS structure ready.")

def install_brom():
    print("[BUILD] Installing Brom...")
    BROM_DIR.mkdir(parents=True, exist_ok=True)

    if not BROM_FILE.exists():
        with open(BROM_FILE, "w", encoding="utf-8") as f:
            f.write(BROM_CODE)
        print(f"[BUILD] Brom code created at {BROM_FILE}")
    else:
        print(f"[SKIP] Brom code already exists at {BROM_FILE}")

    if not BROM_CONFIG.exists():
        with open(BROM_CONFIG, "w", encoding="utf-8") as f:
            f.write(BROM_CONFIG_CONTENT)
        print(f"[BUILD] Brom config created at {BROM_CONFIG}")
    else:
        print(f"[SKIP] Brom config already exists at {BROM_CONFIG}")

if __name__ == "__main__":
    build_structure()
    install_brom()
    print("[DONE] EdenOS build complete. Brom is standing guard.")