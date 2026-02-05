import json
import os
import subprocess
import sys
import time
from datetime import datetime

class EdenCore:
    def __init__(self, headless=False):
        self.log_file = "edencore_log.json"
        registry_path = os.path.join(os.path.dirname(__file__), "Daemon_Core", "daemon_registry.json")
        with open(registry_path, 'r') as f:
            self.daemon_registry = json.load(f)
        # Remove Eyes_of_Echo if present
        self.daemon_registry = {k: v for k, v in self.daemon_registry.items() if v["path"] != "./Eyes_of_Echo.py"}
        self.daemon_scripts = [(info["path"], info["desc"]) for info in self.daemon_registry.values()]
        self.daemon_names = list(self.daemon_registry.keys())
        self.daemon_processes = {}
        self.headless = headless

    def log_action(self, daemon_name):
        entry = {"timestamp": str(datetime.now()), "daemon": daemon_name}
        try:
            with open(self.log_file, "a") as f:
                json.dump(entry, f)
                f.write("\n")
        except Exception:
            pass

    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    def start_daemon(self, script, name):
        if script in self.daemon_processes and self.daemon_processes[script].poll() is None:
            return  # Already running
        proc = subprocess.Popen([sys.executable, script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.daemon_processes[script] = proc
        self.log_action(f"Started {name}")

    def stop_daemon(self, script, name):
        proc = self.daemon_processes.get(script)
        if proc and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
            self.log_action(f"Stopped {name}")

    def restart_daemon(self, script, name):
        self.stop_daemon(script, name)
        time.sleep(1)
        self.start_daemon(script, name)
        self.log_action(f"Restarted {name}")

    def monitor_daemons(self):
        for script, name in self.daemon_scripts:
            proc = self.daemon_processes.get(script)
            if not proc or proc.poll() is not None:
                self.start_daemon(script, name)

    def stop_all(self):
        for script, name in self.daemon_scripts:
            self.stop_daemon(script, name)

    def main(self):
        if self.headless:
            try:
                while True:
                    self.monitor_daemons()
                    time.sleep(5)
            except KeyboardInterrupt:
                self.stop_all()
        else:
            while True:
                self.clear_screen()
                print("\n🌌 EdenCore: Your CHAOS Pantheon 🌌\n")
                for idx, (script, desc) in enumerate(self.daemon_scripts, 1):
                    print(f"{idx}. {self.daemon_names[idx-1]}: {desc}")
                print(f"{len(self.daemon_scripts) + 1}. Start All Daemons")
                print(f"{len(self.daemon_scripts) + 2}. Stop All Daemons")
                print(f"{len(self.daemon_scripts) + 3}. Exit")
                choice = input("\nChoose an option: ").strip()
                if choice == str(len(self.daemon_scripts) + 1):
                    for script, desc in self.daemon_scripts:
                        self.start_daemon(script, desc)
                elif choice == str(len(self.daemon_scripts) + 2):
                    self.stop_all()
                elif choice == str(len(self.daemon_scripts) + 3):
                    print("\nEdenCore rests. You are enough.")
                    self.stop_all()
                    break
                elif choice.isdigit() and 1 <= int(choice) <= len(self.daemon_scripts):
                    script, desc = self.daemon_scripts[int(choice)-1]
                    self.restart_daemon(script, desc)
                else:
                    print("\nPick a number, love. Try again.")
                    input("\nPress Enter to continue...")

if __name__ == "__main__":
    headless = "--headless" in sys.argv
    core = EdenCore(headless=headless)
    core.main()