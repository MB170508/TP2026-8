"""Multi-base number converter — library functions."""

_BASE_NAMES = {2: "Binary", 8: "Octal", 10: "Decimal", 16: "Hexadecimal"}


def convert(value: str, from_base: int) -> dict:
    """Convert a number string from one base to all supported bases.

    Args:
        value: number string (e.g. "FF", "1010", "255")
        from_base: 2, 8, 10, or 16

    Returns:
        dict with keys: success, value (int), results (dict), message
    """
    supported = {2, 8, 10, 16}
    if from_base not in supported:
        return {"success": False, "message": f"Unsupported base: {from_base}. Use 2, 8, 10, or 16."}

    try:
        num = int(value.strip(), from_base)
    except ValueError:
        return {"success": False, "message": f"Invalid {from_base}-base number: '{value}'"}

    results = {}
    for base in sorted(supported):
        if base == 2:
            results["Binary"] = bin(num)[2:]
        elif base == 8:
            results["Octal"] = oct(num)[2:]
        elif base == 10:
            results["Decimal"] = str(num)
        elif base == 16:
            results["Hexadecimal"] = hex(num)[2:].upper()

    return {"success": True, "value": num, "results": results}
