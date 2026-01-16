#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rhea — EdenOS Orchestrator (Smart Edition)

What this does:
  - Auto-discovers sibling daemons in 01_Daemon_Core_Agents\*
  - Dynamically imports each daemon module and queries:
        describe()    -> str | dict (optional)
        healthcheck() -> {"status": "ok"/"warn"/"fail", ...} (optional)
        run(payload|path, **kwargs) -> any (optional)
  - Maintains/merges rhea_registry.json (non-destructive; creates .bak backup)
  - Provides a small CLI for: health map, fixing Sheele input, running Sheele->Briar->Codexa->Janvier->Aderyn
  - Safe defaults for OpenAI export path

Minimal external deps:
  - None required.
  - Optional: jsonschema (pip install jsonschema) if you enable schema checks.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

# -----------------------------
# Custom palette (for logs/UI)
# -----------------------------
PALETTE = {
    "ink": "#0B1D3A",
    "amethyst": "#B9A9D9",
    "teal": "#57C1A7",
    "ember": "#FFB84D",
    "steel": "#C0C5CE",
    "violet": "#9D65C9",
}

# -----------------------------
# Util
# -----------------------------
def log(msg: str, color: Optional[str] = None) -> None:
    prefix = "[Rhea]"
    print(f"{prefix} {msg}")

def warn(msg: str) -> None:
    print(f"[Rhea][WARN] {msg}")

def err(msg: str) -> None:
    print(f"[Rhea][ERROR] {msg}")

def ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def safe_read_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        err(f"Failed to read JSON {path}: {e}")
        return default

def safe_write_json(path: Path, data: Any) -> bool:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        err(f"Failed to write JSON {path}: {e}")
        return False

def backup(path: Path, dest: Path) -> None:
    if path.exists():
        try:
            shutil.copy2(path, dest)
            log(f"Backed up {path.name} -> {dest.name}")
        except Exception as e:
            warn(f"Backup failed ({path}): {e}")

# -----------------------------
# Eden paths & defaults
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def resolve_root(env: Mapping[str, str] | None = None) -> Path:
    """Find the Eden root in a cross-platform, repo-friendly way."""
    env = env or os.environ
    env_root = env.get("EDEN_ROOT")
    if env_root:
        candidate = Path(env_root).expanduser()
        if candidate.exists():
            return candidate
        warn(f"EDEN_ROOT is set to {candidate}, but it does not exist. Falling back to PROJECT_ROOT.")
    return PROJECT_ROOT


def resolve_daemon_dir(root: Path, env: Mapping[str, str] | None = None) -> Path:
    """Pick a daemon directory that actually exists, with sensible fallbacks."""
    env = env or os.environ
    env_daemons = env.get("EDEN_DAEMONS_DIR")
    candidates = [
        Path(env_daemons).expanduser() if env_daemons else None,
        root / "01_Daemon_Core_Agents",
        root / "daemons",
        root,
    ]

    def _looks_like_daemon_home(path: Path) -> bool:
        if not path.is_dir():
            return False
        try:
            for child in path.iterdir():
                if not child.is_dir():
                    continue
                main_py = child / f"{child.name.lower()}.py"
                alt_main = child / f"{child.name.lower()}_main.py"
                if main_py.exists() or alt_main.exists():
                    return True
        except (FileNotFoundError, NotADirectoryError, PermissionError):
            return False
        return False

    first_existing: Optional[Path] = None
    for candidate in candidates:
        if candidate and candidate.exists():
            first_existing = first_existing or candidate
            if _looks_like_daemon_home(candidate):
                return candidate
    return first_existing or root


ROOT = resolve_root()
DAEMON_DIR = resolve_daemon_dir(ROOT)
RHEA_DIR = Path(__file__).resolve().parent
REGISTRY_PATH = RHEA_DIR / "rhea_registry.json"
BACKUP_PATH = RHEA_DIR / f"rhea_registry.{int(time.time())}.bak.json"

# Sheele wanted path (OpenAI exports)
SHEELE_DEFAULT_INPUT = ROOT / "data" / "exports" / "openai_exports" / "conversations.json"

# Name patterns
PY_NAME = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*\.py$")

# -----------------------------
# Data structures
# -----------------------------
@dataclass
class DaemonInfo:
    name: str
    path: Path
    module_path: Path
    describe: Optional[Any] = None
    health: Dict[str, Any] = field(default_factory=dict)
    run_callable: bool = False

# -----------------------------
# Discovery & import
# -----------------------------
def discover_daemons() -> List[DaemonInfo]:
    found: List[DaemonInfo] = []
    if not DAEMON_DIR.exists():
        err(f"Daemon dir missing: {DAEMON_DIR}")
        return found

    for d in sorted(DAEMON_DIR.iterdir()):
        if not d.is_dir():
            continue
        main_py = d / f"{d.name.lower()}.py"
        if not main_py.exists():
            continue

        # Skip self (Rhea should not try to import rhea.py)
        if main_py.resolve() == Path(__file__).resolve():
            continue

        found.append(DaemonInfo(name=d.name, path=d, module_path=main_py))

    return found

def import_module_from_path(module_name: str, file_path: Path):
    try:
        spec = importlib.util.spec_from_file_location(module_name, str(file_path))
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore
        return mod
    except Exception as e:
        err(f"Import failed for {file_path}: {e}")
        return None

def probe_daemon(di: DaemonInfo) -> DaemonInfo:
    mod = import_module_from_path(di.name, di.module_path)
    if mod is None:
        di.health = {"status": "fail", "error": "import_error"}
        return di
    if hasattr(mod, "describe"):
        try:
            di.describe = mod.describe()
        except Exception as e:
            di.describe = {"error": f"describe_failed: {e}"}
    if hasattr(mod, "healthcheck"):
        try:
            h = mod.healthcheck()
            if isinstance(h, dict):
                di.health = h
            else:
                di.health = {"status": "ok", "detail": str(h)}
        except Exception as e:
            di.health = {"status": "fail", "error": f"healthcheck_failed: {e}"}
    else:
        di.health = {"status": "unknown"}
    di.run_callable = hasattr(mod, "run")
    return di

# -----------------------------
# Registry management
# -----------------------------
def load_registry() -> Dict[str, Any]:
    reg = safe_read_json(REGISTRY_PATH, default={"daemons": {}, "teams": {}})
    reg.setdefault("daemons", {})
    reg.setdefault("teams", {})
    return reg

def merge_discovery_into_registry(reg: Dict[str, Any], discovered: List[DaemonInfo]) -> Dict[str, Any]:
    changed = False
    for di in discovered:
        if di.name not in reg["daemons"]:
            reg["daemons"][di.name] = {
                "path": str(di.path),
                "module": str(di.module_path),
                "added_at": ts(),
                "tags": [],
                "enabled": True,
            }
            changed = True
    if changed:
        backup(REGISTRY_PATH, BACKUP_PATH)
        ok = safe_write_json(REGISTRY_PATH, reg)
        if ok:
            log("Registry updated with discovered daemons.")
    return reg

def ensure_sheele_input_points_to_export(reg: Dict[str, Any]) -> bool:
    sheele = reg["daemons"].get("Sheele")
    if not sheele:
        warn("Sheele not found in registry; cannot fix input path.")
        return False
    cfg = sheele.setdefault("config", {})
    cfg.setdefault("inputs", {})
    cfg["inputs"]["raw_conversations_path"] = str(SHEELE_DEFAULT_INPUT)
    backup(REGISTRY_PATH, BACKUP_PATH)
    return safe_write_json(REGISTRY_PATH, reg)

# -----------------------------
# Pipeline execution
# -----------------------------
def try_run_daemon(di: DaemonInfo, payload: Any = None, **kwargs) -> Tuple[bool, Any]:
    mod = import_module_from_path(di.name, di.module_path)
    if mod is None or not hasattr(mod, "run"):
        return False, None
    try:
        res = mod.run(payload, **kwargs)
        return True, res
    except Exception as e:
        err(f"{di.name}.run failed: {e}")
        return False, None

def run_pipeline(discovered: List[DaemonInfo], reg: Dict[str, Any]) -> None:
    """Pipeline: Sheele -> Briar -> Codexa -> Janvier -> Aderyn"""
    name_map = {d.name.lower(): d for d in discovered}
    sheele = name_map.get("sheele")
    briar = name_map.get("briar")
    codexa = name_map.get("codexa")
    janvier = name_map.get("janvier")
    aderyn = name_map.get("aderyn")

    if not sheele:
        err("Sheele not discovered; cannot run pipeline.")
        return

    log("Starting pipeline: Sheele -> Briar -> Codexa -> Janvier -> Aderyn")

    # Sheele
    log("Running Sheele…")
    ok, sheele_out = try_run_daemon(sheele, payload={"input": str(SHEELE_DEFAULT_INPUT)}, registry=reg)
    if not ok:
        err("Sheele failed; aborting pipeline.")
        return

    # Briar
    if briar and briar.run_callable:
        log("Running Briar…")
        ok, briar_out = try_run_daemon(briar, payload=sheele_out, registry=reg)
        if not ok:
            warn("Briar failed; continuing with Sheele output.")
            briar_out = sheele_out
    else:
        warn("Briar not available; skipping.")
        briar_out = sheele_out

    # Codexa
    if codexa and codexa.run_callable:
        log("Running Codexa…")
        ok, codexa_out = try_run_daemon(codexa, payload=briar_out, registry=reg)
        if not ok:
            warn("Codexa failed; continuing without Codexa output.")
            codexa_out = None
    else:
        warn("Codexa not available; skipping.")
        codexa_out = None

    # Janvier
    # Janvier converts Briar's cleaned .txt conversations into .chaos threads,
    # so prefer Briar output when available (fallback to newer outputs if Briar is absent).
    janvier_payload = briar_out if briar_out is not None else codexa_out
    if janvier and janvier.run_callable:
        log("Running Janvier…")
        ok, janvier_out = try_run_daemon(janvier, payload=janvier_payload, registry=reg)
        if not ok:
            warn("Janvier failed.")
            janvier_out = None
    else:
        warn("Janvier not available; skipping.")
        janvier_out = None

    # Aderyn
    if not janvier_out:
        warn("Aderyn depends on Janvier output; skipping because Janvier produced no output.")
    elif aderyn and aderyn.run_callable:
        log("Running Aderyn…")
        ok, aderyn_out = try_run_daemon(aderyn, payload=janvier_out, registry=reg)
        if not ok:
            warn("Aderyn failed.")
    else:
        warn("Aderyn not available; skipping.")

    log("Pipeline complete.")

# -----------------------------
# CLI
# -----------------------------
def print_health_table(discovered: List[DaemonInfo]) -> None:
    cols = ["Name", "Status", "Run()", "Module"]
    widths = [14, 10, 6, 48]
    header = " | ".join(c.ljust(w) for c, w in zip(cols, widths))
    print("\n" + header)
    print("-" * len(header))
    for d in discovered:
        status = d.health.get("status", "unknown")
        runflag = "yes" if d.run_callable else "no"
        line = " | ".join([
            d.name.ljust(widths[0]),
            status.ljust(widths[1]),
            runflag.ljust(widths[2]),
            str(d.module_path).ljust(widths[3]),
        ])
        print(line)
    print()

def main():
    log("Scanning daemon directory…")
    discovered = discover_daemons()
    if not discovered:
        err(f"No daemons found under {DAEMON_DIR}")
        sys.exit(1)
    log(f"Discovered {len(discovered)} daemon(s). Probing…")
    discovered = [probe_daemon(d) for d in discovered]
    reg = load_registry()
    reg = merge_discovery_into_registry(reg, discovered)

    while True:
        print("\n=== Rhea Orchestrator ===")
        print("1) Show health map")
        print("2) Fix Sheele input to OpenAI export path")
        print("3) Run pipeline (Sheele -> Briar -> Codexa -> Janvier -> Aderyn)")
        print("4) Open registry file location")
        print("5) Exit")
        choice = input("Select: ").strip()
        if choice == "1":
            print_health_table(discovered)
        elif choice == "2":
            ok = ensure_sheele_input_points_to_export(reg)
            if ok:
                log(f"Set Sheele input -> {SHEELE_DEFAULT_INPUT}")
            else:
                err("Could not set Sheele input.")
        elif choice == "3":
            run_pipeline(discovered, reg)
        elif choice == "4":
            print(f"Registry: {REGISTRY_PATH}")
            try:
                os.startfile(REGISTRY_PATH.parent)  # Windows only
            except Exception:
                pass
        elif choice == "5":
            log("Goodnight, Dreambearer.")
            break
        else:
            print("…that’s not a thing. Try 1-5.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[Rhea] Interrupted. See you soon.")
