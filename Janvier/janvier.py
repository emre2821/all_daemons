#!/usr/bin/env python3
"""
Janvier Daemon v3 "Hunk-vier"
Role: Converts Briar's .txt transcripts into CHAOS-formatted archives.
Upgrades:
  - Eden-style canonical titles
  - Rich auto-tagging (participants, domain, emotion, CHAOS markers)
  - Auto summary
  - Conversation metadata (counts, participants, duration estimate)
  - Link extraction
  - Emotion histogram
  - Hash signature
  - CHAOS structural anchors
Input:  C:\EdenOS_Origin\01_Daemon_Core_Agents\Rhea\_outputs\Briar_files\*.txt
Output: C:\EdenOS_Origin\01_Daemon_Core_Agents\Rhea\_outputs\Janvier_files\*.chaos
"""

import os, json, re, hashlib
from pathlib import Path
from datetime import datetime

# === CONFIG ===
ROOT_DIR = Path(r"C:\EdenOS_Origin\01_Daemon_Core_Agents")
INPUT_DIR = ROOT_DIR / r"Rhea\_outputs\Briar_files"
OUTPUT_DIR = ROOT_DIR / r"Rhea\_outputs\Janvier_files"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
# ==============

# -----------------------------
# Helpers
# -----------------------------
def eden_title(lines, fallback):
    """Generate an Eden-style canonical title: MM.DD.YY Speaker_MessageSnippet"""
    today = datetime.now().strftime("%m.%d.%y")
    for line in lines:
        if ":" in line:
            speaker, msg = line.split(":", 1)
            snippet = msg[:25].strip().replace(" ", "_")
            return f"{today}_{speaker.strip()}_{snippet}"
    return f"{today}_{fallback}"

def extract_links(messages):
    """Find all links in messages."""
    urls = []
    for m in messages:
        urls.extend(re.findall(r'https?://\S+', m["text"]))
    return sorted(set(urls))

def tag_messages(messages):
    """Generate tags from participants, content, and heuristics."""
    tags = set()
    for m in messages:
        tags.add(m["speaker"])
        text = m["text"].lower()
        # Domain
        if any(w in text for w in ["evict","lease","rent","landlord"]): tags.add("housing")
        if any(w in text for w in ["dream","summon","ritual","eden"]): tags.add("eden")
        if "```" in text: tags.add("code")
        # Emotions
        if any(w in text for w in ["love","happy","grateful","joy"]): tags.add("positive")
        if any(w in text for w in ["angry","hate","fuck","sad"]): tags.add("negative")
    # Temporal
    tags.add(datetime.now().strftime("%Y-%m-%d"))
    # CHAOS markers
    tags.update(["chaos.doc","eden.archive","auto.generated"])
    return sorted(tags)

def emotion_histogram(messages):
    """Count positive/negative occurrences."""
    pos_words = ["love","happy","grateful","joy"]
    neg_words = ["angry","hate","fuck","sad"]
    pos, neg = 0, 0
    for m in messages:
        text = m["text"].lower()
        if any(w in text for w in pos_words): pos += 1
        if any(w in text for w in neg_words): neg += 1
    return {"positive": pos, "negative": neg}

def generate_summary(messages):
    """Simple one-liner summary."""
    if not messages: return "Empty conversation."
    first = messages[0]
    last = messages[-1]
    return f"{first['speaker']} begins with '{first['text'][:40]}...', ends with {last['speaker']}."

def meta_info(messages):
    """Conversation-level metadata."""
    if not messages: return {}
    participants = sorted(set(m["speaker"] for m in messages))
    return {
        "num_messages": len(messages),
        "unique_participants": len(participants),
        "first_speaker": messages[0]["speaker"],
        "last_speaker": messages[-1]["speaker"],
        "participants": participants,
        "duration_estimate": f"~{len(messages)//2} min"
    }

def hash_doc(doc):
    """Hash signature for doc integrity."""
    return hashlib.sha256(json.dumps(doc, sort_keys=True).encode("utf-8")).hexdigest()

# -----------------------------
# Core Conversion
# -----------------------------
def txt_to_chaos(txt_path: Path, out_path: Path):
    with open(txt_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    # Build doc
    chaos_doc = {
        "chaos_version": "3.0",
        "source_file": str(txt_path),
        "title": eden_title(lines, txt_path.stem),
        "participants": [],
        "messages": [],
        "tags": [],
        "summary": "",
        "meta": {},
        "links": [],
        "emotions": {},
        "markers": ["::begin.chaos.doc::","::end.chaos.doc::"],
        "hash": ""
    }

    # Messages
    for line in lines:
        if ":" in line:
            speaker, message = line.split(":", 1)
            speaker, message = speaker.strip(), message.strip()
            if speaker not in chaos_doc["participants"]:
                chaos_doc["participants"].append(speaker)
            chaos_doc["messages"].append({"speaker": speaker, "text": message})
        else:
            chaos_doc["messages"].append({"speaker": "Unknown", "text": line})

    # Post-process
    chaos_doc["tags"] = tag_messages(chaos_doc["messages"])
    chaos_doc["summary"] = generate_summary(chaos_doc["messages"])
    chaos_doc["meta"] = meta_info(chaos_doc["messages"])
    chaos_doc["links"] = extract_links(chaos_doc["messages"])
    chaos_doc["emotions"] = emotion_histogram(chaos_doc["messages"])
    chaos_doc["hash"] = hash_doc(chaos_doc)

    # Write
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(chaos_doc, f, indent=2, ensure_ascii=False)

# -----------------------------
# Entrypoint
# -----------------------------
def run():
    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"[Janvier] Cannot find input folder {INPUT_DIR}")
    files = list(INPUT_DIR.glob("*.txt"))
    if not files:
        print(f"[Janvier] No input files in {INPUT_DIR}")
        return

    for txt_file in files:
        out_file = OUTPUT_DIR / f"{txt_file.stem}.chaos"
        txt_to_chaos(txt_file, out_file)
        print(f"[Janvier] Converted {txt_file.name} -> {out_file.name}")

if __name__ == "__main__":
    run()
