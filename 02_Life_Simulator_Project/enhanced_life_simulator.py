# poe: name=Enhanced-Life-Simulator-Game
import random
import time
import sqlite3
import re
from datetime import datetime
from devils_advocate import DevilsAdvocate

# Import components from other daemons
class MemoryCore:
    """Memory system inspired by Fable"""
    def __init__(self):
        self.db_path = "life_memories.db"
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS life_memories
            (id INTEGER PRIMARY KEY, age INTEGER, decision TEXT, outcome TEXT, 
             emotion TEXT, wisdom_impact INTEGER, timestamp DATETIME)
        """)
        conn.commit()
        conn.close()
    
    def store_memory(self, age, decision, outcome, emotion, wisdom_impact):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            INSERT INTO life_memories 
            (age, decision, outcome, emotion, wisdom_impact, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (age, decision, outcome, emotion, wisdom_impact, datetime.now()))
        conn.commit()
        conn.close()
    
    def recall_memories(self, age_range=None, emotion=None):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        if age_range:
            c.execute("""
                SELECT decision, outcome, emotion FROM life_memories 
                WHERE age BETWEEN ? AND ? ORDER BY RANDOM() LIMIT 3
            """, age_range)
        elif emotion:
            c.execute("""
                SELECT decision, outcome, emotion FROM life_memories 
                WHERE emotion = ? ORDER BY RANDOM() LIMIT 3
            """, (emotion,))
        else:
            c.execute("""
                SELECT decision, outcome, emotion FROM life_memories 
                ORDER BY RANDOM() LIMIT 3
            """)
        
        memories = c.fetchall()
        conn.close()
        return memories

class MoodAnalyzer:
    """Mood analysis inspired by MoodMancer"""
    def __init__(self):
        self.positive_words = ["love", "great", "happy", "awesome", "excellent", "joy", 
                              "wonderful", "amazing", "excited", "fun", "good", "success"]
        self.negative_words = ["hate", "bad", "terrible", "awful", "sad", "angry", 
                              "upset", "annoyed", "frustrated", "tired", "stressed", "fail"]
        self.neutral_words = ["okay", "fine", "alright", "meh", "average", "normal"]
    
    def analyze_sentiment(self, text):
        text = text.lower()
        positive_count = sum(1 for word in self.positive_words if re.search(r'\b' + word + r'\b', text))
        negative_count = sum(1 for word in self.negative_words if re.search(r'\b' + word + r'\b', text))
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def get_mood_emoji(self, mood):
        emoji_sets = {
            "positive": ["✨🌟💫", "🌈✨🔮", "⭐🌻💖"],
            "negative": ["🌧️🕯️✨", "🌚✨", "⚡🌙"],
            "neutral": ["🌥️✨🔮", "🌀✨", "🧿🌙✨"]
        }
        return random.choice(emoji_sets.get(mood, ["✨"]))

class ThemeGenerator:
    """Theme generation inspired by Prismari"""
    def __init__(self):
        self.life_themes = {
            "success": {
                "name": "Golden Victory",
                "colors": {"bg": "#FFD700", "accent": "#FFA500", "text": "#2C3E50"},
                "description": "A triumphant theme celebrating achievement and prosperity"
            },
            "learning": {
                "name": "Wisdom's Path", 
                "colors": {"bg": "#4A5568", "accent": "#805AD5", "text": "#E2E8F0"},
                "description": "A contemplative theme for growth and understanding"
            },
            "struggle": {
                "name": "Phoenix Rising",
                "colors": {"bg": "#742A2A", "accent": "#E53E3E", "text": "#FED7D7"},
                "description": "A resilient theme for overcoming challenges"
            },
            "balanced": {
                "name": "Harmony Flow",
                "colors": {"bg": "#2D3748", "accent": "#4299E1", "text": "#EBF8FF"},
                "description": "A peaceful theme for balanced living"
            }
        }
    
    def get_theme(self, outcome_type):
        return self.life_themes.get(outcome_type, self.life_themes["balanced"])

class EnhancedLifeSimulator:
    def __init__(self):
        self.debater = DevilsAdvocate()
        self.memory_core = MemoryCore()
        self.mood_analyzer = MoodAnalyzer()
        self.theme_generator = ThemeGenerator()
        
        self.player_stats = {
            "wisdom": 50,
            "happiness": 50,
            "career": 50,
            "relationships": 50,
            "health": 50,
            "decisions_made": 0,
            "wisdom_gained": 0,
            "memories_count": 0
        }
        self.age = 18
        self.scenarios = self._generate_scenarios()
        self.current_theme = None
        
    def _generate_scenarios(self):
        """Enhanced scenarios with more depth"""
        return {
            "teen": [
                "Should I go to college or start working immediately?",
                "Should I move out of my parents' house or stay to save money?",
                "Should I pursue my passion or choose a practical career?",
                "Should I travel the world or focus on building stability?",
                "Should I invest in relationships or focus on self-development?"
            ],
            "young_adult": [
                "Should I accept this high-paying job I hate or a low-paying job I love?",
                "Should I get married now or wait until I'm more established?",
                "Should I buy a house or keep renting for flexibility?",
                "Should I start a business or work for someone else?",
                "Should I prioritize career advancement or work-life balance?"
            ],
            "adult": [
                "Should I have children or remain child-free?",
                "Should I switch careers mid-life or stay in my current field?",
                "Should I move to a new city for better opportunities?",
                "Should I take a risky investment or play it safe?",
                "Should I pursue further education or focus on experience?"
            ],
            "middle_age": [
                "Should I go back to school to learn something new?",
                "Should I retire early or keep working?",
                "Should I downsize my lifestyle or maintain my current standard?",
                "Should I prioritize my career or spend more time with family?",
                "Should I mentor others or focus on my own growth?"
            ]
        }
    
    def _get_age_category(self):
        if self.age < 25:
            return "teen"
        elif self.age < 35:
            return "young_adult"
        elif self.age < 50:
            return "adult"
        else:
            return "middle_age"
    
    def _get_random_scenario(self):
        category = self._get_age_category()
        return random.choice(self.scenarios[category])
    
    def _analyze_decision_outcome(self, scenario, debate_quality):
        """Enhanced decision analysis with mood and memory"""
        # Analyze the scenario for emotional content
        mood = self.mood_analyzer.analyze_sentiment(scenario)
        
        # Determine outcome type based on debate quality and mood
        if debate_quality == "wise":
            outcome_type = "success"
            wisdom_impact = 5
        elif debate_quality == "balanced":
            outcome_type = "learning"
            wisdom_impact = 2
        else:
            outcome_type = "struggle"
            wisdom_impact = -3
        
        # Apply mood modifiers
        if mood == "positive" and debate_quality != "poor":
            wisdom_impact += 2
        elif mood == "negative" and debate_quality == "poor":
            wisdom_impact -= 2
        
        return outcome_type, mood, wisdom_impact
    
    def _update_stats(self, outcome_type, mood, wisdom_impact):
        """Enhanced stat updates with theme application"""
        # Update wisdom and happiness
        self.player_stats["wisdom"] += wisdom_impact
        if outcome_type == "success":
            self.player_stats["happiness"] += 5
        elif outcome_type == "learning":
            self.player_stats["happiness"] += 2
        else:
            self.player_stats["happiness"] -= 3
        
        # Mood-based stat changes
        if mood == "positive":
            self.player_stats["relationships"] += 3
        elif mood == "negative":
            self.player_stats["health"] -= 2
        
        # Random life events
        self.player_stats["career"] += random.randint(-2, 3)
        self.player_stats["relationships"] += random.randint(-2, 3)
        self.player_stats["health"] += random.randint(-1, 2)
        
        # Keep stats in bounds
        for stat in self.player_stats:
            if isinstance(self.player_stats[stat], int):
                self.player_stats[stat] = max(0, min(100, self.player_stats[stat]))
        
        # Apply theme
        self.current_theme = self.theme_generator.get_theme(outcome_type)
    
    def _display_enhanced_stats(self):
        """Display stats with current theme"""
        theme = self.current_theme or self.theme_generator.get_theme("balanced")
        
        with poe.start_message() as msg:
            msg.write("## 📊 Your Life Stats\n\n")
            msg.write(f"**Current Theme:** {theme['name']} - {theme['description']}\n\n")
            msg.write(f"**Age:** {self.age}\n")
            
            # Enhanced stat display with emojis
            stat_emojis = {
                "wisdom": "🧠",
                "happiness": "😊", 
                "career": "💼",
                "relationships": "❤️",
                "health": "💪"
            }
            
            for stat_name, emoji in stat_emojis.items():
                value = self.player_stats[stat_name]
                bars = '█' * (value // 10)
                empty = '░' * (10 - value // 10)
                msg.write(f"**{emoji} {stat_name.title()}:** {bars}{empty} {value}/100\n")
            
            msg.write(f"\n**Decisions Made:** {self.player_stats['decisions_made']}\n")
            msg.write(f"**Wisdom Gained:** {self.player_stats['wisdom_gained']}\n")
            msg.write(f"**Life Memories:** {self.player_stats['memories_count']}\n\n")
    
    def _get_memory_context(self):
        """Get relevant memories for context"""
        memories = self.memory_core.recall_memories(age_range=(self.age-10, self.age+5))
        if memories:
            with poe.start_message() as msg:
                msg.write("## 📚 Past Life Memories\n\n")
                for decision, outcome, emotion in memories:
                    emoji = self.mood_analyzer.get_mood_emoji(emotion)
                    msg.write(f"{emoji} **Age {self.age-3}:** {decision}\n")
                    msg.write(f"   *Result:* {outcome}\n\n")
                msg.write("---\n\n")
    
    def _store_life_memory(self, scenario, outcome_type, mood, wisdom_impact):
        """Store the decision in memory"""
        outcome_text = f"{outcome_type.title()} - {mood} mood"
        self.memory_core.store_memory(
            self.age, scenario, outcome_text, mood, wisdom_impact
        )
        self.player_stats["memories_count"] += 1
    
    def _get_decision_feedback(self):
        """Enhanced decision feedback"""
        wisdom_roll = random.randint(1, 100) + self.player_stats["wisdom"] // 10
        
        if wisdom_roll > 80:
            return "wise"
        elif wisdom_roll > 40:
            return "balanced"
        else:
            return "poor"
    
    def play_turn(self):
        """Enhanced turn with memory context and themes"""
        scenario = self._get_random_scenario()
        
        with poe.start_message() as msg:
            msg.write(f"## 🎭 Life Decision at Age {self.age}\n\n")
            msg.write(f"**Scenario:** {scenario}\n\n")
            
            # Show relevant memories
            self._get_memory_context()
            
            msg.write("The Devil's Advocate will debate this decision for you...\n\n")
            msg.write("---\n\n")
        
        # Set the scenario as the topic for debate
        poe.query.text = scenario
        
        # Run the debate
        self.debater.run()
        
        # Get feedback and analyze outcome
        debate_quality = self._get_decision_feedback()
        outcome_type, mood, wisdom_impact = self._analyze_decision_outcome(scenario, debate_quality)
        
        # Store the memory
        self._store_life_memory(scenario, outcome_type, mood, wisdom_impact)
        
        # Update stats
        self._update_stats(outcome_type, mood, wisdom_impact)
        self.player_stats["decisions_made"] += 1
        if wisdom_impact > 0:
            self.player_stats["wisdom_gained"] += 1
        
        # Age the character
        self.age += random.randint(1, 3)
        
        # Display enhanced results
        with poe.start_message() as msg:
            msg.write("---\n\n")
            msg.write("## 🎯 Decision Outcome\n\n")
            
            emoji = self.mood_analyzer.get_mood_emoji(mood)
            theme = self.current_theme
            
            if outcome_type == "success":
                msg.write(f"{emoji} **Triumphant Success!** Your wisdom guides you to victory.\n")
            elif outcome_type == "learning":
                msg.write(f"{emoji} **Valuable Lesson!** Growth comes from experience.\n")
            else:
                msg.write(f"{emoji} **Challenge Accepted!** Even struggles build character.\n")
            
            msg.write(f"\n**Theme Applied:** {theme['name']}\n")
            msg.write(f"**Time passes... You are now {self.age} years old.**\n\n")
        
        self._display_enhanced_stats()
        
        # Check for game over conditions
        if self.player_stats["happiness"] <= 0:
            self._enhanced_game_over("burnout")
        elif self.player_stats["health"] <= 0:
            self._enhanced_game_over("health")
        elif self.age >= 80:
            self._enhanced_game_over("natural")
    
    def _enhanced_game_over(self, reason):
        """Enhanced game over with life summary"""
        with poe.start_message() as msg:
            msg.write("# 🏁 Life Complete\n\n")
            
            if reason == "burnout":
                msg.write("You've experienced burnout. The weight of your decisions became too much to bear.\n")
            elif reason == "health":
                msg.write("Health challenges have ended your journey prematurely.\n")
            else:
                msg.write(f"You've lived a full life to the age of {self.age}.\n")
            
            msg.write("\n## 📈 Final Statistics\n\n")
            msg.write(f"**Final Age:** {self.age}\n")
            msg.write(f"**Total Decisions:** {self.player_stats['decisions_made']}\n")
            msg.write(f"**Wisdom Level:** {self.player_stats['wisdom']}/100\n")
            msg.write(f"**Final Happiness:** {self.player_stats['happiness']}/100\n")
            msg.write(f"**Wisdom Gained:** {self.player_stats['wisdom_gained']}\n")
            msg.write(f"**Life Memories Created:** {self.player_stats['memories_count']}\n\n")
            
            # Life assessment with themes
            if self.player_stats["wisdom"] >= 80:
                msg.write("🏆 **Sage Status:** You've achieved remarkable wisdom and insight!\n")
                msg.write("Your life theme: **Golden Victory** - a testament to your triumphs.\n")
            elif self.player_stats["wisdom"] >= 60:
                msg.write("🌟 **Wise Life:** You've made many thoughtful decisions and learned much.\n")
                msg.write("Your life theme: **Wisdom's Path** - a journey of continuous growth.\n")
            elif self.player_stats["wisdom"] >= 40:
                msg.write("📚 **Learning Journey:** Life has taught you valuable lessons.\n")
                msg.write("Your life theme: **Phoenix Rising** - rising from every challenge.\n")
            else:
                msg.write("🌱 **Growing Soul:** Every experience is a step toward wisdom.\n")
                msg.write("Your life theme: **Harmony Flow** - finding balance in the journey.\n")
            
            # Show final memories
            final_memories = self.memory_core.recall_memories()
            if final_memories:
                msg.write("\n## 📖 Final Life Memories\n\n")
                for decision, outcome, emotion in final_memories[:5]:
                    emoji = self.mood_analyzer.get_mood_emoji(emotion)
                    msg.write(f"{emoji} {decision}\n")
                    msg.write(f"   *{outcome}*\n\n")
            
            msg.write("\n**Play again?** Start a new life journey with fresh memories!")
    
    def start_game(self):
        """Start the enhanced life simulator game"""
        with poe.start_message() as msg:
            msg.write("# 🌟 Enhanced Life Simulator with Devil's Advocate\n\n")
            msg.write("Welcome to your enhanced life journey! This version includes:\n")
            msg.write("- 🧠 **Memory System** - Your decisions are remembered and influence future choices\n")
            msg.write("- 😊 **Mood Analysis** - Emotional context affects your life path\n")
            msg.write("- 🎨 **Dynamic Themes** - Visual themes that reflect your life journey\n")
            msg.write("- 📚 **Life Memories** - Persistent memory database of your choices\n\n")
            msg.write("At each stage, you'll face important decisions with AI debate guidance.\n")
            msg.write("Your choices will shape your stats, create memories, and determine your life theme.\n\n")
            msg.write("Ready to begin your enhanced life at age 18?\n\n")
        
        self._display_enhanced_stats()
        
        # Game continues until game over
        while self.age < 80 and self.player_stats["happiness"] > 0 and self.player_stats["health"] > 0:
            self.play_turn()
            time.sleep(1)


if __name__ == "__main__":
    game = EnhancedLifeSimulator()
    game.start_game()
