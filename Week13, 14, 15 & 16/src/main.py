"""
Main entry point for Documentation Quality Analyzer
"""

import argparse
import json
import logging
import os
import sys

from models import DocumentationAnalyzer


def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze documentation for completeness, staleness, and required terms"
    )
    parser.add_argument("--docs", required=True, help="Docs directory")
    parser.add_argument("--rules", required=True, help="Rules JSON file")
    parser.add_argument("--metadata", help="Metadata JSON file (optional)")
    parser.add_argument("--output", default="results.json", help="Output JSON file")
    parser.add_argument("--report", default="report.txt", help="Text report file")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(levelname)s: %(message)s"
    )

    try:
        logging.info("Starting Documentation Analyzer...")

        rules = load_json(args.rules)
        metadata = load_json(args.metadata) if args.metadata else None

        analyzer = DocumentationAnalyzer(rules, metadata)
        results = []

        for filename in os.listdir(args.docs):
            if filename.endswith(".md") or filename.endswith(".txt"):
                filepath = os.path.join(args.docs, filename)
                logging.info(f"Analyzing {filename}")
                report = analyzer.analyze_document(filepath)
                results.append(report.to_dict())

        with open(args.output, "w", encoding="utf-8") as f:
            json.dump({"results": results}, f, indent=2)

        with open(args.report, "w", encoding="utf-8") as f:
            for r in results:
                f.write(f"Document: {r['document']}\n")
                f.write(f"Score: {r['score']}\n\n")

                if r["issues"]:
                    f.write("Issues:\n")
                    for issue in r["issues"]:
                        label = issue["type"].replace("_", " ").title()
                        f.write(f"- {label}: {issue['details']}\n")
                else:
                    f.write("No issues found.\n")

                f.write("\n" + "-" * 40 + "\n\n")

        logging.info("Analysis complete.")

    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error during processing: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()