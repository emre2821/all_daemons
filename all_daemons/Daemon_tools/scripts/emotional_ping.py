import tkinter as tk
from datetime import datetime
import os

def save_entry(emotion):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = os.path.expanduser(f"~/CHAOS_Logs/quick_ping_{timestamp}.chaos")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"[EVENT]: ping\n[TIME]: {timestamp}\n[EMOTION]: {emotion}\n[INTENSITY]: quick\n")
    root.quit()

root = tk.Tk()
root.title("Muse Emotional Ping")

tk.Label(root, text="Emotion:").pack()
entry = tk.Entry(root)
entry.pack()
tk.Button(root, text="Log", command=lambda: save_entry(entry.get())).pack()

root.mainloop()

