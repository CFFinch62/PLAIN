"""
User Interface module for SCAT (Source Code Analysis Tool).

This module provides the graphical user interface components for the
Source Code Analysis Tool, including the main window, dialogs, and widgets.
"""

from .main_window import SCATMainWindow
from .components import *
from .themes import SCATTheme

__all__ = [
    'SCATMainWindow',
    'SCATTheme'
]

__version__ = '2.0.0'
