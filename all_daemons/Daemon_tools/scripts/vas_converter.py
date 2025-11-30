# vas_converter.py
import json
from datetime import datetime

def convert_vas(input_path, output_path):
    data = {}

    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            if ":" in line:
                key, value = line.split(":", 1)
                data[key.strip().lower()] = value.strip()

    data['timestamp'] = datetime.utcnow().isoformat() + 'Z'

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    print(f"[VAS Converter] Converted to structured format → {output_path}")
