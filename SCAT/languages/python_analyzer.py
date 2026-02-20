"""
Python language analyzer for the Code Analysis Tool.

This module provides Python-specific code complexity analysis using
the Python AST (Abstract Syntax Tree) module for parsing and analysis.
"""

import ast
from typing import List, Any, Dict

from .base import BaseLanguageAnalyzer
from core.models import ComplexityResult


class PythonAnalyzer(BaseLanguageAnalyzer):
    """
    Python-specific code complexity analyzer.

    This analyzer uses Python's AST module to parse and analyze Python code
    for complexity patterns including loops, recursion, built-in functions,
    data structures, and comprehensions.
    """

    def __init__(self, config):
        """Initialize the Python analyzer."""
        super().__init__(config)

        # Python built-in function complexities
        self.builtin_complexities = {
            'sorted': {'time': 'O(n log n)', 'space': 'O(n)'},
            'max': {'time': 'O(n)', 'space': 'O(1)'},
            'min': {'time': 'O(n)', 'space': 'O(1)'},
            'sum': {'time': 'O(n)', 'space': 'O(1)'},
            'len': {'time': 'O(1)', 'space': 'O(1)'},
            'list': {'time': 'O(n)', 'space': 'O(n)'},
            'dict': {'time': 'O(n)', 'space': 'O(n)'},
            'set': {'time': 'O(n)', 'space': 'O(n)'},
            'tuple': {'time': 'O(n)', 'space': 'O(n)'},
            'reversed': {'time': 'O(n)', 'space': 'O(n)'},
            'enumerate': {'time': 'O(1)', 'space': 'O(1)'},
            'zip': {'time': 'O(1)', 'space': 'O(1)'},
            'filter': {'time': 'O(1)', 'space': 'O(1)'},  # Lazy evaluation
            'map': {'time': 'O(1)', 'space': 'O(1)'},     # Lazy evaluation
            'any': {'time': 'O(n)', 'space': 'O(1)'},
            'all': {'time': 'O(n)', 'space': 'O(1)'},
        }

    def get_language_name(self) -> str:
        """Get the language name."""
        return 'python'

    def parse_code(self, code: str) -> ast.AST:
        """
        Parse Python code into an AST.

        Args:
            code: Python source code

        Returns:
            Python AST object

        Raises:
            SyntaxError: If code has syntax errors
        """
        return ast.parse(code)

    def analyze_structure(self, parsed_code: ast.AST) -> List[ComplexityResult]:
        """
        Analyze Python AST for complexity patterns.

        Args:
            parsed_code: Python AST object

        Returns:
            List of complexity analysis results
        """
        results = []
        analysis_state = {
            'results': results,
            'warnings': [],
            'suggestions': []
        }

        # Analyze the AST starting from the root
        self._analyze_ast_node(parsed_code, analysis_state, depth=0, in_loop=False)

        return results

    def _analyze_ast_node(self, node: ast.AST, state: Dict, depth: int = 0, in_loop: bool = False):
        """Recursively analyze AST nodes for complexity patterns."""
        if isinstance(node, (ast.For, ast.While)):
            self._analyze_loop(node, state, depth, in_loop)
            # Analyze loop body with increased depth
            for child in ast.iter_child_nodes(node):
                self._analyze_ast_node(child, state, depth + 1, True)

        elif isinstance(node, ast.FunctionDef):
            self._analyze_function(node, state, depth)
            # Analyze function body
            for child in ast.iter_child_nodes(node):
                self._analyze_ast_node(child, state, depth, in_loop)

        elif isinstance(node, ast.Call):
            self._analyze_function_call(node, state, depth, in_loop)
            # Analyze call arguments
            for child in ast.iter_child_nodes(node):
                self._analyze_ast_node(child, state, depth, in_loop)

        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            self._analyze_assignment(node, state, depth, in_loop)
            # Analyze assignment value
            for child in ast.iter_child_nodes(node):
                self._analyze_ast_node(child, state, depth, in_loop)

        elif isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp)):
            self._analyze_comprehension(node, state, depth, in_loop)
            # Analyze comprehension components
            for child in ast.iter_child_nodes(node):
                self._analyze_ast_node(child, state, depth, in_loop)

        else:
            # Recursively analyze child nodes
            for child in ast.iter_child_nodes(node):
                self._analyze_ast_node(child, state, depth, in_loop)

    def _analyze_loop(self, node: ast.AST, state: Dict, depth: int, in_loop: bool):
        """Analyze loop complexity (time and space)."""
        line_num = getattr(node, 'lineno', 'Unknown')

        # Time complexity based on nesting depth
        if depth == 0:
            time_complexity = 'O(n)'
            time_desc = "Single loop - linear time complexity"
        elif depth == 1:
            time_complexity = 'O(n²)'
            time_desc = "Nested loop - quadratic time complexity"
        else:
            time_complexity = f'O(n^{depth + 1})'
            time_desc = f"Multiple nested loops (depth {depth + 1}) - polynomial time complexity"

        # Space complexity (loops themselves don't typically add space)
        space_complexity = 'O(1)'
        space_desc = "Loop variables use constant space"

        # Create result
        result = ComplexityResult(
            time_complexity=time_complexity,
            space_complexity=space_complexity,
            line_number=line_num,
            description=f"{time_desc}. {space_desc}",
            analysis_type="Loop",
            confidence=0.9,
            suggestions=self._get_loop_suggestions(depth)
        )

        state['results'].append(result)

    def _analyze_function(self, node: ast.FunctionDef, state: Dict, depth: int):
        """Analyze function definition for recursion."""
        func_name = node.name
        line_num = getattr(node, 'lineno', 'Unknown')

        # Check for recursion
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                if child.func.id == func_name:
                    # Recursive function detected
                    time_complexity = 'O(2ⁿ)'
                    space_complexity = 'O(n)'  # Call stack depth

                    result = ComplexityResult(
                        time_complexity=time_complexity,
                        space_complexity=space_complexity,
                        line_number=line_num,
                        description=f"Recursive function '{func_name}' - exponential time, linear space (call stack)",
                        analysis_type="Recursion",
                        confidence=0.8,
                        suggestions=[
                            f"Consider memoization for '{func_name}' to improve time complexity",
                            f"Consider iterative approach to reduce space complexity",
                            "Use dynamic programming if applicable"
                        ]
                    )

                    state['results'].append(result)
                    break

    def _analyze_function_call(self, node: ast.Call, state: Dict, depth: int, in_loop: bool):
        """Analyze function calls for known complexity patterns."""
        line_num = getattr(node, 'lineno', 'Unknown')

        func_name = None
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        if func_name and func_name in self.builtin_complexities:
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
                description=f"Built-in function '{func_name}()' call",
                analysis_type="Built-in Function",
                confidence=0.95,
                suggestions=self._get_builtin_suggestions(func_name, in_loop)
            )

            state['results'].append(result)

    def _analyze_assignment(self, node: ast.AST, state: Dict, depth: int, in_loop: bool):
        """Analyze variable assignments for space complexity."""
        line_num = getattr(node, 'lineno', 'Unknown')

        # Check if assignment creates new data structures
        if isinstance(node.value, (ast.List, ast.Dict, ast.Set)):
            elements = getattr(node.value, 'elts', getattr(node.value, 'keys', []))
            space_complexity = 'O(n)' if len(elements) > 0 else 'O(1)'
            time_complexity = 'O(1)'

            result = ComplexityResult(
                time_complexity=time_complexity,
                space_complexity=space_complexity,
                line_number=line_num,
                description="Data structure creation",
                analysis_type="Assignment",
                confidence=0.8,
                suggestions=["Consider memory usage for large data structures"]
            )

            state['results'].append(result)

    def _analyze_comprehension(self, node: ast.AST, state: Dict, depth: int, in_loop: bool):
        """Analyze list/dict/set comprehensions."""
        line_num = getattr(node, 'lineno', 'Unknown')

        # Comprehensions are typically O(n) time and O(n) space
        time_complexity = 'O(n)'
        space_complexity = 'O(n)'

        comp_type = type(node).__name__.replace('Comp', ' comprehension')

        result = ComplexityResult(
            time_complexity=time_complexity,
            space_complexity=space_complexity,
            line_number=line_num,
            description=f"{comp_type} - creates new collection",
            analysis_type="Comprehension",
            confidence=0.9,
            suggestions=["Consider generator expressions for memory efficiency if full list not needed"]
        )

        state['results'].append(result)

    def _multiply_complexity(self, complexity1: str, complexity2: str) -> str:
        """Multiply two complexity expressions (for nested operations)."""
        # Simplified complexity multiplication
        if complexity1 == 'O(1)':
            return complexity2
        if complexity2 == 'O(1)':
            return complexity1
        if complexity1 == 'O(n)' and complexity2 == 'O(n)':
            return 'O(n²)'
        if 'O(n²)' in [complexity1, complexity2]:
            return 'O(n²)'
        return 'O(n²)'  # Conservative estimate

    def _get_loop_suggestions(self, depth: int) -> List[str]:
        """Get optimization suggestions for loops."""
        suggestions = []
        if depth == 1:
            suggestions.extend([
                "Consider if the inner loop can be eliminated",
                "Look for opportunities to use hash tables or sets for O(1) lookups",
                "Consider sorting data first if it enables more efficient algorithms"
            ])
        elif depth > 1:
            suggestions.extend([
                "Deep nesting indicates potential for significant optimization",
                "Consider breaking down into separate functions",
                "Look for dynamic programming opportunities"
            ])
        return suggestions

    def _get_builtin_suggestions(self, func_name: str, in_loop: bool) -> List[str]:
        """Get suggestions for built-in function usage."""
        suggestions = []
        if in_loop and func_name in ['sorted', 'max', 'min', 'sum']:
            suggestions.append(f"Calling {func_name}() inside a loop increases overall complexity")
        if func_name == 'sorted':
            suggestions.append("Consider if data can be kept sorted to avoid repeated sorting")
        return suggestions