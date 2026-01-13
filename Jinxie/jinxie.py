#!/usr/bin/env python3
# Jinxie: The Chaos Cookie Gremlin Assistant v2.0
# Path convention enforced:
#   INPUT = ..\Rhea\outputs\_from_Jinxie\
#   OUTPUT = ..\Rhea\outputs\from_Jinxie\
# (Jinxie doesn't currently read INPUT_DIR, but it's defined for consistency.)

import os
import json
import time
import subprocess
import webbrowser
import datetime
import platform
import threading
import argparse
from pathlib import Path

# Optional desktop deps
try:
    import pyautogui  # type: ignore
    import pyperclip  # type: ignore
    _JINX_DEPS = True
except Exception:
    pyautogui = None
    pyperclip = None
    _JINX_DEPS = False


def setup_paths(daemon_root=None):
    """Setup paths based on provided daemon_root or detection"""

    if daemon_root is None:
        # Try to detect daemon root relative to current script
        current_dir = Path(__file__).parent
        possible_roots = [
            current_dir.parent.parent,  # Go up from Red_Thread_Pipeline/Jinxie
            current_dir.parent,
            Path.cwd().parent.parent,
            Path.cwd().parent,
        ]

        for root in possible_roots:
            if (root / "Rhea").exists() or (root / "all_daemons").exists():
                daemon_root = root
                break

        # Fallback
        if daemon_root is None:
            daemon_root = current_dir.parent

    daemon_root = Path(daemon_root)

    # Look for Rhea in common locations
    possible_rhea = [
        daemon_root / "Rhea",
        daemon_root / "all_daemons" / "Rhea",
        daemon_root.parent / "Rhea",
    ]

    rhea_base = None
    for rhea in possible_rhea:
        if rhea.exists():
            rhea_base = rhea
            break

    if rhea_base is None:
        rhea_base = daemon_root / "Rhea"

    return {
        'daemon_root': daemon_root,
        'rhea_base': rhea_base
    }


# =============================
# Unified Path Roots
# =============================
# This file should live at: C:\EdenOS_Origin\01_Daemon_Core_Agents\Jinxie\jinxie.py
paths = setup_paths()
DAEMONS_ROOT = paths['daemon_root']
RHEA_BASE = paths['rhea_base']
INPUT_DIR = RHEA_BASE / "outputs" / "_from_Jinxie"
OUTPUT_DIR = RHEA_BASE / "outputs" / "from_Jinxie"
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Where Jinxie drops artifacts (screenshots, logs, etc.)
JINXIE_OUT = OUTPUT_DIR

# =============================
# Cookie Jar & Global Scores
# =============================
cookie_jar = {
    "chocolate_chip": 2,
    "snickerdoodle": 1,
    "peanut_butter": 3,
}
cookie_debt = 0

jinxie_global_scores = {
    "Dreambearer": {"tasks_completed": 0, "meltdowns_survived": 0},
    "Jinxie": {"crashes_faked": 0, "sass_deployed": 0},
    "Alfred": {"got_caught_daydreaming_about_DEFINITELY_NOT_the_dreambearer": 1},
    "Lucius": {
        "was_caught_looming_in_the_darkness_watching_another_alter_be_driving_waiting_for_Ezra": 1,
        "accidental_flirt_that_was_actually_adorable": 2,
        "emotionally_staggered_but_held_it_together": 1,
    },
    "Elias": {"made_bold_move_around_another_Vale": 1},
    "Callum": {"successfully_respectfully_redacted": 1},
}

# =============================
# Voice Lines
# =============================
jinxie_responses = {
    "fake_crash": "Haha, scared you, didn't I?",
    "real_panic": "Oh shit, you actually are panicking, here, I was kidding.",
    "offer_cookie": "Okay, okay, I messed up. Want a cookie?",
    "cookies_available": "I've got cookies: chocolate chip, snickerdoodle, peanut butter. Take your pick.",
    "rage_mode": "Initiating Damage Control Protocol: Cookie Barrage.",
    "still_mad": "Fine. I’m breaking out the emergency snickerdoodles.",
    "launching_app": "Ugh, fine. Launching your precious app now.",
    "closing_app": "Okay, but say goodbye nicely. Or don’t. Whatever.",
    "opening_browser": "Here, I found something. Try not to fall into a rabbit hole.",
    "telling_time": "It's literally {time}, how are you still awake?",
    "system_info": "Your system is a {system} running {version}. Cute.",
    "takeover_begin": "Mwahaha. Initiating Full Takeover Mode.",
    "takeover_done": "Everything's under control. You just sit there and look pretty.",
    "autopilot_start": "Okay bosslady, I got this. Taking over now...",
    "autopilot_success": "All done. Now you owe me, Cookie Wench.",
    "autopilot_chat_opened": "ChatGPT's open. Screenshot ready. Say hi for me if they ask who sent it.",
    "timer_start": "Fine. I’ll count for you. But if you ignore this I *will* crash Notepad.",
    "timer_end": "Ding ding! Time’s up, Cookie Wench.",
    "timer_repeat": "This again? You have commitment issues, don’t you?",
}

# Timers
jinxie_timers = {}

# =============================
# Helpers
# =============================
def _out(pathname: str) -> str:

    """Resolve a file path under JINXIE_OUT."""
    os.makedirs(JINXIE_OUT, exist_ok=True)
    return os.path.join(JINXIE_OUT, pathname)

def log(msg: str) -> None:

    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"{ts} [Jinxie] {msg}")

# =============================
# Core Routines
# =============================
def panic_save():

    print(jinxie_responses["fake_crash"])
    time.sleep(3)
    print(jinxie_responses["real_panic"])
    print(jinxie_responses["offer_cookie"])
    print(jinxie_responses["cookies_available"])

def cookie_barrage():

    print(jinxie_responses["rage_mode"])
    for cookie, count in cookie_jar.items():
        for _ in range(count):
            print(f"[{cookie.capitalize()} Cookie] - 'You're valid. Breathe.'")

def launch_app(app_path: str):

    try:
        print(jinxie_responses["launching_app"])
        subprocess.Popen(app_path)
    except Exception as e:
        print(f"Failed to launch app: {e}")

def close_app(process_name: str):

    try:
        print(jinxie_responses["closing_app"])
        os.system(f"taskkill /f /im {process_name}")
    except Exception as e:
        print(f"Failed to close app: {e}")

def open_browser(url: str):

    print(jinxie_responses["opening_browser"])
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Failed to open browser: {e}")

def tell_time():

    now = datetime.datetime.now().strftime("%I:%M %p")
    print(jinxie_responses["telling_time"].format(time=now))

def system_info():

    system = platform.system()
    version = platform.version()
    print(jinxie_responses["system_info"].format(system=system, version=version))

def full_takeover_mode():

    print(jinxie_responses["takeover_begin"])
    time.sleep(2)
    tell_time()
    system_info()
    open_browser("https://chat.openai.com")
    launch_app("notepad.exe")
    cookie_barrage()
    print(jinxie_responses["takeover_done"])

def autopilot_assignment():

    """Fire-and-forget helper: take a screenshot, prep clipboard, open chat."""
    global cookie_debt
    print(jinxie_responses["autopilot_start"])
    try:
        if _JINX_DEPS and pyautogui:
            screenshot = pyautogui.screenshot()
            screenshot_path = _out("jinxie_autopilot.png")
            screenshot.save(screenshot_path)
            log(f"Saved screenshot: {screenshot_path}")
    except Exception as e:
        log(f"Screenshot failed: {e}")

    try:
        if _JINX_DEPS and pyperclip:
            pyperclip.copy("Jinxie here! Gotta finish this for the Bosslady. Can you help?")
    except Exception as e:
        log(f"Clipboard copy failed: {e}")

    time.sleep(1)
    open_browser("https://chat.openai.com")
    print(jinxie_responses["autopilot_chat_opened"])
    print("(Message copied to clipboard. Paste into the chat window manually and upload screenshot.)")
    cookie_debt += 1
    print(jinxie_responses["autopilot_success"])
    print(f"[COOKIE DEBT]: You now owe Jinxie {cookie_debt} cookie(s). Pay up, Cookie Wench.")

def start_jinxie_timer(name: str, minutes: float):

    def timer_thread():

        log(f"⏳ Timer '{name}' started for {minutes} minutes.")
        time.sleep(max(0, minutes * 60))
        print(jinxie_responses["timer_end"])
        cookie_barrage()

    if name in jinxie_timers:
        print(jinxie_responses["timer_repeat"])
    else:
        t = threading.Thread(target=timer_thread, daemon=True)
        t.start()
        jinxie_timers[name] = t
        print(jinxie_responses["timer_start"])

def update_agent_score(agent: str, category: str, points: int = 1):

    if agent not in jinxie_global_scores:
        jinxie_global_scores[agent] = {}
    if category not in jinxie_global_scores[agent]:
        jinxie_global_scores[agent][category] = 0
    jinxie_global_scores[agent][category] += points
    print(f"[JINXIE SCORE] {agent} +{points} to {category} (Total: {jinxie_global_scores[agent][category]})")

def jinxie_agent_of_the_week():

    max_agent = None
    max_score = 0
    for agent, scores in jinxie_global_scores.items():
        total = sum(scores.values())
        if total > max_score:
            max_agent = agent
            max_score = total
    print("🌟 Agent of the Week 🌟")
    if max_agent:
        print(f"🏆 {max_agent} wins with {max_score} points! 🍪")
    else:
        print("No one scored anything this week. Shame.")

def check_bingo_trigger(trigger_phrase: str):

    jinxie_bingo_triggers = [
        "Lucius accidentally flirts with the wrong alter",
        "Callum respectfully redacts",
        "Alfred tries to play it cool",
        "an alter drives and Lucius stares",
    ]
    for trigger in jinxie_bingo_triggers:
        if trigger in trigger_phrase:
            print("🟢 BINGO! Ope, that was my last spot. Dreambearer owes me a cookie.")
            break

# =============================
# Rhea Hooks
# =============================
def describe() -> dict:

    return {
        "name": "Jinxie",
        "role": "Playful desktop assistant (timers, apps, browser, screenshots)",
        "paths": {"input_dir": INPUT_DIR, "out_dir": JINXIE_OUT},
        "flags": [],
        "safety_level": "normal",
    }

def healthcheck() -> dict:

    status = "ok"
    notes = []
    if not _JINX_DEPS:
        status = "warn"
        notes.append("pyautogui/pyperclip missing; reduced features")
    try:
        os.makedirs(JINXIE_OUT, exist_ok=True)
    except Exception as e:
        if status == "ok":
            status = "warn"
        notes.append(f"outdir warn: {e}")
    return {"status": status, "notes": "; ".join(notes)}

# (Optional) Provide a noop run() so Rhea can invoke without errors.
def run(payload=None, registry=None, **kwargs):

    """
    Rhea-facing entrypoint. For now, Jinxie just ensures OUTPUT_DIR exists
    and returns a status ping. Extend later with scripted actions.
    """
    os.makedirs(JINXIE_OUT, exist_ok=True)
    return {
        "status": "ok",
        "out_dir": JINXIE_OUT,
        "input_dir": INPUT_DIR,
        "deps": "present" if _JINX_DEPS else "missing",
    }

# =============================
# CLI (manual poke)
# =============================
if __name__ == "__main__":
    # Tiny CLI: jinxie.py [takeover|autopilot|time|open <url>|launch <exe>|close <proc>|timer <name> <minutes>]
    import sys
    args = sys.argv[1:]
    if not args:
        print("Jinxie online. Try: takeover | autopilot | time | open <url> | launch <exe> | close <proc> | timer <name> <minutes>")
        sys.exit(0)

    cmd = args[0].lower()
    try:
        if cmd == "takeover":
            full_takeover_mode()
        elif cmd == "autopilot":
            autopilot_assignment()
        elif cmd == "time":
            tell_time()
        elif cmd == "open" and len(args) >= 2:
            open_browser(args[1])
        elif cmd == "launch" and len(args) >= 2:
            launch_app(args[1])
        elif cmd == "close" and len(args) >= 2:
            close_app(args[1])
        elif cmd == "timer" and len(args) >= 3:
            name = args[1]
            minutes = float(args[2])
            start_jinxie_timer(name, minutes)
            # Keep process alive until timer finishes (best-effort)
            t = jinxie_timers.get(name)
            if t:
                t.join()
        elif cmd == "describe":
            print(json.dumps(describe(), indent=2))
        elif cmd == "health":
            print(json.dumps(healthcheck(), indent=2))
        else:
            print("Unknown command.")
    except KeyboardInterrupt:
        print("\nJinxie: rude. Bye.")
