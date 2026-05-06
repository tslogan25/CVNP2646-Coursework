# AI Usage Log

## Project: Documentation Quality Analyzer

## Overview

This document tracks my use of AI tools (ChatGPT and GitHub Copilot) throughout the development of my capstone project. AI was used to assist with planning, debugging, testing, and improving code structure. All AI-generated code was reviewed, tested, and modified where necessary before being included in the final project.

---

## Summary Statistics

- Total AI-assisted sessions: 15  
- Code suggestions accepted as-is: 5  
- Code suggestions modified before use: 8  
- Code suggestions rejected: 2  
- Primary tools used: ChatGPT and GitHub Copilot  
- Primary uses: project structure, CLI design, debugging, testing, README writing, and demo preparation  

---

## Key Prompts & Interactions

### Week 13: Planning

**Prompt:**  
How can I design a Python tool that checks documentation for missing sections, required terms, and outdated content?

**AI Response:**  
Suggested creating a rule-based documentation analyzer using JSON configuration files and metadata.

**My Action:**  
Modified the idea to match assignment requirements and focused on analyzing Markdown documentation files in a folder.

---

### Week 14: Implementation

**Prompt:**  
How do I use argparse to create a command-line interface for my tool?

**AI Response:**  
Provided example code using input and output file arguments.

**My Action:**  
Modified the CLI to use `--docs`, `--rules`, and `--metadata` since my tool processes a folder of documentation files instead of a single input file.

---

### Week 14: Debugging

**Prompt:**  
Why is my Python script not finding src/main.py?

**AI Response:**  
Explained that the script was being run from the wrong directory.

**My Action:**  
Changed into the correct project directory before running the program.

---

### Week 15: Testing

**Prompt:**  
How do I write pytest unit tests for my project?

**AI Response:**  
Suggested writing tests for normal cases, edge cases, missing data, and error handling.

**My Action:**  
Used these ideas to create tests in `test_analyzer.py` and `test_models.py` and ensured they passed successfully.

---

### Week 16: Demo and Documentation

**Prompt:**  
Help me create a demo script for my Documentation Quality Analyzer.

**AI Response:**  
Suggested a structured demo including problem statement, demonstration, results explanation, testing, and impact.

**My Action:**  
Modified the script to match my actual project files, command, and outputs.

---

## Examples of Modified/Rejected AI Code

### Example 1: CLI Argument Design

**Original AI suggestion:**
```python
parser.add_argument("--input", required=True)
parser.add_argument("--output", required=True)
```

**My modified version:**
```python
parser.add_argument("--docs", required=True, help="Path to documentation folder")
parser.add_argument("--rules", required=True, help="Path to rules.json file")
parser.add_argument("--metadata", required=False, help="Optional path to metadata.json file")
```

**Why I changed it:**  
My project analyzes multiple documentation files in a folder, not a single input file. I updated the CLI arguments to match how my tool actually works.

---

### Example 2: Output File Location

**Original AI suggestion:**
```python
def write_json_report(reports, output_path="results.json"):
    results = [report.to_dict() for report in reports]
    with open(output_path, "w") as file:
        json.dump(results, file, indent=4)
```

**My modified version:**
```python
def write_json_report(reports, output_path="data/results.json"):
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    results = [report.to_dict() for report in reports]

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4)
```

**Why I changed it:**  
I wanted the results file to always be saved inside the `data/` folder to match the project structure and README instructions.

---

### Example 3: Rejected Overly Complex Design

**Original AI suggestion:**  
Suggested using multiple additional classes and advanced validation layers.

**My decision:**  
Rejected this design.

**Why I rejected it:**  
The design was unnecessarily complex for the assignment. I simplified the structure to keep the code clear, maintainable, and easy to explain during the demo.

---

## Verification Methods

I verified AI-assisted code by:

- Running the program using the CLI with sample documentation files  
- Checking output in `data/results.json` and `report.txt`  
- Running tests using:
  ```bash
  python -m pytest -v
  ```
- Confirming all 16 tests passed  
- Testing error cases such as missing files and invalid input  
- Reviewing logs for detected issues such as missing sections, missing terms, and stale documents  

---

## Reflection

Using AI tools helped speed up development and provided useful guidance for structuring the project, debugging errors, and writing tests. However, I learned that AI suggestions are not always correct or appropriate for the specific project.

One key lesson was the importance of understanding the code before using it. For example, AI initially suggested using `--input` and `--output`, but my actual program required `--docs`, `--rules`, and `--metadata`. I had to test and adjust these details to ensure everything worked correctly.

I also learned the importance of verifying all AI-generated code through testing and manual review. Running the program, checking outputs, and using pytest ensured that the final implementation was correct.

Overall, AI was a valuable support tool, but I remained responsible for reviewing, modifying, and validating all code to ensure it met the project requirements.
