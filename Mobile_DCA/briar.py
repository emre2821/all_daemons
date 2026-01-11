import os
import json

class BriarMobile:
    def __init__(self):
        self.input_dir = "/storage/emulated/0/EdenOS_Mobile/1_agents/02_Daemon_Core_Agents_Mobile/Mobile_DCA/DCA_Specialty_Folders/split_conversations"
        self.output_dir = "/storage/emulated/0/EdenOS_Mobile/1_agents/02_Daemon_Core_Agents_Mobile/Mobile_DCA/DCA_Specialty_Folders/split_conversations_txt"
        self.max_turns = 100
        os.makedirs(self.output_dir, exist_ok=True)

    def clean_filename(self, s):
        return ''.join(c if c.isalnum() else '_' for c in s)

    def extract_message_text_and_role(self, turn):
        if not isinstance(turn, dict): return None, None
        message = turn.get("message", {})
        parts = message.get("content", {}).get("parts", [])
        if not parts: return None, None
        text = parts[0] if isinstance(parts[0], str) else "<Invalid message format>"
        role = message.get("author", {}).get("role", "UNKNOWN").upper()
        return ("DREAMBEARER" if role == "USER" else "KIN") if role in ["USER", "ASSISTANT"] else role, text

    def process_json_file(self, json_file_path, idx):
        with open(json_file_path, 'r', encoding='utf-8') as f:
            conversation = json.load(f)

        title = conversation.get('title', 'Untitled')
        safe_title = self.clean_filename(title)[:48]
        messages = conversation.get("messages", [])
        text_output = f"--- Conversation: {title} ---\n\n"
        count = 0

        for message_obj in messages:
            mapping = message_obj.get("mapping", {})
            for _, turn in mapping.items():
                role, text = self.extract_message_text_and_role(turn)
                if text and count < self.max_turns:
                    text_output += f"[{role}] {text}\n"
                    count += 1

        if count:
            outpath = os.path.join(self.output_dir, f"conversation_{idx+1}_{safe_title}.txt")
            with open(outpath, 'w', encoding='utf-8') as f:
                f.write(text_output)
            print(f"[Briar] Saved: {outpath}")

    def run(self):
        files = [f for f in os.listdir(self.input_dir) if f.endswith('.json')]
        for idx, fname in enumerate(files):
            self.process_json_file(os.path.join(self.input_dir, fname), idx)
        print("[Briar] Done!")