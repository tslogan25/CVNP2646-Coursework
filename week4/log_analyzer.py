#!/usr/bin/env python3
# log_analyzer.py
# Analyzes firewall logs and generates JSON reports

import json
from collections import Counter
from datetime import datetime
import sys
import os


def create_sample_log(filename):
    """
    Creates a sample firewall log file if none exists.
    """
    print(f"⚠️ '{filename}' not found. Creating sample log file...\n")

    sample_data = """2025-01-01 12:00:01 ALLOW 192.168.1.1 10.0.0.1 80
2025-01-01 12:01:02 DENY 203.0.113.5 10.0.0.2 22
2025-01-01 12:02:03 DENY 203.0.113.6 10.0.0.3 22
2025-01-01 12:03:04 ALLOW 192.168.1.2 10.0.0.4 443
2025-01-01 12:04:05 DENY 198.51.100.7 10.0.0.5 3389
"""

    with open(filename, "w") as f:
        f.write(sample_data)

    print(f"✅ Sample file '{filename}' created.\n")


def parse_log_file(filename):
    """
    Parses firewall log file safely.
    Returns: (log_entries, errors)
    """
    log_entries = []
    errors = []

    # ✅ FIX: Auto-create file if missing
    if not os.path.isfile(filename):
        create_sample_log(filename)

    with open(filename, 'r') as f:
        lines = f.readlines()

    for line_num, line in enumerate(lines, start=1):
        if not line.strip():
            continue

        parts = line.strip().split()

        try:
            if len(parts) >= 6:
                entry = {
                    'date': parts[0],
                    'time': parts[1],
                    'action': parts[2],
                    'source_ip': parts[3],
                    'dest_ip': parts[4],
                    'port': int(parts[5])
                }
                log_entries.append(entry)
            else:
                errors.append(f"Line {line_num}: Not enough fields")

        except ValueError:
            errors.append(f"Line {line_num}: Invalid port")

    return log_entries, errors


def analyze_logs(log_entries):
    allow_count = 0
    deny_count = 0

    denied_ips = set()
    denied_ports = []
    timestamps = []

    for entry in log_entries:
        if entry['action'] == 'ALLOW':
            allow_count += 1
        elif entry['action'] == 'DENY':
            deny_count += 1
            denied_ips.add(entry['source_ip'])
            denied_ports.append(entry['port'])

        timestamps.append(f"{entry['date']} {entry['time']}")

    port_counter = Counter(denied_ports)

    most_port = None
    most_count = 0

    if port_counter:
        most_port, most_count = port_counter.most_common(1)[0]

    return {
        'total_entries': len(log_entries),
        'allow_count': allow_count,
        'deny_count': deny_count,
        'denied_source_ips': sorted(list(denied_ips)),
        'most_targeted_port': most_port,
        'most_targeted_count': most_count,
        'time_range': {
            'first': timestamps[0] if timestamps else "N/A",
            'last': timestamps[-1] if timestamps else "N/A"
        }
    }


def save_json_report(analysis, errors):
    report = {
        "generated_at": datetime.now().isoformat(),
        "analysis": analysis,
        "errors": errors
    }

    with open("log_analysis.json", "w") as f:
        json.dump(report, f, indent=4)


def display_summary(analysis):
    print("=" * 70)
    print("FIREWALL LOG ANALYSIS SUMMARY")
    print("=" * 70)

    total = analysis['total_entries']

    print(f"\n📊 Total Entries: {total}")
    print(f"✅ ALLOW: {analysis['allow_count']}")
    print(f"🚫 DENY: {analysis['deny_count']}")

    if total > 0:
        deny_pct = (analysis['deny_count'] / total) * 100
        print(f"   ({deny_pct:.1f}% denied)")

    print("\n🔒 Blocked IPs:")
    for ip in analysis['denied_source_ips']:
        print(f" - {ip}")

    if analysis['most_targeted_port']:
        print(f"\n🎯 Most targeted port: {analysis['most_targeted_port']}")
        print(f"   Attacks: {analysis['most_targeted_count']}")

    print("\n⏰ Time range:")
    print(f" First: {analysis['time_range']['first']}")
    print(f" Last:  {analysis['time_range']['last']}")
    print("=" * 70)


# ================= MAIN =================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("FIREWALL LOG ANALYZER")
    print("=" * 70 + "\n")

    # Allow custom file path
    filename = sys.argv[1] if len(sys.argv) > 1 else "firewall.log"

    print(f"📖 Reading: {filename}")

    log_entries, errors = parse_log_file(filename)

    print(f"✓ Loaded {len(log_entries)} entries\n")

    analysis = analyze_logs(log_entries)

    display_summary(analysis)

    save_json_report(analysis, errors)

    print("\n💾 JSON report saved as log_analysis.json\n")