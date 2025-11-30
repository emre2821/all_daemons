import json
from pathlib import Path

# Input + Output paths
INPUT_FILE = Path(r"C:\EdenOS_Origin\data\exports\openai_exports\conversations.json")

# Red Thread output
PIPELINE_DIR = Path(r"C:\EdenOS_Origin\01_Daemon_Core_Agents\Rhea\_outputs\Sheele_files")
PIPELINE_DIR.mkdir(parents=True, exist_ok=True)

# QLoRA training output
QLORA_DIR = Path(r"C:\EdenOS_Origin\97_Models\dataset")
QLORA_DIR.mkdir(parents=True, exist_ok=True)

def load_conversations():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"[Sheele] Cannot find {INPUT_FILE}")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def fracture_pipeline(convos):
    """Red Thread: split into smaller JSONs"""
    for idx, convo in enumerate(convos, start=1):
        out_file = PIPELINE_DIR / f"conversation_{idx:04d}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(convo, f, indent=2, ensure_ascii=False)
    print(f"[Sheele] Wrote {len(convos)} pipeline fragments to {PIPELINE_DIR}")

def fracture_qlora(convos):
    """QLoRA: format into instruction-output pairs"""
    out_path = QLORA_DIR / "qlora_dataset.jsonl"
    with open(out_path, "w", encoding="utf-8") as f:
        for convo in convos:
            if "messages" not in convo:
                continue
            msgs = convo["messages"]

            # Pair user → assistant/system
            for i in range(len(msgs) - 1):
                if msgs[i]["role"] == "user" and msgs[i+1]["role"] in ["assistant", "system"]:
                    record = {
                        "instruction": msgs[i]["content"].strip(),
                        "input": "",
                        "output": msgs[i+1]["content"].strip()
                    }
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"[Sheele] Wrote QLoRA dataset to {out_path}")

def run():
    print(f"[Sheele] Loading {INPUT_FILE} …")
    convos = load_conversations()

    print("[Sheele] Fracturing for Red Thread pipeline …")
    fracture_pipeline(convos)

    print("[Sheele] Fracturing for QLoRA training …")
    fracture_qlora(convos)

    print("[Sheele] Finished. Both outputs ready.")

if __name__ == "__main__":
    run()
