import json
from datetime import datetime

class Toto:
    def __init__(self):

        self.log_file = "toto_log.json"
        self.milestones = []

    def add_milestone(self, event):

        entry = {
            "timestamp": str(datetime.now()),
            "event": event
        }
        self.milestones.append(entry)
        self._log_milestone(entry)

    def _log_milestone(self, entry):

        try:
            with open(self.log_file, 'a') as f:
                json.dump(entry, f)
                f.write('\n')
        except Exception:
            pass

    def list_milestones(self):

        if not self.milestones:
            return "Toto guards no cairns yet. Mark a moment."
        report = ["Toto’s Cairns:"]
        for m in self.milestones:
            report.append(f"[{m['timestamp']}] {m['event']}")
        return "\n".join(report)

    def main(self):

        print("🐾 Toto waits. Mark milestones (type 'list' to see, 'exit' to quit):")
        while True:
            event = input("> ").strip()
            if event.lower() == 'exit':
                print("Toto curls up by the cairn.")
                break
            if event.lower() == 'list':
                print(self.list_milestones())
                continue
            if event:
                self.add_milestone(event)
                print("Milestone marked.")

if __name__ == "__main__":
    toto = Toto()
    toto.main()