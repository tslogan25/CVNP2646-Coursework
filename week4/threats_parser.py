#!/usr/bin/env python3
# threat_parser.py

import json
from datetime import datetime
import sys
import os


def load_threat_data(filename):
    """
    Loads threat intelligence data from JSON file.
    """

    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # If user provided full path, use it
    if os.path.isabs(filename):
        filepath = filename
    else:
        # Try file in script directory
        filepath = os.path.join(script_dir, filename)

    # Check if file exists
    if not os.path.exists(filepath):
        print("=" * 70)
        print("ERROR: FILE NOT FOUND")
        print("=" * 70)
        print(f"Tried to open:\n{filepath}\n")

        print("Fix this by:")
        print("1. Make sure 'threats.json' is in the SAME folder as this script")
        print("2. OR run with full path:")
        print("   python threat_parser.py C:\\full\\path\\to\\threats.json")

        print("\nCurrent script location:")
        print(script_dir)

        print("=" * 70)
        sys.exit(1)

    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("ERROR: Invalid JSON format.")
        sys.exit(1)


def analyze_threats(threat_data):
    threats = threat_data.get('threats', [])

    severity_counts = {
        'CRITICAL': 0,
        'HIGH': 0,
        'MEDIUM': 0,
        'LOW': 0
    }

    all_ips = []
    active_exploits = []

    for threat in threats:
        severity = threat.get('severity', 'LOW').upper()

        if severity not in severity_counts:
            severity_counts[severity] = 0

        severity_counts[severity] += 1

        ips = threat.get('indicators', {}).get('ips', [])
        if isinstance(ips, list):
            all_ips.extend(ips)

        if threat.get('active_exploit', False):
            active_exploits.append({
                'id': threat.get('id', 'UNKNOWN'),
                'type': threat.get('type', 'unknown'),
                'description': threat.get('description', 'No description')
            })

    total_threats = len(threats)

    critical_percentage = (
        (severity_counts['CRITICAL'] / total_threats) * 100
        if total_threats > 0 else 0
    )

    return {
        'total_threats': total_threats,
        'severity_counts': severity_counts,
        'unique_ips': list(set(all_ips)),
        'total_ips': len(all_ips),
        'active_exploits': active_exploits,
        'critical_percentage': critical_percentage
    }


def generate_report(threat_data, analysis, output_file):
    report_lines = []

    report_lines.append("=" * 70)
    report_lines.append("THREAT INTELLIGENCE ANALYSIS REPORT")
    report_lines.append("=" * 70)
    report_lines.append(f"Feed: {threat_data.get('feed_name', 'Unknown')}")
    report_lines.append(f"Date: {threat_data.get('date', 'Unknown')}")
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")

    report_lines.append("-" * 70)
    report_lines.append("SUMMARY STATISTICS")
    report_lines.append("-" * 70)
    report_lines.append(f"Total Threats: {analysis['total_threats']}")
    report_lines.append(f"Total Malicious IPs: {analysis['total_ips']}")
    report_lines.append(f"Unique IPs: {len(analysis['unique_ips'])}")
    report_lines.append(f"Active Exploits: {len(analysis['active_exploits'])}")
    report_lines.append("")

    report_lines.append("-" * 70)
    report_lines.append("SEVERITY BREAKDOWN")
    report_lines.append("-" * 70)

    total = analysis['total_threats']
    for severity, count in analysis['severity_counts'].items():
        percent = (count / total * 100) if total > 0 else 0
        report_lines.append(f"{severity:10}: {count} threats ({percent:.1f}%)")

    report_lines.append("")

    report_lines.append("-" * 70)
    report_lines.append("MALICIOUS IP ADDRESSES")
    report_lines.append("-" * 70)
    for ip in sorted(analysis['unique_ips']):
        report_lines.append(f"  - {ip}")

    report_lines.append("")

    report_lines.append("-" * 70)
    report_lines.append("ACTIVE EXPLOITS")
    report_lines.append("-" * 70)

    if analysis['active_exploits']:
        for exploit in analysis['active_exploits']:
            report_lines.append(f"\n{exploit['id']} ({exploit['type'].upper()})")
            report_lines.append(f"  Description: {exploit['description']}")
    else:
        report_lines.append("None found.")

    report_lines.append("")
    report_lines.append("=" * 70)
    report_lines.append("END OF REPORT")
    report_lines.append("=" * 70)

    # Save in script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, output_file)

    with open(output_path, 'w') as f:
        f.write('\n'.join(report_lines))

    return report_lines, output_path


def main():
    print("=" * 70)
    print("THREAT INTELLIGENCE PARSER")
    print("=" * 70)

    # Get filename from CLI or default
    filename = sys.argv[1] if len(sys.argv) > 1 else 'threats.json'

    print(f"\nLoading data from: {filename}")

    threat_data = load_threat_data(filename)

    print(f"Loaded {len(threat_data.get('threats', []))} threats")

    analysis = analyze_threats(threat_data)

    report_lines, output_path = generate_report(
        threat_data,
        analysis,
        'threat_report.txt'
    )

    print(f"\nReport saved to: {output_path}")

    print("\nPreview:")
    print("=" * 70)
    for line in report_lines[:20]:  # show first 20 lines
        print(line)


if __name__ == "__main__":
    main()