# --- terminate.py ---
import os, signal, subprocess, platform

def terminate_pid(pid: int):
    if platform.system() == "Windows":
        subprocess.call(["taskkill", "/PID", str(pid), "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            return
