1. Overview

This project is a Python-based Identity and Access Management (IAM) auditing tool that analyzes user accounts and role assignments to detect security risks and policy violations.

The auditor identifies issues such as:

Disabled accounts that still have permissions
Unauthorized administrative privileges
Inactive (stale) accounts

IAM auditing is critical for security because misconfigured accounts are a common attack vector. Regular audits help enforce least privilege, reduce risk exposure, and maintain compliance with organizational policies.

2. Data Relationship

This system uses two datasets:

Users Dataset

Contains account-level information:

user_id (Primary Key)
username
status (active / disabled)
department
last_login
Roles Dataset

Contains permission assignments:

user_id (Foreign Key)
role
assigned_date
How the Data is Joined

The datasets are linked using user_id.

To optimize performance, a dictionary is built:

users_dict = {user['user_id']: user for user in users_data}

This enables:

O(1) lookup time for user records
Avoids repeated list scans (O(n))
Improves scalability for large datasets

Without this approach, each role lookup would require iterating through the entire user list, significantly increasing runtime.

3. Detection Rules

The auditor implements the following rules:

Rule 1: Disabled Users with Active Roles
Severity: CRITICAL
Detects accounts that are disabled but still have assigned roles
Risk: Unauthorized access if the account is reactivated or misused
Rule 2: Unauthorized Admin Assignments
Severity: HIGH
Flags admin roles assigned to users outside authorized departments (IT, Security)
Risk: Privilege escalation and insider threats
Rule 3: Stale Accounts
Severity: MEDIUM
Identifies active users who have not logged in for 90+ days
Risk: Dormant accounts are attractive targets for attackers
4. AI-Assisted Development

I used ChatGPT to help structure the development process and refine detection logic.

Prompt

"I'm building a user account auditor. I have user data and role assignments.
I've implemented 3 rules. What are 5 additional anomalies to detect?"

AI Suggestions
Conflicting roles (auditor + admin) — NOT IMPLEMENTED
Excessive permissions (>5 roles) — NOT IMPLEMENTED
Orphaned roles — REJECTED (insufficient test data)
Service account pattern detection — CONSIDERED but not implemented
Department validation — OUT OF SCOPE
Notes

The AI-assisted suggestions helped identify potential extensions for future improvements, but only the first three core rules were implemented in this version.

5. Test Results

Results from the provided dataset:

Total violations: 7
CRITICAL: 6 (disabled users with active roles)
HIGH: 1 (unauthorized admin assignment)
MEDIUM: 0 (no stale accounts detected)
Example Findings
Disabled users retaining roles:
asmith → hr_manager
martinl → security_admin
Unauthorized admin:
mooreb (Marketing) → marketing_admin
6. Output

The auditor generates:

Console Output
Summary of violations
Breakdown by severity
Detailed findings
Saved Reports
audit_report.txt → human-readable report
audit_report.json → structured data for further processing
Summary

This project demonstrates how structured data processing and rule-based analysis can identify IAM security risks efficiently. By using dictionary-based lookups (O(1)) and modular rule functions, the system is both scalable and extensible for future enhancements.