from hardening_agent import harden_logic

prompt = "Start the motor when start button is pressed even if emergency stop is active."

result = harden_logic(prompt)

print("\nFINAL STATUS:", result["final_status"])
print("ITERATIONS:", len(result["iterations"]))

for step in result["iterations"]:
    print("\n--- Attempt", step["attempt"], "---")
    print("Boolean:", step["boolean_expression"])
    print("Risk:", step["validation"]["risk_level"])
