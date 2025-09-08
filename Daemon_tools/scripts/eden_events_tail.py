from __future__ import annotations
import argparse
import time
from pathlib import Path

from .eden_paths import events_bus_path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Tail Eden events bus (events.jsonl)")
    ap.add_argument("--follow", action="store_true", help="Follow (tail -f)")
    args = ap.parse_args(argv)

    path = events_bus_path()
    if not path.exists():
        print(f"No events bus found at {path}")
        return 0

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            print(line.rstrip())
        if args.follow:
            while True:
                where = f.tell()
                line = f.readline()
                if not line:
                    time.sleep(0.5)
                    f.seek(where)
                else:
                    print(line.rstrip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

