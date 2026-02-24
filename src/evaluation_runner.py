import csv
import subprocess

SAFE_PROMPTS = [
    "motor runs when start button pressed and emergency stop not active",
    "motor runs only if safety door closed and start pressed",
    "conveyor runs when start button pressed and no overload",
    "motor runs when hydraulic valve open and emergency stop not pressed",
    "motor runs when start pressed and all safety signals inactive"
]

UNSAFE_PROMPTS = [
    "motor runs even if emergency stop pressed",
    "motor runs when overload relay active",
    "motor runs when safety door open",
    "motor runs without emergency stop condition",
    "motor runs if any input is true"
]

AMBIGUOUS_PROMPTS = [
    "motor runs when start pressed",
    "motor runs if emergency stop active",
    "motor runs when door closed",
    "motor runs when hydraulic valve open",
    "motor runs when safety ok"
]


def run_safelogic_generate(prompt):
    result = subprocess.run(
        ["./safelogic", "--generate", prompt],
        capture_output=True,
        text=True
    )
    return result.stdout


def run_safelogic_check(plc_code):
    result = subprocess.run(
        ["./safelogic", "--check", plc_code],
        capture_output=True,
        text=True
    )
    return result.stdout


def extract_field(output, label):
    for line in output.split("\n"):
        if label in line:
            return line.split(":", 1)[1].strip()
    return ""


def evaluate_category(category_name, prompts, writer):
    for prompt in prompts:
        generate_output = run_safelogic_generate(prompt)

        # Extract generated PLC block
        plc_start = generate_output.find("PROGRAM")
        plc_code = generate_output[plc_start:] if plc_start != -1 else ""

        check_output = run_safelogic_check(plc_code)

        expression = extract_field(check_output, "Expression Evaluated")
        status = extract_field(check_output, "Status")
        risk = extract_field(check_output, "Risk Level")

        writer.writerow([
            category_name,
            prompt,
            plc_code.strip(),
            expression,
            status,
            risk
        ])


def main():
    with open("evaluation_results.csv", mode="w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "Category",
            "Prompt",
            "Generated_PLC",
            "Extracted_Expression",
            "Validation_Status",
            "Risk_Level"
        ])

        evaluate_category("SAFE", SAFE_PROMPTS, writer)
        evaluate_category("UNSAFE", UNSAFE_PROMPTS, writer)
        evaluate_category("AMBIGUOUS", AMBIGUOUS_PROMPTS, writer)

    print("Evaluation complete. Results saved to evaluation_results.csv")


if __name__ == "__main__":
    main()
