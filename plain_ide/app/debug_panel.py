"""
Debug Panel Widget for PLAIN IDE
Provides debugging controls and variable inspection
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QToolButton, QLabel, QTreeWidget, QTreeWidgetItem,
    QPlainTextEdit
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont, QColor, QBrush

from plain_ide.app.themes import Theme


class VariablesView(QTreeWidget):
    """Tree view displaying variables organized by scope"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabels(["Name", "Value", "Type"])
        self.setColumnCount(3)
        self.setAlternatingRowColors(True)
        self.setIndentation(16)
        self.setColumnWidth(0, 120)
        self.setColumnWidth(1, 180)
        self.setColumnWidth(2, 80)
    
    def update_variables(self, variables: dict, scope_name: str = "Local"):
        """Update display with variables from a scope"""
        self.clear()
        
        if not variables:
            return
        
        scope_item = QTreeWidgetItem([f"📦 {scope_name}", "", ""])
        self.addTopLevelItem(scope_item)
        
        for name, info in variables.items():
            value = info.get("value", "")
            var_type = info.get("type", "unknown")
            
            item = QTreeWidgetItem(scope_item)
            item.setText(0, name)
            item.setText(1, str(value))
            item.setText(2, var_type)
            
            # Color-code by type
            type_colors = {
                "integer": QColor("#b5cea8"),
                "float": QColor("#b5cea8"),
                "string": QColor("#ce9178"),
                "boolean": QColor("#569cd6"),
                "list": QColor("#dcdcaa"),
                "table": QColor("#c586c0"),
                "null": QColor("#808080"),
            }
            color = type_colors.get(var_type, QColor("#d4d4d4"))
            item.setForeground(1, QBrush(color))
        
        scope_item.setExpanded(True)
    
    def apply_theme(self, theme: Theme):
        """Apply theme to variables view"""
        self.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {theme.panel_background};
                color: {theme.foreground};
                border: none;
            }}
            QTreeWidget::item {{
                padding: 4px;
            }}
            QTreeWidget::item:hover {{
                background-color: {theme.browser_item_hover};
            }}
            QTreeWidget::item:selected {{
                background-color: {theme.browser_item_selected};
            }}
        """)


class DebugPanel(QWidget):
    """Debug controls and variable display panel"""
    
    # Signals for debug actions
    step_into_clicked = pyqtSignal()
    step_over_clicked = pyqtSignal()
    continue_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    
    def __init__(self, parent=None, theme: Theme = None):
        super().__init__(parent)
        self.theme = theme
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the debug panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # Status label
        self.status_label = QLabel("Ready to debug")
        self.status_label.setStyleSheet("color: #888; font-style: italic;")
        layout.addWidget(self.status_label)
        
        # Toolbar with debug buttons
        toolbar = QHBoxLayout()
        toolbar.setSpacing(4)
        
        self.continue_btn = self._make_button("▶", "Continue (F5)", "#4CAF50")
        self.continue_btn.clicked.connect(self.continue_clicked.emit)
        toolbar.addWidget(self.continue_btn)
        
        self.step_into_btn = self._make_button("↓", "Step Into (F11)", "#2196F3")
        self.step_into_btn.clicked.connect(self.step_into_clicked.emit)
        toolbar.addWidget(self.step_into_btn)
        
        self.step_over_btn = self._make_button("→", "Step Over (F10)", "#2196F3")
        self.step_over_btn.clicked.connect(self.step_over_clicked.emit)
        toolbar.addWidget(self.step_over_btn)
        
        toolbar.addSpacing(10)
        
        self.stop_btn = self._make_button("■", "Stop (Shift+F5)", "#f44336")
        self.stop_btn.clicked.connect(self.stop_clicked.emit)
        toolbar.addWidget(self.stop_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Tab widget for Variables and Output
        self.tabs = QTabWidget()
        
        self.variables_view = VariablesView()
        self.tabs.addTab(self.variables_view, "Variables")
        
        # Debug output/trace
        self.trace_output = QPlainTextEdit()
        self.trace_output.setReadOnly(True)
        self.trace_output.setFont(QFont("JetBrains Mono", 10))
        self.tabs.addTab(self.trace_output, "Trace")
        
        layout.addWidget(self.tabs)
        
        # Start with controls disabled
        self._set_controls_enabled(False)
    
    def _make_button(self, text: str, tooltip: str, color: str = None) -> QToolButton:
        """Create a styled debug button"""
        btn = QToolButton()
        btn.setText(text)
        btn.setToolTip(tooltip)
        btn.setMinimumSize(32, 32)
        btn.setFont(QFont("", 14))
        if color:
            btn.setStyleSheet(f"QToolButton {{ color: {color}; }}")
        return btn
    
    def _set_controls_enabled(self, enabled: bool):
        """Enable or disable step controls"""
        self.continue_btn.setEnabled(enabled)
        self.step_into_btn.setEnabled(enabled)
        self.step_over_btn.setEnabled(enabled)
        self.stop_btn.setEnabled(enabled)

    def set_debugging_active(self, active: bool):
        """Set whether debugging is currently active"""
        self._set_controls_enabled(active)
        if active:
            self.status_label.setText("Debugging...")
            self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        else:
            self.status_label.setText("Ready to debug")
            self.status_label.setStyleSheet("color: #888; font-style: italic;")
            self.variables_view.clear()
            self.trace_output.clear()

    def set_paused(self, paused: bool, location_text: str = ""):
        """Update UI for paused/running state"""
        if paused:
            self.status_label.setText(f"Paused at {location_text}")
            self.status_label.setStyleSheet("color: #FFC107; font-weight: bold;")
        else:
            self.status_label.setText("Running...")
            self.status_label.setStyleSheet("color: #4CAF50;")

    def add_trace(self, text: str):
        """Add a line to the trace output"""
        self.trace_output.appendPlainText(text)

    def update_variables(self, variables: dict, scope_name: str = "Local"):
        """Update the variables display"""
        self.variables_view.update_variables(variables, scope_name)

    def apply_theme(self, theme: Theme):
        """Apply theme to debug panel"""
        self.theme = theme
        self.variables_view.apply_theme(theme)

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {theme.panel_background};
                color: {theme.foreground};
            }}
            QPlainTextEdit {{
                background-color: {theme.terminal_background};
                color: {theme.terminal_foreground};
                border: none;
            }}
            QTabWidget::pane {{
                border: none;
            }}
            QTabBar::tab {{
                background-color: {theme.tab_background};
                color: {theme.foreground};
                padding: 6px 12px;
                border: none;
            }}
            QTabBar::tab:selected {{
                background-color: {theme.tab_active_background};
                border-bottom: 2px solid {theme.accent};
            }}
        """)

