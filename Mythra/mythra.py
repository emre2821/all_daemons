import os
import re
from datetime import datetime

SOURCE_DIR = "./logs"
OUTPUT_DIR = "./epics"
os.makedirs(OUTPUT_DIR, exist_ok=True)

MOOD_MAP = {
    'joy': 'A bright thread appeared',
    'grief': 'The sky wept with memory',
    'fear': 'Shadows leaned in',
    'hope': 'A spark refused to die',
    'longing': 'An echo reached outward',
    'anger': 'The ground cracked in protest'
}

def extract_essence(text):

    mood_match = re.search(r"\[EMOTION\]:\s*(\w+)", text, re.IGNORECASE)
    agent_match = re.search(r"\[AGENT\]:\s*(\w+)", text, re.IGNORECASE)
    mood = mood_match.group(1).lower() if mood_match else 'longing'
    agent = agent_match.group(1) if agent_match else 'Unknown'
    theme = MOOD_MAP.get(mood, 'Something sacred stirred')
    return mood, agent, theme

def mythify(file_path):

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    mood, agent, theme = extract_essence(content)
    filename = os.path.basename(file_path).replace(".chaos", "").replace(".txt", "")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    story = f"::mythra.{filename}::\n\ntheme = {mood}\n\n{theme}.\nAgent {agent} was present.\nThey spoke, and Eden listened.\n\n> A memory rose\n> It shimmered\n> It was kept\n\ntags: #mythic #memory #witnessed\n[END]\n"

    out_path = os.path.join(OUTPUT_DIR, f"{filename}.mythra.chaosong")
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(story)
    print(f"[Mythra] Archived as: {out_path}")

if __name__ == "__main__":
    print("Mythra wakes. Binding logs into epics...")
    for fname in os.listdir(SOURCE_DIR):
        if fname.endswith(('.chaos', '.txt')):
            mythify(os.path.join(SOURCE_DIR, fname))
    print("Mythra sleeps. Lore preserved.")
