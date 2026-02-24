from llm_interface import LLMInterface

llm = LLMInterface()

# --------------------------------------------------
# TEST CASE 1 — E-Stop polarity violation
# --------------------------------------------------

print("=" * 60)
print("TEST CASE 1")
print("=" * 60)

output = llm.narrate_violation(
    original_prompt="Motor should run when start button is pressed.",
    extracted_expression="MotorRun := (StartButton OR EmergencyStopButton OR OverloadRelay);",
    violation_reason="EmergencyStopButton used as enabling condition",
    risk_level="CRITICAL",
    counterexample_dict={
        "StartButton": False,
        "EmergencyStopButton": True,
        "OverloadRelay": False
    }
)

print(output)


# --------------------------------------------------
# TEST CASE 2 — Missing interlock
# --------------------------------------------------

print("\n" + "=" * 60)
print("TEST CASE 2")
print("=" * 60)

output = llm.narrate_violation(
    original_prompt="Motor runs when door is closed.",
    extracted_expression="MotorRun := (NOT SafetyDoorOpen);",
    violation_reason="EmergencyStopButton missing from expression",
    risk_level="HIGH",
    counterexample_dict={
        "SafetyDoorOpen": False,
        "EmergencyStopButton": True
    }
)

print(output)


# --------------------------------------------------
# TEST CASE 3 — Overload ignored
# --------------------------------------------------

print("\n" + "=" * 60)
print("TEST CASE 3")
print("=" * 60)

output = llm.narrate_violation(
    original_prompt="Motor should run when overload relay is active.",
    extracted_expression="MotorRun := (OverloadRelay);",
    violation_reason="EmergencyStopButton missing and no shutdown interlock",
    risk_level="CRITICAL",
    counterexample_dict={
        "OverloadRelay": True,
        "EmergencyStopButton": True
    }
)

print(output)
