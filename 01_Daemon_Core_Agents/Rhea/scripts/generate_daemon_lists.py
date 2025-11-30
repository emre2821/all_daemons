#!/usr/bin/env python3
"""
Generate daemon lists from the registry to keep everything in sync.

Writes:
- Rhea/config/daemon_names.txt
- Rhea/scripts/configs/daemon_names.txt
- Rhea/config/daemon_lists/by_team/<team>.txt
- Rhea/config/daemon_lists/by_tag/<tag>.txt
- Rhea/config/daemon_lists/canonical_names.txt           (folder == script name)
- Rhea/config/daemon_lists/canonical_paths.txt           (relative paths)

Run after updating the registry. The canonical lists come from a filesystem
scan and include every <Daemon>/scripts/<daemon>.py match.
"""
from __future__ import annotations
import json
from pathlib import Path
import os

RHEA = Path(__file__).resolve().parent.parent
REG  = RHEA / 'config' / 'rhea_registry.json'

def load_reg() -> dict:
    return json.loads(REG.read_text(encoding='utf-8'))

def write_text(path: Path, lines: list[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding='utf-8')

def main() -> int:
    reg = load_reg()
    daemons = reg.get('daemons', {})
    names = sorted(daemons.keys())

    # Flat names list (both locations)
    write_text(RHEA / 'config' / 'daemon_names.txt', names)
    write_text(RHEA / 'scripts' / 'configs' / 'daemon_names.txt', names)

    # By team
    by_team: dict[str, list[str]] = {}
    for n, d in daemons.items():
        t = (d or {}).get('team', 'Unassigned')
        by_team.setdefault(t, []).append(n)
    base_team = RHEA / 'config' / 'daemon_lists' / 'by_team'
    for t, lst in by_team.items():
        write_text(base_team / f'{t}.txt', sorted(lst))

    # By tag
    by_tag: dict[str, list[str]] = {}
    for n, d in daemons.items():
        for tag in (d or {}).get('tags') or []:
            by_tag.setdefault(tag, []).append(n)
    base_tag = RHEA / 'config' / 'daemon_lists' / 'by_tag'
    for tag, lst in by_tag.items():
        write_text(base_tag / f'{tag}.txt', sorted(lst))

    # Canonical scan: <Daemon>/scripts/<daemon>.py (case-insensitive)
    root = RHEA.parent  # all_daemons
    canonical_names: list[str] = []
    canonical_paths: list[str] = []
    for entry in root.iterdir():
        if not entry.is_dir() or entry.name.startswith('_') or entry.name == 'Rhea':
            continue
        scripts = entry / 'scripts'
        if not scripts.is_dir():
            continue
        daemon = entry.name
        target = scripts / f"{daemon.lower()}.py"
        # case-insensitive check across files in scripts
        chosen = None
        if target.exists():
            chosen = target
        else:
            try:
                for f in scripts.iterdir():
                    if f.is_file() and f.suffix.lower() == '.py' and f.stem.lower() == daemon.lower():
                        chosen = f; break
            except Exception:
                pass
        if chosen is not None:
            canonical_names.append(daemon)
            rel = os.path.relpath(chosen, root).replace('\\','/')
            canonical_paths.append(rel)

    canonical_names.sort(); canonical_paths.sort()
    write_text(RHEA / 'config' / 'daemon_lists' / 'canonical_names.txt', canonical_names)
    write_text(RHEA / 'config' / 'daemon_lists' / 'canonical_paths.txt', canonical_paths)

    print(f"Lists generated: {len(names)} daemons, {len(by_team)} teams, {len(by_tag)} tags")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
