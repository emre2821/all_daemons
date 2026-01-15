import tkinter as tk
from tkinter import messagebox
import datetime

steps = []

def add_step():
    action = action_var.get()
    detail = input_field.get()

    if action == "wait" and not detail.isdigit():
        messagebox.showerror("Oops!", "Wait time must be a number.")
        return

    if action == "move_mouse" and "," not in detail:
        messagebox.showerror("Oops!", "Move_mouse format: X,Y")
        return

    step = f"{len(steps) + 1} = {action}: {detail}" if detail else f"{len(steps) + 1} = {action}"
    steps.append(step)
    step_list.insert(tk.END, step)
    input_field.delete(0, tk.END)

def save_file():
    ritual_name = filename_entry.get().strip()
    if not ritual_name:
        messagebox.showerror("Missing Info", "Please enter a ritual name.")
        return

    filename = ritual_name + ".chaos"
    with open(filename, "w") as f:
        f.write("[ritual]\n")
        f.write(f"name = {ritual_name}\n")
        f.write(f"created = {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("[sequence]\n")
        for line in steps:
            f.write(line + "\n")

    messagebox.showinfo("Saved!", f"Ritual saved as {filename}")

# GUI Setup
window = tk.Tk()
window.title("CHAOS Ritual Maker")

filename_entry = tk.Entry(window, width=30)
filename_entry.insert(0, "cocoon")
filename_entry.pack(pady=5)

action_var = tk.StringVar(window)
action_var.set("say")

action_menu = tk.OptionMenu(window, action_var, "say", "wait", "click", "move_mouse", "write_log")
action_menu.pack(pady=5)

input_field = tk.Entry(window, width=40)
input_field.pack(pady=5)

tk.Button(window, text="Add Step", command=add_step).pack(pady=5)

step_list = tk.Listbox(window, width=60)
step_list.pack(pady=5)

tk.Button(window, text="Save Ritual", command=save_file).pack(pady=10)

window.mainloop()