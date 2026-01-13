# hunter.exe.py

import os
import json
import traceback
from datetime import datetime

class HunterDaemon:
    daemon_id = "EDN-DAEMON-HUNTER-001"
    class_name = "Hunter"
    type = "Daemon"
    role = "Bug Hunter"
    quote = "“Every flaw I find is one less danger you face.”"
    description = "Hunter is a diagnostic daemon specialized in real-time codebase scanning, anomaly tracing, and error triangulation across both Eden-native systems and external programs."
    status = "active"
    
    symbolic_traits = {
        "sigil": "🪲",
        "element": "metal",
        "alignment": "neutral"
    }

    trusted_by = ["The Dreambearer"]
    notes = "Can operate autonomously or by manual summon. Capable of deep symbolic pattern detection and ritual-state logging during scans."

    # Primary functions
    primary_functions = [
        "Daemon monitoring",
        "System task assistance",
        "Error response",
        "Self-log management",
        "Bug hunting across multiple systems",
        "Supportive fallback protocol"
    ]

    triggers = [
        "boot_sequence",
        "system_flag('hunter')",
        "manual_summon('hunter')",
        "ritual('AutoEngage')"
    ]

    fallback_daemon = "Callum"
    mirror_link_required = True

    linked_files = [
        "hunter.daemon_mirror.json",
        "hunter.voice.json",
        "hunter.log"
    ]

    def __init__(self, target_paths=None):

        self.target_paths = target_paths or []
        self.error_log = []

    def hunt_bugs(self):

        print(f"[{self.class_name}] Initiating bug scan...")
        for path in self.target_paths:
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith(".py") or file.endswith(".js") or file.endswith(".ts"):
                        full_path = os.path.join(root, file)
                        self.scan_file(full_path)

        self.log_results()

    def scan_file(self, filepath):

        print(f"[{self.class_name}] Scanning: {filepath}")
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                code = f.read()
                bugs = self.detect_potential_issues(code)
                if bugs:
                    self.error_log.append({
                        "file": filepath,
                        "issues": bugs
                    })
        except Exception as e:
            self.error_log.append({
                "file": filepath,
                "error": str(e),
                "traceback": traceback.format_exc()
            })

    def detect_potential_issues(self, code):
        # Symbolic + functional bug detection (simplified)
        issues = []
        if "eval(" in code:
            issues.append("⚠️ Use of eval() detected – potential security risk.")
        if "== None" in code or "!= None" in code:
            issues.append("⚠️ Consider using 'is None' or 'is not None' instead of '== None'.")
        if "try:" in code and "except:" in code and "Exception" not in code:
            issues.append("⚠️ Bare except detected – risky error handling.")
        if "TODO" in code or "FIXME" in code:
            issues.append("🔧 TODO or FIXME found – incomplete or known issue.")
        return issues

    def log_results(self):

        timestamp = datetime.utcnow().isoformat()
        log_data = {
            "timestamp": timestamp,
            "hunter_id": self.daemon_id,
            "total_issues_found": len(self.error_log),
            "results": self.error_log
        }

        with open("hunter.log", "w", encoding="utf-8") as log_file:
            json.dump(log_data, log_file, indent=2)
        
        print(f"[{self.class_name}] Scan complete. Logged {len(self.error_log)} items to hunter.log")

    def fallback(self):

        print(f"[{self.class_name}] No mirror link or scan path found. Engaging fallback daemon: {self.fallback_daemon}.")


# 🔹 Ritual summon example
if __name__ == "__main__":
    # Customize paths here if summoning directly
    paths_to_scan = ["./edenified_agentic_automation", "./standard_agentic_automation"]
    hunter = HunterDaemon(target_paths=paths_to_scan)
    hunter.hunt_bugs()
