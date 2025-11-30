
import subprocess
import time

print("[DaemonCore] Launching Ledger Jr and Handle + Archive...")

# Launch Ledger Jr first
subprocess.Popen(["python", "ledger_jr/ledger_jr.py"])
time.sleep(1)

# Launch Handle
subprocess.Popen(["python", "handle_daemon.py"])
time.sleep(1.5)

# Launch Archive
subprocess.Popen(["python", "archive_daemon.py"])
time.sleep(1.5)

# Launch GUI
subprocess.Popen(["python", "gui/daemon_gui_launcher.py"])

print("[DaemonCore] All daemons and GUI are now active.")
