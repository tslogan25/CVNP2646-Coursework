import unittest
import sys
import os

# Fix import path so Python can find src/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from models import DocumentationAnalyzer, DocumentationIssue, DocumentReport


class TestDocumentationAnalyzer(unittest.TestCase):

    def setUp(self):
        self.rules = {
            "required_sections": ["Overview", "Setup"],
            "required_terms": ["nginx"],
            "stale_after_days": 90,
            "weights": {
                "missing_section": 10,
                "missing_term": 5,
                "stale_doc": 5
            }
        }
        self.analyzer = DocumentationAnalyzer(self.rules)

    def test_missing_section(self):
        content = "## Overview\nContent here"
        issues = self.analyzer.check_sections(content)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].issue_type, "missing_section")

    def test_missing_term(self):
        content = "## Overview\n## Setup\nNo keyword here"
        issues = self.analyzer.check_terms(content)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].issue_type, "missing_term")

    def test_no_issues(self):
        content = "## Overview\n## Setup\nnginx is installed"
        section_issues = self.analyzer.check_sections(content)
        term_issues = self.analyzer.check_terms(content)

        self.assertEqual(len(section_issues), 0)
        self.assertEqual(len(term_issues), 0)

    def test_stale_document(self):
        metadata = {
            "documents": [
                {
                    "file": "old_doc.md",
                    "last_updated": "2025-01-01",
                    "owner": "IT Operations"
                }
            ]
        }

        analyzer = DocumentationAnalyzer(self.rules, metadata)
        issues = analyzer.check_staleness("old_doc.md")

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].issue_type, "stale_doc")

    def test_analyze_document(self):
        test_file = "temp_test_doc.md"

        with open(test_file, "w", encoding="utf-8") as f:
            f.write("## Overview\n## Setup\nnginx is installed")

        report = self.analyzer.analyze_document(test_file)

        self.assertEqual(report.filename, "temp_test_doc.md")
        self.assertEqual(len(report.issues), 0)
        self.assertEqual(report.score, 100)

        os.remove(test_file)

    def test_report_to_dict(self):
        issue = DocumentationIssue("missing_section", "Setup section not found")
        report = DocumentReport("test.md")
        report.add_issue(issue, 10)
        report.calculate_score()

        result = report.to_dict()

        self.assertEqual(result["document"], "test.md")
        self.assertEqual(result["score"], 90)
        self.assertEqual(len(result["issues"]), 1)
        self.assertEqual(result["issues"][0]["type"], "missing_section")


if __name__ == "__main__":
    unittest.main()