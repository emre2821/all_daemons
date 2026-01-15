#!/usr/bin/env python3
"""
Update Rhea registry from filesystem by treating any <Daemon>/scripts/<file>.py
as a daemon entry. Prefers <daemon>.py if multiple scripts exist.

Keeps existing metadata (enabled, tags, team, group, env) where present.
"""
from __future__ import annotations
import json
from pathlib import Path


RHEA_DIR = Path(__file__).resolve().parent.parent
DAEMONS_ROOT = RHEA_DIR.parent  # .../daemons
REG_PATH = RHEA_DIR / "config" / "rhea_registry.json"


def load_registry() -> dict:
    if REG_PATH.exists():
        try:
            return json.loads(REG_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "version": 1,
        "palettes": {
            "eden_dream": {"bg": "#0b1020", "fg": "#e6f0ff", "accent": "#7aa2f7", "muted": "#94a3b8"},
            "velvet_division": {"bg": "#1a1417", "fg": "#F7E7F3", "accent": "#E84C7F", "muted": "#A08A98"},
            "rootfire": {"bg": "#0e0f0a", "fg": "#f0f5e1", "accent": "#b0f566", "muted": "#93a48a"}
        },
        "daemons": {},
        "teams": {},
        "groups": {},
        "pairs": [],
        "tasks": []
    }


def pick_primary_script(pyfiles: list[Path], daemon: str) -> Path:
    # Prefer <daemon>.py (case-insensitive), else first file
    preferred = None
    for p in pyfiles:
        if p.name.lower() == f"{daemon.lower()}.py":
            preferred = p
            break
    return preferred or (pyfiles[0] if pyfiles else None)


def discover_daemons() -> dict[str, Path]:
    found: dict[str, list[Path]] = {}
    for p in DAEMONS_ROOT.rglob("scripts/*.py"):
        rel = p.relative_to(DAEMONS_ROOT)
        top = rel.parts[0]
        if top == "Rhea" or top.startswith("."):
            continue
        found.setdefault(top, []).append(p)
    choices: dict[str, Path] = {}
    for daemon, files in found.items():
        chosen = pick_primary_script(files, daemon)
        if chosen:
            choices[daemon] = chosen
    return choices


def merge_into_registry(reg: dict, choices: dict[str, Path]) -> int:
    added_or_updated = 0
    daemons = reg.setdefault("daemons", {})
    for name, path in choices.items():
        rel = path.relative_to(DAEMONS_ROOT)
        entry = daemons.get(name, {})
        # Preserve existing metadata where present
        new_entry = {
            "name": name,
            "path": str(rel).replace("\\", "/"),
            "enabled": entry.get("enabled", False),
            "tags": entry.get("tags", []),
            "team": entry.get("team", "Unassigned"),
            "group": entry.get("group", "Default"),
            "env": entry.get("env", {}),
            "start": entry.get("start", {"type": "python", "args": [path.name]}),
        }
        if daemons.get(name) != new_entry:
            daemons[name] = new_entry
            added_or_updated += 1
    return added_or_updated


def main() -> int:
    reg = load_registry()
    choices = discover_daemons()
    changed = merge_into_registry(reg, choices)
    # Ensure teams membership reflects daemon.team (optional; GUI/orchestrator can sync too)
    teams = {}
    for dname, d in reg.get("daemons", {}).items():
        team = d.get("team", "Unassigned")
        teams.setdefault(team, {"members": []})
        if dname not in teams[team]["members"]:
            teams[team]["members"].append(dname)
    reg["teams"] = teams
    # Save
    REG_PATH.parent.mkdir(parents=True, exist_ok=True)
    REG_PATH.write_text(json.dumps(reg, indent=2), encoding="utf-8")
    print(f"Updated registry: {changed} entries added/updated; total daemons = {len(reg.get('daemons', {}))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

