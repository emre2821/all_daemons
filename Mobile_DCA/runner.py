import os
import subprocess

DAEMONS = [
    ("Codexa", "codexa.py"),
    ("Audrey", "audrey.py"),
    ("John", "john.py"),
    ("Briar", "briar.py"),
    ("Sheele", "sheele.py"),
    ("Olyssia", "olyssia.py"),
    ("Saphira", "saphira.py"),
    ("Aderyn", "aderyn.py"),
    ("Janvier", "janvier.py")
]

def display_menu():
    print("\n🌀 EdenOS Mobile Daemon Launcher")
    for i, (name, _) in enumerate(DAEMONS, 1):
        print(f"{i}. {name}")
    print("0. Exit")

def launch_daemon(index):
    name, script = DAEMONS[index]
    if not os.path.exists(script):
        print(f"[Launcher] ❌ Script not found: {script}")
        return
    print(f"[Launcher] Launching {name}...")
    subprocess.Popen(["python3", script])

def main():
    while True:
        display_menu()
        choice = input("Select daemon to launch (0 to exit): ")
        if not choice.isdigit():
            print("Invalid input.")
            continue
        choice = int(choice)
        if choice == 0:
            print("Exiting.")
            break
        elif 1 <= choice <= len(DAEMONS):
            launch_daemon(choice - 1)
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()