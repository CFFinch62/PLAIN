#!/usr/bin/env python3
"""
PLAIN IDE - A modern IDE for the PLAIN programming language
Based on the Steps IDE architecture
"""

import sys
import os

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon

from plain_ide.app.main_window import PlainIDEMainWindow
from plain_ide.app.settings import SettingsManager


def main():
    """Main entry point for the PLAIN IDE"""
    # Enable high DPI scaling
    app = QApplication(sys.argv)
    app.setApplicationName("PLAIN IDE")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("PLAIN Language")
    
    # Load settings
    settings = SettingsManager()
    
    # Apply theme
    from plain_ide.app.themes import ThemeManager
    theme_manager = ThemeManager(settings)
    app.setStyleSheet(theme_manager.get_current_stylesheet())
    
    # Create and show main window
    window = PlainIDEMainWindow(settings, theme_manager)
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

