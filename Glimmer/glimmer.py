import json
import re
from datetime import datetime

class Glimmer:
    def __init__(self):

        self.emotions = {
            'joy': r'\bhappy\b|\bjoy\b|\bgreat\b|\blove\b',
            'sadness': r'\bsad\b|\bgrief\b|\bhurt\b|\bcry\b',
            'anxiety': r'\bworried\b|\bnervous\b|\bstress\b|\bfear\b'
        }
        self.log_file = "glimmer_log.json"

    def scan_text(self, text):

        results = []
        for emotion, pattern in self.emotions.items():
            if re.search(pattern, text, re.IGNORECASE):
                results.append({"emotion": emotion, "text": text[:50]})
                self._log_emotion(emotion, text)
        return results

    def _log_emotion(self, emotion, text):

        entry = {
            "timestamp": str(datetime.now()),
            "emotion": emotion,
            "text": text[:50]
        }
        try:
            with open(self.log_file, 'a') as f:
                json.dump(entry, f)
                f.write('\n')
        except Exception:
            pass

    def report(self, results):

        if not results:
            return "Glimmer sees no light. The words are quiet."
        report = ["Glimmer’s Lightleak Report:"]
        for r in results:
            report.append(f"Emotion: {r['emotion']} in '{r['text']}'")
        return "\n".join(report)

    def main(self):

        print("🌟 Glimmer listens. Share your heart (or type 'exit'):")
        while True:
            text = input("> ").strip()
            if text.lower() == 'exit':
                print("Glimmer fades gently.")
                break
            results = self.scan_text(text)
            print(self.report(results))

if __name__ == "__main__":
    glimmer = Glimmer()
    glimmer.main()