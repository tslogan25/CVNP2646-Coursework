Network Traffic Monitor

Professional network traffic analyzer with port scan and SYN flood detection.

Features
Modular design with separation of I/O, parsing, and logic
Comprehensive logging (file + console with configurable levels)
Full test coverage using unittest (23 tests)
CLI support with argparse and validation
Outputs structured results to results.json
Installation

cd Week12

Usage

Basic usage:
python network_monitor.py

With input file:
python network_monitor.py traffic_sample.log

With custom thresholds:
python network_monitor.py --port-scan-threshold 50 --syn-flood-threshold 200

Help:
python network_monitor.py --help

Project Structure

Week12/
├── network_monitor.py
├── test_network_monitor.py
├── traffic_sample.log
├── network_monitor.log
├── results.json
└── README.md

Output

Console Output:

Analysis complete
Total packets: 147
Port scans detected: 1

10.0.1.99
SYN floods detected: 1
172.16.0.77

results.json:

{
"total_packets": 147,
"port_scans": ["10.0.1.99"],
"syn_floods": ["172.16.0.77"]
}

Logging

Logs are written to:
Week12/network_monitor.log

Log levels:

INFO → program flow
WARNING → detected threats
ERROR → malformed data
Refactoring Journey
Problems with Original Code
Global variables made testing difficult
Magic numbers (25, 100) with no explanation
Mixed concerns (I/O, parsing, logic combined)
No error handling
Print statements instead of logging
No tests
Refactoring Applied
Introduced NetworkConfig class for configuration
Created pure functions for parsing and analysis
Separated I/O from logic (load_traffic_log vs analyze_traffic)
Implemented logging with file and console handlers
Added full test coverage (23 tests)
Built CLI using argparse with validation
Biggest Challenge

Separating I/O from logic was the most difficult part. The original code combined reading, parsing, and analysis, which required restructuring into independent, testable functions.

Testing

Run tests:
python test_network_monitor.py

Output:
Ran 23 tests in 0.006s
OK

AI-Assisted Development
Tools Used
GitHub Copilot for code suggestions
ChatGPT for refactoring and debugging
Claude for test generation
What Worked Well
Generated initial test structure
Suggested function organization
Helped with boilerplate code
What I Had to Fix
Replaced global logger with parameterized logger
Corrected incorrect data types in tests
Added missing boundary tests (threshold edge cases)
Lesson Learned

AI is useful for structure and speed, but always requires review and testing. Several issues were identified and fixed through testing.

AI Best Practices
Be specific with prompts
Iterate on responses
Ask for explanations
Request alternatives
Always test AI-generated code
Learn from patterns instead of copying
License

MIT