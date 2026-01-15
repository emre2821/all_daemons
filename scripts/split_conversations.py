import json
import os
import re
from datetime import datetime

# Path to your exported ChatGPT data file
INPUT_FILE = "conversations.json"

# Directory to save text files
OUTPUT_DIR = "conversations_text"

def sanitize_filename(name: str) -> str:
    """Removes illegal filename characters and limits length for safe saving."""
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = name.strip()
    return name[:100] if len(name) > 100 else name

def format_date(timestamp) -> str:
    """Converts a UNIX timestamp (float or str) to a human-readable date."""
    try:
        dt = datetime.fromtimestamp(float(timestamp))
        return dt.strftime("%B %d, %Y")  # e.g. "March 15, 2024"
    except Exception:
        return "Unknown Date"

def extract_messages(conv) -> list:
    """
    Extracts and sorts all user/assistant messages chronologically.
    Preserves triple backticks and formatting.
    """
    mapping = conv.get("mapping", {})
    messages = []

    for node in mapping.values():
        msg = node.get("message")
        if not msg:
            continue

        author = msg.get("author", {}).get("role", "")
        if author not in ["user", "assistant"]:
            continue

        content = msg.get("content", {}).get("parts", [])
        text = "\n".join(content).strip()
        timestamp = msg.get("create_time", 0)

        if text:
            messages.append({
                "author": author,
                "text": text,
                "time": timestamp
            })

    # Sort messages by timestamp
    messages.sort(key=lambda m: m["time"])
    return messages

def format_conversation(conv, index):
    """Formats one conversation into a readable plain-text transcript."""
    title = conv.get("title") or f"Chat_{index}"
    title_clean = sanitize_filename(title)
    conv_id = conv.get("id", "unknown_id")
    date_str = format_date(conv.get("create_time"))

    messages = extract_messages(conv)

    # Header section
    header = [
        f"Title: {title}",
        f"Chat started on {date_str}",
        f"Conversation ID: {conv_id}",
        "=" * 60,
        ""
    ]

    # Body section
    body_lines = []
    for msg in messages:
        author = "User" if msg["author"] == "user" else "Assistant"
        body_lines.append(f"{author}: {msg['text']}\n")

    return title_clean, "\n".join(header + body_lines)

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    conversations = data.get("conversations", data)
    count = 0

    for i, conv in enumerate(conversations, start=1):
        title_clean, text = format_conversation(conv, i)
        output_path = os.path.join(OUTPUT_DIR, f"{title_clean}.txt")

        with open(output_path, "w", encoding="utf-8") as out:
            out.write(text)

        count += 1
        print(f"Saved: {output_path}")

    print(f"\n✅ Done! Exported {count} conversations to '{OUTPUT_DIR}'")

if __name__ == "__main__":
    main()