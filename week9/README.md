# Patch Tracker - Risk-Based Patch Management Tool

## 1. Overview

The Patch Tracker is a Python-based security tool designed to analyze system patch status and identify high-risk hosts based on multiple risk factors. It processes a JSON inventory of systems, calculates patch age, assigns a risk score, categorizes risk levels, and generates both machine-readable (JSON) and human-readable (text) reports.

Patch management is critical for cybersecurity because unpatched systems are one of the most common attack vectors. Vulnerabilities in outdated software can be exploited by attackers to gain unauthorized access, execute malicious code, or exfiltrate sensitive data. Timely patching reduces the attack surface and is a core requirement of most security frameworks.

---

## 2. Risk Scoring Algorithm

The tool calculates a **risk score (0–100)** based on six key factors:

| Factor              | Condition                          | Points                |
|--------------------|------------------------------------|----------------------|
| Criticality        | critical / high / medium / low     | 40 / 25 / 10 / 5     |
| Patch Age          | >90 / >60 / >30 days               | 30 / 20 / 10         |
| Environment        | production / staging / development | 15 / 8 / 3           |
| PCI Scope          | pci-scope tag present              | +10                  |
| HIPAA Scope        | hipaa tag present                  | +10                  |
| Internet-Facing    | internet-facing tag present        | +15                  |

### Key Notes:
- Patch age is evaluated in descending order (>90 first).
- Total score is capped at **100**.
- Missing or invalid data defaults to safe values (0 points).

---

## 3. CIS Benchmark Alignment

This tool aligns with **CIS Critical Security Control 7.3**:

> *"Perform automated patch management for operating systems and applications."*

### Implementation:
- Identifies systems with outdated patches
- Prioritizes remediation based on risk
- Highlights systems exceeding acceptable patch timelines

### Risk Level → Remediation Timeline:

| Risk Level | Score Range | Recommended Action Timeline |
|-----------|------------|-----------------------------|
| Critical  | ≥70        | Immediate (within 48 hours) |
| High      | 50–69      | Within 7 days               |
| Medium    | 25–49      | Within 30 days              |
| Low       | <25        | Routine patch cycle         |

---

## 4. Functions Overview

The script includes the following key functions:

- `load_inventory()` – Loads host data from JSON file
- `calculate_days_since_patch()` – Computes days since last patch
- `filter_by_os()` – Filters hosts by operating system
- `filter_by_criticality()` – Filters by criticality level
- `filter_by_environment()` – Filters by environment
- `calculate_risk_score()` – Multi-factor risk scoring engine
- `get_risk_level()` – Converts numeric score to risk category
- `get_high_risk_hosts()` – Filters and sorts high-risk hosts
- `generate_json_report()` – Creates structured JSON output
- `generate_text_summary()` – Creates human-readable report
- `main execution block` – Orchestrates full workflow

---

## 5. Sample Output

Example results from running the tool: