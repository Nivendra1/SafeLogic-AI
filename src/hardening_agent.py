import re
from llm_interface import LLMInterface

MAX_ATTEMPTS = 3

llm = LLMInterface()

def generate_plc_code(user_input, violation_feedback=None):
    if violation_feedback:
        system_prompt = """You are a PLC Structured Text generator.
You MUST output a single assignment line in this exact format:
OutputVariableName := (boolean expression here);

Rules you must never break:
1. EmergencyStopButton MUST appear as NOT EmergencyStopButton
2. Do NOT use IF/THEN/ELSE blocks — single assignment line ONLY
3. Do NOT write TRUE or FALSE as the expression
4. Use meaningful variable names ending in Run, Output, Active, or Enable

Example of correct output:
MotorRun := StartButton AND NOT EmergencyStopButton;

Previous attempt failed because: """ + violation_feedback
    else:
        system_prompt = """You are a PLC Structured Text generator.
You MUST output a single assignment line in this exact format:
OutputVariableName := (boolean expression here);

Rules you must never break:
1. EmergencyStopButton MUST appear as NOT EmergencyStopButton
2. Do NOT use IF/THEN/ELSE blocks — single assignment line ONLY
3. Do NOT write TRUE or FALSE as the expression
4. Use meaningful variable names ending in Run, Output, Active, or Enable

Example of correct output:
MotorRun := StartButton AND NOT EmergencyStopButton;"""

    return llm._chat_completion(system_prompt, user_input)


def extract_output_assignment(code):
    """
    Extract Boolean expression from PLC code.
    Priority order:
    1. IF condition block — extract the condition from IF (...) THEN
    2. Single assignment line — extract from OutputVar := expression;
    3. Reject TRUE/FALSE literals as invalid expressions
    """

    # Priority 1: Extract IF condition
    if_pattern = r'IF\s+(.*?)\s+THEN'
    if_match = re.search(if_pattern, code, re.IGNORECASE | re.DOTALL)
    if if_match:
        condition = if_match.group(1).strip()
        # Clean up multiline
        condition = ' '.join(condition.split())
        print(f"✅ Extracted from IF block: {condition}")
        # Find output variable name
        var_pattern = r'(\w+Run|\w+Output|\w+Active|\w+Enable)\s*:='
        var_match = re.search(var_pattern, code, re.IGNORECASE)
        output_var = var_match.group(1) if var_match else "OutputRun"
        return output_var, condition

    # Priority 2: Single assignment line — reject TRUE/FALSE literals
    assign_pattern = r'(\w+Run|\w+Output|\w+Active|\w+Enable)\s*:=\s*(.*?);'
    for match in re.finditer(assign_pattern, code, re.IGNORECASE):
        output_var = match.group(1)
        expression = match.group(2).strip()
        # Skip literal TRUE/FALSE — not a real Boolean expression
        if expression.upper() in ['TRUE', 'FALSE', '1', '0']:
            print(f"⚠️  Skipping literal value: {expression}")
            continue
        print(f"✅ Extracted from assignment: {output_var} := {expression}")
        return output_var, expression

    print("❌ No valid output assignment found.")
    return None, None


def validate_logic(boolean_expr):
    if not boolean_expr:
        return "CRITICAL", "No valid output assignment found"

    if boolean_expr.strip().upper() in ['TRUE', 'FALSE', '1', '0']:
        return "CRITICAL", "Unsafe constant expression — output always on or always off"

    if "EmergencyStopButton" not in boolean_expr:
        return "CRITICAL", "EmergencyStopButton missing"

    if "NOT EmergencyStopButton" not in boolean_expr:
        return "CRITICAL", "EmergencyStopButton present but not correctly negated — estop enables instead of cuts"

    return "LOW", "Valid safety logic"


def harden_logic(user_input, explain=False):
    iterations = []
    explanation = None
    violation_feedback = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"\n🔄 Attempt {attempt}/{MAX_ATTEMPTS}")
        plc_code = generate_plc_code(user_input, violation_feedback)
        output_var, boolean_expr = extract_output_assignment(plc_code)

        if not boolean_expr:
            reason = "No valid output assignment found — LLM generated IF block or unsupported format"
            iterations.append({
                "attempt": attempt,
                "boolean": None,
                "risk": "CRITICAL",
                "reason": reason,
                "raw_code": plc_code
            })
            violation_feedback = reason
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
            if explain:
                explanation = (
                    f"Output Variable: {output_var}\n"
                    f"Boolean Expression: {boolean_expr}\n"
                    f"Safety Check: EmergencyStopButton present and correctly negated.\n"
                    f"Final Status: SAFE"
                )
            return {
                "iterations": iterations,
                "final_status": "SAFE",
                "explanation": explanation
            }

        # Feed violation back to LLM for next attempt
        violation_feedback = f"{reason}. Expression was: {boolean_expr}"

    return {
        "iterations": iterations,
        "final_status": "CRITICAL VIOLATION",
        "explanation": "Unable to generate safe verifiable logic after 3 attempts — human review required."
    }
