"""
Data models for the Code Analysis Tool.

This module defines the core data structures used throughout the application
for representing analysis results, complexity information, and reports.
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime
import json


@dataclass
class ComplexityResult:
    """Data class for individual complexity analysis results."""
    time_complexity: str
    space_complexity: str
    line_number: int
    description: str
    analysis_type: str
    confidence: float
    suggestions: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComplexityResult':
        """Create instance from dictionary."""
        return cls(**data)


@dataclass
class AnalysisReport:
    """Complete analysis report for a code snippet."""
    timestamp: str
    language: str
    code_length: int
    overall_time_complexity: str
    overall_space_complexity: str
    detailed_results: List[ComplexityResult]
    warnings: List[str]
    suggestions: List[str]
    quality_score: float
    performance_rating: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        # Convert detailed_results to list of dicts
        data['detailed_results'] = [result.to_dict() for result in self.detailed_results]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisReport':
        """Create instance from dictionary."""
        # Convert detailed_results from list of dicts
        if 'detailed_results' in data:
            data['detailed_results'] = [
                ComplexityResult.from_dict(result)
                for result in data['detailed_results']
            ]
        return cls(**data)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'AnalysisReport':
        """Create instance from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    @staticmethod
    def create_error_report(error_msg: str, language: str, code: str = "") -> 'AnalysisReport':
        """Create an error report for failed analysis."""
        return AnalysisReport(
            timestamp=datetime.now().isoformat(),
            language=language,
            code_length=len(code.splitlines()) if code else 0,
            overall_time_complexity="Error",
            overall_space_complexity="Error",
            detailed_results=[],
            warnings=[error_msg],
            suggestions=["Fix syntax errors and try again"],
            quality_score=0.0,
            performance_rating="Unable to analyze"
        )


@dataclass
class LanguageInfo:
    """Information about a supported programming language."""
    name: str
    extensions: List[str]
    analyzer_class: str
    description: str
    supported_features: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)


@dataclass
class AnalysisConfig:
    """Configuration for code analysis."""
    max_depth: int = 10
    include_space_analysis: bool = True
    generate_suggestions: bool = True
    confidence_threshold: float = 0.8
    timeout_seconds: int = 30

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisConfig':
        """Create instance from dictionary."""
        return cls(**data)


# Complexity constants and utilities
COMPLEXITY_ORDER = [
    'O(1)', 'O(log n)', 'O(n)', 'O(n log n)',
    'O(n²)', 'O(n³)', 'O(2ⁿ)', 'O(n!)'
]

COMPLEXITY_COLORS = {
    'O(1)': '#4CAF50',      # Green
    'O(log n)': '#8BC34A',  # Light Green
    'O(n)': '#FFC107',      # Amber
    'O(n log n)': '#FF9800', # Orange
    'O(n²)': '#FF5722',     # Deep Orange
    'O(n³)': '#F44336',     # Red
    'O(2ⁿ)': '#9C27B0',     # Purple
    'O(n!)': '#E91E63'      # Pink
}

PERFORMANCE_RATINGS = {
    'Excellent': '#4CAF50',
    'Good': '#8BC34A',
    'Fair': '#FFC107',
    'Poor': '#FF9800',
    'Very Poor': '#F44336'
}


def compare_complexity(complexity1: str, complexity2: str) -> int:
    """
    Compare two complexity expressions.

    Returns:
        -1 if complexity1 is better than complexity2
         0 if they are equal
         1 if complexity1 is worse than complexity2
    """
    try:
        index1 = COMPLEXITY_ORDER.index(complexity1)
    except ValueError:
        index1 = len(COMPLEXITY_ORDER)  # Unknown complexity, assume worst

    try:
        index2 = COMPLEXITY_ORDER.index(complexity2)
    except ValueError:
        index2 = len(COMPLEXITY_ORDER)  # Unknown complexity, assume worst

    if index1 < index2:
        return -1
    elif index1 > index2:
        return 1
    else:
        return 0


def is_worse_complexity(new_complexity: str, current_complexity: str) -> bool:
    """Check if new complexity is worse than current complexity."""
    return compare_complexity(new_complexity, current_complexity) > 0


def get_complexity_color(complexity: str) -> str:
    """Get color code for complexity visualization."""
    return COMPLEXITY_COLORS.get(complexity, '#FFFFFF')


def get_performance_color(rating: str) -> str:
    """Get color code for performance rating visualization."""
    return PERFORMANCE_RATINGS.get(rating, '#FFFFFF')
