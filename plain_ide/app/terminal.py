"""
Terminal Widget for PLAIN IDE
Provides an output terminal for running PLAIN programs
"""

import subprocess
import os
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QProcess, QThread
from PyQt6.QtGui import QFont, QColor, QTextCursor

from plain_ide.app.themes import Theme
from plain_ide.app.settings import SettingsManager


class TerminalWidget(QWidget):
    """Terminal widget for program output"""
    
    execution_finished = pyqtSignal(int)  # Exit code
    
    def __init__(self, parent=None, theme: Theme = None, settings: SettingsManager = None):
        super().__init__(parent)
        self.theme = theme
        self.settings = settings
        self.process = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up terminal UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Control bar
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(8, 4, 8, 4)
        
        self.clear_btn = QPushButton("🗑 Clear")
        self.clear_btn.setFixedHeight(28)
        self.clear_btn.clicked.connect(self.clear)
        control_layout.addWidget(self.clear_btn)
        
        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.setFixedHeight(28)
        self.stop_btn.clicked.connect(self.stop_execution)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)
        
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        # Output area
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        
        # Set monospace font
        if self.settings:
            font = QFont(self.settings.settings.terminal.font_family, 
                        self.settings.settings.terminal.font_size)
        else:
            font = QFont("JetBrains Mono", 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.output.setFont(font)
        
        layout.addWidget(self.output)
    
    def apply_theme(self, theme: Theme):
        """Apply theme to terminal"""
        self.theme = theme
        self.output.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {theme.terminal_background};
                color: {theme.terminal_foreground};
                border: none;
                padding: 8px;
            }}
        """)
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {theme.panel_background};
            }}
            QPushButton {{
                background-color: {theme.button_background};
                color: {theme.button_foreground};
                border: none;
                border-radius: 4px;
                padding: 4px 12px;
            }}
            QPushButton:hover {{
                background-color: {theme.button_hover};
            }}
        """)
    
    def clear(self):
        """Clear terminal output"""
        self.output.clear()
    
    def write(self, text: str, color: str = None):
        """Write text to terminal"""
        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        if color and self.theme:
            cursor.insertHtml(f'<span style="color: {color}">{text}</span>')
        else:
            cursor.insertText(text)
        
        self.output.setTextCursor(cursor)
        self.output.ensureCursorVisible()
    
    def write_line(self, text: str, color: str = None):
        """Write a line to terminal"""
        self.write(text + "\n", color)
    
    def run_plain_file(self, file_path: str, plain_executable: str = None):
        """Run a PLAIN file using the PLAIN interpreter"""
        if self.process is not None:
            self.write_line("⚠ A program is already running!", self.theme.warning if self.theme else None)
            return
        
        # Find PLAIN executable
        if plain_executable is None:
            # Look for it relative to the IDE
            ide_dir = Path(__file__).parent.parent.parent
            plain_executable = str(ide_dir / "plain")
            
            if not Path(plain_executable).exists():
                # Try go run
                plain_executable = None
        
        self.clear()
        self.write_line(f"▶ Running: {file_path}", self.theme.info if self.theme else None)
        self.write_line("-" * 50)
        
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self._on_stdout)
        self.process.readyReadStandardError.connect(self._on_stderr)
        self.process.finished.connect(self._on_finished)
        
        if plain_executable:
            self.process.start(plain_executable, [file_path])
        else:
            # Use go run
            self.process.setWorkingDirectory(str(Path(__file__).parent.parent.parent))
            self.process.start("go", ["run", "./cmd/plain/", file_path])
        
        self.stop_btn.setEnabled(True)
    
    def stop_execution(self):
        """Stop the running program"""
        if self.process:
            self.process.kill()
            self.write_line("\n⏹ Program terminated.", self.theme.warning if self.theme else None)
    
    def _on_stdout(self):
        """Handle stdout from process"""
        data = self.process.readAllStandardOutput().data().decode('utf-8', errors='replace')
        self.write(data)
    
    def _on_stderr(self):
        """Handle stderr from process"""
        data = self.process.readAllStandardError().data().decode('utf-8', errors='replace')
        self.write(data, self.theme.error if self.theme else None)
    
    def _on_finished(self, exit_code, exit_status):
        """Handle process completion"""
        self.write_line("-" * 50)
        if exit_code == 0:
            self.write_line(f"✓ Program finished successfully.", self.theme.success if self.theme else None)
        else:
            self.write_line(f"✗ Program exited with code {exit_code}", self.theme.error if self.theme else None)
        
        self.process = None
        self.stop_btn.setEnabled(False)
        self.execution_finished.emit(exit_code)

