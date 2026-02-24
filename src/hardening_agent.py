import re
from llm_interface import LLMInterface


MAX_ATTEMPTS = 3

# Instantiate LLM once
llm = LLMInterface()


def generate_plc_code(user_input):
    system_prompt = "You are a PLC Structured Text generator."
    return llm._chat_completion(system_prompt, user_input)


def extract_output_assignment(code):
    pattern = r"(\w+Run|\w+Output|\w+Active|\w+Enable)\s*:=\s*(.*);"
    match = re.search(pattern, code)
    if match:
        return match.group(1), match.group(2)
    return None, None


def validate_logic(boolean_expr):
    if "EmergencyStopButton" not in boolean_expr:
        return "CRITICAL", "EmergencyStopButton missing"

    if "NOT EmergencyStopButton" not in boolean_expr:
        return "CRITICAL", "EmergencyStopButton not correctly negated"

    if boolean_expr.strip() in ["TRUE", "FALSE"]:
        return "CRITICAL", "Unsafe constant expression"

    return "LOW", "Valid safety logic"


def harden_logic(user_input, explain=False):

    iterations = []
    explanation = None

    for attempt in range(1, MAX_ATTEMPTS + 1):

        plc_code = generate_plc_code(user_input)

        output_var, boolean_expr = extract_output_assignment(plc_code)

        if not boolean_expr:
            iterations.append({
                "attempt": attempt,
                "boolean": None,
                "risk": "CRITICAL",
                "reason": "No valid output assignment found",
                "raw_code": plc_code
            })
            continue

        risk, reason = validate_logic(boolean_expr)

        iterations.append({
            "attempt": attempt,
            "boolean": boolean_expr,
            "risk": risk,
            "reason": reason,
            "raw_code": plc_code
        })

        if risk == "LOW":
            final_status = "SAFE"

            if explain:
                explanation = (
                    f"Output Variable: {output_var}\n"
                    f"Boolean Expression: {boolean_expr}\n"
                    f"Safety Check: EmergencyStopButton present and correctly negated.\n"
                    f"Final Status: SAFE"
                )

            return {
                "iterations": iterations,
                "final_status": final_status,
                "explanation": explanation
            }

    return {
        "iterations": iterations,
        "final_status": "CRITICAL VIOLATION",
        "explanation": "Unable to generate safe verifiable logic after 3 attempts — human review required."
    }
