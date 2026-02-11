#!/usr/bin/env python3
# threat_parser.py
# Parses JSON threat intelligence data and generates security reports

import json
import os
from datetime import datetime


def load_threat_data(filename):
    """
    Loads threat intelligence data from JSON file.
    """
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find file: {filename}")
        print("Make sure threats.json is in the same directory as this script.")
        exit(1)
    except json.JSONDecodeError:
        print("Error: Invalid JSON format.")
        exit(1)


def analyze_threats(threat_data):
    """
    Analyzes threat data and generates statistics.
    """
    threats = threat_data.get('threats', [])

    severity_counts = {}
    all_ips = set()
    active_exploits = []

    for threat in threats:
        # Severity counting (safe)
        severity = threat.get('severity', 'UNKNOWN')
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

        # Extract IPs safely
        ips = threat.get('indicators', {}).get('ips', [])
        all_ips.update(ips)

        # Active exploits
        if threat.get('active_exploit', False):
            active_exploits.append({
                'id': threat.get('id', 'N/A'),
                'type': threat.get('type', 'N/A'),
                'description': threat.get('description', 'No description')
            })

    total_threats = len(threats)

    critical_percentage = (
        (severity_counts.get('CRITICAL', 0) / total_threats) * 100
        if total_threats > 0 else 0
    )

    return {
        'total_threats': total_threats,
        'severity_counts': severity_counts,
        'unique_ips': sorted(all_ips),
        'total_ips': len(all_ips),
        'active_exploits': active_exploits,
        'critical_percentage': critical_percentage
    }


def generate_report(threat_data, analysis, output_file):
    """
    Generates a formatted text report and saves to file.
    """
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
    report_lines.append(f"Total Unique Malicious IPs: {analysis['total_ips']}")
    report_lines.append(f"Active Exploits: {len(analysis['active_exploits'])}")
    report_lines.append("")

    report_lines.append("-" * 70)
    report_lines.append("SEVERITY BREAKDOWN")
    report_lines.append("-" * 70)

    severity_order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'UNKNOWN']

    for severity in severity_order:
        count = analysis['severity_counts'].get(severity, 0)
        if count > 0:
            report_lines.append(f"{severity:10}: {count} threats")

    report_lines.append(f"\nCRITICAL threats: {analysis['critical_percentage']:.1f}%")
    report_lines.append("")

    report_lines.append("-" * 70)
    report_lines.append("MALICIOUS IP ADDRESSES")
    report_lines.append("-" * 70)

    for ip in analysis['unique_ips']:
        report_lines.append(f"  - {ip}")

    report_lines.append("")

    report_lines.append("-" * 70)
    report_lines.append("ACTIVE EXPLOITS (IMMEDIATE ATTENTION REQUIRED)")
    report_lines.append("-" * 70)

    for exploit in analysis['active_exploits']:
        report_lines.append(f"\n{exploit['id']} ({exploit['type'].upper()})")
        report_lines.append(f"  Description: {exploit['description']}")

    report_lines.append("")
    report_lines.append("=" * 70)
    report_lines.append("END OF REPORT")
    report_lines.append("=" * 70)

    with open(output_file, 'w') as f:
        f.write('\n'.join(report_lines))

    return report_lines


# Main program
if __name__ == "__main__":
    print("=" * 70)
    print("THREAT INTELLIGENCE PARSER")
    print("=" * 70)
    print()

    # Get path of current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, 'threats.json')

    print("📖 Loading threat data...")
    threat_data = load_threat_data(json_path)
    print(f"✓ Loaded {len(threat_data.get('threats', []))} threats")
    print()

    print("🔍 Analyzing threat intelligence...")
    analysis = analyze_threats(threat_data)
    print("✓ Analysis complete")
    print()

    print("📝 Generating security report...")
    report_path = os.path.join(script_dir, 'threat_report.txt')
    report_lines = generate_report(threat_data, analysis, report_path)
    print(f"✓ Report saved to {report_path}")
    print()

    print("=" * 70)
    print("REPORT PREVIEW")
    print("=" * 70)
    for line in report_lines:
        print(line)
