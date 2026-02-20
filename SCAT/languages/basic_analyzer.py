"""
BASIC language analyzer for the Code Analysis Tool.

This module provides BASIC-specific code complexity analysis using
regular expressions and pattern matching for parsing and analysis.
"""

import re
from typing import List, Any, Dict, Tuple

from .base import BaseLanguageAnalyzer
from core.models import ComplexityResult


class BasicAnalyzer(BaseLanguageAnalyzer):
    """
    BASIC-specific code complexity analyzer.

    This analyzer uses regular expressions and pattern matching to analyze BASIC code
    for complexity patterns including loops, recursion, built-in functions,
    data structures, and BASIC-specific constructs.
    """

    def __init__(self, config):
        """Initialize the BASIC analyzer."""
        super().__init__(config)

        # BASIC built-in function complexities
        self.builtin_complexities = {
            'ABS': {'time': 'O(1)', 'space': 'O(1)'},
            'ASC': {'time': 'O(1)', 'space': 'O(1)'},
            'ATN': {'time': 'O(1)', 'space': 'O(1)'},
            'CHR$': {'time': 'O(1)', 'space': 'O(1)'},
            'COS': {'time': 'O(1)', 'space': 'O(1)'},
            'EXP': {'time': 'O(1)', 'space': 'O(1)'},
            'FIX': {'time': 'O(1)', 'space': 'O(1)'},
            'INT': {'time': 'O(1)', 'space': 'O(1)'},
            'LEFT$': {'time': 'O(n)', 'space': 'O(n)'},
            'LEN': {'time': 'O(1)', 'space': 'O(1)'},
            'LOG': {'time': 'O(1)', 'space': 'O(1)'},
            'MID$': {'time': 'O(n)', 'space': 'O(n)'},
            'RIGHT$': {'time': 'O(n)', 'space': 'O(n)'},
            'RND': {'time': 'O(1)', 'space': 'O(1)'},
            'SGN': {'time': 'O(1)', 'space': 'O(1)'},
            'SIN': {'time': 'O(1)', 'space': 'O(1)'},
            'SQR': {'time': 'O(1)', 'space': 'O(1)'},
            'STR$': {'time': 'O(log n)', 'space': 'O(log n)'},
            'TAN': {'time': 'O(1)', 'space': 'O(1)'},
            'VAL': {'time': 'O(n)', 'space': 'O(1)'},
            'INKEY$': {'time': 'O(1)', 'space': 'O(1)'},
            'TIMER': {'time': 'O(1)', 'space': 'O(1)'},
            'DATE$': {'time': 'O(1)', 'space': 'O(1)'},
            'TIME$': {'time': 'O(1)', 'space': 'O(1)'},
        }

        # BASIC syntax patterns
        self.patterns = {
            'loop': [
                r'^\s*FOR\s+\w+\s*=',  # FOR loops
                r'^\s*WHILE\s+',       # WHILE loops
                r'^\s*DO\s*$',         # DO loops
            ],
            'function_def': [
                r'^\s*FUNCTION\s+(\w+)',  # Function definitions
                r'^\s*SUB\s+(\w+)',       # Subroutine definitions
            ],
            'function_call': [
                r'(\w+)\s*\(',           # Function calls
                r'GOSUB\s+(\w+)',        # GOSUB calls
                r'CALL\s+(\w+)',         # CALL statements
            ],
            'array_operations': [
                r'\w+\s*\([^)]+\)\s*=',  # Array assignments
                r'DIM\s+\w+\s*\(',       # Array declarations
            ],
            'string_operations': [
                r'LEFT\$\s*\(',
                r'RIGHT\$\s*\(',
                r'MID\$\s*\(',
                r'CHR\$\s*\(',
                r'STR\$\s*\(',
            ],
            'control_flow': [
                r'^\s*IF\s+.*\s+THEN',   # IF statements
                r'^\s*SELECT\s+CASE',    # SELECT CASE
                r'^\s*GOTO\s+',          # GOTO statements
                r'^\s*GOSUB\s+',         # GOSUB statements
            ]
        }

    def get_language_name(self) -> str:
        """Get the language name."""
        return 'basic'

    def parse_code(self, code: str) -> List[str]:
        """
        Parse BASIC code into lines for analysis.

        Args:
            code: BASIC source code

        Returns:
            List of code lines

        Raises:
            SyntaxError: If code has obvious syntax errors
        """
        lines = code.splitlines()

        # Basic syntax validation
        self._validate_basic_syntax(lines)

        return lines

    def analyze_structure(self, parsed_code: List[str]) -> List[ComplexityResult]:
        """
        Analyze BASIC code lines for complexity patterns.

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
            if not line or line.startswith('REM') or line.startswith("'"):
                continue

            # Remove line numbers if present
            line = re.sub(r'^\d+\s+', '', line)

            # Analyze different patterns
            self._analyze_loops(line, line_num, len(nesting_stack), results)
            self._analyze_functions(line, line_num, function_names, results)
            self._analyze_function_calls(line, line_num, len(nesting_stack) > 0, results)
            self._analyze_arrays(line, line_num, results)
            self._analyze_string_operations(line, line_num, results)
            self._analyze_control_flow(line, line_num, results)

            # Track nesting
            self._update_nesting_stack(line, nesting_stack)

        return results

    def _validate_basic_syntax(self, lines: List[str]):
        """Basic BASIC syntax validation."""
        # Simplified validation - just check for obvious syntax errors
        # Don't be too strict as BASIC has many variations

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('REM') or line.startswith("'"):
                continue

            # Remove line numbers
            line = re.sub(r'^\d+\s+', '', line)

            # Check for basic syntax issues
            # Count parentheses
            if line.count('(') != line.count(')'):
                # Allow unmatched parentheses in some contexts
                pass

            # Check for obvious malformed statements
            if line.endswith('THEN') and 'IF' not in line.upper():
                raise SyntaxError(f"Line {line_num}: THEN without IF")

        # Don't enforce strict keyword matching as BASIC syntax varies widely

    def _analyze_loops(self, line: str, line_num: int, depth: int, results: List[ComplexityResult]):
        """Analyze loop constructs."""
        for pattern in self.patterns['loop']:
            if re.search(pattern, line, re.IGNORECASE):
                # Determine complexity based on loop type and nesting
                if depth == 0:
                    time_complexity = 'O(n)'
                    description = "Single loop"
                elif depth == 1:
                    time_complexity = 'O(n²)'
                    description = "Nested loop (2 levels)"
                else:
                    time_complexity = f'O(n^{depth + 1})'
                    description = f"Deeply nested loop ({depth + 1} levels)"

                result = ComplexityResult(
                    time_complexity=time_complexity,
                    space_complexity='O(1)',
                    line_number=line_num,
                    description=description,
                    analysis_type="Loop",
                    confidence=0.9,
                    suggestions=self._get_loop_suggestions(depth)
                )
                results.append(result)
                break

    def _analyze_functions(self, line: str, line_num: int, function_names: set,
                          results: List[ComplexityResult]):
        """Analyze function definitions and recursion."""
        for pattern in self.patterns['function_def']:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                func_name = match.group(1).upper()
                function_names.add(func_name)

                # Check for potential recursion (simple heuristic)
                if func_name in line.upper() and not re.search(r'\b(FUNCTION|SUB)\b', line, re.IGNORECASE):
                    result = ComplexityResult(
                        time_complexity='O(2ⁿ)',
                        space_complexity='O(n)',
                        line_number=line_num,
                        description=f"Potential recursive function '{func_name}'",
                        analysis_type="Recursion",
                        confidence=0.6,
                        suggestions=[
                            f"Consider iterative approach for '{func_name}' if recursive",
                            "Use memoization to improve recursive performance"
                        ]
                    )
                    results.append(result)
                break

    def _analyze_function_calls(self, line: str, line_num: int, in_loop: bool,
                               results: List[ComplexityResult]):
        """Analyze function calls and built-in functions."""
        # Check for built-in functions
        for func_name, complexity_info in self.builtin_complexities.items():
            if re.search(rf'\b{func_name}\s*\(', line, re.IGNORECASE):
                time_complexity = complexity_info['time']
                space_complexity = complexity_info['space']

                # Adjust complexity if inside loop
                if in_loop and time_complexity != 'O(1)':
                    time_complexity = self._multiply_complexity(time_complexity, 'O(n)')

                result = ComplexityResult(
                    time_complexity=time_complexity,
                    space_complexity=space_complexity,
                    line_number=line_num,
                    description=f"Built-in function '{func_name}' call",
                    analysis_type="Built-in Function",
                    confidence=0.95,
                    suggestions=self._get_builtin_suggestions(func_name, in_loop)
                )
                results.append(result)

    def _analyze_arrays(self, line: str, line_num: int, results: List[ComplexityResult]):
        """Analyze array operations."""
        for pattern in self.patterns['array_operations']:
            if re.search(pattern, line, re.IGNORECASE):
                result = ComplexityResult(
                    time_complexity='O(1)',
                    space_complexity='O(n)',
                    line_number=line_num,
                    description="Array operation",
                    analysis_type="Array",
                    confidence=0.8,
                    suggestions=["Consider memory usage for large arrays"]
                )
                results.append(result)
                break

    def _analyze_string_operations(self, line: str, line_num: int, results: List[ComplexityResult]):
        """Analyze string operations."""
        for pattern in self.patterns['string_operations']:
            if re.search(pattern, line, re.IGNORECASE):
                result = ComplexityResult(
                    time_complexity='O(n)',
                    space_complexity='O(n)',
                    line_number=line_num,
                    description="String manipulation operation",
                    analysis_type="String Operation",
                    confidence=0.8,
                    suggestions=["String operations can be expensive for large strings"]
                )
                results.append(result)
                break

    def _analyze_control_flow(self, line: str, line_num: int, results: List[ComplexityResult]):
        """Analyze control flow statements."""
        if re.search(r'^\s*GOTO\s+', line, re.IGNORECASE):
            result = ComplexityResult(
                time_complexity='O(1)',
                space_complexity='O(1)',
                line_number=line_num,
                description="GOTO statement - consider structured programming",
                analysis_type="Control Flow",
                confidence=0.9,
                suggestions=[
                    "Avoid GOTO statements when possible",
                    "Use structured control flow (IF, WHILE, FOR) instead"
                ]
            )
            results.append(result)

    def _update_nesting_stack(self, line: str, nesting_stack: List[str]):
        """Update nesting stack for tracking loop depth."""
        line_upper = line.upper()

        # Opening constructs
        if re.search(r'\bFOR\b', line_upper):
            nesting_stack.append('FOR')
        elif re.search(r'\bWHILE\b', line_upper):
            nesting_stack.append('WHILE')
        elif re.search(r'\bDO\b', line_upper):
            nesting_stack.append('DO')

        # Closing constructs
        if re.search(r'\bNEXT\b', line_upper) and 'FOR' in nesting_stack:
            nesting_stack.remove('FOR')
        elif re.search(r'\bWEND\b', line_upper) and 'WHILE' in nesting_stack:
            nesting_stack.remove('WHILE')
        elif re.search(r'\bLOOP\b', line_upper) and 'DO' in nesting_stack:
            nesting_stack.remove('DO')

    def _get_loop_suggestions(self, depth: int) -> List[str]:
        """Get suggestions for loop optimization."""
        suggestions = []
        if depth == 0:
            suggestions.append("Consider if loop can be optimized or vectorized")
        elif depth == 1:
            suggestions.append("Nested loops can be expensive - consider algorithm optimization")
        else:
            suggestions.append("Deeply nested loops are very expensive - consider redesigning algorithm")
        return suggestions

    def _get_builtin_suggestions(self, func_name: str, in_loop: bool) -> List[str]:
        """Get suggestions for built-in function usage."""
        suggestions = []
        if in_loop:
            suggestions.append(f"'{func_name}' called in loop - consider moving outside if possible")
        if func_name in ['LEFT$', 'RIGHT$', 'MID$']:
            suggestions.append("String functions can be expensive for large strings")
        return suggestions

    def _multiply_complexity(self, complexity1: str, complexity2: str) -> str:
        """Multiply two complexity expressions."""
        # Simple complexity multiplication
        if complexity1 == 'O(1)':
            return complexity2
        elif complexity2 == 'O(1)':
            return complexity1
        elif complexity1 == 'O(n)' and complexity2 == 'O(n)':
            return 'O(n²)'
        else:
            return f'{complexity1} × {complexity2}'
