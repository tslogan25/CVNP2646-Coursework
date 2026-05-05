import json
import os
from collections import defaultdict
from datetime import datetime, timedelta

def load_json(filename):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(base_dir, filename)

    with open(filepath, 'r') as f:
        return json.load(f)

def build_user_lookup(users_data):
    """Create dictionary keyed by user_id for fast lookups."""
    return {user['user_id']: user for user in users_data}

def group_roles_by_user(roles_data):
    """Group all roles for each user using defaultdict."""
    user_roles = defaultdict(list)

    for role_entry in roles_data:
        user_id = role_entry['user_id']
        user_roles[user_id].append(role_entry['role'])

    return dict(user_roles)

def check_disabled_with_roles(users_dict, roles_data):
    """Detect disabled users who still have active role assignments."""
    violations = []

    users_with_roles = {r['user_id'] for r in roles_data}

    for user_id, user in users_dict.items():
        if user['status'] == 'disabled' and user_id in users_with_roles:
            user_roles = [r['role'] for r in roles_data if r['user_id'] == user_id]

            violations.append({
                'user_id': user_id,
                'username': user['username'],
                'violation_type': 'disabled_with_roles',
                'severity': 'CRITICAL',
                'details': f"Disabled account has {len(user_roles)} active role(s): {', '.join(user_roles)}"
            })

    return violations

def check_unauthorized_admins(users_dict, roles_data, authorized_depts={'IT', 'Security'}):
    """Detect admin roles assigned to users outside authorized departments."""
    violations = []

    for role_entry in roles_data:
        if 'admin' in role_entry['role'].lower():
            user_id = role_entry['user_id']

            if user_id in users_dict:
                user = users_dict[user_id]

                if user['department'] not in authorized_depts:
                    violations.append({
                        'user_id': user_id,
                        'username': user['username'],
                        'violation_type': 'unauthorized_admin',
                        'severity': 'HIGH',
                        'details': f"{user['department']} dept user has admin role: {role_entry['role']}",
                        'department': user['department'],
                        'role': role_entry['role']
                    })

    return violations

def check_stale_accounts(users_dict, stale_days=90):
    """Detect active accounts with no login for 90+ days."""
    violations = []
    now = datetime.now()
    cutoff_date = now - timedelta(days=stale_days)

    for user_id, user in users_dict.items():
        if user['status'] != 'active':
            continue

        last_login_str = user.get('last_login')

        if not last_login_str:
            violations.append({
                'user_id': user_id,
                'username': user['username'],
                'violation_type': 'stale_account',
                'severity': 'MEDIUM',
                'details': 'Active account with no recorded login date',
                'last_login': None
            })
        else:
            last_login = datetime.strptime(last_login_str, '%Y-%m-%d')

            if last_login < cutoff_date:
                days_since = (now - last_login).days
                violations.append({
                    'user_id': user_id,
                    'username': user['username'],
                    'violation_type': 'stale_account',
                    'severity': 'MEDIUM',
                    'details': f"No login for {days_since} days (last: {last_login_str})",
                    'last_login': last_login_str,
                    'days_inactive': days_since
                })

    return violations

def generate_audit_report(*violation_lists):
    """Combine all violations and summarize by severity."""
    all_violations = []

    for violation_list in violation_lists:
        all_violations.extend(violation_list)

    severity_count = defaultdict(int)
    for violation in all_violations:
        severity_count[violation['severity']] += 1

    severity_order = {'CRITICAL': 1, 'HIGH': 2, 'MEDIUM': 3, 'LOW': 4}
    all_violations.sort(key=lambda v: severity_order.get(v['severity'], 99))

    return all_violations, dict(severity_count)

def save_text_report(all_violations, severity_count, filename='audit_report.txt'):
    """Save a human-readable audit report."""
    with open(filename, 'w') as f:
        f.write("=== AUDIT REPORT ===\n")
        f.write(f"Total violations: {len(all_violations)}\n\n")

        f.write("By Severity:\n")
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            if severity in severity_count:
                f.write(f"  {severity}: {severity_count[severity]}\n")

        f.write("\nDetailed Findings:\n")
        for violation in all_violations:
            f.write(
                f"- [{violation['severity']}] "
                f"{violation['username']} ({violation['user_id']}): "
                f"{violation['details']}\n"
            )

def save_json_report(all_violations, severity_count, filename='audit_report.json'):
    """Save a machine-readable audit report as JSON."""
    report_data = {
        'total_violations': len(all_violations),
        'severity_summary': severity_count,
        'violations': all_violations
    }

    with open(filename, 'w') as f:
        json.dump(report_data, f, indent=4)

# Step 1: Load both datasets
users_data = load_json('users.json')
roles_data = load_json('roles.json')

# Confirm first user loaded correctly
first_user = users_data[0]
print(f"Username: {first_user['username']}")
print(f"Department: {first_user['department']}")

# Step 2: Build user lookup dictionary once
users_dict = build_user_lookup(users_data)

# Test fast lookup
user = users_dict['U001']
print(f"{user['username']} is in {user['department']}")

# Step 3: Group roles by user
user_roles = group_roles_by_user(roles_data)

# Test grouped roles
print(f"U002 has roles: {user_roles['U002']}")
print(f"U999 has roles: {user_roles.get('U999', [])}")

# Step 4: Rule 1 - Disabled users with active roles
violations_r1 = check_disabled_with_roles(users_dict, roles_data)

# Step 5: Rule 2 - Unauthorized admin assignments
violations_r2 = check_unauthorized_admins(users_dict, roles_data)

# Step 6: Rule 3 - Stale active accounts
violations_r3 = check_stale_accounts(users_dict)

# Step 7: Combine all violations into one report
all_violations, severity_count = generate_audit_report(
    violations_r1,
    violations_r2,
    violations_r3
)

# Print summary to console
print("\n=== AUDIT REPORT ===")
print(f"Total violations: {len(all_violations)}")

print("\nBy Severity:")
for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
    if severity in severity_count:
        print(f"  {severity}: {severity_count[severity]}")

print("\nDetailed Findings:")
for violation in all_violations:
    print(f"- [{violation['severity']}] {violation['username']}: {violation['details']}")

# Step 8: Save reports
save_text_report(all_violations, severity_count)
save_json_report(all_violations, severity_count)

print("\nReports saved: audit_report.txt, audit_report.json")