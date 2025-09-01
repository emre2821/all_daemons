# --- utils_config.py ---
from pathlib import Path
import json, shutil

class ConfigError(Exception): pass

def load_json_safe(path: Path) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise ConfigError(f"Missing config: {path}")
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in {path}: {e}")

def resolve_binary(*candidates: str) -> str:
    for c in candidates:
        if c and shutil.which(c):
            return c
    raise ConfigError(f"No working binary found among: {candidates}")

def validate_ovpn_path(p: str) -> Path:
    pp = Path(p).expanduser()
    if not pp.exists():
        raise ConfigError(f".ovpn not found: {pp}")
    if not pp.is_file():
        raise ConfigError(f"Not a file: {pp}")
    return pp
