"""
PLAIN to Python code converter.

Parses PLAIN source code using the PLAIN parser and generates
equivalent Python code. Handles variables, tasks, control flow,
expressions, error handling, and stdlib mapping.
"""

import json
from pathlib import Path

from plain_converter.converter.plain_parser import (
    parse_plain,
    Program, Statement, Expression, BlockStatement,
    VarStatement, FxdStatement, AssignStatement, ExpressionStatement,
    DeliverStatement, AbortStatement, SwapStatement, ExitStatement,
    ContinueStatement, CommentStatement,
    IfStatement, ChooseStatement, ChoiceClause, LoopStatement,
    TaskStatement, AttemptStatement, HandleClause,
    RecordStatement, RecordField, UseStatement,
    Identifier, IntegerLiteral, FloatLiteral, StringLiteral,
    InterpolatedString, BooleanLiteral, NullLiteral,
    ListLiteral, TableLiteral,
    PrefixExpression, InfixExpression, CallExpression,
    IndexExpression, DotExpression,
)
from plain_converter.utils.naming import plain_task_to_python_func, to_snake_case
from plain_converter.utils.warnings import ConversionResult, WarningCategory
from plain_converter.utils.formatting import INDENT, format_output, find_long_lines
from plain_converter.stdlib_mapping import load_plain_to_python


class PlainToPythonConverter:
    """Converts PLAIN source code to Python."""

    # Mapping of PLAIN type names to Python type names
    PLAIN_TO_PYTHON_TYPES = {
        "integer": "int", "int": "int",
        "float": "float", "flt": "float",
        "string": "str", "str": "str",
        "boolean": "bool", "bln": "bool",
        "list": "list", "lst": "list",
        "table": "dict", "tbl": "dict",
    }

    def __init__(self, preserve_comments: bool = True, strict: bool = False):
        self.preserve_comments = preserve_comments
        self.strict = strict
        self.result = ConversionResult(code="")
        self.stdlib_map = load_plain_to_python()
        self._stdlib_flat: dict[str, dict] = {}
        self._flatten_stdlib()
        self._imports: set[str] = set()
        self._typing_imports: set[str] = set()
        self._user_imports: list[str] = []  # from use: blocks, in order
        self._user_modules: set[str] = set()  # module names from use: blocks
        self._has_main = False

    def _flatten_stdlib(self) -> None:
        """Flatten the stdlib mapping for quick lookup."""
        for category_name, category in self.stdlib_map.items():
            if category_name.startswith("_"):
                continue
            if isinstance(category, dict):
                for func_name, entry in category.items():
                    if isinstance(entry, dict):
                        self._stdlib_flat[func_name] = entry

    def _plain_type_to_python(self, plain_type: str) -> str:
        """Convert a PLAIN type name to Python type name."""
        return self.PLAIN_TO_PYTHON_TYPES.get(plain_type, plain_type)

    def convert(self, source: str) -> ConversionResult:
        """Convert PLAIN source code to Python."""
        self.result = ConversionResult(code="")
        self._imports = set()
        self._typing_imports = set()
        self._user_imports = []
        self._user_modules = set()
        self._has_main = False

        program, errors = parse_plain(source)
        for err in errors:
            self.result.add_error(f"Parse error: {err}")
        if errors and self.strict:
            return self.result

        lines: list[str] = []
        for stmt in program.statements:
            converted = self._convert_statement(stmt, 0)
            if converted:
                lines.append(converted)

        # Build final output
        output_parts: list[str] = []

        # Imports (typing first, then stdlib, then user imports)
        has_imports = bool(self._imports) or bool(self._typing_imports) or bool(self._user_imports)
        if self._typing_imports:
            typing_names = ", ".join(sorted(self._typing_imports))
            output_parts.append(f"from typing import {typing_names}")
        if self._imports:
            for imp in sorted(self._imports):
                output_parts.append(f"import {imp}")
        if self._user_imports:
            for imp_line in self._user_imports:
                output_parts.append(imp_line)
        if has_imports:
            output_parts.append("")

        # Main code
        output_parts.append("\n\n".join(lines))

        # Add if __name__ == "__main__" guard if there's a main function
        if self._has_main:
            output_parts.append("")
            output_parts.append("")
            output_parts.append('if __name__ == "__main__":')
            output_parts.append(f"{INDENT}main()")

        self.result.code = format_output("\n".join(output_parts))
        self.result.increment_stat("statements_converted", len(program.statements))

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

    # ---- Statement Conversion ----

    def _convert_statement(self, stmt: Statement, indent: int) -> str:
        """Convert a statement to Python code."""
        prefix = INDENT * indent
        if isinstance(stmt, TaskStatement):
            return self._convert_task(stmt, indent)
        if isinstance(stmt, VarStatement):
            return self._convert_var(stmt, prefix)
        if isinstance(stmt, FxdStatement):
            return self._convert_fxd(stmt, prefix)
        if isinstance(stmt, AssignStatement):
            return self._convert_assign(stmt, prefix)
        if isinstance(stmt, ExpressionStatement):
            return f"{prefix}{self._convert_expr(stmt.expression)}"
        if isinstance(stmt, DeliverStatement):
            return self._convert_deliver(stmt, prefix)
        if isinstance(stmt, AbortStatement):
            return self._convert_abort(stmt, prefix)
        if isinstance(stmt, IfStatement):
            return self._convert_if(stmt, indent)
        if isinstance(stmt, ChooseStatement):
            return self._convert_choose(stmt, indent)
        if isinstance(stmt, LoopStatement):
            return self._convert_loop(stmt, indent)
        if isinstance(stmt, AttemptStatement):
            return self._convert_attempt(stmt, indent)
        if isinstance(stmt, SwapStatement):
            return self._convert_swap(stmt, prefix)
        if isinstance(stmt, ExitStatement):
            return f"{prefix}break"
        if isinstance(stmt, ContinueStatement):
            return f"{prefix}continue"
        if isinstance(stmt, CommentStatement):
            if self.preserve_comments and stmt.text:
                if stmt.is_block:
                    # Multi-line note: block → multi-line # comments
                    comment_lines = []
                    for line in stmt.text.splitlines():
                        stripped = line.strip()
                        if stripped:
                            comment_lines.append(f"{prefix}# {stripped}")
                        else:
                            comment_lines.append(f"{prefix}#")
                    return "\n".join(comment_lines) if comment_lines else ""
                return f"{prefix}# {stmt.text}"
            return ""
        if isinstance(stmt, RecordStatement):
            return self._convert_record(stmt, indent)
        if isinstance(stmt, UseStatement):
            self._convert_use_statement(stmt)
            return ""
        self.result.add_warning(
            WarningCategory.UNSUPPORTED_FEATURE,
            f"Unknown statement type: {type(stmt).__name__}"
        )
        return ""

    def _convert_use_statement(self, stmt: UseStatement) -> None:
        """Convert a use: block into Python import statements.

        - assemblies: are declarative markers; skip them
        - modules: X → import X
        - modules: X.Y → from X import Y
        - tasks: X.TaskName → from X import task_name  (snake_case)
        - tasks: X.Y.TaskName → from X.Y import task_name
        """
        # assemblies are declarative only — no Python equivalent

        # Track module names for qualified call conversion
        for mod_path in stmt.modules:
            # Store both the full path and the last component (the imported name)
            parts = mod_path.split(".")
            self._user_modules.add(parts[-1] if len(parts) > 1 else mod_path)

        for mod_path in stmt.modules:
            parts = mod_path.split(".")
            if len(parts) == 1:
                imp_line = f"import {mod_path}"
            else:
                # e.g. mathlib.geometry → from mathlib import geometry
                parent = ".".join(parts[:-1])
                child = parts[-1]
                imp_line = f"from {parent} import {child}"
            if imp_line not in self._user_imports:
                self._user_imports.append(imp_line)

        for task_path in stmt.tasks:
            parts = task_path.split(".")
            if len(parts) < 2:
                # bare task name — unlikely but handle gracefully
                py_name = to_snake_case(parts[0])
                imp_line = f"import {py_name}"
            else:
                # e.g. mathlib.arithmetic.Add → from mathlib.arithmetic import add
                module = ".".join(parts[:-1])
                task_name = to_snake_case(parts[-1])
                imp_line = f"from {module} import {task_name}"
            if imp_line not in self._user_imports:
                self._user_imports.append(imp_line)

    def _convert_task(self, stmt: TaskStatement, indent: int) -> str:
        """Convert task statement to Python def."""
        prefix = INDENT * indent
        py_name = plain_task_to_python_func(stmt.name)
        if py_name == "main":
            self._has_main = True
        # Build parameter list with optional type hints
        param_parts = []
        for param_name, param_type in stmt.parameters:
            if param_type:
                py_type = self._plain_type_to_python(param_type)
                param_parts.append(f"{param_name}: {py_type}")
            else:
                param_parts.append(param_name)
        params = ", ".join(param_parts)
        header = f"{prefix}def {py_name}({params}):"
        body_lines = self._convert_block(stmt.body, indent + 1)
        if not body_lines:
            body_lines = f"{INDENT * (indent + 1)}pass"
        return f"{header}\n{body_lines}"

    def _convert_var(self, stmt: VarStatement, prefix: str) -> str:
        """Convert var statement to Python assignment with optional type hint."""
        name = stmt.name
        if stmt.type_name:
            py_type = self._plain_type_to_python(stmt.type_name)
            if stmt.value is not None:
                val = self._convert_expr(stmt.value)
                return f"{prefix}{name}: {py_type} = {val}"
            return f"{prefix}{name}: {py_type}"
        if stmt.value is not None:
            val = self._convert_expr(stmt.value)
            return f"{prefix}{name} = {val}"
        # var without value - initialize to None
        return f"{prefix}{name} = None"

    def _convert_fxd(self, stmt: FxdStatement, prefix: str) -> str:
        """Convert fxd (constant) to Python Final assignment."""
        name = stmt.name.upper()  # Python convention: UPPER_CASE constants
        if stmt.type_name:
            py_type = self._plain_type_to_python(stmt.type_name)
            self._typing_imports.add("Final")
            if stmt.value is not None:
                val = self._convert_expr(stmt.value)
                return f"{prefix}{name}: Final[{py_type}] = {val}"
            return f"{prefix}{name}: Final[{py_type}]"
        if stmt.value is not None:
            val = self._convert_expr(stmt.value)
            return f"{prefix}{name} = {val}  # constant"
        return f"{prefix}{name} = None  # constant"

    def _convert_assign(self, stmt: AssignStatement, prefix: str) -> str:
        """Convert assignment statement."""
        target = self._convert_expr(stmt.name)
        val = self._convert_expr(stmt.value)
        return f"{prefix}{target} = {val}"

    def _convert_deliver(self, stmt: DeliverStatement, prefix: str) -> str:
        """Convert deliver to return."""
        if stmt.return_value is not None:
            val = self._convert_expr(stmt.return_value)
            return f"{prefix}return {val}"
        return f"{prefix}return"

    def _convert_abort(self, stmt: AbortStatement, prefix: str) -> str:
        """Convert abort to raise."""
        if stmt.message is not None:
            msg = self._convert_expr(stmt.message)
            return f"{prefix}raise Exception({msg})"
        return f"{prefix}raise Exception()"

    def _convert_swap(self, stmt: SwapStatement, prefix: str) -> str:
        """Convert swap to Python tuple swap."""
        left = self._convert_expr(stmt.left)
        right = self._convert_expr(stmt.right)
        return f"{prefix}{left}, {right} = {right}, {left}"

    def _convert_if(self, stmt: IfStatement, indent: int) -> str:
        """Convert if/else to Python if/elif/else."""
        prefix = INDENT * indent
        cond = self._convert_expr(stmt.condition)
        lines = [f"{prefix}if {cond}:"]
        body = self._convert_block(stmt.consequence, indent + 1)
        lines.append(body if body else f"{INDENT * (indent + 1)}pass")

        if stmt.alternative is not None:
            # Check if it's an elif (nested if in the alternative block)
            alt_stmts = stmt.alternative.statements
            if (len(alt_stmts) == 1 and isinstance(alt_stmts[0], IfStatement)):
                # Convert to elif
                elif_stmt = alt_stmts[0]
                elif_cond = self._convert_expr(elif_stmt.condition)
                lines.append(f"{prefix}elif {elif_cond}:")
                elif_body = self._convert_block(elif_stmt.consequence, indent + 1)
                lines.append(elif_body if elif_body else f"{INDENT * (indent + 1)}pass")
                if elif_stmt.alternative is not None:
                    # Recursively handle more elif/else
                    rest = self._convert_else_chain(elif_stmt.alternative, indent)
                    lines.append(rest)
            else:
                lines.append(f"{prefix}else:")
                alt_body = self._convert_block(stmt.alternative, indent + 1)
                lines.append(alt_body if alt_body else f"{INDENT * (indent + 1)}pass")

        return "\n".join(lines)

    def _convert_else_chain(self, block: BlockStatement, indent: int) -> str:
        """Recursively convert else/elif chains."""
        prefix = INDENT * indent
        stmts = block.statements
        if len(stmts) == 1 and isinstance(stmts[0], IfStatement):
            elif_stmt = stmts[0]
            cond = self._convert_expr(elif_stmt.condition)
            lines = [f"{prefix}elif {cond}:"]
            body = self._convert_block(elif_stmt.consequence, indent + 1)
            lines.append(body if body else f"{INDENT * (indent + 1)}pass")
            if elif_stmt.alternative is not None:
                lines.append(self._convert_else_chain(elif_stmt.alternative, indent))
            return "\n".join(lines)
        else:
            lines = [f"{prefix}else:"]
            body = self._convert_block(block, indent + 1)
            lines.append(body if body else f"{INDENT * (indent + 1)}pass")
            return "\n".join(lines)


    def _convert_choose(self, stmt: ChooseStatement, indent: int) -> str:
        """Convert choose/choice/default to Python if/elif/else."""
        prefix = INDENT * indent
        lines: list[str] = []

        # Special case: "choose true" uses choices as direct conditions
        is_choose_true = (
            isinstance(stmt.value, BooleanLiteral) and stmt.value.value is True
        ) or (
            isinstance(stmt.value, Identifier) and stmt.value.value == "true"
        )

        for i, choice in enumerate(stmt.choices):
            keyword = "if" if i == 0 else "elif"
            choice_val = self._convert_expr(choice.value)
            if is_choose_true:
                # choose true: each choice is a direct condition
                lines.append(f"{prefix}{keyword} {choice_val}:")
            else:
                val_expr = self._convert_expr(stmt.value)
                lines.append(f"{prefix}{keyword} {val_expr} == {choice_val}:")
            body = self._convert_block(choice.body, indent + 1)
            lines.append(body if body else f"{INDENT * (indent + 1)}pass")

        if stmt.default is not None:
            lines.append(f"{prefix}else:")
            body = self._convert_block(stmt.default, indent + 1)
            lines.append(body if body else f"{INDENT * (indent + 1)}pass")

        return "\n".join(lines)

    def _convert_loop(self, stmt: LoopStatement, indent: int) -> str:
        """Convert loop statement to Python for/while."""
        prefix = INDENT * indent
        lines: list[str] = []

        if stmt.iterable is not None and stmt.variable:
            # Iteration: loop item in collection -> for item in collection:
            var = stmt.variable
            iterable = self._convert_expr(stmt.iterable)
            lines.append(f"{prefix}for {var} in {iterable}:")
        elif stmt.start is not None and stmt.end is not None and stmt.variable:
            # Counting: loop i from a to b [step s]
            # PLAIN ranges are inclusive, Python range is exclusive
            var = stmt.variable
            start = self._convert_expr(stmt.start)
            end = self._convert_expr(stmt.end)
            if stmt.step is not None:
                step = self._convert_expr(stmt.step)
                lines.append(f"{prefix}for {var} in range({start}, {end} + 1, {step}):")
            else:
                lines.append(f"{prefix}for {var} in range({start}, {end} + 1):")
        elif stmt.condition is not None:
            # While-style: loop condition -> while condition:
            cond = self._convert_expr(stmt.condition)
            lines.append(f"{prefix}while {cond}:")
        else:
            # Infinite loop fallback
            lines.append(f"{prefix}while True:")

        body = self._convert_block(stmt.body, indent + 1)
        lines.append(body if body else f"{INDENT * (indent + 1)}pass")
        return "\n".join(lines)

    def _convert_attempt(self, stmt: AttemptStatement, indent: int) -> str:
        """Convert attempt/handle/ensure to try/except/finally."""
        prefix = INDENT * indent
        lines = [f"{prefix}try:"]
        body = self._convert_block(stmt.body, indent + 1)
        lines.append(body if body else f"{INDENT * (indent + 1)}pass")

        for handler in stmt.handlers:
            if handler.error_name:
                lines.append(f"{prefix}except Exception as {handler.error_name}:")
            else:
                lines.append(f"{prefix}except Exception:")
            hbody = self._convert_block(handler.body, indent + 1)
            lines.append(hbody if hbody else f"{INDENT * (indent + 1)}pass")

        if stmt.ensure is not None:
            lines.append(f"{prefix}finally:")
            ebody = self._convert_block(stmt.ensure, indent + 1)
            lines.append(ebody if ebody else f"{INDENT * (indent + 1)}pass")

        return "\n".join(lines)

    def _convert_record(self, stmt: RecordStatement, indent: int) -> str:
        """Convert record to Python dataclass."""
        prefix = INDENT * indent
        self._imports.add("dataclasses")
        lines = [f"{prefix}@dataclasses.dataclass"]

        # Handle inheritance (record names stay PascalCase — they're class names)
        if stmt.based_on:
            bases = ", ".join(stmt.based_on)
            lines.append(f"{prefix}class {stmt.name}({bases}):")
        else:
            lines.append(f"{prefix}class {stmt.name}:")

        if not stmt.fields:
            lines.append(f"{INDENT * (indent + 1)}pass")
        else:
            for fld in stmt.fields:
                py_type = self._plain_type_to_python(fld.type_name) if fld.type_name else "any"
                if fld.default_value is not None:
                    default = self._convert_expr(fld.default_value)
                    lines.append(f"{INDENT * (indent + 1)}{fld.name}: {py_type} = {default}")
                else:
                    lines.append(f"{INDENT * (indent + 1)}{fld.name}: {py_type}")

        return "\n".join(lines)

    def _convert_block(self, block: BlockStatement | None, indent: int) -> str:
        """Convert a block of statements to Python code."""
        if block is None or not block.statements:
            return ""
        converted: list[str] = []
        for stmt in block.statements:
            line = self._convert_statement(stmt, indent)
            if line:
                converted.append(line)
        return "\n".join(converted)

    # ---- Expression Conversion ----

    def _convert_expr(self, expr: Expression | None) -> str:
        """Convert a PLAIN expression to Python."""
        if expr is None:
            return ""

        if isinstance(expr, Identifier):
            return self._convert_identifier(expr)
        if isinstance(expr, IntegerLiteral):
            return str(expr.value)
        if isinstance(expr, FloatLiteral):
            return str(expr.value)
        if isinstance(expr, StringLiteral):
            return self._convert_string(expr)
        if isinstance(expr, InterpolatedString):
            return self._convert_interpolated_string(expr)
        if isinstance(expr, BooleanLiteral):
            return "True" if expr.value else "False"
        if isinstance(expr, NullLiteral):
            return "None"
        if isinstance(expr, ListLiteral):
            elements = ", ".join(self._convert_expr(e) for e in expr.elements)
            return f"[{elements}]"
        if isinstance(expr, TableLiteral):
            pairs = ", ".join(
                f"{self._convert_expr(k)}: {self._convert_expr(v)}"
                for k, v in expr.pairs
            )
            return "{" + pairs + "}"
        if isinstance(expr, PrefixExpression):
            return self._convert_prefix(expr)
        if isinstance(expr, InfixExpression):
            return self._convert_infix(expr)
        if isinstance(expr, CallExpression):
            return self._convert_call(expr)
        if isinstance(expr, IndexExpression):
            left = self._convert_expr(expr.left)
            idx = self._convert_expr(expr.index)
            return f"{left}[{idx}]"
        if isinstance(expr, DotExpression):
            left = self._convert_expr(expr.left)
            return f"{left}.{expr.right}"

        self.result.add_warning(
            WarningCategory.UNSUPPORTED_FEATURE,
            f"Unknown expression type: {type(expr).__name__}"
        )
        return str(expr)

    def _convert_identifier(self, expr: Identifier) -> str:
        """Convert PLAIN identifier to Python."""
        name = expr.value
        # Map PLAIN boolean/null literals that might be identifiers
        if name == "true":
            return "True"
        if name == "false":
            return "False"
        if name == "null":
            return "None"
        return name

    def _convert_string(self, expr: StringLiteral) -> str:
        """Convert a PLAIN string literal to Python string."""
        # Escape any backslashes and quotes in the value
        val = expr.value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{val}"'

    def _convert_interpolated_string(self, expr: InterpolatedString) -> str:
        """Convert v-string to Python f-string."""
        # v"Hello {name}" -> f"Hello {name}"
        val = expr.value.replace("\\", "\\\\").replace('"', '\\"')
        return f'f"{val}"'

    def _convert_prefix(self, expr: PrefixExpression) -> str:
        """Convert prefix expression to Python."""
        right = self._convert_expr(expr.right)
        op = expr.operator
        if op == "not":
            return f"not {right}"
        if op == "-":
            return f"-{right}"
        return f"{op}{right}"

    def _convert_infix(self, expr: InfixExpression) -> str:
        """Convert infix expression to Python."""
        left = self._convert_expr(expr.left)
        right = self._convert_expr(expr.right)
        op = expr.operator

        # Map PLAIN operators to Python
        op_map = {
            "&": "+",       # String concatenation
            "and": "and",
            "or": "or",
            "=": "==",      # Equality comparison
            "!=": "!=",
            "<": "<",
            ">": ">",
            "<=": "<=",
            ">=": ">=",
            "+": "+",
            "-": "-",
            "*": "*",
            "/": "/",
            "%": "%",
            "^": "**",      # Exponentiation in PLAIN
        }
        py_op = op_map.get(op, op)
        return f"{left} {py_op} {right}"

    def _convert_call(self, expr: CallExpression) -> str:
        """Convert a PLAIN function call to Python, applying stdlib mapping."""
        # Get function name
        func_name = ""
        if isinstance(expr.function, Identifier):
            func_name = expr.function.value
        elif isinstance(expr.function, DotExpression):
            # method call: obj.method(args)
            left = self._convert_expr(expr.function.left)
            method = expr.function.right
            # If calling on a known module, convert task name to snake_case
            if isinstance(expr.function.left, Identifier) and expr.function.left.value in self._user_modules:
                method = to_snake_case(method)
            args = ", ".join(self._convert_expr(a) for a in expr.arguments)
            return f"{left}.{method}({args})"
        else:
            # dynamic call
            fn = self._convert_expr(expr.function)
            args = ", ".join(self._convert_expr(a) for a in expr.arguments)
            return f"{fn}({args})"

        # Check stdlib mapping
        if func_name in self._stdlib_flat:
            mapping = self._stdlib_flat[func_name]
            call_style = mapping.get("call_style", "function")
            import_req = mapping.get("import_required")
            if import_req:
                self._imports.add(import_req)

            converted_args = [self._convert_expr(a) for a in expr.arguments]

            if call_style == "function":
                py_name = mapping["python_name"]
                args_str = ", ".join(converted_args)
                return f"{py_name}({args_str})"

            elif call_style == "special":
                template = mapping.get("python_template", "")
                if template and converted_args:
                    return template.format(*converted_args)
                elif mapping.get("python_name"):
                    args_str = ", ".join(converted_args)
                    return f"{mapping['python_name']}({args_str})"
                return f"{func_name}({', '.join(converted_args)})"

            elif call_style == "method_from_function":
                arg_transform = mapping.get("arg_transform", "")
                py_method = mapping["python_name"]
                if arg_transform == "first_arg_becomes_object" and converted_args:
                    obj = converted_args[0]
                    rest = ", ".join(converted_args[1:])
                    return f"{obj}.{py_method}({rest})"
                elif arg_transform == "swap_and_first_becomes_object" and len(converted_args) >= 2:
                    # join(lst, sep) -> sep.join(lst)
                    obj = converted_args[1]
                    rest = converted_args[0]
                    return f"{obj}.{py_method}({rest})"
                else:
                    args_str = ", ".join(converted_args)
                    return f"{py_method}({args_str})"

        # Not a stdlib function - convert as regular call
        # Convert PascalCase task names to snake_case function names
        py_name = plain_task_to_python_func(func_name)
        args = ", ".join(self._convert_expr(a) for a in expr.arguments)
        return f"{py_name}({args})"