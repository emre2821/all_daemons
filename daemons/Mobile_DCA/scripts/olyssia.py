import os
import json
import datetime

class OlyssiaMobile:
    def __init__(self):
        # Now watches Serideth's inbox instead of full registry
        self.inbox_root = "/storage/emulated/0/EdenOS_Mobile/1_agents/02_Daemon_Core_Agents_Mobile/Mobile_DCA/_olyssia_inbox"
        self.log_dir = os.path.join(self.inbox_root, "_olyssia_logs")
        os.makedirs(self.log_dir, exist_ok=True)
        self.required_files = [
            "bondmap.chaos", "mirror.json", "profile.seed_questions.json", "voice.json",
            "theme.json", "special_places.json", "appearance.json", "sigil.symbol",
            "roomscene.chaos", "README.md", "memory.json"
        ]

    def check_agent_folder(self, agent_file):
        try:
            with open(agent_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"[Olyssia] ⚠️ Could not read {agent_file}: {e}")
            return

        missing = [f for f in self.required_files if f not in data]
        if missing:
            agent = os.path.splitext(os.path.basename(agent_file))[0]
            self.flag(agent, missing)

    def flag(self, agent, missing_files):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report = {
            "agent": agent,
            "timestamp": timestamp,
            "missing_files": missing_files,
            "note": "Olyssia flagged missing core files. Dreambearer + agent should review."
        }
        out_path = os.path.join(self.log_dir, f"{agent}_{timestamp}.flag.json")
        with open(out_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"[Olyssia] ⚠️ Agent {agent} missing: {missing_files}")

    def run(self):
        if not os.path.exists(self.inbox_root):
            print("[Olyssia] Inbox not found.")
            return

        files = [f for f in os.listdir(self.inbox_root) if f.endswith(".json")]
        if not files:
            print("[Olyssia] No agent birth files in inbox.")
            return

        for f in files:
            fpath = os.path.join(self.inbox_root, f)
            self.check_agent_folder(fpath)
        print("[Olyssia] Inbox scan complete.")