"""
Language selector widget for SCAT (Source Code Analysis Tool).

This module provides a widget for selecting programming languages
and managing language-specific settings.
"""

from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QComboBox,
                            QLabel, QPushButton, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap


class LanguageSelector(QWidget):
    """Widget for selecting programming languages."""

    languageChanged = pyqtSignal(str)  # Emitted when language changes
    sampleCodeRequested = pyqtSignal(str)  # Emitted when sample code is requested

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()

        # Available languages with their display info
        self.languages = {
            'python': {
                'display_name': 'Python',
                'description': 'Python programming language with AST-based analysis',
                'extensions': ['.py', '.pyw'],
                'icon': '🐍'
            },
            'ruby': {
                'display_name': 'Ruby',
                'description': 'Ruby programming language with pattern-based analysis',
                'extensions': ['.rb', '.rbw'],
                'icon': '💎'
            },
            'lua': {
                'display_name': 'Lua',
                'description': 'Lua programming language with pattern-based analysis',
                'extensions': ['.lua'],
                'icon': '🌙'
            },
            'basic': {
                'display_name': 'BASIC',
                'description': 'BASIC programming language with pattern-based analysis',
                'extensions': ['.bas', '.basic'],
                'icon': '📟'
            },
            'pseudocode': {
                'display_name': 'Pseudocode',
                'description': 'Pseudocode algorithm notation with structured analysis',
                'extensions': ['.pseudo', '.txt'],
                'icon': '📝'
            }
        }

        self.populate_languages()

    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        layout.setSpacing(4)  # Reduce spacing

        # Language selection group (more compact)
        lang_group = QGroupBox("Programming Language")
        lang_layout = QVBoxLayout(lang_group)
        lang_layout.setSpacing(4)  # Reduce internal spacing

        # Language combo box and sample button in one row
        selector_layout = QHBoxLayout()

        self.language_label = QLabel("Language:")
        self.language_combo = QComboBox()
        self.language_combo.setMinimumWidth(120)  # Slightly smaller

        # Sample code button (more compact)
        self.sample_button = QPushButton("Sample")
        self.sample_button.setMaximumWidth(80)  # Smaller button

        selector_layout.addWidget(self.language_label)
        selector_layout.addWidget(self.language_combo)
        selector_layout.addWidget(self.sample_button)
        selector_layout.addStretch()

        # Language info (more compact, single line)
        self.info_label = QLabel()
        self.info_label.setWordWrap(False)  # Single line
        self.info_label.setStyleSheet("color: #9D9D9D; font-style: italic; font-size: 10px;")

        lang_layout.addLayout(selector_layout)
        lang_layout.addWidget(self.info_label)

        layout.addWidget(lang_group)

    def setup_connections(self):
        """Setup signal connections."""
        self.language_combo.currentTextChanged.connect(self.on_language_changed)
        self.sample_button.clicked.connect(self.on_sample_requested)

    def populate_languages(self):
        """Populate the language combo box."""
        self.language_combo.clear()

        for lang_key, lang_info in self.languages.items():
            display_text = f"{lang_info['icon']} {lang_info['display_name']}"
            self.language_combo.addItem(display_text, lang_key)

        # Set default to Python
        self.language_combo.setCurrentIndex(0)
        self.update_language_info()

    def on_language_changed(self):
        """Handle language selection change."""
        self.update_language_info()
        current_lang = self.get_selected_language()
        if current_lang:
            self.languageChanged.emit(current_lang)

    def update_language_info(self):
        """Update the language information display."""
        current_lang = self.get_selected_language()
        if current_lang and current_lang in self.languages:
            lang_info = self.languages[current_lang]

            # Update description with extensions in one line
            extensions_text = ', '.join(lang_info['extensions'])
            info_text = f"{lang_info['description']} ({extensions_text})"
            self.info_label.setText(info_text)
        else:
            self.info_label.setText("No language selected")

    def get_selected_language(self):
        """Get the currently selected language key."""
        current_index = self.language_combo.currentIndex()
        if current_index >= 0:
            return self.language_combo.itemData(current_index)
        return None

    def set_selected_language(self, language):
        """Set the selected language."""
        for i in range(self.language_combo.count()):
            if self.language_combo.itemData(i) == language:
                self.language_combo.setCurrentIndex(i)
                break

    def on_sample_requested(self):
        """Handle sample code request."""
        current_lang = self.get_selected_language()
        if current_lang:
            # Emit signal for sample code request
            self.sampleCodeRequested.emit(current_lang)

    def add_language(self, key, display_name, description, extensions, icon="📄"):
        """Add a new language to the selector."""
        self.languages[key] = {
            'display_name': display_name,
            'description': description,
            'extensions': extensions,
            'icon': icon
        }

        # Refresh the combo box
        current_selection = self.get_selected_language()
        self.populate_languages()

        # Restore selection if possible
        if current_selection:
            self.set_selected_language(current_selection)

    def remove_language(self, key):
        """Remove a language from the selector."""
        if key in self.languages:
            del self.languages[key]

            # Refresh the combo box
            current_selection = self.get_selected_language()
            self.populate_languages()

            # If the removed language was selected, select the first one
            if current_selection == key and self.language_combo.count() > 0:
                self.language_combo.setCurrentIndex(0)

    def get_language_info(self, language=None):
        """Get information about a language."""
        if language is None:
            language = self.get_selected_language()

        return self.languages.get(language, {})

    def get_all_languages(self):
        """Get all available languages."""
        return self.languages.copy()

    def update_from_analyzer(self, analyzer):
        """Update available languages from the analyzer."""
        try:
            supported_languages = analyzer.get_supported_languages()

            # Clear current languages
            self.languages.clear()

            # Add supported languages
            for lang_key, lang_info in supported_languages.items():
                icon_map = {
                    'python': '🐍',
                    'ruby': '💎',
                    'lua': '🌙',
                    'basic': '📟',
                    'pseudocode': '📝',
                    'plain': '📋',
                    'steps': '🪜',
                    'javascript': '🟨',
                    'java': '☕',
                    'cpp': '⚡',
                    'c': '🔧'
                }

                self.languages[lang_key] = {
                    'display_name': lang_info.name,
                    'description': lang_info.description,
                    'extensions': lang_info.extensions,
                    'icon': icon_map.get(lang_key, '📄')
                }

            # Refresh the combo box
            self.populate_languages()

        except Exception as e:
            print(f"Error updating languages from analyzer: {e}")
            # Fall back to default languages
            pass
