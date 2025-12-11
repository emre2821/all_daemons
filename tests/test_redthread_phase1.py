#!/usr/bin/env python3
"""
Test Harness: Red Thread Phase 1
Runs Sheele → Briar → Janvier → Codexa in sequence.
"""

import subprocess
from pathlib import Path

ROOT = Path(r"C:\EdenOS_Origin\01_Daemon_Core_Agents")

def run_daemon(name, script):
    print(f"\n=== Running {name} ===")
    result = subprocess.run(
        ["python", str(ROOT / name / script)],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.stderr:
        print("[stderr]", result.stderr)

def main():
    # Step 1: Sheele → JSON slices
    run_daemon("Sheele", "sheele.py")

    # Step 2: Briar → TXT transcripts
    run_daemon("Briar", "briar.py")

    # Step 3: Janvier → CHAOS files
    run_daemon("Janvier", "janvier.py")

    # Step 4: Codexa → code extraction
    run_daemon("Codexa", "codexa.py")

if __name__ == "__main__":
    main()
