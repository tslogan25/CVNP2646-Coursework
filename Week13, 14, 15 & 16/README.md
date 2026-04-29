Documentation Quality Analyzer

A Python-based tool that analyzes technical documentation for completeness, required terminology, and staleness. This project helps IT operations teams, DevOps engineers, and technical writers maintain accurate and reliable documentation.

Overview

Technical documentation often becomes outdated, incomplete, or inconsistent over time. This leads to operational risk, slower troubleshooting, and confusion.

The Documentation Quality Analyzer solves this problem by:

Checking for missing required sections
Validating the presence of important technical terms
Detecting outdated (stale) documentation using metadata
Assigning quality scores to documents
Generating structured and readable reports
Features
Section validation (Overview, Setup, Troubleshooting, etc.)
Required term detection (nginx, systemctl, backup.sh)
Staleness detection using metadata
Weighted scoring system
JSON output (machine-readable)
Text report output (human-readable)
Input validation and clear error messages
Logging for debugging and traceability
Automated testing using pytest
Installation
Prerequisites
Python 3.8+
pip
Setup
pip install -r requirements.txt
Usage
Basic Run
python src/main.py --docs docs --rules rules.json
Run with Metadata (Staleness Detection)
python src/main.py --docs docs --rules rules.json --metadata metadata.json
Help Menu
python src/main.py --help
Command Line Arguments
Argument	Description
--docs	Path to documentation directory
--rules	Path to rules configuration file
--metadata	(Optional) Metadata file for staleness checks
Input Files
Documentation Files

Stored in:

docs/
├── monitoring.md
├── network_config.md
└── server_setup.md
rules.json

Defines validation rules:

{
  "required_sections": ["Overview", "Prerequisites", "Setup", "Usage", "Troubleshooting"],
  "stale_after_days": 90,
  "required_terms": ["nginx", "systemctl", "backup.sh"],
  "weights": {
    "missing_section": 30,
    "stale_doc": 25,
    "missing_term": 15
  }
}
metadata.json

Used to detect stale documents:

{
  "documents": [
    {
      "file": "server_setup.md",
      "last_updated": "2024-01-01"
    }
  ]
}
Output
results.json
[
  {
    "document": "server_setup.md",
    "score": 70,
    "issues": [
      {
        "type": "missing_section",
        "details": "Troubleshooting section not found"
      }
    ]
  }
]
report.txt
File: server_setup.md
Score: 70

Issues:
- Missing Section: Troubleshooting section not found
Scoring System
Issue Type	Penalty
Missing Section	30
Missing Term	15
Stale Document	25

Scores never drop below 0.

Error Handling & Validation

The application validates inputs before processing:

Ensures required keys exist in rules.json
Validates data types
Checks file existence before reading
Provides clear error messages for:
Missing files
Invalid rules
Incorrect metadata format

Example:

Input document not found: 'docs/file.md'. Check the path and try again.
Logging

Logging levels used:

INFO → processing steps
WARNING → missing sections/terms
ERROR → failures

Example:

INFO: Analyzing document: server_setup.md
WARNING: Missing section detected: Troubleshooting
Running Tests

Run all tests:

pytest tests/

Run with verbose output:

pytest tests/ -v
Test Coverage

Includes tests for:

DocumentationIssue class
DocumentReport scoring
Section validation
Term validation
Edge cases (empty content)
Missing file handling
Analyzer logic
Project Structure
Week13, 14, 15 & 16/
├── docs/
├── src/
│   ├── main.py
│   ├── models.py
│   └── utils.py
├── tests/
│   ├── __init__.py
│   ├── test_analyzer.py
│   └── test_models.py
├── metadata.json
├── rules.json
├── results.json
├── report.txt
├── requirements.txt
└── README.md
Design & Refactoring
Modular architecture (models vs logic)
Clean separation of concerns
No global state
Reusable components
Maintainable and readable code
AI Usage

AI tools (ChatGPT) were used to:

Improve code structure
Expand test coverage
Debug errors
Enhance validation logic
Improve documentation clarity

All outputs were reviewed and adapted.

Author

Tanya Logan
Cybersecurity Programming Capstone Project