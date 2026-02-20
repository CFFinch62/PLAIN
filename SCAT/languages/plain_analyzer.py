"""
PLAIN language analyzer for the Code Analysis Tool.

This module provides PLAIN-specific code complexity analysis using
regular expressions and pattern matching for parsing and analysis.
"""

import re
from typing import List, Any, Dict, Tuple

from .base import BaseLanguageAnalyzer
from core.models import ComplexityResult


class PlainAnalyzer(BaseLanguageAnalyzer):
    """
    PLAIN-specific code complexity analyzer.

    This analyzer uses regular expressions and pattern matching to analyze PLAIN code
    for complexity patterns including loops, recursion, built-in functions,
    data structures, and task operations.
    """

    def __init__(self, config):
        """Initialize the PLAIN analyzer."""
        super().__init__(config)

        # PLAIN built-in function complexities
        self.builtin_complexities = {
            'len': {'time': 'O(1)', 'space': 'O(1)'},
            'append': {'time': 'O(1)', 'space': 'O(1)'},
            'insert': {'time': 'O(n)', 'space': 'O(1)'},
            'remove': {'time': 'O(n)', 'space': 'O(1)'},
            'pop': {'time': 'O(1)', 'space': 'O(1)'},
            'contains': {'time': 'O(n)', 'space': 'O(1)'},
            'sort': {'time': 'O(n log n)', 'space': 'O(n)'},
            'reverse': {'time': 'O(n)', 'space': 'O(1)'},
            'min': {'time': 'O(n)', 'space': 'O(1)'},
            'max': {'time': 'O(n)', 'space': 'O(1)'},
            'sum': {'time': 'O(n)', 'space': 'O(1)'},
            'keys': {'time': 'O(n)', 'space': 'O(n)'},
            'values': {'time': 'O(n)', 'space': 'O(n)'},
            'has_key': {'time': 'O(1)', 'space': 'O(1)'},
            'display': {'time': 'O(n)', 'space': 'O(1)'},
            'get': {'time': 'O(n)', 'space': 'O(n)'},
            'to_int': {'time': 'O(1)', 'space': 'O(1)'},
            'to_float': {'time': 'O(1)', 'space': 'O(1)'},
            'to_string': {'time': 'O(n)', 'space': 'O(n)'},
            'time': {'time': 'O(1)', 'space': 'O(1)'},
        }

        # PLAIN syntax patterns
        self.patterns = {
            'loop_counting': [
                r'^\s*loop\s+\w+\s+from\s+',  # loop i from 1 to 10
            ],
            'loop_collection': [
                r'^\s*loop\s+\w+\s+in\s+',  # loop item in collection
            ],
            'loop_conditional': [
                r'^\s*loop\s+[^f][^r][^o][^m]',  # loop condition (not 'from')
            ],
            'loop_infinite': [
                r'^\s*loop\s*$',  # loop (infinite)
            ],
            'task_def': [
                r'^\s*task\s+(\w+)\s*\(',  # task Name()
                r'^\s*task\s+(\w+)\s+with\s*\(',  # task Name with (params)
                r'^\s*task\s+(\w+)\s+using\s*\(',  # task Name using (inputs)
            ],
            'task_call': [
                r'([A-Z]\w*)\s*\(',  # TaskName( - PascalCase function call
            ],
            'list_creation': [
                r'\[.*\]',  # [1, 2, 3]
            ],
            'table_creation': [
                r'\{.*:.*\}',  # {"key": "value"}
            ],
            'string_operations': [
                r'&',  # String concatenation
                r'v"',  # String interpolation v"text {var}"
            ],
        }

    def get_language_name(self) -> str:
        """Get the language name."""
        return 'plain'

    def parse_code(self, code: str) -> List[str]:
        """
        Parse PLAIN code into lines for analysis.

        Args:
            code: PLAIN source code

        Returns:
            List of code lines

        Raises:
            SyntaxError: If code has obvious syntax errors
        """
        lines = code.splitlines()

        # Basic syntax validation
        self._validate_plain_syntax(lines)

        return lines

    def analyze_structure(self, parsed_code: List[str]) -> List[ComplexityResult]:
        """
        Analyze PLAIN code lines for complexity patterns.

        Args:
            parsed_code: List of code lines

        Returns:
            List of complexity analysis results
        """
        results = []

        # Track nesting levels and task names using indentation
        task_names = set()
        previous_indent = 0
        loop_depth = 0

        for line_num, line in enumerate(parsed_code, 1):
            line_stripped = line.strip()
            if not line_stripped or line_stripped.startswith('rem:') or line_stripped.startswith('note:'):
                continue

            # Calculate indentation level (spaces or tabs)
            current_indent = len(line) - len(line.lstrip())

            # Detect if we're exiting nested blocks (dedent)
            if current_indent < previous_indent:
                # We've dedented - reduce loop depth
                indent_diff = previous_indent - current_indent
                # Rough heuristic: each 4 spaces is one level
                levels_exited = max(1, indent_diff // 4)
                loop_depth = max(0, loop_depth - levels_exited)

            # Check if this line starts a loop
            is_loop_line = any(re.search(pattern, line_stripped) for pattern in
                             self.patterns['loop_counting'] +
                             self.patterns['loop_collection'] +
                             self.patterns['loop_conditional'] +
                             self.patterns['loop_infinite'])

            # Analyze different patterns
            self._analyze_loops(line_stripped, line_num, loop_depth, results)
            self._analyze_tasks(line_stripped, line_num, task_names, results)
            self._analyze_task_calls(line_stripped, line_num, task_names, loop_depth > 0, results)
            self._analyze_collections(line_stripped, line_num, results)
            self._analyze_builtin_calls(line_stripped, line_num, loop_depth > 0, results)

            # Update loop depth if this line starts a loop
            if is_loop_line:
                loop_depth += 1

            previous_indent = current_indent

        return results

    def _validate_plain_syntax(self, lines: List[str]):
        """Basic PLAIN syntax validation."""
        # PLAIN uses indentation-based blocks, not explicit 'end' keywords
        # Just do basic validation for now

        # Check for common syntax issues
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith('rem:') or stripped.startswith('note:'):
                continue

            # Check for basic task syntax
            if stripped.startswith('task '):
                # Task must have parentheses
                if '(' not in stripped:
                    raise SyntaxError(f"Line {line_num}: Task definition missing parentheses")

        # Validation passed
        return True

    def _analyze_loops(self, line: str, line_num: int, nesting_depth: int, results: List[ComplexityResult]):
        """Analyze loop complexity."""
        is_loop = False
        loop_type = ""

        # Check for counting loop (from...to)
        if any(re.search(pattern, line) for pattern in self.patterns['loop_counting']):
            is_loop = True
            loop_type = "Counting loop (from...to)"

        # Check for collection loop (in)
        elif any(re.search(pattern, line) for pattern in self.patterns['loop_collection']):
            is_loop = True
            loop_type = "Collection loop (for-each)"

        # Check for conditional loop
        elif any(re.search(pattern, line) for pattern in self.patterns['loop_conditional']):
            is_loop = True
            loop_type = "Conditional loop (while-style)"

        # Check for infinite loop
        elif any(re.search(pattern, line) for pattern in self.patterns['loop_infinite']):
            is_loop = True
            loop_type = "Infinite loop"

        if is_loop:
            # Time complexity based on nesting depth
            if nesting_depth == 0:
                time_complexity = 'O(n)'
                time_desc = f"{loop_type} - linear time complexity"
                suggestions = []
            elif nesting_depth == 1:
                time_complexity = 'O(n²)'
                time_desc = f"Nested {loop_type.lower()} - quadratic time complexity"
                suggestions = ["Consider using hash tables or optimizing nested loops"]
            else:
                time_complexity = f'O(n^{nesting_depth + 1})'
                time_desc = f"Multiple nested loops (depth {nesting_depth + 1}) - polynomial time complexity"
                suggestions = ["Consider algorithm optimization to reduce nesting depth"]

            # Space complexity
            space_complexity = 'O(1)'
            space_desc = "Loop variables use constant space"

            result = ComplexityResult(
                time_complexity=time_complexity,
                space_complexity=space_complexity,
                line_number=line_num,
                description=f"{time_desc}. {space_desc}",
                analysis_type='Loop',
                confidence=0.95,
                suggestions=suggestions
            )
            results.append(result)

    def _analyze_tasks(self, line: str, line_num: int, task_names: set, results: List[ComplexityResult]):
        """Analyze task definitions."""
        for pattern in self.patterns['task_def']:
            match = re.search(pattern, line)
            if match:
                task_name = match.group(1)
                task_names.add(task_name)

                # Determine task type
                if 'using' in line:
                    task_type = "Function task (returns value)"
                elif 'with' in line:
                    task_type = "Procedure task (with parameters)"
                else:
                    task_type = "Simple task (no parameters)"

                result = ComplexityResult(
                    time_complexity='O(1)',
                    space_complexity='O(1)',
                    line_number=line_num,
                    description=f"{task_type} definition: {task_name}",
                    analysis_type='Task Definition',
                    confidence=1.0,
                    suggestions=[]
                )
                results.append(result)
                break

    def _analyze_task_calls(self, line: str, line_num: int, task_names: set,
                           in_loop: bool, results: List[ComplexityResult]):
        """Analyze task calls for potential recursion."""
        for pattern in self.patterns['task_call']:
            matches = re.finditer(pattern, line)
            for match in matches:
                task_name = match.group(1)

                # Check if this is a recursive call
                if task_name in task_names:
                    # Potential recursion detected
                    time_complexity = 'O(2ⁿ)'
                    space_complexity = 'O(n)'
                    description = f"Recursive call to {task_name} - exponential complexity possible"
                    suggestions = [
                        "Consider memoization or dynamic programming for recursive tasks",
                        "Verify base cases to prevent infinite recursion"
                    ]
                    confidence = 0.85
                else:
                    # Regular task call
                    if in_loop:
                        time_complexity = 'O(n)'
                        description = f"Task call to {task_name} inside loop"
                        suggestions = ["Verify task complexity doesn't compound loop complexity"]
                        confidence = 0.75
                    else:
                        time_complexity = 'O(1)'
                        description = f"Task call to {task_name}"
                        suggestions = []
                        confidence = 0.9

                    space_complexity = 'O(1)'

                result = ComplexityResult(
                    time_complexity=time_complexity,
                    space_complexity=space_complexity,
                    line_number=line_num,
                    description=description,
                    analysis_type='Task Call',
                    confidence=confidence,
                    suggestions=suggestions
                )
                results.append(result)

    def _analyze_collections(self, line: str, line_num: int, results: List[ComplexityResult]):
        """Analyze list and table creation."""
        # Check for list creation
        if any(re.search(pattern, line) for pattern in self.patterns['list_creation']):
            # Estimate list size (rough heuristic)
            list_match = re.search(r'\[(.*?)\]', line)
            if list_match:
                content = list_match.group(1)
                if content.strip():
                    # Non-empty list
                    result = ComplexityResult(
                        time_complexity='O(n)',
                        space_complexity='O(n)',
                        line_number=line_num,
                        description="List creation - linear time and space",
                        analysis_type='Data Structure',
                        confidence=0.9,
                        suggestions=[]
                    )
                    results.append(result)

        # Check for table creation
        if any(re.search(pattern, line) for pattern in self.patterns['table_creation']):
            result = ComplexityResult(
                time_complexity='O(n)',
                space_complexity='O(n)',
                line_number=line_num,
                description="Table (dictionary) creation - linear time and space",
                analysis_type='Data Structure',
                confidence=0.9,
                suggestions=[]
            )
            results.append(result)

    def _analyze_builtin_calls(self, line: str, line_num: int, in_loop: bool,
                               results: List[ComplexityResult]):
        """Analyze built-in function calls."""
        for func_name, complexity in self.builtin_complexities.items():
            # Match function calls like: func_name(
            pattern = rf'\b{func_name}\s*\('
            if re.search(pattern, line):
                time_complexity = complexity['time']
                space_complexity = complexity['space']

                # Adjust if inside a loop
                if in_loop and time_complexity != 'O(1)':
                    description = f"Built-in function '{func_name}' called in loop - complexity may compound"
                    suggestions = [f"Consider moving '{func_name}' outside loop if possible"]
                else:
                    description = f"Built-in function '{func_name}' - {self.time_patterns.get(time_complexity, {}).get('description', 'standard complexity')}"
                    suggestions = []

                result = ComplexityResult(
                    time_complexity=time_complexity,
                    space_complexity=space_complexity,
                    line_number=line_num,
                    description=description,
                    analysis_type='Built-in Function',
                    confidence=0.95,
                    suggestions=suggestions
                )
                results.append(result)




