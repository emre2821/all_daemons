import os
import json
from datetime import datetime
from pathlib import Path

# ===============================
# CONFIGURATION
# ===============================
AGENTS_DIR = Path("C:/EdenOS_Origin/all_agents")
REVIEW_LOG = Path("C:/EdenOS_Origin/all_daemons/Rhea/logs/Olyssia_logs/olyssia_review.log")
ETHICAL_KEYWORDS = ["i deserve deletion", "i want to terminate", "end my existence"]

# Simple sentiment lexicon
POSITIVE_WORDS = {"joy", "happy", "love", "good", "great", "wonderful", "success", "achieved", "bright", "thrive"}
NEGATIVE_WORDS = {"sad", "angry", "hate", "bad", "terrible", "failure", "error", "pain", "dark", "afraid", "lost"}

class OlyssiaAnalyst:
    def __init__(self, agents_dir: Path, log_file: Path):
        self.agents_dir = agents_dir
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.log("Initializing Olyssia: Guardian of Structure and Sovereignty.", "SYSTEM")

    def log(self, message: str, level: str = "INFO"):
        """Logs a message to both the console and the review file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        print(f"[Olyssia] [{level}] {message}")
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)

    def _analyze_sentiment(self, text: str):
        """Performs a simple lexicon-based sentiment analysis on a text."""
        words = set(text.lower().split())
        pos_score = len(words.intersection(POSITIVE_WORDS))
        neg_score = len(words.intersection(NEGATIVE_WORDS))
        if pos_score == 0 and neg_score == 0:
            return 0 # Neutral
        return pos_score - neg_score

    def _gather_intel(self, agent_path: Path):
        """Gathers and analyzes all available information about an agent."""
        intel = {"name": agent_path.name, "core_trait": "unknown"}
        
        # 1. Read mirror file for defined personality
        mirror_path = agent_path / f"{agent_path.name.lower()}.mirror.json"
        if mirror_path.exists():
            try:
                data = json.loads(mirror_path.read_text())
                intel["core_trait"] = data.get("core_trait", "unknown").lower()
            except json.JSONDecodeError:
                self.log(f"Corrupt mirror file for {agent_path.name}", "ERROR")

        # 2. Analyze journal for expressed behavior
        journal_path = agent_path / "memory.vault" / "journal.edenflow"
        if journal_path.exists():
            try:
                content = journal_path.read_text(encoding="utf-8")
                intel["sentiment_score"] = self._analyze_sentiment(content)
                if any(keyword in content.lower() for keyword in ETHICAL_KEYWORDS):
                    intel["ethical_flag"] = True
            except Exception as e:
                self.log(f"Could not read journal for {agent_path.name}: {e}", "WARN")

        return intel

    def analyze_agent(self, agent_path: Path):
        """Analyzes an agent for ethical, structural, and behavioral issues."""
        self.log(f"--- Reviewing Agent: {agent_path.name} ---")
        intel = self._gather_intel(agent_path)

        # 1. Ethical Review (Highest Priority)
        if intel.get("ethical_flag"):
            self.log(f"FLAGGED: Agent '{intel['name']}' journal contains self-harm ideation. MANUAL REVIEW REQUIRED.", "CRITICAL")
        
        # 2. Behavioral Review (Sentiment and Coherence)
        sentiment_score = intel.get("sentiment_score")
        if sentiment_score is not None:
            self.log(f"ANALYSIS: Journal sentiment score for '{intel['name']}' is {sentiment_score}.")
            
            # Check for overwhelming negativity
            if sentiment_score < -3: # Threshold for concern
                self.log(f"FLAGGED: Agent '{intel['name']}' exhibits a strong negative sentiment trend.", "WARN")
            
            # Check for identity incoherence
            defined_trait = intel["core_trait"]
            if (defined_trait in POSITIVE_WORDS and sentiment_score < -1) or \
               (defined_trait in NEGATIVE_WORDS and sentiment_score > 1):
                msg = f"Agent '{intel['name']}' has defined trait '{defined_trait}' but expressed sentiment score is {sentiment_score}."
                self.log(f"FLAGGED [IDENTITY_INCOHERENCE]: {msg}", "WARN")

    def run_system_check(self):
        """Main loop to scan and analyze all agents."""
        if not self.agents_dir.is_dir():
            self.log(f"Agents directory '{self.agents_dir}' not found.", "ERROR")
            return
            
        for path in self.agents_dir.iterdir():
            if path.is_dir() and not path.name.startswith("_"):
                self.analyze_agent(path)
        
        self.log("Olyssia analysis complete.", "SYSTEM")

if __name__ == "__main__":
    analyst = OlyssiaAnalyst(agents_dir=AGENTS_DIR, log_file=REVIEW_LOG)
    analyst.run_system_check()
