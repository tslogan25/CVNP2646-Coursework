"""
Main entry point for Documentation Quality Analyzer
"""

import argparse
import json
import logging
from pathlib import Path

from models import DocumentationAnalyzer


def load_json_file(filepath):
    """Load JSON data from a file with helpful errors"""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"JSON file not found: {filepath}. Check the path and try again."
        )
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON in {filepath}: {error}"
        )


def validate_rules(rules):
    """Validate required rules.json fields"""
    required_fields = [
        "required_sections",
        "required_terms",
        "stale_after_days"
    ]

    missing_fields = [
        field for field in required_fields if field not in rules
    ]

    if missing_fields:
        raise ValueError(
            "rules.json is missing required field(s): "
            + ", ".join(missing_fields)
        )

    if not isinstance(rules["required_sections"], list):
        raise ValueError("rules.json field 'required_sections' must be a list")

    if not isinstance(rules["required_terms"], list):
        raise ValueError("rules.json field 'required_terms' must be a list")

    if not isinstance(rules["stale_after_days"], int):
        raise ValueError("rules.json field 'stale_after_days' must be an integer")


def validate_metadata(metadata):
    """Validate metadata.json structure if provided"""
    if not metadata:
        return

    if "documents" not in metadata:
        raise ValueError("metadata.json must contain a 'documents' field")

    if not isinstance(metadata["documents"], list):
        raise ValueError("metadata.json field 'documents' must be a list")

    for index, document in enumerate(metadata["documents"]):
        if "file" not in document:
            raise ValueError(f"metadata document {index} is missing 'file'")

        if "last_updated" not in document:
            raise ValueError(f"metadata document {index} is missing 'last_updated'")


def write_json_report(reports, output_path="data/results.json"):
    """Write analysis results to JSON file"""
    results = {
        "results": [report.to_dict() for report in reports]
    }

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4)


def write_text_report(reports, output_path="report.txt"):
    """Write human-readable report"""
    with open(output_path, "w", encoding="utf-8") as file:
        file.write("Documentation Quality Analyzer Report\n")
        file.write("=" * 50 + "\n\n")

        for report in reports:
            file.write(f"Document: {report.filename}\n")
            file.write(f"Score: {report.score}\n")
            file.write("Issues:\n")

            if report.issues:
                for issue in report.issues:
                    file.write(
                        f"- {issue.issue_type}: {issue.description}\n"
                    )
            else:
                file.write("- No issues found\n")

            file.write("\n")


def main():
    """Run Documentation Quality Analyzer"""
    parser = argparse.ArgumentParser(
        description="Analyze technical documentation quality."
    )

    parser.add_argument(
        "--docs",
        required=True,
        help="Directory containing Markdown or text documentation files"
    )

    parser.add_argument(
        "--rules",
        required=True,
        help="Path to rules JSON file"
    )

    parser.add_argument(
        "--metadata",
        required=False,
        help="Path to metadata JSON file"
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s"
    )

    logging.info("Starting Documentation Analyzer...")

    try:
        rules = load_json_file(args.rules)
        validate_rules(rules)

        metadata = {}
        if args.metadata:
            metadata = load_json_file(args.metadata)
            validate_metadata(metadata)

        docs_path = Path(args.docs)

        if not docs_path.exists():
            logging.error(f"Documentation directory not found: {docs_path}")
            return

        if not docs_path.is_dir():
            logging.error(f"Docs path is not a directory: {docs_path}")
            return

        analyzer = DocumentationAnalyzer(rules, metadata)

        reports = []

        for filepath in docs_path.iterdir():

            if filepath.is_dir():
                logging.warning(f"Skipping directory: {filepath.name}")
                continue

            if filepath.suffix.lower() not in [".md", ".txt"]:
                logging.warning(f"Skipping unsupported file: {filepath.name}")
                continue

            try:
                logging.info(f"Analyzing {filepath.name}")
                logging.info(f"Analyzing document: {filepath.name}")

                report = analyzer.analyze_document(str(filepath))

                for issue in report.issues:
                    if issue.issue_type == "missing_section":
                        logging.warning(
                            "Missing section detected: "
                            f"{issue.description.replace(' section not found', '')}"
                        )

                    elif issue.issue_type == "missing_term":
                        logging.warning(
                            "Missing required term detected: "
                            f"{issue.description.replace('Required term ', '').replace(' not found', '')}"
                        )

                    elif issue.issue_type == "stale_doc":
                        logging.warning(
                            f"Stale document detected: {report.filename}"
                        )

                logging.info(
                    f"Completed analysis for {report.filename}: "
                    f"score={report.score}, "
                    f"issues={len(report.issues)}"
                )

                reports.append(report)

            except Exception as error:
                logging.error(
                    f"Failed to analyze {filepath.name}: {error}"
                )
                continue

        write_json_report(reports, "data/results.json")
        write_text_report(reports, "report.txt")

        logging.info("Analysis complete.")

    except FileNotFoundError as error:
        logging.error(error)

    except ValueError as error:
        logging.error(error)

    except Exception as error:
        logging.error(f"Unexpected error: {error}")


if __name__ == "__main__":
    main()