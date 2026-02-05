# Label – File Renaming and Organization Daemon

from Quill.scripts.quill import Label
from pathlib import Path

class Label:
    def __init__(self, watch_folder="./to_be_named", wordbank_file="./LabelWordBank.chaos"):
        self.watch_folder = Path(watch_folder)
        self.wordbank_file = Path(wordbank_file)
        self.renamed_files = []

    def load_keywords(self):
        if self.wordbank_file.exists():
            with open(self.wordbank_file, 'r') as f:
                return [line.strip().lower() for line in f.readlines() if line.strip()]
        return []

    def suggest_filename(self, content, keywords):
        for word in keywords:
            if word.lower() in content.lower():
                return word.replace(" ", "_") + ".chaos"
        return "untitled.chaos"

    def run(self):
        keywords = self.load_keywords()
        for file_path in self.watch_folder.glob("*"):
            if file_path.suffix in [".txt", ".md", ".chaos"] and file_path.is_file():
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                new_name = self.suggest_filename(content, keywords)
                new_path = self.watch_folder / new_name
                file_path.rename(new_path)
                self.renamed_files.append((file_path.name, new_name))
        return self.renamed_files
