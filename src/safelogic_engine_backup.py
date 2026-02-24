import re
import json
from typing import Dict, Any, List
from itertools import product
from pathlib import Path


# =====================================
# 1️⃣ Load Safety Configuration
# =====================================

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "safety_rules.json"

with open(CONFIG_PATH, "r") as f:
    CONFIG = json.load(f)

MANDATORY_SIGNALS = CONFIG["mandatory_signals"]
SAFETY_RULES = CONFIG["rules"]


# =====================================
# 2️⃣ Expression Helpers
# =====================================

def _normalize_expression(expr: str) -> str:
    expr = expr.replace("AND", "and")
    expr = expr.replace("OR", "or")
    expr = expr.replace("NOT", "not")
    return expr


def _extract_variables(expr: str) -> List[str]:
    tokens = re.findall(r"[A-Za-z_]\w*", expr)
    keywords = {"and", "or", "not", "True", "False"}
    return sorted(set(t for t in tokens if t not in keywords))


def _evaluate(expr: str, values: Dict[str, bool]) -> bool:
    safe_expr = expr
    for var, val in values.items():
        safe_expr = re.sub(rf"\b{var}\b", str(val), safe_expr)
    return eval(safe_expr)


# =====================================
# 3️⃣ Main Safety Check Engine
# =====================================

def check_safety(expression: str) -> Dict[str, Any]:
    expression = _normalize_expression(expression)
    variables = _extract_variables(expression)

    # 🚨 Mandatory signal check
    for signal in MANDATORY_SIGNALS:
        if signal not in variables:
            return {
                "status": "VIOLATION",
                "reason": "Missing mandatory safety signal",
                "counterexample": None
            }

    # Evaluate rule violations
    for rule in SAFETY_RULES:
        rule_expr = _normalize_expression(rule["condition"])
        rule_vars = _extract_variables(rule_expr)

        if all(v in variables for v in rule_vars):
            for combo in product([True, False], repeat=len(variables)):
                assignment = dict(zip(variables, combo))

                try:
                    expr_result = _evaluate(expression, assignment)
                    rule_result = _evaluate(rule_expr, assignment)

                    if expr_result and rule_result:
                        return {
                            "status": "VIOLATION",
                            "reason": rule["violation"],
                            "counterexample": assignment
                        }

                except Exception:
                    continue

    return {
        "status": "SAFE",
        "reason": "No violations detected",
        "counterexample": None
    }
