from __future__ import annotations
from pathlib import Path
import os
from typing import Optional


def _find_eden_root_from_here(start: Optional[Path] = None) -> Optional[Path]:
    here = (start or Path(__file__).resolve()).parent

    def candidate_paths(seed: Path):
        return [seed] + list(seed.parents)

    def pick_best(candidates):
        if not candidates:
            return None
        # Prefer a parent whose daemons folder actually looks like the project root
        for p in candidates:
            if (p / "daemons" / "Rhea").exists() or (p / "shared" / "Daemon_tools").exists():
                return p
        return candidates[0]

    candidates = [p for p in candidate_paths(here) if (p / "daemons").exists()]
    if candidates:
        return pick_best(candidates)

    # Try from CWD as a fallback
    cwd = Path.cwd()
    candidates = [p for p in candidate_paths(cwd) if (p / "daemons").exists()]
    return pick_best(candidates)


def eden_root() -> Path:
    """Resolve the EDEN_ROOT in a cross-platform, repo-friendly way.

    Priority:
    1) EDEN_ROOT env var (if exists on disk)
    2) Walk up from this file until a parent containing 'daemons'
    3) Walk up from CWD until a parent containing 'daemons'
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


def eden_work_root() -> Path:
    env = os.environ.get("EDEN_WORK_ROOT")
    if env:
        p = Path(env)
        if p.exists():
            return p
    return eden_root()


def daemons_root() -> Path:
    return eden_root() / "daemons"


def shared_root() -> Path:
    return eden_root() / "shared"


def logs_dir() -> Path:
    p = eden_work_root() / "daemons" / "_logs"
    p.mkdir(parents=True, exist_ok=True)
    return p


def events_bus_path() -> Path:
    return logs_dir() / "events.jsonl"


def daemon_dir(name: str) -> Path:
    return daemons_root() / name


def resolve_path(*parts: str) -> Path:
    return Path(os.path.join(*[str(x) for x in parts]))


# Rhea-centric paths
def rhea_root() -> Path:
    return daemons_root() / "Rhea"


def rhea_outbox() -> Path:
    p = eden_work_root() / "daemons" / "Rhea" / "_outbox"
    p.mkdir(parents=True, exist_ok=True)
    return p


def daemon_out_dir(daemon_name: str) -> Path:
    # Standardized: place daemon outputs directly under Rhea/_outbox/<Daemon>
    p = rhea_outbox() / daemon_name
    p.mkdir(parents=True, exist_ok=True)
    return p
