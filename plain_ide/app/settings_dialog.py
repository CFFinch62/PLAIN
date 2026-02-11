"""
Settings Dialog for PLAIN IDE
Provides a preferences UI for configuring IDE settings
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QSpinBox, QCheckBox, QComboBox, QLineEdit,
    QPushButton, QGroupBox, QFormLayout, QTreeWidget, QTreeWidgetItem,
    QHeaderView, QFontComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFontDatabase

from plain_ide.app.settings import SettingsManager
from plain_ide.app.themes import ThemeManager


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

    settings_applied = pyqtSignal()  # Signal emitted when settings are applied

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

        self.font_family_input = QFontComboBox()
        self.font_family_input.setFontFilters(QFontComboBox.FontFilter.MonospacedFonts)
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

        # UI Theme group
        ui_theme_group = QGroupBox("UI Theme")
        ui_theme_layout = QVBoxLayout()

        self.ui_theme_combo = QComboBox()
        for name in self.theme_manager.get_available_ui_themes():
            self.ui_theme_combo.addItem(name.replace('_', ' ').title(), name)
        ui_theme_layout.addWidget(self.ui_theme_combo)

        ui_theme_group.setLayout(ui_theme_layout)
        layout.addWidget(ui_theme_group)

        # Syntax Theme group
        syntax_theme_group = QGroupBox("Syntax Theme")
        syntax_theme_layout = QVBoxLayout()

        self.syntax_theme_combo = QComboBox()
        for name in self.theme_manager.get_available_syntax_themes():
            self.syntax_theme_combo.addItem(name.replace('_', ' ').title(), name)
        syntax_theme_layout.addWidget(self.syntax_theme_combo)

        syntax_theme_group.setLayout(syntax_theme_layout)
        layout.addWidget(syntax_theme_group)

        # Theme preview
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout()
        
        self.preview_label = QLabel()
        self.preview_label.setFixedHeight(100)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.preview_label.setWordWrap(True)
        self._update_preview()
        self.ui_theme_combo.currentIndexChanged.connect(self._update_preview)
        self.syntax_theme_combo.currentIndexChanged.connect(self._update_preview)
        preview_layout.addWidget(self.preview_label)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        layout.addStretch()
        return tab

    def _create_terminal_tab(self) -> QWidget:
        """Create the terminal settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        font_group = QGroupBox("Terminal Font")
        font_layout = QFormLayout()

        self.terminal_font_input = QFontComboBox()
        self.terminal_font_input.setFontFilters(QFontComboBox.FontFilter.MonospacedFonts)
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
        self.font_family_input.setCurrentText(s.editor.font_family)
        self.font_size_spin.setValue(s.editor.font_size)
        self.tab_width_spin.setValue(s.editor.tab_width)
        self.word_wrap_check.setChecked(s.editor.word_wrap)
        self.line_numbers_check.setChecked(s.editor.show_line_numbers)
        self.highlight_line_check.setChecked(s.editor.highlight_current_line)
        self.bracket_matching_check.setChecked(s.editor.bracket_matching)

        # Theme - load both UI and syntax themes
        ui_theme = getattr(s.theme, 'ui_theme', s.theme.current_theme)
        syntax_theme = getattr(s.theme, 'syntax_theme', 'default')
        
        ui_idx = self.ui_theme_combo.findData(ui_theme)
        if ui_idx >= 0:
            self.ui_theme_combo.setCurrentIndex(ui_idx)
        
        syntax_idx = self.syntax_theme_combo.findData(syntax_theme)
        if syntax_idx >= 0:
            self.syntax_theme_combo.setCurrentIndex(syntax_idx)

        # Terminal
        self.terminal_font_input.setCurrentText(s.terminal.font_family)
        self.terminal_font_size_spin.setValue(s.terminal.font_size)

    def _update_preview(self):
        """Update the theme preview swatch"""
        ui_theme_name = self.ui_theme_combo.currentData()
        syntax_theme_name = self.syntax_theme_combo.currentData()
        
        if ui_theme_name and syntax_theme_name:
            ui_theme = self.theme_manager.get_ui_theme(ui_theme_name)
            syntax_theme = self.theme_manager.get_syntax_theme(syntax_theme_name)
            
            self.preview_label.setStyleSheet(f"""
                background-color: {ui_theme.editor_background};
                color: {ui_theme.editor_foreground};
                border: 1px solid {ui_theme.panel_border};
                border-radius: 6px;
                padding: 12px;
                font-family: monospace;
                font-size: 11px;
            """)
            
            # Show sample code with syntax highlighting colors
            sample_html = f'''
                <span style="color: {syntax_theme.keyword};">var</span> 
                <span style="color: {syntax_theme.identifier};">intCount</span> 
                <span style="color: {syntax_theme.operator};">=</span> 
                <span style="color: {syntax_theme.number};">10</span><br>
                <span style="color: {syntax_theme.function};">display</span>
                <span style="color: {ui_theme.foreground};">(</span>
                <span style="color: {syntax_theme.string};">"Hello, PLAIN!"</span>
                <span style="color: {ui_theme.foreground};">)</span><br>
                <span style="color: {syntax_theme.comment};">rem: Combined theme preview</span>
            '''
            self.preview_label.setText(sample_html)

    def _apply_settings(self):
        """Apply settings without closing"""
        s = self.settings_manager.settings

        # Editor
        s.editor.font_family = self.font_family_input.currentText()
        s.editor.font_size = self.font_size_spin.value()
        s.editor.tab_width = self.tab_width_spin.value()
        s.editor.word_wrap = self.word_wrap_check.isChecked()
        s.editor.show_line_numbers = self.line_numbers_check.isChecked()
        s.editor.highlight_current_line = self.highlight_line_check.isChecked()
        s.editor.bracket_matching = self.bracket_matching_check.isChecked()

        # Theme - save both UI and syntax themes
        new_ui_theme = self.ui_theme_combo.currentData()
        new_syntax_theme = self.syntax_theme_combo.currentData()
        
        if new_ui_theme:
            s.theme.ui_theme = new_ui_theme
            s.theme.current_theme = new_ui_theme  # Keep for backward compatibility
            self.theme_manager.set_ui_theme(new_ui_theme)
        
        if new_syntax_theme:
            s.theme.syntax_theme = new_syntax_theme
            self.theme_manager.set_syntax_theme(new_syntax_theme)

        # Terminal
        s.terminal.font_family = self.terminal_font_input.currentText()
        s.terminal.font_size = self.terminal_font_size_spin.value()

        self.settings_manager.save()

        # Emit signal so main window can apply settings immediately
        self.settings_applied.emit()

    def _ok_clicked(self):
        """Apply and close"""
        self._apply_settings()
        self.accept()

    def get_selected_ui_theme(self) -> str:
        """Get the UI theme name selected in the dialog"""
        return self.ui_theme_combo.currentData() or "dark"
    
    def get_selected_syntax_theme(self) -> str:
        """Get the syntax theme name selected in the dialog"""
        return self.syntax_theme_combo.currentData() or "default"
