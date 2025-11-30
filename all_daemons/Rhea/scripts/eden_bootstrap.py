#!/usr/bin/env python3
"""
Eden Bootstrap - set up configs and reconcile registry so things run.

Runs in order:
1) Update registry from filesystem (treat <Daemon>/scripts/*.py as daemons)
2) Sync daemons.yaml/tasks.yaml from registry (writes to Rhea/config and scripts/configs)
3) Initialize, scan, and fix registry via Rhea orchestrator

Optional next steps printed at the end to start by tags or open GUI.
"""
from __future__ import annotations
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def run_py(relpath: str, *args: str) -> int:
    p = subprocess.run([sys.executable, str(ROOT/relpath), *args], cwd=str((ROOT/relpath).parent))
    return p.returncode

def main() -> int:
    print("[1/3] Updating registry from filesystem...")
    rc = run_py('update_registry_from_fs.py')
    if rc != 0:
        print("! Failed to update registry")
        return rc

    print("[2/3] Syncing configs (daemons.yaml/tasks.yaml)...")
    rc = run_py('sync_config_from_registry.py')
    if rc != 0:
        print("! Failed to sync configs")
        return rc

    print("[3/3] Rhea init/scan/fix...")
    orch = ROOT / 'full_rhea.complete_build.py'
    for cmd in (('init',), ('scan',), ('fix','--apply')):
        r = subprocess.run([sys.executable, str(orch), *cmd], cwd=str(orch.parent))
        if r.returncode != 0:
            print(f"! Rhea step failed: {' '.join(cmd)}")
            return r.returncode

    print("\nAll set. Suggested next commands:\n")
    print("- List daemons:      uv run Rhea/scripts/full_rhea.complete_build.py list")
    print("- Start by tags:     uv run Rhea/scripts/rhea_emergency_boot.py --tags parser,label,organizer,catalog,index,sort,cleanup")
    print("- Open Rhea GUI:     uv run Rhea/scripts/full_rhea.complete_build.py gui")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())

