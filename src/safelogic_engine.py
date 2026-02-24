import re


def extract_expression(plc_code):
    """
    Dynamically extract PLC output assignment.
    Matches:
    - MotorRun
    - ConveyorRun
    - PumpRun
    - ValveOutput
    - PressActive
    - SystemEnable
    """

    pattern = r'(\w+Run|\w+Output|\w+Active|\w+Enable)\s*:=\s*(.*?);'

    match = re.search(pattern, plc_code, re.IGNORECASE)

    if match:
        output_variable = match.group(1)
        boolean_expression = match.group(2).strip()

        print(f"✅ Extracted Output Variable: {output_variable}")
        print(f"✅ Extracted Boolean Expression: {boolean_expression}")

        return {
            "output_variable": output_variable,
            "expression": boolean_expression
        }

    print("❌ No valid output assignment found.")
    return None


def normalize_expression(extracted):
    if not extracted:
        return None

    return extracted["expression"]


def check_mandatory_signal(boolean_expression):
    """
    Safety rules:
    - EmergencyStopButton must be present
    - Must use correct polarity (NOT EmergencyStopButton)
    """

    if boolean_expression is None:
        return {
            "status": "VIOLATION",
            "risk_level": "CRITICAL",
            "reason": "No output assignment detected"
        }

    if "EmergencyStopButton" not in boolean_expression:
        return {
            "status": "VIOLATION",
            "risk_level": "CRITICAL",
            "reason": "EmergencyStopButton missing"
        }

    if "NOT EmergencyStopButton" not in boolean_expression:
        return {
            "status": "VIOLATION",
            "risk_level": "CRITICAL",
            "reason": "Incorrect emergency stop polarity"
        }

    return {
        "status": "SAFE",
        "risk_level": "LOW",
        "reason": "Valid safety logic"
    }
