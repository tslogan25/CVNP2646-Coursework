#!/usr/bin/env python3
# backup_planner.py

import json
import random
from pathlib import Path
from datetime import datetime


# ============================================================
# LOAD CONFIG
# ============================================================

def load_config(filename):
    script_dir = Path(__file__).parent
    file_path = script_dir / filename

    if not file_path.exists():
        print(f"❌ Error: '{filename}' not found in {script_dir}")
        return None

    try:
        content = file_path.read_text(encoding="utf-8").strip()

        if not content:
            print(f"❌ Error: '{filename}' is empty.")
            return None

        config = json.loads(content)

        if not isinstance(config, dict):
            print("❌ Error: JSON root must be an object.")
            return None

        return config

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON format in '{filename}': {e}")
        return None


# ============================================================
# VALIDATION
# ============================================================

def validate_config(config):

    errors = []

    if config is None:
        return False, ["Configuration could not be loaded."]

    required = ["plan_name", "sources", "destination"]

    for field in required:
        if field not in config:
            errors.append(f"Missing required field: '{field}'")

    if errors:
        return False, errors

    if not isinstance(config["sources"], list):
        errors.append("'sources' must be a list")

    if len(config["sources"]) == 0:
        errors.append("'sources' list must not be empty")

    for i, source in enumerate(config["sources"]):
        if "path" not in source:
            errors.append(f"Source {i}: missing 'path' field")

    if "base_path" not in config["destination"]:
        errors.append("Destination: missing 'base_path'")

    return (len(errors) == 0, errors)


# ============================================================
# SIMULATION ENGINE
# ============================================================

def generate_fake_filename(pattern=None):
    today = datetime.now().strftime("%Y-%m-%d")

    if pattern == "*.log":
        return f"firewall_{today}.log"
    elif pattern == "*.txt":
        return f"report_{random.randint(1,100)}.txt"
    elif pattern == "*.json":
        return f"events_{random.randint(1000,9999)}.json"
    else:
        ext = random.choice(["txt", "log", "json", "csv"])
        return f"file_{random.randint(100,999)}.{ext}"


def generate_backup_report(config):

    report = {
        "plan_name": config["plan_name"],
        "timestamp": datetime.now(),
        "sources": [],
        "total_sources": len(config["sources"]),
        "total_files": 0,
        "total_size_mb": 0.0
    }

    for source in config["sources"]:

        file_count = random.randint(5, 15)
        pattern = None

        if "include_patterns" in source and source["include_patterns"]:
            pattern = random.choice(source["include_patterns"])

        files = []
        total_size = 0.0

        for _ in range(file_count):
            size_mb = round(random.uniform(1.0, 100.0), 2)
            total_size += size_mb

            files.append({
                "filename": generate_fake_filename(pattern),
                "size_mb": size_mb
            })

        report["sources"].append({
            "path": source["path"],
            "files": files,
            "file_count": file_count,
            "total_size_mb": round(total_size, 2)
        })

        report["total_files"] += file_count
        report["total_size_mb"] += total_size

    report["total_size_mb"] = round(report["total_size_mb"], 2)

    return report


# ============================================================
# HUMAN-READABLE REPORT OUTPUT
# ============================================================

def format_human_readable_report(report):
    """Returns the human-readable report as a string instead of printing."""
    lines = []
    lines.append("=" * 70)
    lines.append(f"BACKUP PLAN: {report['plan_name']}")
    lines.append(f"Generated:   {report['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("MODE:        DRY-RUN (No files will be copied)")
    lines.append("=" * 70)

    lines.append("\nSUMMARY")
    lines.append("-" * 70)
    lines.append(f"{'Total Sources:':<20} {report['total_sources']:>10}")
    lines.append(f"{'Total Files:':<20} {report['total_files']:>10,}")
    lines.append(f"{'Total Size:':<20} {report['total_size_mb']:>10,.2f} MB")

    lines.append("\nDETAILS BY SOURCE")
    lines.append("-" * 70)

    for source in report["sources"]:
        lines.append(f"\nSource Path: {source['path']}")
        lines.append(f"{'Files:':<15} {source['file_count']:>10,}")
        lines.append(f"{'Total Size:':<15} {source['total_size_mb']:>10,.2f} MB")
        lines.append("\n  Sample Files:")

        sample_files = source["files"][:5]
        for file in sample_files:
            lines.append(f"   - {file['filename']:<40} {file['size_mb']:>8.2f} MB")

        if source["file_count"] > 5:
            remaining = source["file_count"] - 5
            lines.append(f"   ... and {remaining} more files")

    lines.append("\n" + "=" * 70)
    lines.append("DRY-RUN COMPLETE: No files were copied.")
    lines.append("=" * 70)

    return "\n".join(lines)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    config = load_config("backup_config.json")
    is_valid, errors = validate_config(config)

    if not is_valid:
        print("Valid?", is_valid)
        print("Errors:", errors)
    else:
        report = generate_backup_report(config)
        report_text = format_human_readable_report(report)

        # Print to console
        print(report_text)

        # Save to sample_report.txt
        report_file = Path("sample_report.txt")
        report_file.write_text(report_text, encoding="utf-8")
        print(f"\n✅ Dry-run report saved to '{report_file.resolve()}'")