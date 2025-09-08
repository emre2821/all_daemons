#!/usr/bin/env python3
"""
Syncs Rhea/scripts/configs/{daemons.yaml,tasks.yaml} from the canonical
registry at Rhea/config/rhea_registry.json.

- daemons.yaml: overwritten with the full registry JSON (for GUI use).
- tasks.yaml: preserved; appends a YAML document containing a daemon_index
  with name, path, team, tags, enabled for all discovered daemons.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

RHEA = Path(__file__).resolve().parent.parent
REG = RHEA / "config" / "rhea_registry.json"
CFG_DIR = RHEA / "scripts" / "configs"
DAEMONS_YAML = CFG_DIR / "daemons.yaml"
TASKS_YAML = CFG_DIR / "tasks.yaml"


def load_registry() -> dict:
    data = json.loads(REG.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("registry is not an object")
    return data


def write_daemons_yaml_from_registry(reg: dict) -> None:
    # Keep JSON content even though file is named .yaml (GUI expects JSON)
    DAEMONS_YAML.parent.mkdir(parents=True, exist_ok=True)
    DAEMONS_YAML.write_text(json.dumps(reg, indent=2), encoding="utf-8")


def append_daemon_index_to_tasks(reg: dict) -> None:
    daemons = reg.get("daemons", {})
    lines: list[str] = []
    lines.append("---")
    lines.append("# Auto-generated daemon index from rhea_registry.json")
    ts = datetime.now(timezone.utc).isoformat()
    lines.append(f"_daemon_index_generated: {ts}")
    lines.append("daemon_index:")
    for name in sorted(daemons.keys()):
        d = daemons[name] or {}
        # name, path, team, tags, enabled
        path = (d.get("path") or "").replace("\\", "/")
        team = d.get("team", "Unassigned")
        tags = d.get("tags") or []
        enabled = bool(d.get("enabled", False))
        lines.append(f"  - name: {name}")
        lines.append(f"    path: {path}")
        lines.append(f"    team: {team}")
        if tags:
            tags_yaml = ", ".join([str(t) for t in tags])
            lines.append(f"    tags: [{tags_yaml}]")
        else:
            lines.append("    tags: []")
        lines.append(f"    enabled: {str(enabled).lower()}")
    # Append to tasks.yaml (create if missing)
    TASKS_YAML.parent.mkdir(parents=True, exist_ok=True)
    with TASKS_YAML.open("a", encoding="utf-8") as f:
        f.write("\n" + "\n".join(lines) + "\n")


def main() -> int:
    reg = load_registry()
    write_daemons_yaml_from_registry(reg)
    append_daemon_index_to_tasks(reg)
    print(
        "Synced daemons.yaml (registry JSON) and appended daemon_index to tasks.yaml\n"
        f"Total daemons: {len((reg.get('daemons') or {}).keys())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

