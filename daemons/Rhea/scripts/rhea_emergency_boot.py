#!/usr/bin/env python3
"""
Rhea Emergency Boot — triage disk space, repair layout, and start the battalion.

What it does (in order):
1) TRIAGE: check free space, list top heavy dirs/files, optional cache purge
2) REPAIR: build a safe move plan from simple rules → preview or apply with undo log
3) ACTIVATE: if full_rhea.complete_build.py exists, init/scan/fix and start daemons
             by TAGS (parser,label,organizer,catalog,index,sort,cleanup)
             otherwise, fallback: run every *.py under daemons/** as a process

Safety:
- Dry-run by default. Use --apply to actually move or purge.
- Every move is logged to backups/move_log_<ts>.json for --undo.
- Avoids moving .git, .github, node_modules, venv/.venv, __pycache__, .gradle, .m2, .idea, .vscode

Deps: standard library + (optional) rich for nicer output.
If rich is missing, it prints plain text.
"""
from __future__ import annotations
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple, Any

# --- Paths -------------------------------------------------------------
# Resolve paths relative to the Rhea package directory
ROOT = Path(__file__).resolve().parents[1]
# The Eden "daemons" root is the parent of Rhea
DIR_DAEMONS = ROOT.parent
DIR_CONFIG = ROOT / "configs"
DIR_BACKUPS = ROOT / "backups"
DIR_LOGS = ROOT / "logs"
REGISTRY = DIR_CONFIG / "rhea_registry.json"
# Rhea orchestrator script lives under scripts/
RHEA = ROOT / "scripts" / "full_rhea.complete_build.py"

# --- Pretty print shim -------------------------------------------------
try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import track
    RICH = True
    C = Console()
except Exception:
    RICH = False
    class _Dummy:
        def print(self, *a, **k): print(*a)
    C = _Dummy()
    def track(it, **_): 
        return it

# --- Palettes (just for vibes/log clarity) ----------------------------
PALETTES = {
    "eden_dream": {"bg": "#0b1020", "fg": "#e6f0ff", "accent": "#7aa2f7", "muted": "#94a3b8"},
    "velvet_division": {"bg": "#1a1417", "fg": "#F7E7F3", "accent": "#E84C7F", "muted": "#A08A98"},
    "rootfire": {"bg": "#0e0f0a", "fg": "#f0f5e1", "accent": "#b0f566", "muted": "#93a48a"},
}
ACCENT = PALETTES["eden_dream"]["accent"]

# --- Defaults & rules --------------------------------------------------
DEFAULT_TAGS = ["parser","label","organizer","catalog","index","sort","cleanup"]
SAFE_EXCLUDES = {".git",".github","node_modules","venv",".venv","__pycache__",".gradle",".m2",".idea",".vscode",".pytest_cache"}
DEFAULT_RULES = {
    "version": 1,
    "targets": {
        "py_daemon_default": "daemons/Unsorted",
        "chaos_default": "EchoTree/_inbox_chaos",
        "vas_default": "EchoTree/_inbox_vas",
        "docs_default": "_docs/_inbox",
        "assets_default": "_assets/_inbox"
    },
    "ext_buckets": {
        "daemon_py": [".py"],
        "chaos": [".chaos*"],       # <---- wildcard now
        "vas": [".vas", ".docuvas", ".vas.md"],
        "docs": [".md", ".txt", ".rtf", ".pdf"],
        "assets": [".png", ".jpg", ".jpeg", ".gif", ".svg",
                   ".webp", ".mp3", ".wav", ".mp4", ".mov", ".avi"]
    },
    "purge_dirs": ["__pycache__", ".pytest_cache", "node_modules",
                   ".gradle", "build", "dist", ".m2/repository"]
}

# --- Utilities ---------------------------------------------------------
def ensure_dirs():
    for d in (DIR_DAEMONS, DIR_CONFIG, DIR_BACKUPS, DIR_LOGS):
        d.mkdir(parents=True, exist_ok=True)

def bytes_to_gb(n: int) -> float:
    return round(n / (1024**3), 2)

def freespace_gb(path: Path) -> float:
    st = shutil.disk_usage(str(path))
    return bytes_to_gb(st.free)

def load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default

def save_json(path: Path, obj: Any):
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")

# --- TRIAGE ------------------------------------------------------------
def dir_size(path: Path) -> int:
    total = 0
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in SAFE_EXCLUDES]
        for f in files:
            try:
                total += (Path(root)/f).stat().st_size
            except Exception:
                pass
    return total

def top_heavy(root: Path, topn: int = 20) -> List[Tuple[str,int]]:
    sizes = []
    for p in root.iterdir():
        try:
            s = dir_size(p) if p.is_dir() else p.stat().st_size
            sizes.append((str(p), s))
        except Exception:
            continue
    sizes.sort(key=lambda x: x[1], reverse=True)
    return sizes[:topn]

def purge_caches(root: Path, rules: Dict, apply: bool=False) -> List[str]:
    hits = []
    for pattern in rules.get("purge_dirs", []):
        for p in root.rglob(pattern):
            if not p.exists(): 
                continue
            # Safety guard: never touch root or config/logs
            if p.resolve() in (ROOT, DIR_CONFIG.resolve(), DIR_LOGS.resolve()): 
                continue
            hits.append(str(p))
            if apply:
                try:
                    if p.is_dir(): shutil.rmtree(p, ignore_errors=True)
                    else: p.unlink(missing_ok=True)
                except Exception as e:
                    C.print(f"[red]Failed purge {p}: {e}[/red]" if RICH else f"Failed purge {p}: {e}")
    return hits

# --- REPAIR PLAN -------------------------------------------------------
@dataclass
class MoveOp:
    src: str
    dst: str

def ext_bucket(ext: str, rules: Dict) -> str:
    for bucket, exts in rules.get("ext_buckets", {}).items():
        if ext.lower() in [e.lower() for e in exts]:
            return bucket
    return "other"

def plan_repairs(root: Path, rules: Dict) -> List[MoveOp]:
    ops: List[MoveOp] = []
    # known safe inboxes
    targets = rules.get("targets", {})
    for p in root.rglob("*"):
        if any(seg in SAFE_EXCLUDES for seg in p.parts):
            continue
        if not p.is_file():
            continue
        # Skip registry/config/this script
        if p == REGISTRY or p.name.startswith("move_log_") or p.name == Path(__file__).name:
            continue
        # Keep files already under expected roots
        if "daemons" in p.parts:
            continue

        ext = p.suffix
        bucket = ext_bucket(ext, rules)
        if bucket == "daemon_py" and ext == ".py":
            dst_base = ROOT / targets.get("py_daemon_default", "daemons/Unsorted")
        elif bucket == "chaos":
            dst_base = ROOT / targets.get("chaos_default", "EchoTree/_inbox_chaos")
        elif bucket == "vas":
            dst_base = ROOT / targets.get("vas_default", "EchoTree/_inbox_vas")
        elif bucket == "docs":
            dst_base = ROOT / targets.get("docs_default", "_docs/_inbox")
        elif bucket == "assets":
            dst_base = ROOT / targets.get("assets_default", "_assets/_inbox")
        else:
            # Leave unknowns in place unless they’re clearly stray python
            if ext == ".py":
                dst_base = ROOT / targets.get("py_daemon_default", "daemons/Unsorted")
            else:
                continue

        # Preserve folder hint by nesting last parent name to avoid collisions
        hint = p.parent.name
        dst = dst_base / hint / p.name
        ops.append(MoveOp(str(p), str(dst)))
    return ops

def apply_moves(ops: List[MoveOp], limit: int, log_path: Path) -> Tuple[int,int]:
    moved = 0; skipped = 0
    log = {"when": int(time.time()), "moves": []}
    for op in track(ops[:limit], description="Applying moves…") if RICH else ops[:limit]:
        src, dst = Path(op.src), Path(op.dst)
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            log["moves"].append({"from": op.src, "to": op.dst})
            moved += 1
        except Exception as e:
            C.print(f"[red]Skip {src}: {e}[/red]" if RICH else f"Skip {src}: {e}")
            skipped += 1
    save_json(log_path, log)
    return moved, skipped

def undo_moves(log_path: Path) -> Tuple[int,int]:
    data = load_json(log_path, {"moves": []})
    undone = 0; skipped = 0
    for m in reversed(data.get("moves", [])):
        src = Path(m["to"]); dst = Path(m["from"])
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            undone += 1
        except Exception as e:
            C.print(f"[red]Undo skip {src}: {e}[/red]" if RICH else f"Undo skip {src}: {e}")
            skipped += 1
    return undone, skipped

# --- ACTIVATE ----------------------------------------------------------
def run_rhea(*args: str) -> int:
    cmd = [sys.executable, str(RHEA)] + list(args)
    return subprocess.call(cmd)

def start_with_rhea(tags: List[str], parallel: int) -> int:
    # Ensure registry is fresh
    run_rhea("init"); run_rhea("scan"); run_rhea("fix", "--apply")
    reg = load_json(REGISTRY, {})
    daemons = reg.get("daemons", {})
    # Select daemons by tags
    targets = [name for name, d in daemons.items()
               if d.get("enabled", True) and any(t in (d.get("tags") or []) for t in tags)]
    if not targets:
        # fallback: start all enabled
        targets = [name for name, d in daemons.items() if d.get("enabled", True)]
    if parallel <= 1:
        for n in targets:
            run_rhea("start", n)
    else:
        with ThreadPoolExecutor(max_workers=parallel) as ex:
            futs = [ex.submit(run_rhea, "start", n) for n in targets]
            for _ in as_completed(futs): pass
    return 0

def start_without_rhea(parallel: int) -> int:
    # Fallback: run every python file under daemons/** directly
    files = [p for p in DIR_DAEMONS.rglob("*.py")]
    if not files:
        C.print("No daemons found under daemons/", style="yellow" if RICH else None)
        return 0
    def launch(p: Path) -> int:
        return subprocess.Popen([sys.executable, str(p)], cwd=str(p.parent)).pid
    if parallel <= 1:
        for p in files:
            launch(p)
    else:
        with ThreadPoolExecutor(max_workers=parallel) as ex:
            futs = [ex.submit(launch, p) for p in files]
            for _ in as_completed(futs): pass
    return 0

# --- MAIN --------------------------------------------------------------
def main():
    ensure_dirs()
    rules_path = DIR_CONFIG / "repair_rules.json"
    if not rules_path.exists():
        save_json(rules_path, DEFAULT_RULES)

    ap = argparse.ArgumentParser(prog="rhea-emergency-boot", description="Triage → Repair → Activate")
    ap.add_argument("--apply", action="store_true", help="actually move/purge (default is dry-run)")
    ap.add_argument("--purge-caches", action="store_true", help="purge cache dirs (safe list) before repair")
    ap.add_argument("--limit", type=int, default=500, help="max files to move this run")
    ap.add_argument("--tags", type=str, default=",".join(DEFAULT_TAGS), help="comma tags to start via Rhea")
    ap.add_argument("--parallel", type=int, default=3, help="parallelism for starting daemons")
    ap.add_argument("--undo", type=str, help="path to move_log_*.json to undo")
    ap.add_argument("--skip-activate", action="store_true", help="only triage/repair; do not start daemons")
    ap.add_argument("--root", type=str, default=str(ROOT), help="root directory to triage/repair")
    args = ap.parse_args()

    root = Path(args.root)
    rules = load_json(rules_path, DEFAULT_RULES)

    if args.undo:
        logp = Path(args.undo)
        u, s = undo_moves(logp)
        C.print(f"[cyan]Undo complete[/cyan]: restored {u}, skipped {s}" if RICH else f"Undo complete: {u} restored, {s} skipped")
        return

    # 1) TRIAGE
    free = freespace_gb(root)
    C.print(f"[bold]Free space:[/bold] {free} GB" if RICH else f"Free space: {free} GB")
    heavy = top_heavy(root, topn=15)
    if RICH:
        tbl = Table(title="Top heavy items (by size)"); tbl.add_column("Path"); tbl.add_column("GB", justify="right")
        for p, sz in heavy: tbl.add_row(p, str(bytes_to_gb(sz)))
        C.print(tbl)
    else:
        for p, sz in heavy: print(f"{p}  {bytes_to_gb(sz)} GB")

    if args.purge_caches:
        hits = purge_caches(root, rules, apply=args.apply)
        C.print(f"[magenta]Cache hits:[/magenta] {len(hits)} (apply={args.apply})" if RICH else f"Cache hits: {len(hits)} (apply={args.apply})")

    # 2) REPAIR
    ops = plan_repairs(root, rules)
    C.print(f"[bold]{len(ops)}[/bold] files flagged for relocation." if RICH else f"{len(ops)} files flagged for relocation.")
    if not args.apply:
        # Preview first 40 moves
        preview = ops[:40]
        for m in preview:
            # Use ASCII arrows to avoid Windows console encoding issues
            C.print(f"-> {m.src}  [dim]->[/dim]  {m.dst}" if RICH else f"-> {m.src} -> {m.dst}")
        C.print("(dry-run; nothing moved). Use --apply to execute." if RICH else "dry-run; nothing moved.")
    else:
        ts = time.strftime("%Y%m%d_%H%M%S")
        logp = DIR_BACKUPS / f"move_log_{ts}.json"
        moved, skipped = apply_moves(ops, limit=args.limit, log_path=logp)
        C.print(f"[green]Moved[/green] {moved}, skipped {skipped}. Log: {logp}" if RICH else f"Moved {moved}, skipped {skipped}. Log: {logp}")

    # 3) ACTIVATE
    if args.skip_activate:
        return

    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    if Path(RHEA).exists():
        C.print(
            f"[cyan]Starting via Rhea[/cyan] from {RHEA} by tags: {tags}" if RICH
            else f"Starting via Rhea from {RHEA} by tags: {tags}"
        )
        start_with_rhea(tags, parallel=args.parallel)
    else:
        C.print(
            "[yellow]Rhea not found; fallback launcher[/yellow]" if RICH
            else "Rhea not found; fallback launcher"
        )
        start_without_rhea(parallel=args.parallel)

if __name__ == "__main__":
    main()
