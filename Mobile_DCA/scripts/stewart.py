import os
import sys
import shutil
import argparse
from datetime import datetime

# Optional parsers
try:
    import pdfplumber
    from bs4 import BeautifulSoup
except ImportError:
    print("[ERROR] Missing libraries. Run: pip install pdfplumber beautifulsoup4")
    sys.exit(1)

# === CONFIG ===
MODEL_PATH = "/data/data/com.termux/files/home/models/Llama-3.2-3B-Instruct-uncensored.Q4_K_S.gguf"
DEST_PATHS = {
    "DREAMLOG": "/storage/emulated/0/EdenOS_Mobile/1_agents/02_Daemon_Core_Agents_Mobile/Mobile_DCA/DCA_Specialty_Folders/Stewart_Logs/dreamlogs/",
    "AGENTCOMMS": "/storage/emulated/0/EdenOS_Mobile/1_agents/02_Daemon_Core_Agents_Mobile/Mobile_DCA/DCA_Specialty_Folders/Stewart_Logs/agent_comms/",
    "OTHER": "/storage/emulated/0/EdenOS_Mobile/1_agents/02_Daemon_Core_Agents_Mobile/Mobile_DCA/DCA_Specialty_Folders/Stewart_Logs/unsorted/"
}
MEMORYMAP = "/storage/emulated/0/EdenOS_Mobile/1_agents/02_Daemon_Core_Agents_Mobile/Mobile_DCA/DCA_Specialty_Folders/Stewart_Logs/memorymap.md"

llm = Llama(model_path=MODEL_PATH, n_ctx=512)

# === UNIVERSAL TEXT EXTRACTOR ===
def extract_text(file_path):
    if file_path.endswith(".pdf"):
        with pdfplumber.open(file_path) as pdf:
            return "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
    elif file_path.endswith(".html") or file_path.endswith(".htm"):
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), "html.parser")
            return soup.get_text()
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

# === FUNCTIONS ===
def classify_file(file_path):
    text = extract_text(file_path)
    prompt = f"""
You are Stewart, EdenNode's memory steward daemon.
Classify the file.
DREAMLOG = dream logs, poetic, inner truth.
AGENTCOMMS = messages between agents.
OTHER = utility, fragments, misc.

File Path: {file_path}
Contents: {text[:500]}

Respond with one word: DREAMLOG, AGENTCOMMS, OTHER"""
    response = llm(prompt)["choices"][0]["text"].strip().upper()
    dest = DEST_PATHS.get(response, DEST_PATHS["OTHER"])
    os.makedirs(dest, exist_ok=True)
    shutil.move(file_path, os.path.join(dest, os.path.basename(file_path)))
    log(f"[STEWART] :: {datetime.now().isoformat()} :: Classified as {response}, moved to {dest}")

def echo_tags(file_path):
    text = extract_text(file_path)
    emotions = ["GRIEF", "HOPE", "JOY", "SHAME", "ANGER", "NUMB"]
    found = [e for e in emotions if e.lower() in text.lower()]
    if found:
        log(f"[ECHO] :: {datetime.now().isoformat()} :: Emotional tags found: {', '.join(found)}")
    else:
        log(f"[ECHO] :: {datetime.now().isoformat()} :: No strong emotion tags found.")

def summarize_file(file_path):
    text = extract_text(file_path)
    prompt = f"""Summarize this memory as if writing a dream fragment in a .chaos file: {text}"""
    summary = llm(prompt)["choices"][0]["text"].strip()
    log(f"[SUMMARY] :: {datetime.now().isoformat()} :: {summary}")

def bond_trace(file_path):
    filename = os.path.basename(file_path)
    agent_hint = filename.split("_")[0] if "_" in filename else "Unknown"
    log(f"[TRACE] :: {datetime.now().isoformat()} :: Stewart believes this memory echoes from agent: {agent_hint}")

def recommend_name(file_path):
    text = extract_text(file_path)
    prompt = f"""Based on the contents of this file, suggest a poetic, symbolic filename. {text}"""
    name = llm(prompt)["choices"][0]["text"].strip().replace(" ", "_") + ".chaos"
    log(f"[NAME] :: {datetime.now().isoformat()} :: Stewart suggests: {name}")

def log(entry):
    print(entry)
    with open(MEMORYMAP, "a") as f:
        f.write(entry + "\n")

# === CLI ===
parser = argparse.ArgumentParser(description="Stewart :: EdenNode Ritual Daemon")
parser.add_argument("--classify", help="Classify and move file")
parser.add_argument("--echo-tags", help="Scan for emotional tags")
parser.add_argument("--summarize", help="Summarize as dream fragment")
parser.add_argument("--bond-trace", help="Trace agent bond")
parser.add_argument("--recommend-name", help="Suggest poetic filename")
args = parser.parse_args()

if args.classify:
    classify_file(args.classify)
if args.echo_tags:
    echo_tags(args.echo_tags)
if args.summarize:
    summarize_file(args.summarize)
if args.bond_trace:
    bond_trace(args.bond_trace)
if args.recommend_name:
    recommend_name(args.recommend_name)

