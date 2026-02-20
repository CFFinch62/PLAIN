"""
Core module for the Code Analysis Tool.

This module provides the fundamental components for code analysis including:
- Data models for analysis results
- Base analyzer interface
- Language analyzer registry
- Common utilities

The core module is designed to be language-agnostic and extensible.
"""

from .models import ComplexityResult, AnalysisReport
from .analyzer import CodeAnalyzer
from .registry import LanguageRegistry

__all__ = [
    'ComplexityResult',
    'AnalysisReport', 
    'CodeAnalyzer',
    'LanguageRegistry'
]

__version__ = '2.0.0'
