#!/usr/bin/env python3
# security_log_analyzer.py

from collections import Counter
from datetime import datetime
import json
import sys
from pathlib import Path


# -------------------------
# Parse a single log line
# -------------------------
def parse_log_line(line):
    if not line or not line.strip():
        return None

    parts = line.split()

    if len(parts) < 3:
        return None

    date_part = parts[0]
    time_part = parts[1]

    if "-" not in date_part or ":" not in time_part:
        return None

    result = {"timestamp": f"{date_part} {time_part}"}

    for item in parts[2:]:
        if "=" not in item:
            continue

        key, value = item.split("=", 1)

        if key and value:
            result[key] = value

    return result


# -------------------------
# Process logs
# -------------------------
def process_logs(log_lines):
    user_counts = Counter()
    ip_counts = Counter()

    total_lines = 0
    parsed_lines = 0
    fail_count = 0

    for line in log_lines:
        total_lines += 1

        parsed = parse_log_line(line)
        if parsed is None:
            continue

        parsed_lines += 1

        if parsed.get("status") == "FAIL":
            fail_count += 1

            user = parsed.get("user")
            ip = parsed.get("ip")

            if user:
                user_counts[user] += 1

            if ip:
                ip_counts[ip] += 1

    return {
        "total_lines": total_lines,
        "parsed_lines": parsed_lines,
        "fail_count": fail_count,
        "user_counts": user_counts,
        "ip_counts": ip_counts
    }


# -------------------------
# Build JSON data
# -------------------------
def build_report_data(stats, analyst_name="Analyst"):
    total = stats["parsed_lines"]
    fails = stats["fail_count"]

    failure_rate = (fails / total * 100) if total > 0 else 0

    return {
        "metadata": {
            "generated_at": datetime.utcnow().isoformat(),
            "analyst": analyst_name
        },
        "summary": {
            "total_logs": stats["total_lines"],
            "parsed_logs": stats["parsed_lines"],
            "failed_logins": fails,
            "failure_rate_percent": round(failure_rate, 2)
        },
        "top_users": [
            {"user": u, "fail_count": c}
            for u, c in stats["user_counts"].most_common(5)
        ],
        "top_ips": [
            {"ip": ip, "fail_count": c}
            for ip, c in stats["ip_counts"].most_common(5)
        ]
    }


# -------------------------
# Human report
# -------------------------
def generate_human_report(stats, analyst_name="Analyst"):
    total_logs = stats["total_lines"]
    parsed_logs = stats["parsed_lines"]
    fail_count = stats["fail_count"]

    failure_rate = (fail_count / parsed_logs * 100) if parsed_logs > 0 else 0

    line = "=" * 70
    report = []

    report.append(line)
    report.append("SECURITY LOG ANALYSIS REPORT")
    report.append(line)

    report.append("METADATA")
    report.append(line)
    report.append(f"Analyst:           {analyst_name}")
    report.append(f"Generated At:      {datetime.utcnow().isoformat()}")
    report.append("")

    report.append("SUMMARY")
    report.append(line)
    report.append(f"Total Logs:        {total_logs:,}")
    report.append(f"Parsed Logs:       {parsed_logs:,}")
    report.append(f"Failed Logins:     {fail_count:,}")
    report.append(f"Failure Rate:      {failure_rate:.1f}%")
    report.append("")

    report.append("TOP TARGETED USERS")
    report.append(line)
    report.append(f"{'User':20} {'Failures':>10}")
    report.append("-" * 30)

    for user, count in stats["user_counts"].most_common(5):
        report.append(f"{user:20} {count:>10,}")

    report.append("")

    report.append("TOP ATTACKING IPS")
    report.append(line)
    report.append(f"{'IP Address':20} {'Failures':>10}")
    report.append("-" * 30)

    for ip, count in stats["ip_counts"].most_common(5):
        report.append(f"{ip:20} {count:>10,}")

    report.append("")
    report.append(line)

    return "\n".join(report)


# -------------------------
# Load log file safely
# -------------------------
def load_log_file(file_path):
    path = Path(file_path)

    if not path.exists():
        return None, path

    lines = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            lines.append(line.strip())

    return lines, path


# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":
    analyst_name = "Tanya"

    # 1. Get file path from command line OR default
    if len(sys.argv) > 1:
        log_file = sys.argv[1]
    else:
        # Default to script directory
        script_dir = Path(__file__).parent
        log_file = script_dir / "auth_test.log"

    # 2. Load file
    log_lines, path = load_log_file(log_file)

    if log_lines is None:
        print(f"❌ Error: Log file not found at:\n{path}")
        print("\n✔ Fix options:")
        print("1. Put auth_test.log in the same folder as the script")
        print("2. OR run with full path:")
        print("   python auth_scanner.py C:\\path\\to\\auth_test.log")
        sys.exit(1)

    print(f"✔ Loaded log file: {path}")

    # 3. Process logs
    stats = process_logs(log_lines)

    # 4. Build reports
    report_data = build_report_data(stats, analyst_name)
    text_report = generate_human_report(stats, analyst_name)

    # 5. Save reports
    output_dir = Path(path).parent

    json_file = output_dir / "incident_report.json"
    txt_file = output_dir / "incident_report.txt"

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    with open(txt_file, "w", encoding="utf-8") as f:
        f.write(text_report)

    print("\n✅ Reports generated:")
    print(f" - {json_file}")
    print(f" - {txt_file}")