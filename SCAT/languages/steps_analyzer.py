"""
Steps language analyzer for the Code Analysis Tool.

This module provides Steps-specific code complexity analysis using
regular expressions and pattern matching for parsing and analysis.
Steps is an educational programming language that uses indentation-based
nesting and multi-word keywords.
"""

import re
from typing import List

from .base import BaseLanguageAnalyzer
from core.models import ComplexityResult


class StepsAnalyzer(BaseLanguageAnalyzer):
    """
    Steps-specific code complexity analyzer.

    This analyzer uses regular expressions and pattern matching to analyze Steps code
    for complexity patterns including loops, step/riser definitions, step calls,
    data structures, built-in functions, and error handling.
    """

    def __init__(self, config):
        """Initialize the Steps analyzer."""
        super().__init__(config)

        # Steps built-in function complexities
        self.builtin_complexities = {
            # Math - O(1)
            'abs': {'time': 'O(1)', 'space': 'O(1)'},
            'max': {'time': 'O(1)', 'space': 'O(1)'},
            'min': {'time': 'O(1)', 'space': 'O(1)'},
            'round': {'time': 'O(1)', 'space': 'O(1)'},
            'sqr': {'time': 'O(1)', 'space': 'O(1)'},
            'sqrt': {'time': 'O(1)', 'space': 'O(1)'},
            'pow': {'time': 'O(1)', 'space': 'O(1)'},
            'pi': {'time': 'O(1)', 'space': 'O(1)'},
            'sin': {'time': 'O(1)', 'space': 'O(1)'},
            'cos': {'time': 'O(1)', 'space': 'O(1)'},
            'tan': {'time': 'O(1)', 'space': 'O(1)'},
            'asin': {'time': 'O(1)', 'space': 'O(1)'},
            'acos': {'time': 'O(1)', 'space': 'O(1)'},
            'atan': {'time': 'O(1)', 'space': 'O(1)'},
            'atan2': {'time': 'O(1)', 'space': 'O(1)'},
            'degrees': {'time': 'O(1)', 'space': 'O(1)'},
            'radians': {'time': 'O(1)', 'space': 'O(1)'},
            'log': {'time': 'O(1)', 'space': 'O(1)'},
            'log10': {'time': 'O(1)', 'space': 'O(1)'},
            'log2': {'time': 'O(1)', 'space': 'O(1)'},
            'exp': {'time': 'O(1)', 'space': 'O(1)'},
            # Strings - O(n)
            'reverse': {'time': 'O(n)', 'space': 'O(n)'},
            'repeat_text': {'time': 'O(n)', 'space': 'O(n)'},
            'lowercase': {'time': 'O(n)', 'space': 'O(n)'},
            'uppercase': {'time': 'O(n)', 'space': 'O(n)'},
            'trim': {'time': 'O(n)', 'space': 'O(n)'},
            'slice': {'time': 'O(n)', 'space': 'O(n)'},
            'index_of': {'time': 'O(n)', 'space': 'O(1)'},
            'replace': {'time': 'O(n)', 'space': 'O(n)'},
            'characters': {'time': 'O(n)', 'space': 'O(n)'},
            # List math - O(n)
            'list_min': {'time': 'O(n)', 'space': 'O(1)'},
            'list_max': {'time': 'O(n)', 'space': 'O(1)'},
            'list_sum': {'time': 'O(n)', 'space': 'O(1)'},
            # Date/time - O(1)
            'time': {'time': 'O(1)', 'space': 'O(1)'},
            'date': {'time': 'O(1)', 'space': 'O(1)'},
            'date_diff': {'time': 'O(1)', 'space': 'O(1)'},
            # Random - O(1)
            'random_int': {'time': 'O(1)', 'space': 'O(1)'},
            'random_choice': {'time': 'O(1)', 'space': 'O(1)'},
            # File I/O - O(n)
            'read_file': {'time': 'O(n)', 'space': 'O(n)'},
            'write_file': {'time': 'O(n)', 'space': 'O(1)'},
            'append_file': {'time': 'O(n)', 'space': 'O(1)'},
            'file_exists': {'time': 'O(1)', 'space': 'O(1)'},
            'read_csv': {'time': 'O(n)', 'space': 'O(n)'},
            'write_csv': {'time': 'O(n)', 'space': 'O(1)'},
            # TUI - O(n)
            'box': {'time': 'O(n)', 'space': 'O(n)'},
            'line': {'time': 'O(n)', 'space': 'O(n)'},
            'banner': {'time': 'O(n)', 'space': 'O(n)'},
            'center_text': {'time': 'O(n)', 'space': 'O(n)'},
            'pad_text': {'time': 'O(n)', 'space': 'O(n)'},
            'progress_bar': {'time': 'O(n)', 'space': 'O(n)'},
            'menu': {'time': 'O(n)', 'space': 'O(n)'},
            'table_display': {'time': 'O(n)', 'space': 'O(n)'},
            'divider': {'time': 'O(n)', 'space': 'O(n)'},
            # I/O
            'display': {'time': 'O(1)', 'space': 'O(1)'},
            'input': {'time': 'O(1)', 'space': 'O(n)'},
        }

        # Steps syntax patterns
        self.patterns = {
            'loop': [
                r'^\s*repeat\s+\d+\s+times\s*$',
                r'^\s*repeat\s+\w+\s+times\s*$',
                r'^\s*repeat\s+for\s+each\s+',
                r'^\s*repeat\s+while\s+',
            ],
            'step_def': [
                r'^\s*step:\s*(\w+)',
            ],
            'riser_def': [
                r'^\s*riser:\s*(\w+)',
            ],
            'step_call': [
                r'^\s*call\s+(\w+)',
            ],
            'data_structure': [
                r'\[.*\]',
                r'\[.*:.*\]',
            ],
            'string_operations': [
                r'\badded\s+to\b',
                r'\blength\s+of\b',
                r'\bcontains\b',
                r'\bstarts\s+with\b',
                r'\bends\s+with\b',
                r'\bsplit\s+by\b',
                r'\bcharacter\s+at\b',
            ],
            'control_flow': [
                r'^\s*if\b',
                r'^\s*otherwise\s+if\b',
                r'^\s*otherwise\s*$',
            ],
            'error_handling': [
                r'^\s*attempt:\s*$',
                r'^\s*if\s+unsuccessful:\s*$',
            ],
        }

    def get_language_name(self) -> str:
        """Get the language name."""
        return 'steps'

    def parse_code(self, code: str) -> List[str]:
        """
        Parse Steps code into lines for analysis.

        Args:
            code: Steps source code

        Returns:
            List of code lines

        Raises:
            SyntaxError: If code has obvious syntax errors
        """
        lines = code.splitlines()
        self._validate_steps_syntax(lines)
        return lines

    def analyze_structure(self, parsed_code: List[str]) -> List[ComplexityResult]:
        """
        Analyze Steps code lines for complexity patterns.

        Args:
            parsed_code: List of code lines

        Returns:
            List of complexity analysis results
        """
        results = []

        # Track nesting levels, step names, and context
        nesting_stack = []
        step_names = set()
        in_comment_block = False

        for line_num, line in enumerate(parsed_code, 1):
            stripped = line.strip()

            # Handle block comments (note block: ... end note)
            if re.search(r'^\s*note\s+block:', stripped):
                in_comment_block = True
                continue
            if in_comment_block:
                if re.search(r'^\s*end\s+note\b', stripped):
                    in_comment_block = False
                continue

            # Skip empty lines and single-line comments
            if not stripped or stripped.startswith('note:'):
                continue

            # Analyze different patterns
            self._analyze_loops(line, line_num, len(nesting_stack), results)
            self._analyze_step_definitions(line, line_num, step_names, results)
            self._analyze_step_calls(line, line_num, step_names, len(nesting_stack) > 0, results)
            self._analyze_data_structures(line, line_num, results)
            self._analyze_string_operations(line, line_num, results)
            self._analyze_error_handling(line, line_num, results)

            # Track nesting via indentation
            self._update_nesting_stack(line, nesting_stack)

        return results

    def _validate_steps_syntax(self, lines: List[str]):
        """Basic Steps syntax validation."""
        in_comment_block = False

        for _line_num, line in enumerate(lines, 1):
            stripped = line.strip()

            # Track block comments
            if re.search(r'^\s*note\s+block:', stripped):
                in_comment_block = True
                continue
            if in_comment_block:
                if re.search(r'^\s*end\s+note\b', stripped):
                    in_comment_block = False
                continue

            if not stripped or stripped.startswith('note:'):
                continue

            # Check indentation is a multiple of 4 spaces (Steps convention)
            if line and not line.startswith(' ') is False:
                leading_spaces = len(line) - len(line.lstrip(' '))
                if leading_spaces > 0 and leading_spaces % 4 != 0:
                    # Allow non-standard indentation without raising errors
                    pass

        # Don't raise errors for unmatched keywords - be lenient like other analyzers

    def _analyze_loops(self, line: str, line_num: int, depth: int, results: List[ComplexityResult]):
        """Analyze loop constructs."""
        for pattern in self.patterns['loop']:
            if re.search(pattern, line):
                # Determine loop type for description
                if 'for each' in line:
                    loop_type = "repeat for each"
                elif 'while' in line:
                    loop_type = "repeat while"
                else:
                    loop_type = "repeat N times"

                # Determine complexity based on nesting depth
                if depth == 0:
                    time_complexity = 'O(n)'
                    description = f"Single loop ({loop_type}) - linear time complexity"
                elif depth == 1:
                    time_complexity = 'O(n²)'
                    description = f"Nested loop ({loop_type}) - quadratic time complexity"
                else:
                    time_complexity = f'O(n^{depth + 1})'
                    description = f"Deeply nested loop ({loop_type}, depth {depth + 1}) - polynomial time"

                result = ComplexityResult(
                    time_complexity=time_complexity,
                    space_complexity='O(1)',
                    line_number=line_num,
                    description=description,
                    analysis_type="Loop",
                    confidence=0.85,
                    suggestions=self._get_loop_suggestions(depth, loop_type)
                )
                results.append(result)
                break

    def _analyze_step_definitions(self, line: str, line_num: int, step_names: set,
                                  results: List[ComplexityResult]):
        """Analyze step and riser definitions."""
        # Check for step definitions
        for pattern in self.patterns['step_def']:
            match = re.search(pattern, line)
            if match:
                step_name = match.group(1)
                step_names.add(step_name)
                return

        # Check for riser definitions
        for pattern in self.patterns['riser_def']:
            match = re.search(pattern, line)
            if match:
                riser_name = match.group(1)
                step_names.add(riser_name)
                return

    def _analyze_step_calls(self, line: str, line_num: int, step_names: set,
                            in_loop: bool, results: List[ComplexityResult]):
        """Analyze step calls including built-in functions and recursion."""
        for pattern in self.patterns['step_call']:
            match = re.search(pattern, line)
            if match:
                func_name = match.group(1)

                # Check for built-in function calls
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
                        description=f"Built-in function 'call {func_name}'",
                        analysis_type="Built-in Function",
                        confidence=0.9,
                        suggestions=self._get_builtin_suggestions(func_name, in_loop)
                    )
                    results.append(result)

                # Check for potential recursion (calling a step defined in this scope)
                elif func_name in step_names:
                    result = ComplexityResult(
                        time_complexity='O(2ⁿ)',
                        space_complexity='O(n)',
                        line_number=line_num,
                        description=f"Potential recursive call to step '{func_name}'",
                        analysis_type="Recursion",
                        confidence=0.6,
                        suggestions=[
                            f"If '{func_name}' calls itself, consider memoization",
                            "Consider an iterative approach to reduce stack depth",
                            "Use 'repeat' loops instead of recursion when possible"
                        ]
                    )
                    results.append(result)
                break

    def _analyze_data_structures(self, line: str, line_num: int, results: List[ComplexityResult]):
        """Analyze data structure operations."""
        stripped = line.strip()

        # List/table creation with literal syntax
        if re.search(r'\[.*:.*\]', stripped) and not stripped.startswith('note'):
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
        elif re.search(r'\[.+\]', stripped) and not stripped.startswith('note'):
            result = ComplexityResult(
                time_complexity='O(n)',
                space_complexity='O(n)',
                line_number=line_num,
                description="List creation",
                analysis_type="Data Structure",
                confidence=0.8,
                suggestions=["Consider memory usage for large lists"]
            )
            results.append(result)

        # List modification operations: add X to Y / remove X from Y
        if re.search(r'^\s*add\s+.+\s+to\s+', stripped):
            result = ComplexityResult(
                time_complexity='O(1)',
                space_complexity='O(1)',
                line_number=line_num,
                description="List append operation",
                analysis_type="Data Structure",
                confidence=0.85,
                suggestions=["Appending to a list is typically O(1) amortized"]
            )
            results.append(result)
        elif re.search(r'^\s*remove\s+.+\s+from\s+', stripped):
            result = ComplexityResult(
                time_complexity='O(n)',
                space_complexity='O(1)',
                line_number=line_num,
                description="List removal operation",
                analysis_type="Data Structure",
                confidence=0.8,
                suggestions=["Removing from a list may require shifting elements"]
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

    def _analyze_error_handling(self, line: str, line_num: int, results: List[ComplexityResult]):
        """Analyze error handling constructs."""
        if re.search(r'^\s*attempt:\s*$', line):
            result = ComplexityResult(
                time_complexity='O(1)',
                space_complexity='O(1)',
                line_number=line_num,
                description="Error handling block (attempt:/if unsuccessful:)",
                analysis_type="Error Handling",
                confidence=0.9,
                suggestions=["Error handling is good practice for robust code"]
            )
            results.append(result)

    def _update_nesting_stack(self, line: str, nesting_stack: List[str]):
        """
        Update nesting stack based on indentation changes.

        Steps uses 4-space indentation for nesting. We track blocks that
        increase nesting: loops, if/otherwise, attempt, step/riser bodies.
        """
        stripped = line.strip()
        if not stripped:
            return

        # Calculate indentation level (number of 4-space indents)
        leading_spaces = len(line) - len(line.lstrip(' '))
        indent_level = leading_spaces // 4

        # Pop stack entries that are at or above the current indent level
        while len(nesting_stack) > indent_level:
            nesting_stack.pop()

        # Push for constructs that start a new nesting level
        if re.search(r'^\s*repeat\s+', stripped):
            nesting_stack.append('repeat')
        elif re.search(r'^\s*if\b', stripped):
            nesting_stack.append('if')
        elif re.search(r'^\s*attempt:', stripped):
            nesting_stack.append('attempt')

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

    def _get_loop_suggestions(self, depth: int, loop_type: str) -> List[str]:
        """Get optimization suggestions for loops."""
        suggestions = []
        if depth == 0:
            suggestions.append("Consider if the loop body can be optimized")
        elif depth == 1:
            suggestions.extend([
                "Consider if the inner loop can be eliminated",
                "Look for opportunities to use table lookups for O(1) access",
                "Consider breaking nested logic into separate steps"
            ])
        else:
            suggestions.extend([
                "Deeply nested loops indicate potential for significant optimization",
                "Consider breaking down into separate steps or risers",
                "Look for algorithmic improvements to reduce nesting"
            ])

        if loop_type == "repeat while":
            suggestions.append("Ensure the while condition will eventually be false to avoid infinite loops")

        return suggestions

    def _get_builtin_suggestions(self, func_name: str, in_loop: bool) -> List[str]:
        """Get suggestions for built-in function usage."""
        suggestions = []
        if in_loop:
            suggestions.append(f"'call {func_name}' inside a loop increases overall complexity")

        # Specific suggestions for certain functions
        if func_name in ['list_min', 'list_max', 'list_sum']:
            suggestions.append(f"'{func_name}' scans the entire list - O(n) per call")
        if func_name in ['read_file', 'read_csv']:
            suggestions.append(f"File I/O with '{func_name}' can be slow for large files")
            if in_loop:
                suggestions.append("Consider reading the file once outside the loop")
        if func_name == 'replace':
            suggestions.append("'replace' scans the entire string for matches")
        if func_name in ['reverse', 'characters']:
            suggestions.append(f"'{func_name}' creates a new copy of the data")

        return suggestions
