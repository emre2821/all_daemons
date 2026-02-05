#!/usr/bin/env python3
"""
eden_aligner.py — Organizer & healer for C:\\EdenOS_Origin\\daemons

Goals
-----
1) Normalize daemon folders so Rhea can discover & run them.
2) Create expected per-daemon working dirs (logs/inbox/outbox/archive/tmp/work).
3) Detect and (optionally) patch hard-coded paths; create missing target folders.
4) Optionally call Saphira to heal *.daemon_*.json files and audit function lists.

Safety
------
- Default is DRY RUN. Use --apply to write changes.
- When patching code, creates a timestamped .bak alongside original.
- Only replaces exact literal occurrences of EDEN_ROOT patterns unless --aggressive.

Usage
-----
python eden_aligner.py --root "C:/EdenOS_Origin" --apply --patch-code --heal
python eden_aligner.py --work-root "D:/EdenOS_Runtime" --apply

"""

from __future__ import annotations
import os
import re
import ast
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

# --------- Defaults ---------
DEFAULT_EDEN_ROOT = Path(os.environ.get("EDEN_ROOT", Path.cwd()))
DEFAULT_WORK_ROOT = Path(os.environ.get("EDEN_WORK_ROOT", DEFAULT_EDEN_ROOT))
STANDARD_SUBDIRS = ["_logs", "_inbox", "_outbox", "_archive", "_tmp", "_work"]
HARDCODE_PATTERNS = [
    r"C:/EdenOS_Origin",
    r"C:\\EdenOS_Origin",
]

# --------- Helpers ---------

def ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(msg: str):
    print(f"[eden-align] {ts()} | {msg}")

# Discover primary script for a daemon dir (mirrors Rhea's strategy)

def discover_daemon_script(daemon_dir: Path) -> Optional[Path]:
    if not daemon_dir.is_dir():
        return None
    name_lower = daemon_dir.name.lower()
    # 1) exact match {name}.py (case-insensitive)
    for p in daemon_dir.iterdir():
        if p.is_file() and p.suffix.lower() == ".py" and p.stem.lower() == name_lower:
            return p
    # 2) single .py
    py_files = [p for p in daemon_dir.iterdir() if p.is_file() and p.suffix.lower() == ".py"]
    if len(py_files) == 1:
        return py_files[0]
    # 3) any .py whose stem contains the name
    for p in py_files:
        if name_lower in p.stem.lower():
            return p
    return None

# Ensure per-daemon standard subfolders exist

def ensure_standard_dirs(work_daemon_dir: Path, apply: bool) -> List[Path]:
    created = []
    for sub in STANDARD_SUBDIRS:
        target = work_daemon_dir / sub
        if not target.exists():
            if apply:
                target.mkdir(parents=True, exist_ok=True)
            created.append(target)
    return created

# If daemon folder has exactly one .py but it's not name-matching, optionally rename it

def maybe_rename_primary_py(daemon_dir: Path, apply: bool) -> Optional[Tuple[Path, Path]]:
    name_lower = daemon_dir.name.lower()
    py_files = [p for p in daemon_dir.iterdir() if p.is_file() and p.suffix.lower() == ".py"]
    if len(py_files) != 1:
        return None
    the_py = py_files[0]
    if the_py.stem.lower() != name_lower:
        new_path = daemon_dir / f"{name_lower}.py"
        if apply:
            the_py.rename(new_path)
        return (the_py, new_path)
    return None

# Parse Python file to collect literal paths and Path()/os.path.join() string args (best-effort)

class PathLiteralCollector(ast.NodeVisitor):
    def __init__(self):
        self.literal_strings: List[str] = []

    def visit_Constant(self, node: ast.Constant):
        if isinstance(node.value, str):
            s = node.value
            if any(p in s for p in HARDCODE_PATTERNS):
                self.literal_strings.append(s)
        self.generic_visit(node)

    def visit_JoinedStr(self, node: ast.JoinedStr):
        # f-strings: capture literal parts
        for v in node.values:
            if isinstance(v, ast.Constant) and isinstance(v.value, str):
                s = v.value
                if any(p in s for p in HARDCODE_PATTERNS):
                    self.literal_strings.append(s)
        self.generic_visit(node)

# Attempt to patch exact literal root occurrences to EDEN_ROOT variable

def patch_code_root_literals(py_path: Path, eden_root: Path, apply: bool, aggressive: bool=False) -> Tuple[int, Optional[Path]]:
    text = py_path.read_text(encoding="utf-8")
    original = text
    # Conservative replacements first
    for pat in HARDCODE_PATTERNS:
        text = text.replace(pat, str(eden_root).replace("\\", "/"))
    # Aggressive: also normalize doubled backslashes variants
    if aggressive:
        text = re.sub(r"C:[/\\]{1,2}EdenOS_Origin", str(eden_root).replace("\\", "/"), text)

    if text != original:
        backup = py_path.with_suffix(py_path.suffix + f".bak_{datetime.now():%Y%m%d%H%M%S}")
        if apply:
            py_path.rename(backup)
            py_path.write_text(text, encoding="utf-8")
        return (1, backup if apply else None)
    return (0, None)

# Ensure any referenced absolute directories exist (best-effort creates)

def ensure_referenced_dirs(py_path: Path, eden_root: Path, apply: bool) -> List[Path]:
    text = py_path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    c = PathLiteralCollector()
    c.visit(tree)
    made: List[Path] = []
    for s in c.literal_strings:
        # Normalize slashes
        s_norm = s.replace("\\", "/")
        # Only handle directories under Eden root
        if "EdenOS_Origin" not in s_norm:
            continue
        # Extract directory portion
        p = Path(s_norm)
        # If appears to be a file, consider its parent; otherwise the path itself
        target = p if p.suffix == "" else p.parent
        if not str(target).lower().startswith(str(eden_root).replace("\\", "/").lower()):
            # Map into eden_root if someone hard-coded C: on a different drive
            try:
                rel = Path(*Path(s_norm).parts[2:])  # drop drive + first folder
                target = eden_root / rel
            except Exception:
                continue
        # Create if missing
        if not target.exists():
            if apply:
                target.mkdir(parents=True, exist_ok=True)
            made.append(target)
    return made

# Optionally call Saphira to heal metadata/json descriptors

def run_saphira_heal(eden_root: Path, audit: bool, apply: bool) -> None:
    try:
        import importlib.util
        saphira_path = eden_root / "daemons" / "Saphira" / "saphira.py"
        if not saphira_path.exists():
            log("Saphira not found; skipping heal.")
            return
        spec = importlib.util.spec_from_file_location("Saphira", saphira_path)
        mod = importlib.util.module_from_spec(spec)  # type: ignore
        assert spec and spec.loader
        spec.loader.exec_module(mod)  # type: ignore
        SaphiraSynchronizer = getattr(mod, "SaphiraSynchronizer")
        sync = SaphiraSynchronizer(str(eden_root / "daemons"), logger_func=log)
        sync.run(audit=audit, force=apply)
    except Exception as e:
        log(f"Saphira heal failed: {e}")

# --------- Main aligner ---------

def align_all(eden_root: Path, work_root: Path, apply: bool, patch_code: bool, aggressive: bool, heal: bool) -> None:
    daemons = eden_root / "daemons"
    if not daemons.exists():
        raise SystemExit(f"Missing daemons at {daemons}")

    log(f"Scanning {daemons} …")
    for daemon_dir in sorted([p for p in daemons.iterdir() if p.is_dir()]):
        # skip special folders
        if daemon_dir.name.startswith("_"):
            continue
        log(f"-- Daemon: {daemon_dir.name}")

        # 1) ensure standard per-daemon dirs
        work_daemon_dir = work_root / "daemons" / daemon_dir.name
        created = ensure_standard_dirs(work_daemon_dir, apply)
        if created:
            log(f"   + created subdirs: {', '.join(str(p.name) for p in created)}")

        # 2) primary script discovery & optional rename
        primary = discover_daemon_script(daemon_dir)
        if not primary:
            log("   ! no primary script discovered")
            continue
        renamed = maybe_rename_primary_py(daemon_dir, apply)
        if renamed:
            old, new = renamed
            log(f"   ~ renamed {old.name} → {new.name}")
            primary = new
        else:
            log(f"   · script: {primary.name}")

        # 3) path sanity: create referenced dirs, optionally patch literals
        made = ensure_referenced_dirs(primary, eden_root, apply)
        if made:
            log(f"   + created referenced dirs: {', '.join(str(p) for p in made)}")

        if patch_code:
            changes, backup = patch_code_root_literals(primary, eden_root, apply, aggressive)
            if changes:
                log(f"   ~ patched root literals in {primary.name}{' (backup '+backup.name+')' if backup else ''}")

    # 4) Optional metadata heal via Saphira
    if heal:
        run_saphira_heal(eden_root, audit=True, apply=apply)

    log("Alignment complete.")

# --------- CLI ---------

def main():
    ap = argparse.ArgumentParser(description="EdenOS daemons organizer & healer")
    ap.add_argument("--root", default=str(DEFAULT_EDEN_ROOT), help="EDEN_ROOT (default: env EDEN_ROOT or CWD)")
    ap.add_argument("--work-root", default=str(DEFAULT_WORK_ROOT), help="EDEN_WORK_ROOT (default: env EDEN_WORK_ROOT or EDEN_ROOT)")
    ap.add_argument("--apply", action="store_true", help="Write changes (otherwise dry-run)")
    ap.add_argument("--patch-code", action="store_true", help="Replace hard-coded Eden root literals with your --root")
    ap.add_argument("--aggressive", action="store_true", help="Aggressively normalize any C:/\\EdenOS_Origin variants")
    ap.add_argument("--heal", action="store_true", help="Run Saphira to heal *.daemon_* files and audit functions")
    args = ap.parse_args()

    eden_root = Path(args.root)
    work_root = Path(args.work_root)
    align_all(eden_root, work_root, apply=args.apply, patch_code=args.patch_code, aggressive=args.aggressive, heal=args.heal)

if __name__ == "__main__":
    main()
