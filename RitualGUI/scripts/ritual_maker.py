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


def make_ritual(ritual_name: str | None = None, output_path: str | None = None):
    if ritual_name is not None:
        ritual_name = validate_ritual_name(ritual_name)

    while ritual_name is None:
        response = input("What do you want to call this ritual? (no spaces): ")
        try:
            ritual_name = validate_ritual_name(response)
        except ValueError as err:
            print(f"Invalid ritual name: {err} Please try again without spaces.")

    target_directory = Path(output_path or ".")
    target_directory.mkdir(parents=True, exist_ok=True)

    file_name = target_directory / f"{ritual_name}.chaos"

    steps = []
    step_num = 1

    print("\nOkay! Let’s build your ritual step-by-step.")

    while True:
        action = input("\nWhat do you want to do? (say, wait, click, move_mouse, write_log, done): ").strip().lower()

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

    # Create the file
    with open(file_name, "w") as f:
        f.write("[ritual]\n")
        f.write(f"name = {ritual_name}\n")
        f.write(f"created = {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("\n[sequence]\n")
        for line in steps:
            f.write(line + "\n")

    print(f"\nRitual saved as: {file_name}")
    print("You can run it with: python chaosmode.py", file_name)


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

    args = parser.parse_args()

    if args.ritual_name is not None:
        try:
            args.ritual_name = validate_ritual_name(args.ritual_name)
        except ValueError as err:
            parser.error(str(err))

    return args


if __name__ == "__main__":
    parsed_args = parse_args()
    make_ritual(parsed_args.ritual_name, parsed_args.output_path)
