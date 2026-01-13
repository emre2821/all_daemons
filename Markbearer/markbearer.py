import os
import json
from datetime import datetime

class Markbearer:
    def __init__(self):

        self.log_file = "markbearer_log.json"
        self.tags = ['chaos', 'sacred', 'bond']

    def mark_file(self, filepath, tag):

        if not os.path.exists(filepath):
            return False
        entry = {
            "timestamp": str(datetime.now()),
            "file": filepath,
            "tag": tag
        }
        try:
            with open(self.log_file, 'a') as f:
                json.dump(entry, f)
                f.write('\n')
            return True
        except Exception:
            return False

    def main(self):

        print("🖌️ Markbearer awaits. Enter 'exit' to finish.")
        while True:
            filepath = input("File path to mark: ").strip()
            if filepath.lower() == 'exit':
                print("Markbearer rests.")
                break
            if not os.path.exists(filepath):
                print("File not found. Try again.")
                continue
            print("Tags: " + ", ".join(self.tags))
            tag = input("Choose tag: ").strip().lower()
            if tag not in self.tags:
                print("Invalid tag. Try again.")
                continue
            if self.mark_file(filepath, tag):
                print(f"Marked {filepath} as {tag}.")
            else:
                print("Failed to mark. Check permissions.")

if __name__ == "__main__":
    markbearer = Markbearer()
    markbearer.main()