import argparse
import datetime
from pathlib import Path


def validate_ritual_name(name: str) -> str:
    normalized_name = name.strip().lower()

    if not normalized_name:
        raise ValueError("Ritual name cannot be empty.")

    if any(char.isspace() for char in normalized_name):
        raise ValueError("Ritual name cannot contain spaces.")

    return normalized_name


def prompt_for_ritual_name() -> str:
    while True:
        response = input("What do you want to call this ritual? (no spaces): ")
        try:
            return validate_ritual_name(response)
        except ValueError as err:
            print(f"Invalid ritual name: {err} Please try again without spaces.")


def make_ritual(ritual_name: str | None = None, output_path: str | None = None):
    name = (
        validate_ritual_name(ritual_name)
        if ritual_name is not None
        else prompt_for_ritual_name()
    )

    target_directory = Path(output_path or ".")
    target_directory.mkdir(parents=True, exist_ok=True)
    file_path = target_directory / f"{name}.chaos"

    steps = []
    step_num = 1

    print("\nOkay! Let’s build your ritual step-by-step.")

    while True:
        action = (
            input(
                "\nWhat do you want to do? (say, wait, click, move_mouse, write_log, done): "
            )
            .strip()
            .lower()
        )

        if action == "say":
            message = input("What should it say? ")
            steps.append(f"{step_num} = say: {message}")

        elif action == "wait":
            seconds = input("How many seconds should it wait? ")
            steps.append(f"{step_num} = wait: {seconds}")

        elif action == "click":
            steps.append(f"{step_num} = click")

        elif action == "move_mouse":
            x = input("X coordinate? ")
            y = input("Y coordinate? ")
            steps.append(f"{step_num} = move_mouse: {x},{y}")

        elif action == "write_log":
            log_text = input("What should it log? ")
            steps.append(f"{step_num} = write_log: {log_text}")

        elif action == "done":
            break

        else:
            print("I don't recognize that action—but you're doing great! Try again.")
            continue

        step_num += 1

    with file_path.open("w", encoding="utf-8") as f:
        f.write("[ritual]\n")
        f.write(f"name = {name}\n")
        f.write(f"created = {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("\n[sequence]\n")
        for line in steps:
            f.write(line + "\n")

    print(f"\nRitual saved as: {file_path}")
    print(f"You can run it with: python chaosmode.py {file_path}")


def parse_args():
    parser = argparse.ArgumentParser(description="Build a ritual .chaos file.")
    parser.add_argument(
        "-n",
        "--name",
        dest="ritual_name",
        help="Name of the ritual (no spaces).",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output_path",
        default=".",
        help="Directory where the .chaos file will be written.",
    )

    return parser.parse_args()


def main():
    args = parse_args()
    try:
        make_ritual(args.ritual_name, args.output_path)
    except ValueError as err:
        raise SystemExit(f"Invalid ritual name: {err}")


if __name__ == "__main__":
    main()
