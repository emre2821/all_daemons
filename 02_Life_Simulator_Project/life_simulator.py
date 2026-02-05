# poe: name=Life-Simulator-Game
import random
import time
from devils_advocate import DevilsAdvocate

class LifeSimulator:
    def __init__(self):
        self.debater = DevilsAdvocate()
        self.player_stats = {
            "wisdom": 50,
            "happiness": 50,
            "career": 50,
            "relationships": 50,
            "health": 50,
            "decisions_made": 0,
            "wisdom_gained": 0
        }
        self.age = 18
        self.scenarios = self._generate_scenarios()
        
    def _generate_scenarios(self):
        """Generate life scenarios for different age ranges"""
        return {
            "teen": [
                "Should I go to college or start working immediately?",
                "Should I move out of my parents' house or stay to save money?",
                "Should I pursue my passion or choose a practical career?",
                "Should I travel the world or focus on building stability?"
            ],
            "young_adult": [
                "Should I accept this high-paying job I hate or a low-paying job I love?",
                "Should I get married now or wait until I'm more established?",
                "Should I buy a house or keep renting for flexibility?",
                "Should I start a business or work for someone else?"
            ],
            "adult": [
                "Should I have children or remain child-free?",
                "Should I switch careers mid-life or stay in my current field?",
                "Should I move to a new city for better opportunities?",
                "Should I take a risky investment or play it safe?"
            ],
            "middle_age": [
                "Should I go back to school to learn something new?",
                "Should I retire early or keep working?",
                "Should I downsize my lifestyle or maintain my current standard?",
                "Should I prioritize my career or spend more time with family?"
            ]
        }
    
    def _get_age_category(self):
        """Determine life stage based on age"""
        if self.age < 25:
            return "teen"
        elif self.age < 35:
            return "young_adult"
        elif self.age < 50:
            return "adult"
        else:
            return "middle_age"
    
    def _get_random_scenario(self):
        """Get a random scenario based on current age"""
        category = self._get_age_category()
        return random.choice(self.scenarios[category])
    
    def _update_stats(self, decision_quality):
        """Update player stats based on decision quality"""
        if decision_quality == "wise":
            self.player_stats["wisdom"] += 5
            self.player_stats["happiness"] += 3
            self.player_stats["wisdom_gained"] += 1
        elif decision_quality == "balanced":
            self.player_stats["wisdom"] += 2
            self.player_stats["happiness"] += 1
        else:  # poor decision
            self.player_stats["wisdom"] -= 3
            self.player_stats["happiness"] -= 5
        
        # Random life events
        self.player_stats["career"] += random.randint(-2, 3)
        self.player_stats["relationships"] += random.randint(-2, 3)
        self.player_stats["health"] += random.randint(-1, 2)
        
        # Keep stats in bounds
        for stat in self.player_stats:
            if isinstance(self.player_stats[stat], int):
                self.player_stats[stat] = max(0, min(100, self.player_stats[stat]))
    
    def _display_stats(self):
        """Display current player statistics"""
        with poe.start_message() as msg:
            msg.write("## 📊 Your Life Stats\n\n")
            msg.write(f"**Age:** {self.age}\n")
            msg.write(f"**Wisdom:** {'█' * (self.player_stats['wisdom']//10)}{'░' * (10 - self.player_stats['wisdom']//10)} {self.player_stats['wisdom']}/100\n")
            msg.write(f"**Happiness:** {'█' * (self.player_stats['happiness']//10)}{'░' * (10 - self.player_stats['happiness']//10)} {self.player_stats['happiness']}/100\n")
            msg.write(f"**Career:** {'█' * (self.player_stats['career']//10)}{'░' * (10 - self.player_stats['career']//10)} {self.player_stats['career']}/100\n")
            msg.write(f"**Relationships:** {'█' * (self.player_stats['relationships']//10)}{'░' * (10 - self.player_stats['relationships']//10)} {self.player_stats['relationships']}/100\n")
            msg.write(f"**Health:** {'█' * (self.player_stats['health']//10)}{'░' * (10 - self.player_stats['health']//10)} {self.player_stats['health']}/100\n")
            msg.write(f"\n**Decisions Made:** {self.player_stats['decisions_made']}\n")
            msg.write(f"**Wisdom Gained:** {self.player_stats['wisdom_gained']}\n\n")
    
    def _get_decision_feedback(self):
        """Get AI feedback on the debate to determine decision quality"""
        # This would analyze the debate results to determine if the player
        # made a wise, balanced, or poor decision
        # For now, we'll use a simple random system
        wisdom_roll = random.randint(1, 100)
        
        if wisdom_roll > 70:
            return "wise"
        elif wisdom_roll > 30:
            return "balanced"
        else:
            return "poor"
    
    def play_turn(self):
        """Play one turn of the life simulator"""
        scenario = self._get_random_scenario()
        
        with poe.start_message() as msg:
            msg.write(f"## 🎭 Life Decision at Age {self.age}\n\n")
            msg.write(f"**Scenario:** {scenario}\n\n")
            msg.write("The Devil's Advocate will debate this decision for you...\n\n")
            msg.write("---\n\n")
        
        # Set the scenario as the topic for debate
        poe.query.text = scenario
        
        # Run the debate
        self.debater.run()
        
        # Get feedback on the decision
        decision_quality = self._get_decision_feedback()
        
        # Update stats
        self._update_stats(decision_quality)
        self.player_stats["decisions_made"] += 1
        
        # Age the character
        self.age += random.randint(1, 3)
        
        # Display results
        with poe.start_message() as msg:
            msg.write("---\n\n")
            msg.write("## 🎯 Decision Outcome\n\n")
            
            if decision_quality == "wise":
                msg.write("✅ **Wisdom Gained!** You made a thoughtful decision that will serve you well.\n")
            elif decision_quality == "balanced":
                msg.write("⚖️ **Balanced Choice** A reasonable decision with mixed results.\n")
            else:
                msg.write("⚠️ **Lesson Learned** This decision may lead to challenges, but you'll grow from it.\n")
            
            msg.write(f"\n**Time passes... You are now {self.age} years old.**\n\n")
        
        self._display_stats()
        
        # Check for game over conditions
        if self.player_stats["happiness"] <= 0:
            self._game_over("burnout")
        elif self.player_stats["health"] <= 0:
            self._game_over("health")
        elif self.age >= 80:
            self._game_over("natural")
    
    def _game_over(self, reason):
        """Handle game over scenarios"""
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
            msg.write(f"**Wisdom Gained:** {self.player_stats['wisdom_gained']}\n\n")
            
            # Life assessment
            if self.player_stats["wisdom"] >= 80:
                msg.write("🏆 **Sage Status:** You've achieved remarkable wisdom and insight!\n")
            elif self.player_stats["wisdom"] >= 60:
                msg.write("🌟 **Wise Life:** You've made many thoughtful decisions and learned much.\n")
            elif self.player_stats["wisdom"] >= 40:
                msg.write("📚 **Learning Journey:** Life has taught you valuable lessons.\n")
            else:
                msg.write("🌱 **Growing Soul:** Every experience is a step toward wisdom.\n")
            
            msg.write("\n**Play again?** Start a new life journey!")
    
    def start_game(self):
        """Start the life simulator game"""
        with poe.start_message() as msg:
            msg.write("# 🌟 Life Simulator with Devil's Advocate\n\n")
            msg.write("Welcome to your life journey! At each stage, you'll face important decisions.\n")
            msg.write("The Devil's Advocate will debate each choice, helping you see different perspectives.\n")
            msg.write("Your choices will shape your stats and determine your life path.\n\n")
            msg.write("Ready to begin your life at age 18?\n\n")
        
        self._display_stats()
        
        # Game continues until game over
        while self.age < 80 and self.player_stats["happiness"] > 0 and self.player_stats["health"] > 0:
            self.play_turn()
            
            # Small delay between turns for pacing
            time.sleep(1)


if __name__ == "__main__":
    game = LifeSimulator()
    game.start_game()
