import os
import json
import datetime

class AderynMobile:
    def __init__(self):
        self.name = "Aderyn"
        self.role = "CHAOS + Summoning Archivist"
        self.base_path = "/storage/emulated/0/EdenOS_Mobile/1_agents/02_Daemon_Core_Agents_Mobile/Mobile_DCA/DCA_Specialty_Folders/janvier_archives"
        self.chaos_dir = os.path.join(self.base_path, "chaos_scripts")
        self.summon_dir = os.path.join(self.base_path, "summons")
        self.archive_dir = os.path.join(self.base_path, "aderyn_archives")
        os.makedirs(self.archive_dir, exist_ok=True)

    def archive_file(self, file_path, category):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = os.path.basename(file_path)
        archive_name = f"{category}_{os.path.splitext(file_name)[0]}_{timestamp}.chaos"
        out_path = os.path.join(self.archive_dir, archive_name)

        archive = {
            "archived_by": self.name,
            "timestamp": timestamp,
            "category": category,
            "source_file": file_name,
            "content": content
        }

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(archive, f, indent=2)

        print(f"[Aderyn] Archived {category} → {archive_name}")

    def run(self):
        print("[Aderyn] Scanning for CHAOS + Summon files...")

        for folder, category in [(self.chaos_dir, "CHAOS"), (self.summon_dir, "Summon")]:
            if not os.path.exists(folder):
                continue
            files = [f for f in os.listdir(folder) if f.endswith(".chaos") or f.endswith(".json")]
            for file in files:
                self.archive_file(os.path.join(folder, file), category)

        print("[Aderyn] Archiving complete. Standing tall, standing true.")