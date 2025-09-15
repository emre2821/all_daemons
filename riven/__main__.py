import argparse

from . import (
    check_system_pressure,
    deliver_messages,
    generate_sigil,
    pulse,
    mend_fragments,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Riven CLI")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("check", help="Run Harper's system check")
    sub.add_parser("deliver", help="Run Maribel's courier service")

    forge_parser = sub.add_parser("forge", help="Forge a sigil with Glypha")
    forge_parser.add_argument("text", nargs="?", default="eden")

    pulse_parser = sub.add_parser("pulse", help="Record a mood with Tempo")
    pulse_parser.add_argument("mood", nargs="?", default="calm")

    sub.add_parser("mend", help="Mend fractured logs with Riven")

    args = parser.parse_args()

    if args.command == "check":
        check_system_pressure()
    elif args.command == "deliver":
        deliver_messages()
    elif args.command == "forge":
        generate_sigil(args.text)
    elif args.command == "pulse":
        pulse(args.mood)
    elif args.command == "mend":
        mend_fragments()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
