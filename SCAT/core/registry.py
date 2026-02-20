"""
Language analyzer registry for the Code Analysis Tool.

This module manages the registration and retrieval of language-specific
analyzers, providing a plugin-like architecture for adding new languages.
"""

from typing import Dict, Optional, Type, List
from .models import LanguageInfo


class LanguageRegistry:
    """
    Registry for managing language analyzers.
    
    This class provides a centralized way to register, retrieve, and manage
    language-specific code analyzers in a plugin-like architecture.
    """
    
    def __init__(self):
        """Initialize the language registry."""
        self._analyzers: Dict[str, Type] = {}
        self._language_info: Dict[str, LanguageInfo] = {}
    
    def register_analyzer(self, language: str, analyzer_class: Type,
                         extensions: List[str] = None, 
                         description: str = "",
                         features: List[str] = None):
        """
        Register a language analyzer.
        
        Args:
            language: Language name (e.g., 'python', 'ruby', 'lua')
            analyzer_class: Analyzer class that implements the language analysis
            extensions: File extensions for this language (e.g., ['.py', '.pyw'])
            description: Human-readable description of the language
            features: List of supported analysis features
        """
        language = language.lower()
        
        # Validate analyzer class
        if not hasattr(analyzer_class, 'analyze'):
            raise ValueError(f"Analyzer class for {language} must have an 'analyze' method")
        
        # Register the analyzer
        self._analyzers[language] = analyzer_class
        
        # Create and store language info
        language_info = LanguageInfo(
            name=language.title(),
            extensions=extensions or [],
            analyzer_class=analyzer_class.__name__,
            description=description,
            supported_features=features or []
        )
        self._language_info[language] = language_info
    
    def get_analyzer(self, language: str) -> Optional[Type]:
        """
        Get analyzer class for a language.
        
        Args:
            language: Language name
            
        Returns:
            Analyzer class or None if not found
        """
        return self._analyzers.get(language.lower())
    
    def is_supported(self, language: str) -> bool:
        """
        Check if a language is supported.
        
        Args:
            language: Language name
            
        Returns:
            True if language is supported, False otherwise
        """
        return language.lower() in self._analyzers
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of all supported language names.
        
        Returns:
            List of supported language names
        """
        return list(self._analyzers.keys())
    
    def get_language_info(self, language: str) -> Optional[LanguageInfo]:
        """
        Get information about a specific language.
        
        Args:
            language: Language name
            
        Returns:
            LanguageInfo object or None if not found
        """
        return self._language_info.get(language.lower())
    
    def get_all_languages(self) -> Dict[str, LanguageInfo]:
        """
        Get information about all registered languages.
        
        Returns:
            Dictionary mapping language names to LanguageInfo objects
        """
        return self._language_info.copy()
    
    def get_language_by_extension(self, extension: str) -> Optional[str]:
        """
        Get language name by file extension.
        
        Args:
            extension: File extension (e.g., '.py', '.rb')
            
        Returns:
            Language name or None if not found
        """
        extension = extension.lower()
        for language, info in self._language_info.items():
            if extension in info.extensions:
                return language
        return None
    
    def unregister_analyzer(self, language: str):
        """
        Unregister a language analyzer.
        
        Args:
            language: Language name to unregister
        """
        language = language.lower()
        self._analyzers.pop(language, None)
        self._language_info.pop(language, None)
    
    def clear_all(self):
        """Clear all registered analyzers."""
        self._analyzers.clear()
        self._language_info.clear()
    
    def get_registry_stats(self) -> Dict[str, int]:
        """
        Get statistics about the registry.
        
        Returns:
            Dictionary with registry statistics
        """
        total_extensions = sum(
            len(info.extensions) for info in self._language_info.values()
        )
        
        return {
            'total_languages': len(self._analyzers),
            'total_extensions': total_extensions,
            'languages_with_extensions': len([
                info for info in self._language_info.values() 
                if info.extensions
            ])
        }
    
    def validate_registry(self) -> List[str]:
        """
        Validate the registry and return any issues found.
        
        Returns:
            List of validation error messages
        """
        errors = []
        
        for language, analyzer_class in self._analyzers.items():
            # Check if analyzer class has required methods
            if not hasattr(analyzer_class, 'analyze'):
                errors.append(f"Analyzer for {language} missing 'analyze' method")
            
            # Check if language info exists
            if language not in self._language_info:
                errors.append(f"Missing language info for {language}")
        
        # Check for duplicate extensions
        extension_map = {}
        for language, info in self._language_info.items():
            for ext in info.extensions:
                if ext in extension_map:
                    errors.append(
                        f"Extension {ext} registered for both {language} and {extension_map[ext]}"
                    )
                else:
                    extension_map[ext] = language
        
        return errors
