"""Boolean algebra simplifier — library functions.

Supports AND (· or &), OR (+ or |), NOT (~ or ! or '), XOR (^).
Expression examples: "A·B + C", "~A + B·C", "(A + B) · C"
"""

import itertools
import re


def parse_expression(expr: str) -> list[tuple[str, dict]] | None:
    """Parse boolean expression, return truth table rows or None on error."""
    expr = expr.strip()
    if not expr:
        return None

    # Normalize operators
    expr = expr.replace("'", ")'")  # handle A' style
    expr = expr.replace("·", "*")
    expr = expr.replace("&", "*")
    expr = expr.replace("|", "+")
    expr = expr.replace("!", "~")

    # Find all variables (single uppercase letters)
    vars_found = sorted(set(re.findall(r'[A-Z]', expr)))
    if not vars_found:
        return None

    n = len(vars_found)

    # Build a safe eval function
    def eval_expr(assignment: dict) -> int:
        local_vars = assignment.copy()
        # Handle NOT: ~A
        safe_expr = expr
        # Replace variables with their values
        for var in sorted(vars_found, key=len, reverse=True):
            safe_expr = safe_expr.replace(var, str(assignment[var]))
        # Handle NOT prefix
        safe_expr = re.sub(r'~(\d)', lambda m: str(int(not int(m.group(1)))), safe_expr)
        # Handle postfix NOT (e.g., 0' or 1')
        safe_expr = re.sub(r"(\d)'", lambda m: str(int(not int(m.group(1)))), safe_expr)
        # Handle XOR
        safe_expr = safe_expr.replace("^", "^")
        # Replace * with AND, + with OR
        # Use integer arithmetic: * = AND, + with clamp = OR
        safe_expr = safe_expr.replace("*", "&")
        safe_expr = safe_expr.replace("+", "|")

        try:
            result = eval(safe_expr, {"__builtins__": {}}, {})
            return int(bool(result))
        except Exception:
            raise ValueError(f"Cannot evaluate: {safe_expr}")

    table = []
    for bits in itertools.product([0, 1], repeat=n):
        assignment = dict(zip(vars_found, bits))
        try:
            result = eval_expr(assignment)
        except ValueError:
            return None
        table.append((assignment, result))

    return table


def get_minterms(table: list[tuple[str, dict]]) -> list[int]:
    """Get minterm indices where output is 1."""
    return [i for i, (_, result) in enumerate(table) if result == 1]


def get_maxterms(table: list[tuple[str, dict]]) -> list[int]:
    """Get maxterm indices where output is 0."""
    return [i for i, (_, result) in enumerate(table) if result == 0]


def simplify_expression(expr: str) -> dict:
    """Analyze and attempt to simplify a boolean expression.

    Returns dict with truth table, minterms, maxterms, SOP/POS forms, and info.
    """
    table = parse_expression(expr)
    if table is None:
        return {"success": False, "message": "Could not parse expression. Use A, B, C with + (OR), · (AND), ~ (NOT)"}

    vars_found = sorted(set(re.findall(r'[A-Z]', expr)))
    n = len(vars_found)
    minterms = get_minterms(table)
    maxterms = get_maxterms(table)

    # Check for tautology or contradiction
    if len(minterms) == 2 ** n:
        return {"success": True, "type": "tautology", "message": "Expression is always TRUE (tautology)", "vars": vars_found, "table": table}
    if len(minterms) == 0:
        return {"success": True, "type": "contradiction", "message": "Expression is always FALSE (contradiction)", "vars": vars_found, "table": table}

    # Build canonical SOP
    def minterm_str(idx):
        bits = format(idx, f'0{n}b')
        terms = []
        for var, bit in zip(vars_found, bits):
            terms.append(var if bit == '1' else f"~{var}")
        return " · ".join(terms)

    def maxterm_str(idx):
        bits = format(idx, f'0{n}b')
        terms = []
        for var, bit in zip(vars_found, bits):
            terms.append(f"~{var}" if bit == '1' else var)
        return " + ".join(terms)

    sop = " + ".join(minterm_str(m) for m in minterms)
    pos = " · ".join(f"({maxterm_str(m)})" for m in maxterms)

    return {
        "success": True,
        "type": "normal",
        "vars": vars_found,
        "minterms": minterms,
        "maxterms": maxterms,
        "sop": sop,
        "pos": pos,
        "table": table,
    }


class BooleanAlgebraSimplifier:
    """Boolean algebra expression simplifier with truth table analysis."""

    def __init__(self):
        self.last_result = None

    def simplify(self, expression: str) -> dict:
        """Simplify a boolean expression and return analysis."""
        self.last_result = simplify_expression(expression)
        return self.last_result

    def get_truth_table_text(self) -> str:
        """Get formatted truth table as text."""
        if not self.last_result or not self.last_result.get("success"):
            return "No valid expression analyzed yet."

        if self.last_result["type"] in ("tautology", "contradiction"):
            return f"Expression is {self.last_result['type'].upper()}"

        table = self.last_result["table"]
        vars_found = self.last_result["vars"]

        lines = []
        header = " | ".join(vars_found) + " | Out"
        lines.append(header)
        lines.append("-" * len(header))

        for assignment, result in table:
            row = " | ".join(str(assignment[var]) for var in vars_found) + f" | {result}"
            lines.append(row)

        return "\n".join(lines)

    def get_examples(self) -> list:
        """Get example boolean expressions."""
        return [
            "A · B + C",
            "~A + B · C",
            "(A + B) · C",
            "A ^ B",
            "A + A · B",
            "~(A + B)",
        ]
