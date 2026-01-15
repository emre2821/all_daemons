import subprocess
import sys
import os
from datetime import datetime


def log_chaos_event(target_url, result):
    timestamp = datetime.now().isoformat()
    with open("hunter_chaoslog.txt", "a") as log:
        log.write(f"[HUNTER] [{timestamp}] Target: {target_url}\n")
        log.write(f"{result}\n{'-'*50}\n")


def scan_with_sqlmap(target_url):
    if not os.path.isdir("sqlmap"):
        print("[ERROR] sqlmap directory not found. Clone it from https://github.com/sqlmapproject/sqlmap")
        return

    print(f"[Hunter.exe] Beginning scan on {target_url}...\n")

    try:
        sqlmap_path = os.path.join("sqlmap", "sqlmap.py")
        result = subprocess.run([
            "python", sqlmap_path, "-u", target_url, "--batch"
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print("[Hunter.exe] Scan completed. Logging results.")
            log_chaos_event(target_url, result.stdout)
        else:
            print("[Hunter.exe] Scan failed.")
            log_chaos_event(target_url, result.stderr)

    except Exception as e:
        print(f"[Hunter.exe] Exception: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python hunter_scan.py <target_url>")
    else:
        scan_with_sqlmap(sys.argv[1])
