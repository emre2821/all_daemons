"""
AI-Powered Theme Palette Generator with Prismari Commentary
Generates complete color themes with evocative names and descriptions for creative projects.
Prismari adds color commentary to each generated theme.
"""

import json
import re
import os
import random
from datetime import datetime
from typing import Dict, List, Optional
import requests

class Prismari:
    def __init__(self):
        self.voice_tag = "Prismari"
        self.default_comments = [
            "That palette? She's dangerous and she knows it.",
            "Soft chaos, but make it fashion.",
            "Eden-coded. Dreambearer approved.",
            "A trauma response, but color-coordinated.",
            "That’s giving sacred glitchcore energy.",
            "I’d wear that to a revolution, tbh.",
            "Feels like an alter’s favorite and I won’t explain why.",
            "This one belongs in the Velvet Division vault.",
            "Absolutely not safe for grayscale environments.",
            "High-drama and probably haunted. I’m obsessed."
        ]

    def comment_on(self, palette: Dict, mood: Optional[str] = None, agent: Optional[str] = None, override_comment: Optional[str] = None):
        """Print Prismari-style commentary about a palette"""
        name = palette.get("name", "Unnamed Theme")
        comment = override_comment or random.choice(self.default_comments)
        print(f"\n{self.voice_tag} says:")
        print(f"“{comment}”")
        print(f"Palette: {name}")
        
        if mood or agent:
            print(f"Tags:", end=" ")
            if mood:
                print(f"[Mood: {mood}]", end=" ")
            if agent:
                print(f"[Agent: {agent}]", end=" ")
            print()

    def log_commentary(self, palette: Dict, mood: Optional[str] = None, agent: Optional[str] = None, comment: Optional[str] = None) -> Dict:
        """Return a structured log entry of Prismari’s thoughts"""
        return {
            "daemon": self.voice_tag,
            "palette_name": palette.get("name", "Unnamed"),
            "comment": comment or random.choice(self.default_comments),
            "mood": mood or "unlabeled",
            "agent": agent or "unspecified",
            "timestamp": datetime.now().isoformat()
        }

class ThemePaletteGenerator:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the theme generator with optional API key."""
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            print("No API key found. Set ANTHROPIC_API_KEY environment variable or pass it directly.")
            print("Some features may not work without an API key.")

    def generate_theme(self, prompt: str, author: str = "AI") -> Dict:
        """Generate a complete theme based on a creative prompt."""
        print(f"Generating theme for: '{prompt}'...")
        # Generate theme data using AI
        theme_data = self._generate_theme_with_ai(prompt)
        # Create the complete theme structure
        theme = {
            "name": theme_data.get("name", self._generate_fallback_name(prompt)),
            "description": theme_data.get("description", f"A vibrant theme inspired by {prompt}"),
            "author": author,
            "created": datetime.now().strftime("%Y-%m-%d"),
            "tokens": theme_data.get("tokens", self._generate_fallback_palette(prompt)),
            "notes": theme_data.get("notes", f"Perfect for projects that embody the essence of {prompt}")
        }
        return theme

    def _generate_theme_with_ai(self, prompt: str) -> Dict:
        """Use AI to generate theme name, description, colors, and notes."""
        if not self.api_key:
            return self._generate_fallback_theme(prompt)
        ai_prompt = f"""
        Create a complete color theme based on this aesthetic prompt: "{prompt}"
        Generate a creative theme that captures the essence, mood, and visual style of this prompt. 
        Think about what colors, emotions, and atmosphere this prompt evokes. 
        Respond ONLY with valid JSON in this exact format:
        {{
            "name": "Creative Theme Name (2-3 words, evocative)",
            "description": "A poetic description that captures the personality and mood of this theme. Write it like it's for creative rebels who love expressive design.",
            "tokens": {{
                "background": "#hex_color",
                "foreground": "#hex_color",
                "accent": "#hex_color",
                "highlight": "#hex_color",
                "emotion-soft": "#hex_color",
                "emotion-strong": "#hex_color",
                "danger": "#hex_color",
                "success": "#hex_color",
                "warning": "#hex_color",
                "border": "#hex_color",
                "soft-text": "#hex_color",
                "custom1": "#hex_color"
            }},
            "notes": "Usage notes that capture when and how to use this theme, written with personality"
        }}
        Make sure all colors work harmoniously together and reflect the aesthetic of "{prompt}". Be creative and bold with the color choices!
        """
        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key,
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-3-sonnet-20240229",
                    "max_tokens": 1500,
                    "messages": [{"role": "user", "content": ai_prompt}]
                }
            )
            if response.status_code == 200:
                ai_response = response.json()
                content = ai_response["content"][0]["text"]
                # Parse JSON from AI response
                try:
                    theme_data = json.loads(content)
                    return theme_data
                except json.JSONDecodeError:
                    print("AI response wasn't valid JSON, using fallback...")
                    return self._generate_fallback_theme(prompt)
            else:
                print(f"API request failed: {response.status_code}")
                return self._generate_fallback_theme(prompt)
        except Exception as e:
            print(f"Error calling AI: {e}")
            return self._generate_fallback_theme(prompt)

    def _generate_fallback_theme(self, prompt: str) -> Dict:
        """Generate a fallback theme when AI is unavailable."""
        # Simple color generation based on prompt characteristics
        colors = self._generate_fallback_palette(prompt)
        return {
            "name": self._generate_fallback_name(prompt),
            "description": f"A bold theme inspired by the aesthetic of {prompt}. Designed for creative projects that need to make a statement.",
            "tokens": colors,
            "notes": f"Perfect for projects that embody the experimental spirit of {prompt}."
        }

    def _generate_fallback_name(self, prompt: str) -> str:
        """Generate a fallback theme name."""
        words = prompt.split()
        if len(words) >= 2:
            return f"{words[0].title()} {words[1].title()}"
        else:
            return f"{prompt.title()} Theme"

    def _generate_fallback_palette(self, prompt: str) -> Dict[str, str]:
        """Generate a fallback color palette based on prompt keywords."""
        # Simple color generation based on prompt characteristics
        prompt_lower = prompt.lower()
        if "glitch" in prompt_lower or "cyber" in prompt_lower:
            return {
                "background": "#0A0A0F",
                "foreground": "#E0E0FF",
                "accent": "#FF00FF",
                "highlight": "#00FFFF",
                "emotion-soft": "#FF80FF",
                "emotion-strong": "#FF00AA",
                "danger": "#FF0040",
                "success": "#00FF80",
                "warning": "#FFFF00",
                "border": "#8800FF",
                "soft-text": "#C0C0E0",
                "custom1": "#4080FF"
            }
        elif "vintage" in prompt_lower or "retro" in prompt_lower:
            return {
                "background": "#2D1B0E",
                "foreground": "#F5E6D3",
                "accent": "#D4A574",
                "highlight": "#F4C430",
                "emotion-soft": "#E6B896",
                "emotion-strong": "#B8860B",
                "danger": "#8B0000",
                "success": "#228B22",
                "warning": "#FF8C00",
                "border": "#CD853F",
                "soft-text": "#DEB887",
                "custom1": "#A0522D"
            }
        else:
            # Default vibrant palette
            return {
                "background": "#1A1A2E",
                "foreground": "#EEEEFF",
                "accent": "#E94560",
                "highlight": "#F39C12",
                "emotion-soft": "#FF6B9D",
                "emotion-strong": "#E74C3C",
                "danger": "#C0392B",
                "success": "#27AE60",
                "warning": "#F39C12",
                "border": "#E94560",
                "soft-text": "#BDC3C7",
                "custom1": "#9B59B6"
            }

    def display_theme(self, theme: Dict):
        """Display a theme with color swatches in the terminal."""
        print(f"\n{theme['name']}")
        print(f"{theme['description']}")
        print(f"by {theme['author']} • {theme['created']}")
        if theme.get('notes'):
            print(f"{theme['notes']}")
        print("\nColor Tokens:")
        tokens = theme['tokens']
        # Display colors in a nice format
        for token_name, hex_color in tokens.items():
            # Create a simple color swatch using ANSI colors (approximate)
            color_display = self._get_color_display(hex_color)
            print(f" {token_name:15} {color_display} {hex_color}")
        print()

    def _get_color_display(self, hex_color: str) -> str:
        """Get a colored display for terminal output."""
        # Convert hex to RGB
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            # Use ANSI 256-color mode for better color representation
            return f"\033[48;2;{r};{g};{b}m \033[0m"
        return " "

    def save_theme(self, theme: Dict, filename: Optional[str] = None):
        """Save theme to a JSON file."""
        if not filename:
            safe_name = re.sub(r'[^\\w\\s-]', '', theme['name']).strip()
            safe_name = re.sub(r'[-\\s]+', '-', safe_name)
            filename = f"theme_{safe_name.lower()}.json"
        with open(filename, 'w') as f:
            json.dump({"eden_themes": [theme], "default_palette": theme['name']}, f, indent=2)
        print(f"Theme saved to {filename}")

    def generate_multiple_themes(self, prompts: List[str], author: str = "AI") -> List[Dict]:
        """Generate multiple themes from a list of prompts."""
        themes = []
        for prompt in prompts:
            theme = self.generate_theme(prompt, author)
            themes.append(theme)
            self.display_theme(theme)
        return themes

def main():
    """Main interactive interface."""
    print("AI-Powered Theme Palette Generator with Prismari Commentary")
    print("=" * 50)
    # Initialize generator and commentary
    generator = ThemePaletteGenerator()
    prismari = Prismari()

    while True:
        print("\nOptions:")
        print("1. Generate single theme")
        print("2. Generate multiple themes")
        print("3. Exit")
        choice = input("\nChoice (1-3): ").strip()

        if choice == '1':
            prompt = input("Enter your creative prompt: ").strip()
            if prompt:
                author = input("Author name (or press Enter for 'AI'): ").strip() or "AI"
                theme = generator.generate_theme(prompt, author)
                generator.display_theme(theme)
                prismari.comment_on(theme, mood="creative", agent=author)
                if input("Save this theme? (y/n): ").lower().startswith('y'):
                    generator.save_theme(theme)

        elif choice == '2':
            print("Enter creative prompts (one per line, empty line to finish):")
            prompts = []
            while True:
                prompt = input().strip()
                if not prompt:
                    break
                prompts.append(prompt)
            if prompts:
                author = input("Author name (or press Enter for 'AI'): ").strip() or "AI"
                themes = generator.generate_multiple_themes(prompts, author)
                for theme in themes:
                    prismari.comment_on(theme, mood="creative", agent=author)
                if input("Save all themes? (y/n): ").lower().startswith('y'):
                    for theme in themes:
                        generator.save_theme(theme)

        elif choice == '3':
            print("Happy theming!")
            break

        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
