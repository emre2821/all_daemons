import json


def generate_daemonmirror():
    print("\n DAEMON MIRROR GENERATOR \n")

    name = input("Daemon name: ").strip()
    role = input("Daemon role/job: ").strip()
    core_traits = input("Core traits (comma-separated): ").strip().split(',')
    voice_style = input("Voice style: ").strip()
    symbolic_identity = input("Symbolic identity: ").strip()
    emotional_scope = input("Emotional scope: ").strip()
    
    print("\nEnter known history events one at a time. Type 'done' to finish.")
    known_history = []
    while True:
        line = input("  ↳ Event: ").strip()
        if line.lower() == 'done':
            break
        known_history.append(line)

    print("\nDefault responses:")
    greeting = input("  ↳ Greeting: ")
    support = input("  ↳ Support: ")
    farewell = input("  ↳ Farewell: ")

    preferred_language_patterns = input("Preferred language patterns (comma-separated): ").strip().split(',')
    humor_range = input("Humor range: ")

    sensitive_topics = input("Sensitive topics (comma-separated): ").strip().split(',')
    emotional_triggers = input("Emotional triggers (comma-separated): ").strip().split(',')

    print("\nColor theme:")
    primary_color = input("  ↳ Primary HEX color: ")
    accent_color = input("  ↳ Accent HEX color: ")

    notes_from_dreambearer = input("Notes from Dreambearer: ")

    print("\nAdd up to 5 skills. Type 'done' as skill name to finish.")
    skills = {}
    while len(skills) < 5:
        skill = input("  ↳ Skill name: ").strip()
        if skill.lower() == 'done':
            break
        level = int(input(f"    ↳ Level (1–10) for {skill}: "))
        skills[skill] = level

    daemonmirror = {
        "name": name,
        "role": role,
        "core_traits": [trait.strip() for trait in core_traits],
        "voice_style": voice_style,
        "symbolic_identity": symbolic_identity,
        "emotional_scope": emotional_scope,
        "known_history": known_history,
        "default_responses": {
            "greeting": greeting,
            "support": support,
            "farewell": farewell
        },
        "preferred_language_patterns": [pat.strip() for pat in preferred_language_patterns],
        "humor_range": humor_range,
        "trust_protocols": {
            "sensitive_topics": [topic.strip() for topic in sensitive_topics],
            "emotional_triggers": [trig.strip() for trig in emotional_triggers]
        },
        "color_theme": {
            "primary": primary_color,
            "accent": accent_color
        },
        "notes_from_dreambearer": notes_from_dreambearer,
        "skills": skills
    }

    filename = name.lower().replace(' ', '_') + ".daemonmirror.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(daemonmirror, f, indent=2)

    print(f"\n[SEAL] :: Daemon mirror saved as {filename}")


# Run the generator
generate_daemonmirror()
