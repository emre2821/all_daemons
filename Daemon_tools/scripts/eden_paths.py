from __future__ import annotations
from pathlib import Path
import os
from typing import Optional


def _find_eden_root_from_here(start: Optional[Path] = None) -> Optional[Path]:
    here = (start or Path(__file__).resolve()).parent
    for p in [here] + list(here.parents):
        if (p / "all_daemons").exists():
            return p
    # Try from CWD as a fallback
    cwd = Path.cwd()
    for p in [cwd] + list(cwd.parents):
        if (p / "all_daemons").exists():
            return p
    return None


def eden_root() -> Path:
    """Resolve the EDEN_ROOT in a cross-platform, repo-friendly way.

    Priority:
    1) EDEN_ROOT env var (if exists on disk)
    2) Walk up from this file until a parent containing 'all_daemons'
    3) Walk up from CWD until a parent containing 'all_daemons'
    4) Fallback to CWD
    """
    env = os.environ.get("EDEN_ROOT")
    if env:
        p = Path(env)
        if p.exists():
            return p
    detected = _find_eden_root_from_here()
    if detected:
        return detected
    return Path.cwd()


def daemons_root() -> Path:
    return eden_root() / "all_daemons"


def logs_dir() -> Path:
    p = daemons_root() / "_logs"
    p.mkdir(parents=True, exist_ok=True)
    return p


def events_bus_path() -> Path:
    return logs_dir() / "events.jsonl"


def daemon_dir(name: str) -> Path:
    return daemons_root() / name


def resolve_path(*parts: str) -> Path:
    return Path(os.path.join(*[str(x) for x in parts]))

