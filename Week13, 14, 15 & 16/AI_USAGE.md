# AI Usage Log

## Project: Documentation Quality Analyzer

---

## Overview

This document tracks my use of AI tools throughout the development of the Documentation Quality Analyzer capstone project.

AI tools were used to assist with:
- Debugging
- Refactoring
- Test generation
- README documentation
- Error handling improvements
- Logging improvements
- Project organization

All AI-generated code and suggestions were reviewed, tested, and modified before being included in the final project.

---

## AI Tools Used

- ChatGPT
- GitHub Copilot

---

## Summary Statistics

- Total AI-assisted sessions: 20+
- Code suggestions accepted as-is: 5
- Code suggestions modified before use: 10+
- Code suggestions rejected: 5+
- Primary uses:
  - Debugging
  - Documentation
  - Test generation
  - Refactoring
  - Validation logic
  - Error handling

---

# Week 13: Planning and Project Design

## AI Assistance

AI was used to:
- Brainstorm project structure
- Refine the Documentation Quality Analyzer concept
- Organize project folders
- Plan CLI functionality
- Discuss JSON configuration structure

---

## Example Prompt

```text
Help me design a Python project structure for a rule-based documentation analyzer.
```

### My Action

Modified the suggested structure to better fit the coursework requirements and added dedicated `docs/` and `data/` folders.

---

# Week 14: Core Implementation

## AI Assistance

AI helped with:
- `argparse` setup
- Object-oriented class structure
- JSON report generation
- Logging setup
- File handling improvements
- Debugging import and path issues

---

## Example Prompt

```text
Generate a Python argparse CLI for analyzing documentation files using rules.json and metadata.json.
```

### My Action

Accepted the basic CLI structure but modified:
- Argument names
- File paths
- Logging output
- Error handling behavior

to better fit the project requirements.

---

## Example of Modified AI Code

### Original AI Suggestion

```python
for filepath in docs_path.glob("*.md"):
    report = analyzer.analyze_document(str(filepath))
```

### My Modified Version

```python
for filepath in docs_path.iterdir():

    if filepath.is_dir():
        continue

    if filepath.suffix.lower() not in [".md", ".txt"]:
        continue

    try:
        report = analyzer.analyze_document(str(filepath))
    except Exception as error:
        logging.error(f"Failed to analyze {filepath.name}: {error}")
        continue
```

### Why I Changed It

The original suggestion:
- did not skip directories
- did not support `.txt` files
- would stop execution if one file failed

I improved the logic to make the analyzer more robust and fault tolerant.

---

# Week 15: Testing and Validation

## AI Assistance

AI helped with:
- pytest examples
- edge case suggestions
- validation logic
- improving error messages
- test organization

---

## Example Prompt

```text
Suggest pytest tests for normal cases, edge cases, and invalid input for a documentation analyzer.
```

### My Action

Used the suggestions as a starting point and customized:
- test names
- assertions
- fixtures
- expected results

to match the actual implementation.

---

## Example of Rejected AI Code

### Rejected Suggestion

```python
if "Overview" not in content:
    return False
```

### Why I Rejected It

The suggestion was too simplistic and did not:
- generate structured issue objects
- integrate with the scoring system
- support reusable issue reporting

Instead, I implemented `DocumentationIssue` objects and integrated them into `DocumentReport`.

---

# Verification Methods

All AI-generated code and suggestions were verified by:

- Running the analyzer from the command line
- Running pytest unit tests
- Inspecting generated `data/results.json`
- Inspecting generated `report.txt`
- Testing missing-file scenarios
- Testing invalid JSON handling
- Testing unsupported file handling
- Reviewing logs for correctness

---

# What I Learned About AI Usage

This project taught me that AI works best as:
- a debugging assistant
- a brainstorming tool
- a code refactoring helper
- a documentation assistant

AI was most effective when:
- prompts were specific
- I already understood the problem
- I verified the output myself

I learned that AI-generated code often requires modification to:
- handle edge cases
- improve readability
- fit project requirements
- improve maintainability

I also learned the importance of:
- testing AI-generated code
- understanding every line before using it
- rejecting overly complex solutions I could not explain

---

# Responsible AI Usage

To ensure responsible AI usage:
- I reviewed all generated code manually
- I modified code to match project requirements
- I rejected suggestions that added unnecessary complexity
- I tested all important functionality independently
- I documented how AI influenced the project

The final implementation reflects my understanding, testing, debugging, and design decisions rather than direct AI-generated output alone.

---

# Final Reflection on AI Collaboration

AI significantly accelerated development, especially for:
- debugging
- test generation
- documentation
- project organization

However, the most important learning came from:
- debugging problems manually
- understanding why code failed
- improving AI-generated ideas
- refining the project architecture

This project demonstrated that AI is most useful when combined with critical thinking, testing, and personal understanding rather than blind copy/paste development.

