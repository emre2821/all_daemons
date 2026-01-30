from argparse import ArgumentParser

from .harper import check_system_pressure
from .maribel import deliver_messages
from .glypha import generate_sigil
from .tempo import pulse
from .riven import mend_fragments


def main() -> None:
    parser = ArgumentParser(description="Riven roles")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("check", help="Run Harper's system check")
    sub.add_parser("deliver", help="Run Maribel's courier duties")
    forge = sub.add_parser("forge", help="Forge a sigil with Glypha")
    forge.add_argument("text")
    pulse_parser = sub.add_parser("pulse", help="Log rhythm with Tempo")
    pulse_parser.add_argument("mood")
    sub.add_parser("mend", help="Mend fractured logs with Riven")

    args = parser.parse_args()
    if args.cmd == "check":
        check_system_pressure()
    elif args.cmd == "deliver":
        deliver_messages()
    elif args.cmd == "forge":
        generate_sigil(args.text)
    elif args.cmd == "pulse":
        pulse(args.mood)
    elif args.cmd == "mend":
        mend_fragments()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
