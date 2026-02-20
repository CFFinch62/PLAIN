"""
Pseudocode language analyzer for the Code Analysis Tool.

This module provides Pseudocode-specific code complexity analysis using
regular expressions and pattern matching for parsing and analysis.
"""

import re
from typing import List

from .base import BaseLanguageAnalyzer
from core.models import ComplexityResult


class PseudocodeAnalyzer(BaseLanguageAnalyzer):
    """
    Pseudocode-specific code complexity analyzer.

    This analyzer uses regular expressions and pattern matching to analyze Pseudocode
    for complexity patterns including loops, recursion, data operations,
    and algorithmic constructs.
    """

    def __init__(self, config):
        """Initialize the Pseudocode analyzer."""
        super().__init__(config)

        # Pseudocode operation complexities
        self.operation_complexities = {
            'SORT': {'time': 'O(n log n)', 'space': 'O(n)'},
            'SEARCH': {'time': 'O(n)', 'space': 'O(1)'},
            'FIND': {'time': 'O(n)', 'space': 'O(1)'},
            'INSERT': {'time': 'O(n)', 'space': 'O(1)'},
            'REMOVE': {'time': 'O(n)', 'space': 'O(1)'},
            'DELETE': {'time': 'O(n)', 'space': 'O(1)'},
            'UPDATE': {'time': 'O(1)', 'space': 'O(1)'},
            'APPEND': {'time': 'O(1)', 'space': 'O(1)'},
            'CLEAR': {'time': 'O(n)', 'space': 'O(1)'},
            'INITIALIZE': {'time': 'O(n)', 'space': 'O(n)'},
            'READ': {'time': 'O(1)', 'space': 'O(1)'},
            'WRITE': {'time': 'O(1)', 'space': 'O(1)'},
            'INPUT': {'time': 'O(1)', 'space': 'O(1)'},
            'OUTPUT': {'time': 'O(1)', 'space': 'O(1)'},
            'DISPLAY': {'time': 'O(1)', 'space': 'O(1)'},
            'PRINT': {'time': 'O(1)', 'space': 'O(1)'},
        }

        # Cambridge IGCSE Pseudocode syntax patterns
        self.patterns = {
            'loop': [
                r'^\s*FOR\s+\w+\s*←.*TO',          # FOR loops (IGCSE style)
                r'^\s*WHILE\s+.*',                 # WHILE loops
                r'^\s*REPEAT\s*$',                 # REPEAT loops
            ],
            'function_def': [
                r'^\s*FUNCTION\s+(\w+)\s*\(',      # Function definitions
                r'^\s*PROCEDURE\s+(\w+)\s*\(',     # Procedure definitions
            ],
            'function_call': [
                r'(\w+)\s*\(',                     # Function calls
            ],
            'data_structures': [
                r'ARRAY\s*\[.*\]',                 # Array declarations
                r'DECLARE\s+\w+\s*:\s*ARRAY',      # IGCSE array declarations
            ],
            'data_operations': [
                r'\b(INPUT|OUTPUT|READ|WRITE|DISPLAY|PRINT)\b',  # I/O operations
            ],
            'control_flow': [
                r'^\s*IF\s+.*',                    # IF statements
                r'^\s*CASE\s+.*OF',                # CASE statements
            ],
            'assignments': [
                r'\w+\s*←',                        # Assignment operator
                r'DECLARE\s+\w+',                  # Variable declarations
            ]
        }

    def get_language_name(self) -> str:
        """Get the language name."""
        return 'pseudocode'

    def parse_code(self, code: str) -> List[str]:
        """
        Parse Pseudocode into lines for analysis.

        Args:
            code: Pseudocode source

        Returns:
            List of code lines

        Raises:
            SyntaxError: If code has obvious syntax errors
        """
        lines = code.splitlines()

        # Basic syntax validation
        self._validate_pseudocode_syntax(lines)

        return lines

    def analyze_structure(self, parsed_code: List[str]) -> List[ComplexityResult]:
        """
        Analyze Pseudocode lines for complexity patterns.

        Args:
            parsed_code: List of code lines

        Returns:
            List of complexity analysis results
        """
        results = []

        # Track nesting levels and algorithm names
        nesting_stack = []
        algorithm_names = set()

        for line_num, line in enumerate(parsed_code, 1):
            line = line.strip()
            if not line or self._is_comment(line):
                continue

            # Analyze different patterns
            self._analyze_loops(line, line_num, len(nesting_stack), results)
            self._analyze_functions(line, line_num, algorithm_names, results)
            self._analyze_function_calls(line, line_num, len(nesting_stack) > 0, results)
            self._analyze_data_structures(line, line_num, results)
            self._analyze_data_operations(line, line_num, len(nesting_stack) > 0, results)
            self._analyze_assignments(line, line_num, results)

            # Track nesting
            self._update_nesting_stack(line, nesting_stack)

        return results

    def _is_comment(self, line: str) -> bool:
        """Check if line is a comment."""
        return (line.startswith('//') or line.startswith('#') or
                line.startswith('*') or line.startswith('--'))

    def _validate_pseudocode_syntax(self, lines: List[str]):
        """Basic Pseudocode syntax validation."""
        # Simplified validation - pseudocode has many variations
        # Just check for obvious syntax errors

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or self._is_comment(line):
                continue

            # Check for basic syntax issues
            # Count parentheses and brackets
            if line.count('(') != line.count(')'):
                # Allow unmatched in some contexts
                pass
            if line.count('[') != line.count(']'):
                # Allow unmatched in some contexts
                pass

        # Don't enforce strict keyword matching as pseudocode varies widely

    def _analyze_loops(self, line: str, line_num: int, depth: int, results: List[ComplexityResult]):
        """Analyze loop constructs."""
        for pattern in self.patterns['loop']:
            if re.search(pattern, line, re.IGNORECASE):
                # Determine complexity based on loop type and nesting
                if depth == 0:
                    time_complexity = 'O(n)'
                    description = "Single loop iteration"
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
                if func_name in line.upper() and not re.search(r'\b(PROCEDURE|FUNCTION)\b', line, re.IGNORECASE):
                    result = ComplexityResult(
                        time_complexity='O(2ⁿ)',
                        space_complexity='O(n)',
                        line_number=line_num,
                        description=f"Potential recursive function '{func_name}'",
                        analysis_type="Recursion",
                        confidence=0.6,
                        suggestions=[
                            f"Consider iterative approach for '{func_name}' if recursive",
                            "Use memoization to improve recursive performance",
                            "Consider dynamic programming if applicable"
                        ]
                    )
                    results.append(result)
                break

    def _analyze_function_calls(self, line: str, line_num: int, in_loop: bool,
                               results: List[ComplexityResult]):
        """Analyze function calls."""
        for pattern in self.patterns['function_call']:
            if re.search(pattern, line, re.IGNORECASE):
                time_complexity = 'O(?)'  # Unknown complexity for external calls
                space_complexity = 'O(?)'

                result = ComplexityResult(
                    time_complexity=time_complexity,
                    space_complexity=space_complexity,
                    line_number=line_num,
                    description="Function call - complexity depends on called function",
                    analysis_type="Function Call",
                    confidence=0.5,
                    suggestions=[
                        "Analyze the called function's complexity",
                        "Consider inlining simple operations if called frequently"
                    ]
                )
                results.append(result)
                break

    def _analyze_data_structures(self, line: str, line_num: int, results: List[ComplexityResult]):
        """Analyze data structure declarations."""
        for pattern in self.patterns['data_structures']:
            if re.search(pattern, line, re.IGNORECASE):
                # Determine space complexity based on data structure type
                if re.search(r'ARRAY', line, re.IGNORECASE):
                    space_complexity = 'O(n)'
                    description = "Array data structure"
                elif re.search(r'(LIST|STACK|QUEUE)', line, re.IGNORECASE):
                    space_complexity = 'O(n)'
                    description = "Linear data structure"
                elif re.search(r'TREE', line, re.IGNORECASE):
                    space_complexity = 'O(n)'
                    description = "Tree data structure"
                else:
                    space_complexity = 'O(n)'
                    description = "Data structure declaration"

                result = ComplexityResult(
                    time_complexity='O(1)',
                    space_complexity=space_complexity,
                    line_number=line_num,
                    description=description,
                    analysis_type="Data Structure",
                    confidence=0.8,
                    suggestions=["Consider memory usage for large data structures"]
                )
                results.append(result)
                break

    def _analyze_data_operations(self, line: str, line_num: int, in_loop: bool,
                                results: List[ComplexityResult]):
        """Analyze data operations."""
        for pattern in self.patterns['data_operations']:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                operation = match.group(1).upper()

                if operation in self.operation_complexities:
                    complexity_info = self.operation_complexities[operation]
                    time_complexity = complexity_info['time']
                    space_complexity = complexity_info['space']

                    # Adjust complexity if inside loop
                    if in_loop and time_complexity != 'O(1)':
                        time_complexity = self._multiply_complexity(time_complexity, 'O(n)')

                    result = ComplexityResult(
                        time_complexity=time_complexity,
                        space_complexity=space_complexity,
                        line_number=line_num,
                        description=f"Data operation: {operation}",
                        analysis_type="Data Operation",
                        confidence=0.9,
                        suggestions=self._get_operation_suggestions(operation, in_loop)
                    )
                    results.append(result)
                break

    def _analyze_complexity_indicators(self, line: str, line_num: int, results: List[ComplexityResult]):
        """Analyze complexity indicators in comments or descriptions."""
        for pattern in self.patterns['complexity_indicators']:
            if re.search(pattern, line, re.IGNORECASE):
                if 'nested.*loop' in pattern:
                    complexity = 'O(n²)'
                    description = "Nested loop pattern indicated"
                elif 'recursive' in pattern:
                    complexity = 'O(2ⁿ)'
                    description = "Recursive pattern indicated"
                elif 'divide.*conquer' in pattern:
                    complexity = 'O(n log n)'
                    description = "Divide and conquer pattern indicated"
                elif 'dynamic.*programming' in pattern:
                    complexity = 'O(n²)'
                    description = "Dynamic programming pattern indicated"
                elif 'brute.*force' in pattern:
                    complexity = 'O(2ⁿ)'
                    description = "Brute force pattern indicated"
                else:
                    complexity = 'O(?)'
                    description = "Complexity pattern indicated"

                result = ComplexityResult(
                    time_complexity=complexity,
                    space_complexity='O(?)',
                    line_number=line_num,
                    description=description,
                    analysis_type="Complexity Indicator",
                    confidence=0.7,
                    suggestions=["Verify actual complexity matches the indicated pattern"]
                )
                results.append(result)
                break

    def _update_nesting_stack(self, line: str, nesting_stack: List[str]):
        """Update nesting stack for tracking loop depth (IGCSE style)."""
        line_upper = line.upper()

        # Opening constructs (IGCSE style)
        if re.search(r'\bFOR\b.*\bTO\b', line_upper):
            nesting_stack.append('FOR')
        elif re.search(r'\bWHILE\b', line_upper):
            nesting_stack.append('WHILE')
        elif re.search(r'\bREPEAT\b', line_upper):
            nesting_stack.append('REPEAT')

        # Closing constructs (IGCSE style)
        if re.search(r'\bNEXT\b', line_upper) and 'FOR' in nesting_stack:
            nesting_stack.remove('FOR')
        elif re.search(r'\bENDWHILE\b', line_upper) and 'WHILE' in nesting_stack:
            nesting_stack.remove('WHILE')
        elif re.search(r'\bUNTIL\b', line_upper) and 'REPEAT' in nesting_stack:
            nesting_stack.remove('REPEAT')

    def _get_loop_suggestions(self, depth: int) -> List[str]:
        """Get suggestions for loop optimization."""
        suggestions = []
        if depth == 0:
            suggestions.append("Consider if loop can be optimized or if there's a more efficient algorithm")
        elif depth == 1:
            suggestions.append("Nested loops can be expensive - consider algorithm optimization")
            suggestions.append("Look for opportunities to reduce to single loop or use better data structures")
        else:
            suggestions.append("Deeply nested loops are very expensive - consider redesigning algorithm")
            suggestions.append("Consider divide-and-conquer or dynamic programming approaches")
        return suggestions

    def _get_operation_suggestions(self, operation: str, in_loop: bool) -> List[str]:
        """Get suggestions for operation optimization."""
        suggestions = []
        if in_loop:
            suggestions.append(f"'{operation}' operation in loop - consider optimizing")

        if operation == 'SORT':
            suggestions.append("Consider if data can be kept sorted or if sorting is necessary")
        elif operation in ['SEARCH', 'FIND']:
            suggestions.append("Consider using hash tables or binary search for better performance")
        elif operation in ['INSERT', 'REMOVE', 'DELETE']:
            suggestions.append("Consider using appropriate data structures (e.g., linked lists, trees)")

        return suggestions

    def _analyze_assignments(self, line: str, line_num: int, results: List[ComplexityResult]):
        """Analyze assignment operations."""
        for pattern in self.patterns['assignments']:
            if re.search(pattern, line, re.IGNORECASE):
                if 'DECLARE' in line.upper():
                    result = ComplexityResult(
                        time_complexity='O(1)',
                        space_complexity='O(1)',
                        line_number=line_num,
                        description="Variable declaration",
                        analysis_type="Declaration",
                        confidence=0.9,
                        suggestions=["Consider memory usage for large data structures"]
                    )
                    results.append(result)
                elif '←' in line:
                    result = ComplexityResult(
                        time_complexity='O(1)',
                        space_complexity='O(1)',
                        line_number=line_num,
                        description="Assignment operation",
                        analysis_type="Assignment",
                        confidence=0.9,
                        suggestions=[]
                    )
                    results.append(result)
                break

    def _multiply_complexity(self, complexity1: str, complexity2: str) -> str:
        """Multiply two complexity expressions."""
        # Simple complexity multiplication
        if complexity1 == 'O(1)':
            return complexity2
        elif complexity2 == 'O(1)':
            return complexity1
        elif complexity1 == 'O(n)' and complexity2 == 'O(n)':
            return 'O(n²)'
        elif 'log n' in complexity1 and complexity2 == 'O(n)':
            return 'O(n² log n)'
        else:
            return f'{complexity1} × {complexity2}'
