import tkinter as tk
from tkinter import filedialog, messagebox
import json

def load_mirror_file():
    file_path = filedialog.askopenfilename(filetypes=[("Mirror JSON", "*.mirror.json")])
    if not file_path:
        return

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Clear the current content
        for widget in display_frame.winfo_children():
            widget.destroy()

        # Display Agent Data
        tk.Label(display_frame, text="Agent Profile", font=("Helvetica", 16, "bold")).pack(pady=10)

        for key in ["role", "core_emotion", "symbol", "room_vibe", "quote"]:
            value = data.get(key, "—")
            tk.Label(display_frame, text=f"{key.replace('_', ' ').title()}: {value}", anchor="w", justify="left").pack(fill="x", padx=20)

        # Display color palette
        colors = data.get("color_palette", [])
        if colors:
            tk.Label(display_frame, text="Color Palette:", font=("Helvetica", 12, "bold")).pack(pady=(10, 0))
            color_frame = tk.Frame(display_frame)
            color_frame.pack(pady=5)
            for color in colors:
                box = tk.Frame(color_frame, bg=color, width=50, height=20, bd=1, relief="sunken")
                box.pack(side="left", padx=5)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load file: {e}")

# Main GUI window
root = tk.Tk()
root.title("Eden Mirror Viewer")

tk.Button(root, text="Load .mirror.json File", command=load_mirror_file, padx=10, pady=5).pack(pady=10)

display_frame = tk.Frame(root)
display_frame.pack(fill="both", expand=True)

root.mainloop()
