# Documentation Quality Analyzer

## Project Overview

The Documentation Quality Analyzer is a rule-based Python tool that analyzes technical documentation for quality issues. It checks documentation files for missing required sections, missing technical terms, and stale update dates.

This tool is useful because technical documentation can become outdated, incomplete, or inconsistent over time. By automatically checking documentation quality, the tool helps IT teams, system administrators, DevOps engineers, and technical writers identify problems before they cause confusion or operational risk.

---

## Features

- Loads Markdown and text documentation files from a `docs/` folder
- Loads rules from `data/rules.json`
- Loads optional metadata from `data/metadata.json`
- Detects missing required sections
- Detects missing required technical terms
- Detects stale documentation
- Calculates quality scores
- Generates structured JSON output
- Generates a human-readable text report
- Uses a command-line interface with `argparse`
- Includes logging and error handling
- Includes pytest unit tests

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

Install required packages:

```bash
pip install -r requirements.txt
```

If pytest is not already installed, install it with:

```bash
pip install pytest
```

---

## Usage

Run the analyzer from the main project folder:

```bash
python src/main.py --docs docs --rules data/rules.json --metadata data/metadata.json
```

You can also run it without metadata:

```bash
python src/main.py --docs docs --rules data/rules.json
```

---

## CLI Arguments

| Argument | Required | Description |
|---|---|---|
| `--docs` | Yes | Path to the documentation folder |
| `--rules` | Yes | Path to the rules JSON file |
| `--metadata` | No | Path to the metadata JSON file |

---

## Input Files

### Documentation Files

Documentation files are stored in the `docs/` folder.

Supported file types:

```text
.md
.txt
```

Example files:

```text
docs/server_setup.md
docs/backup_guide.md
docs/deployment.md
docs/monitoring.md
docs/network_config.md
```

---

### Rules File

Location:

```text
data/rules.json
```

Example:

```json
{
  "required_sections": [
    "Overview",
    "Prerequisites",
    "Setup",
    "Usage",
    "Troubleshooting"
  ],
  "stale_after_days": 90,
  "required_terms": [
    "nginx",
    "systemctl",
    "backup.sh"
  ],
  "weights": {
    "missing_section": 30,
    "stale_doc": 25,
    "missing_term": 15
  }
}
```

---

### Metadata File

Location:

```text
data/metadata.json
```

Example:

```json
{
  "documents": [
    {
      "file": "server_setup.md",
      "last_updated": "2026-01-10",
      "owner": "IT Operations"
    }
  ]
}
```

---

## Output Files

### JSON Output

The analyzer writes structured results to:

```text
data/results.json
```

Example:

```json
{
  "results": [
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
}
```

---

### Text Report

The analyzer also writes a readable report to:

```text
report.txt
```

Example:

```text
Documentation Quality Analyzer Report
==================================================

Document: server_setup.md
Score: 70
Issues:
- missing_section: Troubleshooting section not found
```

---

## Running Tests

Run all tests with:

```bash
pytest tests/
```

Expected result:

```text
12 passed
```

---

## Project Structure

```text
Week13, 14, 15 & 16/
├── src/
│   ├── main.py
│   └── models.py
├── tests/
│   ├── __init__.py
│   ├── test_analyzer.py
│   └── test_models.py
├── docs/
│   ├── backup_guide.md
│   ├── deployment.md
│   ├── monitoring.md
│   ├── network_config.md
│   └── server_setup.md
├── data/
│   ├── input_sample.json
│   ├── output_sample.json
│   ├── metadata.json
│   ├── rules.json
│   └── results.json
├── README.md
├── CHECKPOINT.md
├── AI_USAGE.md
├── report.txt
└── requirements.txt
```

---

## Main Classes

### DocumentationIssue

Represents a single issue found in a documentation file.

### DocumentReport

Stores the results for one analyzed document, including the document name, score, and list of issues.

### DocumentationAnalyzer

Handles the main analysis logic, including loading documents, checking sections, checking terms, checking staleness, and producing reports.

---

## Error Handling

The analyzer includes error handling for:

- Missing JSON files
- Invalid JSON files
- Missing documentation directory
- Unsupported file types
- Bad files inside the docs folder

If one document fails, the program logs the error and continues processing the remaining documents.

---

## Logging

The program logs progress and warnings during execution.

Example:

```text
INFO: Starting Documentation Analyzer...
INFO: Analyzing deployment.md
WARNING: Missing section detected: Troubleshooting
INFO: Analysis complete.
```

---

## Limitations

Current limitations include:

- No HTML report generation
- No visual dashboard
- Basic scoring logic only
- Limited file support beyond `.md` and `.txt`
- Simple keyword and header matching

---

## Author

Tanya Logan

CVNP2646 Coursework Project

Documentation Quality Analyzer