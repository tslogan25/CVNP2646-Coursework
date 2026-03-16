#!/usr/bin/env python3
# threat_aggregator.py
# Stage 1-8: Load -> Normalize -> Validate -> Deduplicate -> Filter -> Export -> Statistics

import json
from pathlib import Path
from datetime import datetime
from collections import Counter


# ============================================================
# LOAD JSON FEED
# ============================================================

def load_feed(filename):
    script_dir = Path(__file__).parent
    file_path = script_dir / filename

    if not file_path.exists():
        print(f"❌ Error: '{filename}' not found in {script_dir}")
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ JSON format error in {filename}: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error in {filename}: {e}")
        return None


# ============================================================
# NORMALIZATION HELPERS
# ============================================================

def normalize_type(raw_type):
    type_map = {
        "ip": "ip",
        "ipv4": "ip",
        "domain": "domain",
        "domain_name": "domain",
        "fqdn": "domain",
        "hash": "hash",
        "sha256": "hash",
        "url": "url",
    }

    if raw_type is None:
        return None

    raw_type = str(raw_type).strip().lower()
    return type_map.get(raw_type, raw_type)


def normalize_confidence(raw_confidence):
    confidence_map = {
        "low": 25,
        "medium": 50,
        "high": 90,
        "critical": 100
    }

    if raw_confidence is None:
        return None

    if isinstance(raw_confidence, (int, float)):
        return int(raw_confidence)

    raw_confidence = str(raw_confidence).strip().lower()

    if raw_confidence.isdigit():
        return int(raw_confidence)

    return confidence_map.get(raw_confidence)


# ============================================================
# NORMALIZE INDICATORS
# ============================================================

def normalize_indicator(raw_indicator, source_name):
    raw_type = (
        raw_indicator.get("type")
        or raw_indicator.get("indicator_type")
        or raw_indicator.get("ioc_type")
    )

    raw_value = (
        raw_indicator.get("value")
        or raw_indicator.get("indicator_value")
        or raw_indicator.get("ioc")
    )

    raw_confidence = (
        raw_indicator.get("confidence")
        or raw_indicator.get("confidence_score")
        or raw_indicator.get("confidence_level")
    )

    raw_threat = (
        raw_indicator.get("threat")
        or raw_indicator.get("severity")
        or raw_indicator.get("severity_level")
    )

    normalized_value = raw_value.strip() if isinstance(raw_value, str) else raw_value

    return {
        "id": raw_indicator.get("id", f"{source_name}-{normalized_value}"),
        "type": normalize_type(raw_type),
        "value": normalized_value,
        "confidence": normalize_confidence(raw_confidence),
        "threat_level": raw_threat,
        "first_seen": raw_indicator.get("first_seen"),
        "sources": [source_name]
    }


# ============================================================
# VALIDATION
# ============================================================

def validate_indicators(indicators):
    valid = []
    errors = []

    valid_types = {"ip", "domain", "hash", "url"}
    required_fields = ["id", "type", "value", "confidence"]

    for idx, indicator in enumerate(indicators):
        missing_fields = []

        for field in required_fields:
            if field not in indicator or indicator[field] is None:
                missing_fields.append(field)

        if missing_fields:
            errors.append(
                f"Indicator {idx}: missing required field(s): {', '.join(missing_fields)}"
            )
            continue

        if indicator["type"] not in valid_types:
            errors.append(f"Indicator {idx}: invalid type '{indicator['type']}'")
            continue

        if not isinstance(indicator["value"], str) or not indicator["value"].strip():
            errors.append(f"Indicator {idx}: value must be a non-empty string")
            continue

        if not isinstance(indicator["confidence"], (int, float)):
            errors.append(f"Indicator {idx}: confidence not numeric")
            continue

        if not (0 <= indicator["confidence"] <= 100):
            errors.append(f"Indicator {idx}: confidence out of range")
            continue

        valid.append(indicator)

    return valid, len(errors), errors


# ============================================================
# DEDUPLICATION
# ============================================================

def deduplicate_indicators(indicators):
    unique = {}
    duplicate_count = 0

    for indicator in indicators:
        key = (indicator["type"], indicator["value"])

        if key not in unique:
            unique[key] = indicator.copy()
            unique[key]["sources"] = list(indicator.get("sources", []))
        else:
            duplicate_count += 1
            existing = unique[key]

            merged_sources = existing.get("sources", []) + indicator.get("sources", [])
            existing["sources"] = list(dict.fromkeys(merged_sources))

            if indicator["confidence"] > existing["confidence"]:
                replacement = indicator.copy()
                replacement["sources"] = existing["sources"]
                unique[key] = replacement

    return list(unique.values()), duplicate_count


# ============================================================
# FILTERING
# ============================================================

def filter_indicators(indicators, min_conf=85, levels=None, types=None):
    if levels is None:
        levels = ["high", "critical"]
    if types is None:
        types = ["ip", "domain"]

    return [
        ind for ind in indicators
        if ind["confidence"] >= min_conf
        and ind["threat_level"] in levels
        and ind["type"] in types
    ]


# ============================================================
# STATISTICS
# ============================================================

def generate_statistics(loaded, valid, deduped, filtered):
    type_counts = Counter(ind["type"] for ind in filtered)
    severity_counts = Counter(ind["threat_level"] for ind in filtered)

    source_counts = Counter()
    for ind in deduped:
        for source in ind["sources"]:
            source_counts[source] += 1

    return {
        "total_loaded": loaded,
        "valid_count": valid,
        "unique_count": len(deduped),
        "filtered_count": len(filtered),
        "duplicates_removed": loaded - len(deduped),
        "type_distribution": dict(type_counts),
        "severity_distribution": dict(severity_counts),
        "source_contribution": dict(source_counts)
    }


# ============================================================
# OUTPUT TRANSFORMS
# ============================================================

def transform_to_firewall(indicators, statistics):
    entries = []

    for ind in indicators:
        entry = {
            "address": ind["value"],
            "action": "block",
            "priority": "high" if ind["threat_level"] == "critical" else "medium",
            "reason": f"Threat level: {ind['threat_level']}, Confidence: {ind['confidence']}%",
            "sources": ind["sources"]
        }
        entries.append(entry)

    return {
        "generated_at": datetime.now().isoformat(),
        "total_entries": len(entries),
        "statistics": statistics,
        "blocklist": entries
    }


def transform_to_siem(indicators, statistics):
    events = []

    for ind in indicators:
        event = {
            "ioc_id": ind["id"],
            "ioc_type": ind["type"],
            "ioc_value": ind["value"],
            "risk_score": ind["confidence"],
            "severity": ind["threat_level"],
            "vendors": ind["sources"],
            "first_seen": ind["first_seen"],
            "recommended_action": (
                "alert_block_escalate"
                if ind["threat_level"] == "critical"
                else "alert_and_enrich"
            )
        }
        events.append(event)

    return {
        "generated_at": datetime.now().isoformat(),
        "event_count": len(events),
        "statistics": statistics,
        "indicators": events
    }


def build_text_report(
    all_indicators,
    valid_indicators,
    error_count,
    error_list,
    deduplicated_indicators,
    duplicate_count,
    filtered_indicators,
    statistics
):
    lines = []

    lines.append("=" * 70)
    lines.append("THREAT FEED AGGREGATOR REPORT")
    lines.append("=" * 70)
    lines.append(f"Generated: {datetime.now().isoformat()}")
    lines.append("")

    lines.append("SUMMARY")
    lines.append("-" * 70)
    lines.append(f"Total indicators loaded:           {len(all_indicators):>5,}")
    lines.append(f"Valid indicators:                  {len(valid_indicators):>5,}")
    lines.append(f"Validation errors:                 {error_count:>5,}")
    lines.append(f"Unique after deduplication:        {len(deduplicated_indicators):>5,}")
    lines.append(f"Duplicates removed:                {duplicate_count:>5,}")
    lines.append(f"Indicators after filtering:        {len(filtered_indicators):>5,}")
    lines.append("")

    lines.append("STATISTICS")
    lines.append("-" * 70)
    lines.append(f"Total loaded:                      {statistics['total_loaded']:>5,}")
    lines.append(f"Valid count:                       {statistics['valid_count']:>5,}")
    lines.append(f"Unique count:                      {statistics['unique_count']:>5,}")
    lines.append(f"Filtered count:                    {statistics['filtered_count']:>5,}")
    lines.append(f"Duplicates removed:                {statistics['duplicates_removed']:>5,}")
    lines.append("")

    lines.append("Type Distribution")
    for key, value in statistics["type_distribution"].items():
        lines.append(f"  {key:<20} {value:>5,}")
    if not statistics["type_distribution"]:
        lines.append("  None")
    lines.append("")

    lines.append("Severity Distribution")
    for key, value in statistics["severity_distribution"].items():
        lines.append(f"  {key:<20} {value:>5,}")
    if not statistics["severity_distribution"]:
        lines.append("  None")
    lines.append("")

    lines.append("Source Contribution")
    for key, value in statistics["source_contribution"].items():
        lines.append(f"  {key:<20} {value:>5,}")
    if not statistics["source_contribution"]:
        lines.append("  None")
    lines.append("")

    if error_list:
        lines.append("VALIDATION ERRORS")
        lines.append("-" * 70)
        for err in error_list:
            lines.append(f"- {err}")
        lines.append("")

    lines.append("FILTERED HIGH-PRIORITY INDICATORS")
    lines.append("-" * 70)

    if filtered_indicators:
        for idx, ind in enumerate(filtered_indicators, start=1):
            lines.append(f"{idx}. Type:       {ind['type']}")
            lines.append(f"   Value:      {ind['value']}")
            lines.append(f"   Confidence: {ind['confidence']}%")
            lines.append(f"   Threat:     {ind['threat_level']}")
            lines.append(f"   Sources:    {', '.join(ind['sources'])}")
            lines.append("")
    else:
        lines.append("No indicators matched the configured filters.")
        lines.append("")

    return "\n".join(lines)


# ============================================================
# SAVE OUTPUT FILES
# ============================================================

def save_json(filename, data):
    script_dir = Path(__file__).parent
    file_path = script_dir / filename

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return file_path


def save_text(filename, text):
    script_dir = Path(__file__).parent
    file_path = script_dir / filename

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)

    return file_path


# ============================================================
# MAIN
# ============================================================

def main():
    all_indicators = []

    # VendorA
    feed_a = load_feed("vendor_a.json")
    if feed_a:
        for indicator in feed_a.get("indicators", []):
            all_indicators.append(normalize_indicator(indicator, "VendorA"))

    # VendorB
    feed_b = load_feed("vendor_b.json")
    if feed_b:
        for indicator in feed_b.get("items", []):
            all_indicators.append(normalize_indicator(indicator, "VendorB"))

    # VendorC
    feed_c = load_feed("vendor_c.json")
    if feed_c:
        for indicator in feed_c.get("observables", []):
            all_indicators.append(normalize_indicator(indicator, "VendorC"))

    valid_indicators, error_count, error_list = validate_indicators(all_indicators)
    deduplicated_indicators, duplicate_count = deduplicate_indicators(valid_indicators)
    filtered_indicators = filter_indicators(deduplicated_indicators)

    statistics = generate_statistics(
        loaded=len(all_indicators),
        valid=len(valid_indicators),
        deduped=deduplicated_indicators,
        filtered=filtered_indicators
    )

    firewall_output = transform_to_firewall(filtered_indicators, statistics)
    siem_output = transform_to_siem(filtered_indicators, statistics)
    text_report = build_text_report(
        all_indicators,
        valid_indicators,
        error_count,
        error_list,
        deduplicated_indicators,
        duplicate_count,
        filtered_indicators,
        statistics
    )

    firewall_path = save_json("firewall_blocklist.json", firewall_output)
    siem_path = save_json("siem_indicators.json", siem_output)
    report_path = save_text("threat_report.txt", text_report)

    print("=" * 60)
    print("Threat Feed Aggregator")
    print("=" * 60)
    print(f"Total indicators loaded: {len(all_indicators)}")
    print(f"Valid indicators: {len(valid_indicators)}")
    print(f"Validation errors: {error_count}")
    print(f"Unique indicators after deduplication: {len(deduplicated_indicators)}")
    print(f"Duplicates removed: {duplicate_count}")
    print(f"Indicators after filtering: {len(filtered_indicators)}")

    print("\nStatistics:")
    print(f" - Type distribution: {statistics['type_distribution']}")
    print(f" - Severity distribution: {statistics['severity_distribution']}")
    print(f" - Source contribution: {statistics['source_contribution']}")

    if error_list:
        print("\nValidation Errors:")
        for err in error_list:
            print(f" - {err}")

    print("\nFiltered Indicators:")
    for ind in filtered_indicators:
        print(ind)

    print("\nOutput files created:")
    print(f" - {firewall_path.name}")
    print(f" - {siem_path.name}")
    print(f" - {report_path.name}")


if __name__ == "__main__":
    main()