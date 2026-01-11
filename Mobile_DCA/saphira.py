import os
import json
import datetime

class SaphiraMobile:
    def __init__(self):
        # Now watches Serideth's inbox instead of full DCA root
        self.inbox_root = "/storage/emulated/0/EdenOS_Mobile/1_agents/02_Daemon_Core_Agents_Mobile/Mobile_DCA/_saphira_inbox"
        self.log_dir = os.path.join(self.inbox_root, "_saphira_logs")
        os.makedirs(self.log_dir, exist_ok=True)

    def check_dca(self, dca_file):
        try:
            with open(dca_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"[Saphira] ⚠️ Could not read {dca_file}: {e}")
            return

        if "daemon_profile.json" not in data and "daemon_profile" not in data:
            self.flag(dca_file, "Missing canonical daemon_profile.json")

    def flag(self, dca_file, reason):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report = {
            "dca_file": dca_file,
            "timestamp": timestamp,
            "reason": reason
        }
        out_path = os.path.join(self.log_dir, f"{os.path.basename(dca_file)}_{timestamp}.flag.json")
        with open(out_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"[Saphira] ⚠️ DCA {dca_file} flagged: {reason}")

    def run(self):
        if not os.path.exists(self.inbox_root):
            print("[Saphira] Inbox not found.")
            return

        files = [f for f in os.listdir(self.inbox_root) if f.endswith(".json")]
        if not files:
            print("[Saphira] No DCA birth files in inbox.")
            return

        for f in files:
            fpath = os.path.join(self.inbox_root, f)
            self.check_dca(fpath)
        print("[Saphira] Inbox scan complete. Standing tall, standing true.")