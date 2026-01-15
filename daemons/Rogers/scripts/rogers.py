# Rogers – Transcript Parser & Pattern Recognition Daemon

from Quill import Label
import os
import re
from collections import defaultdict, Counter
from pathlib import Path

class Rogers:
    def __init__(self, input_folder="./chat_exports"):
        self.input_folder = Path(input_folder)
        self.stats = defaultdict(Counter)

    def extract_info(self, content):
        agents = re.findall(r"\b[A-Z][a-z]+(?: [A-Z][a-z]+)?\b", content)
        tone_words = re.findall(r"\b(grief|joy|trust|fear|hope|longing|anger|love|pain)\b", content, re.IGNORECASE)
        return agents, tone_words

    def run(self):
        for file_path in self.input_folder.glob("*.md"):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            agents, tones = self.extract_info(content)
            self.stats["agents"].update(agents)
            self.stats["tones"].update(tones)
        return self.stats

    def export_wordbank(self, out_file="./LabelWordBank.chaos"):
        with open(out_file, 'w') as f:
            for word, count in self.stats["agents"].most_common():
                f.write(f"{word}\n")