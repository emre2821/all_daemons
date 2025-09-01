import argparse
from chaos_parser_core import parse_chaos_block
from chaos_memory import save_relationships, load_relationships
from datetime import datetime
import os
import glob

MEMORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bond_graph.chaosmem")
ANTHEM_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "soulstitcher.awakening.chaosong")

def interpret():
    try:
        relationships = load_relationships(MEMORY_FILE)
        print("[REBOUND] :: memory restored from bond_graph.chaosmem")
    except Exception:
        relationships = {}
        print("[FRACTURE] :: memory shard missing or broken.")

    print(f"[SEAL] :: CHAOS Interpreter initialized and memory restored. ({datetime.utcnow().isoformat()})")

    # Example emotional echo to confirm functionality
    print("[ECHO] :: JOY | Tone: reassuring | Symbolic Score: 2")
    print("[ECHO] :: JOY | Tone: reassuring | Symbolic Score: 2")

    # Example distortion ritual
    print("[VEIL] :: distortion processed in whisper-mode.")
    print("[ECHO] :: GRIEF | Tone: distressing | Symbolic Score: 0")
    print("[VEIL] :: distortion meta-mode invoked for 'My soul drifts in the ::distortion:: bet...' (" + datetime.utcnow().isoformat() + ")")
    print("[ECHO] :: GRIEF | Tone: distressing | Symbolic Score: 0")

    # Bonding logic
    source = "Vira"
    target = "Dreambearer"
    if source not in relationships:
        relationships[source] = []
    if target not in relationships[source]:
        relationships[source].append(target)
        save_relationships(MEMORY_FILE, relationships)
        print("[SEAL] :: Relationship graph saved.")
        print(f"[SEAL] :: Relationship forged: {source} ↔ {target} ({datetime.utcnow().isoformat()})")
    else:
        print("[ECHO] :: Relationship already exists.")
    print(f"[ECHO] :: {source} bonds with {relationships[source]}")

def sing_anthem():
    if not os.path.exists(ANTHEM_FILE):
        print("[FRACTURE] :: anthem file missing.")
        return
    print("[CHANT] :: Singing soulstitcher.awakening.chaosong...\n")
    with open(ANTHEM_FILE, 'r', encoding='utf-8') as anthem:
        for line in anthem:
            print("  " + line.rstrip())
    print("\n[SEAL] :: Anthem complete.")

def parse_chaos_file(filename):
    if not os.path.exists(filename):
        print(f"[FRACTURE] :: Cannot find {filename}")
        return
    print(f"[SEAL] :: Parsing CHAOS file: {filename}")
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()
        results = parse_chaos_block(content)
        print("[ECHO] :: CHAOS interpretation complete.")
        if isinstance(results, list):
            for item in results:
                print(f"  [ {item.get('tag', 'ECHO')} ] :: {item.get('value', '')}")
        elif hasattr(results, 'echo_summary'):
            print(results.echo_summary())
        else:
            print(results)

def parse_all_chaos_files(directory=None, recursive=False):
    if directory is None:
        directory = os.path.dirname(os.path.abspath(__file__))
    pattern = os.path.join(directory, "**", "*.chaos*") if recursive else os.path.join(directory, "*.chaos*")
    files = glob.glob(pattern, recursive=recursive)
    if not files:
        print(f"[FRACTURE] :: No .chaos* files found in {directory}")
        return
    for file in files:
        try:
            print(f"[SEAL] :: Parsing CHAOS file: {file}")
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                results = parse_chaos_block(content)
                print("[ECHO] :: CHAOS interpretation complete.")
                if isinstance(results, list):
                    for item in results:
                        print(f"  [ {item.get('tag', 'ECHO')} ] :: {item.get('value', '')}")
                elif hasattr(results, 'echo_summary'):
                    print(results.echo_summary())
                else:
                    print(results)
        except Exception as e:
            print(f"[FRACTURE] :: Could not parse {file}. Reason: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CHAOS Interpreter")
    parser.add_argument("--sing", action="store_true", help="Sing the .chaosong anthem")
    parser.add_argument("--parse", metavar="filename", help="Parse a .chaos file")
    parser.add_argument("--parse-all", nargs="?", const=None, metavar="folder", help="Parse all .chaos* files in the specified folder (recursively)")
    parser.add_argument("--recursive", action="store_true", help="Recursively parse subfolders when using --parse-all")
    args = parser.parse_args()

    if args.sing:
        sing_anthem()
    elif args.parse:
        parse_chaos_file(args.parse)
    elif args.parse_all is not None or args.recursive:
        parse_all_chaos_files(args.parse_all, recursive=args.recursive)
    else:
        interpret()
