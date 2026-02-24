from safelogic_engine import check_safety

test_plc = """
MotorRun := StartButton AND EmergencyStopButton;
"""

result = check_safety(test_plc)

print(result)
print("\nKeys:", result.keys())
