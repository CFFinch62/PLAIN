"""
Code Formatter for PLAIN IDE
Normalizes indentation, converts tabs to spaces, and trims trailing whitespace.

Because PLAIN uses indentation to define block structure (like Python),
the formatter cannot arbitrarily re-indent code.  Instead it:
  1. Expands tabs to spaces (matching the Go interpreter's tab=4 rule).
  2. Snaps each line's indent to the nearest valid level, building a
     consistent indent stack as it goes.
  3. Trims trailing whitespace from every line.
  4. Collapses excessive consecutive blank lines.
  5. Ensures a single trailing newline.
"""

from __future__ import annotations


def format_plain_code(source: str, indent_size: int = 4) -> str:
    """Format PLAIN source code.

    Args:
        source: The raw PLAIN source code.
        indent_size: Number of spaces per indentation level (default 4).

    Returns:
        The formatted source code.
    """
    lines = source.split('\n')

    # Phase 1: expand tabs and strip trailing whitespace
    expanded = []
    for line in lines:
        # Expand tabs to spaces (each tab = indent_size spaces)
        line = line.replace('\t', ' ' * indent_size)
        # Strip trailing whitespace
        line = line.rstrip()
        expanded.append(line)

    # Phase 2: normalize indentation using an indent stack
    normalized = _normalize_indentation(expanded, indent_size)

    # Phase 3: collapse runs of 3+ blank lines down to 2
    normalized = _collapse_blank_lines(normalized, max_consecutive=2)

    # Phase 4: trim trailing blank lines, ensure single final newline
    while normalized and normalized[-1] == '':
        normalized.pop()
    normalized.append('')  # single trailing newline

    return '\n'.join(normalized)


def _normalize_indentation(lines: list[str], indent_size: int) -> list[str]:
    """Normalize indentation so every indent level is a clean multiple of indent_size.

    Uses an indent stack (similar to the lexer) to track nesting:
      - If a line's raw indent is greater than the current level, push a new level
        and snap it to current + indent_size.
      - If a line's raw indent is less than the current level, pop back to the
        closest matching level on the stack.
      - If equal, keep the same level.

    This handles mixed tabs/spaces gracefully: a line indented with 1 tab (expanded
    to 4 spaces) and a line indented with 4 spaces will be treated identically.
    Lines indented with e.g. 3 tabs (12 spaces) after a line at 8 spaces will be
    snapped to 12 (the next level up).
    """
    result: list[str] = []
    # Stack of (raw_indent, normalized_indent) pairs
    indent_stack: list[tuple[int, int]] = [(0, 0)]

    in_note_block = False
    note_raw_indent = 0
    note_norm_indent = 0

    for line in lines:
        stripped = line.lstrip()

        # Blank lines – preserve as empty
        if stripped == '':
            result.append('')
            continue

        raw_indent = len(line) - len(stripped)

        # --- note: block handling ---
        # Everything indented deeper than the note: line is part of the block.
        # Preserve relative indentation within the block.
        if in_note_block:
            if raw_indent > note_raw_indent:
                # Still inside the note block
                relative = raw_indent - note_raw_indent
                result.append(' ' * (note_norm_indent + relative) + stripped)
                continue
            else:
                # Block ended – fall through to process normally
                in_note_block = False

        # Determine the normalized indent for this line
        current_raw = indent_stack[-1][0]
        current_norm = indent_stack[-1][1]

        if raw_indent > current_raw:
            # Indenting deeper – push new level
            new_norm = current_norm + indent_size
            indent_stack.append((raw_indent, new_norm))
            norm_indent = new_norm
        elif raw_indent < current_raw:
            # Dedenting – pop to the closest level at or below raw_indent
            while len(indent_stack) > 1 and indent_stack[-1][0] > raw_indent:
                indent_stack.pop()
            # If exact match in stack, use that level
            if indent_stack[-1][0] == raw_indent:
                norm_indent = indent_stack[-1][1]
            else:
                # raw_indent doesn't match any previous level exactly.
                # Snap to the top of the stack (closest match).
                norm_indent = indent_stack[-1][1]
        else:
            # Same level
            norm_indent = current_norm

        result.append(' ' * norm_indent + stripped)

        # Start tracking note: blocks
        if stripped.startswith('note:'):
            in_note_block = True
            note_raw_indent = raw_indent
            note_norm_indent = norm_indent

    return result


def _collapse_blank_lines(lines: list[str], max_consecutive: int = 2) -> list[str]:
    """Collapse runs of blank lines to at most max_consecutive."""
    result: list[str] = []
    blank_count = 0
    for line in lines:
        if line.strip() == '':
            blank_count += 1
            if blank_count <= max_consecutive:
                result.append(line)
        else:
            blank_count = 0
            result.append(line)
    return result
