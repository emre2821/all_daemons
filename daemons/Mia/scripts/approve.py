#!/usr/bin/env python3
import os
import sys
from pathlib import Path

EDEN_ROOT = Path(os.environ.get("EDEN_ROOT", Path.cwd()))
DRAFT_DIR = EDEN_ROOT / "private" / "RealityKeeper_DRAFT"
ACTIVE_DIR = EDEN_ROOT / "active_tasks" / "RealityKeeper"

def approve(date_tag):

    src = DRAFT_DIR / date_tag / "plan.md"
    if not src.exists():
        print("No draft found for", date_tag)
        return
    ACTIVE_DIR.mkdir(parents=True, exist_ok=True)
    dest = ACTIVE_DIR / f"plan_{date_tag}.md"
    src.replace(dest)
    print("[Approved] →", dest)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python approve.py YYYYMMDD")
    else:
        approve(sys.argv[1])
