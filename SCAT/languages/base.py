"""
Base language analyzer for the Code Analysis Tool.

This module defines the abstract base class that all language-specific
analyzers must inherit from, providing a common interface and shared
functionality for code complexity analysis.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

from core.models import AnalysisReport, ComplexityResult, AnalysisConfig
from core.utils import calculate_quality_score


class BaseLanguageAnalyzer(ABC):
    """
    Abstract base class for language-specific code analyzers.

    All language analyzers must inherit from this class and implement
    the required abstract methods for parsing and analyzing code.
    """

    def __init__(self, config: AnalysisConfig):
        """
        Initialize the language analyzer.

        Args:
            config: Analysis configuration
        """
        self.config = config
        self.language_name = self.get_language_name()

        # Common complexity patterns
        self.time_patterns = {
            'O(1)': {'weight': 1, 'description': 'Constant time - excellent performance'},
            'O(log n)': {'weight': 2, 'description': 'Logarithmic time - very good performance'},
            'O(n)': {'weight': 3, 'description': 'Linear time - good performance'},
            'O(n log n)': {'weight': 4, 'description': 'Linearithmic time - acceptable performance'},
            'O(n²)': {'weight': 5, 'description': 'Quadratic time - poor performance for large inputs'},
            'O(n³)': {'weight': 6, 'description': 'Cubic time - very poor performance'},
            'O(2ⁿ)': {'weight': 7, 'description': 'Exponential time - extremely poor performance'},
            'O(n!)': {'weight': 8, 'description': 'Factorial time - impractical for large inputs'}
        }

        self.space_patterns = {
            'O(1)': {'weight': 1, 'description': 'Constant space - excellent memory efficiency'},
            'O(log n)': {'weight': 2, 'description': 'Logarithmic space - very good memory efficiency'},
            'O(n)': {'weight': 3, 'description': 'Linear space - acceptable memory usage'},
            'O(n²)': {'weight': 4, 'description': 'Quadratic space - poor memory efficiency'},
            'O(2ⁿ)': {'weight': 5, 'description': 'Exponential space - extremely poor memory efficiency'}
        }

    @abstractmethod
    def get_language_name(self) -> str:
        """
        Get the name of the programming language this analyzer handles.

        Returns:
            Language name (e.g., 'python', 'ruby', 'lua')
        """
        pass

    @abstractmethod
    def parse_code(self, code: str) -> Any:
        """
        Parse source code into an abstract syntax tree or similar structure.

        Args:
            code: Source code to parse

        Returns:
            Parsed code structure (AST, tokens, etc.)

        Raises:
            SyntaxError: If code has syntax errors
            Exception: For other parsing errors
        """
        pass

    @abstractmethod
    def analyze_structure(self, parsed_code: Any) -> List[ComplexityResult]:
        """
        Analyze parsed code structure for complexity patterns.

        Args:
            parsed_code: Parsed code structure from parse_code()

        Returns:
            List of complexity analysis results
        """
        pass

    def analyze(self, code: str) -> AnalysisReport:
        """
        Perform complete code analysis.

        Args:
            code: Source code to analyze

        Returns:
            Complete analysis report
        """
        try:
            # Parse the code
            parsed_code = self.parse_code(code)

            # Analyze for complexity patterns
            detailed_results = self.analyze_structure(parsed_code)

            # Calculate overall complexity
            overall_time, overall_space = self._calculate_overall_complexity(detailed_results)

            # Generate warnings and suggestions
            warnings = self._generate_warnings(detailed_results)
            suggestions = self._generate_suggestions(detailed_results)

            # Calculate quality metrics
            quality_score = calculate_quality_score(
                overall_time, overall_space, len(warnings), len(suggestions)
            )
            performance_rating = self._get_performance_rating(overall_time, overall_space)

            # Create analysis report
            return AnalysisReport(
                timestamp=datetime.now().isoformat(),
                language=self.language_name,
                code_length=len(code.splitlines()),
                overall_time_complexity=overall_time,
                overall_space_complexity=overall_space,
                detailed_results=detailed_results,
                warnings=warnings,
                suggestions=suggestions,
                quality_score=quality_score,
                performance_rating=performance_rating
            )

        except SyntaxError as e:
            return self._create_error_report(f"Syntax Error: {str(e)}", code)
        except Exception as e:
            return self._create_error_report(f"Analysis Error: {str(e)}", code)

    def _calculate_overall_complexity(self, results: List[ComplexityResult]) -> tuple:
        """
        Calculate overall time and space complexity from detailed results.

        Args:
            results: List of complexity results

        Returns:
            Tuple of (overall_time_complexity, overall_space_complexity)
        """
        if not results:
            return 'O(1)', 'O(1)'

        # Find worst time and space complexity
        worst_time = 'O(1)'
        worst_space = 'O(1)'

        for result in results:
            if self._is_worse_complexity(result.time_complexity, worst_time):
                worst_time = result.time_complexity
            if self._is_worse_complexity(result.space_complexity, worst_space):
                worst_space = result.space_complexity

        return worst_time, worst_space

    def _is_worse_complexity(self, new_complexity: str, current_complexity: str) -> bool:
        """Check if new complexity is worse than current."""
        complexity_order = ['O(1)', 'O(log n)', 'O(n)', 'O(n log n)', 'O(n²)', 'O(n³)', 'O(2ⁿ)', 'O(n!)']

        # Skip unknown complexities (O(?)) - don't let them override known complexities
        if new_complexity == 'O(?)' or 'O(?)' in new_complexity:
            return False
        if current_complexity == 'O(?)' or 'O(?)' in current_complexity:
            return True  # Replace unknown with known

        try:
            new_index = complexity_order.index(new_complexity)
        except ValueError:
            return False  # Unknown complexity, don't replace known ones

        try:
            current_index = complexity_order.index(current_complexity)
        except ValueError:
            return True  # Current is unknown, replace with known

        return new_index > current_index

    def _generate_warnings(self, results: List[ComplexityResult]) -> List[str]:
        """
        Generate performance warnings based on analysis results.

        Args:
            results: List of complexity results

        Returns:
            List of warning messages
        """
        warnings = []

        # Check for high complexity patterns
        for result in results:
            if result.time_complexity in ['O(n²)', 'O(n³)', 'O(2ⁿ)', 'O(n!)']:
                warnings.append(
                    f"Line {result.line_number}: {result.analysis_type} has {result.time_complexity} complexity"
                )

        # Check for nested loops
        loop_depths = {}
        for result in results:
            if result.analysis_type == 'Loop':
                line = result.line_number
                if line not in loop_depths:
                    loop_depths[line] = 0
                loop_depths[line] += 1

        for line, depth in loop_depths.items():
            if depth > 1:
                warnings.append(f"Line {line}: Nested loops detected (depth {depth})")

        return warnings

    def _generate_suggestions(self, results: List[ComplexityResult]) -> List[str]:
        """
        Generate optimization suggestions based on analysis results.

        Args:
            results: List of complexity results

        Returns:
            List of suggestion messages
        """
        suggestions = []

        # Collect suggestions from individual results
        for result in results:
            suggestions.extend(result.suggestions)

        # Add general suggestions based on patterns
        time_complexities = [r.time_complexity for r in results]

        if 'O(n²)' in time_complexities:
            suggestions.append("Consider using hash tables or sets for O(1) lookups to reduce quadratic complexity")

        if 'O(2ⁿ)' in time_complexities:
            suggestions.append("Consider memoization or dynamic programming to optimize exponential algorithms")

        # Remove duplicates while preserving order
        seen = set()
        unique_suggestions = []
        for suggestion in suggestions:
            if suggestion not in seen:
                seen.add(suggestion)
                unique_suggestions.append(suggestion)

        return unique_suggestions

    def _get_performance_rating(self, time_complexity: str, space_complexity: str) -> str:
        """Get human-readable performance rating."""
        time_weight = self.time_patterns.get(time_complexity, {}).get('weight', 5)
        space_weight = self.space_patterns.get(space_complexity, {}).get('weight', 3)

        avg_weight = (time_weight + space_weight) / 2

        if avg_weight <= 2:
            return "Excellent"
        elif avg_weight <= 3:
            return "Good"
        elif avg_weight <= 4:
            return "Fair"
        elif avg_weight <= 5:
            return "Poor"
        else:
            return "Very Poor"

    def _create_error_report(self, error_msg: str, code: str) -> AnalysisReport:
        """Create error report for failed analysis."""
        return AnalysisReport(
            timestamp=datetime.now().isoformat(),
            language=self.language_name,
            code_length=len(code.splitlines()) if code else 0,
            overall_time_complexity="Error",
            overall_space_complexity="Error",
            detailed_results=[],
            warnings=[error_msg],
            suggestions=["Fix syntax errors and try again"],
            quality_score=0.0,
            performance_rating="Unable to analyze"
        )
