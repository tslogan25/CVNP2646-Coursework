1. Overview

This project implements a JSON configuration drift checker that compares a baseline configuration against a current configuration to identify differences.

The tool detects missing, extra, and changed configuration values, helping identify potential security issues or unintended system changes.

Configuration monitoring is critical in cybersecurity because unauthorized or accidental changes can weaken defenses, disable logging, or expose services to the internet. Detecting drift early helps maintain system integrity and security.

2. Drift Types

The drift checker identifies three types of configuration drift:

Missing
A key exists in the baseline but not in the current configuration.
This indicates a lost configuration or removed security control.

Example:

Baseline: { "logging": true }
Current: { }
Result: logging is missing

Extra
A key exists in the current configuration but not in the baseline.
This indicates a potential unauthorized addition.

Example:

Baseline: { }
Current: { "debug": true }
Result: debug is extra

Changed
A key exists in both configurations, but the values differ.
This indicates a modified setting.

Example:

Baseline: { "port": 443 }
Current: { "port": 8080 }
Result: port is changed
3. How Recursion Works

The core function, compare_configs, uses recursion to handle nested JSON structures.

The function follows a decision process:

If both values are dictionaries:
Identify missing keys (in baseline but not current)
Identify extra keys (in current but not baseline)
Recurse only on keys that exist in both configurations
If both values are lists:
Compare elements by index
Recurse on matching indices
Record extra or missing items without recursion
If neither condition applies:
Base case: compare the values directly

This approach allows the function to traverse arbitrarily deep structures and build precise paths such as logging.enabled or rules[0].port.

4. DriftResult Class

The DriftResult class represents a single drift finding and encapsulates both data and behavior.

Attributes:

path: location of the drift (e.g., rules[1].source)
drift_type: missing, extra, or changed
baseline_value: original value
current_value: new value
severity: HIGH, MEDIUM, or LOW

Methods:

_calculate_severity()
Assigns severity based on simple rules:
HIGH if the path contains critical keywords (e.g., "enabled", "admin")
MEDIUM if the drift type is missing
LOW otherwise
__str__()
Returns a formatted string such as:
[~] logging.enabled (high)
to_dict()
Converts the result into a dictionary for JSON export
is_critical()
Returns True if the severity is HIGH

Using a class improves readability, organization, and scalability compared to using plain dictionaries.

5. Test Results

Testing was performed using a firewall-style configuration.

Total findings: 6
Severity breakdown:

HIGH: 2
MEDIUM: 2
LOW: 2

Critical findings:

logging.enabled changed from True to False
→ Logging disabled, reducing visibility
rules[1].source changed from 10.0.0.0/8 to 0.0.0.0/0
→ Internal access changed to public exposure

Additional findings:

Missing logging destination
Port change from 443 to 8080
Extra debug rule added on port 9999

These results demonstrate the tool’s ability to detect both functional and security-relevant configuration drift.

6. Challenges Encountered

Recursion Logic
Understanding when to recurse versus when to stop was a key challenge. The correct approach is to recurse only on shared structures (common keys or indices) and not on missing or extra items.

append() vs extend()
A major issue was handling recursive results correctly:

Using append() created nested lists and broke processing
Using extend() correctly merged results into a flat list

Path Building
Constructing accurate paths required careful handling:

Avoid leading dots (e.g., .logging)
Correct formats include logging.enabled and rules[0].port

Type Checking Order
Incorrect type checking caused runtime errors. The solution was to ensure both values are the same type before accessing methods like .keys().

Example:

Always check both are dictionaries before calling .keys()
If types differ, fall back to the base case comparison
Conclusion

This project demonstrates how to build a recursive configuration comparison tool capable of analyzing complex nested JSON structures.

It combines:

Recursive traversal
Path tracking
Object-oriented design
Security-focused drift detection

The final solution provides clear, structured output and can be extended for real-world use cases such as security monitoring and compliance validation.