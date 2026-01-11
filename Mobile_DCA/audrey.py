import os
import time
import json

class AudreyMobile:
    def __init__(self):
        self.name = "Audrey"
        self.role = "Crash Analyst DCA"
        self.base_path = "/storage/emulated/0/EdenOS_Mobile/1_agents/02_Daemon_Core_Agents_Mobile/Mobile_DCA/DCA_Specialty_Folders"
        self.input_dir = os.path.join(self.base_path, "Johns_Logs")
        self.output_dir = os.path.join(self.base_path, "Audrey_Reports")
        os.makedirs(self.output_dir, exist_ok=True)

    def analyze_latest(self):
        logs = [f for f in os.listdir(self.input_dir) if f.startswith("bsod_aftermath.") and f.endswith(".chaos")]
        if not logs:
            return None
        latest = max(logs, key=lambda f: os.path.getctime(os.path.join(self.input_dir, f)))
        with open(os.path.join(self.input_dir, latest), "r") as f:
            data = f.read()

        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        report = {
            "analyst": self.name,
            "timestamp": timestamp,
            "findings": [
                {"type": "crashlog", "file": latest, "detail": "System rebooted unexpectedly (BSOD)"}
            ],
            "notes": "Automated crash analysis"
        }

        out_path = os.path.join(self.output_dir, f"analysis_{timestamp}.json")
        with open(out_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"[{self.name}] Wrote analysis to {out_path}")

    def run(self, interval=30):
        print(f"[{self.name}] Watching for new BSOD logs...")
        while True:
            self.analyze_latest()
            time.sleep(interval)