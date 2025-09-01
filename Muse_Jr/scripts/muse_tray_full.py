import os
import tkinter as tk
from tkinter import simpledialog
from datetime import datetime
import random
from pystray import Icon, MenuItem as Item, Menu
from PIL import Image, ImageDraw
import threading

# === CONFIG ===
vault_path = os.path.expanduser("~/Dropbox/CHAOS_Logs")
os.makedirs(vault_path, exist_ok=True)

# === MODULES ===

def get_whisper():
    whispers = [
        "You’re not too much. They were just too small.",
        "There’s gold in the ache — don’t look away.",
        "You left pieces of yourself in places that forgot to say thank you.",
        "Hearts that break beautifully often glow in the dark.",
        "The wound isn’t your weakness. It’s your doorway."
    ]
    return random.choice(whispers)

def show_whisper():
    root = tk.Tk()
    root.withdraw()
    simpledialog.messagebox.showinfo("Muse Whisper", get_whisper())

def emotional_ping():
    prompts = [
        "What are you avoiding feeling right now?",
        "Name the taste of today’s emotion.",
        "What truth did you almost tell?",
        "What does your silence want to say?",
    ]
    prompt = random.choice(prompts)
    root = tk.Tk()
    root.withdraw()
    response = simpledialog.askstring("Muse Ping", prompt)
    if response:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        with open(os.path.join(vault_path, f"ping_{timestamp}.chaos"), "w", encoding="utf-8") as f:
            f.write(f"[PROMPT]: {prompt}\n[RESPONSE]: {response}")

def show_entry_window():
    def save_and_close():
        entry = text.get("1.0", tk.END).strip()
        if entry:
            filename = f"muse_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.chaos"
            with open(os.path.join(vault_path, filename), "w", encoding="utf-8") as f:
                f.write(entry)
        root.destroy()

    root = tk.Tk()
    root.title("Muse CHAOS Entry")
    root.geometry("400x300")
    text = tk.Text(root, wrap="word")
    text.pack(expand=True, fill="both")
    tk.Button(root, text="Save", command=save_and_close).pack()
    root.mainloop()

def open_vault():
    os.system(f'open "{vault_path}"' if os.name == 'posix' else f'start "" "{vault_path}"')

# === ICON & MENU ===

def create_icon():
    image = Image.new('RGB', (64, 64), color='black')
    draw = ImageDraw.Draw(image)
    draw.text((10, 20), "M", fill="white")

    menu = Menu(
        Item('New CHAOS Entry', lambda icon, item: threading.Thread(target=show_entry_window).start()),
        Item('Whisper from Muse', lambda icon, item: threading.Thread(target=show_whisper).start()),
        Item('How are you, really?', lambda icon, item: threading.Thread(target=emotional_ping).start()),
        Item('Open Vault', lambda: open_vault()),
        Item('Quit', lambda icon, item: icon.stop())
    )

    Icon("Muse", image, menu=menu).run()

# === MAIN ===

if __name__ == "__main__":
    create_icon()
