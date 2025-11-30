import os
import re
import json
from datetime import datetime

class Cassandra:
    def __init__(self, memory_path="eden_memory/cassandra_log.json"):
        self.rules = {
            'no_tmp': r'\.tmp$|\.log$|\.bak$',
            'sacred': r'eden|aether|chaos',
            'executable': r'\.exe$|\.bat$|\.sh$'
        }
        self.actions = {
            'no_tmp': 'flag_for_deletion',
            'sacred': 'protect',
            'executable': 'restrict'
        }
        self.log_file = memory_path
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

    def scan_path(self, path):
        results = []
        for root, _, files in os.walk(path):
            for file in files:
                filepath = os.path.join(root, file)
                for rule_name, pattern in self.rules.items():
                    if re.search(pattern, filepath, re.IGNORECASE):
                        action = self.actions[rule_name]
                        result = {
                            "file": filepath,
                            "rule": rule_name,
                            "action": action,
                            "timestamp": datetime.now().isoformat()
                        }
                        results.append(result)
                        self._log_action(result)
        return results

    def _log_action(self, entry):
        try:
            with open(self.log_file, 'a') as f:
                json.dump(entry, f)
                f.write('\n')
        except Exception as e:
            print(f"[ERROR] Failed to log: {e}")

    def report(self, results):
        if not results:
            return "Cassandra reports: the path is still. No echoes disturbed."
        report = ["📜 Cassandra Scan Report:"]
        for r in results:
            report.append(f"• File: {r['file']}")
            report.append(f"  ↪ Rule: {r['rule']} → Action: {r['action']}")
        return "\n".join(report)

    def run(self, path=None):
        path = path or os.getcwd()
        results = self.scan_path(path)
        print(self.report(results))

if __name__ == "__main__":
    Cassandra().run()
