Documentation Quality Analyzer

A Python-based tool that analyzes technical documentation for completeness, required terminology, and staleness. This tool helps IT operations teams, DevOps engineers, and technical writers maintain accurate, consistent, and reliable documentation.

Overview

Technical documentation often becomes incomplete, outdated, or inconsistent as systems evolve. This can lead to operational issues, slower troubleshooting, and increased risk.

The Documentation Quality Analyzer solves this problem by:

Checking for missing required sections
Validating required technical terms
Detecting stale documents using metadata
Assigning quality scores based on configurable rules
Generating both structured and human-readable reports
Features
Required section validation (Overview, Setup, Troubleshooting, etc.)
Required term detection (e.g., nginx, systemctl, backup.sh)
Staleness detection using metadata
Weighted scoring system
JSON output (results.json)
Text report output (report.txt)
CLI interface using argparse
Logging with INFO, WARNING, and ERROR levels
Input validation and clear error messages
Per-file error handling (continues processing on failure)
Safe file filtering (skips unsupported files and folders)
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
--rules	Path to rules.json file
--metadata	Optional metadata file for staleness detection
Input Structure
Documentation Files
docs/
├── backup_guide.md
├── deployment.md
├── monitoring.md
├── network_config.md
└── server_setup.md
rules.json
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
metadata.json (optional)
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

The analyzer includes robust validation and error handling:

Validates rules.json before processing
Ensures correct data types and required fields
Handles missing or invalid files gracefully
Provides clear, user-friendly error messages
File Filtering (Instructor Feedback Fix)
Only .md and .txt files are processed
Folders and unsupported files are skipped
Prevents unexpected files from breaking execution
Per-File Error Handling (Instructor Feedback Fix)
Each document is processed independently
If one file fails, the error is logged
The analyzer continues processing remaining files

Example:

WARNING: Skipping unsupported file type: temp.log
ERROR: Failed to analyze bad_file.md: Invalid content
Logging

Logging levels used:

INFO → Processing steps
WARNING → Missing sections/terms or skipped files
ERROR → Failures

Example:

INFO: Analyzing document: server_setup.md
WARNING: Missing section detected: Troubleshooting
Running Tests

Run all tests:

pytest tests/

Verbose mode:

pytest tests/ -v
Test Coverage

Tests include:

DocumentationIssue class
DocumentReport scoring
Analyzer logic
Section validation
Term detection
Edge cases (empty files)
Missing file handling
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
Design & Code Quality
Modular architecture (separation of concerns)
Object-oriented design
Clean, readable code structure
No hardcoded paths
Reusable components
AI Usage

AI tools (ChatGPT) were used to:

Refactor and improve code structure
Generate and expand test cases
Debug errors and improve validation
Enhance documentation quality

All AI-generated content was reviewed, tested, and adjusted to ensure correctness.

Author

Tanya Logan
Cybersecurity Programming Capstone Project