"""
Code formatting utilities for generated output.

Handles indentation, blank lines, and general code formatting
for both Python and PLAIN output.
"""

INDENT = "    "  # 4 spaces for both Python and PLAIN
MAX_LINE_LENGTH = 88  # PEP 8 compatible (matches Black default)


def indent_code(code: str, level: int = 1) -> str:
    """
    Indent a block of code by the given level.

    Args:
        code: The code to indent.
        level: Number of indentation levels (default: 1).

    Returns:
        The indented code.
    """
    prefix = INDENT * level
    lines = code.split('\n')
    indented = []
    for line in lines:
        if line.strip():  # Don't indent empty lines
            indented.append(prefix + line)
        else:
            indented.append('')
    return '\n'.join(indented)


def dedent_code(code: str, level: int = 1) -> str:
    """
    Remove indentation from a block of code.

    Args:
        code: The code to dedent.
        level: Number of indentation levels to remove (default: 1).

    Returns:
        The dedented code.
    """
    prefix = INDENT * level
    lines = code.split('\n')
    dedented = []
    for line in lines:
        if line.startswith(prefix):
            dedented.append(line[len(prefix):])
        else:
            dedented.append(line)
    return '\n'.join(dedented)


def normalize_blank_lines(code: str, max_consecutive: int = 2) -> str:
    """
    Normalize consecutive blank lines in code.

    Args:
        code: The code to normalize.
        max_consecutive: Maximum number of consecutive blank lines allowed.

    Returns:
        The normalized code.
    """
    lines = code.split('\n')
    result = []
    blank_count = 0

    for line in lines:
        if line.strip() == '':
            blank_count += 1
            if blank_count <= max_consecutive:
                result.append('')
        else:
            blank_count = 0
            result.append(line)

    return '\n'.join(result)


def ensure_trailing_newline(code: str) -> str:
    """Ensure the code ends with exactly one newline."""
    return code.rstrip('\n') + '\n'


def get_indent_level(line: str) -> int:
    """
    Get the indentation level of a line.

    Returns the number of indentation levels (each level = 4 spaces).
    """
    spaces = len(line) - len(line.lstrip())
    return spaces // len(INDENT)


def strip_trailing_whitespace(code: str) -> str:
    """Remove trailing whitespace from each line."""
    lines = code.split('\n')
    return '\n'.join(line.rstrip() for line in lines)


def find_long_lines(code: str, max_length: int = MAX_LINE_LENGTH
                    ) -> list[tuple[int, int, str]]:
    """
    Find lines that exceed the maximum length.

    Args:
        code: The code to check.
        max_length: Maximum allowed line length.

    Returns:
        List of (line_number, length, line_text) tuples for long lines.
        Line numbers are 1-based.
    """
    long_lines = []
    for i, line in enumerate(code.splitlines(), start=1):
        if len(line) > max_length:
            long_lines.append((i, len(line), line))
    return long_lines


def format_output(code: str) -> str:
    """
    Apply standard formatting to output code.

    - Normalize blank lines
    - Strip trailing whitespace
    - Ensure trailing newline
    """
    code = strip_trailing_whitespace(code)
    code = normalize_blank_lines(code)
    code = ensure_trailing_newline(code)
    return code

