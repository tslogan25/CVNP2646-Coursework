# Documentation Quality Analyzer

A professional tool that analyzes technical documentation for completeness, required terminology, and staleness using rule-based validation.

---

## Overview

The Documentation Quality Analyzer evaluates Markdown documentation files to identify:

- Missing required sections
- Missing required technical terms
- Outdated (stale) documentation

It helps IT teams, DevOps engineers, and technical writers maintain accurate and complete documentation.

---

## Features

- Detects missing sections (e.g., Overview, Setup, Troubleshooting)
- Detects missing required terms (e.g., nginx, systemctl)
- Detects stale documents using metadata
- Generates structured JSON output (`results.json`)
- Generates human-readable report (`report.txt`)
- CLI interface using argparse
- Logging for analysis progress and errors
- Unit tests for validation and scoring

---

## Project Structure


Week13, 14, 15 & 16/
├── src/
│ ├── main.py
│ ├── models.py
│ └── utils.py
├── docs/
│ ├── server_setup.md
│ ├── deployment.md
│ ├── backup_guide.md
│ ├── monitoring.md
│ └── network_config.md
├── Tests/
│ └── test_analyzer.py
├── rules.json
├── metadata.json
├── input_sample.json
├── results.json
├── report.txt
└── README.md


---

## Setup

No external dependencies required.

Run from your project directory:

```bash
cd Week13, 14, 15 & 16
Usage

Run the analyzer:

python src/main.py --docs docs --rules rules.json --metadata metadata.json

Optional arguments:

--docs : Directory containing documentation files
--rules : JSON file defining validation rules
--metadata : JSON file for document staleness (optional)
--output : Output JSON file (default: results.json)
--report : Output text report (default: report.txt)
Example
python src/main.py --docs docs --rules rules.json --metadata metadata.json

This will:

Analyze all files in docs/
Generate results.json
Generate report.txt
Sample Input

Sample project data is represented by the documentation files in docs/, with input_sample.json included to describe the sample dataset, rules.json for validation rules, and metadata.json for staleness metadata.

Output
JSON Output (results.json)
{
  "results": [
    {
      "document": "server_setup.md",
      "score": 15,
      "issues": [
        {
          "type": "missing_section",
          "details": "Prerequisites section not found"
        }
      ]
    }
  ]
}
Text Report (report.txt)
Document: server_setup.md
Score: 15

Issues:
- Missing Section: Prerequisites section not found

----------------------------------------
Testing

Run all tests:

python -m unittest discover Tests
Current Limitations
Section detection uses simple text matching rather than strict Markdown parsing.
Term detection currently flags a document only when none of the required terms are present.
Staleness checks depend on metadata entries being available for each file.
Future Improvements (Week 15)
Improve Markdown parsing for more accurate section detection
Enhance term detection to support partial matches and synonyms
Add weighted scoring improvements
Improve edge case handling
Expand test coverage
Author

Tanya Logan