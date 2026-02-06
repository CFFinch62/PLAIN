"""
Theme Manager for PLAIN IDE
Handles loading and applying themes
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

from plain_ide.app.settings import SettingsManager, get_config_dir


@dataclass
class SyntaxColors:
    """Syntax highlighting colors for code editor"""
    keyword: str = "#c678dd"
    builtin: str = "#e5c07b"
    type: str = "#56b6c2"
    string: str = "#98c379"
    number: str = "#d19a66"
    comment: str = "#5c6370"
    operator: str = "#56b6c2"
    function: str = "#61afef"
    variable: str = "#e06c75"
    constant: str = "#d19a66"
    identifier: str = "#abb2bf"
    interpolation: str = "#c678dd"  # For v"..." strings


@dataclass  
class Theme:
    """Complete theme definition"""
    name: str
    is_dark: bool
    
    # Main colors
    background: str
    foreground: str
    accent: str
    accent_hover: str
    
    # Panel colors
    panel_background: str
    panel_border: str
    
    # Editor colors
    editor_background: str
    editor_foreground: str
    editor_line_highlight: str
    editor_selection: str
    editor_gutter_bg: str
    editor_gutter_fg: str
    
    # Tab colors
    tab_background: str
    tab_active_background: str
    tab_hover_background: str
    tab_border: str
    
    # File browser colors
    browser_background: str
    browser_item_hover: str
    browser_item_selected: str
    
    # Terminal colors
    terminal_background: str
    terminal_foreground: str
    
    # Scrollbar
    scrollbar_background: str
    scrollbar_handle: str
    scrollbar_handle_hover: str
    
    # Button colors
    button_background: str
    button_foreground: str
    button_hover: str
    button_pressed: str
    
    # Input colors
    input_background: str
    input_border: str
    input_focus_border: str
    
    # Status colors
    success: str
    warning: str
    error: str
    info: str
    
    # Syntax highlighting
    syntax: SyntaxColors = None
    
    def __post_init__(self):
        if self.syntax is None:
            self.syntax = SyntaxColors()


# Built-in Dark Theme (One Dark inspired)
DARK_THEME = Theme(
    name="Dark",
    is_dark=True,
    background="#1e1e2e",
    foreground="#cdd6f4",
    accent="#89b4fa",
    accent_hover="#74c7ec",
    panel_background="#181825",
    panel_border="#313244",
    editor_background="#1e1e2e",
    editor_foreground="#cdd6f4",
    editor_line_highlight="#2a2a3c",
    editor_selection="#44475a",
    editor_gutter_bg="#181825",
    editor_gutter_fg="#6c7086",
    tab_background="#181825",
    tab_active_background="#1e1e2e",
    tab_hover_background="#313244",
    tab_border="#313244",
    browser_background="#181825",
    browser_item_hover="#313244",
    browser_item_selected="#45475a",
    terminal_background="#11111b",
    terminal_foreground="#cdd6f4",
    scrollbar_background="#181825",
    scrollbar_handle="#45475a",
    scrollbar_handle_hover="#585b70",
    button_background="#45475a",
    button_foreground="#cdd6f4",
    button_hover="#585b70",
    button_pressed="#313244",
    input_background="#313244",
    input_border="#45475a",
    input_focus_border="#89b4fa",
    success="#a6e3a1",
    warning="#f9e2af",
    error="#f38ba8",
    info="#89b4fa",
    syntax=SyntaxColors(
        keyword="#cba6f7",
        builtin="#f9e2af",
        type="#94e2d5",
        string="#a6e3a1",
        number="#fab387",
        comment="#6c7086",
        operator="#94e2d5",
        function="#89b4fa",
        variable="#f38ba8",
        constant="#fab387",
        identifier="#cdd6f4",
        interpolation="#cba6f7"
    )
)


# Built-in Light Theme
LIGHT_THEME = Theme(
    name="Light",
    is_dark=False,
    background="#eff1f5",
    foreground="#4c4f69",
    accent="#1e66f5",
    accent_hover="#2a7afd",
    panel_background="#e6e9ef",
    panel_border="#bcc0cc",
    editor_background="#eff1f5",
    editor_foreground="#4c4f69",
    editor_line_highlight="#dce0e8",
    editor_selection="#acb0be",
    editor_gutter_bg="#e6e9ef",
    editor_gutter_fg="#8c8fa1",
    tab_background="#e6e9ef",
    tab_active_background="#eff1f5",
    tab_hover_background="#ccd0da",
    tab_border="#bcc0cc",
    browser_background="#e6e9ef",
    browser_item_hover="#ccd0da",
    browser_item_selected="#bcc0cc",
    terminal_background="#dce0e8",
    terminal_foreground="#4c4f69",
    scrollbar_background="#e6e9ef",
    scrollbar_handle="#bcc0cc",
    scrollbar_handle_hover="#acb0be",
    button_background="#bcc0cc",
    button_foreground="#4c4f69",
    button_hover="#acb0be",
    button_pressed="#ccd0da",
    input_background="#ccd0da",
    input_border="#bcc0cc",
    input_focus_border="#1e66f5",
    success="#40a02b",
    warning="#df8e1d",
    error="#d20f39",
    info="#1e66f5",
    syntax=SyntaxColors(
        keyword="#8839ef",
        builtin="#df8e1d",
        type="#179299",
        string="#40a02b",
        number="#fe640b",
        comment="#8c8fa1",
        operator="#179299",
        function="#1e66f5",
        variable="#d20f39",
        constant="#fe640b",
        identifier="#4c4f69",
        interpolation="#8839ef"
    )
)


BUILTIN_THEMES = {
    "dark": DARK_THEME,
    "light": LIGHT_THEME,
}


class ThemeManager:
    """Manages themes for the IDE"""

    def __init__(self, settings: SettingsManager):
        self.settings = settings
        self.themes = dict(BUILTIN_THEMES)
        self.custom_themes_dir = get_config_dir() / "themes"
        self.custom_themes_dir.mkdir(parents=True, exist_ok=True)
        self._current_theme: Optional[Theme] = None

    def get_theme(self, name: str) -> Theme:
        """Get a theme by name"""
        return self.themes.get(name.lower(), DARK_THEME)

    def get_current_theme(self) -> Theme:
        """Get the currently active theme"""
        if self._current_theme is None:
            theme_name = self.settings.settings.theme.current_theme
            self._current_theme = self.get_theme(theme_name)
        return self._current_theme

    def set_theme(self, name: str):
        """Set the current theme"""
        self.settings.settings.theme.current_theme = name
        self._current_theme = self.get_theme(name)
        self.settings.save()

    def get_available_themes(self) -> list:
        """Get list of available theme names"""
        return list(self.themes.keys())

    def get_current_stylesheet(self) -> str:
        """Generate Qt stylesheet for current theme"""
        return self.generate_stylesheet(self.get_current_theme())

    def generate_stylesheet(self, theme: Theme) -> str:
        """Generate a complete Qt stylesheet from a theme"""
        return f"""
/* Main Window */
QMainWindow, QWidget {{
    background-color: {theme.background};
    color: {theme.foreground};
    font-family: "Segoe UI", "SF Pro Display", "Ubuntu", sans-serif;
    font-size: 13px;
}}

/* Menu Bar */
QMenuBar {{
    background-color: {theme.panel_background};
    color: {theme.foreground};
    border-bottom: 1px solid {theme.panel_border};
    padding: 4px 0px;
}}

QMenuBar::item {{
    background: transparent;
    padding: 6px 12px;
    border-radius: 4px;
    margin: 0 2px;
}}

QMenuBar::item:selected {{
    background-color: {theme.button_hover};
}}

/* Menus */
QMenu {{
    background-color: {theme.panel_background};
    color: {theme.foreground};
    border: 1px solid {theme.panel_border};
    border-radius: 8px;
    padding: 6px;
}}

QMenu::item {{
    padding: 8px 32px 8px 24px;
    border-radius: 4px;
}}

QMenu::item:selected {{
    background-color: {theme.accent};
    color: {theme.background};
}}

/* Toolbar */
QToolBar {{
    background-color: {theme.panel_background};
    border: none;
    padding: 4px;
    spacing: 4px;
}}

QToolButton {{
    background-color: transparent;
    border: none;
    border-radius: 6px;
    padding: 8px;
    margin: 2px;
}}

QToolButton:hover {{
    background-color: {theme.button_hover};
}}

/* Tabs */
QTabWidget::pane {{
    border: none;
    background-color: {theme.editor_background};
}}

QTabBar::tab {{
    background-color: {theme.tab_background};
    color: {theme.foreground};
    border: none;
    border-bottom: 2px solid transparent;
    padding: 10px 20px;
}}

QTabBar::tab:selected {{
    background-color: {theme.tab_active_background};
    border-bottom: 2px solid {theme.accent};
}}

QTabBar::tab:hover:!selected {{
    background-color: {theme.tab_hover_background};
}}

/* Splitter */
QSplitter::handle {{
    background-color: {theme.panel_border};
}}

QSplitter::handle:horizontal {{
    width: 2px;
}}

QSplitter::handle:vertical {{
    height: 2px;
}}

/* Scrollbars */
QScrollBar:vertical {{
    background: {theme.scrollbar_background};
    width: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:vertical {{
    background: {theme.scrollbar_handle};
    border-radius: 5px;
    min-height: 30px;
    margin: 2px;
}}

QScrollBar::handle:vertical:hover {{
    background: {theme.scrollbar_handle_hover};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background: {theme.scrollbar_background};
    height: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:horizontal {{
    background: {theme.scrollbar_handle};
    border-radius: 5px;
    min-width: 30px;
    margin: 2px;
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* Tree View (File Browser) */
QTreeView {{
    background-color: {theme.browser_background};
    color: {theme.foreground};
    border: none;
    padding: 4px;
}}

QTreeView::item {{
    padding: 6px 8px;
    border-radius: 4px;
}}

QTreeView::item:hover {{
    background-color: {theme.browser_item_hover};
}}

QTreeView::item:selected {{
    background-color: {theme.browser_item_selected};
}}

/* Push Button */
QPushButton {{
    background-color: {theme.button_background};
    color: {theme.button_foreground};
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
}}

QPushButton:hover {{
    background-color: {theme.button_hover};
}}

/* Line Edit */
QLineEdit {{
    background-color: {theme.input_background};
    color: {theme.foreground};
    border: 1px solid {theme.input_border};
    border-radius: 6px;
    padding: 8px 12px;
}}

QLineEdit:focus {{
    border-color: {theme.input_focus_border};
}}

/* Status Bar */
QStatusBar {{
    background-color: {theme.panel_background};
    color: {theme.foreground};
    border-top: 1px solid {theme.panel_border};
    padding: 4px;
}}
"""

