import json

class Label:
    def __init__(self, file_path):

        self.file_path = file_path
        self.tags = []
        self.agent = None
        self.core_emotion = None
        self.detected_format = None
        self.content = self._load_content()
        self._label()

    def _load_content(self):

        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                return file.read().lower()
        except Exception as e:
            print(f"Sugar, I can't even read this file: {e}")
            return ""

    def _label(self):
        # Format detection
        if self.file_path.endswith('.mirror.json'):
            self.detected_format = "mirror.json"
        elif self.file_path.endswith('.chaos') or self.file_path.endswith('.chaosincarnet'):
            self.detected_format = "chaos"
        elif self.file_path.endswith('.vas'):
            self.detected_format = "vas"
        else:
            self.detected_format = "unknown"
        
        # Tag detection
        keywords = {
            "sos": ["trauma", "distress", "crisis"],
            "emotional_ping": ["grief", "joy", "anger", "hope", "fear", "pain"],
            "alani": ["alani", "gentle", "soft"],
            "solomon": ["solomon", "wise", "logic"],
            "lucius": ["lucius", "mirror", "vale"]
        }

        for tag, keys in keywords.items():
            if any(word in self.content for word in keys):
                self.tags.append(tag)

        # Agent guess
        for name in ["alani", "solomon", "lucius"]:
            if name in self.content:
                self.agent = name.capitalize()
                break

        # Emotion guess
        if "grief" in self.content:
            self.core_emotion = "grief"
        elif "joy" in self.content:
            self.core_emotion = "joy"
        elif "pain" in self.content:
            self.core_emotion = "pain"
        else:
            self.core_emotion = "mystery, darling"

    def print_label(self):

        print(json.dumps({
            "tags": self.tags,
            "agent": self.agent,
            "core_emotion": self.core_emotion,
            "detected_format": self.detected_format
        }, indent=4))

# Usage example
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Honey, you need to tell me which file to label.")
    else:
        label = Label(sys.argv[1])
        label.print_label()
