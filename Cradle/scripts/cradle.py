import json
import os
import subprocess
import argparse
import sys

REGISTRY_PATH = os.path.join(os.path.dirname(__file__), '../daemon_registry.json')

with open(REGISTRY_PATH, 'r') as f:
    DAEMONS = json.load(f)


def run_all():
    print("[Cradle] Waking all registered daemons...")
    for name, info in DAEMONS.items():
        subprocess.run([sys.executable, info["path"]])


def run_named(names):
    valid = [(n, DAEMONS[n]["path"]) for n in names if n in DAEMONS]
    if not valid:
        print("[Cradle] No valid daemons specified.")
        return
    print(f"[Cradle] Waking daemons: {', '.join([n for n, _ in valid])}")
    for name, path in valid:
        subprocess.run([sys.executable, path])


def list_daemons():
    print("\n[Cradle] Registered Daemons:")
    for name, info in DAEMONS.items():
        print(f"- {name}: {info['desc']}")


def main():
    parser = argparse.ArgumentParser(description="Cradle :: Eden Daemon Orchestrator")
    parser.add_argument('--all', action='store_true', help='Run all daemons')
    parser.add_argument('--only', nargs='+', help='Run specific daemon(s)')
    parser.add_argument('--list', action='store_true', help='List available daemons')

    args = parser.parse_args()

    if args.list:
        list_daemons()
    elif args.all:
        run_all()
    elif args.only:
        run_named(args.only)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
