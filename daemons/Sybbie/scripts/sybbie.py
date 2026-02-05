# Sybbie.py
# Notion sync daemon (Markdown-to-Notion Sync)
# Moved from 03_Low_Priority/Profiles/Sybbie.py on 2025-06-13
# If you update this file, please document changes in Daemon_Core/daemon_core.json

import os
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = "1f742eb27c3d80289339e74abed58b90"
import json
import requests

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def get_database_rows():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    res = requests.post(url, headers=HEADERS)
    res.raise_for_status()
    return res.json()

def md_to_notion_blocks(md_text):
    # Placeholder: convert markdown to Notion blocks
    return [{"object": "block", "type": "paragraph", "paragraph": {"text": [{"type": "text", "text": {"content": md_text}}]}}]

def get_page_id_by_name(name):
    data = get_database_rows()
    for result in data.get("results", []):
        props = result.get("properties", {})
        title = props.get("Name", {}).get("title", [])
        if title and title[0]["plain_text"] == name:
            return result["id"]
    return None

def inject_content(page_id, blocks):
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    res = requests.patch(url, headers=HEADERS, data=json.dumps({"children": blocks}))
    res.raise_for_status()
    return res.json()

def sync_all_md_files(folder="./NotionSync"):
    for filename in os.listdir(folder):
        if filename.endswith(".md"):
            name = os.path.splitext(filename)[0]
            with open(os.path.join(folder, filename), "r", encoding="utf-8") as f:
                md_text = f.read()
            page_id = get_page_id_by_name(name)
            if page_id:
                blocks = md_to_notion_blocks(md_text)
                inject_content(page_id, blocks)
                print(f"✅ Synced: {name}")
            else:
                print(f"❌ Page not found in database for: {name}")

if __name__ == "__main__":
    print("🧶 Sybbie wakes. Lore syncing begins...")
    sync_all_md_files()
    print("📜 Sybbie seals the scrolls. Sync complete.")
