#!/usr/bin/env python3
# Rhea Orchestrator — self-managing daemon system
# - Watches ./daemons for changes
# - Maintains ./config/rhea_registry.json with schema validation
# - Auto-discovers daemon metadata from YAML docstring headers
# - Self-corrects common issues and keeps teams/pairs in sync
# - CLI for scan/list/start/stop/add/validate/fix/gui

from __future__ import annotations
import os, sys, json, time, threading, subprocess, shutil, difflib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

import yaml  # PyYAML
from jsonschema import Draft7Validator
import builtins as _bi
from rich.console import Console
from rich.table import Table
import typer

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except Exception:
    WATCHDOG_AVAILABLE = False

APP = typer.Typer(help="Rhea — self-managing daemon orchestrator")
C = Console()
# Layout assumptions:
# - This script resides in Rhea/scripts/
# - The Rhea package dir is the parent of this script
# - The Eden daemon root directory is the parent of Rhea (contains all daemon folders)
RHEA_DIR = Path(__file__).resolve().parent.parent  # .../Rhea
DAEMONS_ROOT = RHEA_DIR.parent                     # .../daemons

# Directories for Rhea's own state/config
DIR_DAEMONS = DAEMONS_ROOT
DIR_CONFIG = RHEA_DIR / "config"
DIR_BACKUPS = RHEA_DIR / "backups"
DIR_LOGS = RHEA_DIR / "logs"
REGISTRY_PATH = DIR_CONFIG / "rhea_registry.json"
SCHEMA_PATH = DIR_CONFIG / "rhea_schema.json"
GUI_PATH = RHEA_DIR / "scripts" / "rhea_gui.self_editing.py"

DEFAULT_PALETTES = {
    "eden_dream": {"bg": "#0b1020", "fg": "#e6f0ff", "accent": "#7aa2f7", "muted": "#94a3b8"},
    "velvet_division": {"bg": "#1a1417", "fg": "#F7E7F3", "accent": "#E84C7F", "muted": "#A08A98"},
    "rootfire": {"bg": "#0e0f0a", "fg": "#f0f5e1", "accent": "#b0f566", "muted": "#93a48a"}
}

SCHEMA_JSON = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Rhea Registry",
    "type": "object",
    "required": ["version", "palettes", "daemons", "teams", "groups", "pairs", "tasks"],
    "properties": {
        "version": {"type": "integer", "minimum": 1},
        "palettes": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "properties": {
                    "bg": {"type": "string"},
                    "fg": {"type": "string"},
                    "accent": {"type": "string"},
                    "muted": {"type": "string"}
                },
                "required": ["bg", "fg", "accent", "muted"]
            }
        },
        "daemons": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "required": ["name", "path", "enabled", "tags", "start", "team", "group"],
                "properties": {
                    "name": {"type": "string"},
                    "path": {"type": "string"},
                    "enabled": {"type": "boolean"},
                    "tags": {"type": "array", "items": {"type": "string"}},
                    "team": {"type": "string"},
                    "group": {"type": "string"},
                    "env": {"type": "object", "additionalProperties": {"type": "string"}},
                    "start": {
                        "type": "object",
                        "required": ["type", "args"],
                        "properties": {
                            "type": {"type": "string", "enum": ["python", "shell"]},
                            "args": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                }
            }
        },
        "teams": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "required": ["members"],
                "properties": {"members": {"type": "array", "items": {"type": "string"}}}
            }
        },
        "groups": {"type": "object", "additionalProperties": {"type": "object"}},
        "pairs": {"type": "array", "items": {"type": "array", "items": {"type": "string"}, "minItems": 2, "maxItems": 2}},
        "tasks": {"type": "array", "items": {"type": "object", "properties": {
            "name": {"type": "string"},
            "target": {"type": "string"},
            "cmd": {"type": "string"},
            "schedule": {"type": "string"}
        }, "required": ["name", "target", "cmd"]}}
    }
}

RUNNING: Dict[str, subprocess.Popen] = {}

# ----------------- Utilities -----------------

def _ensure_dirs():
    # Ensure Rhea's own dirs exist; the daemon root should already exist
    for d in (DIR_CONFIG, DIR_BACKUPS, DIR_LOGS):
        d.mkdir(parents=True, exist_ok=True)


def _load_registry() -> Dict[str, Any]:
    if not REGISTRY_PATH.exists():
        return {
            "version": 1,
            "palettes": DEFAULT_PALETTES,
            "daemons": {},
            "teams": {},
            "groups": {},
            "pairs": [],
            "tasks": []
        }
    with REGISTRY_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # Sanitize/repair common corruption (e.g., null values) before use
    if not isinstance(data, dict):
        data = {}
    data.setdefault("version", 1)
    if not isinstance(data.get("palettes"), _bi.dict) or not data.get("palettes"):
        data["palettes"] = DEFAULT_PALETTES
    if not isinstance(data.get("daemons"), _bi.dict):
        data["daemons"] = {}
    if not isinstance(data.get("teams"), _bi.dict):
        data["teams"] = {}
    if not isinstance(data.get("groups"), _bi.dict):
        data["groups"] = {}
    if not isinstance(data.get("pairs"), _bi.list):
        data["pairs"] = []
    if not isinstance(data.get("tasks"), _bi.list):
        data["tasks"] = []
    return data


def _save_registry(data: Dict[str, Any], backup: bool = True):
    validator = Draft7Validator(SCHEMA_JSON)
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
    if errors:
        C.print("[red]Validation failed; not saving.[/red]")
        for e in errors:
            C.print(f"[red]- {'/'.join(map(str, e.path))}: {e.message}[/red]")
        raise typer.Exit(code=1)
    if backup and REGISTRY_PATH.exists():
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(REGISTRY_PATH, DIR_BACKUPS / f"registry_{ts}.json")
    with REGISTRY_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    C.print("[green]Registry saved.[/green]")


def _write_schema_if_missing():
    if not SCHEMA_PATH.exists():
        with SCHEMA_PATH.open("w", encoding="utf-8") as f:
            json.dump(SCHEMA_JSON, f, indent=2)


def _read_yaml_docstring(pyfile: Path) -> Optional[Dict[str, Any]]:
    try:
        text = pyfile.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None
    # First triple-quoted block is treated as YAML
    for quote in ('"""', "'''"):
        if text.strip().startswith(quote):
            end = text.find(quote, 3)
            if end > 3:
                block = text[3:end]
                try:
                    data = yaml.safe_load(block) or {}
                    if isinstance(data, dict):
                        return data
                except Exception:
                    return None
    return None


def discover_daemons() -> Dict[str, Dict[str, Any]]:
    discovered: Dict[str, Dict[str, Any]] = {}
    if not DIR_DAEMONS.exists():
        return discovered
    # Skip heavy/noisy folders from discovery
    SKIP_PARTS = {
        "node_modules", "Rhea_historic", "_inbox", ".git", "__pycache__", "logs"
    }
    for pyfile in DIR_DAEMONS.rglob("*.py"):
        # ignore if any part of the path is in SKIP_PARTS
        if any(part in SKIP_PARTS for part in pyfile.parts):
            continue
        meta = _read_yaml_docstring(pyfile)
        if not meta:
            continue
        daemon_name = meta.get("daemon", {}).get("name") or meta.get("name")
        if not daemon_name:
            continue
        start_cmd = meta.get("daemon", {}).get("start") or meta.get("start")
        team = meta.get("daemon", {}).get("team") or meta.get("team", "Unassigned")
        group = meta.get("daemon", {}).get("group") or meta.get("group", "Default")
        tags = meta.get("daemon", {}).get("tags") or meta.get("tags") or []
        env = meta.get("daemon", {}).get("env") or meta.get("env") or {}
        start: Dict[str, Any]
        if isinstance(start_cmd, str):
            # Split on spaces, naive
            start = {"type": "shell", "args": [start_cmd]}
        elif isinstance(start_cmd, dict):
            start = start_cmd
        else:
            start = {"type": "python", "args": [str(pyfile.name)]}
        discovered[daemon_name] = {
            "name": daemon_name,
            # Store path relative to the daemons root (daemons)
            "path": str(pyfile.relative_to(DAEMONS_ROOT)),
            "enabled": True,
            "tags": tags,
            "team": team,
            "group": group,
            "env": env,
            "start": start
        }
    return discovered


# ----------------- Self-correction -----------------

def reconcile_registry(reg: Dict[str, Any], discovered: Dict[str, Dict[str, Any]]) -> Tuple[Dict[str, Any], List[str]]:
    logs: List[str] = []
    # Add or update discovered daemons
    for name, d in discovered.items():
        if name not in reg["daemons"]:
            reg["daemons"][name] = d
            logs.append(f"+ added daemon {name}")
        else:
            # merge on path/team/group/tags/env/start; keep enabled flag
            cur = reg["daemons"][name]
            changed = []
            for k in ("path", "team", "group", "tags", "env", "start"):
                if cur.get(k) != d.get(k):
                    cur[k] = d.get(k)
                    changed.append(k)
            if changed:
                logs.append(f"~ updated {name}: {', '.join(changed)}")
    # Disable missing files
    for name, d in list(reg["daemons"].items()):
        path = DAEMONS_ROOT / d.get("path", "")
        if not path.exists():
            if d.get("enabled", True):
                d["enabled"] = False
                logs.append(f"! disabled {name} (file missing)")
    # Sync teams -> members
    team_members: Dict[str, List[str]] = {}
    for name, d in reg["daemons"].items():
        team = d.get("team", "Unassigned")
        team_members.setdefault(team, []).append(name)
    for team, members in team_members.items():
        t = reg["teams"].setdefault(team, {"members": []})
        if sorted(t["members"]) != sorted(members):
            t["members"] = sorted(members)
            logs.append(f"~ synced team {team} members")
    # Drop empty teams not referenced
    for team in list(reg["teams"].keys()):
        if team not in team_members:
            del reg["teams"][team]
            logs.append(f"- removed empty team {team}")
    return reg, logs


# ----------------- Process control -----------------

def _python_exe() -> str:
    # Favor current interpreter
    return sys.executable or "python"


def start_daemon(name: str, reg: Dict[str, Any]):
    if name in RUNNING:
        C.print(f"[yellow]{name} already running[/yellow]")
        return
    d = reg["daemons"].get(name)
    if not d or not d.get("enabled", True):
        C.print(f"[red]Cannot start {name}: not found or disabled[/red]")
        return
    cwd = (DAEMONS_ROOT / d["path"]).parent
    env = os.environ.copy()
    env.update({k: v for k, v in d.get("env", {}).items()})
    start = d.get("start", {"type": "python", "args": [Path(d["path"]).name]})
    if start.get("type") == "python":
        args = [_python_exe()] + start.get("args", [])
    else:
        # shell command string or args array
        args = start.get("args", [])
    C.print(f"[cyan]Starting {name}[/cyan]: {' '.join(args)} @ {cwd}")
    p = subprocess.Popen(args, cwd=str(cwd), env=env)
    RUNNING[name] = p


def stop_daemon(name: str):
    p = RUNNING.get(name)
    if not p:
        C.print(f"[yellow]{name} not running[/yellow]")
        return
    p.terminate()
    try:
        p.wait(timeout=5)
    except Exception:
        p.kill()
    del RUNNING[name]
    C.print(f"[green]Stopped {name}[/green]")


# ----------------- Watchdog -----------------
class RheaHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.py') or event.src_path.endswith('.json'):
            C.print("[blue]Change detected; reconciling...[/blue]")
            reg = _load_registry()
            discovered = discover_daemons()
            reg, logs = reconcile_registry(reg, discovered)
            _save_registry(reg)
            for line in logs:
                C.print("[magenta]•[/magenta]", line)


# ----------------- CLI commands -----------------
@APP.command()
def init():
    """Create folders and seed registry + schema."""
    _ensure_dirs()
    _write_schema_if_missing()
    reg = _load_registry()
    _save_registry(reg, backup=False)
    C.print("[green]Initialized Rhea folders and registry.[/green]")


@APP.command()
def scan():
    """Scan daemons and reconcile into registry."""
    _ensure_dirs()
    discovered = discover_daemons()
    reg = _load_registry()
    reg, logs = reconcile_registry(reg, discovered)
    _save_registry(reg)
    for line in logs:
        C.print("[magenta]•[/magenta]", line)
    C.print(f"[bold]{len(discovered)}[/bold] daemons discovered.")


@APP.command(name="list")
def list_cmd(kind: str = typer.Argument("daemons", help="daemons|teams|pairs|tasks")):
    reg = _load_registry()
    if kind == "daemons":
        tbl = Table(title="Daemons")
        for col in ("name", "enabled", "team", "group", "path"):
            tbl.add_column(col)
        for name, d in sorted(reg["daemons"].items()):
            tbl.add_row(d.get("name", name), str(d.get("enabled", False)), d.get("team", ""), d.get("group", ""), d.get("path", ""))
        C.print(tbl)
    elif kind == "teams":
        tbl = Table(title="Teams")
        tbl.add_column("team"); tbl.add_column("members")
        for team, t in sorted(reg["teams"].items()):
            tbl.add_row(team, ", ".join(t.get("members", [])))
        C.print(tbl)
    elif kind == "pairs":
        for a, b in reg.get("pairs", []):
            C.print(f"• {a} ↔ {b}")
    elif kind == "tasks":
        for t in reg.get("tasks", []):
            C.print(f"• {t.get('name')} -> {t.get('target')} [{t.get('schedule', '-')}] :: {t.get('cmd')}")
    else:
        C.print("[red]Unknown kind[/red]")


@APP.command()
def add_daemon(from_file: Path):
    """Add/refresh a daemon by reading its YAML docstring metadata."""
    if not from_file.exists():
        C.print("[red]File not found[/red]"); raise typer.Exit(1)
    meta = _read_yaml_docstring(from_file)
    if not meta:
        C.print("[red]No YAML docstring found[/red]"); raise typer.Exit(1)
    name = meta.get("daemon", {}).get("name") or meta.get("name")
    if not name:
        C.print("[red]Missing name in metadata[/red]"); raise typer.Exit(1)
    target_dir = DIR_DAEMONS / name
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / from_file.name
    if from_file.resolve() != target_path.resolve():
        shutil.copy2(str(from_file), str(target_path))
    reg = _load_registry()
    disc = discover_daemons()
    reg, logs = reconcile_registry(reg, disc)
    _save_registry(reg)
    for line in logs:
        C.print("[magenta]•[/magenta]", line)


@APP.command()
def validate():
    reg = _load_registry()
    errors = list(Draft7Validator(SCHEMA_JSON).iter_errors(reg))
    if not errors:
        C.print("[green]Registry is valid.[/green]")
        raise typer.Exit(0)
    for e in errors:
        C.print(f"[red]- {'/'.join(map(str, e.path))}: {e.message}[/red]")
    raise typer.Exit(1)


@APP.command()
def fix(apply: bool = typer.Option(True, help="apply fixes (otherwise just preview)")):
    reg = _load_registry()
    disc = discover_daemons()
    new, logs = reconcile_registry(reg, disc)
    diff = difflib.unified_diff(json.dumps(reg, indent=2).splitlines(), json.dumps(new, indent=2).splitlines(), lineterm="")
    C.print("\n".join(diff))
    if apply:
        _save_registry(new)
        for line in logs:
            C.print("[magenta]•[/magenta]", line)


@APP.command()
def start(name: str):
    reg = _load_registry(); start_daemon(name, reg)


@APP.command()
def stop(name: str):
    stop_daemon(name)


@APP.command()
def start_team(team: str):
    reg = _load_registry()
    for name in reg["teams"].get(team, {}).get("members", []):
        start_daemon(name, reg)


@APP.command()
def stop_team(team: str):
    reg = _load_registry()
    for name in reg["teams"].get(team, {}).get("members", []):
        stop_daemon(name)


@APP.command()
def watch():
    if not WATCHDOG_AVAILABLE:
        C.print("[red]watchdog not installed[/red]"); raise typer.Exit(1)
    _ensure_dirs()
    handler = RheaHandler()
    obs = Observer(); obs.schedule(handler, str(DIR_DAEMONS), recursive=True)
    obs.schedule(handler, str(DIR_CONFIG), recursive=False)
    obs.start()
    C.print("[green]Watching for changes… Ctrl+C to stop.[/green]")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        obs.stop(); obs.join()


@APP.command()
def gui():
    if not GUI_PATH.exists():
        C.print("[red]GUI file missing: rhea_gui.self_editing.py[/red]"); raise typer.Exit(1)
    subprocess.call([_python_exe(), str(GUI_PATH)])


if __name__ == "__main__":
    APP()
