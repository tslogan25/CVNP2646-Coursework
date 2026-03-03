This script is a backup planner simulator.

It:

Loads a JSON configuration file (backup_config.json) safely.

Validates the configuration to ensure required fields like plan_name, sources, and destination exist and make sense.

Simulates a backup (dry-run) by generating 5–15 fake files per source with realistic names and random sizes.

Calculates totals for number of files and total storage size.

Prints a clean, human-readable report showing:

Plan name and timestamp

Summary statistics

Details per source

Sample files

A reminder that no files were actually copied

In short, it mimics what a real backup would do—without copying any files—so you can preview results safely.