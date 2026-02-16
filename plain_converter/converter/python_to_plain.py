"""
Python to PLAIN code converter.

Uses Python's ast module to parse Python source code and generates
equivalent PLAIN code. Handles variable declarations, functions,
control flow, expressions, error handling, and stdlib mapping.
"""

import ast
import json
from pathlib import Path

from plain_converter.utils.naming import (
    python_func_to_plain_task,
    to_pascal_case,
    to_upper_snake_case,
    add_type_prefix,
)
from plain_converter.utils.warnings import (
    ConversionResult,
    WarningCategory,
)
from plain_converter.utils.formatting import INDENT, format_output, find_long_lines
from plain_converter.stdlib_mapping import load_python_to_plain


class PythonToPlainConverter:
    """Converts Python source code to PLAIN."""

    def __init__(self, add_type_prefixes: bool = False,
                 prefer_choose: bool = True,
                 preserve_comments: bool = True,
                 strict: bool = False):
        self.add_type_prefixes = add_type_prefixes
        self.prefer_choose = prefer_choose
        self.preserve_comments = preserve_comments
        self.strict = strict
        self.result = ConversionResult(code="")
        self.stdlib_map = load_python_to_plain()
        # Track declared variables per scope to distinguish var vs reassignment
        self._declared_vars: list[set[str]] = [set()]
        # Track which Python source lines are comments (for comment preservation)
        self._source_lines: list[str] = []
        # Imports collected from the source for use: block generation
        self._use_modules: list[str] = []   # e.g. ["helpers", "mathlib.geometry"]
        self._use_tasks: list[str] = []     # e.g. ["mathlib.arithmetic.Add"]
        # Python stdlib modules that are handled by the stdlib mapping (skip these)
        self._stdlib_modules: set[str] = {
            "math", "random", "os", "sys", "json", "typing", "dataclasses",
            "collections", "itertools", "functools", "re", "datetime", "time",
            "pathlib", "io", "copy", "string", "abc", "enum",
        }

    def convert(self, source: str) -> ConversionResult:
        """Convert Python source code to PLAIN.

        Args:
            source: Python source code string.

        Returns:
            ConversionResult with the generated PLAIN code and any warnings.
        """
        self.result = ConversionResult(code="")
        self._declared_vars = [set()]
        self._source_lines = source.splitlines()
        self._use_modules = []
        self._use_tasks = []

        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            self.result.add_error(f"Python syntax error: {e}")
            return self.result

        lines = []

        # Preserve leading comments
        if self.preserve_comments:
            for src_line in self._source_lines:
                stripped = src_line.strip()
                if stripped.startswith('#'):
                    lines.append("rem: " + stripped[1:].strip())
                elif stripped == '':
                    lines.append('')
                else:
                    break

        body_lines = self._convert_body(tree.body, indent_level=0)

        # Build use: block from collected imports (inserted before body)
        use_block = self._build_use_block()
        if use_block:
            lines.extend(use_block)
            lines.append("")  # blank line after use: block

        lines.extend(body_lines)

        self.result.code = format_output('\n'.join(lines))

        # Warn about overly long lines
        for line_num, length, line_text in find_long_lines(self.result.code):
            self.result.add_warning(
                WarningCategory.STYLE,
                f"Line exceeds {88} characters ({length} chars)",
                line=line_num,
                source_code=line_text.strip()[:60],
                suggestion="Consider breaking this line into multiple lines",
            )

        return self.result

    # ── Scope helpers ───────────────────────────────────────────

    def _push_scope(self):
        self._declared_vars.append(set())

    def _pop_scope(self):
        self._declared_vars.pop()

    def _is_declared(self, name: str) -> bool:
        for scope in self._declared_vars:
            if name in scope:
                return True
        return False

    def _declare(self, name: str):
        self._declared_vars[-1].add(name)

    # ── Import collection and use: block generation ──────────────

    def _is_stdlib_import(self, module_name: str) -> bool:
        """Check if a module is a Python stdlib module handled by the converter."""
        top_level = module_name.split(".")[0] if module_name else ""
        return top_level in self._stdlib_modules

    def _collect_import(self, node: ast.Import) -> None:
        """Collect 'import module' into use: modules list."""
        for alias in node.names:
            if not self._is_stdlib_import(alias.name):
                if alias.name not in self._use_modules:
                    self._use_modules.append(alias.name)

    def _collect_import_from(self, node: ast.ImportFrom) -> None:
        """Collect 'from module import name' into use: tasks list."""
        module = node.module or ""
        if self._is_stdlib_import(module):
            return
        for alias in node.names:
            task_path = f"{module}.{to_pascal_case(alias.name)}" if module else to_pascal_case(alias.name)
            if task_path not in self._use_tasks:
                self._use_tasks.append(task_path)

    def _build_use_block(self) -> list[str]:
        """Build the PLAIN use: block from collected imports."""
        if not self._use_modules and not self._use_tasks:
            return []

        lines = ["use:"]

        if self._use_modules:
            lines.append(f"{INDENT}modules:")
            for mod in self._use_modules:
                lines.append(f"{INDENT}{INDENT}{mod}")

        if self._use_tasks:
            lines.append(f"{INDENT}tasks:")
            for task in self._use_tasks:
                lines.append(f"{INDENT}{INDENT}{task}")

        return lines

    # ── Type inference ──────────────────────────────────────────

    def _infer_type(self, node: ast.expr) -> str | None:
        """Infer the PLAIN type from a Python AST expression."""
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool):
                return "boolean"
            if isinstance(node.value, int):
                return "integer"
            if isinstance(node.value, float):
                return "float"
            if isinstance(node.value, str):
                return "string"
            if node.value is None:
                return None
        if isinstance(node, ast.List):
            return "list"
        if isinstance(node, ast.Dict):
            return "table"
        if isinstance(node, (ast.JoinedStr, ast.FormattedValue)):
            return "string"
        if isinstance(node, ast.BoolOp):
            return "boolean"
        if isinstance(node, ast.Compare):
            return "boolean"
        if isinstance(node, ast.Call):
            func_name = self._get_call_name(node)
            if func_name in ("int", "to_int"):
                return "integer"
            if func_name in ("float", "to_float"):
                return "float"
            if func_name in ("str", "to_string"):
                return "string"
            if func_name in ("bool",):
                return "boolean"
            if func_name in ("list",):
                return "list"
            if func_name in ("dict",):
                return "table"
        return None

    def _get_call_name(self, node: ast.Call) -> str:
        """Get the function name from a Call node."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        if isinstance(node.func, ast.Attribute):
            return node.func.attr
        return ""

    def _is_main_guard(self, node: ast.If) -> bool:
        """Check if this is an `if __name__ == '__main__':` guard."""
        test = node.test
        if isinstance(test, ast.Compare):
            if (isinstance(test.left, ast.Name) and test.left.id == '__name__'
                    and len(test.ops) == 1 and isinstance(test.ops[0], ast.Eq)
                    and len(test.comparators) == 1
                    and isinstance(test.comparators[0], ast.Constant)
                    and test.comparators[0].value == '__main__'):
                return True
        return False

    # ── Body conversion ─────────────────────────────────────────

    def _convert_body(self, stmts: list[ast.stmt],
                      indent_level: int) -> list[str]:
        """Convert a list of statements to PLAIN lines."""
        lines = []
        prev_stmt = None
        for i, stmt in enumerate(stmts):
            # Add blank line between function defs, or before first non-import
            if isinstance(stmt, (ast.FunctionDef, ast.ClassDef)):
                if prev_stmt is not None and not isinstance(prev_stmt, (ast.FunctionDef, ast.ClassDef)):
                    lines.append('')
            converted = self._convert_stmt(stmt, indent_level)
            lines.extend(converted)
            # Add blank line after function/class definitions
            if isinstance(stmt, (ast.FunctionDef, ast.ClassDef)):
                if i < len(stmts) - 1:
                    lines.append('')
            prev_stmt = stmt
        return lines

    # ── Statement dispatch ──────────────────────────────────────

    def _convert_stmt(self, node: ast.stmt, indent: int) -> list[str]:
        """Convert a single statement to PLAIN lines."""
        prefix = INDENT * indent

        if isinstance(node, ast.FunctionDef):
            return self._convert_function_def(node, indent)
        if isinstance(node, ast.Return):
            return self._convert_return(node, indent)
        if isinstance(node, ast.Assign):
            return self._convert_assign(node, indent)
        if isinstance(node, ast.AugAssign):
            return self._convert_aug_assign(node, indent)
        if isinstance(node, ast.AnnAssign):
            return self._convert_ann_assign(node, indent)
        if isinstance(node, ast.If):
            # Check for if __name__ == "__main__" pattern
            if self._is_main_guard(node):
                # Just emit the body as top-level code
                return self._convert_body(node.body, indent)
            return self._convert_if(node, indent)
        if isinstance(node, ast.For):
            return self._convert_for(node, indent)
        if isinstance(node, ast.While):
            return self._convert_while(node, indent)
        if isinstance(node, ast.Break):
            return [f"{prefix}exit"]
        if isinstance(node, ast.Continue):
            return [f"{prefix}continue"]
        if isinstance(node, ast.Try):
            return self._convert_try(node, indent)
        if isinstance(node, ast.Raise):
            return self._convert_raise(node, indent)
        if isinstance(node, ast.Expr):
            return self._convert_expr_stmt(node, indent)
        if isinstance(node, ast.Pass):
            return [f"{prefix}rem: pass"]
        if isinstance(node, ast.Import):
            self._collect_import(node)
            return []
        if isinstance(node, ast.ImportFrom):
            self._collect_import_from(node)
            return []
        if isinstance(node, ast.ClassDef):
            return self._convert_class_def(node, indent)
        if isinstance(node, ast.Global):
            return []  # Skip global statements
        if isinstance(node, ast.Nonlocal):
            return []  # Skip nonlocal statements
        # Handle Python 3.10+ match/case statements
        if hasattr(ast, 'Match') and isinstance(node, ast.Match):
            return self._convert_match(node, indent)

        # Unsupported statement
        self.result.add_warning(
            WarningCategory.UNSUPPORTED_FEATURE,
            f"Unsupported statement type: {type(node).__name__}",
            line=getattr(node, 'lineno', None),
        )
        return [f"{prefix}rem: UNSUPPORTED: {type(node).__name__}"]

    # ── Variable declarations / assignments ─────────────────────

    def _convert_assign(self, node: ast.Assign, indent: int) -> list[str]:
        """Convert assignment statement."""
        prefix = INDENT * indent
        lines = []
        value_str = self._convert_expr(node.value)

        for target in node.targets:
            if isinstance(target, ast.Name):
                name = target.id
                # Check if this is a constant (UPPER_SNAKE_CASE)
                if name.isupper() and '_' in name or (name.isupper() and len(name) > 1):
                    inferred = self._infer_type(node.value)
                    type_annotation = f" as {self._python_type_to_plain(inferred)}" if inferred else ""
                    lines.append(f"{prefix}fxd {name}{type_annotation} = {value_str}")
                    self._declare(name)
                elif not self._is_declared(name):
                    var_name = name
                    if self.add_type_prefixes:
                        inferred = self._infer_type(node.value)
                        if inferred:
                            var_name = add_type_prefix(name, inferred)
                    lines.append(f"{prefix}var {var_name} = {value_str}")
                    self._declare(name)
                else:
                    lines.append(f"{prefix}{name} = {value_str}")
            elif isinstance(target, ast.Tuple):
                # Tuple unpacking - PLAIN doesn't support this directly
                self.result.add_warning(
                    WarningCategory.UNSUPPORTED_FEATURE,
                    "Tuple unpacking not supported in PLAIN",
                    line=node.lineno,
                    suggestion="Convert to individual assignments",
                )
                names = [self._convert_expr(elt) for elt in target.elts]
                lines.append(f"{prefix}rem: MANUAL FIX: tuple unpacking")
                lines.append(f"{prefix}rem: {', '.join(names)} = {value_str}")
            elif isinstance(target, ast.Subscript):
                target_str = self._convert_expr(target)
                lines.append(f"{prefix}{target_str} = {value_str}")
            elif isinstance(target, ast.Attribute):
                target_str = self._convert_expr(target)
                lines.append(f"{prefix}{target_str} = {value_str}")
            else:
                lines.append(f"{prefix}{self._convert_expr(target)} = {value_str}")

        return lines

    def _convert_aug_assign(self, node: ast.AugAssign, indent: int) -> list[str]:
        """Convert augmented assignment (+=, -=, etc.)."""
        prefix = INDENT * indent
        target = self._convert_expr(node.target)
        value = self._convert_expr(node.value)
        op = self._convert_binop(node.op)
        return [f"{prefix}{target} = {target} {op} {value}"]

    def _convert_ann_assign(self, node: ast.AnnAssign, indent: int) -> list[str]:
        """Convert annotated assignment (x: int = 5) to PLAIN with type."""
        prefix = INDENT * indent
        if node.target and isinstance(node.target, ast.Name):
            name = node.target.id
            plain_type = self._convert_type_annotation(node.annotation)
            type_suffix = f" as {plain_type}" if plain_type else ""

            # Check if constant (UPPER_SNAKE_CASE)
            is_const = name.isupper() and (len(name) > 1 or '_' in name)

            if is_const:
                if node.value:
                    value_str = self._convert_expr(node.value)
                    self._declare(name)
                    return [f"{prefix}fxd {name}{type_suffix} = {value_str}"]
                self._declare(name)
                return [f"{prefix}fxd {name}{type_suffix}"]

            if node.value:
                value_str = self._convert_expr(node.value)
                if not self._is_declared(name):
                    self._declare(name)
                    return [f"{prefix}var {name}{type_suffix} = {value_str}"]
                return [f"{prefix}{name} = {value_str}"]
            else:
                # Type annotation without value
                if not self._is_declared(name):
                    self._declare(name)
                    return [f"{prefix}var {name}{type_suffix}"]
                return [f"{prefix}rem: {name} type annotation (no value)"]
        return []



    # ── Function definitions ────────────────────────────────────

    def _convert_function_def(self, node: ast.FunctionDef,
                              indent: int) -> list[str]:
        """Convert a Python function definition to a PLAIN task."""
        prefix = INDENT * indent
        lines = []

        # Convert docstring to rem: (single-line) or note: (multi-line) comment
        docstring = ast.get_docstring(node)
        if docstring and self.preserve_comments:
            doc_lines = docstring.strip().splitlines()
            if len(doc_lines) == 1:
                lines.append(f"{prefix}rem: {doc_lines[0].strip()}")
            else:
                lines.append(f"{prefix}note: {doc_lines[0].strip()}")
                for doc_line in doc_lines[1:]:
                    lines.append(f"{prefix}    {doc_line.strip()}")

        # Determine task name (snake_case -> PascalCase)
        task_name = python_func_to_plain_task(node.name)

        # Determine if function or procedure
        has_return = self._has_return_value(node)

        # Convert parameters
        params = self._convert_params(node.args)

        # Build the task signature
        if params:
            keyword = "using" if has_return else "with"
            lines.append(f"{prefix}task {task_name} {keyword} ({params})")
        else:
            lines.append(f"{prefix}task {task_name}()")

        # Enter new scope
        self._push_scope()
        # Declare parameters in scope
        for arg in node.args.args:
            self._declare(arg.arg)

        # Convert function body (skip docstring if present)
        body = node.body
        if docstring and body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
            body = body[1:]  # Skip docstring node

        body_lines = self._convert_body(body, indent + 1)
        lines.extend(body_lines)

        self._pop_scope()
        self.result.increment_stat("functions_converted")
        return lines

    def _has_return_value(self, node: ast.FunctionDef) -> bool:
        """Check if a function returns a value (uses 'deliver' vs no return)."""
        for child in ast.walk(node):
            if isinstance(child, ast.Return) and child.value is not None:
                return True
        return False

    def _convert_params(self, args: ast.arguments) -> str:
        """Convert function parameters to PLAIN format with optional types."""
        params = []
        for arg in args.args:
            if arg.arg == 'self':
                continue
            if arg.annotation:
                plain_type = self._convert_type_annotation(arg.annotation)
                params.append(f"{arg.arg} as {plain_type}")
            else:
                params.append(arg.arg)
        return ", ".join(params)

    def _convert_return(self, node: ast.Return, indent: int) -> list[str]:
        """Convert return statement to deliver."""
        prefix = INDENT * indent
        if node.value is not None:
            value = self._convert_expr(node.value)
            return [f"{prefix}deliver {value}"]
        return [f"{prefix}deliver"]

    # ── Control flow ────────────────────────────────────────────

    def _convert_if(self, node: ast.If, indent: int) -> list[str]:
        """Convert if/elif/else to PLAIN if/else or choose/choice/default."""
        # Check if we should use choose (3+ elif branches)
        if self.prefer_choose and self._count_elif_branches(node) >= 3:
            return self._convert_if_as_choose(node, indent)
        return self._convert_if_simple(node, indent)

    def _count_elif_branches(self, node: ast.If) -> int:
        """Count total branches in an if/elif/else chain."""
        count = 1
        current = node
        while current.orelse:
            if len(current.orelse) == 1 and isinstance(current.orelse[0], ast.If):
                count += 1
                current = current.orelse[0]
            else:
                count += 1  # else branch
                break
        return count

    def _convert_if_simple(self, node: ast.If, indent: int) -> list[str]:
        """Convert if/elif/else using PLAIN if/else syntax."""
        prefix = INDENT * indent
        lines = []

        cond = self._convert_expr(node.test)
        lines.append(f"{prefix}if {cond}")
        lines.extend(self._convert_body(node.body, indent + 1))

        orelse = node.orelse
        while orelse:
            if len(orelse) == 1 and isinstance(orelse[0], ast.If):
                elif_node = orelse[0]
                cond = self._convert_expr(elif_node.test)
                lines.append(f"{prefix}else if {cond}")
                lines.extend(self._convert_body(elif_node.body, indent + 1))
                orelse = elif_node.orelse
            else:
                lines.append(f"{prefix}else")
                lines.extend(self._convert_body(orelse, indent + 1))
                break

        return lines

    def _convert_if_as_choose(self, node: ast.If, indent: int) -> list[str]:
        """Convert if/elif/else chain to choose/choice/default."""
        prefix = INDENT * indent
        lines = [f"{prefix}choose true"]

        current = node
        while True:
            cond = self._convert_expr(current.test)
            lines.append(f"{prefix}{INDENT}choice {cond}")
            lines.extend(self._convert_body(current.body, indent + 2))

            if current.orelse:
                if len(current.orelse) == 1 and isinstance(current.orelse[0], ast.If):
                    current = current.orelse[0]
                    continue
                else:
                    lines.append(f"{prefix}{INDENT}default")
                    lines.extend(self._convert_body(current.orelse, indent + 2))
            break

        return lines

    def _convert_match(self, node: ast.Match, indent: int) -> list[str]:
        """Convert Python 3.10+ match/case to PLAIN choose/choice/default."""
        prefix = INDENT * indent
        lines = []

        # Convert the subject expression
        subject = self._convert_expr(node.subject)
        lines.append(f"{prefix}choose {subject}")

        # Track if we have a wildcard case
        has_wildcard = False

        # Convert each case
        for case in node.cases:
            # Check if this is a wildcard pattern (case _:)
            if hasattr(ast, 'MatchAs') and isinstance(case.pattern, ast.MatchAs):
                if case.pattern.name is None:  # This is the _ wildcard
                    has_wildcard = True
                    lines.append(f"{prefix}{INDENT}default")
                    lines.extend(self._convert_body(case.body, indent + 2))
                else:
                    # case x: (capture pattern) - treat as default with variable binding
                    has_wildcard = True
                    lines.append(f"{prefix}{INDENT}default")
                    # Add a comment about the captured variable
                    lines.append(f"{prefix}{INDENT}{INDENT}rem: captured as {case.pattern.name}")
                    lines.extend(self._convert_body(case.body, indent + 2))
            # Literal pattern (case 10:, case "hello":, etc.)
            elif hasattr(ast, 'MatchValue') and isinstance(case.pattern, ast.MatchValue):
                value = self._convert_expr(case.pattern.value)
                lines.append(f"{prefix}{INDENT}choice {value}")
                lines.extend(self._convert_body(case.body, indent + 2))
            # Or pattern (case 1 | 2 | 3:)
            elif hasattr(ast, 'MatchOr') and isinstance(case.pattern, ast.MatchOr):
                # For or patterns, we need to create multiple choice clauses
                for pattern in case.pattern.patterns:
                    if hasattr(ast, 'MatchValue') and isinstance(pattern, ast.MatchValue):
                        value = self._convert_expr(pattern.value)
                        lines.append(f"{prefix}{INDENT}choice {value}")
                        lines.extend(self._convert_body(case.body, indent + 2))
                    else:
                        # Complex pattern in OR - add warning
                        self.result.add_warning(
                            WarningCategory.LOSSY_CONVERSION,
                            f"Complex pattern in match/case OR clause may not convert perfectly",
                            line=getattr(case, 'lineno', None),
                        )
                        lines.append(f"{prefix}{INDENT}rem: MANUAL FIX: complex OR pattern")
            # Sequence pattern, mapping pattern, class pattern, etc.
            else:
                # For complex patterns, add a warning and a comment
                self.result.add_warning(
                    WarningCategory.LOSSY_CONVERSION,
                    f"Complex match pattern ({type(case.pattern).__name__}) converted to default - manual review needed",
                    line=getattr(case, 'lineno', None),
                )
                if not has_wildcard:
                    has_wildcard = True
                    lines.append(f"{prefix}{INDENT}default")
                    lines.append(f"{prefix}{INDENT}{INDENT}rem: MANUAL FIX: complex pattern {type(case.pattern).__name__}")
                    lines.extend(self._convert_body(case.body, indent + 2))

        self.result.increment_stat("match_statements_converted")
        return lines

    def _convert_for(self, node: ast.For, indent: int) -> list[str]:
        """Convert for loop to PLAIN loop."""
        prefix = INDENT * indent
        lines = []

        target = self._convert_expr(node.target)
        self._declare(target)

        # Check for range() pattern
        if isinstance(node.iter, ast.Call) and self._get_call_name(node.iter) == "range":
            lines.extend(self._convert_range_loop(node, target, indent))
        else:
            # for item in collection
            iterable = self._convert_expr(node.iter)
            lines.append(f"{prefix}loop {target} in {iterable}")
            lines.extend(self._convert_body(node.body, indent + 1))

        self.result.increment_stat("loops_converted")
        return lines

    def _convert_range_loop(self, node: ast.For, target: str,
                            indent: int) -> list[str]:
        """Convert for i in range(...) to PLAIN loop i from ... to ..."""
        prefix = INDENT * indent
        call = node.iter
        args = call.args

        if len(args) == 1:
            # range(stop) -> loop target from 0 to stop - 1
            stop_str = self._range_stop_to_inclusive(args[0])
            lines = [f"{prefix}loop {target} from 0 to {stop_str}"]
        elif len(args) == 2:
            # range(start, stop) -> loop target from start to stop - 1
            start = self._convert_expr(args[0])
            stop_str = self._range_stop_to_inclusive(args[1])
            lines = [f"{prefix}loop {target} from {start} to {stop_str}"]
        elif len(args) == 3:
            # range(start, stop, step) -> loop target from start to stop - 1 step s
            start = self._convert_expr(args[0])
            stop_str = self._range_stop_to_inclusive(args[1])
            step = self._convert_expr(args[2])
            lines = [f"{prefix}loop {target} from {start} to {stop_str} step {step}"]
        else:
            lines = [f"{prefix}rem: UNSUPPORTED range() with {len(args)} args"]

        lines.extend(self._convert_body(node.body, indent + 1))
        return lines

    def _range_stop_to_inclusive(self, stop_node: ast.expr) -> str:
        """Convert exclusive stop value to inclusive (subtract 1).
        Tries to simplify: literal N -> N-1, expr + 1 -> expr."""
        # Literal integer: just subtract 1
        if isinstance(stop_node, ast.Constant) and isinstance(stop_node.value, int):
            return str(stop_node.value - 1)
        # expr + 1 pattern: just use expr
        if (isinstance(stop_node, ast.BinOp) and isinstance(stop_node.op, ast.Add)
                and isinstance(stop_node.right, ast.Constant)
                and stop_node.right.value == 1):
            return self._convert_expr(stop_node.left)
        # expr - 1 pattern: emit expr - 2
        if (isinstance(stop_node, ast.BinOp) and isinstance(stop_node.op, ast.Sub)
                and isinstance(stop_node.right, ast.Constant)
                and isinstance(stop_node.right.value, int)):
            new_val = stop_node.right.value + 1
            return f"{self._convert_expr(stop_node.left)} - {new_val}"
        # General case: append - 1
        stop = self._convert_expr(stop_node)
        return f"{stop} - 1"

    def _convert_while(self, node: ast.While, indent: int) -> list[str]:
        """Convert while loop to PLAIN loop."""
        prefix = INDENT * indent
        lines = []

        # while True -> loop (infinite)
        if isinstance(node.test, ast.Constant) and node.test.value is True:
            lines.append(f"{prefix}loop")
        else:
            cond = self._convert_expr(node.test)
            lines.append(f"{prefix}loop {cond}")

        lines.extend(self._convert_body(node.body, indent + 1))
        self.result.increment_stat("loops_converted")
        return lines

    # ── Error handling ──────────────────────────────────────────

    def _convert_try(self, node: ast.Try, indent: int) -> list[str]:
        """Convert try/except/finally to attempt/handle/ensure."""
        prefix = INDENT * indent
        lines = []

        lines.append(f"{prefix}attempt")
        lines.extend(self._convert_body(node.body, indent + 1))

        for handler in node.handlers:
            lines.append(f"{prefix}handle")
            if handler.name:
                lines.append(f"{prefix}{INDENT}rem: caught as {handler.name}")
            lines.extend(self._convert_body(handler.body, indent + 1))

        if node.finalbody:
            lines.append(f"{prefix}ensure")
            lines.extend(self._convert_body(node.finalbody, indent + 1))

        self.result.increment_stat("error_handling_converted")
        return lines

    def _convert_raise(self, node: ast.Raise, indent: int) -> list[str]:
        """Convert raise to abort."""
        prefix = INDENT * indent
        if node.exc:
            # Try to extract the message from Exception("msg")
            if isinstance(node.exc, ast.Call) and node.exc.args:
                msg = self._convert_expr(node.exc.args[0])
                return [f"{prefix}abort {msg}"]
            exc_str = self._convert_expr(node.exc)
            return [f"{prefix}abort {exc_str}"]
        return [f"{prefix}abort \"An error occurred\""]

    # ── Expression statements ───────────────────────────────────

    def _convert_expr_stmt(self, node: ast.Expr, indent: int) -> list[str]:
        """Convert expression statement (function call, etc.)."""
        prefix = INDENT * indent

        # Check if it's a standalone string (possibly a comment/docstring)
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            if self.preserve_comments:
                text = node.value.value.strip()
                text_lines = text.splitlines()
                if len(text_lines) == 1:
                    return [f"{prefix}rem: {text_lines[0].strip()}"]
                else:
                    result = [f"{prefix}note: {text_lines[0].strip()}"]
                    for line in text_lines[1:]:
                        result.append(f"{prefix}    {line.strip()}")
                    return result
            return []

        expr = self._convert_expr(node.value)
        return [f"{prefix}{expr}"]

    # ── Class / record conversion ───────────────────────────────

    def _convert_class_def(self, node: ast.ClassDef, indent: int) -> list[str]:
        """Convert a class to a PLAIN record (if simple) or warn."""
        prefix = INDENT * indent
        lines = []

        # Check for dataclass-like patterns
        class_name = to_pascal_case(node.name)

        # Simple case: class with only __init__ or annotated fields
        has_complex_methods = False
        init_method = None
        other_methods = []

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                if item.name == '__init__':
                    init_method = item
                else:
                    other_methods.append(item)
                    has_complex_methods = True
            elif isinstance(item, ast.AnnAssign):
                pass  # Field annotation - good for records
            elif isinstance(item, ast.Expr) and isinstance(item.value, ast.Constant):
                pass  # Docstring
            else:
                has_complex_methods = True

        if has_complex_methods:
            self.result.add_warning(
                WarningCategory.LOSSY_CONVERSION,
                f"Class '{node.name}' has methods; converted as record (methods lost)",
                line=node.lineno,
                suggestion="PLAIN records don't support methods",
            )

        lines.append(f"{prefix}record {class_name}:")

        # Convert annotated fields
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                field_name = item.target.id
                type_str = self._convert_type_annotation(item.annotation)
                if item.value:
                    default = self._convert_expr(item.value)
                    lines.append(f"{prefix}{INDENT}{field_name} as {type_str} = {default}")
                else:
                    lines.append(f"{prefix}{INDENT}{field_name} as {type_str}")

        # If there's an __init__ but no annotations, try to extract fields
        if init_method and not any(isinstance(i, ast.AnnAssign) for i in node.body):
            for stmt in init_method.body:
                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
                            if target.value.id == 'self':
                                field_name = target.attr
                                inferred = self._infer_type(stmt.value)
                                type_str = self._python_type_to_plain(inferred) if inferred else "string"
                                lines.append(f"{prefix}{INDENT}{field_name} as {type_str}")

        # Convert other methods as separate tasks
        for method in other_methods:
            lines.append('')
            lines.extend(self._convert_function_def(method, indent))

        self.result.increment_stat("classes_converted")
        return lines

    def _convert_type_annotation(self, node: ast.expr) -> str:
        """Convert a Python type annotation to PLAIN type string."""
        type_mapping = {
            'int': 'int', 'float': 'float', 'str': 'string',
            'bool': 'boolean', 'list': 'list', 'dict': 'table',
            'List': 'list', 'Dict': 'table', 'Set': 'list',
            'Tuple': 'list', 'Optional': '', 'Final': '',
        }
        if isinstance(node, ast.Name):
            return type_mapping.get(node.id, node.id)
        if isinstance(node, ast.Attribute):
            # e.g., typing.List → list
            return type_mapping.get(node.attr, node.attr)
        if isinstance(node, ast.Subscript):
            # e.g., List[int], Dict[str, int], Final[int], Optional[str]
            if isinstance(node.value, ast.Name):
                base = node.value.id
            elif isinstance(node.value, ast.Attribute):
                base = node.value.attr
            else:
                base = ""
            # For Final[X] and Optional[X], return the inner type
            if base in ('Final', 'Optional'):
                return self._convert_type_annotation(node.slice)
            # For generic containers, return the base PLAIN type (drop params)
            return type_mapping.get(base, base)
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        return "string"  # Default fallback

    def _python_type_to_plain(self, type_name: str | None) -> str:
        """Convert a Python type name to PLAIN type name."""
        if type_name is None:
            return "string"
        mapping = {
            "integer": "int", "float": "float", "string": "string",
            "boolean": "boolean", "list": "list", "table": "table",
        }
        return mapping.get(type_name, type_name)

    # ── Expression conversion ───────────────────────────────────

    def _convert_expr(self, node: ast.expr) -> str:
        """Convert a Python expression to PLAIN."""
        if isinstance(node, ast.Constant):
            return self._convert_constant(node)
        if isinstance(node, ast.Name):
            return self._convert_name(node)
        if isinstance(node, ast.BinOp):
            return self._convert_binop_expr(node)
        if isinstance(node, ast.UnaryOp):
            return self._convert_unaryop(node)
        if isinstance(node, ast.BoolOp):
            return self._convert_boolop(node)
        if isinstance(node, ast.Compare):
            return self._convert_compare(node)
        if isinstance(node, ast.Call):
            return self._convert_call(node)
        if isinstance(node, ast.Attribute):
            return self._convert_attribute(node)
        if isinstance(node, ast.Subscript):
            return self._convert_subscript(node)
        if isinstance(node, ast.List):
            return self._convert_list(node)
        if isinstance(node, ast.Dict):
            return self._convert_dict(node)
        if isinstance(node, ast.Tuple):
            return self._convert_tuple(node)
        if isinstance(node, ast.JoinedStr):
            return self._convert_fstring(node)
        if isinstance(node, ast.IfExp):
            return self._convert_ifexp(node)
        if isinstance(node, ast.FormattedValue):
            return self._convert_formatted_value(node)

        self.result.add_warning(
            WarningCategory.UNSUPPORTED_FEATURE,
            f"Unsupported expression: {type(node).__name__}",
            line=getattr(node, 'lineno', None),
        )
        return f"/* UNSUPPORTED: {type(node).__name__} */"

    def _convert_constant(self, node: ast.Constant) -> str:
        """Convert a constant value."""
        if isinstance(node.value, bool):
            return "true" if node.value else "false"
        if node.value is None:
            return "null"
        if isinstance(node.value, str):
            return f'"{node.value}"'
        return str(node.value)

    def _convert_name(self, node: ast.Name) -> str:
        """Convert a name reference."""
        # Map Python built-in constants
        mapping = {"True": "true", "False": "false", "None": "null"}
        return mapping.get(node.id, node.id)

    def _convert_binop(self, op: ast.operator) -> str:
        """Convert a binary operator to its string representation."""
        ops = {
            ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/",
            ast.FloorDiv: "//", ast.Mod: "%", ast.Pow: "**",
            ast.BitAnd: "&", ast.BitOr: "|", ast.BitXor: "^",
            ast.LShift: "<<", ast.RShift: ">>",
        }
        return ops.get(type(op), "?")

    def _convert_binop_expr(self, node: ast.BinOp) -> str:
        """Convert a binary operation expression."""
        left = self._convert_expr(node.left)
        right = self._convert_expr(node.right)
        op = self._convert_binop(node.op)

        # Special case: string concatenation with + -> &
        if isinstance(node.op, ast.Add):
            if self._is_string_expr(node.left) or self._is_string_expr(node.right):
                op = "&"

        return f"{left} {op} {right}"

    def _is_string_expr(self, node: ast.expr) -> bool:
        """Check if an expression is likely a string."""
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return True
        if isinstance(node, (ast.JoinedStr, ast.FormattedValue)):
            return True
        if isinstance(node, ast.Call):
            name = self._get_call_name(node)
            if name in ("str", "to_string"):
                return True
        return False

    def _convert_unaryop(self, node: ast.UnaryOp) -> str:
        """Convert unary operation."""
        operand = self._convert_expr(node.operand)
        if isinstance(node.op, ast.Not):
            return f"not {operand}"
        if isinstance(node.op, ast.USub):
            return f"-{operand}"
        if isinstance(node.op, ast.UAdd):
            return f"+{operand}"
        if isinstance(node.op, ast.Invert):
            return f"~{operand}"
        return operand

    def _convert_boolop(self, node: ast.BoolOp) -> str:
        """Convert boolean operation (and/or)."""
        op = "and" if isinstance(node.op, ast.And) else "or"
        parts = [self._convert_expr(v) for v in node.values]
        return f" {op} ".join(parts)

    def _convert_compare(self, node: ast.Compare) -> str:
        """Convert comparison expression."""
        parts = [self._convert_expr(node.left)]
        for op, comparator in zip(node.ops, node.comparators):
            op_str = self._convert_cmpop(op)
            comp_str = self._convert_expr(comparator)

            # Special case: 'in' operator -> contains()
            if isinstance(op, ast.In):
                return f"contains({comp_str}, {parts[0]})"
            if isinstance(op, ast.NotIn):
                return f"not contains({comp_str}, {parts[0]})"

            parts.append(op_str)
            parts.append(comp_str)
        return " ".join(parts)

    def _convert_cmpop(self, op: ast.cmpop) -> str:
        """Convert comparison operator."""
        ops = {
            ast.Eq: "==", ast.NotEq: "!=", ast.Lt: "<", ast.LtE: "<=",
            ast.Gt: ">", ast.GtE: ">=", ast.Is: "==", ast.IsNot: "!=",
            ast.In: "in", ast.NotIn: "not in",
        }
        return ops.get(type(op), "?")

    def _convert_call(self, node: ast.Call) -> str:
        """Convert a function call, applying stdlib mappings."""
        args = [self._convert_expr(a) for a in node.args]
        kwargs = [f"{kw.arg}: {self._convert_expr(kw.value)}"
                  for kw in node.keywords if kw.arg]

        # Handle method calls (obj.method(args))
        if isinstance(node.func, ast.Attribute):
            return self._convert_method_call(node, args, kwargs)

        # Handle regular function calls
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id

        # Check stdlib mapping
        mapped = self._map_builtin_call(func_name, args)
        if mapped:
            return mapped

        # Convert function name to PascalCase for user-defined functions
        plain_name = python_func_to_plain_task(func_name) if func_name else self._convert_expr(node.func)

        all_args = args + kwargs
        return f"{plain_name}({', '.join(all_args)})"

    def _map_builtin_call(self, func_name: str, args: list[str]) -> str | None:
        """Map a Python builtin function to PLAIN equivalent."""
        builtins = self.stdlib_map.get("builtin_functions", {})
        mapping = builtins.get(func_name)
        if not mapping:
            return None

        plain_name = mapping.get("plain_name")
        call_style = mapping.get("call_style", "function")

        # Skip special-case entries (e.g. isinstance) that need custom handling
        if call_style == "special" or plain_name is None:
            return None

        return f"{plain_name}({', '.join(args)})"

    def _convert_method_call(self, node: ast.Call, args: list[str],
                             kwargs: list[str]) -> str:
        """Convert obj.method(args) to PLAIN function call."""
        obj = self._convert_expr(node.func.value)
        method = node.func.attr

        # Check for module-qualified calls: math.floor(), random.randint(), os.remove()
        if isinstance(node.func.value, ast.Name):
            module_name = node.func.value.id
            qualified = f"{module_name}.{method}"
            for category in ("math_module", "random_module", "os_module"):
                cat = self.stdlib_map.get(category, {})
                mapping = cat.get(qualified)
                if mapping and isinstance(mapping, dict):
                    plain_name = mapping["plain_name"]
                    return f"{plain_name}({', '.join(args)})"

        # Check for user-imported module-qualified calls: helpers.add_numbers()
        if isinstance(node.func.value, ast.Name):
            module_name = node.func.value.id
            if module_name in self._use_modules:
                plain_method = to_pascal_case(method)
                return f"{module_name}.{plain_method}({', '.join(args)})"

        # Check for deeply-qualified calls: os.path.exists()
        if isinstance(node.func.value, ast.Attribute):
            inner = node.func.value
            if isinstance(inner.value, ast.Name):
                qualified = f"{inner.value.id}.{inner.attr}.{method}"
                for category in ("os_module",):
                    cat = self.stdlib_map.get(category, {})
                    mapping = cat.get(qualified)
                    if mapping and isinstance(mapping, dict):
                        plain_name = mapping["plain_name"]
                        return f"{plain_name}({', '.join(args)})"

        # Check str_methods, list_methods, dict_methods mappings
        for category in ("str_methods", "list_methods", "dict_methods"):
            mapping = self.stdlib_map.get(category, {}).get(method)
            if mapping and isinstance(mapping, dict):
                plain_name = mapping["plain_name"]
                arg_transform = mapping.get("arg_transform", "object_becomes_first_arg")

                if arg_transform == "swap_object_and_first_arg" and args:
                    # sep.join(lst) -> join(lst, sep)
                    all_args = args + [obj]
                    return f"{plain_name}({', '.join(all_args)})"
                else:
                    # Default: object becomes first arg
                    all_args = [obj] + args
                    return f"{plain_name}({', '.join(all_args)})"

        # Fallback: keep as method call notation or convert
        all_args = [obj] + args + kwargs
        return f"{method}({', '.join(all_args)})"

    def _convert_attribute(self, node: ast.Attribute) -> str:
        """Convert attribute access."""
        value = self._convert_expr(node.value)
        return f"{value}.{node.attr}"

    def _convert_subscript(self, node: ast.Subscript) -> str:
        """Convert subscript/indexing."""
        value = self._convert_expr(node.value)
        slice_str = self._convert_expr(node.slice)
        return f"{value}[{slice_str}]"

    def _convert_list(self, node: ast.List) -> str:
        """Convert list literal."""
        elts = [self._convert_expr(e) for e in node.elts]
        return f"[{', '.join(elts)}]"

    def _convert_dict(self, node: ast.Dict) -> str:
        """Convert dict literal to PLAIN table."""
        pairs = []
        for key, value in zip(node.keys, node.values):
            k = self._convert_expr(key)
            v = self._convert_expr(value)
            pairs.append(f"{k}: {v}")
        return "{" + ", ".join(pairs) + "}"

    def _convert_tuple(self, node: ast.Tuple) -> str:
        """Convert tuple (PLAIN doesn't have tuples, use list)."""
        elts = [self._convert_expr(e) for e in node.elts]
        self.result.add_warning(
            WarningCategory.LOSSY_CONVERSION,
            "Tuple converted to list (PLAIN has no tuple type)",
            line=getattr(node, 'lineno', None),
        )
        return f"[{', '.join(elts)}]"

    def _convert_fstring(self, node: ast.JoinedStr) -> str:
        """Convert f-string to v-string."""
        parts = []
        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                parts.append(value.value)
            elif isinstance(value, ast.FormattedValue):
                expr = self._convert_expr(value.value)
                parts.append(f"{{{expr}}}")
            else:
                parts.append(self._convert_expr(value))
        return 'v"' + ''.join(parts) + '"'

    def _convert_formatted_value(self, node: ast.FormattedValue) -> str:
        """Convert a formatted value within an f-string."""
        return self._convert_expr(node.value)

    def _convert_ifexp(self, node: ast.IfExp) -> str:
        """Convert ternary expression (x if cond else y).
        PLAIN doesn't have ternary expressions, so we note it."""
        self.result.add_warning(
            WarningCategory.LOSSY_CONVERSION,
            "Ternary expression converted inline (PLAIN has no ternary)",
            line=getattr(node, 'lineno', None),
        )
        body = self._convert_expr(node.body)
        test = self._convert_expr(node.test)
        orelse = self._convert_expr(node.orelse)
        # Return as comment-annotated expression
        return f"{body} rem: if {test} else {orelse}"