#!/usr/bin/env python3
import time
import subprocess
from pathlib import Path

WATCH_DIR = Path("C:/EdenOS_Origin/meetings/QuickSit/")
DRAFT_DIR = Path("C:/EdenOS_Origin/private/RealityKeeper_DRAFT/")

# Models
MODELS = {
    "life.primary": "stablelm2:1.6b",   # nuanced "life" planning
    "life.fallback": "gemma:1b",        # fast/light backup
    "code": "codegemma:2b",
    "lightcode": "deepseek-coder:1.3b"
}

def call_ollama(prompt: str, model: str) -> str:

    result = subprocess.run(
        ["ollama", "run", model],
        input=prompt.encode(),
        capture_output=True
    )
    return result.stdout.decode().strip()

def choose_model(text: str) -> str:

    """Route disclosures to primary vs fallback."""
    lowered = text.lower()
    if "urgent" in lowered or "fast" in lowered:
        return MODELS["life.fallback"]
    else:
        return MODELS["life.primary"]

def make_plan(text: str) -> str:

    model = choose_model(text)
    prompt = f"""
    The Dreambearer disclosed: {text}

    Write a 3-item, low-friction action plan: - Item 1: Shelter/safety options - Item 2: Cash options (fast, legal, simple) - Item 3: Harm-reduction/health steps
    Keep it short (2–3 steps each). Draft only, not published.
    """
    return call_ollama(prompt, model)

def watch():

    print("RealityKeeper running...")
    while True:
        for vas in WATCH_DIR.glob("*.vas"):
            text = vas.read_text()
            if "priority.reality" in text.lower():
                date_tag = time.strftime("%Y%m%d")
                draft_path = DRAFT_DIR / date_tag
                draft_path.mkdir(parents=True, exist_ok=True)

                plan = make_plan(text)
                out_file = draft_path / "plan.md"
                with open(out_file, "w", encoding="utf-8") as f:
                    f.write(plan)

                print(f"[Draft created] {out_file}")
                vas.rename(vas.with_suffix(".processed.vas"))
        time.sleep(60)  # check every minute

if __name__ == "__main__":
    watch()
