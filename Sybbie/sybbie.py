#!/usr/bin/env python3
"""
Sybbie.py — EchoStore Order View Daemon
Reborn from Notion sync into local-first archivist.

Role:
- Re-index the EchoStore vault (Markdown files).
- Extract metadata, backlinks, and titles.
- Save a JSON index to packages/core/order_index.json.
"""

import re
import json
import argparse
from pathlib import Path
from datetime import datetime

class Sybbie:
    def __init__(self, vault_path: Path, core_path: Path):

        self.vault_path = vault_path
        self.core_index = core_path / "order_index.json"
        self.index = {
            "notes": [],
            "links": [],
            "metadata": {},
            "updated": datetime.utcnow().isoformat()
        }

    def run(self):

        print("🧶 Sybbie wakes. Re-indexing the vault...")
        self.scan_vault()
        self.save_index()
        print("📜 Sybbie seals the scrolls. Order restored.")

    def scan_vault(self):

        for file in self.vault_path.glob("*.md"):
            with file.open("r", encoding="utf-8") as f:
                content = f.read()

            note_id = file.stem
            title = self.extract_title(content, note_id)
            backlinks = self.extract_backlinks(content)
            metadata = self.extract_metadata(content)

            self.index["notes"].append({
                "id": note_id,
                "title": title,
                "path": str(file),
                "content": content
            })

            for link in backlinks:
                self.index["links"].append({
                    "from": note_id,
                    "to": link
                })

            if metadata:
                self.index["metadata"][note_id] = metadata

    def extract_title(self, content: str, fallback: str) -> str:
        # Use first Markdown heading as title
        match = re.search(r"^# (.+)", content, re.MULTILINE)
        return match.group(1).strip() if match else fallback

    def extract_backlinks(self, content: str):
        # Match [[NoteName]] style backlinks
        return re.findall(r"\[\[(.*?)\]\]", content)

    def extract_metadata(self, content: str):
        # Match inline metadata like "archetype=Hero"
        meta = {}
        matches = re.findall(r"(\w+)=([\w-]+)", content)
        for key, value in matches:
            meta[key] = value
        return meta

    def save_index(self):

        self.core_index.parent.mkdir(parents=True, exist_ok=True)
        with open(self.core_index, "w", encoding="utf-8") as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sybbie — Order View Daemon")
    parser.add_argument("--path", type=str, help="Path to echo-vault repo")
    args = parser.parse_args()

    if not args.path:
        args.path = input("Enter path to echo-vault repo: ").strip()

    repo_path = Path(args.path).resolve()
    vault_path = repo_path / "vault"
    core_path = repo_path / "packages" / "core"

    if not vault_path.exists():
        raise FileNotFoundError(f"Vault not found: {vault_path}")

    Sybbie(vault_path, core_path).run()
