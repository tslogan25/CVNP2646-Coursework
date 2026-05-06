import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from models import DocumentationAnalyzer, DocumentationIssue, DocumentReport


@pytest.fixture
def sample_rules():
    return {
        "required_sections": ["Overview", "Setup", "Usage"],
        "required_terms": ["nginx"],
        "stale_after_days": 90,
        "weights": {
            "missing_section": 30,
            "stale_doc": 25,
            "missing_term": 15
        }
    }


def test_analyzer_can_be_created(sample_rules):
    analyzer = DocumentationAnalyzer(sample_rules)

    assert analyzer.rules == sample_rules
    assert analyzer.metadata == {}


def test_check_sections_normal_case(sample_rules):
    analyzer = DocumentationAnalyzer(sample_rules)

    content = """
## Overview
This is the overview.

## Setup
Install nginx.

## Usage
Run the service.
"""

    issues = analyzer.check_sections(content)

    assert issues == []


def test_check_sections_missing_section(sample_rules):
    analyzer = DocumentationAnalyzer(sample_rules)

    content = """
## Overview
This is the overview.

## Setup
Install nginx.
"""

    issues = analyzer.check_sections(content)

    assert len(issues) == 1
    assert issues[0].issue_type == "missing_section"
    assert "Usage" in issues[0].description


def test_check_terms_normal_case(sample_rules):
    analyzer = DocumentationAnalyzer(sample_rules)

    content = "Install nginx before starting the service."

    issues = analyzer.check_terms(content)

    assert issues == []


def test_check_terms_missing_term(sample_rules):
    analyzer = DocumentationAnalyzer(sample_rules)

    content = "Install the web server before starting the service."

    issues = analyzer.check_terms(content)

    assert len(issues) == 1
    assert issues[0].issue_type == "missing_term"
    assert "nginx" in issues[0].description


def test_empty_document_detects_missing_items(sample_rules):
    analyzer = DocumentationAnalyzer(sample_rules)

    content = ""

    section_issues = analyzer.check_sections(content)
    term_issues = analyzer.check_terms(content)

    assert len(section_issues) == 3
    assert len(term_issues) == 1


def test_document_report_to_dict():
    report = DocumentReport("test.md")
    issue = DocumentationIssue("missing_section", "Usage section not found")

    report.add_issue(issue, 30)

    result = report.to_dict()

    assert result["document"] == "test.md"
    assert result["score"] == 70
    assert result["issues"][0]["type"] == "missing_section"
    assert result["issues"][0]["details"] == "Usage section not found"


def test_load_document_reads_file(sample_rules):
    analyzer = DocumentationAnalyzer(sample_rules)

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md", encoding="utf-8") as temp_file:
        temp_file.write("## Overview\nTest document")
        temp_path = temp_file.name

    try:
        content = analyzer.load_document(temp_path)
        assert "Test document" in content
    finally:
        os.remove(temp_path)


def test_missing_file_raises_error(sample_rules):
    analyzer = DocumentationAnalyzer(sample_rules)

    with pytest.raises(FileNotFoundError):
        analyzer.load_document("nonexistent_file.md")