#!/usr/bin/env python3
"""
Enhanced Life Simulator - Standalone Version
A complete life simulation game with AI debates, memory system, and mood analysis.
No POE dependencies - runs entirely standalone.
"""

import random
import time
import sqlite3
import re
import os
from datetime import datetime


class SimpleDebater:
    """Simple debate system without POE dependency"""
    def __init__(self):
        self.pro_arguments = [
            "This choice offers stability and security for your future.",
            "Taking this path shows wisdom and careful planning.",
            "This decision aligns with long-term success and fulfillment.",
            "Choosing this option demonstrates maturity and foresight.",
            "This path provides a solid foundation for growth."
        ]
        
        self.con_arguments = [
            "This choice might limit your potential for growth and adventure.",
            "Taking this path could lead to missed opportunities and regret.",
            "This decision may prioritize safety over personal fulfillment.",
            "Choosing this option might prevent you from discovering your true passions.",
            "This path could become too predictable and boring."
        ]
        
        self.rebuttals_pro = [
            "While valid concerns, the benefits outweigh the risks in the long run.",
            "That perspective has merit, but consider the stability this provides.",
            "I understand that viewpoint, but this choice offers more security.",
            "Those are valid points, yet this path ensures steady progress.",
            "While I see that concern, this decision minimizes potential failures."
        ]
        
        self.rebuttals_con = [
            "Security is important, but what about living a truly fulfilling life?",
            "Stability is valuable, but at what cost to your personal growth?",
            "Planning is wise, but life's greatest lessons come from taking risks.",
            "Foresight is good, but don't let fear prevent you from amazing experiences.",
            "A solid foundation is great, but don't forget to actually build something meaningful on it."
        ]
    
    def debate_topic(self, topic):
        """Generate a complete debate on the given topic"""
        debate_output = []
        
        # Opening arguments
        pro_arg = random.choice(self.pro_arguments)
        con_arg = random.choice(self.con_arguments)
        
        debate_output.append("## 🎯 Round 1: Opening Arguments\n\n")
        debate_output.append(f"**🟢 FOR:**\n{pro_arg}\n\n")
        debate_output.append(f"**🔴 AGAINST:**\n{con_arg}\n\n")
        debate_output.append("---\n\n")
        
        # Rebuttals
        pro_rebuttal = random.choice(self.rebuttals_pro)
        con_rebuttal = random.choice(self.rebuttals_con)
        
        debate_output.append("## ⚡ Round 2: Rebuttals\n\n")
        debate_output.append(f"**🟢 FOR responds:**\n{pro_rebuttal}\n\n")
        debate_output.append(f"**🔴 AGAINST responds:**\n{con_rebuttal}\n\n")
        debate_output.append("---\n\n")
        
        # Neutral analysis
        debate_output.append("## 🤝 Neutral Analysis\n\n")
        analysis = self._generate_analysis(topic, pro_arg, con_arg, pro_rebuttal, con_rebuttal)
        debate_output.append(analysis)
        
        return "\n".join(debate_output)
    
    def _generate_analysis(self, topic, pro_arg, con_arg, pro_rebuttal, con_rebuttal):
        """Generate a balanced analysis of the debate"""
        analyses = [
            "This debate highlights the classic tension between security and adventure. The 'for' side emphasizes stability and long-term planning, while the 'against' side prioritizes growth and life experience. Both perspectives have merit - the ideal choice depends on your current life stage and personal values.\n\n**Key considerations:**\n1. What does your intuition tell you about this decision?\n2. Which argument resonates more with your life goals?\n3. Are you seeking security or growth at this moment?",
            
            "The discussion reveals important trade-offs between comfort and challenge. The conservative approach offers predictability, while the adventurous path promises richer life experiences. Your decision should reflect what you need most at this point in your journey.\n\n**Questions to consider:**\n1. Will you regret not taking this opportunity?\n2. Does this choice align with your core values?\n3. What story do you want to tell about this decision later?",
            
            "This debate centers on the balance between practical wisdom and lived experience. Both sides present compelling cases - one for thoughtful planning, the other for embracing life's uncertainties. The right path depends on your personal definition of a fulfilling life.\n\n**Reflection points:**\n1. Which choice feels more authentic to you?\n2. How does each option align with your long-term vision?\n3. What would your future self advise you to do?"
        ]
        
        return random.choice(analyses)


class MemoryCore:
    """Memory system for storing life decisions"""
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
    """Mood analysis system"""
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
    """Theme generation for different life outcomes"""
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


class StandaloneLifeSimulator:
    def __init__(self):
        self.debater = SimpleDebater()
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
        """Generate life scenarios for different age ranges"""
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
        """Analyze decision outcome with mood and wisdom impact"""
        mood = self.mood_analyzer.analyze_sentiment(scenario)
        
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
        """Update player stats based on decision outcome"""
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
        for stat_name in self.player_stats:
            if isinstance(self.player_stats[stat_name], int):
                self.player_stats[stat_name] = max(0, min(100, self.player_stats[stat_name]))
        
        # Apply theme
        self.current_theme = self.theme_generator.get_theme(outcome_type)
    
    def _display_stats(self):
        """Display current player statistics"""
        theme = self.current_theme or self.theme_generator.get_theme("balanced")
        
        print("\n## 📊 Your Life Stats\n")
        print(f"**Current Theme:** {theme['name']} - {theme['description']}\n")
        print(f"**Age:** {self.age}")
        
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
            print(f"**{emoji} {stat_name.title()}:** {bars}{empty} {value}/100")
        
        print(f"\n**Decisions Made:** {self.player_stats['decisions_made']}")
        print(f"**Wisdom Gained:** {self.player_stats['wisdom_gained']}")
        print(f"**Life Memories:** {self.player_stats['memories_count']}\n")
    
    def _get_memory_context(self):
        """Display relevant memories for context"""
        memories = self.memory_core.recall_memories(age_range=(self.age-10, self.age+5))
        if memories:
            print("## 📚 Past Life Memories\n")
            for decision, outcome, emotion in memories:
                emoji = self.mood_analyzer.get_mood_emoji(emotion)
                print(f"{emoji} **Age {self.age-3}:** {decision}")
                print(f"   *Result:* {outcome}")
            print("\n---\n")
    
    def _store_life_memory(self, scenario, outcome_type, mood, wisdom_impact):
        """Store the decision in memory"""
        outcome_text = f"{outcome_type.title()} - {mood} mood"
        self.memory_core.store_memory(
            self.age, scenario, outcome_text, mood, wisdom_impact
        )
        self.player_stats["memories_count"] += 1
    
    def _get_decision_feedback(self):
        """Get decision quality feedback"""
        wisdom_roll = random.randint(1, 100) + self.player_stats["wisdom"] // 10
        
        if wisdom_roll > 80:
            return "wise"
        elif wisdom_roll > 40:
            return "balanced"
        else:
            return "poor"
    
    def _clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def play_turn(self):
        """Play one turn of the life simulator"""
        scenario = self._get_random_scenario()
        
        print(f"\n## 🎭 Life Decision at Age {self.age}")
        print(f"\n**Scenario:** {scenario}\n")
        
        # Show relevant memories
        self._get_memory_context()
        
        print("The Devil's Advocate will debate this decision for you...")
        print("---\n")
        
        # Generate and display debate
        debate_text = self.debater.debate_topic(scenario)
        print(debate_text)
        
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
        
        # Display results
        print("---\n")
        print("\n## 🎯 Decision Outcome\n")
        
        emoji = self.mood_analyzer.get_mood_emoji(mood)
        theme = self.current_theme
        
        if outcome_type == "success":
            print(f"{emoji} **Triumphant Success!** Your wisdom guides you to victory.")
        elif outcome_type == "learning":
            print(f"{emoji} **Valuable Lesson!** Growth comes from experience.")
        else:
            print(f"{emoji} **Challenge Accepted!** Even struggles build character.")
        
        print(f"\n**Theme Applied:** {theme['name']}")
        print(f"**Time passes... You are now {self.age} years old.**\n")
        
        self._display_stats()
        
        # Check for game over conditions
        if self.player_stats["happiness"] <= 0:
            self._game_over("burnout")
            return False
        elif self.player_stats["health"] <= 0:
            self._game_over("health")
            return False
        elif self.age >= 80:
            self._game_over("natural")
            return False
        
        return True
    
    def _game_over(self, reason):
        """Handle game over scenarios"""
        print("\n# 🏁 Life Complete\n")
        
        if reason == "burnout":
            print("You've experienced burnout. The weight of your decisions became too much to bear.")
        elif reason == "health":
            print("Health challenges have ended your journey prematurely.")
        else:
            print(f"You've lived a full life to the age of {self.age}.")
        
        print("\n## 📈 Final Statistics\n")
        print(f"**Final Age:** {self.age}")
        print(f"**Total Decisions:** {self.player_stats['decisions_made']}")
        print(f"**Wisdom Level:** {self.player_stats['wisdom']}/100")
        print(f"**Final Happiness:** {self.player_stats['happiness']}/100")
        print(f"**Wisdom Gained:** {self.player_stats['wisdom_gained']}")
        print(f"**Life Memories Created:** {self.player_stats['memories_count']}\n")
        
        # Life assessment with themes
        if self.player_stats["wisdom"] >= 80:
            print("🏆 **Sage Status:** You've achieved remarkable wisdom and insight!")
            print("Your life theme: **Golden Victory** - a testament to your triumphs.")
        elif self.player_stats["wisdom"] >= 60:
            print("🌟 **Wise Life:** You've made many thoughtful decisions and learned much.")
            print("Your life theme: **Wisdom's Path** - a journey of continuous growth.")
        elif self.player_stats["wisdom"] >= 40:
            print("📚 **Learning Journey:** Life has taught you valuable lessons.")
            print("Your life theme: **Phoenix Rising** - rising from every challenge.")
        else:
            print("🌱 **Growing Soul:** Every experience is a step toward wisdom.")
            print("Your life theme: **Harmony Flow** - finding balance in the journey.")
        
        # Show final memories
        final_memories = self.memory_core.recall_memories()
        if final_memories:
            print("\n## 📖 Final Life Memories\n")
            for decision, outcome, emotion in final_memories[:5]:
                emoji = self.mood_analyzer.get_mood_emoji(emotion)
                print(f"{emoji} {decision}")
                print(f"   *{outcome}*")
        
        print("\n**Play again?** Start a new life journey with fresh memories!")
    
    def start_game(self):
        """Start the standalone life simulator game"""
        self._clear_screen()
        
        print("# 🌟 Enhanced Life Simulator - Standalone Version")
        print("=" * 60)
        print("\nWelcome to your enhanced life journey! This version includes:")
        print("- 🧠 **Memory System** - Your decisions are remembered and influence future choices")
        print("- 😊 **Mood Analysis** - Emotional context affects your life path")
        print("- 🎨 **Dynamic Themes** - Visual themes that reflect your life journey")
        print("- 📚 **Life Memories** - Persistent memory database of your choices")
        print("- 🤔 **AI Debates** - Built-in debate system for decision guidance")
        print("\nAt each stage, you'll face important decisions with debate guidance.")
        print("Your choices will shape your stats, create memories, and determine your life theme.")
        print("\nReady to begin your enhanced life at age 18?")
        
        input("\nPress Enter to begin your journey...")
        
        self._display_stats()
        
        # Game continues until game over
        game_active = True
        while game_active:
            game_active = self.play_turn()
            
            if game_active:
                print("\n" + "="*50)
                continue_choice = input("Continue your life journey? (Press Enter to continue, or 'q' to quit): ")
                if continue_choice.lower() == 'q':
                    print("\nChoosing to end your journey early...")
                    self._game_over("choice")
                    break
                print("="*50)
                time.sleep(1)


def main():
    """Main entry point for the standalone life simulator"""
    print("🌟 Enhanced Life Simulator - Standalone Version")
    print("=" * 50)
    print("A complete life simulation game with AI debates, memory system, and mood analysis.")
    print("No external dependencies required - runs entirely standalone!")
    print()
    
    game = StandaloneLifeSimulator()
    game.start_game()


if __name__ == "__main__":
    main()
