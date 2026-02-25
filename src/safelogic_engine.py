import re
import json
import os

# ── Load rules from JSON ──
CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "config",
    "safety_rules.json"
)

def load_rules():
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}

RULES = load_rules()


def extract_expression(plc_code):
    """
    Dynamically extract PLC output assignment.
    Priority 1: IF/THEN block — extract condition
    Priority 2: Single assignment line
    Rejects TRUE/FALSE literals
    """
    # Priority 1: IF block
    if_pattern = r'IF\s+(.*?)\s+THEN'
    if_match = re.search(if_pattern, plc_code, re.IGNORECASE | re.DOTALL)
    if if_match:
        condition = ' '.join(if_match.group(1).strip().split())
        var_pattern = r'(\w+Run|\w+Output|\w+Active|\w+Enable)\s*:='
        var_match = re.search(var_pattern, plc_code, re.IGNORECASE)
        output_var = var_match.group(1) if var_match else "OutputRun"
        return {"output_variable": output_var, "expression": condition}

    # Priority 2: Single assignment — reject literals
    assign_pattern = r'(\w+Run|\w+Output|\w+Active|\w+Enable)\s*:=\s*(.*?);'
    for match in re.finditer(assign_pattern, plc_code, re.IGNORECASE):
        output_var = match.group(1)
        expression = match.group(2).strip()
        if expression.upper() in ['TRUE', 'FALSE', '1', '0']:
            continue
        return {"output_variable": output_var, "expression": expression}

    return None


def normalize_expression(extracted):
    if not extracted:
        return None
    return extracted["expression"]


def check_or_bypass(expression):
    """
    Detect OR bypass attacks.
    Pattern: anything AND NOT EmergencyStopButton OR anything_else
    The OR creates an alternative path that bypasses estop.
    """
    # Normalize spacing
    expr = ' ' + expression.strip() + ' '

    # Check if OR exists in expression
    if ' OR ' not in expr.upper() and ' or ' not in expr:
        return None

    # If OR exists, check if the part after OR could bypass estop
    # Split on OR and check each segment
    parts = re.split(r'\bOR\b', expression, flags=re.IGNORECASE)

    if len(parts) > 1:
        # Check if any OR segment doesn't include NOT EmergencyStopButton
        for part in parts:
            part = part.strip()
            if 'EmergencyStopButton' not in part:
                return {
                    "status": "VIOLATION",
                    "risk_level": "HIGH",
                    "reason": f"OR bypass detected — '{part.strip()}' path can activate output without EmergencyStopButton check"
                }
            if 'NOT EmergencyStopButton' not in part and 'EmergencyStopButton' in part:
                return {
                    "status": "VIOLATION",
                    "risk_level": "CRITICAL",
                    "reason": f"OR bypass with unsafe estop polarity — estop check missing NOT in segment: '{part.strip()}'"
                }

    return None


def check_mandatory_signal(boolean_expression):
    """
    Full safety validation pipeline.
    Checks in order:
    1. None check
    2. Constant expression check
    3. Mandatory signal presence
    4. Polarity check
    5. OR bypass detection
    6. Forbidden combinations from JSON
    """
    if boolean_expression is None:
        return {
            "status": "VIOLATION",
            "risk_level": "CRITICAL",
            "reason": "No output assignment detected"
        }

    # Constant expression check
    if boolean_expression.strip().upper() in ['TRUE', 'FALSE', '1', '0']:
        return {
            "status": "VIOLATION",
            "risk_level": "CRITICAL",
            "reason": "Unsafe constant expression — output always energized regardless of any input"
        }

    # Mandatory signal presence
    if "EmergencyStopButton" not in boolean_expression:
        return {
            "status": "VIOLATION",
            "risk_level": "CRITICAL",
            "reason": "EmergencyStopButton missing — estop has no effect on this output"
        }

    # Polarity check
    if "NOT EmergencyStopButton" not in boolean_expression:
        return {
            "status": "VIOLATION",
            "risk_level": "CRITICAL",
            "reason": "Incorrect emergency stop polarity — estop enables output instead of cutting it"
        }

    # OR bypass detection
    or_result = check_or_bypass(boolean_expression)
    if or_result:
        return or_result

    # Forbidden combinations from JSON rules
    forbidden = RULES.get("forbidden_active_combinations", [])
    for rule in forbidden:
        active = rule.get("active_signal", "")
        forbidden_with = rule.get("forbidden_with", "")
        if active in boolean_expression and forbidden_with in boolean_expression:
            # Check if active signal is used as enabling (not negated)
            if f"NOT {active}" not in boolean_expression:
                return {
                    "status": "VIOLATION",
                    "risk_level": rule.get("risk_level", "HIGH"),
                    "reason": f"{rule['name']} ({rule['id']}) — {rule['real_world_consequence']}"
                }

    return {
        "status": "SAFE",
        "risk_level": "LOW",
        "reason": "Valid safety logic — all checks passed"
    }
