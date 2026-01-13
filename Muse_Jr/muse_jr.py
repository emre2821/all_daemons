import json
from datetime import datetime

class MuseJr:
    def __init__(self):

        self.log_file = "musejr_log.json"
        self.ideas = []

    def save_idea(self, idea):

        entry = {
            "timestamp": str(datetime.now()),
            "idea": idea
        }
        self.ideas.append(entry)
        self._log_idea(entry)

    def _log_idea(self, entry):

        try:
            with open(self.log_file, 'a') as f:
                json.dump(entry, f)
                f.write('\n')
        except Exception:
            pass

    def list_ideas(self):

        if not self.ideas:
            return "Muse Jr. holds no sparks yet. Share an idea."
        report = ["Muse Jr.’s Sparks:"]
        for e in self.ideas:
            report.append(f"[{e['timestamp']}] {e['idea']}")
        return "\n".join(report)

    def main(self):

        print("✨ Muse Jr. dreams. Share ideas (type 'list' to see, 'exit' to quit):")
        while True:
            idea = input("> ").strip()
            if idea.lower() == 'exit':
                print("Muse Jr. drifts to sleep.")
                break
            if idea.lower() == 'list':
                print(self.list_ideas())
                continue
            if idea:
                self.save_idea(idea)
                print("Idea sparked and saved.")

if __name__ == "__main__":
    musejr = MuseJr()
    musejr.main()