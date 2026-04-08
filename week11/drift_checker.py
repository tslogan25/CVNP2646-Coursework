import json
import os


class DriftResult:
    """Represents a single configuration drift finding."""

    # Shared keyword list for simple severity scoring
    CRITICAL_KEYWORDS = ["password", "secret", "admin", "root", "enabled"]

    def __init__(self, path, drift_type, baseline_value, current_value):
        self.path = path
        self.drift_type = drift_type
        self.baseline_value = baseline_value
        self.current_value = current_value
        self.severity = self._calculate_severity()

    def _calculate_severity(self):
        """
        Determine severity using simple project rules:
        - HIGH if the path contains a critical keyword
        - MEDIUM if the drift type is 'missing'
        - LOW otherwise
        """
        path_lower = self.path.lower()

        for keyword in self.CRITICAL_KEYWORDS:
            if keyword in path_lower:
                return "HIGH"

        if self.drift_type == "missing":
            return "MEDIUM"

        return "LOW"

    def is_critical(self):
        """Return True if this finding is HIGH severity."""
        return self.severity == "HIGH"

    def to_dict(self):
        """Convert the result into a dictionary for JSON export."""
        return {
            "path": self.path,
            "drift_type": self.drift_type,
            "baseline_value": self.baseline_value,
            "current_value": self.current_value,
            "severity": self.severity,
        }

    def __str__(self):
        """Readable one-line output for reports."""
        symbol = {
            "changed": "~",
            "missing": "-",
            "extra": "+",
        }.get(self.drift_type, "?")

        return f"[{symbol}] {self.path} ({self.severity.lower()})"


def load_json_file(filename):
    """
    Load a JSON file safely.

    Returns:
        Parsed JSON object on success
        None on failure
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)

    except FileNotFoundError:
        print(f"[ERROR] File not found: {filename}")
        return None

    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in {filename}")
        print(f"        Line {e.lineno}, Column {e.colno}: {e.msg}")
        return None

    except Exception as e:
        print(f"[ERROR] Unexpected error while reading {filename}: {e}")
        return None


def build_path(current_path, key):
    """
    Build a dotted path for dictionary keys.

    Examples:
        build_path("", "logging") -> "logging"
        build_path("logging", "enabled") -> "logging.enabled"
    """
    if current_path:
        return f"{current_path}.{key}"
    return key


def build_list_path(current_path, index):
    """
    Build a list path.

    Examples:
        build_list_path("rules", 0) -> "rules[0]"
        build_list_path("server.ports", 1) -> "server.ports[1]"
    """
    return f"{current_path}[{index}]"


def compare_configs(baseline, current, path=""):
    """
    Recursively compare two JSON structures.

    Decision tree:
    1. If BOTH are dicts:
       - find missing keys
       - find extra keys
       - recurse only on common keys
    2. Else if BOTH are lists:
       - compare shared indices recursively
       - report missing/extra items without recursing
    3. Otherwise:
       - base case: compare values directly

    Important:
    Type checking order matters. We only call .keys() if BOTH values are dicts,
    and only use list indexing logic if BOTH values are lists. If types differ,
    the function falls through to the base case and records a changed value.
    """
    results = []

    # Case 1: both are dictionaries
    if isinstance(baseline, dict) and isinstance(current, dict):
        baseline_keys = set(baseline.keys())
        current_keys = set(current.keys())

        missing_keys = baseline_keys - current_keys
        extra_keys = current_keys - baseline_keys
        common_keys = baseline_keys & current_keys

        # Missing keys: drift already found, do not recurse
        for key in sorted(missing_keys):
            full_path = build_path(path, key)
            results.append(DriftResult(full_path, "missing", baseline[key], None))

        # Extra keys: drift already found, do not recurse
        for key in sorted(extra_keys):
            full_path = build_path(path, key)
            results.append(DriftResult(full_path, "extra", None, current[key]))

        # Common keys: recurse and EXTEND results
        for key in sorted(common_keys):
            full_path = build_path(path, key)
            nested_results = compare_configs(baseline[key], current[key], full_path)
            results.extend(nested_results)

    # Case 2: both are lists
    elif isinstance(baseline, list) and isinstance(current, list):
        min_len = min(len(baseline), len(current))

        # Shared indices: recurse and EXTEND results
        for i in range(min_len):
            idx_path = build_list_path(path, i)
            nested_results = compare_configs(baseline[i], current[i], idx_path)
            results.extend(nested_results)

        # Missing items from current
        for i in range(min_len, len(baseline)):
            idx_path = build_list_path(path, i)
            results.append(DriftResult(idx_path, "missing", baseline[i], None))

        # Extra items in current
        for i in range(min_len, len(current)):
            idx_path = build_list_path(path, i)
            results.append(DriftResult(idx_path, "extra", None, current[i]))

    # Case 3: base case
    else:
        if baseline != current:
            results.append(DriftResult(path, "changed", baseline, current))

    return results


def print_report(results):
    """Print a readable drift report."""
    print("\n=== DRIFT REPORT ===")

    if not results:
        print("\nNo drift detected.")
        return

    missing = [r for r in results if r.drift_type == "missing"]
    extra = [r for r in results if r.drift_type == "extra"]
    changed = [r for r in results if r.drift_type == "changed"]

    high = [r for r in results if r.severity == "HIGH"]
    medium = [r for r in results if r.severity == "MEDIUM"]
    low = [r for r in results if r.severity == "LOW"]

    print(f"\nTotal findings: {len(results)}")
    print(f"  Missing: {len(missing)}")
    print(f"  Extra:   {len(extra)}")
    print(f"  Changed: {len(changed)}")

    print("\nBy Severity:")
    print(f"  HIGH:   {len(high)}")
    print(f"  MEDIUM: {len(medium)}")
    print(f"  LOW:    {len(low)}")

    print("\nDetailed Findings:")
    for result in results:
        print(f"- [{result.severity}] {result.drift_type.upper()} {result.path}")
        if result.baseline_value is not None:
            print(f"    Baseline: {result.baseline_value}")
        if result.current_value is not None:
            print(f"    Current:  {result.current_value}")


def export_results_to_json(results, output_file):
    """Optional helper to save findings to a JSON file."""
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump([r.to_dict() for r in results], f, indent=2)
        print(f"\n[INFO] Results exported to: {output_file}")
    except Exception as e:
        print(f"\n[ERROR] Could not export results: {e}")


def main():
    """
    Main program flow:
    1. Load baseline.json and current.json from the script folder
    2. Compare them recursively
    3. Print the drift report
    4. Export findings to drift_report.json
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))

    baseline_path = os.path.join(base_dir, "baseline.json")
    current_path = os.path.join(base_dir, "current.json")
    output_path = os.path.join(base_dir, "drift_report.json")

    print("=== JSON DRIFT CHECKER ===")
    print(f"Looking for files in: {base_dir}")

    baseline = load_json_file(baseline_path)
    current = load_json_file(current_path)

    if baseline is None or current is None:
        print("\n[ERROR] Could not continue because one or both JSON files are missing or invalid.")
        return

    results = compare_configs(baseline, current)
    print_report(results)
    export_results_to_json(results, output_path)


if __name__ == "__main__":
    main()