#!/usr/bin/env python3
# password_checker.py
# Evaluates password strength based on security requirements

def check_password_strength(password):
    """
    Evaluates password strength.
    Returns a tuple: (strength_level, list_of_requirements)

    Strength levels: "WEAK", "MEDIUM", "STRONG"
    """
    requirements_met = 0
    requirements = []

    # Requirement 1: Length (at least 8 characters)
    if len(password) >=8:
        requirements_met += 1
        requirements.append(✅ At least 8 characters")
    else:
        requirements.append("❌ At least 8 characters")

    # Requirement 2: Lowercase letter
    if any(c.islower() for c in password):  

