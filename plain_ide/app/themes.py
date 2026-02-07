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


# Monokai Theme
MONOKAI_THEME = Theme(
    name="Monokai",
    is_dark=True,
    background="#272822",
    foreground="#f8f8f2",
    accent="#a6e22e",
    accent_hover="#b6f23e",
    panel_background="#1e1f1c",
    panel_border="#3e3d32",
    editor_background="#272822",
    editor_foreground="#f8f8f2",
    editor_line_highlight="#3e3d32",
    editor_selection="#49483e",
    editor_gutter_bg="#1e1f1c",
    editor_gutter_fg="#75715e",
    tab_background="#1e1f1c",
    tab_active_background="#272822",
    tab_hover_background="#3e3d32",
    tab_border="#3e3d32",
    browser_background="#1e1f1c",
    browser_item_hover="#3e3d32",
    browser_item_selected="#49483e",
    terminal_background="#1a1b16",
    terminal_foreground="#f8f8f2",
    scrollbar_background="#1e1f1c",
    scrollbar_handle="#49483e",
    scrollbar_handle_hover="#5e5d53",
    button_background="#49483e",
    button_foreground="#f8f8f2",
    button_hover="#5e5d53",
    button_pressed="#3e3d32",
    input_background="#3e3d32",
    input_border="#49483e",
    input_focus_border="#a6e22e",
    success="#a6e22e",
    warning="#e6db74",
    error="#f92672",
    info="#66d9ef",
    syntax=SyntaxColors(
        keyword="#f92672",
        builtin="#66d9ef",
        type="#66d9ef",
        string="#e6db74",
        number="#ae81ff",
        comment="#75715e",
        operator="#f92672",
        function="#a6e22e",
        variable="#fd971f",
        constant="#ae81ff",
        identifier="#f8f8f2",
        interpolation="#f92672"
    )
)


# Nord Theme
NORD_THEME = Theme(
    name="Nord",
    is_dark=True,
    background="#2e3440",
    foreground="#d8dee9",
    accent="#88c0d0",
    accent_hover="#8fbcbb",
    panel_background="#292e39",
    panel_border="#3b4252",
    editor_background="#2e3440",
    editor_foreground="#d8dee9",
    editor_line_highlight="#3b4252",
    editor_selection="#434c5e",
    editor_gutter_bg="#292e39",
    editor_gutter_fg="#4c566a",
    tab_background="#292e39",
    tab_active_background="#2e3440",
    tab_hover_background="#3b4252",
    tab_border="#3b4252",
    browser_background="#292e39",
    browser_item_hover="#3b4252",
    browser_item_selected="#434c5e",
    terminal_background="#242933",
    terminal_foreground="#d8dee9",
    scrollbar_background="#292e39",
    scrollbar_handle="#434c5e",
    scrollbar_handle_hover="#4c566a",
    button_background="#434c5e",
    button_foreground="#d8dee9",
    button_hover="#4c566a",
    button_pressed="#3b4252",
    input_background="#3b4252",
    input_border="#434c5e",
    input_focus_border="#88c0d0",
    success="#a3be8c",
    warning="#ebcb8b",
    error="#bf616a",
    info="#88c0d0",
    syntax=SyntaxColors(
        keyword="#81a1c1",
        builtin="#88c0d0",
        type="#8fbcbb",
        string="#a3be8c",
        number="#b48ead",
        comment="#616e88",
        operator="#81a1c1",
        function="#88c0d0",
        variable="#d08770",
        constant="#b48ead",
        identifier="#d8dee9",
        interpolation="#81a1c1"
    )
)


# Dracula Theme
DRACULA_THEME = Theme(
    name="Dracula",
    is_dark=True,
    background="#282a36",
    foreground="#f8f8f2",
    accent="#bd93f9",
    accent_hover="#caa9fa",
    panel_background="#21222c",
    panel_border="#44475a",
    editor_background="#282a36",
    editor_foreground="#f8f8f2",
    editor_line_highlight="#44475a",
    editor_selection="#44475a",
    editor_gutter_bg="#21222c",
    editor_gutter_fg="#6272a4",
    tab_background="#21222c",
    tab_active_background="#282a36",
    tab_hover_background="#44475a",
    tab_border="#44475a",
    browser_background="#21222c",
    browser_item_hover="#44475a",
    browser_item_selected="#6272a4",
    terminal_background="#1d1e28",
    terminal_foreground="#f8f8f2",
    scrollbar_background="#21222c",
    scrollbar_handle="#44475a",
    scrollbar_handle_hover="#6272a4",
    button_background="#44475a",
    button_foreground="#f8f8f2",
    button_hover="#6272a4",
    button_pressed="#383a46",
    input_background="#44475a",
    input_border="#6272a4",
    input_focus_border="#bd93f9",
    success="#50fa7b",
    warning="#f1fa8c",
    error="#ff5555",
    info="#8be9fd",
    syntax=SyntaxColors(
        keyword="#ff79c6",
        builtin="#8be9fd",
        type="#8be9fd",
        string="#f1fa8c",
        number="#bd93f9",
        comment="#6272a4",
        operator="#ff79c6",
        function="#50fa7b",
        variable="#ffb86c",
        constant="#bd93f9",
        identifier="#f8f8f2",
        interpolation="#ff79c6"
    )
)


# Solarized Dark Theme
SOLARIZED_THEME = Theme(
    name="Solarized",
    is_dark=True,
    background="#002b36",
    foreground="#839496",
    accent="#268bd2",
    accent_hover="#2aa1f5",
    panel_background="#00252f",
    panel_border="#073642",
    editor_background="#002b36",
    editor_foreground="#839496",
    editor_line_highlight="#073642",
    editor_selection="#073642",
    editor_gutter_bg="#00252f",
    editor_gutter_fg="#586e75",
    tab_background="#00252f",
    tab_active_background="#002b36",
    tab_hover_background="#073642",
    tab_border="#073642",
    browser_background="#00252f",
    browser_item_hover="#073642",
    browser_item_selected="#0a4a5c",
    terminal_background="#001e26",
    terminal_foreground="#839496",
    scrollbar_background="#00252f",
    scrollbar_handle="#073642",
    scrollbar_handle_hover="#0a4a5c",
    button_background="#073642",
    button_foreground="#839496",
    button_hover="#0a4a5c",
    button_pressed="#00252f",
    input_background="#073642",
    input_border="#586e75",
    input_focus_border="#268bd2",
    success="#859900",
    warning="#b58900",
    error="#dc322f",
    info="#268bd2",
    syntax=SyntaxColors(
        keyword="#859900",
        builtin="#b58900",
        type="#2aa198",
        string="#2aa198",
        number="#d33682",
        comment="#586e75",
        operator="#859900",
        function="#268bd2",
        variable="#cb4b16",
        constant="#d33682",
        identifier="#839496",
        interpolation="#859900"
    )
)


BUILTIN_THEMES = {
    "dark": DARK_THEME,
    "light": LIGHT_THEME,
    "monokai": MONOKAI_THEME,
    "nord": NORD_THEME,
    "dracula": DRACULA_THEME,
    "solarized": SOLARIZED_THEME,
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

