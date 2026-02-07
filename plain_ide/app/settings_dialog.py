"""
Settings Dialog for PLAIN IDE
Provides a preferences UI for configuring IDE settings
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QSpinBox, QCheckBox, QComboBox, QLineEdit,
    QPushButton, QGroupBox, QFormLayout, QTreeWidget, QTreeWidgetItem,
    QHeaderView
)
from PyQt6.QtCore import Qt

from plain_ide.app.settings import SettingsManager
from plain_ide.app.themes import ThemeManager, Theme


# Keyboard shortcuts reference table
SHORTCUTS = [
    ("File", "New File", "Ctrl+N"),
    ("File", "Open File", "Ctrl+O"),
    ("File", "Open Folder", "Ctrl+Shift+O"),
    ("File", "Save", "Ctrl+S"),
    ("File", "Save As", "Ctrl+Shift+S"),
    ("File", "Exit", "Ctrl+Q"),
    ("Edit", "Undo", "Ctrl+Z"),
    ("Edit", "Redo", "Ctrl+Shift+Z"),
    ("Edit", "Cut", "Ctrl+X"),
    ("Edit", "Copy", "Ctrl+C"),
    ("Edit", "Paste", "Ctrl+V"),
    ("Edit", "Find", "Ctrl+F"),
    ("Edit", "Replace", "Ctrl+H"),
    ("Edit", "Preferences", "Ctrl+,"),
    ("View", "Toggle File Browser", "Ctrl+B"),
    ("View", "Toggle Terminal", "Ctrl+`"),
    ("Run", "Run", "F5"),
    ("Run", "Stop", "Shift+F5"),
    ("Debug", "Debug", "F6"),
    ("Debug", "Continue", "F8"),
    ("Debug", "Toggle Breakpoint", "F9"),
    ("Debug", "Step Over", "F10"),
    ("Debug", "Step Into", "F11"),
    ("Debug", "Toggle Debug Panel", "Ctrl+D"),
    ("Help", "Quick Reference", "F1"),
]


class SettingsDialog(QDialog):
    """Preferences dialog for IDE settings"""

    def __init__(self, settings: SettingsManager, theme_manager: ThemeManager,
                 parent=None):
        super().__init__(parent)
        self.settings_manager = settings
        self.theme_manager = theme_manager
        self.setWindowTitle("Preferences")
        self.setMinimumSize(500, 450)
        self._setup_ui()
        self._load_current_settings()

    def _setup_ui(self):
        """Set up the dialog UI"""
        layout = QVBoxLayout(self)

        # Tab widget
        self.tabs = QTabWidget()

        # Editor tab
        self.tabs.addTab(self._create_editor_tab(), "Editor")

        # Theme tab
        self.tabs.addTab(self._create_theme_tab(), "Theme")

        # Terminal tab
        self.tabs.addTab(self._create_terminal_tab(), "Terminal")

        # Shortcuts tab
        self.tabs.addTab(self._create_shortcuts_tab(), "Shortcuts")

        layout.addWidget(self.tabs)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self._apply_settings)
        btn_layout.addWidget(apply_btn)

        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self._ok_clicked)
        btn_layout.addWidget(ok_btn)

        layout.addLayout(btn_layout)

    def _create_editor_tab(self) -> QWidget:
        """Create the editor settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Font group
        font_group = QGroupBox("Font")
        font_layout = QFormLayout()

        self.font_family_input = QLineEdit()
        font_layout.addRow("Font Family:", self.font_family_input)

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 32)
        font_layout.addRow("Font Size:", self.font_size_spin)

        font_group.setLayout(font_layout)
        layout.addWidget(font_group)

        # Editor behavior group
        behavior_group = QGroupBox("Behavior")
        behavior_layout = QVBoxLayout()

        self.tab_width_spin = QSpinBox()
        self.tab_width_spin.setRange(2, 8)
        tab_row = QHBoxLayout()
        tab_row.addWidget(QLabel("Tab Width:"))
        tab_row.addWidget(self.tab_width_spin)
        tab_row.addStretch()
        behavior_layout.addLayout(tab_row)

        self.word_wrap_check = QCheckBox("Word Wrap")
        behavior_layout.addWidget(self.word_wrap_check)

        self.line_numbers_check = QCheckBox("Show Line Numbers")
        behavior_layout.addWidget(self.line_numbers_check)

        self.highlight_line_check = QCheckBox("Highlight Current Line")
        behavior_layout.addWidget(self.highlight_line_check)

        self.bracket_matching_check = QCheckBox("Bracket Matching")
        behavior_layout.addWidget(self.bracket_matching_check)

        behavior_group.setLayout(behavior_layout)
        layout.addWidget(behavior_group)

        layout.addStretch()
        return tab

    def _create_theme_tab(self) -> QWidget:
        """Create the theme settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        theme_group = QGroupBox("Theme Selection")
        theme_layout = QVBoxLayout()

        self.theme_combo = QComboBox()
        for name in self.theme_manager.get_available_themes():
            self.theme_combo.addItem(name.capitalize(), name)
        theme_layout.addWidget(self.theme_combo)

        # Theme preview
        self.preview_label = QLabel()
        self.preview_label.setFixedHeight(80)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._update_preview()
        self.theme_combo.currentIndexChanged.connect(self._update_preview)
        theme_layout.addWidget(self.preview_label)

        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)

        layout.addStretch()
        return tab

    def _create_terminal_tab(self) -> QWidget:
        """Create the terminal settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        font_group = QGroupBox("Terminal Font")
        font_layout = QFormLayout()

        self.terminal_font_input = QLineEdit()
        font_layout.addRow("Font Family:", self.terminal_font_input)

        self.terminal_font_size_spin = QSpinBox()
        self.terminal_font_size_spin.setRange(8, 24)
        font_layout.addRow("Font Size:", self.terminal_font_size_spin)

        font_group.setLayout(font_layout)
        layout.addWidget(font_group)

        layout.addStretch()
        return tab

    def _create_shortcuts_tab(self) -> QWidget:
        """Create the keyboard shortcuts tab (read-only reference)"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        info_label = QLabel("Current keyboard shortcuts:")
        layout.addWidget(info_label)

        tree = QTreeWidget()
        tree.setHeaderLabels(["Action", "Shortcut", "Category"])
        tree.setRootIsDecorated(False)
        tree.setAlternatingRowColors(True)
        tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        tree.header().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        for category, action, shortcut in SHORTCUTS:
            item = QTreeWidgetItem([action, shortcut, category])
            tree.addTopLevelItem(item)

        layout.addWidget(tree)
        return tab

    def _load_current_settings(self):
        """Load current settings into the dialog"""
        s = self.settings_manager.settings

        # Editor
        self.font_family_input.setText(s.editor.font_family)
        self.font_size_spin.setValue(s.editor.font_size)
        self.tab_width_spin.setValue(s.editor.tab_width)
        self.word_wrap_check.setChecked(s.editor.word_wrap)
        self.line_numbers_check.setChecked(s.editor.show_line_numbers)
        self.highlight_line_check.setChecked(s.editor.highlight_current_line)
        self.bracket_matching_check.setChecked(s.editor.bracket_matching)

        # Theme
        idx = self.theme_combo.findData(s.theme.current_theme)
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)

        # Terminal
        self.terminal_font_input.setText(s.terminal.font_family)
        self.terminal_font_size_spin.setValue(s.terminal.font_size)

    def _update_preview(self):
        """Update the theme preview swatch"""
        name = self.theme_combo.currentData()
        if name:
            theme = self.theme_manager.get_theme(name)
            self.preview_label.setStyleSheet(f"""
                background-color: {theme.editor_background};
                color: {theme.editor_foreground};
                border: 1px solid {theme.panel_border};
                border-radius: 6px;
                padding: 8px;
                font-family: monospace;
                font-size: 12px;
            """)
            # Show sample code with theme colors
            self.preview_label.setText(
                f"var intCount = 10\n"
                f'display("Hello, PLAIN!")\n'
                f"rem: {theme.name} theme"
            )

    def _apply_settings(self):
        """Apply settings without closing"""
        s = self.settings_manager.settings

        # Editor
        s.editor.font_family = self.font_family_input.text()
        s.editor.font_size = self.font_size_spin.value()
        s.editor.tab_width = self.tab_width_spin.value()
        s.editor.word_wrap = self.word_wrap_check.isChecked()
        s.editor.show_line_numbers = self.line_numbers_check.isChecked()
        s.editor.highlight_current_line = self.highlight_line_check.isChecked()
        s.editor.bracket_matching = self.bracket_matching_check.isChecked()

        # Theme
        new_theme = self.theme_combo.currentData()
        if new_theme and new_theme != s.theme.current_theme:
            s.theme.current_theme = new_theme

        # Terminal
        s.terminal.font_family = self.terminal_font_input.text()
        s.terminal.font_size = self.terminal_font_size_spin.value()

        self.settings_manager.save()

    def _ok_clicked(self):
        """Apply and close"""
        self._apply_settings()
        self.accept()

    def get_selected_theme(self) -> str:
        """Get the theme name selected in the dialog"""
        return self.theme_combo.currentData() or "dark"
