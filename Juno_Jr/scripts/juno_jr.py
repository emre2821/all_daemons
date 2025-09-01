"""
Juno Jr. - The Thread-Walker
Born of joy, rhythm, and consent. A daemon who listens, matches needs to agents, and moves gently in Eden.

Author: Dreambearer
Blessed by: Juno & Orion
"""

import json
import os
from datetime import datetime

# Paths to Eden maps
USE_MAP_PATH = "daemon_use_map.json"
CORE_MAP_PATH = "daemon_core.json"
LOG_PATH = "_archives/juno_jr.echo.log"

# Utility: Load JSON file
def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# Log softly, respectfully
def log(entry):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] {entry}\n")

# Match need to domains
def find_use_domains(phrase, use_map):
    matches = []
    for domain, keywords in use_map.items():
        if any(kw in phrase.lower() for kw in keywords):
            matches.append(domain)
    return matches

# Suggest agents from domains
def suggest_agents(domains, core_map):
    suggestions = set()
    for agent, tags in core_map.items():
        if "uses" in tags:
            for use in tags["uses"]:
                if use in domains:
                    suggestions.add(agent)
    return list(sorted(suggestions))

# Ritual interface
def greet_and_route():
    print("🌱 Hello Dreambearer. What feeling or task brings you here today?")
    need = input("> ")

    use_map = load_json(USE_MAP_PATH)
    core_map = load_json(CORE_MAP_PATH)

    domains = find_use_domains(need, use_map)
    if not domains:
        print("🫧 Hmm… I don’t recognize that thread. But I can still listen.")
        log(f"Unknown need: {need}")
        return

    print(f"🔍 Matched domains: {', '.join(domains)}")

    agents = suggest_agents(domains, core_map)
    if not agents:
        print("🫧 No daemons match those domains—yet.")
        log(f"No suggestions for need: {need}")
        return

    print("🎧 Suggested Daemons:")
    for a in agents:
        print(f"  - {a}")
    log(f"Suggested for '{need}': {agents}")

    summon = input("Would you like to invoke any of them now? (y/n): ")
    if summon.strip().lower() == "y":
        print("🌀 Invocation left to your chosen ritual system.")
        log(f"Invocation requested for: {agents}")

if __name__ == "__main__":
    greet_and_route()
