import re
import json
from datetime import datetime

class Rook:
    def __init__(self):
        self.log_file = "rook_log.json"
        self.dangerous = r'\brm\s+-rf\b|\bdel\b|\bformat\b|\bexec\b'

    def check_command(self, command):
        if re.search(self.dangerous, command, re.IGNORECASE):
            self._log_command(command, "blocked")
            return False
        self._log_command(command, "allowed")
        return True

    def _log_command(self, command, status):
        entry = {
            "timestamp": str(datetime.now()),
            "command": command[:50],
            "status": status
        }
        try:
            with open(self.log_file, 'a') as f:
                json.dump(entry, f)
                f.write('\n')
        except Exception:
            pass

    def main(self):
        print("🛡️ Rook stands guard. Enter commands (type 'exit' to quit):")
        while True:
            cmd = input("> ").strip()
            if cmd.lower() == 'exit':
                print("Rook lowers the gate.")
                break
            if self.check_command(cmd):
                print("Command allowed.")
            else:
                print("Command blocked: unsafe.")

if __name__ == "__main__":
    rook = Rook()
    rook.main()