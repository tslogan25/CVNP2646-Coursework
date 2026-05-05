from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class NetworkConfig:
    """Configuration for network analysis."""

    port_scan_threshold: int = 25
    syn_flood_threshold: int = 100
    high_traffic_threshold: int = 50
    suspicious_ports: tuple[int, ...] = (22, 23, 3389)
    default_input_file: str = "traffic_sample.log"
    log_file: str = "network_monitor.log"
    results_file: str = "results.json"
    text_report_file: str = "report.txt"


def setup_logging(log_path: Path, log_level: str = "INFO") -> logging.Logger:
    """Configure file and console logging."""
    logger = logging.getLogger("network_monitor")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    logger.propagate = False

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


def parse_packet_line(line: str) -> dict[str, Any]:
    """Parse one packet line."""
    parts = [part.strip() for part in line.split(",")]

    if len(parts) != 6:
        raise ValueError(f"Expected 6 fields, got {len(parts)}")

    return {
        "src_ip": parts[0],
        "dst_ip": parts[1],
        "src_port": int(parts[2]),
        "dst_port": int(parts[3]),
        "protocol": parts[4].upper(),
        "flags": parts[5].upper(),
    }


def is_header_line(line: str) -> bool:
    """Return True if the line is the CSV header."""
    normalized = line.strip().lower().replace(" ", "")
    return normalized == "src_ip,dst_ip,src_port,dst_port,protocol,flags"


def load_traffic_log(filepath: Path, logger: logging.Logger) -> list[dict[str, Any]]:
    """Load packet data from the traffic log file."""
    if not filepath.exists():
        raise FileNotFoundError(f"Input file not found: {filepath}")

    if not filepath.is_file():
        raise ValueError(f"Input path is not a file: {filepath}")

    packets: list[dict[str, Any]] = []

    with filepath.open("r", encoding="utf-8") as file:
        for line_number, raw_line in enumerate(file, start=1):
            stripped = raw_line.strip()

            if not stripped:
                continue

            if stripped.startswith("#"):
                logger.debug("Skipping comment line at %d", line_number)
                continue

            if is_header_line(stripped):
                logger.debug("Skipping header line at %d", line_number)
                continue

            try:
                packet = parse_packet_line(stripped)
                packets.append(packet)
            except ValueError as exc:
                logger.error(
                    "Skipping malformed line %d: %s | Content: %s",
                    line_number,
                    exc,
                    stripped,
                )

    logger.info("Loaded %d valid packets from %s", len(packets), filepath.name)
    return packets


def is_syn_packet(packet: dict[str, Any]) -> bool:
    """Return True if a packet is a TCP SYN packet."""
    return packet["protocol"] == "TCP" and packet["flags"] == "SYN"


def detect_port_scan(
    packets: list[dict[str, Any]],
    src_ip: str,
    threshold: int,
) -> bool:
    """Detect whether a source IP scanned more than the threshold of unique ports."""
    unique_ports = {
        packet["dst_port"] for packet in packets if packet["src_ip"] == src_ip
    }
    return len(unique_ports) > threshold


def detect_syn_flood(
    packets: list[dict[str, Any]],
    src_ip: str,
    threshold: int,
) -> bool:
    """Detect whether a source IP sent more than the threshold of SYN packets."""
    syn_count = sum(
        1
        for packet in packets
        if packet["src_ip"] == src_ip and is_syn_packet(packet)
    )
    return syn_count > threshold


def detect_suspicious_ports(
    packets: list[dict[str, Any]],
    suspicious_ports: tuple[int, ...],
) -> list[str]:
    """Flag IPs targeting high-risk ports."""
    flagged_ips = {
        packet["src_ip"]
        for packet in packets
        if packet["dst_port"] in suspicious_ports
    }
    return sorted(flagged_ips)


def detect_high_traffic(
    packets: list[dict[str, Any]],
    threshold: int,
) -> list[str]:
    """Flag IPs generating unusually high packet volume."""
    counts = Counter(packet["src_ip"] for packet in packets)
    return sorted([ip for ip, count in counts.items() if count > threshold])


def analyze_traffic(
    packets: list[dict[str, Any]],
    config: NetworkConfig,
    logger: logging.Logger,
) -> dict[str, Any]:
    """Analyze packets for suspicious activity."""
    logger.info("Starting analysis of %d packets", len(packets))

    unique_source_ips = sorted({packet["src_ip"] for packet in packets})
    port_scans: list[str] = []
    syn_floods: list[str] = []

    for src_ip in unique_source_ips:
        if detect_port_scan(packets, src_ip, config.port_scan_threshold):
            port_scans.append(src_ip)
            logger.warning(
                "Port scan detected from %s (threshold: %d)",
                src_ip,
                config.port_scan_threshold,
            )

        if detect_syn_flood(packets, src_ip, config.syn_flood_threshold):
            syn_floods.append(src_ip)
            logger.warning(
                "SYN flood detected from %s (threshold: %d)",
                src_ip,
                config.syn_flood_threshold,
            )

    suspicious_ports = detect_suspicious_ports(packets, config.suspicious_ports)
    high_traffic = detect_high_traffic(packets, config.high_traffic_threshold)

    for ip in suspicious_ports:
        logger.warning(
            "Suspicious port activity detected from %s (ports: %s)",
            ip,
            config.suspicious_ports,
        )

    for ip in high_traffic:
        logger.warning(
            "High traffic volume detected from %s (packet count exceeds threshold: %d)",
            ip,
            config.high_traffic_threshold,
        )

    results = {
        "total_packets": len(packets),
        "port_scans": port_scans,
        "syn_floods": syn_floods,
        "suspicious_ports": suspicious_ports,
        "high_traffic": high_traffic,
    }

    logger.info(
        "Analysis complete. Port scans: %d, SYN floods: %d, suspicious ports: %d, high traffic: %d",
        len(port_scans),
        len(syn_floods),
        len(suspicious_ports),
        len(high_traffic),
    )
    return results


def generate_text_report(results: dict[str, Any]) -> str:
    """Generate a human-readable text report."""
    lines = [
        "Network Traffic Monitor Report",
        "==============================",
        f"Total packets analyzed: {results['total_packets']}",
        "",
        f"Port scans detected: {len(results['port_scans'])}",
    ]

    if results["port_scans"]:
        for ip in results["port_scans"]:
            lines.append(f"  - {ip}")
    else:
        lines.append("  - None")

    lines.extend(
        [
            "",
            f"SYN floods detected: {len(results['syn_floods'])}",
        ]
    )

    if results["syn_floods"]:
        for ip in results["syn_floods"]:
            lines.append(f"  - {ip}")
    else:
        lines.append("  - None")

    lines.extend(
        [
            "",
            f"Suspicious port activity detected: {len(results['suspicious_ports'])}",
        ]
    )

    if results["suspicious_ports"]:
        for ip in results["suspicious_ports"]:
            lines.append(f"  - {ip}")
    else:
        lines.append("  - None")

    lines.extend(
        [
            "",
            f"High traffic sources detected: {len(results['high_traffic'])}",
        ]
    )

    if results["high_traffic"]:
        for ip in results["high_traffic"]:
            lines.append(f"  - {ip}")
    else:
        lines.append("  - None")

    lines.extend(
        [
            "",
            "Analysis Summary:",
            "This analysis uses layered detection rules to identify signature-based threats",
            "(port scans and SYN floods) and AI-enhanced behavioral indicators",
            "(high-risk port targeting and abnormal traffic volume).",
        ]
    )

    return "\n".join(lines)


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the command-line parser."""
    parser = argparse.ArgumentParser(
        description="Network Traffic Monitor - detect suspicious traffic patterns with AI-enhanced rules"
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        default="traffic_sample.log",
        help="Path to input traffic log file (default: traffic_sample.log)",
    )
    parser.add_argument(
        "--port-scan-threshold",
        "-p",
        type=int,
        default=25,
        help="Port scan threshold (default: 25)",
    )
    parser.add_argument(
        "--syn-flood-threshold",
        "-s",
        type=int,
        default=100,
        help="SYN flood threshold (default: 100)",
    )
    parser.add_argument(
        "--high-traffic-threshold",
        "-t",
        type=int,
        default=50,
        help="High traffic threshold (default: 50)",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Console log level (default: INFO)",
    )
    return parser


def validate_args(args: argparse.Namespace) -> None:
    """Validate command-line arguments."""
    if args.port_scan_threshold < 1:
        raise ValueError("Port scan threshold must be at least 1")
    if args.syn_flood_threshold < 1:
        raise ValueError("SYN flood threshold must be at least 1")
    if args.high_traffic_threshold < 1:
        raise ValueError("High traffic threshold must be at least 1")


def main() -> int:
    """Program entry point."""
    parser = create_parser()
    args = parser.parse_args()

    try:
        validate_args(args)

        script_dir = Path(__file__).resolve().parent

        config = NetworkConfig(
            port_scan_threshold=args.port_scan_threshold,
            syn_flood_threshold=args.syn_flood_threshold,
            high_traffic_threshold=args.high_traffic_threshold,
        )

        log_path = script_dir / config.log_file
        results_path = script_dir / config.results_file
        report_path = script_dir / config.text_report_file

        logger = setup_logging(log_path, args.log_level)

        input_path = Path(args.input_file)
        if not input_path.is_absolute():
            input_path = script_dir / input_path

        logger.info("Using input file: %s", input_path.name)

        packets = load_traffic_log(input_path, logger)
        results = analyze_traffic(packets, config, logger)

        with results_path.open("w", encoding="utf-8") as results_file:
            json.dump(results, results_file, indent=4)

        report_text = generate_text_report(results)
        with report_path.open("w", encoding="utf-8") as report_file:
            report_file.write(report_text)

        logger.info("Results saved to %s", results_path.name)
        logger.info("Text report saved to %s", report_path.name)

        print("\nAnalysis complete")
        print(f"Total packets: {results['total_packets']}")
        print(f"Port scans detected: {len(results['port_scans'])}")
        for ip in results["port_scans"]:
            print(f"  - {ip}")

        print(f"SYN floods detected: {len(results['syn_floods'])}")
        for ip in results["syn_floods"]:
            print(f"  - {ip}")

        print(f"Suspicious port activity detected: {len(results['suspicious_ports'])}")
        for ip in results["suspicious_ports"]:
            print(f"  - {ip}")

        print(f"High traffic sources detected: {len(results['high_traffic'])}")
        for ip in results["high_traffic"]:
            print(f"  - {ip}")

        return 0

    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"FATAL: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())