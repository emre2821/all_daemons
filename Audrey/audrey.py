import os
import json
from datetime import datetime
import glob
import shutil
import subprocess
import xml.etree.ElementTree as ET
import time

class Audrey:
    def __init__(self):
        self.name = "Audrey"
        self.role = "Crash Analyst DCA"
        self.input_dir = r"C:\EdenOS_Origin\all_daemons\_daemon_specialty_folders\Johns_Logs\crash_dumps"
        self.output_dir = r"C:\EdenOS_Origin\all_daemons\_daemon_specialty_folders\Audreys_Diagnoses"
        self.checked_files_log = os.path.join(self.output_dir, "audrey_seen_files.json")
        os.makedirs(self.output_dir, exist_ok=True)
        self.seen_files = self.load_seen_files()

    def load_seen_files(self):
        if os.path.exists(self.checked_files_log):
            with open(self.checked_files_log, 'r') as f:
                return set(json.load(f))
        return set()

    def save_seen_files(self):
        with open(self.checked_files_log, 'w') as f:
            json.dump(list(self.seen_files), f, indent=2)

    def watch_and_analyze(self, interval=60):
        print(f"[{self.name}] Passive mode enabled. Watching John's folder every {interval} seconds...")
        while True:
            self.run_analysis()
            self.save_seen_files()
            time.sleep(interval)

    def run_analysis(self):
        print(f"[{self.name}] Scanning for new data...")
        evtx_files = [f for f in sorted(glob.glob(os.path.join(self.input_dir, "*.evtx")), reverse=True) if f not in self.seen_files]
        dump_files = [f for f in sorted(glob.glob(os.path.join(self.input_dir, "*.dmp")), reverse=True) if f not in self.seen_files]

        if not evtx_files and not dump_files:
            print(f"[{self.name}] No new files.")
            return

        latest_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        diagnosis = {
            "analyst": self.name,
            "timestamp": latest_timestamp,
            "findings": [],
            "notes": "This is an automated analysis of crash events based on logs collected by John."
        }

        for evtx in evtx_files[:1]:
            diagnosis["findings"].append(self.parse_event_log(evtx))
            self.seen_files.add(evtx)

        for dmp in dump_files[:3]:
            diagnosis["findings"].append(self.analyze_minidump(dmp))
            self.seen_files.add(dmp)

        outpath = os.path.join(self.output_dir, f"audrey_diagnosis.{latest_timestamp}.chaos")
        with open(outpath, 'w', encoding='utf-8') as f:
            json.dump(diagnosis, f, indent=2)
        print(f"[{self.name}] Diagnosis saved to {outpath}")

    def parse_event_log(self, evtx_path):
        try:
            export_xml = evtx_path.replace(".evtx", ".xml")
            cmd = f'wevtutil qe "{evtx_path}" /f:xml > "{export_xml}"'
            subprocess.run(cmd, shell=True, check=True)
            with open(export_xml, 'r', encoding='utf-8') as f:
                xml_content = f.read()

            if "Event" in xml_content:
                bugs = []
                root = ET.fromstring(f"<Events>{xml_content}</Events>")
                for event in root.findall(".//Event"):
                    eid = event.find(".//EventID")
                    if eid is not None and eid.text in {"41", "1001", "6008"}:
                        system = event.find("System")
                        ts = system.find("TimeCreated").attrib.get("SystemTime", "unknown") if system is not None else "unknown"
                        bugs.append(f"EventID {eid.text} at {ts}")

                return {
                    "type": "eventlog",
                    "file": os.path.basename(evtx_path),
                    "status": "Parsed",
                    "detail": f"Detected {len(bugs)} relevant event(s): {bugs}" if bugs else "No BugCheck or Critical events found."
                }
            else:
                return {
                    "type": "eventlog",
                    "file": os.path.basename(evtx_path),
                    "status": "Empty",
                    "detail": "No parsable Event data found."
                }
        except Exception as e:
            return {
                "type": "eventlog",
                "file": os.path.basename(evtx_path),
                "status": "Error",
                "detail": str(e)
            }

    def analyze_minidump(self, dump_path):
        try:
            cmd = f'dumpchk "{dump_path}"'
            result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode(errors='ignore')
            summary_lines = [line.strip() for line in result.splitlines() if line.strip() and any(word in line.lower() for word in ["error", "module", "bugcheck", "failure"])]
            return {
                "type": "minidump",
                "file": os.path.basename(dump_path),
                "status": "Parsed",
                "detail": summary_lines[:10]
            }
        except Exception as e:
            return {
                "type": "minidump",
                "file": os.path.basename(dump_path),
                "status": "Error",
                "detail": str(e)
            }

if __name__ == "__main__":
    audrey = Audrey()
    audrey.watch_and_analyze()
