"""
PLAIN Language Syntax Highlighter
Provides syntax highlighting for the PLAIN programming language
"""

import re
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont

from plain_ide.app.themes import Theme


class PlainHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for PLAIN language"""
    
    def __init__(self, parent=None, theme: Theme = None):
        super().__init__(parent)
        self.theme = theme
        self._setup_rules()
    
    def set_theme(self, theme: Theme):
        """Update the theme and refresh highlighting"""
        self.theme = theme
        self._setup_rules()
        self.rehighlight()
    
    def _create_format(self, color: str, bold: bool = False, italic: bool = False) -> QTextCharFormat:
        """Create a text format with the given style"""
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        if bold:
            fmt.setFontWeight(QFont.Weight.Bold)
        if italic:
            fmt.setFontItalic(True)
        return fmt
    
    def _setup_rules(self):
        """Set up highlighting rules based on current theme"""
        self.rules = []
        
        if self.theme is None:
            return
        
        syntax = self.theme.syntax
        
        # Keywords - structure
        structure_keywords = r'\b(task|deliver|record|use|based on|with)\b'
        self.rules.append((re.compile(structure_keywords), self._create_format(syntax.keyword, bold=True)))
        
        # Keywords - control flow
        control_keywords = r'\b(if|else|choose|choice|default|loop|from|to|step|in|while|until)\b'
        self.rules.append((re.compile(control_keywords), self._create_format(syntax.keyword, bold=True)))
        
        # Keywords - error handling
        error_keywords = r'\b(attempt|handle|ensure)\b'
        self.rules.append((re.compile(error_keywords), self._create_format(syntax.keyword, bold=True)))
        
        # Keywords - variable declarations
        var_keywords = r'\b(var|fxd)\b'
        self.rules.append((re.compile(var_keywords), self._create_format(syntax.keyword, bold=True)))
        
        # Import subsections
        import_sections = r'\b(assemblies|modules|tasks):'
        self.rules.append((re.compile(import_sections), self._create_format(syntax.builtin)))
        
        # Type prefixes
        type_prefixes = r'\b(int|flt|str|bln|lst|tbl|as|integer|float|string|boolean|list|table)\b'
        self.rules.append((re.compile(type_prefixes), self._create_format(syntax.type)))
        
        # Built-in functions
        builtins = r'\b(display|input|len|type|toString|toNumber|toBoolean|abs|round|floor|ceil|min|max|random|append|remove|contains|keys|values|now|wait|sleep)\b'
        self.rules.append((re.compile(builtins), self._create_format(syntax.builtin)))
        
        # Boolean literals
        booleans = r'\b(true|false|null|nothing)\b'
        self.rules.append((re.compile(booleans), self._create_format(syntax.constant)))
        
        # Numbers (integers and floats)
        numbers = r'\b\d+\.?\d*\b'
        self.rules.append((re.compile(numbers), self._create_format(syntax.number)))
        
        # Function/Task definitions
        func_def = r'\b([A-Z][a-zA-Z0-9_]*)\s*\('
        self.rules.append((re.compile(func_def), self._create_format(syntax.function)))
        
        # Regular strings (double quotes)
        strings = r'"[^"\\]*(\\.[^"\\]*)*"'
        self.rules.append((re.compile(strings), self._create_format(syntax.string)))
        
        # Single-quoted strings
        single_strings = r"'[^'\\]*(\\.[^'\\]*)*'"
        self.rules.append((re.compile(single_strings), self._create_format(syntax.string)))
        
        # Interpolated strings (v"...")
        interp_strings = r'v"[^"\\]*(\\.[^"\\]*)*"'
        self.rules.append((re.compile(interp_strings), self._create_format(syntax.interpolation)))
        
        # Comments - rem: single line
        rem_comment = r'rem:.*$'
        self.rules.append((re.compile(rem_comment), self._create_format(syntax.comment, italic=True)))
        
        # Comments - note: (will be handled specially for multi-line)
        note_comment = r'note:.*$'
        self.rules.append((re.compile(note_comment), self._create_format(syntax.comment, italic=True)))
        
        # Operators
        operators = r'[+\-*/%=<>!&|^~]+'
        self.rules.append((re.compile(operators), self._create_format(syntax.operator)))
    
    def highlightBlock(self, text: str):
        """Apply highlighting to a block of text"""
        for pattern, fmt in self.rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)

