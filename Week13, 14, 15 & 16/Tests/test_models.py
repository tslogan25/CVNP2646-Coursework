"""
Unit tests for Documentation Quality Analyzer models.
"""

import sys
import os
import pytest

# Add src directory to Python path
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../src")
    )
)

from models import DocumentationAnalyzer


def test_documentation_analyzer_creation():
    """
    Test that DocumentationAnalyzer can be created successfully.
    """

    rules = {
        "required_sections": [
            "Setup",
            "Usage",
            "Troubleshooting",
            "Prerequisites"
        ],
        "required_terms": [
            "nginx"
        ],
        "stale_after_days": 180
    }

    metadata = {}

    analyzer = DocumentationAnalyzer(
        rules=rules,
        metadata=metadata
    )

    assert analyzer is not None
    assert analyzer.rules == rules
    assert analyzer.metadata == metadata


def test_required_sections_exist():
    """
    Test that required sections are loaded correctly.
    """

    rules = {
        "required_sections": [
            "Setup",
            "Usage"
        ],
        "required_terms": [],
        "stale_after_days": 180
    }

    analyzer = DocumentationAnalyzer(
        rules=rules,
        metadata={}
    )

    assert "Setup" in analyzer.rules["required_sections"]
    assert "Usage" in analyzer.rules["required_sections"]


def test_required_terms_exist():
    """
    Test that required technical terms are loaded correctly.
    """

    rules = {
        "required_sections": [],
        "required_terms": [
            "nginx",
            "docker"
        ],
        "stale_after_days": 180
    }

    analyzer = DocumentationAnalyzer(
        rules=rules,
        metadata={}
    )

    assert "nginx" in analyzer.rules["required_terms"]
    assert "docker" in analyzer.rules["required_terms"]


def test_stale_after_days_setting():
    """
    Test that stale document threshold is stored correctly.
    """

    rules = {
        "required_sections": [],
        "required_terms": [],
        "stale_after_days": 90
    }

    analyzer = DocumentationAnalyzer(
        rules=rules,
        metadata={}
    )

    assert analyzer.rules["stale_after_days"] == 90


def test_empty_rules():
    """
    Test analyzer with empty rules configuration.
    """

    rules = {
        "required_sections": [],
        "required_terms": [],
        "stale_after_days": 0
    }

    analyzer = DocumentationAnalyzer(
        rules=rules,
        metadata={}
    )

    assert analyzer is not None
    assert analyzer.rules["required_sections"] == []
    assert analyzer.rules["required_terms"] == []


def test_metadata_storage():
    """
    Test that metadata is stored correctly.
    """

    metadata = {
        "server_setup.md": {
            "last_updated": "2024-01-01"
        }
    }

    analyzer = DocumentationAnalyzer(
        rules={},
        metadata=metadata
    )

    assert "server_setup.md" in analyzer.metadata
    assert analyzer.metadata["server_setup.md"]["last_updated"] == "2024-01-01"