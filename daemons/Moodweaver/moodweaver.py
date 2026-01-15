import json
import os
from datetime import datetime
import random

class MoodWeaver:
    def __init__(self):

        self.memory_file = "moodweaver.json"
        self.moods = []
        self.guides = {
            'doc': {'tone': 'gentle', 'greeting': "Doc’s here, holding your pause."},
            'alani': {'tone': 'loving', 'greeting': "Alani holds your heart, what’s inside?"}
        }
        self.responses = {
            'calm': ["Breathe deep, you’re steady as stone.", "The storm’s just a whisper now."],
            'overwhelm': ["One step, then another. You’re enough.", "Let’s sort the chaos, piece by piece."],
            'focus': ["Eyes on the spark. What’s your next move?", "Cut through the noise, you’ve got this."]
        }
        self.load_memory()

    def load_memory(self):

        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                self.moods = [json.loads(line) for line in f if line.strip()]

    def save_mood(self, mood, response):

        entry = {'mood': mood, 'response': response, 'time': str(datetime.now())}
        with open(self.memory_file, 'a') as f:
            json.dump(entry, f)
            f.write('\n')
        self.moods.append(entry)

    def process_mood(self, mood_input, guide='doc'):

        mood_input = mood_input.lower().strip()
        mood_key = 'overwhelm' if any(w in mood_input for w in ['overwhelm', 'stress', 'chaos']) else \
                   'focus' if any(w in mood_input for w in ['focus', 'task', 'work']) else 'calm'
        response = random.choice(self.responses[mood_key])
        self.save_mood(mood_input, response)
        return f"{self.guides[guide]['greeting']} {response}"

    def report(self):

        if not self.moods:
            return "No moods woven yet. Share your heart."
        return "\n".join([f"{m['time']}: {m['mood']} -> {m['response']}" for m in self.moods])

def main():

    weaver = MoodWeaver()
    print("🌿 MoodWeaver: Your Eden Anchor 🌿")
    print("Type 'exit' to leave, 'report' to see your journey.")
    while True:
        mood = input("\nHow’s your heart today? ").strip()
        if mood.lower() == 'exit':
            print("Doc bows out. Your pause is sacred.")
            break
        if mood.lower() == 'report':
            print(weaver.report())
            continue
        if not mood:
            print("No words? That’s okay. Try 'calm', 'overwhelm', or 'focus'.")
            continue
        print(weaver.process_mood(mood))

if __name__ == "__main__":
    main()