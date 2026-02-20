# SCAT Syntax Highlighting System

## Overview

SCAT uses a modular syntax highlighting system that makes it easy to add support for new programming languages. The system is built around a factory pattern that creates language-specific syntax highlighters.

## Architecture

### Core Components

1. **BaseSyntaxHighlighter**: Base class that provides common functionality
2. **Language-specific highlighters**: Python, Ruby, Lua highlighters
3. **SyntaxHighlighterFactory**: Factory class for creating highlighters
4. **CodeEditor**: Integrates with the highlighting system

### File Structure

```
ui/components/
├── syntax_highlighting.py    # Main highlighting system
└── code_editor.py           # Code editor with highlighting integration
```

## Currently Supported Languages

- **Python**: Full syntax highlighting with keywords, built-ins, strings, comments, numbers, decorators
- **Ruby**: Keywords, built-ins, symbols, strings, comments, variables, regex
- **Lua**: Keywords, built-ins, modules, strings, comments, numbers, functions
- **BASIC**: Keywords, built-ins, data types, strings, comments, line numbers, variables with type suffixes
- **Pseudocode**: Cambridge IGCSE compliant - control flow, data operations, declarations, assignment operators

## Adding a New Language

### Step 1: Create a Language Highlighter

Create a new class that inherits from `BaseSyntaxHighlighter`:

```python
class JavaScriptSyntaxHighlighter(BaseSyntaxHighlighter):
    """JavaScript syntax highlighter."""

    def _setup_highlighting_rules(self):
        """Setup JavaScript-specific highlighting rules."""
        # Keywords
        keyword_format = self._create_format("#569CD6", bold=True)
        keywords = [
            'var', 'let', 'const', 'function', 'return', 'if', 'else',
            'for', 'while', 'do', 'break', 'continue', 'switch', 'case',
            'default', 'try', 'catch', 'finally', 'throw', 'new', 'this'
        ]
        self._add_keyword_rules(keywords, keyword_format)

        # Built-in objects
        builtin_format = self._create_format("#DCDCAA")
        builtins = ['console', 'document', 'window', 'Array', 'Object', 'String']
        self._add_keyword_rules(builtins, builtin_format)

        # Strings
        string_format = self._create_format("#CE9178")
        self._add_pattern_rule(r'"[^"\\]*(\\.[^"\\]*)*"', string_format)
        self._add_pattern_rule(r"'[^'\\]*(\\.[^'\\]*)*'", string_format)
        self._add_pattern_rule(r'`[^`\\]*(\\.[^`\\]*)*`', string_format)  # Template literals

        # Comments
        comment_format = self._create_format("#6A9955", italic=True)
        self._add_pattern_rule(r'//.*', comment_format)
        self._add_pattern_rule(r'/\*.*?\*/', comment_format)

        # Numbers
        number_format = self._create_format("#B5CEA8")
        self._add_pattern_rule(r'\b\d+\.?\d*\b', number_format)
```

### Step 2: Register the Language

Add your highlighter to the factory:

```python
# In syntax_highlighting.py, update the _highlighters dictionary:
_highlighters: Dict[str, type] = {
    'python': PythonSyntaxHighlighter,
    'ruby': RubySyntaxHighlighter,
    'lua': LuaSyntaxHighlighter,
    'javascript': JavaScriptSyntaxHighlighter,  # Add your new language
}
```

### Step 3: Add Sample Code (Optional)

Update the `insert_sample_code` method in `code_editor.py`:

```python
samples = {
    'python': '''# Python sample code...''',
    'ruby': '''# Ruby sample code...''',
    'lua': '''-- Lua sample code...''',
    'javascript': '''// JavaScript sample code
function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n-1) + fibonacci(n-2);
}

console.log("Fibonacci(10):", fibonacci(10));'''
}
```

## Helper Methods

The `BaseSyntaxHighlighter` provides several helper methods:

### `_create_format(color, bold=False, italic=False)`
Creates a text format with specified properties.

### `_add_keyword_rules(keywords, format_obj)`
Adds highlighting rules for a list of keywords.

### `_add_pattern_rule(pattern, format_obj)`
Adds a single regex pattern highlighting rule.

## Color Scheme

The highlighting system uses a consistent color scheme:

- **Keywords**: `#569CD6` (Blue, Bold)
- **Built-ins**: `#DCDCAA` (Yellow)
- **Strings**: `#CE9178` (Orange)
- **Comments**: `#6A9955` (Green, Italic)
- **Numbers**: `#B5CEA8` (Light Green)
- **Constants**: `#4EC9B0` (Cyan)
- **Variables**: `#9CDCFE` (Light Blue)

## Testing

Use the test script to verify your implementation:

```bash
python test_syntax_highlighting.py
```

## Dynamic Registration

You can also register languages at runtime:

```python
from ui.components.syntax_highlighting import SyntaxHighlighterFactory

# Register a new language
SyntaxHighlighterFactory.register_highlighter('mylang', MyLanguageHighlighter)

# Check if supported
if SyntaxHighlighterFactory.is_language_supported('mylang'):
    print("Language registered successfully!")
```

## Best Practices

1. **Use consistent colors** from the established color scheme
2. **Test thoroughly** with real code samples
3. **Handle edge cases** like nested strings, multi-line comments
4. **Keep patterns specific** to avoid false matches
5. **Document your patterns** for maintainability

## Future Enhancements

- **Semantic highlighting**: Context-aware highlighting
- **Theme support**: Multiple color schemes
- **Plugin system**: External language plugins
- **Performance optimization**: Lazy loading of highlighters
