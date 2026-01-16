from __future__ import annotations

from importlib import util
from pathlib import Path
import sys

_RHEA_MAIN_PATH = Path(__file__).resolve().parents[1] / "daemons" / "Rhea" / "rhea_main.py"

_spec = util.spec_from_file_location("Rhea.rhea_main", _RHEA_MAIN_PATH)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Unable to load rhea_main module from {_RHEA_MAIN_PATH}")

rhea_main = util.module_from_spec(_spec)
sys.modules[_spec.name] = rhea_main
_spec.loader.exec_module(rhea_main)

__all__ = ["rhea_main"]
