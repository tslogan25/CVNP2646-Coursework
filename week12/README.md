# Network Traffic Monitor

Professional network traffic analyzer with port scan, SYN flood, and AI-enhanced behavioral detection.

## Features

- Modular design with clear separation of I/O, parsing, and analysis logic  
- Comprehensive logging with file and console handlers  
- Structured JSON output in results.json  
- Human-readable text output in report.txt  
- Full automated test coverage using unittest  
- CLI support with argparse, help text, validation, and exit codes  
- AI-enhanced behavioral rules for suspicious ports and high traffic volume  

## Installation

cd Week12

## Usage

python network_monitor.py
python network_monitor.py traffic_sample.log
python network_monitor.py --port-scan-threshold 50 --syn-flood-threshold 200 --high-traffic-threshold 75
python network_monitor.py --help

## Project Structure

Week12/
├── network_monitor.py
├── test_network_monitor.py
├── traffic_sample.log
├── network_monitor.log
├── results.json
├── report.txt
└── README.md

## Output

Console Output:

Analysis complete
Total packets: 147
Port scans detected: 1
  - 10.0.1.99
SYN floods detected: 1
  - 172.16.0.77
Suspicious port activity detected: 1
  - 10.0.1.99
High traffic sources detected: 1
  - 172.16.0.77

results.json:

{
  "total_packets": 147,
  "port_scans": ["10.0.1.99"],
  "syn_floods": ["172.16.0.77"],
  "suspicious_ports": ["10.0.1.99"],
  "high_traffic": ["172.16.0.77"]
}

report.txt:

The program generates a human-readable report containing:
- total packets analyzed  
- detected port scans  
- detected SYN floods  
- suspicious port activity  
- high traffic sources  
- analysis summary  

## Logging

Logs are written to Week12/network_monitor.log

Log levels used:
- INFO for program flow  
- WARNING for detected threats  
- ERROR for malformed data  

## AI-Enhanced Rules

In addition to signature-based rules, the system applies two AI-enhanced behavioral rules:

Suspicious Port Detection  
Flags source IPs targeting high-risk ports such as 22, 23, and 3389, which are commonly associated with remote access and unauthorized activity.

High Traffic Volume Detection  
Flags source IPs generating unusually high packet volume, indicating automated behavior, scanning, or flood activity.

## Analysis Approach

The system uses a layered detection strategy combining:
- signature-based detection (port scans and SYN floods)  
- behavioral analysis (high traffic volume)  
- risk-based detection (targeting sensitive ports)  

This approach improves detection accuracy and demonstrates how rule-based systems can be extended toward AI-style pattern recognition.

## Refactoring Journey

Problems with Original Code:
- Global variables made testing difficult  
- Magic numbers had no explanation  
- Mixed concerns (I/O, parsing, logic combined)  
- No error handling  
- Print statements instead of logging  
- No tests  

Refactoring Applied:
- Introduced NetworkConfig class  
- Created pure functions  
- Separated I/O from logic  
- Implemented structured logging  
- Added JSON and text report output  
- Built CLI with argparse  
- Added full test coverage  

Biggest Challenge:
Separating I/O from logic required restructuring the program into independent, testable functions.

## Testing

Run tests:

python test_network_monitor.py

Expected result:

Ran 25 tests  

OK  

## CLI Design

- Supports input file argument  
- Supports custom thresholds  
- Provides help menu  
- Validates input  
- Uses proper exit codes (0, 1, 2)  

## AI-Assisted Development

Tools Used:
- GitHub Copilot  
- ChatGPT  
- Claude  

What Worked Well:
- Generated structure and boilerplate  
- Helped design test cases  
- Improved organization  

What I Had to Fix:
- Removed global logger usage  
- Fixed incorrect data types  
- Added missing edge case tests  
- Improved parsing and validation  
- Added AI-enhanced detection rules  

Lesson Learned:
AI is helpful but requires validation, testing, and manual refinement.

## AI Best Practices

- Be specific with prompts  
- Iterate on responses  
- Ask for explanations  
- Test all generated code  
- Review everything before using  

## License

MIT