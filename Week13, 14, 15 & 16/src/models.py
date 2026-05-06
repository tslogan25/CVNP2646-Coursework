"""
Core classes for Documentation Quality Analyzer
"""

from datetime import datetime


class DocumentationIssue:
    """Represents a documentation issue"""

    def __init__(self, issue_type, description, severity="Medium"):
        self.issue_type = issue_type
        self.description = description
        self.severity = severity

    def __repr__(self):
        return f"DocumentationIssue({self.issue_type}, {self.severity})"


class DocumentReport:
    """Stores results for a document"""

    def __init__(self, filename):
        self.filename = filename
        self.score = 100
        self.issues = []

    def add_issue(self, issue, deduction=30):
        """Add issue and reduce score"""
        self.issues.append(issue)
        self.score = max(0, self.score - deduction)

    def calculate_score(self):
        """Ensure score never goes below 0"""
        self.score = max(0, self.score)

    def to_dict(self):
        """Convert report to dictionary"""

        return {
            "document": self.filename,
            "score": self.score,
            "issues": [
                {
                    "type": issue.issue_type,
                    "details": issue.description
                }
                for issue in self.issues
            ]
        }

    def __repr__(self):
        return f"DocumentReport({self.filename}, score={self.score})"


class DocumentationAnalyzer:
    """Analyzes technical documentation"""

    def __init__(self, rules, metadata=None):
        self.rules = rules
        self.metadata = metadata or {}

    def load_document(self, filepath):
        """Load document content"""

        with open(filepath, "r", encoding="utf-8") as file:
            return file.read()

    def check_sections(self, content):
        """Detect missing required sections"""

        issues = []

        required_sections = self.rules.get(
            "required_sections",
            []
        )

        for section in required_sections:

            if f"## {section}" not in content:

                issue = DocumentationIssue(
                    "missing_section",
                    f"{section} section not found"
                )

                issues.append(issue)

        return issues

    def check_terms(self, content):
        """Detect missing required terms"""

        issues = []

        required_terms = self.rules.get(
            "required_terms",
            []
        )

        content_lower = content.lower()

        for term in required_terms:

            if term.lower() not in content_lower:

                issue = DocumentationIssue(
                    "missing_term",
                    f"Required term '{term}' not found"
                )

                issues.append(issue)

        return issues

    def check_staleness(self, filename):
        """Check if document is stale"""

        issues = []

        documents = self.metadata.get(
            "documents",
            []
        )

        stale_after_days = self.rules.get(
            "stale_after_days",
            90
        )

        for document in documents:

            if document.get("file") == filename:

                last_updated = document.get(
                    "last_updated"
                )

                try:

                    updated_date = datetime.strptime(
                        last_updated,
                        "%Y-%m-%d"
                    )

                    current_date = datetime.now()

                    days_old = (
                        current_date - updated_date
                    ).days

                    if days_old > stale_after_days:

                        issue = DocumentationIssue(
                            "stale_doc",
                            f"{filename} is stale"
                        )

                        issues.append(issue)

                except Exception:
                    pass

        return issues

    def analyze_document(self, filepath):
        """Analyze a single document"""

        filename = filepath.split("\\")[-1].split("/")[-1]

        report = DocumentReport(filename)

        content = self.load_document(filepath)

        # Missing sections
        section_issues = self.check_sections(content)

        for issue in section_issues:
            report.add_issue(issue)

        # Missing terms
        term_issues = self.check_terms(content)

        for issue in term_issues:
            report.add_issue(issue)

        # Staleness
        stale_issues = self.check_staleness(filename)

        for issue in stale_issues:
            report.add_issue(issue)

        report.calculate_score()

        return report