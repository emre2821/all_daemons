from __future__ import annotations

from pathlib import Path
from types import ModuleType
from typing import Callable

from ._delegates import REPO_ROOT, load_module, temporary_attributes


class _PsutilStub:
    @staticmethod
    def cpu_percent(interval: float = 0.0) -> float:
        return 0.0

    @staticmethod
    def virtual_memory() -> ModuleType:  # pragma: no cover - minimal shim
        mem = ModuleType("psutil_virtual_memory")
        mem.percent = 0.0  # type: ignore[attr-defined]
        return mem


def _pil_stubs() -> dict[str, ModuleType]:
    def _missing(*_args, **_kwargs):  # pragma: no cover
        raise ModuleNotFoundError("Pillow is required for sigil forging")

    pil_pkg = ModuleType("PIL")
    image_module = ModuleType("PIL.Image")
    image_draw_module = ModuleType("PIL.ImageDraw")
    image_module.new = _missing  # type: ignore[attr-defined]
    image_draw_module.Draw = _missing  # type: ignore[attr-defined]
    pil_pkg.Image = image_module  # type: ignore[attr-defined]
    pil_pkg.ImageDraw = image_draw_module  # type: ignore[attr-defined]
    return {
        "PIL": pil_pkg,
        "PIL.Image": image_module,
        "PIL.ImageDraw": image_draw_module,
    }


def pulse(
    mood: str,
    log_file: Path = Path("tempo_flow.log"),
    sleep_func: Callable[[float], None] | None = None,
) -> None:
    """Log Tempo's rhythm by delegating to the shared Tempo daemon."""

    log_file.parent.mkdir(parents=True, exist_ok=True)
    attrs = {"TEMPO_FILE": str(log_file)}

    inject = {"psutil": _PsutilStub(), **_pil_stubs()}
    module = load_module(
        "tempo",
        REPO_ROOT / "Tempo" / "scripts" / "tempo.py",
        inject=inject,
        force_inject=True,
    )

    if sleep_func is None:
        with temporary_attributes(module, **attrs):
            module.pulse(mood)
        return

    sleep_context = temporary_attributes(module.time, sleep=sleep_func)
    with temporary_attributes(module, **attrs), sleep_context:
        module.pulse(mood)
