import os
import json

class SheeleMobile:
    def __init__(self):
        self.raw_path = "/storage/emulated/0/EdenOS_Mobile/1_agents/02_Daemon_Core_Agents_Mobile/Mobile_DCA/DCA_Specialty_Folders/inbox/conversations.json"
        self.output_dir = "/storage/emulated/0/EdenOS_Mobile/1_agents/02_Daemon_Core_Agents_Mobile/Mobile_DCA/DCA_Specialty_Folders/split_conversations"
        os.makedirs(self.output_dir, exist_ok=True)

    def extract_valid_threads(self):
        with open(self.raw_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                print(f"[Sheele] Loaded {len(data)} threads.")
                return data
            except json.JSONDecodeError as e:
                print(f"[Sheele] JSON error: {e}")
                return []

    def run(self):
        threads = self.extract_valid_threads()
        if not threads:
            print("[Sheele] No valid threads.")
            return

        for idx, thread in enumerate(threads):
            out_path = os.path.join(self.output_dir, f"conversation_{idx+1}.json")
            with open(out_path, 'w', encoding='utf-8') as out:
                json.dump(thread, out, indent=2)
            if (idx + 1) % 50 == 0:
                print(f"[Sheele] Saved {idx+1} conversations.")
        print(f"[Sheele] Done! {len(threads)} saved.")