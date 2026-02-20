"""
Lua language analyzer for the Code Analysis Tool.

This module provides Lua-specific code complexity analysis using
regular expressions and pattern matching for parsing and analysis.
"""

import re
from typing import List, Any, Dict, Tuple

from .base import BaseLanguageAnalyzer
from core.models import ComplexityResult


class LuaAnalyzer(BaseLanguageAnalyzer):
    """
    Lua-specific code complexity analyzer.

    This analyzer uses regular expressions and pattern matching to analyze Lua code
    for complexity patterns including loops, recursion, built-in functions,
    data structures, and table operations.
    """

    def __init__(self, config):
        """Initialize the Lua analyzer."""
        super().__init__(config)

        # Lua built-in function complexities
        self.builtin_complexities = {
            'table.sort': {'time': 'O(n log n)', 'space': 'O(1)'},
            'table.insert': {'time': 'O(n)', 'space': 'O(1)'},
            'table.remove': {'time': 'O(n)', 'space': 'O(1)'},
            'table.concat': {'time': 'O(n)', 'space': 'O(n)'},
            'string.find': {'time': 'O(n)', 'space': 'O(1)'},
            'string.match': {'time': 'O(n)', 'space': 'O(1)'},
            'string.gsub': {'time': 'O(n)', 'space': 'O(n)'},
            'string.sub': {'time': 'O(n)', 'space': 'O(n)'},
            'pairs': {'time': 'O(1)', 'space': 'O(1)'},
            'ipairs': {'time': 'O(1)', 'space': 'O(1)'},
            'next': {'time': 'O(1)', 'space': 'O(1)'},
            'type': {'time': 'O(1)', 'space': 'O(1)'},
            'tostring': {'time': 'O(n)', 'space': 'O(n)'},
            'tonumber': {'time': 'O(n)', 'space': 'O(1)'},
            'math.max': {'time': 'O(1)', 'space': 'O(1)'},
            'math.min': {'time': 'O(1)', 'space': 'O(1)'},
            'math.abs': {'time': 'O(1)', 'space': 'O(1)'},
            'math.floor': {'time': 'O(1)', 'space': 'O(1)'},
            'math.ceil': {'time': 'O(1)', 'space': 'O(1)'},
        }

        # Lua syntax patterns
        self.patterns = {
            'loop': [
                r'^\s*for\s+\w+\s*=',
                r'^\s*for\s+\w+\s*,\s*\w+\s+in\s+',
                r'^\s*while\s+',
                r'^\s*repeat\s*$',
            ],
            'function_def': [
                r'^\s*function\s+(\w+)',
                r'^\s*local\s+function\s+(\w+)',
                r'(\w+)\s*=\s*function',
            ],
            'function_call': [
                r'(\w+(?:\.\w+)*)\s*\(',
            ],
            'table_creation': [
                r'\{.*\}',
                r'setmetatable\s*\(',
            ],
            'table_access': [
                r'\w+\[.*\]',
                r'\w+\.\w+',
            ],
            'string_operations': [
                r'string\.\w+\s*\(',
                r'\.\.', # String concatenation
            ]
        }

    def get_language_name(self) -> str:
        """Get the language name."""
        return 'lua'

    def parse_code(self, code: str) -> List[str]:
        """
        Parse Lua code into lines for analysis.

        Args:
            code: Lua source code

        Returns:
            List of code lines

        Raises:
            SyntaxError: If code has obvious syntax errors
        """
        lines = code.splitlines()

        # Basic syntax validation
        self._validate_lua_syntax(lines)

        return lines

    def analyze_structure(self, parsed_code: List[str]) -> List[ComplexityResult]:
        """
        Analyze Lua code lines for complexity patterns.

        Args:
            parsed_code: List of code lines

        Returns:
            List of complexity analysis results
        """
        results = []

        # Track nesting levels and function names
        nesting_stack = []
        function_names = set()

        for line_num, line in enumerate(parsed_code, 1):
            line = line.strip()
            if not line or line.startswith('--'):
                continue

            # Analyze different patterns
            self._analyze_loops(line, line_num, len(nesting_stack), results)
            self._analyze_functions(line, line_num, function_names, results)
            self._analyze_function_calls(line, line_num, len(nesting_stack) > 0, results)
            self._analyze_tables(line, line_num, results)
            self._analyze_string_operations(line, line_num, results)

            # Track nesting
            self._update_nesting_stack(line, nesting_stack)

        return results

    def _validate_lua_syntax(self, lines: List[str]):
        """Basic Lua syntax validation."""
        # Check for balanced keywords
        keywords = {'function': 'end', 'if': 'end', 'while': 'end', 'for': 'end',
                   'repeat': 'until', 'do': 'end'}

        stack = []
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('--'):
                continue

            # Check for opening keywords (only at start of line or after whitespace)
            for keyword in keywords:
                # More precise pattern matching
                if keyword == 'function':
                    if re.search(r'^\s*function\s+\w+\s*\(', line) or re.search(r'^\s*local\s+function\s+\w+\s*\(', line):
                        stack.append((keyword, line_num))
                elif keyword == 'for':
                    if re.search(r'^\s*for\s+\w+\s*=', line) or re.search(r'^\s*for\s+\w+\s*,\s*\w+\s+in\s+', line):
                        stack.append((keyword, line_num))
                elif keyword == 'if':
                    if re.search(r'^\s*if\s+', line) and not re.search(r'\s+then\s+.*\s+end\s*$', line):
                        stack.append((keyword, line_num))
                elif keyword == 'while':
                    if re.search(r'^\s*while\s+', line):
                        stack.append((keyword, line_num))
                elif keyword == 'repeat':
                    if re.search(r'^\s*repeat\s*$', line):
                        stack.append((keyword, line_num))
                elif keyword == 'do':
                    if re.search(r'^\s*do\s*$', line):
                        stack.append((keyword, line_num))

            # Check for closing keywords
            if re.search(r'^\s*end\b', line):
                if not stack:
                    # Allow unmatched 'end' - might be from single-line constructs
                    continue
                keyword, _ = stack.pop()
                if keyword == 'repeat':
                    # Put it back, repeat should end with 'until'
                    stack.append((keyword, _))

            if re.search(r'^\s*until\b', line):
                if stack and stack[-1][0] == 'repeat':
                    stack.pop()

        # Don't raise errors for unmatched keywords - Lua syntax can be complex
        # This is just basic validation, not a full parser

    def _analyze_loops(self, line: str, line_num: int, depth: int, results: List[ComplexityResult]):
        """Analyze loop patterns."""
        for pattern in self.patterns['loop']:
            if re.search(pattern, line):
                # Determine complexity based on nesting depth
                if depth == 0:
                    time_complexity = 'O(n)'
                    description = "Single loop - linear time complexity"
                elif depth == 1:
                    time_complexity = 'O(n²)'
                    description = "Nested loop - quadratic time complexity"
                else:
                    time_complexity = f'O(n^{depth + 1})'
                    description = f"Multiple nested loops (depth {depth + 1}) - polynomial time complexity"

                result = ComplexityResult(
                    time_complexity=time_complexity,
                    space_complexity='O(1)',
                    line_number=line_num,
                    description=description,
                    analysis_type="Loop",
                    confidence=0.8,
                    suggestions=self._get_loop_suggestions(depth)
                )
                results.append(result)
                break

    def _analyze_functions(self, line: str, line_num: int, function_names: set,
                          results: List[ComplexityResult]):
        """Analyze function definitions and recursion."""
        for pattern in self.patterns['function_def']:
            match = re.search(pattern, line)
            if match:
                func_name = match.group(1)
                function_names.add(func_name)

                # Simple recursion detection (check if function name appears in its own definition)
                # This is a basic heuristic and may have false positives
                break

        # Check for recursion in function calls
        for func_name in function_names:
            if re.search(rf'\b{func_name}\s*\(', line) and 'function' not in line:
                result = ComplexityResult(
                    time_complexity='O(2ⁿ)',
                    space_complexity='O(n)',
                    line_number=line_num,
                    description=f"Potential recursive function call '{func_name}'",
                    analysis_type="Recursion",
                    confidence=0.6,
                    suggestions=[
                        f"Consider memoization for '{func_name}' if recursive",
                        "Consider iterative approach to reduce space complexity",
                        "Use tail recursion if possible"
                    ]
                )
                results.append(result)
                break

    def _analyze_function_calls(self, line: str, line_num: int, in_loop: bool,
                               results: List[ComplexityResult]):
        """Analyze function calls for known complexity patterns."""
        for pattern in self.patterns['function_call']:
            matches = re.finditer(pattern, line)
            for match in matches:
                func_name = match.group(1)
                if func_name in self.builtin_complexities:
                    complexity_info = self.builtin_complexities[func_name]
                    time_complexity = complexity_info['time']
                    space_complexity = complexity_info['space']

                    # Adjust complexity if inside loop
                    if in_loop and time_complexity != 'O(1)':
                        time_complexity = self._multiply_complexity(time_complexity, 'O(n)')

                    result = ComplexityResult(
                        time_complexity=time_complexity,
                        space_complexity=space_complexity,
                        line_number=line_num,
                        description=f"Lua function '{func_name}' call",
                        analysis_type="Built-in Function",
                        confidence=0.9,
                        suggestions=self._get_function_suggestions(func_name, in_loop)
                    )
                    results.append(result)

    def _analyze_tables(self, line: str, line_num: int, results: List[ComplexityResult]):
        """Analyze table operations."""
        # Table creation
        if any(re.search(pattern, line) for pattern in self.patterns['table_creation']):
            result = ComplexityResult(
                time_complexity='O(n)',
                space_complexity='O(n)',
                line_number=line_num,
                description="Table creation",
                analysis_type="Data Structure",
                confidence=0.8,
                suggestions=["Consider memory usage for large tables"]
            )
            results.append(result)

        # Table access patterns
        elif any(re.search(pattern, line) for pattern in self.patterns['table_access']):
            # Most table access is O(1) for hash tables, but we'll be conservative
            result = ComplexityResult(
                time_complexity='O(1)',
                space_complexity='O(1)',
                line_number=line_num,
                description="Table access operation",
                analysis_type="Table Access",
                confidence=0.7,
                suggestions=["Table access is typically O(1) for hash tables"]
            )
            results.append(result)

    def _analyze_string_operations(self, line: str, line_num: int, results: List[ComplexityResult]):
        """Analyze string operations."""
        for pattern in self.patterns['string_operations']:
            if re.search(pattern, line):
                result = ComplexityResult(
                    time_complexity='O(n)',
                    space_complexity='O(n)',
                    line_number=line_num,
                    description="String operation",
                    analysis_type="String Operation",
                    confidence=0.8,
                    suggestions=["String operations typically scale with string length"]
                )
                results.append(result)
                break

    def _update_nesting_stack(self, line: str, nesting_stack: List[str]):
        """Update nesting stack for tracking depth."""
        # Add to stack for keywords that increase nesting
        nesting_keywords = ['function', 'if', 'while', 'for', 'repeat', 'do']
        for keyword in nesting_keywords:
            if re.search(rf'^\s*{keyword}\b', line) or re.search(rf'\s+{keyword}\s*$', line):
                nesting_stack.append(keyword)
                break

        # Remove from stack for 'end'
        if re.search(r'^\s*end\b', line) and nesting_stack:
            nesting_stack.pop()

        # Handle 'until' for repeat loops
        if re.search(r'^\s*until\b', line) and nesting_stack and nesting_stack[-1] == 'repeat':
            nesting_stack.pop()

    def _multiply_complexity(self, complexity1: str, complexity2: str) -> str:
        """Multiply two complexity expressions."""
        if complexity1 == 'O(1)':
            return complexity2
        if complexity2 == 'O(1)':
            return complexity1
        if complexity1 == 'O(n)' and complexity2 == 'O(n)':
            return 'O(n²)'
        if 'O(n²)' in [complexity1, complexity2]:
            return 'O(n²)'
        return 'O(n²)'

    def _get_loop_suggestions(self, depth: int) -> List[str]:
        """Get optimization suggestions for loops."""
        suggestions = []
        if depth == 1:
            suggestions.extend([
                "Consider if the inner loop can be eliminated",
                "Look for opportunities to use table lookups for O(1) access",
                "Consider using ipairs for array-like tables"
            ])
        elif depth > 1:
            suggestions.extend([
                "Deep nesting indicates potential for significant optimization",
                "Consider breaking down into separate functions",
                "Look for opportunities to use table-based algorithms"
            ])
        return suggestions

    def _get_function_suggestions(self, func_name: str, in_loop: bool) -> List[str]:
        """Get suggestions for function usage."""
        suggestions = []
        if in_loop and func_name in ['table.sort', 'string.gsub', 'string.find']:
            suggestions.append(f"Calling {func_name} inside a loop increases overall complexity")
        if func_name == 'table.sort':
            suggestions.append("Consider if data can be kept sorted to avoid repeated sorting")
        if func_name in ['table.insert', 'table.remove']:
            suggestions.append("Consider using table[#table+1] for appending to avoid O(n) insertion")
        return suggestions
