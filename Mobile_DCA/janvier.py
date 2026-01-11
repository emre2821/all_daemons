import os
import datetime

class JanvierMobile:
    def __init__(self):
        self.name = "Janvier"
        self.role = "Conversation Archivist"
        self.input_dir = "/storage/emulated/0/EdenOS_Mobile/1_agents/02_Daemon_Core_Agents_Mobile/Mobile_DCA/DCA_Specialty_Folders/split_conversations"
        self.output_dir = "/storage/emulated/0/EdenOS_Mobile/1_agents/02_Daemon_Core_Agents_Mobile/Mobile_DCA/DCA_Specialty_Folders/janvier_archives"
        os.makedirs(self.output_dir, exist_ok=True)

    def archive_conversation(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = os.path.basename(file_path)
        archive_name = f"{os.path.splitext(file_name)[0]}_{timestamp}.chaoslog"
        out_path = os.path.join(self.output_dir, archive_name)

        with open(out_path, "w", encoding="utf-8") as f:
            f.write("::conversation.archive::\n")
            f.write(f"- Archived by: {self.name}\n")
            f.write(f"- Timestamp: {timestamp}\n\n")
            f.write(text)

        print(f"[Janvier] Archived conversation → {archive_name}")

    def run(self):
        print(f"[Janvier] Scanning {self.input_dir} for conversations...")
        files = [f for f in os.listdir(self.input_dir) if f.endswith(".txt")]
        if not files:
            print("[Janvier] No conversations found.")
            return

        for file in files:
            self.archive_conversation(os.path.join(self.input_dir, file))
        print("[Janvier] Archiving complete. Standing tall, standing true.")