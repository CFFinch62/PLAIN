"""
Language analyzers for the Code Analysis Tool.

This module contains language-specific analyzers that implement
code complexity analysis for different programming languages.

Each language analyzer inherits from BaseLanguageAnalyzer and
implements language-specific parsing and analysis logic.
"""

from .base import BaseLanguageAnalyzer

__all__ = [
    'BaseLanguageAnalyzer'
]

# Available language analyzers
AVAILABLE_ANALYZERS = {
    'python': 'languages.python_analyzer.PythonAnalyzer',
    'ruby': 'languages.ruby_analyzer.RubyAnalyzer',
    'lua': 'languages.lua_analyzer.LuaAnalyzer',
    'basic': 'languages.basic_analyzer.BasicAnalyzer',
    'pseudocode': 'languages.pseudocode_analyzer.PseudocodeAnalyzer'
}


def get_analyzer_class(language: str):
    """
    Get analyzer class for a specific language.

    Args:
        language: Language name

    Returns:
        Analyzer class or None if not available
    """
    analyzer_path = AVAILABLE_ANALYZERS.get(language.lower())
    if not analyzer_path:
        return None

    try:
        module_path, class_name = analyzer_path.rsplit('.', 1)
        module = __import__(module_path, fromlist=[class_name])
        return getattr(module, class_name)
    except (ImportError, AttributeError):
        return None


def list_available_languages():
    """
    Get list of available language analyzers.

    Returns:
        List of language names
    """
    return list(AVAILABLE_ANALYZERS.keys())
