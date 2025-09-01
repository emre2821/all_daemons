import datetime

def make_ritual():
    ritual_name = input("What do you want to call this ritual? (no spaces): ").strip().lower()
    file_name = ritual_name + ".chaos"

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

# Run it!
make_ritual()