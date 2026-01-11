import json
import re
import uuid
import os
from datetime import datetime

class CodexaMobile:
    def __init__(self):
        self.base_path = "/storage/emulated/0/EdenOS_Mobile/1_agents/02_Daemon_Core_Agents_Mobile/Mobile_DCA/DCA_Specialty_Folders/inbox"
        self.input_dir = os.path.join(self.base_path, "inbox")
        self.output_dir = os.path.join(self.base_path, "codexa_output")
        self.archive_dir = os.path.join(self.base_path, "codexa_archive")
        self.output_file = os.path.join(self.output_dir, "extracted_code_blocks.json")
        for d in [self.output_dir, self.archive_dir]:
            os.makedirs(d, exist_ok=True)

    def get_latest_input_file(self):
        files = [f for f in os.listdir(self.input_dir) if f.startswith("conversations") and f.endswith(".json")]
        files.sort(key=lambda f: os.path.getmtime(os.path.join(self.input_dir, f)), reverse=True)
        return os.path.join(self.input_dir, files[0]) if files else None

    def extract_code_blocks(self, text):
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        return [{
            'id': str(uuid.uuid4()),
            'daemon': "Codexa_Mobile",
            'language': lang if lang else "plaintext",
            'code': code.strip()
        } for lang, code in matches]

    def process_conversations(self):
        input_file = self.get_latest_input_file()
        if not input_file:
            print("[Codexa] No input file found.")
            return

        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        conversations = data if isinstance(data, list) else data.get('conversations', [])
        code_blocks = []

        for conv in conversations:
            conv_id = conv.get('id', 'unknown')
            for msg in conv.get('messages', []):
                text = msg.get('content', '')
                timestamp = msg.get('created', msg.get('timestamp', 'unknown'))
                for block in self.extract_code_blocks(text):
                    block.update({
                        'conversation_id': conv_id,
                        'message_id': msg.get('id', 'unknown'),
                        'message_timestamp': timestamp
                    })
                    code_blocks.append(block)

        if os.path.exists(self.output_file):
            with open(self.output_file, 'r', encoding='utf-8') as f:
                existing = json.load(f)
            code_blocks = existing + code_blocks

        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(code_blocks, f, indent=2)

        archive_name = f"extracted_code_blocks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        archive_path = os.path.join(self.archive_dir, archive_name)
        with open(archive_path, 'w', encoding='utf-8') as f:
            json.dump(code_blocks, f, indent=2)

        print(f"[Codexa] {len(code_blocks)} blocks extracted.")
        print(f"[Codexa] Snapshot saved to {archive_path}")

    def run(self):
        self.process_conversations()