import subprocess
import time

# Define daemon paths in relay order
DAEMON_ORDER = [
    "C:/EdenOS_Origin/all_daemons/Sheele/Sheele.py",
    "C:/EdenOS_Origin/all_daemons/Briar/Briar.py",
    "C:/EdenOS_Origin/all_daemons/Aderyn/aderyn.py",
    "C:/EdenOS_Origin/all_daemons/Janvier/janvier.py",
    "C:/EdenOS_Origin/all_daemons/Serideth/serideth.py",
    # Twins run together
    [
        "C:/EdenOS_Origin/all_daemons/Olyssia/olyssia.py",
        "C:/EdenOS_Origin/all_daemons/Saphira/saphira_gui.py"
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
