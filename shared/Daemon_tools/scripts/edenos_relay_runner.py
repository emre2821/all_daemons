import subprocess
import time

try:
    from .eden_paths import eden_root
except Exception:
    from eden_paths import eden_root  # type: ignore

ROOT = eden_root()
DAEMONS = ROOT / "daemons"

# Define daemon paths in relay order
DAEMON_ORDER = [
    str(DAEMONS / "Sheele" / "Sheele.py"),
    str(DAEMONS / "Briar" / "Briar.py"),
    str(DAEMONS / "Aderyn" / "aderyn.py"),
    str(DAEMONS / "Janvier" / "janvier.py"),
    str(DAEMONS / "Serideth" / "serideth.py"),
    # Twins run together
    [
        str(DAEMONS / "Olyssia" / "olyssia.py"),
        str(DAEMONS / "Saphira" / "saphira_gui.py"),
    ]
]

def run_daemon(path):
    try:
        print(f"[RELAY] Launching: {path}")
        subprocess.run(["python", path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Daemon failed: {path} — {e}")

def main():
    for item in DAEMON_ORDER:
        if isinstance(item, list):
            for twin in item:
                run_daemon(twin)
        else:
            run_daemon(item)
        time.sleep(1)

if __name__ == "__main__":
    main()
