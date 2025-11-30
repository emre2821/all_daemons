from __future__ import annotations

import hashlib
from pathlib import Path
from types import ModuleType

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


def generate_sigil(text: str, sigil_dir: Path = Path("sigils")) -> Path:
    """Forge a sigil by delegating to Glypha's shared forge."""

    sigil_dir.mkdir(parents=True, exist_ok=True)
    filename = f"sigil_{hashlib.sha256(text.encode()).hexdigest()[:8]}.png"
    target = sigil_dir / filename

    module = load_module(
        "glypha",
        REPO_ROOT / "Glypha" / "scripts" / "glypha.py",
        inject={"psutil": _PsutilStub()},
        force_inject=True,
    )

    with temporary_attributes(module, SIGIL_DIR=str(sigil_dir)):
        module.generate_sigil(text)

    return target
