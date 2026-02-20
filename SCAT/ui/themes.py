"""
Theme and styling for SCAT (Source Code Analysis Tool).

This module provides consistent styling and theming for the GUI application.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor


class SCATTheme:
    """Theme configuration for SCAT application."""

    # Color palette
    COLORS = {
        'primary': '#0E639C',
        'primary_hover': '#1177BB',
        'primary_pressed': '#005A9E',
        'secondary': '#2D2D30',
        'background': '#1E1E1E',
        'surface': '#2D2D30',
        'border': '#3C3C3C',
        'text_primary': '#FFFFFF',
        'text_secondary': '#D4D4D4',
        'text_muted': '#9D9D9D',
        'success': '#4CAF50',
        'warning': '#FF9800',
        'error': '#F44336',
        'info': '#2196F3',

        # Complexity colors
        'complexity_excellent': '#4CAF50',
        'complexity_good': '#8BC34A',
        'complexity_fair': '#FFC107',
        'complexity_poor': '#FF9800',
        'complexity_very_poor': '#F44336',
        'complexity_exponential': '#9C27B0',
        'complexity_factorial': '#E91E63',
    }

    # Fonts
    FONTS = {
        'default': QFont('Segoe UI', 9),
        'heading': QFont('Segoe UI', 12, QFont.Weight.Bold),
        'subheading': QFont('Segoe UI', 10, QFont.Weight.Bold),
        'code': QFont('Consolas', 10),
        'code_large': QFont('Consolas', 12),
        'small': QFont('Segoe UI', 8),
    }

    @classmethod
    def get_stylesheet(cls) -> str:
        """Get the complete application stylesheet."""
        return f"""
        /* Main Application */
        QMainWindow {{
            background-color: {cls.COLORS['background']};
            color: {cls.COLORS['text_primary']};
        }}

        /* Menu Bar */
        QMenuBar {{
            background-color: {cls.COLORS['secondary']};
            color: {cls.COLORS['text_primary']};
            border-bottom: 1px solid {cls.COLORS['border']};
            padding: 4px;
        }}

        QMenuBar::item {{
            background-color: transparent;
            padding: 8px 12px;
            border-radius: 4px;
        }}

        QMenuBar::item:selected {{
            background-color: {cls.COLORS['primary']};
        }}

        QMenu {{
            background-color: {cls.COLORS['secondary']};
            color: {cls.COLORS['text_primary']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: 4px;
            padding: 4px;
        }}

        QMenu::item {{
            padding: 8px 16px;
            border-radius: 4px;
        }}

        QMenu::item:selected {{
            background-color: {cls.COLORS['primary']};
        }}

        QMenu::separator {{
            height: 1px;
            background-color: {cls.COLORS['border']};
            margin: 4px 8px;
        }}

        /* Buttons */
        QPushButton {{
            background-color: {cls.COLORS['primary']};
            color: {cls.COLORS['text_primary']};
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
            min-width: 80px;
        }}

        QPushButton:hover {{
            background-color: {cls.COLORS['primary_hover']};
        }}

        QPushButton:pressed {{
            background-color: {cls.COLORS['primary_pressed']};
        }}

        QPushButton:disabled {{
            background-color: {cls.COLORS['border']};
            color: {cls.COLORS['text_muted']};
        }}

        /* Secondary buttons */
        QPushButton[class="secondary"] {{
            background-color: {cls.COLORS['surface']};
            border: 1px solid {cls.COLORS['border']};
        }}

        QPushButton[class="secondary"]:hover {{
            background-color: {cls.COLORS['border']};
        }}

        /* Text inputs */
        QTextEdit, QPlainTextEdit {{
            background-color: {cls.COLORS['background']};
            color: {cls.COLORS['text_secondary']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: 4px;
            padding: 8px;
            selection-background-color: {cls.COLORS['primary']};
        }}

        QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {cls.COLORS['primary']};
        }}

        /* Combo boxes */
        QComboBox {{
            background-color: {cls.COLORS['surface']};
            color: {cls.COLORS['text_primary']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: 4px;
            padding: 6px 12px;
            min-width: 120px;
        }}

        QComboBox:hover {{
            border-color: {cls.COLORS['primary']};
        }}

        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}

        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {cls.COLORS['text_primary']};
        }}

        QComboBox QAbstractItemView {{
            background-color: {cls.COLORS['surface']};
            color: {cls.COLORS['text_primary']};
            border: 1px solid {cls.COLORS['border']};
            selection-background-color: {cls.COLORS['primary']};
        }}

        /* Tab Widget */
        QTabWidget::pane {{
            border: 1px solid {cls.COLORS['border']};
            background-color: {cls.COLORS['background']};
            border-radius: 4px;
        }}

        QTabBar::tab {{
            background-color: {cls.COLORS['surface']};
            color: {cls.COLORS['text_primary']};
            border: 1px solid {cls.COLORS['border']};
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}

        QTabBar::tab:selected {{
            background-color: {cls.COLORS['primary']};
            border-bottom-color: {cls.COLORS['primary']};
        }}

        QTabBar::tab:hover:!selected {{
            background-color: {cls.COLORS['border']};
        }}

        /* Group boxes */
        QGroupBox {{
            font-weight: bold;
            border: 2px solid {cls.COLORS['border']};
            border-radius: 6px;
            margin-top: 12px;
            padding-top: 8px;
            color: {cls.COLORS['text_primary']};
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 8px;
            background-color: {cls.COLORS['background']};
        }}

        /* Lists and Tables */
        QListWidget, QTableWidget {{
            background-color: {cls.COLORS['background']};
            color: {cls.COLORS['text_secondary']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: 4px;
            selection-background-color: {cls.COLORS['primary']};
            alternate-background-color: {cls.COLORS['surface']};
        }}

        QListWidget::item, QTableWidget::item {{
            padding: 4px;
            border-bottom: 1px solid {cls.COLORS['border']};
        }}

        QListWidget::item:selected, QTableWidget::item:selected {{
            background-color: {cls.COLORS['primary']};
        }}

        QHeaderView::section {{
            background-color: {cls.COLORS['surface']};
            color: {cls.COLORS['text_primary']};
            border: 1px solid {cls.COLORS['border']};
            padding: 8px;
            font-weight: bold;
        }}

        /* Progress bars */
        QProgressBar {{
            border: 1px solid {cls.COLORS['border']};
            border-radius: 4px;
            text-align: center;
            color: {cls.COLORS['text_primary']};
            background-color: {cls.COLORS['surface']};
        }}

        QProgressBar::chunk {{
            background-color: {cls.COLORS['primary']};
            border-radius: 3px;
        }}

        /* Splitters */
        QSplitter::handle {{
            background-color: {cls.COLORS['border']};
        }}

        QSplitter::handle:horizontal {{
            width: 2px;
        }}

        QSplitter::handle:vertical {{
            height: 2px;
        }}

        /* Status bar */
        QStatusBar {{
            background-color: {cls.COLORS['surface']};
            color: {cls.COLORS['text_primary']};
            border-top: 1px solid {cls.COLORS['border']};
        }}

        /* Scrollbars */
        QScrollBar:vertical {{
            background-color: {cls.COLORS['surface']};
            width: 12px;
            border-radius: 6px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {cls.COLORS['border']};
            border-radius: 6px;
            min-height: 20px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {cls.COLORS['primary']};
        }}

        QScrollBar:horizontal {{
            background-color: {cls.COLORS['surface']};
            height: 12px;
            border-radius: 6px;
        }}

        QScrollBar::handle:horizontal {{
            background-color: {cls.COLORS['border']};
            border-radius: 6px;
            min-width: 20px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background-color: {cls.COLORS['primary']};
        }}

        QScrollBar::add-line, QScrollBar::sub-line {{
            border: none;
            background: none;
        }}

        /* Tooltips */
        QToolTip {{
            background-color: {cls.COLORS['surface']};
            color: {cls.COLORS['text_primary']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: 4px;
            padding: 4px 8px;
        }}
        """

    @classmethod
    def get_complexity_color(cls, complexity: str) -> str:
        """Get color for complexity display."""
        color_map = {
            'O(1)': cls.COLORS['complexity_excellent'],
            'O(log n)': cls.COLORS['complexity_good'],
            'O(n)': cls.COLORS['complexity_fair'],
            'O(n log n)': cls.COLORS['complexity_poor'],
            'O(n²)': cls.COLORS['complexity_very_poor'],
            'O(n³)': cls.COLORS['complexity_very_poor'],
            'O(n^2)': cls.COLORS['complexity_very_poor'],  # Alternative notation
            'O(n^3)': cls.COLORS['complexity_very_poor'],  # Alternative notation
            'O(2ⁿ)': cls.COLORS['complexity_exponential'],
            'O(2^n)': cls.COLORS['complexity_exponential'],  # Alternative notation
            'O(n!)': cls.COLORS['complexity_factorial'],
            'O(?)': cls.COLORS['text_muted'],  # Unknown complexity
        }

        # Debug: Print what complexity we're looking for
        result_color = color_map.get(complexity, cls.COLORS['complexity_very_poor'])

        # If not found in map, try to categorize by pattern
        if complexity not in color_map:
            complexity_lower = complexity.lower()
            if 'log' in complexity_lower:
                result_color = cls.COLORS['complexity_good']
            elif 'n^3' in complexity_lower or 'n³' in complexity_lower:
                result_color = cls.COLORS['complexity_very_poor']
            elif 'n^2' in complexity_lower or 'n²' in complexity_lower:
                result_color = cls.COLORS['complexity_very_poor']
            elif '^n' in complexity_lower or 'ⁿ' in complexity_lower:
                result_color = cls.COLORS['complexity_exponential']
            elif '!' in complexity_lower:
                result_color = cls.COLORS['complexity_factorial']
            elif 'n' in complexity_lower:
                result_color = cls.COLORS['complexity_fair']
            else:
                result_color = cls.COLORS['complexity_very_poor']  # Default for unknown

        return result_color

    @classmethod
    def get_quality_color(cls, score: float) -> str:
        """Get color for quality score."""
        if score >= 80:
            return cls.COLORS['complexity_excellent']
        elif score >= 60:
            return cls.COLORS['complexity_fair']
        elif score >= 40:
            return cls.COLORS['complexity_poor']
        else:
            return cls.COLORS['complexity_very_poor']
