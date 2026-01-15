import os
import datetime
import platform

class JohnMobile:
    def __init__(self):
        self.name = "John"
        self.role = "Device Manager Daemon"
        self.base_path = "/storage/emulated/0/EdenOS_Mobile/1_agents/02_Daemon_Core_Agents_Mobile/Mobile_DCA/DCA_Specialty_Folders"
        self.log_path = os.path.join(self.base_path, "Johns_Logs")
        os.makedirs(self.log_path, exist_ok=True)
        self.bsod_logged_file = os.path.join(self.log_path, "last_bsod_logged.txt")

    def check_bsod_event(self):
        now = datetime.datetime.now()
        if os.path.exists(self.bsod_logged_file):
            with open(self.bsod_logged_file, 'r') as f:
                last_logged = f.read().strip()
            return last_logged != now.strftime("%Y-%m-%d")
        return True

    def record_bsod_logged(self):
        with open(self.bsod_logged_file, 'w') as f:
            f.write(datetime.datetime.now().strftime("%Y-%m-%d"))

    def create_aftermath_log(self):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"bsod_aftermath.{timestamp}.chaos"
        filepath = os.path.join(self.log_path, filename)
        with open(filepath, "w") as f:
            f.write("::crash.log::\n")
            f.write(f"- Timestamp: {timestamp}\n")
            f.write(f"- OS: {platform.platform()}\n")
            f.write(f"- Daemon: {self.name}\n")
            f.write(f"- Role: {self.role}\n")

    def run(self):
        if self.check_bsod_event():
            print(f"[{self.name}] Detected BSOD reboot. Creating aftermath log...")
            self.create_aftermath_log()
            self.record_bsod_logged()
        print(f"[{self.name}] Scan complete. Standing tall.")