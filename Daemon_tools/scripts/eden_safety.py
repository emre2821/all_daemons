from __future__ import annotations
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, Dict, Any

try:
    from .eden_paths import logs_dir, events_bus_path
except Exception:
    # Fallback for direct script use
    import sys as _sys
    from pathlib import Path as _Path
    _HERE = _Path(__file__).resolve().parent
    if str(_HERE) not in _sys.path:
        _sys.path.append(str(_HERE))
    from eden_paths import logs_dir, events_bus_path  # type: ignore


# Simple Rook-like command filter
_DANGEROUS = re.compile(r"\b(rm\s+-rf|del\s+|format\b|exec\b|shutil\.rmtree\()", re.IGNORECASE)


def is_command_safe(command: str) -> bool:
    return _DANGEROUS.search(command) is None


def _jsonl_append(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def log_event(daemon: str, action: str, target: str = "", outcome: str = "", error: Optional[str] = None,
              extra: Optional[Dict[str, Any]] = None, log_dir: Optional[Path] = None) -> None:
    entry: Dict[str, Any] = {
        "daemon": daemon,
        "action": action,
        "target": target,
        "outcome": outcome,
    }
    if error:
        entry["error"] = error
    if extra:
        entry.update(extra)

    ldir = log_dir or logs_dir()
    _jsonl_append(ldir / f"{daemon}.log", entry)
    _jsonl_append(events_bus_path(), entry)


@dataclass
class SafetyContext:
    daemon: str
    dry_run: bool = True
    confirm: bool = False
    log_dir: Optional[Path] = None

    def require_confirm(self) -> None:
        if not self.confirm and not self.dry_run:
            print("[safety] Refusing to execute without --confirm; using --dry-run instead.")
            self.dry_run = True

    def log(self, action: str, target: str = "", outcome: str = "", error: Optional[str] = None,
            extra: Optional[Dict[str, Any]] = None) -> None:
        log_event(self.daemon, action, target, outcome, error=error, extra=extra, log_dir=self.log_dir)


def plan_or_delete(ctx: SafetyContext, paths: Iterable[Path]) -> None:
    """Delete files/dirs or just plan, respecting SafetyContext."""
    for p in paths:
        if ctx.dry_run or not ctx.confirm:
            print(f"[DRY RUN] Would delete: {p}")
            ctx.log("plan_delete", str(p), outcome="planned")
            continue
        try:
            if p.is_dir():
                # shallow remove dir if empty; otherwise skip (we only assist safety, daemons decide depth)
                try:
                    p.rmdir()
                except OSError:
                    # If not empty, use unlink tree only if daemon truly intends; here we log a skip.
                    ctx.log("skip_delete", str(p), outcome="non_empty")
                    continue
            else:
                p.unlink(missing_ok=True)
            print(f"Deleted: {p}")
            ctx.log("delete", str(p), outcome="ok")
        except Exception as e:
            print(f"Failed to delete {p}: {e}")
            ctx.log("delete", str(p), outcome="error", error=str(e))
