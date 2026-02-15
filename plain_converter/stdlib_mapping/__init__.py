"""
Standard library mapping between Python and PLAIN.

Provides functions to load and query the mapping files.
"""

import json
from pathlib import Path

_MAPPING_DIR = Path(__file__).parent


def load_python_to_plain() -> dict:
    """Load the Python -> PLAIN stdlib mapping."""
    path = _MAPPING_DIR / "python_to_plain.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_plain_to_python() -> dict:
    """Load the PLAIN -> Python stdlib mapping."""
    path = _MAPPING_DIR / "plain_to_python.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_python_builtin_mapping(func_name: str) -> dict | None:
    """Look up a Python builtin function in the mapping."""
    data = load_python_to_plain()
    return data.get("builtin_functions", {}).get(func_name)


def get_python_method_mapping(method_name: str, obj_type: str = "str") -> dict | None:
    """Look up a Python method in the mapping by type category."""
    data = load_python_to_plain()
    category = f"{obj_type}_methods"
    return data.get(category, {}).get(method_name)


def get_plain_function_mapping(func_name: str) -> dict | None:
    """Look up a PLAIN function across all categories."""
    data = load_plain_to_python()
    # Search across all categories
    for category_name, category in data.items():
        if category_name.startswith("_"):
            continue
        if isinstance(category, dict) and func_name in category:
            entry = category[func_name]
            if isinstance(entry, dict):
                return entry
    return None