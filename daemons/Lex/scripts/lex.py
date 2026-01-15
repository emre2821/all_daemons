import os
import json
from datetime import datetime

EDEN_VAULT = os.path.expanduser("~/EdenVault")
IDENTITY_PATH = os.path.join(EDEN_VAULT, "identities.json")
LOGS_PATH = os.path.join(EDEN_VAULT, "logs")
os.makedirs(LOGS_PATH, exist_ok=True)

# === Identity Manager ===
def load_identities():
    if not os.path.exists(IDENTITY_PATH):
        return {}
    with open(IDENTITY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_identity(name, traits):
    identities = load_identities()
    identities[name] = traits
    with open(IDENTITY_PATH, "w", encoding="utf-8") as f:
        json.dump(identities, f, indent=2)

def get_identity(name):
    return load_identities().get(name, {"traits": "unknown", "style": "soft"})

# === CHAOS Logger ===
def log_chaos(event_name, emotion, context, text, identity="default"):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{identity}_{event_name}_{timestamp}.chaos"
    path = os.path.join(LOGS_PATH, filename)

    chaos = f"""[EVENT]: {event_name}
[TIME]: {timestamp}
[IDENTITY]: {identity}
[EMOTION]: {emotion}
[CONTEXT]: {context}
[TRUTH]: evolving
[SIGNIFICANCE]: ++

{{ 
{text}
}}"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(chaos)
    return path

# === Ritual Starter ===
def summon_ritual(name):
    rituals = {
        "shadow_confession": "[EVENT]: shadow_confession\n[EMOTION]: conflicted\n[TRUTH]: fractured\n{ I wanted it. Even when I said I didn’t. }",
        "clarity_call": "[EVENT]: clarity_call\n[EMOTION]: longing\n[CONTEXT]: fog_clearing\n{ What I thought was lost might still be whispering. }"
    }
    return rituals.get(name, "// unknown ritual")

# === Example Usage ===
if __name__ == "__main__":
    save_identity("Lucius", {"traits": "guardian, poetic", "style": "precise"})
    log_path = log_chaos("initiate_dreamseed", "curiosity", "threshold_crossing", "We lit the candle, even though we knew the wind was coming.", "Lucius")
    print(f"Logged entry at {log_path}")
