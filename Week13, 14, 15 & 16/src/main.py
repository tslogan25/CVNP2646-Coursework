"""
Main entry point for Documentation Quality Analyzer
"""

import argparse
import json
import logging
import os
import sys

from models import DocumentationAnalyzer


def load_json_file(filepath):
    """Load a JSON file and return parsed data."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)


def write_json_report(reports, output_path="results.json"):
    """Write analysis results to a JSON file."""
    results = [report.to_dict() for report in reports]

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4)


def write_text_report(reports, output_path="report.txt"):
    """Write analysis results to a readable text report."""
    with open(output_path, "w", encoding="utf-8") as file:
        file.write("Documentation Quality Analysis Report\n")
        file.write("=" * 45 + "\n\n")

        for report in reports:
            file.write(f"File: {report.filename}\n")
            file.write(f"Score: {report.score}\n\n")

            if report.issues:
                file.write("Issues:\n")
                for issue in report.issues:
                    label = issue.issue_type.replace("_", " ").title()
                    file.write(f"- {label}: {issue.description}\n")
            else:
                file.write("Issues: None\n")

            file.write("\n" + "-" * 45 + "\n\n")


def setup_logging():
    """Configure console and file logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
        handlers=[
            logging.FileHandler("documentation_analyzer.log", mode="w"),
            logging.StreamHandler()
        ]
    )


def main():
    """Run the Documentation Quality Analyzer."""
    parser = argparse.ArgumentParser(
        description=(
            "Documentation Quality Analyzer - checks documentation "
            "for required sections, required terms, and stale content."
        )
    )

    parser.add_argument(
        "--docs",
        required=True,
        help="Path to documentation folder"
    )

    parser.add_argument(
        "--rules",
        required=True,
        help="Path to rules.json file"
    )

    parser.add_argument(
        "--metadata",
        required=False,
        help="Optional path to metadata.json file"
    )

    args = parser.parse_args()
    setup_logging()

    try:
        logging.info("Starting Documentation Analyzer...")

        if not os.path.isdir(args.docs):
            logging.error(f"Docs folder not found: {args.docs}")
            sys.exit(1)

        rules = load_json_file(args.rules)

        metadata = None
        if args.metadata:
            metadata = load_json_file(args.metadata)

        analyzer = DocumentationAnalyzer(rules, metadata)
        reports = []

        for filename in os.listdir(args.docs):
            filepath = os.path.join(args.docs, filename)

            if not os.path.isfile(filepath):
                logging.warning(f"Skipping folder or invalid path: {filepath}")
                continue

            if not filename.lower().endswith((".md", ".txt")):
                logging.warning(f"Skipping unsupported file type: {filename}")
                continue

            try:
                logging.info(f"Analyzing {filename}")
                report = analyzer.analyze_document(filepath)
                reports.append(report)

            except Exception as error:
                logging.error(f"Failed to analyze {filename}: {error}")
                continue

        write_json_report(reports)
        write_text_report(reports)

        logging.info("Analysis complete.")

    except Exception as error:
        logging.error(f"Program failed: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()