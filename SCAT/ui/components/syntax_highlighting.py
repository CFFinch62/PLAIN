"""
Modular syntax highlighting system for SCAT (Source Code Analysis Tool).

This module provides a flexible, extensible syntax highlighting system that
supports multiple programming languages through a factory pattern.
"""

from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
import re
from typing import Dict, List, Optional


class BaseSyntaxHighlighter(QSyntaxHighlighter):
    """
    Base class for syntax highlighters.

    This class defines the common interface and shared functionality
    for all language-specific syntax highlighters.
    """

    def __init__(self, document):
        super().__init__(document)
        self.highlighting_rules = []
        self._setup_highlighting_rules()

    def _setup_highlighting_rules(self):
        """Setup language-specific highlighting rules. Override in subclasses."""
        pass

    def highlightBlock(self, text):
        """Apply syntax highlighting to a block of text."""
        for pattern, format_obj in self.highlighting_rules:
            for match in pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, format_obj)

    def _create_format(self, color: str, bold: bool = False, italic: bool = False) -> QTextCharFormat:
        """Create a text format with specified properties."""
        format_obj = QTextCharFormat()
        format_obj.setForeground(QColor(color))
        if bold:
            format_obj.setFontWeight(QFont.Weight.Bold)
        if italic:
            format_obj.setFontItalic(True)
        return format_obj

    def _add_keyword_rules(self, keywords: List[str], format_obj: QTextCharFormat):
        """Add highlighting rules for keywords."""
        for keyword in keywords:
            pattern = rf'\b{re.escape(keyword)}\b'
            self.highlighting_rules.append((re.compile(pattern), format_obj))

    def _add_pattern_rule(self, pattern: str, format_obj: QTextCharFormat):
        """Add a single pattern highlighting rule."""
        self.highlighting_rules.append((re.compile(pattern), format_obj))


class PythonSyntaxHighlighter(BaseSyntaxHighlighter):
    """Python syntax highlighter."""

    def _setup_highlighting_rules(self):
        """Setup Python-specific highlighting rules."""
        # Keywords
        keyword_format = self._create_format("#569CD6", bold=True)  # Blue
        keywords = [
            'and', 'as', 'assert', 'break', 'class', 'continue', 'def',
            'del', 'elif', 'else', 'except', 'exec', 'finally', 'for',
            'from', 'global', 'if', 'import', 'in', 'is', 'lambda',
            'not', 'or', 'pass', 'print', 'raise', 'return', 'try',
            'while', 'with', 'yield', 'async', 'await', 'nonlocal'
        ]
        self._add_keyword_rules(keywords, keyword_format)

        # Built-in functions
        builtin_format = self._create_format("#DCDCAA")  # Yellow
        builtins = [
            'abs', 'all', 'any', 'bin', 'bool', 'chr', 'dict', 'dir',
            'enumerate', 'filter', 'float', 'int', 'len', 'list', 'map',
            'max', 'min', 'range', 'set', 'sorted', 'str', 'sum', 'tuple',
            'type', 'zip', 'open', 'print', 'input', 'isinstance', 'hasattr'
        ]
        self._add_keyword_rules(builtins, builtin_format)

        # Constants
        constant_format = self._create_format("#569CD6", bold=True)  # Blue
        constants = ['True', 'False', 'None']
        self._add_keyword_rules(constants, constant_format)

        # Strings (double quotes)
        string_format = self._create_format("#CE9178")  # Orange
        self._add_pattern_rule(r'"[^"\\]*(\\.[^"\\]*)*"', string_format)

        # Strings (single quotes)
        self._add_pattern_rule(r"'[^'\\]*(\\.[^'\\]*)*'", string_format)

        # Triple-quoted strings
        self._add_pattern_rule(r'""".*?"""', string_format)
        self._add_pattern_rule(r"'''.*?'''", string_format)

        # Comments
        comment_format = self._create_format("#6A9955", italic=True)  # Green
        self._add_pattern_rule(r'#.*', comment_format)

        # Numbers
        number_format = self._create_format("#B5CEA8")  # Light green
        self._add_pattern_rule(r'\b\d+\.?\d*\b', number_format)

        # Decorators
        decorator_format = self._create_format("#DCDCAA")  # Yellow
        self._add_pattern_rule(r'@\w+', decorator_format)

        # Function definitions
        function_format = self._create_format("#DCDCAA")  # Yellow
        self._add_pattern_rule(r'\bdef\s+(\w+)', function_format)

        # Class definitions
        class_format = self._create_format("#4EC9B0")  # Cyan
        self._add_pattern_rule(r'\bclass\s+(\w+)', class_format)


class RubySyntaxHighlighter(BaseSyntaxHighlighter):
    """Ruby syntax highlighter."""

    def _setup_highlighting_rules(self):
        """Setup Ruby-specific highlighting rules."""
        # Keywords
        keyword_format = self._create_format("#569CD6", bold=True)  # Blue
        keywords = [
            'alias', 'and', 'begin', 'break', 'case', 'class', 'def', 'defined',
            'do', 'else', 'elsif', 'end', 'ensure', 'false', 'for', 'if',
            'in', 'module', 'next', 'nil', 'not', 'or', 'redo', 'rescue',
            'retry', 'return', 'self', 'super', 'then', 'true', 'undef',
            'unless', 'until', 'when', 'while', 'yield', '__FILE__', '__LINE__'
        ]
        self._add_keyword_rules(keywords, keyword_format)

        # Built-in methods
        builtin_format = self._create_format("#DCDCAA")  # Yellow
        builtins = [
            'puts', 'print', 'p', 'gets', 'require', 'include', 'extend',
            'attr_reader', 'attr_writer', 'attr_accessor', 'private', 'protected',
            'public', 'initialize', 'new', 'class', 'instance_of?', 'kind_of?',
            'respond_to?', 'send', 'method', 'methods', 'instance_variables'
        ]
        self._add_keyword_rules(builtins, builtin_format)

        # Constants and symbols
        constant_format = self._create_format("#4EC9B0")  # Cyan
        self._add_pattern_rule(r'\b[A-Z][A-Z0-9_]*\b', constant_format)

        # Symbols
        symbol_format = self._create_format("#D7BA7D")  # Gold
        self._add_pattern_rule(r':\w+', symbol_format)
        self._add_pattern_rule(r':\'[^\']*\'', symbol_format)
        self._add_pattern_rule(r':"[^"]*"', symbol_format)

        # Strings (double quotes)
        string_format = self._create_format("#CE9178")  # Orange
        self._add_pattern_rule(r'"[^"\\]*(\\.[^"\\]*)*"', string_format)

        # Strings (single quotes)
        self._add_pattern_rule(r"'[^'\\]*(\\.[^'\\]*)*'", string_format)

        # Comments
        comment_format = self._create_format("#6A9955", italic=True)  # Green
        self._add_pattern_rule(r'#.*', comment_format)

        # Numbers
        number_format = self._create_format("#B5CEA8")  # Light green
        self._add_pattern_rule(r'\b\d+\.?\d*\b', number_format)

        # Instance variables
        instance_var_format = self._create_format("#9CDCFE")  # Light blue
        self._add_pattern_rule(r'@\w+', instance_var_format)

        # Class variables
        class_var_format = self._create_format("#9CDCFE")  # Light blue
        self._add_pattern_rule(r'@@\w+', class_var_format)

        # Global variables
        global_var_format = self._create_format("#9CDCFE")  # Light blue
        self._add_pattern_rule(r'\$\w+', global_var_format)

        # Regular expressions
        regex_format = self._create_format("#D16969")  # Red
        self._add_pattern_rule(r'/[^/\\]*(\\.[^/\\]*)*/[gimxo]*', regex_format)


class LuaSyntaxHighlighter(BaseSyntaxHighlighter):
    """Lua syntax highlighter."""

    def _setup_highlighting_rules(self):
        """Setup Lua-specific highlighting rules."""
        # Keywords
        keyword_format = self._create_format("#569CD6", bold=True)  # Blue
        keywords = [
            'and', 'break', 'do', 'else', 'elseif', 'end', 'false', 'for',
            'function', 'if', 'in', 'local', 'nil', 'not', 'or', 'repeat',
            'return', 'then', 'true', 'until', 'while', 'goto'
        ]
        self._add_keyword_rules(keywords, keyword_format)

        # Built-in functions
        builtin_format = self._create_format("#DCDCAA")  # Yellow
        builtins = [
            'assert', 'collectgarbage', 'dofile', 'error', 'getmetatable',
            'ipairs', 'load', 'loadfile', 'next', 'pairs', 'pcall', 'print',
            'rawequal', 'rawget', 'rawlen', 'rawset', 'require', 'select',
            'setmetatable', 'tonumber', 'tostring', 'type', 'unpack', 'xpcall'
        ]
        self._add_keyword_rules(builtins, builtin_format)

        # Standard library modules
        module_format = self._create_format("#4EC9B0")  # Cyan
        modules = [
            'table', 'string', 'math', 'io', 'os', 'debug', 'coroutine',
            'package', 'utf8'
        ]
        self._add_keyword_rules(modules, module_format)

        # Strings (double quotes)
        string_format = self._create_format("#CE9178")  # Orange
        self._add_pattern_rule(r'"[^"\\]*(\\.[^"\\]*)*"', string_format)

        # Strings (single quotes)
        self._add_pattern_rule(r"'[^'\\]*(\\.[^'\\]*)*'", string_format)

        # Long strings
        self._add_pattern_rule(r'\[\[.*?\]\]', string_format)

        # Comments (single line)
        comment_format = self._create_format("#6A9955", italic=True)  # Green
        self._add_pattern_rule(r'--.*', comment_format)

        # Comments (multi-line)
        self._add_pattern_rule(r'--\[\[.*?\]\]', comment_format)

        # Numbers
        number_format = self._create_format("#B5CEA8")  # Light green
        self._add_pattern_rule(r'\b\d+\.?\d*([eE][+-]?\d+)?\b', number_format)
        self._add_pattern_rule(r'\b0[xX][0-9a-fA-F]+\b', number_format)  # Hex numbers

        # Function definitions
        function_format = self._create_format("#DCDCAA")  # Yellow
        self._add_pattern_rule(r'\bfunction\s+(\w+)', function_format)

        # String concatenation
        concat_format = self._create_format("#D4D4D4")  # White
        self._add_pattern_rule(r'\.\.', concat_format)


class BasicSyntaxHighlighter(BaseSyntaxHighlighter):
    """BASIC syntax highlighter."""

    def _setup_highlighting_rules(self):
        """Setup BASIC-specific highlighting rules."""
        # Keywords
        keyword_format = self._create_format("#569CD6", bold=True)  # Blue
        keywords = [
            'AND', 'AS', 'CASE', 'CONST', 'DIM', 'DO', 'ELSE', 'ELSEIF', 'END',
            'EXIT', 'FOR', 'FUNCTION', 'GOSUB', 'GOTO', 'IF', 'INPUT', 'LET',
            'LOOP', 'NEXT', 'NOT', 'OR', 'PRINT', 'RETURN', 'SELECT', 'STEP',
            'SUB', 'THEN', 'TO', 'UNTIL', 'WEND', 'WHILE', 'WITH', 'XOR',
            # Case insensitive versions
            'and', 'as', 'case', 'const', 'dim', 'do', 'else', 'elseif', 'end',
            'exit', 'for', 'function', 'gosub', 'goto', 'if', 'input', 'let',
            'loop', 'next', 'not', 'or', 'print', 'return', 'select', 'step',
            'sub', 'then', 'to', 'until', 'wend', 'while', 'with', 'xor'
        ]
        self._add_keyword_rules(keywords, keyword_format)

        # Built-in functions
        builtin_format = self._create_format("#DCDCAA")  # Yellow
        builtins = [
            'ABS', 'ASC', 'ATN', 'CHR$', 'COS', 'EXP', 'FIX', 'INT', 'LEFT$',
            'LEN', 'LOG', 'MID$', 'RIGHT$', 'RND', 'SGN', 'SIN', 'SQR', 'STR$',
            'TAN', 'VAL', 'INKEY$', 'TIMER', 'DATE$', 'TIME$',
            # Case insensitive versions
            'abs', 'asc', 'atn', 'chr$', 'cos', 'exp', 'fix', 'int', 'left$',
            'len', 'log', 'mid$', 'right$', 'rnd', 'sgn', 'sin', 'sqr', 'str$',
            'tan', 'val', 'inkey$', 'timer', 'date$', 'time$'
        ]
        self._add_keyword_rules(builtins, builtin_format)

        # Data types
        type_format = self._create_format("#4EC9B0")  # Cyan
        types = [
            'INTEGER', 'LONG', 'SINGLE', 'DOUBLE', 'STRING', 'BOOLEAN',
            'integer', 'long', 'single', 'double', 'string', 'boolean'
        ]
        self._add_keyword_rules(types, type_format)

        # Constants
        constant_format = self._create_format("#569CD6", bold=True)  # Blue
        constants = ['TRUE', 'FALSE', 'true', 'false']
        self._add_keyword_rules(constants, constant_format)

        # Strings
        string_format = self._create_format("#CE9178")  # Orange
        self._add_pattern_rule(r'"[^"]*"', string_format)

        # Comments (REM and ')
        comment_format = self._create_format("#6A9955", italic=True)  # Green
        self._add_pattern_rule(r"'.*", comment_format)
        self._add_pattern_rule(r'\bREM\b.*', comment_format)
        self._add_pattern_rule(r'\brem\b.*', comment_format)

        # Numbers
        number_format = self._create_format("#B5CEA8")  # Light green
        self._add_pattern_rule(r'\b\d+\.?\d*\b', number_format)

        # Line numbers (classic BASIC)
        line_number_format = self._create_format("#D4D4D4")  # White
        self._add_pattern_rule(r'^\s*\d+\s+', line_number_format)

        # Variables with type suffixes
        variable_format = self._create_format("#9CDCFE")  # Light blue
        self._add_pattern_rule(r'\b\w+[$%&!#]', variable_format)


class PseudocodeSyntaxHighlighter(BaseSyntaxHighlighter):
    """Pseudocode syntax highlighter."""

    def _setup_highlighting_rules(self):
        """Setup Cambridge IGCSE Pseudocode highlighting rules."""
        # Control flow keywords (IGCSE style)
        keyword_format = self._create_format("#569CD6", bold=True)  # Blue
        keywords = [
            'IF', 'THEN', 'ELSE', 'ENDIF', 'WHILE', 'ENDWHILE',
            'FOR', 'TO', 'NEXT', 'REPEAT', 'UNTIL', 'CASE', 'OF', 'ENDCASE',
            'PROCEDURE', 'ENDPROCEDURE', 'FUNCTION', 'ENDFUNCTION', 'RETURN',
            'RETURNS', 'DECLARE', 'CONSTANT',
            # Case insensitive versions
            'if', 'then', 'else', 'endif', 'while', 'endwhile',
            'for', 'to', 'next', 'repeat', 'until', 'case', 'of', 'endcase',
            'procedure', 'endprocedure', 'function', 'endfunction', 'return',
            'returns', 'declare', 'constant'
        ]
        self._add_keyword_rules(keywords, keyword_format)

        # Logical operators
        operator_format = self._create_format("#D4D4D4", bold=True)  # White
        operators = [
            'AND', 'OR', 'NOT', 'XOR', 'NAND', 'NOR',
            'and', 'or', 'not', 'xor', 'nand', 'nor'
        ]
        self._add_keyword_rules(operators, operator_format)

        # Data operations (IGCSE style)
        data_format = self._create_format("#DCDCAA")  # Yellow
        data_ops = [
            'INPUT', 'OUTPUT', 'READ', 'WRITE', 'DISPLAY', 'PRINT',
            'OPENFILE', 'CLOSEFILE', 'READFILE', 'WRITEFILE',
            'input', 'output', 'read', 'write', 'display', 'print',
            'openfile', 'closefile', 'readfile', 'writefile'
        ]
        self._add_keyword_rules(data_ops, data_format)

        # Data types (IGCSE style)
        type_format = self._create_format("#4EC9B0")  # Cyan
        types = [
            'INTEGER', 'REAL', 'STRING', 'BOOLEAN', 'CHAR', 'ARRAY',
            'integer', 'real', 'string', 'boolean', 'char', 'array'
        ]
        self._add_keyword_rules(types, type_format)

        # Constants (IGCSE style)
        constant_format = self._create_format("#569CD6", bold=True)  # Blue
        constants = [
            'TRUE', 'FALSE',
            'true', 'false'
        ]
        self._add_keyword_rules(constants, constant_format)

        # Strings (IGCSE uses double quotes)
        string_format = self._create_format("#CE9178")  # Orange
        self._add_pattern_rule(r'"[^"]*"', string_format)

        # Comments (IGCSE uses // style)
        comment_format = self._create_format("#6A9955", italic=True)  # Green
        self._add_pattern_rule(r'//.*', comment_format)

        # Numbers
        number_format = self._create_format("#B5CEA8")  # Light green
        self._add_pattern_rule(r'\b\d+\.?\d*\b', number_format)

        # Assignment operator (IGCSE uses ←)
        assignment_format = self._create_format("#D4D4D4", bold=True)  # White
        self._add_pattern_rule(r'←', assignment_format)

        # Mathematical operators (IGCSE style)
        math_format = self._create_format("#D4D4D4")  # White
        self._add_pattern_rule(r'[+\-*/=<>≤≥≠]', math_format)
        self._add_pattern_rule(r'\bMOD\b|\bmod\b|\bDIV\b|\bdiv\b', math_format)

        # Array indexing
        array_format = self._create_format("#9CDCFE")  # Light blue
        self._add_pattern_rule(r'\w+\[[^\]]+\]', array_format)


class SyntaxHighlighterFactory:
    """
    Factory class for creating syntax highlighters.

    This factory provides a centralized way to create syntax highlighters
    for different programming languages and makes it easy to add new languages.
    """

    _highlighters: Dict[str, type] = {
        'python': PythonSyntaxHighlighter,
        'ruby': RubySyntaxHighlighter,
        'lua': LuaSyntaxHighlighter,
        'basic': BasicSyntaxHighlighter,
        'pseudocode': PseudocodeSyntaxHighlighter,
    }

    @classmethod
    def create_highlighter(cls, language: str, document) -> Optional[BaseSyntaxHighlighter]:
        """
        Create a syntax highlighter for the specified language.

        Args:
            language: Programming language name (case-insensitive)
            document: QTextDocument to apply highlighting to

        Returns:
            Syntax highlighter instance or None if language not supported
        """
        language_key = language.lower().strip()
        highlighter_class = cls._highlighters.get(language_key)

        if highlighter_class:
            return highlighter_class(document)
        return None

    @classmethod
    def get_supported_languages(cls) -> List[str]:
        """Get list of supported languages."""
        return list(cls._highlighters.keys())

    @classmethod
    def register_highlighter(cls, language: str, highlighter_class: type):
        """
        Register a new syntax highlighter for a language.

        Args:
            language: Programming language name
            highlighter_class: Highlighter class (must inherit from BaseSyntaxHighlighter)
        """
        if not issubclass(highlighter_class, BaseSyntaxHighlighter):
            raise ValueError("Highlighter class must inherit from BaseSyntaxHighlighter")

        cls._highlighters[language.lower().strip()] = highlighter_class

    @classmethod
    def is_language_supported(cls, language: str) -> bool:
        """Check if a language is supported."""
        return language.lower().strip() in cls._highlighters
