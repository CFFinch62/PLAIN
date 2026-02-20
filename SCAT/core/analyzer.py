"""
Main code analyzer that coordinates language-specific analysis.

This module provides the central CodeAnalyzer class that manages
language detection, analyzer selection, and result aggregation.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from .models import AnalysisReport, AnalysisConfig, LanguageInfo
from .registry import LanguageRegistry
from .utils import detect_language_from_extension, detect_language_from_content


class CodeAnalyzer:
    """
    Main code analyzer that coordinates language-specific analysis.

    This class serves as the central coordinator for code analysis,
    managing language detection, analyzer selection, and result aggregation.
    """

    def __init__(self, config: Optional[AnalysisConfig] = None):
        """
        Initialize the code analyzer.

        Args:
            config: Analysis configuration. If None, uses default config.
        """
        self.config = config or AnalysisConfig()
        self.registry = LanguageRegistry()
        self._load_default_analyzers()

    def _load_default_analyzers(self):
        """Load default language analyzers."""
        # Import and register default analyzers
        try:
            from languages.python_analyzer import PythonAnalyzer
            self.registry.register_analyzer(
                'python',
                PythonAnalyzer,
                ['.py', '.pyw'],
                'Python programming language',
                ['loops', 'recursion', 'built-ins', 'comprehensions', 'data-structures']
            )
        except ImportError:
            pass

        try:
            from languages.ruby_analyzer import RubyAnalyzer
            self.registry.register_analyzer(
                'ruby',
                RubyAnalyzer,
                ['.rb', '.rbw'],
                'Ruby programming language',
                ['loops', 'iterators', 'built-ins', 'blocks', 'data-structures']
            )
        except ImportError:
            pass

        try:
            from languages.lua_analyzer import LuaAnalyzer
            self.registry.register_analyzer(
                'lua',
                LuaAnalyzer,
                ['.lua'],
                'Lua programming language',
                ['loops', 'functions', 'tables', 'strings', 'built-ins']
            )
        except ImportError:
            pass

        try:
            from languages.basic_analyzer import BasicAnalyzer
            self.registry.register_analyzer(
                'basic',
                BasicAnalyzer,
                ['.bas', '.basic'],
                'BASIC programming language',
                ['loops', 'functions', 'arrays', 'strings', 'built-ins', 'control-flow']
            )
        except ImportError:
            pass

        try:
            from languages.pseudocode_analyzer import PseudocodeAnalyzer
            self.registry.register_analyzer(
                'pseudocode',
                PseudocodeAnalyzer,
                ['.pseudo', '.txt'],
                'Pseudocode algorithm notation',
                ['loops', 'algorithms', 'data-structures', 'complexity-analysis']
            )
        except ImportError:
            pass

        try:
            from languages.plain_analyzer import PlainAnalyzer
            self.registry.register_analyzer(
                'plain',
                PlainAnalyzer,
                ['.plain'],
                'PLAIN programming language',
                ['loops', 'tasks', 'recursion', 'built-ins', 'data-structures', 'collections']
            )
        except ImportError:
            pass

        try:
            from languages.steps_analyzer import StepsAnalyzer
            self.registry.register_analyzer(
                'steps',
                StepsAnalyzer,
                ['.step', '.building', '.floor'],
                'Steps educational programming language',
                ['loops', 'steps', 'risers', 'built-ins', 'data-structures', 'error-handling']
            )
        except ImportError:
            pass

    def analyze_code(self, code: str, language: Optional[str] = None,
                    file_path: Optional[str] = None) -> AnalysisReport:
        """
        Analyze code for complexity and performance.

        Args:
            code: Source code to analyze
            language: Programming language (auto-detected if None)
            file_path: Optional file path for language detection

        Returns:
            AnalysisReport containing analysis results
        """
        try:
            # Detect language if not provided
            if language is None:
                language = self._detect_language(code, file_path)

            # Normalize language name
            language = language.lower()

            # Get analyzer for the language
            analyzer_class = self.registry.get_analyzer(language)
            if analyzer_class is None:
                return AnalysisReport.create_error_report(
                    f"Language '{language}' is not supported",
                    language,
                    code
                )

            # Create analyzer instance and perform analysis
            analyzer = analyzer_class(self.config)
            return analyzer.analyze(code)

        except Exception as e:
            return AnalysisReport.create_error_report(
                f"Analysis error: {str(e)}",
                language or "unknown",
                code
            )

    def analyze_file(self, file_path: str, language: Optional[str] = None) -> AnalysisReport:
        """
        Analyze a code file.

        Args:
            file_path: Path to the code file
            language: Programming language (auto-detected if None)

        Returns:
            AnalysisReport containing analysis results
        """
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()

            # Analyze with file path for language detection
            return self.analyze_code(code, language, file_path)

        except FileNotFoundError:
            return AnalysisReport.create_error_report(
                f"File not found: {file_path}",
                language or "unknown"
            )
        except UnicodeDecodeError:
            return AnalysisReport.create_error_report(
                f"Unable to decode file: {file_path}",
                language or "unknown"
            )
        except Exception as e:
            return AnalysisReport.create_error_report(
                f"Error reading file {file_path}: {str(e)}",
                language or "unknown"
            )

    def _detect_language(self, code: str, file_path: Optional[str] = None) -> str:
        """
        Detect programming language from code and/or file path.

        Args:
            code: Source code content
            file_path: Optional file path

        Returns:
            Detected language name
        """
        # Try to detect from file extension first
        if file_path:
            lang_from_ext = detect_language_from_extension(file_path)
            if lang_from_ext and self.registry.is_supported(lang_from_ext):
                return lang_from_ext

        # Try to detect from code content
        lang_from_content = detect_language_from_content(code)
        if lang_from_content and self.registry.is_supported(lang_from_content):
            return lang_from_content

        # Default to Python if unable to detect
        return 'python'

    def get_supported_languages(self) -> Dict[str, LanguageInfo]:
        """Get information about all supported languages."""
        return self.registry.get_all_languages()

    def is_language_supported(self, language: str) -> bool:
        """Check if a language is supported."""
        return self.registry.is_supported(language.lower())

    def get_language_info(self, language: str) -> Optional[LanguageInfo]:
        """Get information about a specific language."""
        return self.registry.get_language_info(language.lower())

    def register_language_analyzer(self, language: str, analyzer_class,
                                 extensions: list, description: str = "",
                                 features: list = None):
        """
        Register a new language analyzer.

        Args:
            language: Language name
            analyzer_class: Analyzer class
            extensions: File extensions for this language
            description: Language description
            features: Supported features list
        """
        self.registry.register_analyzer(
            language, analyzer_class, extensions, description, features or []
        )

    def update_config(self, config: AnalysisConfig):
        """Update analysis configuration."""
        self.config = config
