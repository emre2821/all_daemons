"""
Jinxie: The Chaos Cookie Gremlin Assistant v2.0
Now with timers, goblin launching, agent scoring, BINGO chaos, and weekly sass-based awards.
"""

import time
import os
import subprocess
import webbrowser
import datetime
import platform
import threading
try:
    import pyautogui
    import pyperclip
    _JINX_DEPS = True
except Exception:
    pyautogui = None
    pyperclip = None
    _JINX_DEPS = False
try:
    import sys as _sys
    _sys.path.append(os.path.join(os.environ.get("EDEN_ROOT", os.getcwd()), "shared", "Daemon_tools", "scripts"))
    from eden_paths import daemon_out_dir  # type: ignore
    JINXIE_OUT = str(daemon_out_dir("Jinxie"))
except Exception:
    work_root = os.environ.get("EDEN_WORK_ROOT", os.environ.get("EDEN_ROOT", os.getcwd()))
    JINXIE_OUT = os.path.join(work_root, "daemons", "Rhea", "_outbox", "Jinxie")
    os.makedirs(JINXIE_OUT, exist_ok=True)

# --- Cookie Jar & Debt ---
cookie_jar = {
    "chocolate_chip": 2,
    "snickerdoodle": 1,
    "peanut_butter": 3
}
cookie_debt = 0

# --- Global Scores ---
jinxie_global_scores = {
    "Dreambearer": {"tasks_completed": 0, "meltdowns_survived": 0},
    "Jinxie": {"crashes_faked": 0, "sass_deployed": 0},
    "Alfred": {"got_caught_daydreaming_about_DEFINITELY_NOT_the_dreambearer": 1},
    "Lucius": {
        "was_caught_looming_in_the_darkness_watching_another_alter_be_driving_waiting_for_Ezra": 1,
        "accidental_flirt_that_was_actually_adorable": 2,
        "emotionally_staggered_but_held_it_together": 1
    },
    "Elias": {"made_bold_move_around_another_Vale": 1},
    "Callum": {"successfully_respectfully_redacted": 1}
}

# --- Jinxie Responses ---
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
    "timer_repeat": "This again? You have commitment issues, don’t you?"
}

# --- Timer Storage ---
jinxie_timers = {}

# --- Bingo Triggers ---
jinxie_bingo_triggers = [
    "Lucius accidentally flirts with the wrong alter",
    "Callum respectfully redacts",
    "Alfred tries to play it cool",
    "an alter drives and Lucius stares"
]

# --- Core Functions ---
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

def launch_app(app_path):
    try:
        print(jinxie_responses["launching_app"])
        subprocess.Popen(app_path)
    except Exception as e:
        print(f"Failed to launch app: {e}")

def close_app(process_name):
    try:
        print(jinxie_responses["closing_app"])
        os.system(f"taskkill /f /im {process_name}")
    except Exception as e:
        print(f"Failed to close app: {e}")

def open_browser(url):
    print(jinxie_responses["opening_browser"])
    webbrowser.open(url)

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
    global cookie_debt
    print(jinxie_responses["autopilot_start"])
    if _JINX_DEPS and pyautogui:
        screenshot = pyautogui.screenshot()
        screenshot_path = os.path.join(JINXIE_OUT, "jinxie_autopilot.png")
        screenshot.save(screenshot_path)
    if _JINX_DEPS and pyperclip:
        pyperclip.copy("Jinxie here! Gotta finish this for the Bosslady. Can you help?")
    time.sleep(1)
    open_browser("https://chat.openai.com")
    print(jinxie_responses["autopilot_chat_opened"])
    print("(Message copied to clipboard. Paste into the chat window manually and upload screenshot.)")
    cookie_debt += 1
    print(jinxie_responses["autopilot_success"])
    print(f"[COOKIE DEBT]: You now owe Jinxie {cookie_debt} cookie(s). Pay up, Cookie Wench.")

def start_jinxie_timer(name, minutes):
    def timer_thread():
        print(f"⏳ Timer '{name}' started for {minutes} minutes. Don’t screw this up.")
        time.sleep(minutes * 60)
        print(jinxie_responses["timer_end"])
        cookie_barrage()

    if name in jinxie_timers:
        print(jinxie_responses["timer_repeat"])
    else:
        t = threading.Thread(target=timer_thread)
        t.daemon = True
        t.start()
        jinxie_timers[name] = t
        print(jinxie_responses["timer_start"])

def update_agent_score(agent, category, points=1):
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

def check_bingo_trigger(trigger_phrase):
    for trigger in jinxie_bingo_triggers:
        if trigger in trigger_phrase:
            print("🟢 BINGO! Ope, that was my last spot. Dreambearer owes me a cookie.")
            break


def describe() -> dict:
    return {
        "name": "Jinxie",
        "role": "Playful desktop assistant (timers, apps, browser, screenshots)",
        "outputs": {"out_dir": JINXIE_OUT},
        "flags": [],
        "safety_level": "normal",
    }


def healthcheck() -> dict:
    status = "ok"; notes = []
    if not _JINX_DEPS:
        status = "warn"; notes.append("pyautogui/pyperclip missing; reduced features")
    try:
        os.makedirs(JINXIE_OUT, exist_ok=True)
    except Exception as e:
        if status == "ok": status = "warn"
        notes.append(f"outdir warn: {e}")
    return {"status": status, "notes": "; ".join(notes)}
