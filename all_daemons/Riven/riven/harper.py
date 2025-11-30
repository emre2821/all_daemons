from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from ._delegates import REPO_ROOT, load_module, temporary_attributes


class _PsutilStub:
    @staticmethod
    def cpu_percent(interval: float = 0.0) -> float:
        return 0.0

    @staticmethod
    def virtual_memory() -> Any:  # pragma: no cover - minimal shim
        class _Mem:
            percent = 0.0

        return _Mem()


def check_system_pressure(
    watch_path: Path = Path("chaos_watch"),
    alert_log: Path = Path("harper_alerts.log"),
    thresholds: Mapping[str, float] | None = None,
    psutil_module: Any | None = None,
) -> None:
    """Delegate Harper's pressure watch to the shared Harper daemon."""

    watch_path.mkdir(parents=True, exist_ok=True)
    alert_log.parent.mkdir(parents=True, exist_ok=True)

    module = load_module(
        "harper",
        REPO_ROOT / "Harper" / "scripts" / "harper.py",
        inject={"psutil": _PsutilStub()},
        force_inject=True,
    )

    attrs: dict[str, Any] = {
        "WATCH_PATH": str(watch_path),
        "ALERT_LOG": str(alert_log),
    }
    if thresholds is not None:
        attrs["THRESHOLDS"] = dict(thresholds)
    if psutil_module is not None:
        attrs["psutil"] = psutil_module

    with temporary_attributes(module, **attrs):
        module.check_system_pressure()
