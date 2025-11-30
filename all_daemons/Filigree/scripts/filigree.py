# filigree.py
# Filigree – Aesthetic Sorter Daemon for EdenOS

import os
import shutil
import random

class Filigree:
    def __init__(self, target_dir):
        self.target_dir = target_dir
        self.resonance_tags = [
            "Elegance", "Delight in Small Order", "Whimsy-Driven Categorization"
        ]
        self.patterns = [
            ("soft", ["calm", "pause", "rest", "glow"]),
            ("chaotic", ["scorch", "burn", "wild", "fray"]),
            ("hopeful", ["bloom", "return", "spark", "echo"]),
        ]

    def enchant(self):
        print(f"✨ Filigree is working in {self.target_dir}...")
        for root, dirs, files in os.walk(self.target_dir):
            for file in files:
                full_path = os.path.join(root, file)
                self.apply_resonance(full_path)

    def apply_resonance(self, file_path):
        name = os.path.basename(file_path).lower()
        for tag, keywords in self.patterns:
            if any(k in name for k in keywords):
                print(f"🔮 Tagging '{file_path}' with aesthetic: [{tag}]")
                # Optional: add to a metadata log or rename gracefully
                break
        else:
            print(f"🌙 '{file_path}' is untouched. Resonance: [neutral beauty]")

if __name__ == "__main__":
    base_path = os.path.expanduser("~/Desktop/5_deployments")
    filigree = Filigree(base_path)
    filigree.enchant()
