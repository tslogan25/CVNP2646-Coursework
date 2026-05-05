# Documentation Quality Analyzer

A rule-based Python tool that analyzes technical documentation for completeness, accuracy, and staleness using JSON-driven configuration.

## Overview

The Documentation Quality Analyzer helps IT teams, DevOps engineers, and technical writers identify issues in documentation such as:

- Missing required sections
- Outdated (stale) documents
- Missing critical technical terms

By automating these checks, the tool reduces operational risk caused by incomplete or outdated documentation.

## Features

- JSON-Driven Rules Engine: Define validation rules using `rules.json`
- Completeness Checks: Detect missing required sections such as Setup, Usage, and Troubleshooting
- Staleness Detection: Identify outdated documents using metadata timestamps
- Keyword Validation: Ensure important technical terms are present
- Risk Scoring System: Assign scores based on weighted issues
- Dual Output: Generates `results.json` and `report.txt`
- CLI Interface: Run directly from the terminal using command-line arguments
- Logging & Error Handling: Handles invalid input and logs issues gracefully

## Project Structure

```text
Week13, 14, 15 & 16/
├── data/
│   ├── input_sample.json
│   ├── metadata.json
│   ├── rules.json
│   └── results.json
├── src/
│   ├── main.py
│   ├── analyzer.py
│   └── models.py
├── tests/
│   ├── test_analyzer.py
│   └── test_models.py
├── README.md
├── AI_USAGE.md
├── CHECKPOINT.md
├── report.txt
├── requirements.txt
```

## Installation

Navigate to the project folder:

```bash
cd "Week13, 14, 15 & 16"
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python src/main.py --input data/input_sample.json --rules data/rules.json --metadata data/metadata.json --output data/results.json
```

## Input Files

- `input_sample.json`: Contains documentation content to analyze
- `rules.json`: Defines required sections, stale threshold, required terms, and scoring weights
- `metadata.json`: Contains timestamps for staleness checks

## Output Files

- `results.json`: Structured analysis results, including scores and issues per document
- `report.txt`: Human-readable summary including document scores, detected issues, and overall statistics

## Running Tests

```bash
python -m pytest -v
```

Tests include:

- Normal cases
- Edge cases
- Invalid input handling

## Technical Approach

- `models.py`: Defines data structures such as Document and RuleSet
- `analyzer.py`: Handles section validation, keyword checks, and scoring
- `main.py`: Handles the CLI interface and coordinates execution

## Error Handling

The tool handles:

- Missing files
- Invalid JSON
- Missing fields
- Incorrect data types

Errors are logged without crashing the program.

## Logging

- INFO: Normal processing
- WARNING: Skipped or invalid data
- ERROR: Failures

## AI-Assisted Development

See `AI_USAGE.md` for:

- Tools used (ChatGPT, GitHub Copilot, Claude)
- Prompts used
- Accepted and rejected code
- Lessons learned

## Clean Checkout Test

```bash
git clone <repo>
cd project
pip install -r requirements.txt
python src/main.py --input data/input_sample.json --rules data/rules.json --metadata data/metadata.json --output data/results.json
python -m pytest -v
```

## Future Improvements

- HTML report output
- Real-time document monitoring
- CI/CD integration
- Advanced NLP analysis

## License

For academic use only.