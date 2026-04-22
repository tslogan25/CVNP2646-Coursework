"""
Core classes for Documentation Quality Analyzer
"""

import os
from datetime import datetime


class DocumentationIssue:
    """
    Represents a single issue found in a document.
    """

    def __init__(self, issue_type, description, severity="medium"):
        self.issue_type = issue_type
        self.description = description
        self.severity = severity

    def __repr__(self):
        return (
            f"DocumentationIssue(type={self.issue_type}, "
            f"description={self.description}, severity={self.severity})"
        )

    def to_dict(self):
        return {
            "type": self.issue_type,
            "details": self.description
        }


class DocumentReport:
    """
    Stores analysis results for a single document.
    """

    def __init__(self, filename):
        self.filename = filename
        self.score = 100
        self.issues = []

    def __repr__(self):
        return (
            f"DocumentReport(filename={self.filename}, "
            f"score={self.score}, issues={len(self.issues)})"
        )

    def add_issue(self, issue, weight=0):
        """Add an issue to the report and deduct its weight from the score."""
        self.issues.append(issue)
        self.score = max(0, self.score - weight)

    def calculate_score(self):
        """Ensure score does not drop below 0."""
        self.score = max(0, self.score)

    def to_dict(self):
        return {
            "document": self.filename,
            "score": self.score,
            "issues": [issue.to_dict() for issue in self.issues]
        }


class DocumentationAnalyzer:
    """
    Main analyzer class for processing documentation files.
    """

    def __init__(self, rules, metadata=None):
        self.rules = rules
        self.metadata = metadata or {}

    def load_document(self, filepath):
        """Load document content from file."""
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    def check_sections(self, content):
        """Check for required sections."""
        issues = []
        content_lower = content.lower()

        for section in self.rules.get("required_sections", []):
            if section.lower() not in content_lower:
                issues.append(
                    DocumentationIssue(
                        "missing_section",
                        f"{section} section not found"
                    )
                )
        return issues

    def check_terms(self, content):
        """Check for required terms."""
        issues = []
        content_lower = content.lower()

        found_any_required_term = any(
            term.lower() in content_lower
            for term in self.rules.get("required_terms", [])
        )

        if not found_any_required_term:
            for term in self.rules.get("required_terms", []):
                issues.append(
                    DocumentationIssue(
                        "missing_term",
                        f"Required term '{term}' not found"
                    )
                )
                break

        return issues

    def check_staleness(self, filename):
        """Check if document is outdated based on metadata."""
        issues = []

        if not self.metadata:
            return issues

        for doc in self.metadata.get("documents", []):
            if doc.get("file") == filename:
                last_updated = doc.get("last_updated")
                if not last_updated:
                    return issues

                last_updated_date = datetime.strptime(last_updated, "%Y-%m-%d")
                days_old = (datetime.now() - last_updated_date).days

                if days_old > self.rules.get("stale_after_days", 90):
                    issues.append(
                        DocumentationIssue(
                            "stale_doc",
                            f"Document is {days_old} days old"
                        )
                    )
                break

        return issues

    def analyze_document(self, filepath):
        """Analyze a single document and return a DocumentReport."""
        filename = os.path.basename(filepath)
        content = self.load_document(filepath)

        report = DocumentReport(filename)

        section_issues = self.check_sections(content)
        for issue in section_issues:
            report.add_issue(issue, self.rules["weights"]["missing_section"])

        term_issues = self.check_terms(content)
        for issue in term_issues:
            report.add_issue(issue, self.rules["weights"]["missing_term"])

        stale_issues = self.check_staleness(filename)
        for issue in stale_issues:
            report.add_issue(issue, self.rules["weights"]["stale_doc"])

        report.calculate_score()
        return report


if __name__ == "__main__":
    issue = DocumentationIssue("missing_section", "Setup section not found")
    report = DocumentReport("server_setup.md")
    report.add_issue(issue, 30)

    print(issue)
    print(report)