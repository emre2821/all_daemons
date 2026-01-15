#!/usr/bin/env python3
import subprocess
import time
import sys
import os
from datetime import datetime

# === CONFIG ===
BASE_PATH = "/Internal shared storage/EdenOS_Mobile/1_agents/02_Daemon_Core_Agents_Mobile/Mobile_DCA"

DAEMON_NAMES = [
    "emberly",
    "dove",
    "everett",
    "sylva",
    "stewart",
    "nancy",
    "kinsley",
    "luke",
    "koko",
    "scorchick",
    "glypha",
]

DAEMON_SCRIPTS = [os.path.join(BASE_PATH, name, f"{name}.py") for name in DAEMON_NAMES]

LOG_FILE = os.path.expanduser("~/EdenGate_log.txt")
PYTHON_CMD = sys.executable  # current python interpreter path

def log(message):

    timestamp = datetime.now().isoformat()
    line = f"[EdenGate] {timestamp} :: {message}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def launch_daemon(script):

    log(f"Starting {script}...")
    return subprocess.Popen([PYTHON_CMD, script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def main():

    processes = {}

    # Start all daemons
    for script in DAEMON_SCRIPTS:
        if not os.path.isfile(script):
            log(f"WARNING: {script} not found, skipping.")
            continue
        proc = launch_daemon(script)
        processes[script] = proc

    try:
        while True:
            time.sleep(5)
            for script, proc in list(processes.items()):
                retcode = proc.poll()
                if retcode is not None:  # Process exited
                    log(f"{script} exited with code {retcode}. Restarting...")
                    # Restart
                    processes[script] = launch_daemon(script)
    except KeyboardInterrupt:
        log("Shutdown requested. Terminating daemons...")
        for proc in processes.values():
            proc.terminate()
        log("EdenGate shutting down.")

if __name__ == "__main__":
    main()