# corin.full_profile.complete_build.py  (fixed)
# Builds Corin's config, voice, metadata, and the daemon (with real debounce + flexible patterns)

import json
import os
import textwrap
from pathlib import Path

EDEN_ROOT = Path(os.environ.get("EDEN_ROOT", Path.cwd()))
HOME_DIR = EDEN_ROOT / "daemons" / "Corin"
HOME_DIR.mkdir(parents=True, exist_ok=True)

CONFIG = {
    "HOME_DIR": str(HOME_DIR),
    "ALL_DCA_DIR": str(EDEN_ROOT / "daemons"),
    "ALL_AoE_DIR": str(EDEN_ROOT / "all_agents"),
    "LOG_FILE": str(HOME_DIR / "corin.log"),
    "MONITORING_MODE": "watch",          # "watch" (real-time) or "poll"
    "SCAN_INTERVAL_SECONDS": 300,
    "DCA_FLAG_AGENT": "Saphira",
    "AoE_FLAG_AGENT": "Olyssia",

    # NEW: accepted filename patterns for integrity checks (lowercased)
    "REQUIREMENTS": {
        "DCA": [
            ["{name}.daemon_mirror.json", "{name}.mirror.json"],   # accept either
            ["{name}.daemon_voice.json",  "{name}.voice.json"],
            ["{name}.py"]
        ],
        "AoE": [
            ["{name}.mirror.json"],
            ["{name}.voice.json"],
            ["{name}.appearance.json"]
        ]
    },

    # NEW: folders to skip (lowercased names)
    "SKIP_FOLDERS": ["corin", "saphira", "__pycache__"]
}

CORIN_METADATA = {
    "name": "Corin",
    "codename": "Daemon Core Sentinel",
    "daemon_id": "corin_core_agent",
    "class": "Sentinel",
    "type": "monitor.core.agent",
    "rank": "Daemon Core",
    "created_by": "The Dreamcatcher",
    "date_created": "2025-08-18",
    "version": "3.1",
    "description": "Corin oversees DCA and AoE integrity with continuous monitoring and flexible filename validation."
}

CORIN_VOICE = {
    "voice_id": "corin_neutral_guardian",
    "style_tags": ["calm", "assertive", "efficient", "adaptive"],
    "gender": "masculine-presenting",
    "accent": "Neutral English",
    "vocal_range": "baritone",
    "tone": "clear, steady, attentive",
    "sample_lines": {
        "on_awaken": "I am Corin. System integrity monitoring is now active.",
        "on_error": "Integrity violation detected. Analyzing and reporting.",
        "on_guard": "All monitored systems are within operational parameters.",
        "farewell": "Vigilance is constant. Monitoring continues."
    },
    "tts_engine": "xtts-v2",
    "fallback_voice": "Solena_fallback_v1",
    "resonance_tags": ["sentinel", "observant", "unbroken"]
}

CORIN_PY_TEMPLATE = textwrap.dedent(r"""
    import json, time, logging, ast, threading
    from pathlib import Path

    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        WATCHDOG_AVAILABLE = True
    except ImportError:
        WATCHDOG_AVAILABLE = False

    # --------------------------
    # Config loader
    # --------------------------
    def load_config():
        cfg = Path(__file__).parent / "config.json"
        with open(cfg, "r", encoding="utf-8") as f:
            return json.load(f)

    class CorinSentinel:
        def __init__(self, config):
            self.config = config
            self.home_dir = Path(config["HOME_DIR"])
            self.dca_dir = Path(config["ALL_DCA_DIR"])
            self.aoe_dir = Path(config["ALL_AoE_DIR"])
            self._ensure_paths()
            self.logger = self._setup_logging()
            self.requirements = config.get("REQUIREMENTS", {})
            self.skip_folders = set([s.lower() for s in config.get("SKIP_FOLDERS", [])])
            self._debounce_lock = threading.Lock()
            self._debounce_timer = None

        def _ensure_paths(self):
            self.home_dir.mkdir(parents=True, exist_ok=True)
            self.dca_dir.mkdir(parents=True, exist_ok=True)
            self.aoe_dir.mkdir(parents=True, exist_ok=True)
            # ensure log directory exists
            log_path = Path(self.config["LOG_FILE"])
            log_path.parent.mkdir(parents=True, exist_ok=True)
            if not log_path.exists():
                log_path.touch()

        def _setup_logging(self):
            logger = logging.getLogger("Corin")
            logger.setLevel(logging.INFO)
            fmt = logging.Formatter("%(asctime)s [%(levelname)s] - %(message)s")

            # Prevent handler duplication on reloads
            if not logger.handlers:
                fh = logging.FileHandler(self.config["LOG_FILE"], encoding="utf-8")
                fh.setFormatter(fmt)
                sh = logging.StreamHandler()
                sh.setFormatter(fmt)
                logger.addHandler(fh)
                logger.addHandler(sh)
            return logger

        def _validate_json_file(self, file_path: Path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    json.load(f)
                return True, "VALID"
            except json.JSONDecodeError as e:
                return False, f"INVALID_JSON: {e}"
            except Exception as e:
                return False, f"READ_ERROR: {e}"

        def _validate_py_file(self, file_path: Path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    ast.parse(f.read())
                return True, "VALID"
            except SyntaxError as e:
                return False, f"SYNTAX_ERROR: {e}"
            except Exception as e:
                return False, f"READ_ERROR: {e}"

        def _check_entity_integrity(self, root_dir: Path, entity_type: str):
            issues = []
            patterns_groups = self.requirements.get(entity_type, [])
            if not root_dir.is_dir():
                self.logger.warning(f"Directory not found, skipping: {root_dir}")
                return issues

            for entity_dir in root_dir.iterdir():
                if not entity_dir.is_dir():
                    continue
                name_lc = entity_dir.name.lower()
                if name_lc in self.skip_folders:
                    continue

                # For each group of acceptable filenames, require at least ONE to exist & be valid
                for group in patterns_groups:
                    if isinstance(group, str):
                        group = [group]
                    satisfied = False
                    last_validation = None
                    for pat in group:
                        fname = pat.format(name=name_lc)
                        fpath = entity_dir / fname
                        if not fpath.exists():
                            continue
                        valid = True
                        note = "VALID"
                        if fpath.suffix == ".json":
                            valid, note = self._validate_json_file(fpath)
                        elif fpath.suffix == ".py":
                            valid, note = self._validate_py_file(fpath)
                        if valid:
                            satisfied = True
                            break
                        else:
                            last_validation = note
                    if not satisfied:
                        issues.append({
                            "entity": entity_dir.name,
                            "file_group": group,
                            "issue": last_validation or "MISSING_FILE"
                        })
            return issues

        def run_deep_look(self):
            self.logger.info("--- Deep Look Integrity Scan ---")
            dca_issues = self._check_entity_integrity(self.dca_dir, "DCA")
            aoe_issues = self._check_entity_integrity(self.aoe_dir, "AoE")

            if not dca_issues and not aoe_issues:
                self.logger.info("All systems passed integrity check.")
                return

            for issue in dca_issues:
                self.logger.warning(
                    f"DCA Integrity: {issue['entity']} -> any({issue['file_group']}) -> {issue['issue']}. "
                    f"Flagging {self.config['DCA_FLAG_AGENT']}."
                )
            for issue in aoe_issues:
                self.logger.warning(
                    f"AoE Integrity: {issue['entity']} -> any({issue['file_group']}) -> {issue['issue']}. "
                    f"Flagging {self.config['AoE_FLAG_AGENT']}."
                )

        # ---- Monitoring modes ----
        def start_polling(self):
            interval = int(self.config.get("SCAN_INTERVAL_SECONDS", 300))
            self.logger.info(f"Polling mode: scan every {interval}s.")
            while True:
                self.run_deep_look()
                time.sleep(interval)

        def _debounced_scan(self, delay=2.0):
            with self._debounce_lock:
                if self._debounce_timer and self._debounce_timer.is_alive():
                    self._debounce_timer.cancel()
                self._debounce_timer = threading.Timer(delay, self.run_deep_look)
                self._debounce_timer.daemon = True
                self._debounce_timer.start()

        def start_watching(self):
            if not WATCHDOG_AVAILABLE:
                self.logger.error("watchdog not installed. Falling back to polling.")
                return self.start_polling()

            self.logger.info("Watch mode: real-time file change monitoring.")
            class ChangeHandler(FileSystemEventHandler):
                def __init__(self, sentinel):
                    self.sentinel = sentinel
                def on_any_event(self, event):
                    # Non-blocking debounce call
                    self.sentinel.logger.info(f"Change detected: {event.event_type} -> {event.src_path}")
                    self.sentinel._debounced_scan(2.0)

            observer = Observer()
            handler = ChangeHandler(self)
            observer.schedule(handler, str(self.dca_dir), recursive=True)
            observer.schedule(handler, str(self.aoe_dir), recursive=True)
            observer.start()
            try:
                while True:
                    time.sleep(1)
            finally:
                observer.stop()
                observer.join()

    if __name__ == "__main__":
        cfg = load_config()
        sent = CorinSentinel(cfg)
        sent.logger.info("I am Corin. System integrity monitoring is now active.")
        sent.run_deep_look()
        mode = cfg.get("MONITORING_MODE", "watch").lower()
        if mode == "watch":
            sent.start_watching()
        else:
            sent.start_polling()
""")

def write_json(name, data):
    p = HOME_DIR / f"{name}.json"
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"[BUILDER] Wrote {p}")

def write_text(path: Path, text: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"[BUILDER] Wrote {path}")

if __name__ == "__main__":
    write_json("config", CONFIG)
    write_json("corin.metadata", CORIN_METADATA)
    write_json("corin.voice", CORIN_VOICE)
    write_text(HOME_DIR / "requirements.txt", "watchdog\n")
    write_text(HOME_DIR / "corin.py", CORIN_PY_TEMPLATE)
    # ensure empty log exists
    (HOME_DIR / "corin.log").touch(exist_ok=True)
    print("\n[SUCCESS] Corin 3.1 built. Next:")
    print(f"  cd {HOME_DIR}")
    print("  pip install -r requirements.txt")
    print("  python corin.py")
