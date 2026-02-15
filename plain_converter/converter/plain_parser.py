"""
PLAIN language parser for the converter.

Provides a tokenizer, AST node classes, and a recursive descent parser
for PLAIN source code. This is a Python reimplementation tailored for
the converter (not the full interpreter).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any
import re


# ============================================================================
# TOKEN TYPES
# ============================================================================

class TokenType(Enum):
    """Token types for the PLAIN lexer."""
    # Special
    ILLEGAL = auto()
    EOF = auto()
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()

    # Literals
    IDENT = auto()
    INT = auto()
    FLOAT = auto()
    STRING = auto()
    VSTRING = auto()

    # Keywords - Task
    TASK = auto()
    WITH = auto()
    USING = auto()
    DELIVER = auto()
    ABORT = auto()
    SWAP = auto()

    # Keywords - Variables
    VAR = auto()
    FXD = auto()
    AS = auto()

    # Keywords - Control flow
    IF = auto()
    THEN = auto()
    ELSE = auto()
    CHOOSE = auto()
    CHOICE = auto()
    DEFAULT = auto()
    LOOP = auto()
    FROM = auto()
    TO = auto()
    STEP = auto()
    IN = auto()
    EXIT = auto()
    CONTINUE = auto()

    # Keywords - Error handling
    ATTEMPT = auto()
    HANDLE = auto()
    ENSURE = auto()

    # Keywords - Records
    RECORD = auto()
    BASED = auto()
    ON = auto()

    # Keywords - Types
    INTEGER = auto()
    FLOAT_TYPE = auto()
    STRING_TYPE = auto()
    BOOLEAN = auto()
    LIST = auto()
    TABLE = auto()
    OF = auto()

    # Keywords - Literals
    TRUE = auto()
    FALSE = auto()
    NULL = auto()

    # Keywords - Logical
    AND = auto()
    OR = auto()
    NOT = auto()

    # Keywords - Comments
    REM = auto()
    NOTE = auto()

    # Keywords - Modules
    USE = auto()
    ASSEMBLIES = auto()
    MODULES = auto()
    TASKS = auto()

    # Operators
    PLUS = auto()
    MINUS = auto()
    ASTERISK = auto()
    SLASH = auto()
    MODULO = auto()
    AMPERSAND = auto()  # string concat

    # Comparison
    EQ = auto()       # ==
    NOT_EQ = auto()   # !=
    LT = auto()       # <
    GT = auto()       # >
    LT_EQ = auto()    # <=
    GT_EQ = auto()    # >=

    # Assignment
    ASSIGN = auto()   # =

    # Delimiters
    LPAREN = auto()   # (
    RPAREN = auto()   # )
    LBRACKET = auto() # [
    RBRACKET = auto() # ]
    LBRACE = auto()   # {
    RBRACE = auto()   # }
    COMMA = auto()    # ,
    DOT = auto()      # .
    COLON = auto()    # :


# Keyword map
KEYWORDS = {
    "task": TokenType.TASK, "with": TokenType.WITH, "using": TokenType.USING,
    "deliver": TokenType.DELIVER, "abort": TokenType.ABORT, "swap": TokenType.SWAP,
    "var": TokenType.VAR, "fxd": TokenType.FXD, "as": TokenType.AS,
    "if": TokenType.IF, "then": TokenType.THEN, "else": TokenType.ELSE,
    "choose": TokenType.CHOOSE, "choice": TokenType.CHOICE,
    "default": TokenType.DEFAULT,
    "loop": TokenType.LOOP, "from": TokenType.FROM, "to": TokenType.TO,
    "step": TokenType.STEP, "in": TokenType.IN,
    "exit": TokenType.EXIT, "continue": TokenType.CONTINUE,
    "attempt": TokenType.ATTEMPT, "handle": TokenType.HANDLE,
    "ensure": TokenType.ENSURE,
    "record": TokenType.RECORD, "based": TokenType.BASED, "on": TokenType.ON,
    "integer": TokenType.INTEGER, "int": TokenType.INTEGER,
    "float": TokenType.FLOAT_TYPE, "flt": TokenType.FLOAT_TYPE,
    "string": TokenType.STRING_TYPE, "str": TokenType.STRING_TYPE,
    "boolean": TokenType.BOOLEAN, "bln": TokenType.BOOLEAN,
    "list": TokenType.LIST, "lst": TokenType.LIST,
    "table": TokenType.TABLE, "tbl": TokenType.TABLE, "of": TokenType.OF,
    "true": TokenType.TRUE, "false": TokenType.FALSE, "null": TokenType.NULL,
    "and": TokenType.AND, "or": TokenType.OR, "not": TokenType.NOT,
    "use": TokenType.USE, "assemblies": TokenType.ASSEMBLIES,
    "modules": TokenType.MODULES, "tasks": TokenType.TASKS,
}


# ============================================================================
# TOKEN
# ============================================================================

@dataclass
class Token:
    """A single token from the PLAIN lexer."""
    type: TokenType
    literal: str
    line: int = 0
    column: int = 0


# ============================================================================
# AST NODES
# ============================================================================

@dataclass
class Node:
    """Base AST node."""
    pass

@dataclass
class Expression(Node):
    """Base class for expression nodes."""
    pass

@dataclass
class Statement(Node):
    """Base class for statement nodes."""
    pass

@dataclass
class Program(Node):
    """Root AST node containing all statements."""
    statements: list[Statement] = field(default_factory=list)

# --- Expressions ---

@dataclass
class Identifier(Expression):
    value: str

@dataclass
class IntegerLiteral(Expression):
    value: int

@dataclass
class FloatLiteral(Expression):
    value: float

@dataclass
class StringLiteral(Expression):
    value: str

@dataclass
class InterpolatedString(Expression):
    value: str  # raw content with {expressions}

@dataclass
class BooleanLiteral(Expression):
    value: bool

@dataclass
class NullLiteral(Expression):
    pass

@dataclass
class ListLiteral(Expression):
    elements: list[Expression] = field(default_factory=list)

@dataclass
class TableLiteral(Expression):
    pairs: list[tuple[Expression, Expression]] = field(default_factory=list)

@dataclass
class PrefixExpression(Expression):
    operator: str
    right: Expression | None = None

@dataclass
class InfixExpression(Expression):
    left: Expression | None = None
    operator: str = ""
    right: Expression | None = None

@dataclass
class CallExpression(Expression):
    function: Expression | None = None
    arguments: list[Expression] = field(default_factory=list)

@dataclass
class IndexExpression(Expression):
    left: Expression | None = None
    index: Expression | None = None

@dataclass
class DotExpression(Expression):
    left: Expression | None = None
    right: str = ""

# --- Statements ---

@dataclass
class VarStatement(Statement):
    name: str = ""
    type_name: str | None = None
    value: Expression | None = None

@dataclass
class FxdStatement(Statement):
    name: str = ""
    type_name: str | None = None
    value: Expression | None = None

@dataclass
class AssignStatement(Statement):
    name: Expression | None = None  # can be identifier or index expr
    value: Expression | None = None

@dataclass
class ExpressionStatement(Statement):
    expression: Expression | None = None

@dataclass
class DeliverStatement(Statement):
    return_value: Expression | None = None

@dataclass
class AbortStatement(Statement):
    message: Expression | None = None

@dataclass
class SwapStatement(Statement):
    left: Expression | None = None
    right: Expression | None = None

@dataclass
class ExitStatement(Statement):
    pass

@dataclass
class ContinueStatement(Statement):
    pass

@dataclass
class CommentStatement(Statement):
    text: str = ""
    is_block: bool = False

@dataclass
class BlockStatement(Node):
    statements: list[Statement] = field(default_factory=list)

# --- Control Flow ---

@dataclass
class IfStatement(Statement):
    condition: Expression | None = None
    consequence: BlockStatement | None = None
    alternative: BlockStatement | None = None  # else block or nested if

@dataclass
class ChoiceClause(Node):
    value: Expression | None = None
    body: BlockStatement | None = None

@dataclass
class ChooseStatement(Statement):
    value: Expression | None = None
    choices: list[ChoiceClause] = field(default_factory=list)
    default: BlockStatement | None = None

@dataclass
class LoopStatement(Statement):
    condition: Expression | None = None   # while-style
    variable: str | None = None           # counting/iteration
    start: Expression | None = None       # counting: from
    end: Expression | None = None         # counting: to
    step: Expression | None = None        # counting: step
    iterable: Expression | None = None    # iteration: in
    body: BlockStatement | None = None

# --- Task/Function ---

@dataclass
class TaskStatement(Statement):
    name: str = ""
    parameters: list[tuple[str, str | None]] = field(default_factory=list)
    is_function: bool = False  # True if 'using', False if 'with' or no params
    body: BlockStatement | None = None

# --- Error Handling ---

@dataclass
class HandleClause(Node):
    pattern: Expression | None = None
    error_name: str | None = None
    body: BlockStatement | None = None

@dataclass
class AttemptStatement(Statement):
    body: BlockStatement | None = None
    handlers: list[HandleClause] = field(default_factory=list)
    ensure: BlockStatement | None = None

# --- Records ---

@dataclass
class RecordField(Node):
    name: str = ""
    type_name: str = ""
    default_value: Expression | None = None

@dataclass
class RecordStatement(Statement):
    name: str = ""
    fields: list[RecordField] = field(default_factory=list)
    based_on: list[str] = field(default_factory=list)
    with_records: list[str] = field(default_factory=list)

# --- Imports ---

@dataclass
class UseStatement(Statement):
    """Represents a use: block with assemblies, modules, and tasks sections."""
    assemblies: list[str] = field(default_factory=list)   # e.g. ["mathlib", "textlib"]
    modules: list[str] = field(default_factory=list)      # e.g. ["helpers", "mathlib.geometry"]
    tasks: list[str] = field(default_factory=list)        # e.g. ["mathlib.arithmetic.Add", "helpers.Greet"]


# ============================================================================
# LEXER
# ============================================================================

class Lexer:
    """Tokenizer for PLAIN source code."""

    def __init__(self, source: str):
        self.source = source
        self.lines = source.split("\n")
        self.tokens: list[Token] = []
        self.indent_stack: list[int] = [0]
        self._in_note_block = False
        self._note_indent = 0
        self._note_text = ""
        self._note_token: Token | None = None  # Reference to NOTE token for deferred literal update
        self._tokenize()

    def _tokenize(self) -> None:
        """Tokenize the entire source."""
        last_line = 1
        for line_num, raw_line in enumerate(self.lines, start=1):
            last_line = line_num

            # Skip completely empty lines
            if raw_line.strip() == "":
                continue

            # Handle note: block comments
            if self._in_note_block:
                stripped = raw_line.lstrip()
                indent = len(raw_line) - len(stripped)
                if indent <= self._note_indent and stripped and not stripped[0] == " ":
                    # Block ended — save accumulated text to the NOTE token
                    self._in_note_block = False
                    if self._note_token is not None:
                        self._note_token.literal = self._note_text.rstrip("\n")
                        self._note_token = None
                    # fall through to process this line normally
                else:
                    self._note_text += raw_line.strip() + "\n"
                    continue

            stripped = raw_line.lstrip()
            indent = len(raw_line) - len(stripped)

            # Handle rem: single-line comments
            if stripped.startswith("rem:"):
                self._emit_indentation(indent, line_num)
                comment_text = stripped[4:].strip()
                self.tokens.append(Token(TokenType.REM, comment_text, line_num, indent))
                self.tokens.append(Token(TokenType.NEWLINE, "\\n", line_num, 0))
                continue

            # Handle note: multi-line comments start
            if stripped.startswith("note:"):
                self._emit_indentation(indent, line_num)
                self._in_note_block = True
                self._note_indent = indent
                self._note_text = stripped[5:].strip() + "\n"
                note_token = Token(TokenType.NOTE, "", line_num, indent)
                self._note_token = note_token
                self.tokens.append(note_token)
                self.tokens.append(Token(TokenType.NEWLINE, "\\n", line_num, 0))
                continue

            # Emit indentation changes
            self._emit_indentation(indent, line_num)

            # Tokenize the line content
            self._tokenize_line(stripped, line_num, indent)
            self.tokens.append(Token(TokenType.NEWLINE, "\\n", line_num, 0))

        # Flush any open note: block at EOF
        if self._in_note_block and self._note_token is not None:
            self._note_token.literal = self._note_text.rstrip("\n")
            self._in_note_block = False
            self._note_token = None

        # Close any remaining indentation
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(Token(TokenType.DEDENT, "", last_line, 0))

        self.tokens.append(Token(TokenType.EOF, "", last_line, 0))

    def _emit_indentation(self, indent: int, line_num: int) -> None:
        """Emit INDENT/DEDENT tokens based on indentation change."""
        current = self.indent_stack[-1]
        if indent > current:
            self.indent_stack.append(indent)
            self.tokens.append(Token(TokenType.INDENT, "", line_num, 0))
        elif indent < current:
            while len(self.indent_stack) > 1 and self.indent_stack[-1] > indent:
                self.indent_stack.pop()
                self.tokens.append(Token(TokenType.DEDENT, "", line_num, 0))

    def _tokenize_line(self, line: str, line_num: int, base_col: int) -> None:
        """Tokenize a single line of PLAIN code."""
        i = 0
        while i < len(line):
            ch = line[i]

            # Skip whitespace
            if ch == " " or ch == "\t":
                i += 1
                continue

            col = base_col + i

            # String literals
            if ch == '"':
                i = self._read_string(line, i, line_num, col)
                continue
            if ch == 'v' and i + 1 < len(line) and line[i + 1] == '"':
                i = self._read_vstring(line, i, line_num, col)
                continue

            # Numbers
            if ch.isdigit():
                i = self._read_number(line, i, line_num, col)
                continue

            # Negative number after operator (handled by parser as prefix expr)
            # Identifiers and keywords
            if ch.isalpha() or ch == '_':
                i = self._read_identifier(line, i, line_num, col)
                continue

            # Two-character operators
            if i + 1 < len(line):
                two = line[i:i+2]
                if two == "==":
                    self.tokens.append(Token(TokenType.EQ, "==", line_num, col))
                    i += 2
                    continue
                if two == "!=":
                    self.tokens.append(Token(TokenType.NOT_EQ, "!=", line_num, col))
                    i += 2
                    continue
                if two == "<=":
                    self.tokens.append(Token(TokenType.LT_EQ, "<=", line_num, col))
                    i += 2
                    continue
                if two == ">=":
                    self.tokens.append(Token(TokenType.GT_EQ, ">=", line_num, col))
                    i += 2
                    continue

            # Single-character tokens
            tok_map = {
                "+": TokenType.PLUS, "-": TokenType.MINUS,
                "*": TokenType.ASTERISK, "/": TokenType.SLASH,
                "%": TokenType.MODULO, "&": TokenType.AMPERSAND,
                "<": TokenType.LT, ">": TokenType.GT,
                "=": TokenType.ASSIGN,
                "(": TokenType.LPAREN, ")": TokenType.RPAREN,
                "[": TokenType.LBRACKET, "]": TokenType.RBRACKET,
                "{": TokenType.LBRACE, "}": TokenType.RBRACE,
                ",": TokenType.COMMA, ".": TokenType.DOT,
                ":": TokenType.COLON,
            }
            if ch in tok_map:
                self.tokens.append(Token(tok_map[ch], ch, line_num, col))
                i += 1
                continue

            # Unknown character
            self.tokens.append(Token(TokenType.ILLEGAL, ch, line_num, col))
            i += 1


    def _read_string(self, line: str, start: int, line_num: int, col: int) -> int:
        """Read a regular string literal."""
        i = start + 1  # skip opening quote
        result = []
        while i < len(line) and line[i] != '"':
            if line[i] == '\\' and i + 1 < len(line):
                result.append(line[i:i+2])
                i += 2
            else:
                result.append(line[i])
                i += 1
        if i < len(line):
            i += 1  # skip closing quote
        self.tokens.append(Token(TokenType.STRING, "".join(result), line_num, col))
        return i

    def _read_vstring(self, line: str, start: int, line_num: int, col: int) -> int:
        """Read an interpolated v-string literal."""
        i = start + 2  # skip 'v"'
        result = []
        while i < len(line) and line[i] != '"':
            if line[i] == '\\' and i + 1 < len(line):
                result.append(line[i:i+2])
                i += 2
            else:
                result.append(line[i])
                i += 1
        if i < len(line):
            i += 1  # skip closing quote
        self.tokens.append(Token(TokenType.VSTRING, "".join(result), line_num, col))
        return i

    def _read_number(self, line: str, start: int, line_num: int, col: int) -> int:
        """Read a number (integer or float)."""
        i = start
        is_float = False
        while i < len(line) and (line[i].isdigit() or line[i] == '.'):
            if line[i] == '.':
                if is_float:
                    break  # second dot - stop
                is_float = True
            i += 1
        literal = line[start:i]
        if is_float:
            self.tokens.append(Token(TokenType.FLOAT, literal, line_num, col))
        else:
            self.tokens.append(Token(TokenType.INT, literal, line_num, col))
        return i

    def _read_identifier(self, line: str, start: int, line_num: int, col: int) -> int:
        """Read an identifier or keyword."""
        i = start
        while i < len(line) and (line[i].isalnum() or line[i] == '_'):
            i += 1
        literal = line[start:i]
        # Check if it's a keyword
        lower = literal.lower()
        if lower in KEYWORDS:
            tok_type = KEYWORDS[lower]
        else:
            tok_type = TokenType.IDENT
        self.tokens.append(Token(tok_type, literal, line_num, col))
        return i


# ============================================================================
# PARSER
# ============================================================================

# Operator precedence levels
class Precedence(Enum):
    LOWEST = 1
    OR = 2
    AND = 3
    NOT = 4
    EQUALS = 5       # ==, !=
    LESSGREATER = 6  # <, >, <=, >=
    SUM = 7          # +, -, &
    PRODUCT = 8      # *, /, %
    PREFIX = 9       # -x, not x
    CALL = 10        # func(x)
    INDEX = 11       # arr[i]
    DOT = 12         # obj.field

PRECEDENCES: dict[TokenType, int] = {
    TokenType.OR: Precedence.OR.value,
    TokenType.AND: Precedence.AND.value,
    TokenType.EQ: Precedence.EQUALS.value,
    TokenType.NOT_EQ: Precedence.EQUALS.value,
    TokenType.LT: Precedence.LESSGREATER.value,
    TokenType.GT: Precedence.LESSGREATER.value,
    TokenType.LT_EQ: Precedence.LESSGREATER.value,
    TokenType.GT_EQ: Precedence.LESSGREATER.value,
    TokenType.PLUS: Precedence.SUM.value,
    TokenType.MINUS: Precedence.SUM.value,
    TokenType.AMPERSAND: Precedence.SUM.value,
    TokenType.ASTERISK: Precedence.PRODUCT.value,
    TokenType.SLASH: Precedence.PRODUCT.value,
    TokenType.MODULO: Precedence.PRODUCT.value,
    TokenType.LPAREN: Precedence.CALL.value,
    TokenType.LBRACKET: Precedence.INDEX.value,
    TokenType.DOT: Precedence.DOT.value,
}


class Parser:
    """Recursive descent parser for PLAIN source code."""

    def __init__(self, source: str):
        self.lexer = Lexer(source)
        self.tokens = self.lexer.tokens
        self.pos = 0
        self.errors: list[str] = []
        self._eq_is_comparison = False  # when True, = is equality (not assignment)

    @property
    def cur(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token(TokenType.EOF, "", 0, 0)

    @property
    def peek(self) -> Token:
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return Token(TokenType.EOF, "", 0, 0)

    def advance(self) -> Token:
        tok = self.cur
        self.pos += 1
        return tok

    def expect(self, tok_type: TokenType) -> Token:
        if self.cur.type != tok_type:
            self.errors.append(
                f"Line {self.cur.line}: expected {tok_type.name}, got {self.cur.type.name} ('{self.cur.literal}')"
            )
        return self.advance()

    def skip_newlines(self) -> None:
        while self.cur.type == TokenType.NEWLINE:
            self.advance()

    def parse(self) -> Program:
        """Parse the token stream into an AST."""
        program = Program()
        self.skip_newlines()
        while self.cur.type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt is not None:
                program.statements.append(stmt)
            self.skip_newlines()
        return program

    # ---- Statement Parsing ----

    def parse_statement(self) -> Statement | None:
        """Parse a single statement based on the current token."""
        tt = self.cur.type

        if tt == TokenType.VAR:
            return self.parse_var_statement()
        if tt == TokenType.FXD:
            return self.parse_fxd_statement()
        if tt == TokenType.TASK:
            return self.parse_task_statement()
        if tt == TokenType.IF:
            return self.parse_if_statement()
        if tt == TokenType.CHOOSE:
            return self.parse_choose_statement()
        if tt == TokenType.LOOP:
            return self.parse_loop_statement()
        if tt == TokenType.ATTEMPT:
            return self.parse_attempt_statement()
        if tt == TokenType.DELIVER:
            return self.parse_deliver_statement()
        if tt == TokenType.ABORT:
            return self.parse_abort_statement()
        if tt == TokenType.EXIT:
            self.advance()
            self.skip_newlines()
            return ExitStatement()
        if tt == TokenType.CONTINUE:
            self.advance()
            self.skip_newlines()
            return ContinueStatement()
        if tt == TokenType.SWAP:
            return self.parse_swap_statement()
        if tt == TokenType.RECORD:
            return self.parse_record_statement()
        if tt == TokenType.USE:
            return self.parse_use_statement()
        if tt == TokenType.REM:
            text = self.cur.literal
            self.advance()
            self.skip_newlines()
            return CommentStatement(text=text)
        if tt == TokenType.NOTE:
            text = self.cur.literal
            self.advance()
            self.skip_newlines()
            return CommentStatement(text=text, is_block=True)
        if tt == TokenType.NEWLINE:
            self.advance()
            return None
        if tt == TokenType.DEDENT:
            return None

        # Could be assignment or expression statement
        return self.parse_expression_or_assignment()

    def parse_var_statement(self) -> VarStatement:
        """Parse: var name = expression"""
        self.advance()  # consume 'var'
        name = self.expect(TokenType.IDENT).literal
        type_name = None
        if self.cur.type == TokenType.AS:
            self.advance()
            type_name = self.cur.literal
            self.advance()
        value = None
        if self.cur.type == TokenType.ASSIGN:
            self.advance()
            value = self.parse_expression(Precedence.LOWEST.value)
        self.skip_newlines()
        return VarStatement(name=name, type_name=type_name, value=value)

    def parse_fxd_statement(self) -> FxdStatement:
        """Parse: fxd name = expression"""
        self.advance()  # consume 'fxd'
        name = self.expect(TokenType.IDENT).literal
        type_name = None
        if self.cur.type == TokenType.AS:
            self.advance()
            type_name = self.cur.literal
            self.advance()
        value = None
        if self.cur.type == TokenType.ASSIGN:
            self.advance()
            value = self.parse_expression(Precedence.LOWEST.value)
        self.skip_newlines()
        return FxdStatement(name=name, type_name=type_name, value=value)

    def parse_task_statement(self) -> TaskStatement:
        """Parse: task Name() / task Name with (params) / task Name using (params)"""
        self.advance()  # consume 'task'
        name = self.expect(TokenType.IDENT).literal
        params: list[str] = []
        is_function = False

        if self.cur.type == TokenType.USING:
            is_function = True
            self.advance()
            self.expect(TokenType.LPAREN)
            params = self._parse_param_list()
            self.expect(TokenType.RPAREN)
        elif self.cur.type == TokenType.WITH:
            is_function = False
            self.advance()
            self.expect(TokenType.LPAREN)
            params = self._parse_param_list()
            self.expect(TokenType.RPAREN)
        elif self.cur.type == TokenType.LPAREN:
            self.advance()
            if self.cur.type != TokenType.RPAREN:
                params = self._parse_param_list()
            self.expect(TokenType.RPAREN)

        self.skip_newlines()
        body = self.parse_block()
        return TaskStatement(name=name, parameters=params,
                             is_function=is_function, body=body)

    def _parse_param_list(self) -> list[tuple[str, str | None]]:
        """Parse a comma-separated parameter list with optional type annotations.

        Supports: name, name as type, name as type, name
        Returns list of (name, type_name) tuples.
        """
        params: list[tuple[str, str | None]] = []
        if self.cur.type == TokenType.IDENT:
            name = self.cur.literal
            self.advance()
            type_name = None
            if self.cur.type == TokenType.AS:
                self.advance()
                type_name = self.cur.literal
                self.advance()
            params.append((name, type_name))
        while self.cur.type == TokenType.COMMA:
            self.advance()
            if self.cur.type == TokenType.IDENT:
                name = self.cur.literal
                self.advance()
                type_name = None
                if self.cur.type == TokenType.AS:
                    self.advance()
                    type_name = self.cur.literal
                    self.advance()
                params.append((name, type_name))
        return params

    def parse_if_statement(self) -> IfStatement:
        """Parse: if condition [then] / body / else ..."""
        self.advance()  # consume 'if'
        old_eq = self._eq_is_comparison
        self._eq_is_comparison = True
        condition = self.parse_expression(Precedence.LOWEST.value)
        self._eq_is_comparison = old_eq
        # Consume optional 'then' keyword
        if self.cur.type == TokenType.THEN:
            self.advance()
        self.skip_newlines()
        consequence = self.parse_block()
        alternative = None
        if self.cur.type == TokenType.ELSE:
            self.advance()
            self.skip_newlines()
            if self.cur.type == TokenType.IF:
                # else if -> nested IfStatement in a BlockStatement
                nested = self.parse_if_statement()
                alternative = BlockStatement(statements=[nested])
            else:
                alternative = self.parse_block()
        return IfStatement(condition=condition, consequence=consequence,
                           alternative=alternative)

    def parse_choose_statement(self) -> ChooseStatement:
        """Parse: choose expr / choice val / ... / default ..."""
        self.advance()  # consume 'choose'
        value = self.parse_expression(Precedence.LOWEST.value)
        self.skip_newlines()
        if self.cur.type != TokenType.INDENT:
            return ChooseStatement(value=value)
        self.advance()  # consume INDENT
        self.skip_newlines()
        choices: list[ChoiceClause] = []
        default_block = None
        while self.cur.type not in (TokenType.DEDENT, TokenType.EOF):
            if self.cur.type == TokenType.CHOICE:
                self.advance()
                old_eq = self._eq_is_comparison
                self._eq_is_comparison = True
                choice_val = self.parse_expression(Precedence.LOWEST.value)
                self._eq_is_comparison = old_eq
                self.skip_newlines()
                body = self.parse_block()
                choices.append(ChoiceClause(value=choice_val, body=body))
            elif self.cur.type == TokenType.DEFAULT:
                self.advance()
                self.skip_newlines()
                default_block = self.parse_block()
            else:
                self.skip_newlines()
                if self.cur.type not in (TokenType.CHOICE, TokenType.DEFAULT,
                                          TokenType.DEDENT, TokenType.EOF):
                    self.advance()
        if self.cur.type == TokenType.DEDENT:
            self.advance()
        return ChooseStatement(value=value, choices=choices,
                               default=default_block)

    def parse_loop_statement(self) -> LoopStatement:
        """Parse various loop forms:
           loop condition            (while-loop)
           loop i from a to b        (counting)
           loop i from a to b step s (counting with step)
           loop item in collection   (iteration)
        """
        self.advance()  # consume 'loop'
        stmt = LoopStatement()

        # Check for counting/iteration loop: next token is IDENT
        if self.cur.type == TokenType.IDENT:
            var_name = self.cur.literal
            # Look ahead to see if it's 'from' or 'in'
            if self.peek.type == TokenType.FROM:
                # Counting loop: loop i from a to b [step s]
                stmt.variable = var_name
                self.advance()  # consume var name
                self.advance()  # consume 'from'
                stmt.start = self.parse_expression(Precedence.LOWEST.value)
                self.expect(TokenType.TO)
                stmt.end = self.parse_expression(Precedence.LOWEST.value)
                if self.cur.type == TokenType.STEP:
                    self.advance()
                    stmt.step = self.parse_expression(Precedence.LOWEST.value)
            elif self.peek.type == TokenType.IN:
                # Iteration loop: loop item in collection
                stmt.variable = var_name
                self.advance()  # consume var name
                self.advance()  # consume 'in'
                stmt.iterable = self.parse_expression(Precedence.LOWEST.value)
            else:
                # while-style with expression starting with identifier
                old_eq = self._eq_is_comparison
                self._eq_is_comparison = True
                stmt.condition = self.parse_expression(Precedence.LOWEST.value)
                self._eq_is_comparison = old_eq
        else:
            # while-style loop
            old_eq = self._eq_is_comparison
            self._eq_is_comparison = True
            stmt.condition = self.parse_expression(Precedence.LOWEST.value)
            self._eq_is_comparison = old_eq

        self.skip_newlines()
        stmt.body = self.parse_block()
        return stmt

    def parse_attempt_statement(self) -> AttemptStatement:
        """Parse: attempt / body / handle [error] / body / ensure / body"""
        self.advance()  # consume 'attempt'
        self.skip_newlines()
        body = self.parse_block()
        handlers: list[HandleClause] = []
        ensure_block = None

        while self.cur.type == TokenType.HANDLE:
            self.advance()
            error_name = None
            pattern = None
            if self.cur.type == TokenType.IDENT:
                error_name = self.cur.literal
                self.advance()
            self.skip_newlines()
            handler_body = self.parse_block()
            handlers.append(HandleClause(pattern=pattern,
                                          error_name=error_name,
                                          body=handler_body))

        if self.cur.type == TokenType.ENSURE:
            self.advance()
            self.skip_newlines()
            ensure_block = self.parse_block()

        return AttemptStatement(body=body, handlers=handlers,
                                ensure=ensure_block)

    def parse_deliver_statement(self) -> DeliverStatement:
        """Parse: deliver [expression]"""
        self.advance()  # consume 'deliver'
        value = None
        if self.cur.type not in (TokenType.NEWLINE, TokenType.EOF,
                                  TokenType.DEDENT):
            value = self.parse_expression(Precedence.LOWEST.value)
        self.skip_newlines()
        return DeliverStatement(return_value=value)

    def parse_abort_statement(self) -> AbortStatement:
        """Parse: abort [expression]"""
        self.advance()  # consume 'abort'
        msg = None
        if self.cur.type not in (TokenType.NEWLINE, TokenType.EOF,
                                  TokenType.DEDENT):
            msg = self.parse_expression(Precedence.LOWEST.value)
        self.skip_newlines()
        return AbortStatement(message=msg)

    def parse_swap_statement(self) -> SwapStatement:
        """Parse: swap a, b"""
        self.advance()  # consume 'swap'
        left = self.parse_expression(Precedence.LOWEST.value)
        self.expect(TokenType.COMMA)
        right = self.parse_expression(Precedence.LOWEST.value)
        self.skip_newlines()
        return SwapStatement(left=left, right=right)

    def parse_record_statement(self) -> RecordStatement:
        """Parse: record Name: / record Name based on Parent:"""
        self.advance()  # consume 'record'
        name = self.expect(TokenType.IDENT).literal
        stmt = RecordStatement(name=name)

        # Handle optional 'based on Parent'
        if self.cur.type == TokenType.BASED:
            self.advance()  # consume 'based'
            if self.cur.type == TokenType.ON:
                self.advance()  # consume 'on'
            if self.cur.type == TokenType.IDENT:
                stmt.based_on.append(self.cur.literal)
                self.advance()

        # Consume optional colon after record name / parent
        if self.cur.type == TokenType.COLON:
            self.advance()

        self.skip_newlines()

        if self.cur.type == TokenType.INDENT:
            self.advance()
            self.skip_newlines()
            while self.cur.type not in (TokenType.DEDENT, TokenType.EOF):
                if self.cur.type == TokenType.IDENT:
                    field_name = self.cur.literal
                    self.advance()
                    type_name = ""
                    if self.cur.type == TokenType.AS:
                        self.advance()
                        type_name = self.cur.literal
                        self.advance()
                    default_val = None
                    if self.cur.type == TokenType.ASSIGN:
                        self.advance()
                        default_val = self.parse_expression(Precedence.LOWEST.value)
                    stmt.fields.append(RecordField(name=field_name,
                                                    type_name=type_name,
                                                    default_value=default_val))
                else:
                    # Skip unexpected tokens to prevent infinite loop
                    self.advance()
                self.skip_newlines()
            if self.cur.type == TokenType.DEDENT:
                self.advance()
        return stmt

    def parse_use_statement(self) -> UseStatement:
        """Parse: use: / assemblies: / modules: / tasks: sections."""
        self.advance()  # consume 'use'
        # Consume optional colon
        if self.cur.type == TokenType.COLON:
            self.advance()
        self.skip_newlines()

        stmt = UseStatement()

        if self.cur.type != TokenType.INDENT:
            return stmt
        self.advance()  # consume INDENT
        self.skip_newlines()

        while self.cur.type not in (TokenType.DEDENT, TokenType.EOF):
            if self.cur.type == TokenType.ASSEMBLIES:
                self.advance()  # consume 'assemblies'
                if self.cur.type == TokenType.COLON:
                    self.advance()
                self.skip_newlines()
                if self.cur.type == TokenType.INDENT:
                    self.advance()
                    self.skip_newlines()
                    while self.cur.type not in (TokenType.DEDENT, TokenType.EOF):
                        if self.cur.type == TokenType.IDENT:
                            stmt.assemblies.append(self._parse_dotted_name())
                        else:
                            self.advance()
                        self.skip_newlines()
                    if self.cur.type == TokenType.DEDENT:
                        self.advance()

            elif self.cur.type == TokenType.MODULES:
                self.advance()  # consume 'modules'
                if self.cur.type == TokenType.COLON:
                    self.advance()
                self.skip_newlines()
                if self.cur.type == TokenType.INDENT:
                    self.advance()
                    self.skip_newlines()
                    while self.cur.type not in (TokenType.DEDENT, TokenType.EOF):
                        if self.cur.type == TokenType.IDENT:
                            stmt.modules.append(self._parse_dotted_name())
                        else:
                            self.advance()
                        self.skip_newlines()
                    if self.cur.type == TokenType.DEDENT:
                        self.advance()

            elif self.cur.type == TokenType.TASKS:
                self.advance()  # consume 'tasks'
                if self.cur.type == TokenType.COLON:
                    self.advance()
                self.skip_newlines()
                if self.cur.type == TokenType.INDENT:
                    self.advance()
                    self.skip_newlines()
                    while self.cur.type not in (TokenType.DEDENT, TokenType.EOF):
                        if self.cur.type == TokenType.IDENT:
                            stmt.tasks.append(self._parse_dotted_name())
                        else:
                            self.advance()
                        self.skip_newlines()
                    if self.cur.type == TokenType.DEDENT:
                        self.advance()
            else:
                self.advance()
            self.skip_newlines()

        if self.cur.type == TokenType.DEDENT:
            self.advance()
        return stmt

    def _parse_dotted_name(self) -> str:
        """Parse a dotted identifier like 'mathlib.geometry.Add'."""
        name = self.cur.literal
        self.advance()
        while self.cur.type == TokenType.DOT:
            self.advance()  # consume '.'
            if self.cur.type in (TokenType.IDENT, TokenType.EOF):
                name += "." + self.cur.literal
                self.advance()
            else:
                break
        return name

    def parse_block(self) -> BlockStatement:
        """Parse an indented block of statements."""
        block = BlockStatement()
        if self.cur.type != TokenType.INDENT:
            return block
        self.advance()  # consume INDENT
        self.skip_newlines()
        while self.cur.type not in (TokenType.DEDENT, TokenType.EOF):
            stmt = self.parse_statement()
            if stmt is not None:
                block.statements.append(stmt)
            self.skip_newlines()
        if self.cur.type == TokenType.DEDENT:
            self.advance()
        return block

    def parse_expression_or_assignment(self) -> Statement:
        """Parse an expression statement or assignment."""
        expr = self.parse_expression(Precedence.LOWEST.value)
        # Check for assignment: ident = expr or obj.field = expr or arr[i] = expr
        if self.cur.type == TokenType.ASSIGN:
            self.advance()
            value = self.parse_expression(Precedence.LOWEST.value)
            self.skip_newlines()
            return AssignStatement(name=expr, value=value)
        self.skip_newlines()
        return ExpressionStatement(expression=expr)

    # ---- Expression Parsing (Pratt parser) ----

    def parse_expression(self, precedence: int) -> Expression:
        """Parse an expression with the given precedence."""
        left = self.parse_prefix()
        if left is None:
            self.errors.append(
                f"Line {self.cur.line}: unexpected token {self.cur.type.name} ('{self.cur.literal}')"
            )
            self.advance()
            return Identifier(value="<error>")

        while (self.cur.type not in (TokenType.NEWLINE, TokenType.EOF,
                                      TokenType.DEDENT) and
               precedence < self._peek_precedence()):
            left = self.parse_infix(left)

        return left

    def _peek_precedence(self) -> int:
        if self._eq_is_comparison and self.cur.type == TokenType.ASSIGN:
            return Precedence.EQUALS.value
        return PRECEDENCES.get(self.cur.type, Precedence.LOWEST.value)

    def parse_prefix(self) -> Expression | None:
        """Parse a prefix expression or primary."""
        tt = self.cur.type

        if tt == TokenType.IDENT:
            ident = Identifier(value=self.cur.literal)
            self.advance()
            return ident

        if tt == TokenType.INT:
            val = int(self.cur.literal)
            self.advance()
            return IntegerLiteral(value=val)

        if tt == TokenType.FLOAT:
            val = float(self.cur.literal)
            self.advance()
            return FloatLiteral(value=val)

        if tt == TokenType.STRING:
            val = self.cur.literal
            self.advance()
            return StringLiteral(value=val)

        if tt == TokenType.VSTRING:
            val = self.cur.literal
            self.advance()
            return InterpolatedString(value=val)

        if tt == TokenType.TRUE:
            self.advance()
            return BooleanLiteral(value=True)

        if tt == TokenType.FALSE:
            self.advance()
            return BooleanLiteral(value=False)

        if tt == TokenType.NULL:
            self.advance()
            return NullLiteral()

        if tt == TokenType.MINUS:
            self.advance()
            right = self.parse_expression(Precedence.PREFIX.value)
            return PrefixExpression(operator="-", right=right)

        if tt == TokenType.NOT:
            self.advance()
            right = self.parse_expression(Precedence.NOT.value)
            return PrefixExpression(operator="not", right=right)

        if tt == TokenType.LPAREN:
            self.advance()  # consume '('
            expr = self.parse_expression(Precedence.LOWEST.value)
            self.expect(TokenType.RPAREN)
            return expr

        if tt == TokenType.LBRACKET:
            return self.parse_list_literal()

        if tt == TokenType.LBRACE:
            return self.parse_table_literal()

        return None

    def parse_infix(self, left: Expression) -> Expression:
        """Parse an infix expression (binary op, call, index, dot)."""
        tt = self.cur.type

        if tt == TokenType.LPAREN:
            # Function call
            self.advance()  # consume '('
            args = self._parse_expression_list(TokenType.RPAREN)
            self.expect(TokenType.RPAREN)
            return CallExpression(function=left, arguments=args)

        if tt == TokenType.LBRACKET:
            # Index expression
            self.advance()  # consume '['
            index = self.parse_expression(Precedence.LOWEST.value)
            self.expect(TokenType.RBRACKET)
            return IndexExpression(left=left, index=index)

        if tt == TokenType.DOT:
            # Dot access
            self.advance()  # consume '.'
            field_name = self.expect(TokenType.IDENT).literal
            return DotExpression(left=left, right=field_name)

        # Binary operators
        prec = self._peek_precedence()
        op = self.cur.literal
        # Map keyword operators to their string representation
        if tt == TokenType.AND:
            op = "and"
        elif tt == TokenType.OR:
            op = "or"
        self.advance()
        right = self.parse_expression(prec)
        return InfixExpression(left=left, operator=op, right=right)

    def _parse_expression_list(self, end: TokenType) -> list[Expression]:
        """Parse a comma-separated list of expressions."""
        args: list[Expression] = []
        if self.cur.type == end:
            return args
        args.append(self.parse_expression(Precedence.LOWEST.value))
        while self.cur.type == TokenType.COMMA:
            self.advance()
            args.append(self.parse_expression(Precedence.LOWEST.value))
        return args

    def parse_list_literal(self) -> ListLiteral:
        """Parse: [expr, expr, ...]"""
        self.advance()  # consume '['
        elements = self._parse_expression_list(TokenType.RBRACKET)
        self.expect(TokenType.RBRACKET)
        return ListLiteral(elements=elements)

    def parse_table_literal(self) -> TableLiteral:
        """Parse: {key: value, key: value, ...}"""
        self.advance()  # consume '{'
        pairs: list[tuple[Expression, Expression]] = []
        while self.cur.type != TokenType.RBRACE and self.cur.type != TokenType.EOF:
            key = self.parse_expression(Precedence.LOWEST.value)
            self.expect(TokenType.COLON)
            value = self.parse_expression(Precedence.LOWEST.value)
            pairs.append((key, value))
            if self.cur.type == TokenType.COMMA:
                self.advance()
        self.expect(TokenType.RBRACE)
        return TableLiteral(pairs=pairs)


def parse_plain(source: str) -> tuple[Program, list[str]]:
    """Convenience function to parse PLAIN source code.

    Returns:
        (program, errors) tuple
    """
    parser = Parser(source)
    program = parser.parse()
    return program, parser.errors