Threat Intelligence Feed Aggregator
1. Overview

This project implements a Threat Intelligence Feed Aggregator written in Python.
The purpose of the aggregator is to collect threat indicators from multiple vendor feeds, normalize their formats, validate data quality, remove duplicates, apply filtering rules, and generate output formats usable by security tools.

The aggregator processes three different vendor feeds:

VendorA

VendorB

VendorC

Each feed represents a different threat intelligence provider using its own schema and field naming conventions.

Using multiple feeds improves security coverage because:

Different vendors detect different threats

Overlapping indicators increase confidence

Combined sources improve threat attribution and validation

The aggregator performs the following pipeline:

Load feeds

Normalize schemas

Validate indicators

Deduplicate duplicates

Apply filtering rules

Generate outputs

Calculate statistics

2. Feed Schemas

Each vendor uses different field names for the same data.

Standard Field	VendorA	VendorB	VendorC
type	type	indicator_type	ioc_type
value	value	indicator_value	ioc
confidence	confidence	confidence_score	confidence_level
threat_level	threat	severity	severity_level
source	implicit	feed	origin

Example differences:

VendorA example

{
"type": "ip",
"value": "203.0.113.50",
"confidence": "high",
"threat": "critical"
}

VendorB example

{
"indicator_type": "ipv4",
"indicator_value": "203.0.113.50",
"confidence_score": "medium",
"severity": "critical"
}

VendorC example

{
"ioc_type": "fqdn",
"ioc": "login-security-check.com",
"confidence_level": "high",
"severity_level": "high"
}

These differences require normalization before processing.

3. Normalization Strategy

The aggregator uses a flexible normalization approach using .get() chaining.

Instead of writing vendor-specific parsing code, the script checks for multiple possible field names:

Example:

type_val = (
    raw_indicator.get("type")
    or raw_indicator.get("indicator_type")
    or raw_indicator.get("ioc_type")
)

This allows the same function to process all feeds without needing vendor-specific logic.

Additional normalization steps include:

Type normalization

Vendor-specific types are mapped to standard types:

Vendor Type	Standard Type
ipv4	ip
fqdn	domain
domain_name	domain
sha256	hash
Confidence normalization

Confidence values are converted to numeric scores:

Vendor Value	Standard Value
low	25
medium	50
high	90
critical	100

This ensures all indicators can be compared consistently.

4. Deduplication Logic

The aggregator removes duplicate indicators across feeds.

Duplicate Identification

Two indicators are considered duplicates when they have the same:

(type, value)

Example key used:

key = (indicator["type"], indicator["value"])

This allows indicators from different vendors to be matched even if their schemas differ.

Duplicate Resolution

When duplicates are found, the aggregator keeps the indicator with the highest confidence score.

Example logic:

if indicator["confidence"] > existing["confidence"]:
    replace existing indicator

Higher confidence indicates stronger threat intelligence.

Source Merging

Even when one indicator is kept, all contributing sources are preserved.

Example:

VendorA

203.0.113.50 confidence 90

VendorB

203.0.113.50 confidence 50

Result:

{
"type": "ip",
"value": "203.0.113.50",
"confidence": 90,
"sources": ["VendorA", "VendorB"]
}

This ensures visibility into which feeds reported the threat.

5. Test Data

Three test feeds were created.

VendorA

Total indicators: 6

Includes:

1 critical IP

2 high domains

1 medium hash

1 low confidence IP

1 URL

VendorB

Total indicators: 6

Includes:

duplicate IP from VendorA (different confidence)

high domain

hash

URL

low IP

one intentionally invalid indicator (missing confidence)

VendorC

Total indicators: 6

Includes:

duplicate domain from VendorA

critical IP

hash

URL

domain

one invalid type (email)

Expected Duplicates

Two duplicates exist across feeds:

Indicator	Vendors
203.0.113.50	VendorA + VendorB
login-security-check.com	VendorA + VendorC

Expected duplicate count:

2 duplicates
6. Output Formats

The aggregator produces three output formats designed for different security systems.

Firewall Output

File: firewall_blocklist.json

Purpose:

Used by firewalls or network security devices to block malicious IPs or domains.

Example entry:

{
"address": "203.0.113.50",
"action": "block",
"priority": "high",
"reason": "Threat level: critical, Confidence: 90%",
"sources": ["VendorA", "VendorB"]
}
SIEM Output

File: siem_indicators.json

Purpose:

Used by SIEM platforms (Security Information and Event Management) to generate alerts and correlate events.

Example entry:

{
"ioc_id": "VendorA-203.0.113.50",
"ioc_type": "ip",
"ioc_value": "203.0.113.50",
"risk_score": 90,
"severity": "critical",
"vendors": ["VendorA","VendorB"]
}
Text Report

File: threat_report.txt

Purpose:

Provides a human-readable report summarizing the analysis.

The report includes:

total indicators loaded

validation errors

duplicates removed

filtered high-confidence indicators

type distribution

severity distribution

vendor contributions

This report allows analysts to quickly review the aggregated threat intelligence.

Conclusion

This threat intelligence aggregator demonstrates how security tools can combine multiple vendor feeds into a single normalized threat intelligence dataset.

Key capabilities include:

multi-feed ingestion

schema normalization

validation

deduplication

filtering

multi-format output

statistical analysis

This approach improves threat detection coverage, confidence scoring, and operational efficiency when integrating multiple intelligence sources.