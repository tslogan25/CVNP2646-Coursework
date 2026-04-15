from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class NetworkConfig:
    """Configuration for network analysis."""

    port_scan_threshold: int = 25
    syn_flood_threshold: int = 100
    default_input_file: str = "traffic_sample.log"
    log_file: str = "network_monitor.log"
    results_file: str = "results.json"


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
    """
    Parse one packet line.

    Expected format:
    src_ip,dst_ip,src_port,dst_port,protocol,flags
    """
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
    """
    Load packet data from a traffic log file.

    Skips:
    - blank lines
    - comment lines starting with '#'
    - header line

    Logs and skips malformed rows.
    """
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

    results = {
        "total_packets": len(packets),
        "port_scans": port_scans,
        "syn_floods": syn_floods,
    }

    logger.info(
        "Analysis complete. Port scans: %d, SYN floods: %d",
        len(port_scans),
        len(syn_floods),
    )
    return results


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the command-line parser."""
    parser = argparse.ArgumentParser(
        description="Network Traffic Monitor - detect suspicious traffic patterns"
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
        )

        log_path = script_dir / config.log_file
        logger = setup_logging(log_path, args.log_level)

        input_path = Path(args.input_file)
        if not input_path.is_absolute():
            input_path = script_dir / input_path

        results_path = script_dir / config.results_file

        logger.info("Using input file: %s", input_path.name)

        packets = load_traffic_log(input_path, logger)
        results = analyze_traffic(packets, config, logger)

        with results_path.open("w", encoding="utf-8") as results_file:
            json.dump(results, results_file, indent=4)

        logger.info("Results saved to %s", results_path.name)

        print("\nAnalysis complete")
        print(f"Total packets: {results['total_packets']}")
        print(f"Port scans detected: {len(results['port_scans'])}")
        for ip in results["port_scans"]:
            print(f"  - {ip}")

        print(f"SYN floods detected: {len(results['syn_floods'])}")
        for ip in results["syn_floods"]:
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