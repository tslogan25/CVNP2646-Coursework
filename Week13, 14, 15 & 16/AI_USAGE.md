\# AI Usage Log



\## Week 14 AI Usage



\### Tools Used

\- ChatGPT

\- GitHub Copilot



\### How AI Was Used

AI was used to support implementation, debugging, and code refinement for the Documentation Quality Analyzer project.



\### Appropriate Uses

\- Generated starter argparse structure for the CLI

\- Suggested class structure for `DocumentationIssue`, `DocumentReport`, and `DocumentationAnalyzer`

\- Helped debug file path issues, import issues, indentation errors, and JSON parsing errors

\- Suggested improvements for error handling and logging

\- Helped improve report formatting and readability



\### Code I Accepted

\- Basic `argparse` setup in `main.py`

\- Class method structure for loading, checking, and reporting

\- Try/except error handling for missing files and invalid JSON

\- Logging setup with INFO/ERROR handling



\### Code I Modified

\- Adjusted AI-generated code to match my project requirements

\- Changed logic so the analyzer works with `.md` and `.txt` files in a docs folder

\- Simplified term detection logic to better fit the assignment scope

\- Improved report formatting to remove duplicate entries and make issue labels readable

\- Added `\_\_repr\_\_` methods to better match class implementation requirements



\### Code I Rejected

\- Rejected overly complex class designs that added unnecessary abstraction

\- Rejected suggestions that did not match the scope of the assignment

\- Rejected code that I could not clearly explain or verify



\### Verification Process

\- Ran the CLI with sample documentation files

\- Checked generated `results.json` and `report.txt`

\- Tested missing-file error handling with fake input

\- Ran unit tests using:

&#x20; `python -m unittest discover Tests`



\### What I Learned

\- How to build a structured Python project with `src`, `docs`, and `Tests`

\- How to use `argparse` for a professional CLI

\- How to load JSON safely and handle JSON errors

\- How to design and test simple OOP classes

\- How to debug common Python issues such as indentation, import paths, and file handling

