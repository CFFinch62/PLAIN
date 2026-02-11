"""
Terminal Widget for PLAIN IDE
Provides an output terminal for running PLAIN programs
"""

import subprocess
import os
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QProcess, QThread
from PyQt6.QtGui import QFont, QColor, QTextCursor, QKeyEvent

from plain_ide.app.themes import Theme
from plain_ide.app.settings import SettingsManager


class TerminalOutput(QPlainTextEdit):
    """Custom terminal output widget that handles user input"""

    input_submitted = pyqtSignal(str)  # Signal emitted when user presses Enter

    def __init__(self, parent=None):
        super().__init__(parent)
        self.input_start_pos = 0  # Position where current input line starts
        self.input_enabled = False  # Whether input is currently allowed

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key presses for input"""
        if not self.input_enabled:
            # If input is disabled, only allow navigation and copying
            if event.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Left,
                             Qt.Key.Key_Right, Qt.Key.Key_Home, Qt.Key.Key_End,
                             Qt.Key.Key_PageUp, Qt.Key.Key_PageDown):
                super().keyPressEvent(event)
            elif event.matches(QKeySequence.StandardKey.Copy):
                super().keyPressEvent(event)
            return

        # Input is enabled - handle text input
        cursor = self.textCursor()

        # Don't allow editing before the input start position
        if cursor.position() < self.input_start_pos:
            if event.key() not in (Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Left,
                                   Qt.Key.Key_Right, Qt.Key.Key_Home, Qt.Key.Key_End):
                cursor.setPosition(self.input_start_pos)
                self.setTextCursor(cursor)

        # Handle Enter key - submit input
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            # Get the input text (from input_start_pos to end)
            cursor.setPosition(self.input_start_pos)
            cursor.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
            input_text = cursor.selectedText()

            # Move cursor to end and add newline
            cursor.clearSelection()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.setTextCursor(cursor)
            self.appendPlainText("")  # Add newline

            # Emit the input
            self.input_submitted.emit(input_text)

            # Update input start position for next input
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.input_start_pos = cursor.position()
        else:
            # Handle normal text input
            super().keyPressEvent(event)

    def enable_input(self):
        """Enable input mode and mark where input starts"""
        self.input_enabled = True
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)
        self.input_start_pos = cursor.position()
        self.setReadOnly(False)

    def disable_input(self):
        """Disable input mode"""
        self.input_enabled = False
        self.setReadOnly(True)


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
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setFixedHeight(28)
        self.clear_btn.clicked.connect(self.clear)
        control_layout.addWidget(self.clear_btn)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setFixedHeight(28)
        self.stop_btn.clicked.connect(self.stop_execution)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)
        
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        # Output area
        self.output = TerminalOutput()
        self.output.setReadOnly(True)
        self.output.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.output.input_submitted.connect(self._on_input_submitted)
        
        # Set monospace font
        if self.settings:
            font = QFont(self.settings.settings.terminal.font_family, 
                        self.settings.settings.terminal.font_size)
        else:
            font = QFont("JetBrains Mono", 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.output.setFont(font)
        
        layout.addWidget(self.output)
    
    def apply_settings(self):
        """Apply terminal settings (font)"""
        if self.settings:
            font = QFont(self.settings.settings.terminal.font_family,
                        self.settings.settings.terminal.font_size)
            font.setStyleHint(QFont.StyleHint.Monospace)
            self.output.setFont(font)
            # Reapply theme to ensure font is included in stylesheet
            if self.theme:
                self.apply_theme(self.theme)

    def apply_theme(self, theme: Theme):
        """Apply theme to terminal"""
        self.theme = theme

        # Get font settings
        if self.settings:
            font_family = self.settings.settings.terminal.font_family
            font_size = self.settings.settings.terminal.font_size
        else:
            font_family = "JetBrains Mono"
            font_size = 11

        self.output.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {theme.terminal_background};
                color: {theme.terminal_foreground};
                border: none;
                padding: 8px;
                font-family: "{font_family}", monospace;
                font-size: {font_size}pt;
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

        # Update input start position so user can't edit program output
        if self.output.input_enabled:
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.output.input_start_pos = cursor.position()
    
    def write_line(self, text: str, color: str = None):
        """Write a line to terminal"""
        self.write(text + "\n", color)
    
    def run_plain_file(self, file_path: str, plain_executable: str = None):
        """Run a PLAIN file using the PLAIN interpreter"""
        if self.process is not None:
            self.write_line("[!] A program is already running!", self.theme.warning if self.theme else None)
            return
        
        # Find PLAIN executable using multiple strategies
        if plain_executable is None:
            plain_executable = self._find_plain_interpreter()
        
        if not plain_executable:
            self.clear()
            self.write_line("[ERROR] PLAIN interpreter not found!", self.theme.error if self.theme else None)
            self.write_line("")
            self.write_line("Please ensure the 'plain' executable is:")
            self.write_line("  1. In your PATH, or")
            self.write_line("  2. In the same directory as the IDE")
            return
        
        self.clear()
        self.write_line(f"[>] Running: {file_path}", self.theme.info if self.theme else None)
        self.write_line(f"[>] Interpreter: {plain_executable}", self.theme.info if self.theme else None)
        self.write_line("-" * 50)
        
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self._on_stdout)
        self.process.readyReadStandardError.connect(self._on_stderr)
        self.process.finished.connect(self._on_finished)

        self.process.start(plain_executable, [file_path])
        self.stop_btn.setEnabled(True)

        # Enable input so user can provide input when program requests it
        self.output.enable_input()
    
    def _find_plain_interpreter(self) -> str:
        """Find the PLAIN interpreter using multiple strategies"""
        import shutil
        import sys
        
        # Strategy 1: Check settings for configured path
        if self.settings and self.settings.settings.plain_interpreter_path:
            path = Path(self.settings.settings.plain_interpreter_path)
            if path.exists() and path.is_file():
                return str(path)
        
        # Strategy 2: Check PATH
        plain_in_path = shutil.which("plain")
        if plain_in_path:
            return plain_in_path
        
        # Strategy 3: Check same directory as IDE executable
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            exe_dir = Path(sys.executable).parent
        else:
            # Running from source
            exe_dir = Path(__file__).parent.parent.parent
        
        plain_exe = exe_dir / "plain"
        if plain_exe.exists():
            return str(plain_exe)
        
        # Strategy 4: Check ../plain (for installed IDE where plain is in parent dir)
        parent_plain = exe_dir.parent / "plain"
        if parent_plain.exists():
            return str(parent_plain)
        
        return None
    
    def stop_execution(self):
        """Stop the running program"""
        if self.process:
            self.process.kill()
            self.output.disable_input()
            self.write_line("\n[STOPPED] Program terminated.", self.theme.warning if self.theme else None)
    
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
        # Disable input if it was enabled
        self.output.disable_input()

        self.write_line("-" * 50)
        if exit_code == 0:
            self.write_line(f"[OK] Program finished successfully.", self.theme.success if self.theme else None)
        else:
            self.write_line(f"[ERROR] Program exited with code {exit_code}", self.theme.error if self.theme else None)

        self.process = None
        self.stop_btn.setEnabled(False)
        self.execution_finished.emit(exit_code)

    def _on_input_submitted(self, text: str):
        """Handle input submitted by user"""
        if self.process:
            # Send input to process stdin
            data = (text + "\n").encode('utf-8')
            self.process.write(data)

