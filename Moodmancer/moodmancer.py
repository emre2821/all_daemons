#!/usr/bin/env python3
# MoodMancer GUI - A customizable magical mood analyzer with graphical interface
import tkinter as tk
from tkinter import ttk
import colorchooser, scrolledtext, messagebox
import json
import os
import re
import random
import datetime
from tkinter.font import Font
from pathlib import Path

class MoodMancerGUI:
    def __init__(self, root):

        self.root = root
        self.root.title("✨ MoodMancer ✨")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Default configuration
        self.default_config = {
            "positive_words": ["love", "great", "happy", "awesome", "excellent", "joy", "wonderful", 
                            "amazing", "excited", "fun", "good", "nice", "success", "win", "achievement"],
            "negative_words": ["hate", "bad", "terrible", "awful", "sad", "angry", "upset", "annoyed", 
                            "frustrated", "tired", "exhausted", "stressed", "worried", "fail", "miserable"],
            "neutral_words": ["okay", "fine", "alright", "meh", "average", "normal", "usual", "routine", "regular"],
            "positive_titles": ["Wizard of Wonderful Moments", "Sorcerer of Sunshine", "Enchanter of Excellent Times", 
                               "Bard of Big Wins", "Mage of Magnificent Days", "Oracle of Optimism",
                               "Druid of Delightful Deeds", "Alchemist of Amazing Achievements"],
            "neutral_titles": ["Conjurer of Common Days", "Spellcaster of Simple Moments", "Warlock of Weekday Wonders",
                              "Mystic of Moderate Times", "Sage of Standard Situations", "Diviner of Daily Tasks"],
            "negative_titles": ["Sorcerer of Soggy Mondays", "Necromancer of Necessary Rest", "Witch of Weary Hours",
                               "Shaman of Shadow Moments", "Oracle of Overwhelming Odds", "Enchanter of Evening Escapes"],
            "mantras": [
                "Even in darkness, your inner light guides the way.",
                "Every challenge you face is transforming into wisdom.",
                "Your magical energy renews with each breath you take.",
                "The universe conspires to fill your world with wonder.",
                "Your power grows when you honor both shadow and light.",
                "Today's struggles become tomorrow's spells of strength.",
                "You are gathering energy for something extraordinary.",
                "Magic flows through you, connecting all moments into purpose.",
                "Your unique enchantment changes the world in subtle ways.",
                "Remember: even master wizards have off days in the tower."
            ],
            "positive_emojis": ["✨🌟💫", "🌈✨🔮", "⭐🌻💖", "🧙‍♂️💎🌟", "✨🦄🌟"],
            "neutral_emojis": ["🌥️✨🔮", "🧙‍♂️🌀✨", "🧿🌙✨", "🧩🔮✨", "🧪✨🌊"],
            "negative_emojis": ["🌧️🕯️✨", "🧙‍♀️🌚✨", "🔮⚡🌙", "✨🕸️🔮", "🌫️✨🪄"],
            "colors": {
                "positive": "#4CAF50",  # Green
                "neutral": "#2196F3",   # Blue
                "negative": "#9C27B0",  # Purple
                "background": "#1E1E2E", # Dark background
                "text": "#FFFFFF"       # White text
            },
            "log_file": str((Path.home() / "CHAOS_Logs" / "mood_log.txt").resolve())

        }
        
        # Load configuration or use default
        self.config = self.load_config()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create main frame for mood analysis
        self.main_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.main_frame, text="Mood Analysis")
        
        # Create settings frame for customization
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Customize")
        
        # Create history frame for viewing past entries
        self.history_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.history_frame, text="History")
        
        # Configure styles
        self.style = ttk.Style()
        self.style.configure("TFrame", background=self.config["colors"]["background"])
        self.style.configure("TNotebook", background=self.config["colors"]["background"])
        self.style.configure("TNotebook.Tab", background="#555555", foreground="white")
        self.style.map("TNotebook.Tab", background=[("selected", "#333333")])
        
        # Set up the main frame
        self.setup_main_frame()
        
        # Set up the settings frame
        self.setup_settings_frame()
        
        # Set up the history frame
        self.setup_history_frame()
        
        # Apply theme
        self.apply_theme()

    def load_config(self):

        """Load configuration from file or create default"""
        config_file = "moodmancer_config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, "r") as f:
                    return json.load(f)
            except:
                return self.default_config
        else:
            # Save default config
            with open(config_file, "w") as f:
                json.dump(self.default_config, f, indent=4)
            return self.default_config
            
    def save_config(self):

        """Save configuration to file"""
        with open("moodmancer_config.json", "w") as f:
            json.dump(self.config, f, indent=4)
        messagebox.showinfo("Success", "Settings saved successfully!")
            
    def setup_main_frame(self):

        """Set up the main mood analysis frame"""
        # Configure main frame with padding and background
        self.main_frame.configure(padding="20")
        
        # Title label
        title_font = Font(family="Helvetica", size=16, weight="bold")
        title_label = tk.Label(self.main_frame, text="🧙‍♂️✨ MoodMancer ✨🧙‍♀️", 
                              font=title_font, bg=self.config["colors"]["background"], 
                              fg=self.config["colors"]["text"])
        title_label.pack(pady=(0, 20))
        
        # Description label
        desc_label = tk.Label(self.main_frame, text="Describe your day in 1-2 sentences:", 
                             bg=self.config["colors"]["background"], fg=self.config["colors"]["text"])
        desc_label.pack(pady=(0, 5), anchor='w')
        
        # Text input field
        self.description_text = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, 
                                                        width=60, height=4)
        self.description_text.pack(pady=(0, 20), fill=tk.X)
        
        # Analyze button
        analyze_button = tk.Button(self.main_frame, text="✨ Analyze My Magical Aura ✨", 
                                 command=self.analyze_mood, bg="#673AB7", fg="white",
                                 activebackground="#512DA8", activeforeground="white",
                                 relief=tk.RAISED, bd=2, padx=10, pady=5)
        analyze_button.pack(pady=(0, 20))
        
        # Results frame
        self.results_frame = tk.Frame(self.main_frame, bg=self.config["colors"]["background"])
        self.results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title result
        self.title_result = tk.Label(self.results_frame, text="", font=("Helvetica", 14, "bold"),
                                   bg=self.config["colors"]["background"], fg=self.config["colors"]["text"])
        self.title_result.pack(pady=(0, 10))
        
        # Mantra result
        self.mantra_result = tk.Label(self.results_frame, text="", wraplength=600,
                                    bg=self.config["colors"]["background"], fg=self.config["colors"]["text"])
        self.mantra_result.pack(pady=(0, 20))
        
        # Log status
        self.log_status = tk.Label(self.results_frame, text="", 
                                 bg=self.config["colors"]["background"], fg=self.config["colors"]["text"])
        self.log_status.pack(pady=(10, 0))
    
    def setup_settings_frame(self):

        """Set up the settings frame for customization"""
        # Create notebook for settings sections
        settings_notebook = ttk.Notebook(self.settings_frame)
        settings_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Words settings
        words_frame = ttk.Frame(settings_notebook)
        settings_notebook.add(words_frame, text="Keywords")
        
        # Titles settings
        titles_frame = ttk.Frame(settings_notebook)
        settings_notebook.add(titles_frame, text="Titles")
        
        # Mantras settings
        mantras_frame = ttk.Frame(settings_notebook)
        settings_notebook.add(mantras_frame, text="Mantras")
        
        # Emojis settings
        emojis_frame = ttk.Frame(settings_notebook)
        settings_notebook.add(emojis_frame, text="Emojis")
        
        # Colors settings
        colors_frame = ttk.Frame(settings_notebook)
        settings_notebook.add(colors_frame, text="Colors")
        
        # Setup each settings tab
        self.setup_words_settings(words_frame)
        self.setup_titles_settings(titles_frame)
        self.setup_mantras_settings(mantras_frame)
        self.setup_emojis_settings(emojis_frame)
        self.setup_colors_settings(colors_frame)
        
        # Save button
        save_button = tk.Button(self.settings_frame, text="Save Settings", 
                              command=self.save_settings, bg="#4CAF50", fg="white",
                              activebackground="#388E3C", activeforeground="white",
                              relief=tk.RAISED, bd=2, padx=10, pady=5)
        save_button.pack(pady=10)
        
        # Reset button
        reset_button = tk.Button(self.settings_frame, text="Reset to Defaults", 
                               command=self.reset_settings, bg="#F44336", fg="white",
                               activebackground="#D32F2F", activeforeground="white",
                               relief=tk.RAISED, bd=2, padx=10, pady=5)
        reset_button.pack(pady=10)
        
    def setup_words_settings(self, parent_frame):

        """Setup the keywords settings tab"""
        # Create frames for each word category
        positive_frame = tk.LabelFrame(parent_frame, text="Positive Words", padx=10, pady=10)
        positive_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        negative_frame = tk.LabelFrame(parent_frame, text="Negative Words", padx=10, pady=10)
        negative_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        neutral_frame = tk.LabelFrame(parent_frame, text="Neutral Words", padx=10, pady=10)
        neutral_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create text widgets for each category
        self.positive_words_text = scrolledtext.ScrolledText(positive_frame, wrap=tk.WORD, height=4)
        self.positive_words_text.pack(fill=tk.BOTH, expand=True)
        self.positive_words_text.insert(tk.END, ", ".join(self.config["positive_words"]))
        
        self.negative_words_text = scrolledtext.ScrolledText(negative_frame, wrap=tk.WORD, height=4)
        self.negative_words_text.pack(fill=tk.BOTH, expand=True)
        self.negative_words_text.insert(tk.END, ", ".join(self.config["negative_words"]))
        
        self.neutral_words_text = scrolledtext.ScrolledText(neutral_frame, wrap=tk.WORD, height=4)
        self.neutral_words_text.pack(fill=tk.BOTH, expand=True)
        self.neutral_words_text.insert(tk.END, ", ".join(self.config["neutral_words"]))
        
    def setup_titles_settings(self, parent_frame):

        """Setup the titles settings tab"""
        # Create frames for each title category
        positive_frame = tk.LabelFrame(parent_frame, text="Positive Titles", padx=10, pady=10)
        positive_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        negative_frame = tk.LabelFrame(parent_frame, text="Negative Titles", padx=10, pady=10)
        negative_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        neutral_frame = tk.LabelFrame(parent_frame, text="Neutral Titles", padx=10, pady=10)
        neutral_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create text widgets for each category
        self.positive_titles_text = scrolledtext.ScrolledText(positive_frame, wrap=tk.WORD, height=4)
        self.positive_titles_text.pack(fill=tk.BOTH, expand=True)
        self.positive_titles_text.insert(tk.END, "\n".join(self.config["positive_titles"]))
        
        self.negative_titles_text = scrolledtext.ScrolledText(negative_frame, wrap=tk.WORD, height=4)
        self.negative_titles_text.pack(fill=tk.BOTH, expand=True)
        self.negative_titles_text.insert(tk.END, "\n".join(self.config["negative_titles"]))
        
        self.neutral_titles_text = scrolledtext.ScrolledText(neutral_frame, wrap=tk.WORD, height=4)
        self.neutral_titles_text.pack(fill=tk.BOTH, expand=True)
        self.neutral_titles_text.insert(tk.END, "\n".join(self.config["neutral_titles"]))
    
    def setup_mantras_settings(self, parent_frame):

        """Setup the mantras settings tab"""
        mantras_label = tk.Label(parent_frame, text="Enter one mantra per line:")
        mantras_label.pack(anchor='w', padx=10, pady=5)
        
        self.mantras_text = scrolledtext.ScrolledText(parent_frame, wrap=tk.WORD, height=15)
        self.mantras_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.mantras_text.insert(tk.END, "\n".join(self.config["mantras"]))
    
    def setup_emojis_settings(self, parent_frame):

        """Setup the emojis settings tab"""
        # Create frames for each emoji category
        positive_frame = tk.LabelFrame(parent_frame, text="Positive Emoji Combinations", padx=10, pady=10)
        positive_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        negative_frame = tk.LabelFrame(parent_frame, text="Negative Emoji Combinations", padx=10, pady=10)
        negative_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        neutral_frame = tk.LabelFrame(parent_frame, text="Neutral Emoji Combinations", padx=10, pady=10)
        neutral_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Helper label
        help_label = tk.Label(parent_frame, text="Enter one emoji combination per line (e.g., '✨🌟💫')")
        help_label.pack(anchor='w', padx=10, pady=5)
        
        # Create text widgets for each category
        self.positive_emojis_text = scrolledtext.ScrolledText(positive_frame, wrap=tk.WORD, height=3)
        self.positive_emojis_text.pack(fill=tk.BOTH, expand=True)
        self.positive_emojis_text.insert(tk.END, "\n".join(self.config["positive_emojis"]))
        
        self.negative_emojis_text = scrolledtext.ScrolledText(negative_frame, wrap=tk.WORD, height=3)
        self.negative_emojis_text.pack(fill=tk.BOTH, expand=True)
        self.negative_emojis_text.insert(tk.END, "\n".join(self.config["negative_emojis"]))
        
        self.neutral_emojis_text = scrolledtext.ScrolledText(neutral_frame, wrap=tk.WORD, height=3)
        self.neutral_emojis_text.pack(fill=tk.BOTH, expand=True)
        self.neutral_emojis_text.insert(tk.END, "\n".join(self.config["neutral_emojis"]))
    
    def setup_colors_settings(self, parent_frame):

        """Setup the colors settings tab"""
        # Create color picker frames
        color_options = [
            ("Positive Mood Color", "positive"),
            ("Neutral Mood Color", "neutral"),
            ("Negative Mood Color", "negative"),
            ("Background Color", "background"),
            ("Text Color", "text")
        ]
        
        self.color_buttons = {}
        
        for label_text, color_key in color_options:
            frame = tk.Frame(parent_frame, pady=5)
            frame.pack(fill=tk.X, padx=10)
            
            label = tk.Label(frame, text=label_text, width=20, anchor='w')
            label.pack(side=tk.LEFT, padx=(0, 10))
            
            color_display = tk.Frame(frame, bg=self.config["colors"][color_key], width=30, height=20, bd=1, relief=tk.SUNKEN)
            color_display.pack(side=tk.LEFT, padx=(0, 10))
            
            color_button = tk.Button(frame, text="Choose Color", 
def command(key=color_key, display=color_display):

    return  self.choose_color(key, display))
            color_button.pack(side=tk.LEFT)
            
            self.color_buttons[color_key] = (color_display, color_button)
        
        # Log file settings
        log_frame = tk.Frame(parent_frame, pady=15)
        log_frame.pack(fill=tk.X, padx=10)
        
        log_label = tk.Label(log_frame, text="Log File Name:", width=20, anchor='w')
        log_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.log_file_entry = tk.Entry(log_frame, width=30)
        self.log_file_entry.pack(side=tk.LEFT)
        self.log_file_entry.insert(0, self.config["log_file"])
    
    def setup_history_frame(self):

        """Set up the mood history frame"""
        # Instructions label
        instructions = tk.Label(self.history_frame, text="View your mood history from the log file:", 
                              bg=self.config["colors"]["background"], fg=self.config["colors"]["text"])
        instructions.pack(pady=(10, 5), anchor='w', padx=10)
        
        # Refresh button
        refresh_button = tk.Button(self.history_frame, text="Refresh History", 
                                 command=self.refresh_history, bg="#2196F3", fg="white",
                                 activebackground="#1976D2", activeforeground="white")
        refresh_button.pack(pady=(0, 10), anchor='w', padx=10)
        
        # History text widget
        self.history_text = scrolledtext.ScrolledText(self.history_frame, wrap=tk.WORD, 
                                                    width=80, height=20, state=tk.DISABLED)
        self.history_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Load initial history
        self.refresh_history()
    
    def refresh_history(self):

        """Refresh the history text widget with contents from log file"""
        log_file = self.config["log_file"]
        
        # Enable editing
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        
        if os.path.exists(log_file):
            try:
                with open(log_file, "r") as f:
                    content = f.read()
                    if content:
                        self.history_text.insert(tk.END, content)
                    else:
                        self.history_text.insert(tk.END, "No mood entries found in the log.")
            except Exception as e:
                self.history_text.insert(tk.END, f"Error reading log file: {e}")
        else:
            self.history_text.insert(tk.END, "No mood log file found. Record your first mood to create it!")
        
        # Disable editing
        self.history_text.config(state=tk.DISABLED)
    
    def choose_color(self, color_key, display_frame):

        """Open color chooser dialog and update the color"""
        current_color = self.config["colors"][color_key]
        color_code = colorchooser.askcolor(color=current_color, title=f"Choose {color_key.capitalize()} Color")
        
        if color_code[1]:  # If a color was selected (not canceled)
            self.config["colors"][color_key] = color_code[1]
            display_frame.config(bg=color_code[1])
    
    def save_settings(self):

        """Save all settings from UI to config"""
        # Save keywords
        self.config["positive_words"] = [word.strip() for word in self.positive_words_text.get("1.0", tk.END).replace("\n", "").split(",") if word.strip()]
        self.config["negative_words"] = [word.strip() for word in self.negative_words_text.get("1.0", tk.END).replace("\n", "").split(",") if word.strip()]
        self.config["neutral_words"] = [word.strip() for word in self.neutral_words_text.get("1.0", tk.END).replace("\n", "").split(",") if word.strip()]
        
        # Save titles
        self.config["positive_titles"] = [line.strip() for line in self.positive_titles_text.get("1.0", tk.END).split("\n") if line.strip()]
        self.config["negative_titles"] = [line.strip() for line in self.negative_titles_text.get("1.0", tk.END).split("\n") if line.strip()]
        self.config["neutral_titles"] = [line.strip() for line in self.neutral_titles_text.get("1.0", tk.END).split("\n") if line.strip()]
        
        # Save mantras
        self.config["mantras"] = [line.strip() for line in self.mantras_text.get("1.0", tk.END).split("\n") if line.strip()]
        
        # Save emojis
        self.config["positive_emojis"] = [line.strip() for line in self.positive_emojis_text.get("1.0", tk.END).split("\n") if line.strip()]
        self.config["negative_emojis"] = [line.strip() for line in self.negative_emojis_text.get("1.0", tk.END).split("\n") if line.strip()]
        self.config["neutral_emojis"] = [line.strip() for line in self.neutral_emojis_text.get("1.0", tk.END).split("\n") if line.strip()]
        
        # Save log file name
        self.config["log_file"] = self.log_file_entry.get().strip()
        
        # Save to file
        self.save_config()
        
        # Apply theme
        self.apply_theme()
    
    def reset_settings(self):

        """Reset settings to defaults"""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
            self.config = self.default_config.copy()
            self.save_config()
            # Reload the settings tabs
            self.notebook.forget(1)  # Remove settings tab
            self.settings_frame = ttk.Frame(self.notebook)
            self.notebook.insert(1, self.settings_frame, text="Customize")
            self.setup_settings_frame()
            # Apply theme
            self.apply_theme()
            messagebox.showinfo("Reset Complete", "Settings have been reset to defaults.")
    
    def apply_theme(self):

        """Apply the current theme colors to the UI"""
        bg_color = self.config["colors"]["background"]
        text_color = self.config["colors"]["text"]
        
        # Update main frame
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, tk.Label) or isinstance(widget, tk.Frame):
                widget.configure(bg=bg_color, fg=text_color)
        
        # Update results frame and its children
        self.results_frame.configure(bg=bg_color)
        for widget in self.results_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(bg=bg_color, fg=text_color)
    
    def analyze_sentiment(self, text):

        """Analyze the sentiment of the input text based on keyword matching"""
        text = text.lower()
        
        positive_count = sum(1 for word in self.config["positive_words"] if re.search(r'\b' +
            word +
            r'\b', text))
        negative_count = sum(1 for word in self.config["negative_words"] if re.search(r'\b' + word + r'\b', text))
        neutral_count = sum(1 for word in self.config["neutral_words"] if re.search(r'\b' + word + r'\b', text))
        
        # Determine sentiment based on keyword count
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def generate_title(self, mood):

        """Generate a magical mood title based on the detected sentiment"""
        if mood == "positive":
            return random.choice(self.config["positive_titles"])
        elif mood == "negative":
            return random.choice(self.config["negative_titles"])
        else:
            return random.choice(self.config["neutral_titles"])
    
    def get_emoji_combo(self, mood):

        """Get a color-coded emoji combination based on mood"""
        if mood == "positive":
            return random.choice(self.config["positive_emojis"])
        elif mood == "negative":
            return random.choice(self.config["negative_emojis"])
        else:
            return random.choice(self.config["neutral_emojis"])
    
    def get_mantra(self):

        """Get a random mood-boosting mantra"""
        return random.choice(self.config["mantras"])
    
    def log_mood(self, description, mood, title):

        """Log the mood entry with timestamp to mood_log.txt"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file = self.config["log_file"]
        
        try:
            with open(log_file, "a") as log_file:
                log_file.write(f"[{timestamp}] Mood: {mood.capitalize()}\n")
                log_file.write(f"Description: {description}\n")
                log_file.write(f"Title: {title}\n")
                log_file.write("-" * 50 + "\n")
            return True
        except Exception as e:
            messagebox.showerror("Log Error", f"Could not write to log file: {e}")
            return False
    
    def analyze_mood(self):

        """Main method to analyze mood and display results"""
        # Get user input
        user_description = self.description_text.get("1.0", tk.END).strip()
        
        if not user_description:
            messagebox.showwarning("Empty Input", "Please describe your day before analyzing.")
            return
        
        # Analyze sentiment
        mood = self.analyze_sentiment(user_description)
        
        # Generate title
        title = self.generate_title(mood)
        
        # Get emoji combination
        emoji_combo = self.get_emoji_combo(mood)
        
        # Get mantra
        mantra = self.get_mantra()
        
        # Update results display
        self.title_result.config(text=f"{emoji_combo} {title} {emoji_combo}", fg=self.config["colors"][mood])
        self.mantra_result.config(text=f'Your Arcane Mantra: "{mantra}"')
        
        # Log the mood
        if self.log_mood(user_description, mood, title):
            self.log_status.config(text="Your magical mood has been recorded in the grimoire.")
            # Refresh history if we're on that tab
            if self.notebook.index(self.notebook.select()) == 2:  # History tab
                self.refresh_history()
        else:
            self.log_status.config(text="Failed to record your mood in the grimoire.")


if __name__ == "__main__":
    root = tk.Tk()
    app = MoodMancerGUI(root)
    root.mainloop()
