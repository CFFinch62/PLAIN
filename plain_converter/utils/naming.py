"""
Naming convention conversion utilities.

Handles conversion between:
- snake_case (Python functions/variables)
- PascalCase (PLAIN tasks)
- camelCase (PLAIN variables with type prefixes)
- UPPER_SNAKE_CASE (Python constants)
"""

import re


def detect_case_style(name: str) -> str:
    """
    Detect the naming convention of a given identifier.

    Returns one of: 'snake_case', 'PascalCase', 'camelCase',
    'UPPER_SNAKE_CASE', 'unknown'
    """
    if not name:
        return "unknown"

    # UPPER_SNAKE_CASE: all uppercase with underscores (e.g., MAX_VALUE)
    if re.match(r'^[A-Z][A-Z0-9]*(_[A-Z0-9]+)*$', name):
        return "UPPER_SNAKE_CASE"

    # snake_case: lowercase with underscores (e.g., my_variable)
    if re.match(r'^[a-z][a-z0-9]*(_[a-z0-9]+)*$', name):
        return "snake_case"

    # PascalCase: starts with uppercase, no underscores (e.g., MyFunction)
    if re.match(r'^[A-Z][a-zA-Z0-9]*$', name) and '_' not in name:
        return "PascalCase"

    # camelCase: starts with lowercase, has uppercase (e.g., myVariable)
    if re.match(r'^[a-z][a-zA-Z0-9]*$', name) and any(c.isupper() for c in name):
        return "camelCase"

    # Single lowercase word could be snake_case
    if re.match(r'^[a-z][a-z0-9]*$', name):
        return "snake_case"

    return "unknown"


def to_snake_case(name: str) -> str:
    """
    Convert a name to snake_case.

    Examples:
        MyFunction -> my_function
        myVariable -> my_variable
        MAX_VALUE -> max_value
        already_snake -> already_snake
    """
    if not name:
        return name

    # Handle UPPER_SNAKE_CASE
    if detect_case_style(name) == "UPPER_SNAKE_CASE":
        return name.lower()

    # Insert underscore before uppercase letters (handles PascalCase and camelCase)
    result = re.sub(r'([A-Z])', r'_\1', name)

    # Remove leading underscore if present
    if result.startswith('_'):
        result = result[1:]

    # Handle consecutive uppercase letters (e.g., HTMLParser -> html_parser)
    result = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', result)

    return result.lower()


def to_pascal_case(name: str) -> str:
    """
    Convert a name to PascalCase.

    Examples:
        my_function -> MyFunction
        myVariable -> MyVariable
        MAX_VALUE -> MaxValue
        Already -> Already
    """
    if not name:
        return name

    style = detect_case_style(name)

    if style == "PascalCase":
        return name

    if style in ("snake_case", "UPPER_SNAKE_CASE"):
        # Split on underscores and capitalize each part
        parts = name.split('_')
        return ''.join(part.capitalize() for part in parts if part)

    if style == "camelCase":
        # Just capitalize the first letter
        return name[0].upper() + name[1:]

    # Fallback: try splitting on underscores
    parts = name.split('_')
    return ''.join(part.capitalize() for part in parts if part)


def to_camel_case(name: str) -> str:
    """
    Convert a name to camelCase.

    Examples:
        my_function -> myFunction
        MyFunction -> myFunction
        MAX_VALUE -> maxValue
        already -> already
    """
    if not name:
        return name

    pascal = to_pascal_case(name)
    if len(pascal) <= 1:
        return pascal.lower()
    return pascal[0].lower() + pascal[1:]


def to_upper_snake_case(name: str) -> str:
    """
    Convert a name to UPPER_SNAKE_CASE.

    Examples:
        myVariable -> MY_VARIABLE
        MyFunction -> MY_FUNCTION
        max_value -> MAX_VALUE
    """
    return to_snake_case(name).upper()


# PLAIN type prefixes
TYPE_PREFIXES = {
    "int": "integer",
    "flt": "float",
    "str": "string",
    "bln": "boolean",
    "lst": "list",
    "tbl": "table",
}

# Reverse mapping: full type name -> prefix
TYPE_PREFIX_REVERSE = {v: k for k, v in TYPE_PREFIXES.items()}


def add_type_prefix(name: str, type_name: str) -> str:
    """
    Add a PLAIN type prefix to a variable name.

    Examples:
        add_type_prefix("count", "integer") -> "intCount"
        add_type_prefix("name", "string") -> "strName"
        add_type_prefix("is_valid", "boolean") -> "blnIsValid"
    """
    prefix = TYPE_PREFIX_REVERSE.get(type_name, "")
    if not prefix:
        return name

    # Convert the name to camelCase first, then prepend prefix
    camel = to_pascal_case(name)
    return prefix + camel


def strip_type_prefix(name: str) -> tuple[str, str | None]:
    """
    Strip a PLAIN type prefix from a variable name.

    Returns a tuple of (stripped_name, detected_type).
    If no prefix is found, returns (original_name, None).

    Examples:
        strip_type_prefix("intCount") -> ("count", "integer")
        strip_type_prefix("strName") -> ("name", "string")
        strip_type_prefix("myVar") -> ("myVar", None)
    """
    for prefix, type_name in TYPE_PREFIXES.items():
        if name.startswith(prefix) and len(name) > len(prefix):
            # Check that the character after the prefix is uppercase
            # (to avoid matching words like "string" or "integer")
            rest = name[len(prefix):]
            if rest[0].isupper():
                # Convert the rest to snake_case
                stripped = rest[0].lower() + rest[1:]
                return stripped, type_name

    return name, None


def python_func_to_plain_task(name: str) -> str:
    """
    Convert a Python function name to a PLAIN task name.

    Python uses snake_case, PLAIN uses PascalCase.

    Examples:
        python_func_to_plain_task("my_function") -> "MyFunction"
        python_func_to_plain_task("main") -> "Main"
        python_func_to_plain_task("calculate_sum") -> "CalculateSum"
    """
    return to_pascal_case(name)


def plain_task_to_python_func(name: str) -> str:
    """
    Convert a PLAIN task name to a Python function name.

    PLAIN uses PascalCase, Python uses snake_case.

    Examples:
        plain_task_to_python_func("MyFunction") -> "my_function"
        plain_task_to_python_func("Main") -> "main"
        plain_task_to_python_func("CalculateSum") -> "calculate_sum"
    """
    return to_snake_case(name)

