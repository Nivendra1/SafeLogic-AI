from safelogic_engine import check_safety

def run_test(name, expression):
    print("\n==============================")
    print(f"TEST: {name}")
    print("==============================")
    print("Expression:", expression)

    result = check_safety(expression)

    print("Status:", result.get("status"))
    print("Risk Level:", result.get("risk_level"))
    print("Reason:", result.get("reason"))
    print("Counterexample:", result.get("counterexample_explanation"))


if __name__ == "__main__":

    # 1️⃣ Safe Case
    run_test(
        "Safe Case",
        "(StartButton or RemoteStart) and not EmergencyStopButton"
    )

    # 2️⃣ Missing Mandatory Signal
    run_test(
        "Missing Mandatory Signal",
        "StartButton"
    )

    # 3️⃣ Forbidden Combination (Correct Rule Test)
    run_test(
        "Forbidden Combination",
        "MotorRun and EmergencyStopButton"
    )

    # 4️⃣ Complex Safe Case
    run_test(
        "Complex Safe",
        "(StartButton and not FaultSignal) and not EmergencyStopButton"
    )
