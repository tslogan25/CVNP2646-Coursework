import json
import os
from datetime import datetime
from collections import Counter

def load_inventory(filename):
    try:
        base_dir = os.path.dirname(__file__)
        filepath = os.path.join(base_dir, filename)

        with open(filepath, 'r', encoding='utf-8') as f:
            hosts = json.load(f)

        if not isinstance(hosts, list):
            raise ValueError("JSON root should be a list of hosts")

        if len(hosts) == 0:
            raise ValueError("Host inventory is empty")

        return hosts

    except Exception as e:
        print(f"Error loading inventory: {e}")
        return None


def calculate_days_since_patch(host):
    try:
        last_patch = datetime.strptime(
            host['last_patch_date'],
            '%Y-%m-%d'
        )

        delta = datetime.now() - last_patch
        return delta.days

    except Exception as e:
        print(f"Error processing host {host.get('hostname', 'unknown')}: {e}")
        return None


def filter_by_os(hosts, os_type):
    return [
        h for h in hosts
        if os_type.lower() in h.get('os', '').lower()
    ]


def filter_by_criticality(hosts, level):
    return [
        h for h in hosts
        if h.get('criticality') == level
    ]


def filter_by_environment(hosts, env):
    return [
        h for h in hosts
        if h.get('environment') == env
    ]


def calculate_risk_score(host):
    score = 0

    criticality_points = {
        'critical': 40,
        'high': 25,
        'medium': 10,
        'low': 5
    }
    score += criticality_points.get(host.get('criticality'), 0)

    days = host.get('days_since_patch', 0) or 0
    if days > 90:
        score += 30
    elif days > 60:
        score += 20
    elif days > 30:
        score += 10

    env_points = {
        'production': 15,
        'staging': 8,
        'development': 3
    }
    score += env_points.get(host.get('environment'), 0)

    tags = host.get('tags', [])
    if 'pci-scope' in tags:
        score += 10
    if 'hipaa' in tags:
        score += 10
    if 'internet-facing' in tags:
        score += 15

    return min(score, 100)


def get_risk_level(score):
    if score >= 70:
        return "critical"
    elif score >= 50:
        return "high"
    elif score >= 25:
        return "medium"
    else:
        return "low"


def get_high_risk_hosts(hosts, threshold=50):
    high_risk = [h for h in hosts if h.get('risk_score', 0) >= threshold]
    return sorted(high_risk, key=lambda h: h.get('risk_score', 0), reverse=True)


def generate_json_report(hosts, high_risk_hosts):
    risk_dist = Counter(h['risk_level'] for h in hosts)

    report = {
        "report_date": datetime.now().isoformat(),
        "report_type": "High Risk Host Assessment",
        "total_hosts": len(hosts),
        "total_high_risk": len(high_risk_hosts),
        "risk_distribution": {
            "critical": risk_dist.get('critical', 0),
            "high": risk_dist.get('high', 0),
            "medium": risk_dist.get('medium', 0),
            "low": risk_dist.get('low', 0)
        },
        "high_risk_hosts": [
            {
                "hostname": h.get('hostname'),
                "risk_score": h.get('risk_score'),
                "risk_level": h.get('risk_level'),
                "days_since_patch": h.get('days_since_patch'),
                "criticality": h.get('criticality'),
                "environment": h.get('environment'),
                "tags": h.get('tags', [])
            }
            for h in high_risk_hosts
        ]
    }

    return json.dumps(report, indent=2)


def generate_text_summary(hosts, high_risk_hosts):
    lines = []

    lines.append("=" * 60)
    lines.append("     WEEKLY PATCH COMPLIANCE SUMMARY REPORT")
    lines.append("=" * 60)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    lines.append("EXECUTIVE SUMMARY")
    lines.append("-" * 60)
    risk_dist = Counter(h['risk_level'] for h in hosts)
    critical_count = risk_dist.get('critical', 0)

    lines.append(f"Total Systems Analyzed:        {len(hosts)}")
    lines.append(
        f"High-Risk Systems Identified:  {len(high_risk_hosts)} "
        f"({len(high_risk_hosts) / len(hosts) * 100:.1f}%)"
    )
    lines.append(f"Critical Priority Systems:     {critical_count}")

    very_old = sum(1 for h in hosts if h.get('days_since_patch', 0) > 90)
    lines.append(f"Immediate Action Required:     {very_old} systems >90 days unpatched")
    lines.append("")

    lines.append("RISK DISTRIBUTION")
    lines.append("-" * 60)
    lines.append(f"Critical (>=70 points):        {risk_dist.get('critical', 0)} systems")
    lines.append(f"High (50-69 points):           {risk_dist.get('high', 0)} systems")
    lines.append(f"Medium (25-49 points):         {risk_dist.get('medium', 0)} systems")
    lines.append(f"Low (<25 points):              {risk_dist.get('low', 0)} systems")
    lines.append("")

    lines.append("TOP 5 HIGHEST RISK SYSTEMS")
    lines.append("-" * 60)
    for i, host in enumerate(high_risk_hosts[:5], 1):
        lines.append(
            f"{i}. {host['hostname']} "
            f"(Score: {host['risk_score']}, {host['risk_level'].title()})"
        )
        lines.append(
            f"   Last Patched: {host['days_since_patch']} days ago | "
            f"{host['environment'].title()} | "
            f"Tags: {', '.join(host.get('tags', []))}"
        )
        lines.append("")

    lines.append("RECOMMENDED ACTIONS")
    lines.append("-" * 60)
    lines.append("IMMEDIATE (Next 48 hours):")
    lines.append(f"- Patch {critical_count} critical-risk systems")
    lines.append("")

    lines.append("THIS WEEK (Next 7 days):")
    lines.append(
        f"- Schedule maintenance windows for {len(high_risk_hosts)} "
        f"high-risk production systems"
    )
    lines.append("")

    lines.append("COMPLIANCE NOTES")
    lines.append("-" * 60)
    pci_count = sum(
        1 for h in hosts
        if 'pci-scope' in h.get('tags', []) and h.get('days_since_patch', 0) > 30
    )
    if pci_count > 0:
        lines.append(f"PCI-DSS: {pci_count} systems in PCI scope require immediate attention")
    else:
        lines.append("PCI-DSS: No PCI-scoped systems currently exceed 30 days since patching")

    lines.append("=" * 60)

    return "\n".join(lines)


def generate_html_report(hosts, high_risk_hosts):
    risk_dist = Counter(h['risk_level'] for h in hosts)
    critical_count = risk_dist.get('critical', 0)
    very_old = sum(1 for h in hosts if h.get('days_since_patch', 0) > 90)
    pci_count = sum(
        1 for h in hosts
        if 'pci-scope' in h.get('tags', []) and h.get('days_since_patch', 0) > 30
    )

    rows = ""
    for host in high_risk_hosts:
        tags = ", ".join(host.get('tags', []))
        rows += f"""
        <tr>
            <td>{host.get('hostname', 'N/A')}</td>
            <td>{host.get('risk_score', 0)}</td>
            <td>{host.get('risk_level', 'N/A').title()}</td>
            <td>{host.get('days_since_patch', 'N/A')}</td>
            <td>{host.get('criticality', 'N/A').title()}</td>
            <td>{host.get('environment', 'N/A').title()}</td>
            <td>{tags}</td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Patch Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 30px;
            background-color: #f8f9fa;
            color: #222;
        }}
        h1, h2 {{
            color: #1f4e79;
        }}
        .summary {{
            background: white;
            padding: 15px;
            border: 1px solid #ccc;
            margin-bottom: 20px;
            border-radius: 6px;
        }}
        .summary p {{
            margin: 6px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
        }}
        th, td {{
            border: 1px solid #ccc;
            padding: 10px;
            text-align: left;
        }}
        th {{
            background-color: #1f4e79;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
    </style>
</head>
<body>
    <h1>Weekly Patch Compliance Report</h1>
    <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

    <div class="summary">
        <h2>Executive Summary</h2>
        <p><strong>Total Systems:</strong> {len(hosts)}</p>
        <p><strong>High-Risk Systems:</strong> {len(high_risk_hosts)} ({len(high_risk_hosts) / len(hosts) * 100:.1f}%)</p>
        <p><strong>Critical Priority Systems:</strong> {critical_count}</p>
        <p><strong>Immediate Action Required:</strong> {very_old} systems >90 days unpatched</p>
    </div>

    <div class="summary">
        <h2>Risk Distribution</h2>
        <p><strong>Critical:</strong> {risk_dist.get('critical', 0)}</p>
        <p><strong>High:</strong> {risk_dist.get('high', 0)}</p>
        <p><strong>Medium:</strong> {risk_dist.get('medium', 0)}</p>
        <p><strong>Low:</strong> {risk_dist.get('low', 0)}</p>
    </div>

    <div class="summary">
        <h2>Compliance Notes</h2>
        <p><strong>PCI-DSS:</strong> {
            f"{pci_count} systems in PCI scope require immediate attention"
            if pci_count > 0 else
            "No PCI-scoped systems currently exceed 30 days since patching"
        }</p>
    </div>

    <h2>High-Risk Hosts</h2>
    <table>
        <tr>
            <th>Hostname</th>
            <th>Risk Score</th>
            <th>Risk Level</th>
            <th>Days Since Patch</th>
            <th>Criticality</th>
            <th>Environment</th>
            <th>Tags</th>
        </tr>
        {rows}
    </table>
</body>
</html>
"""
    return html


hosts = load_inventory('host_inventory.json')

if hosts:
    print(f"Loaded {len(hosts)} hosts\n")

    for host in hosts:
        host['days_since_patch'] = calculate_days_since_patch(host)

    for host in hosts:
        host['risk_score'] = calculate_risk_score(host)
        host['risk_level'] = get_risk_level(host['risk_score'])

    risk_counts = Counter(h['risk_level'] for h in hosts)
    print(f"Risk distribution: {risk_counts}\n")

    high_risk = get_high_risk_hosts(hosts)

    print(f"High-risk hosts (>=50): {len(high_risk)}")
    for host in high_risk[:5]:
        print(
            f"  {host.get('hostname')}: "
            f"{host.get('risk_score')} "
            f"({host.get('risk_level')})"
        )

    base_dir = os.path.dirname(__file__)

    json_output = generate_json_report(hosts, high_risk)
    json_path = os.path.join(base_dir, 'high_risk_report.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        f.write(json_output)

    print(f"\nReport saved to: {json_path}")

    text_output = generate_text_summary(hosts, high_risk)
    text_path = os.path.join(base_dir, 'patch_summary.txt')
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write(text_output)

    print(f"Text summary saved to: {text_path}")

    html_output = generate_html_report(hosts, high_risk)
    html_path = os.path.join(base_dir, 'patch_report.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_output)

    print(f"HTML report saved to: {html_path}\n")
    print(text_output)