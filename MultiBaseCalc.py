"""Multi-base number equation evaluator — library functions.

Supports arithmetic equations with numbers in any base (2, 8, 10, 16).
Prefix notation: 0b (binary), 0o (octal), 0x (hex), or plain decimal.
Examples:
    "0b1010 + 0xFF"  -> 10 + 255 = 265
    "0o77 * 2"       -> 63 * 2 = 126
    "255 / 0xF"      -> 255 / 15 = 17
    "0b1010 & 0xFF"  -> 10 & 255 = 10  (bitwise)
"""

import re


def parse_number(s: str) -> int | None:
    """Parse a number string with optional base prefix."""
    s = s.strip()
    try:
        if s.startswith("0b") or s.startswith("0B"):
            return int(s, 2)
        elif s.startswith("0o") or s.startswith("0O"):
            return int(s, 8)
        elif s.startswith("0x") or s.startswith("0X"):
            return int(s, 16)
        else:
            return int(s, 10)
    except ValueError:
        return None


def detect_base(s: str) -> int:
    """Detect the base of a number string by its prefix."""
    s = s.strip()
    if s.startswith("0b") or s.startswith("0B"):
        return 2
    elif s.startswith("0o") or s.startswith("0O"):
        return 8
    elif s.startswith("0x") or s.startswith("0X"):
        return 16
    return 10


def evaluate(expression: str) -> dict:
    """Evaluate an arithmetic expression with multi-base numbers.

    Supports: +, -, *, /, //, %, ** (power), &, |, ^, ~, <<, >>
    Also supports parentheses.

    Returns dict with: success, result (int), results (dict of all bases), message
    """
    expr = expression.strip()
    if not expr:
        return {"success": False, "message": "Empty expression."}

    # Tokenize: split into numbers, operators, parentheses
    tokens = re.findall(r'0[bBoxX][0-9a-fA-F]+|\d+|[+\-*/%&|^~<>()]+|\*\*|//|<<|>>', expr)
    if not tokens:
        return {"success": False, "message": "Could not parse expression."}

    # Validate all tokens
    safe_expr = expr
    for token in tokens:
        token_stripped = token.strip()
        if not token_stripped:
            continue
        if token_stripped in ('+', '-', '*', '/', '//', '%', '**', '&', '|', '^', '~', '(', ')', '<<', '>>'):
            continue
        if re.match(r'^0[bBoxX][0-9a-fA-F]+$', token_stripped):
            continue
        if re.match(r'^\d+$', token_stripped):
            continue
        return {"success": False, "message": f"Invalid token: '{token_stripped}'"}

    # Replace multi-base numbers with their decimal values
    eval_expr = expr
    numbers = re.findall(r'0[bBoxX][0-9a-fA-F]+|\d+', expr)
    # Sort by position in reverse to replace from end to start
    replacements = []
    for m in re.finditer(r'0[bBoxX][0-9a-fA-F]+|\d+', expr):
        num_str = m.group()
        val = parse_number(num_str)
        if val is None:
            return {"success": False, "message": f"Cannot parse number: '{num_str}'"}
        # Track the base of each number for display
        base = detect_base(num_str)
        replacements.append((m.start(), m.end(), str(val), num_str, base))

    # Build safe expression by replacing numbers from end to start
    for start, end, dec_val, orig, base in reversed(replacements):
        eval_expr = eval_expr[:start] + dec_val + eval_expr[end:]

    # Replace ** and // for safety
    eval_expr = eval_expr.replace('**', '**').replace('//', '//')

    try:
        result = eval(eval_expr, {"__builtins__": {}}, {})
        if not isinstance(result, (int, float)):
            return {"success": False, "message": f"Result is not a number: {result}"}
        result = int(result)
    except ZeroDivisionError:
        return {"success": False, "message": "Division by zero."}
    except Exception as e:
        return {"success": False, "message": f"Evaluation error: {e}"}

    # Convert result to all bases
    results = {
        "Decimal": str(result),
        "Binary": bin(result)[2:] if result >= 0 else "-" + bin(abs(result))[2:],
        "Octal": oct(result)[2:] if result >= 0 else "-" + oct(abs(result))[2:],
        "Hexadecimal": hex(result)[2:].upper() if result >= 0 else "-" + hex(abs(result))[2:].upper(),
    }

    return {
        "success": True,
        "result": result,
        "results": results,
        "expression": expr,
    }


def format_number(value: int, base: int) -> str:
    """Format an integer in the specified base."""
    if base == 2:
        return bin(value)[2:] if value >= 0 else "-" + bin(abs(value))[2:]
    elif base == 8:
        return oct(value)[2:] if value >= 0 else "-" + oct(abs(value))[2:]
    elif base == 16:
        return hex(value)[2:].upper() if value >= 0 else "-" + hex(abs(value))[2:].upper()
    return str(value)
