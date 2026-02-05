#!/usr/bin/env python3
"""
Start a minimal, lightweight set of daemons that avoid heavy GUIs/deps.

Edit LITE to tweak which daemons you want.
"""
from __future__ import annotations
import json
import sys
import subprocess
from pathlib import Path

from rhea_paths import ensure_rhea_dirs, resolve_rhea_paths

PATHS = resolve_rhea_paths(Path(__file__))
HERE = Path(__file__).resolve().parent
ORCH = PATHS.rhea_dir / "scripts" / "full_rhea.complete_build.py"
REG = PATHS.registry_path

# Fallback curated lightweight set (no pandas/kivy/psutil required)
FALLBACK_LITE = {
    'Saphira','Savvy','Codexa','Parsley','Cassandra','Lex',
    'Bellwrit','Whisperfang','Scribevein','Ledger_Jr','Toto','Muse_Jr','Markbearer'
}


def load_registry() -> dict:
    try:
        return json.loads(REG.read_text(encoding='utf-8'))
    except Exception:
        return {"daemons": {name: {} for name in FALLBACK_LITE}}


def choose_lite(reg: dict, use_all: bool=False) -> list[str]:
    names = sorted(reg.get('daemons', {}).keys())
    if use_all:
        return names
    # Prefer tag 'lite' if present
    tagged = [n for n in names if 'lite' in (reg['daemons'][n].get('tags') or [])]
    if tagged:
        return tagged
    # Otherwise, fall back to curated set filtered by presence
    return [n for n in names if n in FALLBACK_LITE]


def main(argv: list[str]) -> int:
    ensure_rhea_dirs(PATHS)
    use_all = ('--all' in argv)
    reg = load_registry()
    to_start = choose_lite(reg, use_all=use_all)
    print(f"Starting {len(to_start)} daemon(s){' (ALL)' if use_all else ''}...")
    for name in to_start:
        print(f"-> {name}")
        subprocess.call([sys.executable, str(ORCH), 'start', name], cwd=str(ORCH.parent))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
