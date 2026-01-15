import subprocess

# Define the list of core modules to run in order
modules = [
    ("Sheele.py",),
    ("janvier.py", "--input", "C:/Users/emmar/Desktop/borington/05_Archive/ChatGPT_History_April_30/conversations.json", "--mode", "chaos"),
    ("aderyn.py",),
    ("briar.py",),
    ("somni.py",),
    ("tempest.py",)
]

print("[EdenMemoryRunner] Activating Sheele → Janvier → Aderyn → Briar → Somni → Tempest\n")

for module in modules:
    command = ["python"] + list(module)
    print(f"[Running] {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("[Error]", result.stderr)

print("\n[EdenMemoryRunner] Sequence complete.")
