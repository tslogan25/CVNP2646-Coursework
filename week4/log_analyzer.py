#!/usr/bin/env python3
# log_analyzer.py
# Analyzes firewall logs and generates JSON reports

import json
import sys
import os
from collections import Counter
from datetime import datetime


def create_sample_log(filename):
    """Creates a sample firewall.log if none exists."""
    sample_data = """2026-02-10 10:15:32 ALLOW 192.168.1.10 10.0.0.5 80
2026-02-10 10:16:01 DENY 203.0.113.5 10.0.0.5 22
2026-02-10 10:16:45 DENY 203.0.113.5 10.0.0.5 22
2026-02-10 10:17:12 ALLOW 192.168.1.15 10.0.0.5 443
2026-02-10 10:18:03 DENY 198.51.100.9 10.0.0.5 3389
"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(sample_data)


def parse_log_file(filename):
    log_entries = []

    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue

            parts = line.strip().split()

            if len(parts) >= 6:
                try:
                    entry = {
                        'date': parts[0],
                        'time': parts[1],
                        'action': parts[2].upper(),
                        'source_ip': parts[3],
                        'dest_ip': parts[4],
                        'port': int(parts[5])
                    }
                    log_entries.append(entry)
                except ValueError:
                    continue

    return log_entries


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

        try:
            dt = datetime.strptime(
                f"{entry['date']} {entry['time']}",
                "%Y-%m-%d %H:%M:%S"
            )
            timestamps.append(dt)
        except ValueError:
            continue

    port_counter = Counter(denied_ports)

    most_targeted_port = None
    most_targeted_count = 0

    if port_counter:
        most_targeted_port, most_targeted_count = port_counter.most_common(1)[0]

    timestamps.sort()

    first_timestamp = timestamps[0].strftime("%Y-%m-%d %H:%M:%S") if timestamps else "N/A"
    last_timestamp = timestamps[-1].strftime("%Y-%m-%d %H:%M:%S") if timestamps else "N/A"

    return {
        'total_entries': len(log_entries),
        'allow_count': allow_count,
        'deny_count': deny_count,
        'denied_source_ips': sorted(list(denied_ips)),
        'most_targeted_port': most_targeted_port,
        'most_targeted_count': most_targeted_count,
        'time_range': {
            'first': first_timestamp,
            'last': last_timestamp
        }
    }


def save_json_report(analysis, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2)


def display_summary(analysis):
    print("=" * 70)
    print("FIREWALL LOG ANALYSIS SUMMARY")
    print("=" * 70)
    print()

    print(f"Total Log Entries: {analysis['total_entries']}")
    print()
    print(f"ALLOW actions: {analysis['allow_count']}")
    print(f"DENY actions:  {analysis['deny_count']}")

    total = analysis['total_entries']
    deny_pct = (analysis['deny_count'] / total * 100) if total > 0 else 0
    print(f"({deny_pct:.1f}% of traffic was denied)")
    print()

    print(f"Unique denied source IPs: {len(analysis['denied_source_ips'])}")
    for ip in analysis['denied_source_ips']:
        print(f" - {ip}")
    print()

    if analysis['most_targeted_port']:
        print(f"Most targeted port: {analysis['most_targeted_port']}")
        print(f"Attacked {analysis['most_targeted_count']} times")
        print()

    print("Time range:")
    print(f"First entry: {analysis['time_range']['first']}")
    print(f"Last entry:  {analysis['time_range']['last']}")
    print("=" * 70)


if __name__ == "__main__":
    print()
    print("=" * 70)
    print("FIREWALL LOG ANALYZER")
    print("=" * 70)
    print()

    # Always look in the same directory as this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(script_dir, "firewall.log")

    # If file doesn't exist, create a sample one automatically
    if not os.path.exists(filename):
        print("firewall.log not found.")
        print("Creating a sample firewall.log for testing...\n")
        create_sample_log(filename)

    print(f"Reading {filename}...")
    log_entries = parse_log_file(filename)
    print(f"Parsed {len(log_entries)} log entries\n")

    print("Analyzing firewall traffic patterns...")
    analysis = analyze_logs(log_entries)
    print("Analysis complete\n")

    display_summary(analysis)

    print("\nSaving analysis to log_analysis.json...")
    save_json_report(analysis, os.path.join(script_dir, "log_analysis.json"))
    print("JSON report saved successfully\n")