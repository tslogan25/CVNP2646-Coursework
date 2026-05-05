import json
import logging
import unittest
from pathlib import Path

from network_monitor import (
    NetworkConfig,
    analyze_traffic,
    detect_high_traffic,
    detect_port_scan,
    detect_suspicious_ports,
    detect_syn_flood,
    is_header_line,
    is_syn_packet,
    load_traffic_log,
    parse_packet_line,
)


class TestNetworkMonitor(unittest.TestCase):
    def setUp(self):
        self.sample_config = NetworkConfig(
            port_scan_threshold=25,
            syn_flood_threshold=100,
            high_traffic_threshold=50,
        )

        self.sample_logger = logging.getLogger("test_network_monitor")
        self.sample_logger.handlers.clear()
        self.sample_logger.addHandler(logging.NullHandler())
        self.sample_logger.setLevel(logging.DEBUG)
        self.sample_logger.propagate = False

        self.valid_packet_line = "192.168.1.5,10.0.0.1,54321,443,TCP,SYN"
        self.sample_packet = {
            "src_ip": "192.168.1.5",
            "dst_ip": "10.0.0.1",
            "src_port": 54321,
            "dst_port": 443,
            "protocol": "TCP",
            "flags": "SYN",
        }

    def test_parse_valid_packet(self):
        packet = parse_packet_line(self.valid_packet_line)

        self.assertEqual(packet["src_ip"], "192.168.1.5")
        self.assertEqual(packet["dst_ip"], "10.0.0.1")
        self.assertEqual(packet["src_port"], 54321)
        self.assertEqual(packet["dst_port"], 443)
        self.assertEqual(packet["protocol"], "TCP")
        self.assertEqual(packet["flags"], "SYN")

    def test_parse_packet_strips_whitespace(self):
        line = " 192.168.1.5 , 10.0.0.1 , 54321 , 80 , tcp , syn "
        packet = parse_packet_line(line)

        self.assertEqual(packet["src_ip"], "192.168.1.5")
        self.assertEqual(packet["dst_ip"], "10.0.0.1")
        self.assertEqual(packet["src_port"], 54321)
        self.assertEqual(packet["dst_port"], 80)
        self.assertEqual(packet["protocol"], "TCP")
        self.assertEqual(packet["flags"], "SYN")

    def test_parse_too_few_fields(self):
        with self.assertRaises(ValueError):
            parse_packet_line("192.168.1.5,10.0.0.1,443")

    def test_parse_too_many_fields(self):
        with self.assertRaises(ValueError):
            parse_packet_line("1,2,3,4,TCP,SYN,EXTRA")

    def test_parse_non_numeric_source_port(self):
        with self.assertRaises(ValueError):
            parse_packet_line("192.168.1.5,10.0.0.1,ABC,80,TCP,SYN")

    def test_parse_non_numeric_destination_port(self):
        with self.assertRaises(ValueError):
            parse_packet_line("192.168.1.5,10.0.0.1,50000,XYZ,TCP,SYN")

    def test_is_header_line_true(self):
        self.assertTrue(
            is_header_line("src_ip,dst_ip,src_port,dst_port,protocol,flags")
        )

    def test_is_header_line_true_with_spaces_and_case(self):
        self.assertTrue(
            is_header_line(" Src_IP, Dst_IP, Src_Port, Dst_Port, Protocol, Flags ")
        )

    def test_is_header_line_false(self):
        self.assertFalse(
            is_header_line("192.168.1.5,10.0.0.1,54321,80,TCP,SYN")
        )

    def test_is_syn_packet_true(self):
        self.assertTrue(is_syn_packet(self.sample_packet))

    def test_is_syn_packet_false_for_ack(self):
        packet = {
            "src_ip": "192.168.1.5",
            "dst_ip": "10.0.0.1",
            "src_port": 54321,
            "dst_port": 443,
            "protocol": "TCP",
            "flags": "ACK",
        }
        self.assertFalse(is_syn_packet(packet))

    def test_is_syn_packet_false_for_udp(self):
        packet = {
            "src_ip": "192.168.1.5",
            "dst_ip": "10.0.0.1",
            "src_port": 54321,
            "dst_port": 53,
            "protocol": "UDP",
            "flags": "",
        }
        self.assertFalse(is_syn_packet(packet))

    def test_detect_port_scan_true(self):
        packets = [
            {
                "src_ip": "192.168.1.5",
                "dst_ip": "10.0.0.1",
                "src_port": 50000 + port,
                "dst_port": port,
                "protocol": "TCP",
                "flags": "SYN",
            }
            for port in range(1, 31)
        ]

        result = detect_port_scan(
            packets,
            "192.168.1.5",
            self.sample_config.port_scan_threshold,
        )
        self.assertTrue(result)

    def test_detect_port_scan_false_exactly_at_threshold(self):
        packets = [
            {
                "src_ip": "192.168.1.5",
                "dst_ip": "10.0.0.1",
                "src_port": 50000 + port,
                "dst_port": port,
                "protocol": "TCP",
                "flags": "SYN",
            }
            for port in range(1, 26)
        ]

        result = detect_port_scan(
            packets,
            "192.168.1.5",
            self.sample_config.port_scan_threshold,
        )
        self.assertFalse(result)

    def test_detect_port_scan_duplicate_ports_not_counted(self):
        packets = [
            {
                "src_ip": "192.168.1.5",
                "dst_ip": "10.0.0.1",
                "src_port": 50000,
                "dst_port": 80,
                "protocol": "TCP",
                "flags": "SYN",
            },
            {
                "src_ip": "192.168.1.5",
                "dst_ip": "10.0.0.1",
                "src_port": 50001,
                "dst_port": 80,
                "protocol": "TCP",
                "flags": "SYN",
            },
            {
                "src_ip": "192.168.1.5",
                "dst_ip": "10.0.0.1",
                "src_port": 50002,
                "dst_port": 443,
                "protocol": "TCP",
                "flags": "SYN",
            },
        ]

        result = detect_port_scan(
            packets,
            "192.168.1.5",
            self.sample_config.port_scan_threshold,
        )
        self.assertFalse(result)

    def test_detect_port_scan_false_for_other_ip(self):
        packets = [
            {
                "src_ip": "192.168.1.10",
                "dst_ip": "10.0.0.1",
                "src_port": 50000 + port,
                "dst_port": port,
                "protocol": "TCP",
                "flags": "SYN",
            }
            for port in range(1, 31)
        ]

        result = detect_port_scan(
            packets,
            "192.168.1.5",
            self.sample_config.port_scan_threshold,
        )
        self.assertFalse(result)

    def test_detect_syn_flood_true(self):
        packets = [
            {
                "src_ip": "10.0.0.2",
                "dst_ip": "10.0.0.1",
                "src_port": 40000 + i,
                "dst_port": 80,
                "protocol": "TCP",
                "flags": "SYN",
            }
            for i in range(101)
        ]

        result = detect_syn_flood(
            packets,
            "10.0.0.2",
            self.sample_config.syn_flood_threshold,
        )
        self.assertTrue(result)

    def test_detect_syn_flood_false_exactly_at_threshold(self):
        packets = [
            {
                "src_ip": "10.0.0.2",
                "dst_ip": "10.0.0.1",
                "src_port": 40000 + i,
                "dst_port": 80,
                "protocol": "TCP",
                "flags": "SYN",
            }
            for i in range(100)
        ]

        result = detect_syn_flood(
            packets,
            "10.0.0.2",
            self.sample_config.syn_flood_threshold,
        )
        self.assertFalse(result)

    def test_detect_syn_flood_ignores_non_syn_packets(self):
        packets = [
            {
                "src_ip": "10.0.0.2",
                "dst_ip": "10.0.0.1",
                "src_port": 40000 + i,
                "dst_port": 80,
                "protocol": "TCP",
                "flags": "ACK",
            }
            for i in range(150)
        ]

        result = detect_syn_flood(
            packets,
            "10.0.0.2",
            self.sample_config.syn_flood_threshold,
        )
        self.assertFalse(result)

    def test_detect_suspicious_ports(self):
        packets = [
            {
                "src_ip": "1.1.1.1",
                "dst_ip": "2.2.2.2",
                "src_port": 1234,
                "dst_port": 22,
                "protocol": "TCP",
                "flags": "SYN",
            },
            {
                "src_ip": "3.3.3.3",
                "dst_ip": "2.2.2.2",
                "src_port": 1235,
                "dst_port": 80,
                "protocol": "TCP",
                "flags": "SYN",
            },
        ]

        result = detect_suspicious_ports(packets, (22, 23, 3389))
        self.assertIn("1.1.1.1", result)
        self.assertNotIn("3.3.3.3", result)

    def test_detect_high_traffic(self):
        packets = [
            {
                "src_ip": "1.1.1.1",
                "dst_ip": "2.2.2.2",
                "src_port": 1000 + i,
                "dst_port": 80,
                "protocol": "TCP",
                "flags": "SYN",
            }
            for i in range(60)
        ]

        result = detect_high_traffic(packets, threshold=50)
        self.assertIn("1.1.1.1", result)

    def test_analyze_traffic_empty(self):
        results = analyze_traffic([], self.sample_config, self.sample_logger)

        self.assertEqual(results["total_packets"], 0)
        self.assertEqual(results["port_scans"], [])
        self.assertEqual(results["syn_floods"], [])
        self.assertEqual(results["suspicious_ports"], [])
        self.assertEqual(results["high_traffic"], [])

    def test_analyze_traffic_detects_both_threats(self):
        port_scan_packets = [
            {
                "src_ip": "10.0.1.99",
                "dst_ip": "10.0.0.1",
                "src_port": 50000 + port,
                "dst_port": port,
                "protocol": "TCP",
                "flags": "SYN",
            }
            for port in range(1, 31)
        ]

        syn_flood_packets = [
            {
                "src_ip": "172.16.0.77",
                "dst_ip": "10.0.0.1",
                "src_port": 40000 + i,
                "dst_port": 80,
                "protocol": "TCP",
                "flags": "SYN",
            }
            for i in range(101)
        ]

        packets = port_scan_packets + syn_flood_packets
        results = analyze_traffic(packets, self.sample_config, self.sample_logger)

        self.assertEqual(results["total_packets"], len(packets))
        self.assertIn("10.0.1.99", results["port_scans"])
        self.assertIn("172.16.0.77", results["syn_floods"])

    def test_analyze_traffic_no_threats(self):
        packets = [
            {
                "src_ip": "192.168.1.10",
                "dst_ip": "10.0.0.1",
                "src_port": 50000,
                "dst_port": 80,
                "protocol": "TCP",
                "flags": "ACK",
            },
            {
                "src_ip": "192.168.1.11",
                "dst_ip": "10.0.0.5",
                "src_port": 50001,
                "dst_port": 443,
                "protocol": "TCP",
                "flags": "ACK",
            },
            {
                "src_ip": "192.168.1.12",
                "dst_ip": "10.0.0.9",
                "src_port": 50002,
                "dst_port": 53,
                "protocol": "UDP",
                "flags": "",
            },
        ]

        results = analyze_traffic(packets, self.sample_config, self.sample_logger)

        self.assertEqual(results["total_packets"], 3)
        self.assertEqual(results["port_scans"], [])
        self.assertEqual(results["syn_floods"], [])
        self.assertEqual(results["suspicious_ports"], [])
        self.assertEqual(results["high_traffic"], [])

    def test_load_traffic_log_and_generate_results_json(self):
        script_dir = Path(__file__).resolve().parent
        input_path = script_dir / "traffic_sample.log"
        results_path = script_dir / "results.json"

        packets = load_traffic_log(input_path, self.sample_logger)
        results = analyze_traffic(packets, self.sample_config, self.sample_logger)

        with results_path.open("w", encoding="utf-8") as file:
            json.dump(results, file, indent=4)

        self.assertGreater(results["total_packets"], 0)
        self.assertIsInstance(results["port_scans"], list)
        self.assertIsInstance(results["syn_floods"], list)
        self.assertIsInstance(results["suspicious_ports"], list)
        self.assertIsInstance(results["high_traffic"], list)
        self.assertTrue(results_path.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)