import time
import os
import json
from datetime import datetime

class PulsePause:
    def __init__(self):
        self.log_file = "pulse_log.json"
        self.exercises = [
            {"name": "Breathe Deep", "pattern": [4, 4, 6], "desc": "Inhale 4s, hold 4s, exhale 6s"},
            {"name": "Finger Tap", "pattern": [1, 1, 1], "desc": "Tap each finger to thumb, 1s per tap"},
            {"name": "Color Scan", "pattern": [5], "desc": "Name 5 colors you see, 5s each"}
        ]

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log_session(self, exercise_name, duration):
        entry = {
            "timestamp": str(datetime.now()),
            "exercise": exercise_name,
            "duration_seconds": duration
        }
        try:
            with open(self.log_file, 'a') as f:
                json.dump(entry, f)
                f.write('\n')
        except Exception:
            pass  # Silent fail to keep it lightweight

    def run_exercise(self, exercise):
        self.clear_screen()
        print(f"\n🌿 {exercise['name']}: {exercise['desc']}\n")
        input("Press Enter when you're ready to start...")
        start_time = time.time()
        while True:
            for duration in exercise['pattern']:
                for _ in range(duration):
                    print(".", end="", flush=True)
                    time.sleep(1)
                print(" ", end="", flush=True)
            print("\nKeep going or press Ctrl+C to stop.")
            try:
                time.sleep(0.5)
            except KeyboardInterrupt:
                duration = int(time.time() - start_time)
                self.log_session(exercise['name'], duration)
                print(f"\nPaused. You grounded for {duration}s. You're enough.")
                input("\nPress Enter to return...")
                break

    def main_menu(self):
        while True:
            self.clear_screen()
            print("\n🌑 PulsePause: Your Grounding Anchor 🌑\n")
            for i, ex in enumerate(self.exercises, 1):
                print(f"{i}. {ex['name']} - {ex['desc']}")
            print(f"{len(self.exercises) + 1}. Exit")
            choice = input("\nChoose an exercise (1-4): ").strip()
            try:
                choice = int(choice)
                if 1 <= choice <= len(self.exercises):
                    self.run_exercise(self.exercises[choice - 1])
                elif choice == len(self.exercises) + 1:
                    print("\nRest well, warrior.")
                    break
                else:
                    print("\nPick a number between 1 and 4.")
                    time.sleep(1)
            except ValueError:
                print("\nJust a number, love. Try again.")
                time.sleep(1)

if __name__ == "__main__":
    app = PulsePause()
    app.main_menu()