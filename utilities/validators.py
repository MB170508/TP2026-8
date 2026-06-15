"""Input validation utilities for IT Toolbox."""

import re
from typing import Tuple, Optional


def validate_ipv4_network(value: str) -> Tuple[bool, str]:
    """Validate IPv4 network in CIDR notation.

    Args:
        value: User input (e.g., "192.168.0.0/24")

    Returns:
        (is_valid, error_message)
    """
    if not value or not value.strip():
        return False, "Network cannot be empty"

    if '/' not in value:
        return False, "Use CIDR format: 192.168.0.0/24"

    try:
        addr, cidr = value.split('/')
        parts = addr.split('.')
        if len(parts) != 4:
            return False, "Invalid IPv4 address"

        for part in parts:
            num = int(part)
            if not 0 <= num <= 255:
                return False, "Each octet must be 0-255"

        cidr_num = int(cidr)
        if not 0 <= cidr_num <= 32:
            return False, "CIDR must be 0-32"

        return True, ""
    except ValueError:
        return False, "Invalid format"


def validate_positive_integer(value: str, max_val: Optional[int] = None) -> Tuple[bool, str]:
    """Validate positive integer.

    Args:
        value: User input
        max_val: Optional maximum value

    Returns:
        (is_valid, error_message)
    """
    if not value or not value.strip():
        return False, "Cannot be empty"

    try:
        num = int(value)
        if num <= 0:
            return False, "Must be positive"
        if max_val and num > max_val:
            return False, f"Maximum is {max_val}"
        return True, ""
    except ValueError:
        return False, "Must be a whole number"


def validate_float(value: str, min_val: float = 0, max_val: Optional[float] = None) -> Tuple[bool, str]:
    """Validate floating-point number.

    Args:
        value: User input
        min_val: Minimum value (default 0)
        max_val: Optional maximum value

    Returns:
        (is_valid, error_message)
    """
    if not value or not value.strip():
        return False, "Cannot be empty"

    try:
        num = float(value)
        if num < min_val:
            return False, f"Must be >= {min_val}"
        if max_val and num > max_val:
            return False, f"Must be <= {max_val}"
        return True, ""
    except ValueError:
        return False, "Must be a number"


def validate_url(value: str) -> Tuple[bool, str]:
    """Validate URL format.

    Args:
        value: User input

    Returns:
        (is_valid, error_message)
    """
    if not value or not value.strip():
        return False, "URL cannot be empty"

    url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    if re.match(url_pattern, value):
        return True, ""
    return False, "Invalid URL format"


def validate_api_key(value: str, min_length: int = 10) -> Tuple[bool, str]:
    """Validate API key format.

    Args:
        value: User input
        min_length: Minimum key length (default 10)

    Returns:
        (is_valid, error_message)
    """
    if not value or not value.strip():
        return False, "API key cannot be empty"
    if len(value) < min_length:
        return False, f"API key too short (minimum {min_length} chars)"
    return True, ""


def validate_boolean_expression(value: str) -> Tuple[bool, str]:
    """Validate boolean algebra expression syntax.

    Args:
        value: User input

    Returns:
        (is_valid, error_message)
    """
    if not value or not value.strip():
        return False, "Expression cannot be empty"

    # Check for basic syntax issues
    value = value.upper().replace(" ", "")

    # Valid characters: letters, operators, parentheses
    if not re.match(r'^[A-Z0-9+*\'().]+$', value):
        return False, "Invalid characters. Use A-Z, +, *, ', (), 0-9"

    # Check for balanced parentheses
    if value.count('(') != value.count(')'):
        return False, "Unbalanced parentheses"

    # Check that it's not just operators
    if re.match(r'^[+*\'()]+$', value):
        return False, "Expression must contain variables (letters)"

    return True, ""
