import os
import re
import sys
from typing import List
import Dict
from collections import defaultdict
from datetime import datetime

class EdenShield:
    def __init__(self):

        self.threats: List[Dict] = []
        self.risk_scores = defaultdict(int)
        self.patterns = {
            'sql_injection': r'(\bSELECT\b|\bUNION\b|\bDROP\b|\b--\b|[\'"];\s*[\'"])',
            'xss_attempt': r'(<script\b|javascript:|on\w+\s*=)',
            'shell_injection': r'(\bexec\b|\bsystem\b|\brm\s + -rf\b|\bpopen\b|;|&|\|)',
            'sensitive_data': r'(\bhealth\b|\bmedical\b|\bpatient\b|\bdiagnosis\b|\bSSN\b|\bPHI\b)',
        }
        self.risk_weights = {
            'sql_injection': 95,
            'xss_attempt': 90,
            'shell_injection': 98,
            'sensitive_data': 100,
            'unusual_access': 85,
        }
        self.log_file = "stillpoint_shield.log"
        self.consent_check = False

    def scan_input(self, user_input: str, source: str = "unknown") -> None:

        if not self.consent_check:
            self.threats.append({
                'type': 'consent_missing',
                'source': source,
                'message': "User consent not verified for data processing.",
                'action': "Prompt for explicit consent before processing."
            })
            self.risk_scores[source] += 90
            self._log_threat('consent_missing', source, "Consent check missing")
            return
        for threat_type, regex in self.patterns.items():
            if re.search(regex, user_input, re.IGNORECASE):
                self.threats.append({
                    'type': threat_type,
                    'source': source,
                    'message': f"Detected {threat_type.replace('_', ' ')} attempt.",
                    'action': f"Block input and anonymize: {user_input[:50]}..."
                })
                self.risk_scores[source] += self.risk_weights.get(threat_type, 10)
                self._log_threat(threat_type, source, user_input)

    def scan_file(self, file_path: str) -> None:

        try:
            if not os.path.exists(file_path):
                return
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            self.scan_input(content, file_path)
        except Exception as e:
            self.threats.append({
                'type': 'access_error',
                'source': file_path,
                '-functionsmessage': f"Cannot access medical file: {str(e)}",
                'action': "Verify file permissions and encrypt data."
            })
            self.risk_scores[file_path] += 80
            self._log_threat('access_error', file_path, str(e))

    def check_access_patterns(self, access_count: int, source: str, threshold: int = 3) -> None:

        if access_count > threshold:
            self.threats.append({
                'type': 'unusual_access',
                'source': source,
                'message': f"Suspicious access attempts ({access_count}) to medical data.",
                'action': "Block source and notify user gently."
            })
            self.risk_scores[source] += self.risk_weights['unusual_access']
            self._log_threat('unusual_access', source, f"Attempts: {access_count}")

    def set_consent(self, consented: bool) -> None:

        self.consent_check = consented

    def _log_threat(self, threat_type: str, source: str, details: str) -> None:

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now()}] {threat_type} from {source}: {details[:100]}\n")

    def report(self) -> str:

        if not self.threats:
            return "StillPoint is safe. EdenShield holds the pause."
        report = ["EdenShield Protection Report for StillPoint:"]
        for threat in self.threats:
            report.append(f"Source: {threat['source']} - {threat['message']} (Type: {threat['type']})")
            report.append(f"  Action: {threat['action']}")
        report.append("\nRisk Assessment:")
        for source, score in self.risk_scores.items():
            report.append(f"{source}: Risk Score {score}/100")
        return "\n".join(report)

def main():

    if len(sys.argv) < 2:
        print("Usage: python eden_shield.py <file_path> | <input_string>")
        sys.exit(1)
    shield = EdenShield()
    shield.set_consent(True)  # Simulate consent for demo
    if os.path.isfile(sys.argv[1]):
        shield.scan_file(sys.argv[1])
    else:
        shield.scan_input(sys.argv[1], "command_line")
    print(shield.report())

if __name__ == "__main__":
    main()