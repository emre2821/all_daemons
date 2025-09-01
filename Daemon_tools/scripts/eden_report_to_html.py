import os
from datetime import datetime

LOG_DIR = "chaos_logs"
EXPORT_FILE = "eden_log_report.html"

def load_logs():
    logs = {}
    for filename in os.listdir(LOG_DIR):
        if filename.endswith(".chaos"):
            with open(os.path.join(LOG_DIR, filename), "r", encoding="utf-8") as f:
                logs[filename] = f.read()
    return logs

def extract_data(logs):
    entries = []
    activity = {}

    for fname, content in logs.items():
        lines = content.splitlines()
        agent = next((l.split(": ")[1] for l in lines if l.startswith("[AGENT]")), "Unknown")
        report = next((l[9:] for l in lines if l.startswith("[REPORT]")), "(No report)")
        entries.append((agent, report, fname))

        activity[agent] = activity.get(agent, 0) + 1

    return entries, activity

def build_html(entries, activity):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Eden CHAOS Log Report</title>
<style>
    body {{ font-family: 'Segoe UI', sans-serif; background: #1e1e2f; color: #eee; padding: 2em; }}
    h1 {{ color: #ffc6ff; }}
    .entry {{ border-bottom: 1px solid #444; margin-bottom: 1em; padding-bottom: 1em; }}
    .agent {{ color: #7fffd4; font-weight: bold; }}
    .report {{ color: #fceaff; margin-left: 1em; }}
    .activity-chart div {{ background: #ff9de2; height: 20px; margin: 3px 0; color: #111; padding-left: 5px; }}
</style>
</head>
<body>
    <h1>🪐 Eden CHAOS Log Report</h1>
    <p>Generated: {timestamp}</p>

    <h2>📊 Agent Activity Summary</h2>
    <div class="activity-chart">
"""
    for agent, count in sorted(activity.items(), key=lambda x: -x[1]):
        html += f"<div style='width:{count*20}px'>{agent} ({count})</div>\n"

    html += "</div><h2>📝 Log Entries</h2>\n"

    for agent, report, fname in entries:
        html += f"""<div class="entry">
            <div class="agent">{agent}</div>
            <div class="report">{report}</div>
            <div class="filename"><small>{fname}</small></div>
        </div>\n"""

    html += "</body></html>"
    return html

def save_html(html):
    with open(EXPORT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"📁 HTML report saved to: {EXPORT_FILE}")

if __name__ == "__main__":
    logs = load_logs()
    entries, activity = extract_data(logs)
    html = build_html(entries, activity)
    save_html(html)
