import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from models import DocumentationIssue, DocumentReport, DocumentationAnalyzer


def test_documentation_issue_creation():
    issue = DocumentationIssue(
        "missing_section",
        "Missing section: Troubleshooting",
        "medium"
    )

    assert issue.issue_type == "missing_section"
    assert issue.description == "Missing section: Troubleshooting"
    assert issue.severity == "medium"


def test_documentation_issue_to_dict():
    issue = DocumentationIssue(
        "missing_term",
        "Required term 'nginx' not found"
    )

    result = issue.to_dict()

    assert result["type"] == "missing_term"
    assert result["details"] == "Required term 'nginx' not found"


def test_document_report_creation():
    report = DocumentReport("server_setup.md")

    assert report.filename == "server_setup.md"
    assert report.score == 100
    assert report.issues == []


def test_document_report_add_issue():
    report = DocumentReport("server_setup.md")
    issue = DocumentationIssue("missing_section", "Setup section not found")

    report.add_issue(issue, weight=30)

    assert len(report.issues) == 1
    assert report.score == 70


def test_document_report_score_never_below_zero():
    report = DocumentReport("server_setup.md")
    issue1 = DocumentationIssue("missing_section", "Setup section not found")
    issue2 = DocumentationIssue("missing_term", "Required term not found")

    report.add_issue(issue1, weight=80)
    report.add_issue(issue2, weight=80)

    assert report.score == 0


def test_document_report_to_dict():
    report = DocumentReport("server_setup.md")
    issue = DocumentationIssue("missing_section", "Setup section not found")

    report.add_issue(issue, weight=30)
    result = report.to_dict()

    assert result["document"] == "server_setup.md"
    assert result["score"] == 70
    assert result["issues"][0]["type"] == "missing_section"
    assert result["issues"][0]["details"] == "Setup section not found"


def test_analyzer_check_sections_normal_case():
    rules = {
        "required_sections": ["Overview", "Setup"],
        "required_terms": [],
        "stale_after_days": 90,
        "weights": {
            "missing_section": 30,
            "missing_term": 15,
            "stale_doc": 25
        }
    }

    analyzer = DocumentationAnalyzer(rules)
    content = "# Overview\nThis is an overview."

    issues = analyzer.check_sections(content)

    assert len(issues) == 1
    assert issues[0].issue_type == "missing_section"


def test_analyzer_check_terms_normal_case():
    rules = {
        "required_sections": [],
        "required_terms": ["nginx", "systemctl"],
        "stale_after_days": 90,
        "weights": {
            "missing_section": 30,
            "missing_term": 15,
            "stale_doc": 25
        }
    }

    analyzer = DocumentationAnalyzer(rules)
    content = "This guide explains how to use nginx."

    issues = analyzer.check_terms(content)

    assert issues == []


def test_analyzer_empty_content():
    rules = {
        "required_sections": ["Overview"],
        "required_terms": ["nginx"],
        "stale_after_days": 90,
        "weights": {
            "missing_section": 30,
            "missing_term": 15,
            "stale_doc": 25
        }
    }

    analyzer = DocumentationAnalyzer(rules)
    issues = analyzer.check_sections("")

    assert len(issues) == 1
    assert issues[0].issue_type == "missing_section"


def test_missing_file_raises_error():
    rules = {
        "required_sections": [],
        "required_terms": [],
        "stale_after_days": 90,
        "weights": {
            "missing_section": 30,
            "missing_term": 15,
            "stale_doc": 25
        }
    }

    analyzer = DocumentationAnalyzer(rules)

    with pytest.raises(FileNotFoundError):
        analyzer.load_document("missing_file.md")