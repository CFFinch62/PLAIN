"""
Main Window for PLAIN IDE
The primary application window containing all IDE components
"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTabWidget, QMenuBar, QMenu, QToolBar, QStatusBar, QFileDialog,
    QMessageBox, QLabel
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QKeySequence

from plain_ide.app.settings import SettingsManager
from plain_ide.app.themes import ThemeManager, Theme
from plain_ide.app.editor import CodeEditor
from plain_ide.app.file_browser import FileBrowserWidget
from plain_ide.app.terminal import TerminalWidget
from plain_ide.app.debug_panel import DebugPanel
from plain_ide.app.debug_manager import DebugManager


class PlainIDEMainWindow(QMainWindow):
    """Main window for the PLAIN IDE"""

    def __init__(self, settings: SettingsManager, theme_manager: ThemeManager):
        super().__init__()
        self.settings = settings
        self.theme_manager = theme_manager
        self.editors = {}  # path -> CodeEditor
        self.debug_manager = DebugManager(self)
        self.current_project_path = None
        
        self._setup_ui()
        self._setup_menus()
        self._setup_toolbar()
        self._setup_statusbar()
        self._apply_settings()
        self._apply_theme()
    
    def _setup_ui(self):
        """Set up the main UI layout"""
        self.setWindowTitle("PLAIN IDE")
        
        # Central widget with main layout
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Main horizontal splitter (file browser | editor + terminal)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # File browser
        self.file_browser = FileBrowserWidget(theme=self.theme_manager.get_current_theme())
        self.file_browser.file_double_clicked.connect(self.open_file)
        self.main_splitter.addWidget(self.file_browser)
        
        # Middle: editor + terminal/debug in vertical splitter
        self.middle_splitter = QSplitter(Qt.Orientation.Vertical)

        # Tab widget for editors
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        self.middle_splitter.addWidget(self.tab_widget)

        # Terminal
        self.terminal = TerminalWidget(
            theme=self.theme_manager.get_current_theme(),
            settings=self.settings
        )
        self.middle_splitter.addWidget(self.terminal)

        # Set splitter proportions
        self.middle_splitter.setSizes([600, 200])

        self.main_splitter.addWidget(self.middle_splitter)

        # Debug panel on the right
        self.debug_panel = DebugPanel(theme=self.theme_manager.get_current_theme())
        self.debug_panel.setMinimumWidth(250)
        self.debug_panel.setVisible(False)  # Hidden by default
        self.debug_panel.continue_clicked.connect(self._debug_continue)
        self.debug_panel.step_into_clicked.connect(self._debug_step_into)
        self.debug_panel.step_over_clicked.connect(self._debug_step_over)
        self.debug_panel.stop_clicked.connect(self._debug_stop)
        self.main_splitter.addWidget(self.debug_panel)

        # Connect debug manager signals
        self.debug_manager.stopped.connect(self._on_debug_stopped)
        self.debug_manager.terminated.connect(self._on_debug_terminated)
        self.debug_manager.variables_received.connect(self._on_debug_variables)
        self.debug_manager.output_received.connect(self._on_debug_output)
        self.debug_manager.error_received.connect(self._on_debug_error)

        self.main_splitter.setSizes([250, 750, 0])
        
        main_layout.addWidget(self.main_splitter)
    
    def _setup_menus(self):
        """Set up the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("📄 New", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("📂 Open File...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_action)
        
        open_folder_action = QAction("📁 Open Folder...", self)
        open_folder_action.setShortcut("Ctrl+Shift+O")
        open_folder_action.triggered.connect(self.open_folder_dialog)
        file_menu.addAction(open_folder_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("💾 Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        undo_action = QAction("Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self._undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self._redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("Cut", self)
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(self._cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("Copy", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self._copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("Paste", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self._paste)
        edit_menu.addAction(paste_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        toggle_browser = QAction("📁 Toggle File Browser", self)
        toggle_browser.setShortcut("Ctrl+B")
        toggle_browser.triggered.connect(self._toggle_file_browser)
        view_menu.addAction(toggle_browser)

        toggle_terminal = QAction("🖥 Toggle Terminal", self)
        toggle_terminal.setShortcut("Ctrl+`")
        toggle_terminal.triggered.connect(self._toggle_terminal)
        view_menu.addAction(toggle_terminal)

        view_menu.addSeparator()

        # Theme submenu
        theme_menu = view_menu.addMenu("🎨 Theme")
        for theme_name in self.theme_manager.get_available_themes():
            theme_action = QAction(theme_name.capitalize(), self)
            theme_action.triggered.connect(lambda checked, n=theme_name: self._set_theme(n))
            theme_menu.addAction(theme_action)

        # Run menu
        run_menu = menubar.addMenu("&Run")

        run_action = QAction("▶ Run", self)
        run_action.setShortcut("F5")
        run_action.triggered.connect(self.run_current_file)
        run_menu.addAction(run_action)

        stop_action = QAction("⏹ Stop", self)
        stop_action.setShortcut("Shift+F5")
        stop_action.triggered.connect(self.terminal.stop_execution)
        run_menu.addAction(stop_action)

        # Debug menu
        debug_menu = menubar.addMenu("&Debug")

        debug_run_action = QAction("🐛 Debug", self)
        debug_run_action.setShortcut("F6")
        debug_run_action.triggered.connect(self.debug_current_file)
        debug_menu.addAction(debug_run_action)

        debug_menu.addSeparator()

        step_into_action = QAction("↓ Step Into", self)
        step_into_action.setShortcut("F11")
        step_into_action.triggered.connect(self._debug_step_into)
        debug_menu.addAction(step_into_action)

        step_over_action = QAction("→ Step Over", self)
        step_over_action.setShortcut("F10")
        step_over_action.triggered.connect(self._debug_step_over)
        debug_menu.addAction(step_over_action)

        continue_action = QAction("▶ Continue", self)
        continue_action.setShortcut("F8")
        continue_action.triggered.connect(self._debug_continue)
        debug_menu.addAction(continue_action)

        debug_menu.addSeparator()

        toggle_breakpoint_action = QAction("🔴 Toggle Breakpoint", self)
        toggle_breakpoint_action.setShortcut("F9")
        toggle_breakpoint_action.triggered.connect(self._toggle_breakpoint_at_cursor)
        debug_menu.addAction(toggle_breakpoint_action)

        clear_breakpoints_action = QAction("Clear All Breakpoints", self)
        clear_breakpoints_action.triggered.connect(self._clear_all_breakpoints)
        debug_menu.addAction(clear_breakpoints_action)

        debug_menu.addSeparator()

        toggle_debug_panel_action = QAction("Toggle Debug Panel", self)
        toggle_debug_panel_action.setShortcut("Ctrl+D")
        toggle_debug_panel_action.triggered.connect(self._toggle_debug_panel)
        debug_menu.addAction(toggle_debug_panel_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("About PLAIN IDE", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_toolbar(self):
        """Set up the toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)

        # New file
        new_btn = QAction("📄", self)
        new_btn.setToolTip("New File (Ctrl+N)")
        new_btn.triggered.connect(self.new_file)
        toolbar.addAction(new_btn)

        # Open
        open_btn = QAction("📂", self)
        open_btn.setToolTip("Open File (Ctrl+O)")
        open_btn.triggered.connect(self.open_file_dialog)
        toolbar.addAction(open_btn)

        # Save
        save_btn = QAction("💾", self)
        save_btn.setToolTip("Save (Ctrl+S)")
        save_btn.triggered.connect(self.save_file)
        toolbar.addAction(save_btn)

        toolbar.addSeparator()

        # Run
        run_btn = QAction("▶", self)
        run_btn.setToolTip("Run (F5)")
        run_btn.triggered.connect(self.run_current_file)
        toolbar.addAction(run_btn)

        # Stop
        stop_btn = QAction("⏹", self)
        stop_btn.setToolTip("Stop (Shift+F5)")
        stop_btn.triggered.connect(self.terminal.stop_execution)
        toolbar.addAction(stop_btn)

    def _setup_statusbar(self):
        """Set up the status bar"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        self.file_label = QLabel("No file open")
        self.statusbar.addWidget(self.file_label, 1)

        self.cursor_label = QLabel("Ln 1, Col 1")
        self.statusbar.addPermanentWidget(self.cursor_label)

    def _apply_settings(self):
        """Apply settings to the window"""
        ws = self.settings.settings.window
        self.resize(ws.width, ws.height)
        if ws.maximized:
            self.showMaximized()

        # Set home directory as default file browser root
        home = str(Path.home())
        self.file_browser.set_root_path(home)

    def _apply_theme(self):
        """Apply the current theme to all components"""
        theme = self.theme_manager.get_current_theme()
        self.file_browser.apply_theme(theme)
        self.terminal.apply_theme(theme)
        self.debug_panel.apply_theme(theme)

        # Apply to all open editors
        for editor in self.editors.values():
            editor.apply_theme(theme)

    def _set_theme(self, name: str):
        """Set and apply a new theme"""
        self.theme_manager.set_theme(name)
        from PyQt6.QtWidgets import QApplication
        QApplication.instance().setStyleSheet(self.theme_manager.get_current_stylesheet())
        self._apply_theme()

    # File operations
    def new_file(self):
        """Create a new empty file"""
        editor = CodeEditor(
            theme=self.theme_manager.get_current_theme(),
            settings=self.settings
        )
        editor.apply_theme(self.theme_manager.get_current_theme())
        editor.cursorPositionChanged.connect(self._update_cursor_position)

        self.tab_widget.addTab(editor, "Untitled")
        self.tab_widget.setCurrentWidget(editor)

    def open_file_dialog(self):
        """Open file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", str(Path.home()),
            "PLAIN Files (*.plain);;All Files (*)"
        )
        if file_path:
            self.open_file(file_path)

    def open_folder_dialog(self):
        """Open folder dialog"""
        folder = QFileDialog.getExistingDirectory(
            self, "Open Folder", str(Path.home())
        )
        if folder:
            self.file_browser.set_root_path(folder)
            self.current_project_path = folder

    def open_file(self, file_path: str):
        """Open a file in a new or existing tab"""
        path = Path(file_path)

        # Check if already open
        if file_path in self.editors:
            idx = self.tab_widget.indexOf(self.editors[file_path])
            self.tab_widget.setCurrentIndex(idx)
            return

        if not path.exists():
            QMessageBox.warning(self, "Error", f"File not found: {file_path}")
            return

        try:
            content = path.read_text(encoding='utf-8')
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not read file: {e}")
            return

        editor = CodeEditor(
            theme=self.theme_manager.get_current_theme(),
            settings=self.settings
        )
        editor.apply_theme(self.theme_manager.get_current_theme())
        editor.file_path = file_path
        editor.setPlainText(content)
        editor.set_modified(False)
        editor.cursorPositionChanged.connect(self._update_cursor_position)
        editor.file_modified.connect(lambda m, p=file_path: self._on_file_modified(p, m))

        self.editors[file_path] = editor
        idx = self.tab_widget.addTab(editor, path.name)
        self.tab_widget.setCurrentIndex(idx)

        self.settings.add_recent_file(file_path)
        self.file_label.setText(file_path)

    def save_file(self):
        """Save the current file"""
        editor = self.tab_widget.currentWidget()
        if not isinstance(editor, CodeEditor):
            return

        if editor.file_path:
            self._save_editor(editor, editor.file_path)
        else:
            self.save_file_as()

    def save_file_as(self):
        """Save the current file with a new name"""
        editor = self.tab_widget.currentWidget()
        if not isinstance(editor, CodeEditor):
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File", str(Path.home()),
            "PLAIN Files (*.plain);;All Files (*)"
        )
        if file_path:
            self._save_editor(editor, file_path)

    def _save_editor(self, editor: CodeEditor, file_path: str):
        """Save editor content to file"""
        try:
            Path(file_path).write_text(editor.toPlainText(), encoding='utf-8')
            editor.file_path = file_path
            editor.set_modified(False)

            # Update tab title
            idx = self.tab_widget.indexOf(editor)
            self.tab_widget.setTabText(idx, Path(file_path).name)

            # Update editors dict
            if file_path not in self.editors:
                self.editors[file_path] = editor

            self.file_label.setText(file_path)
            self.statusbar.showMessage("File saved", 3000)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not save file: {e}")

    def close_tab(self, index: int):
        """Close a tab"""
        editor = self.tab_widget.widget(index)
        if not isinstance(editor, CodeEditor):
            return

        if editor.is_modified():
            reply = QMessageBox.question(
                self, "Save Changes?",
                "This file has unsaved changes. Save before closing?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Cancel:
                return
            elif reply == QMessageBox.StandardButton.Save:
                self.tab_widget.setCurrentIndex(index)
                self.save_file()

        # Remove from editors dict
        if editor.file_path and editor.file_path in self.editors:
            del self.editors[editor.file_path]

        self.tab_widget.removeTab(index)

    def _on_tab_changed(self, index: int):
        """Handle tab change"""
        editor = self.tab_widget.widget(index)
        if isinstance(editor, CodeEditor) and editor.file_path:
            self.file_label.setText(editor.file_path)
        else:
            self.file_label.setText("No file open")
        self._update_cursor_position()

    def _on_file_modified(self, path: str, modified: bool):
        """Handle file modification"""
        if path in self.editors:
            editor = self.editors[path]
            idx = self.tab_widget.indexOf(editor)
            name = Path(path).name
            if modified:
                self.tab_widget.setTabText(idx, f"● {name}")
            else:
                self.tab_widget.setTabText(idx, name)

    def _update_cursor_position(self):
        """Update cursor position in status bar"""
        editor = self.tab_widget.currentWidget()
        if isinstance(editor, CodeEditor):
            cursor = editor.textCursor()
            line = cursor.blockNumber() + 1
            col = cursor.columnNumber() + 1
            self.cursor_label.setText(f"Ln {line}, Col {col}")

    # Edit operations
    def _undo(self):
        editor = self.tab_widget.currentWidget()
        if isinstance(editor, CodeEditor):
            editor.undo()

    def _redo(self):
        editor = self.tab_widget.currentWidget()
        if isinstance(editor, CodeEditor):
            editor.redo()

    def _cut(self):
        editor = self.tab_widget.currentWidget()
        if isinstance(editor, CodeEditor):
            editor.cut()

    def _copy(self):
        editor = self.tab_widget.currentWidget()
        if isinstance(editor, CodeEditor):
            editor.copy()

    def _paste(self):
        editor = self.tab_widget.currentWidget()
        if isinstance(editor, CodeEditor):
            editor.paste()

    # View operations
    def _toggle_file_browser(self):
        """Toggle file browser visibility"""
        self.file_browser.setVisible(not self.file_browser.isVisible())

    def _toggle_terminal(self):
        """Toggle terminal visibility"""
        self.terminal.setVisible(not self.terminal.isVisible())

    # Run operations
    def run_current_file(self):
        """Run the current PLAIN file"""
        editor = self.tab_widget.currentWidget()
        if not isinstance(editor, CodeEditor):
            QMessageBox.warning(self, "No File", "No file is open to run.")
            return

        # Save first if modified
        if editor.is_modified():
            if editor.file_path:
                self._save_editor(editor, editor.file_path)
            else:
                reply = QMessageBox.question(
                    self, "Save File?",
                    "File must be saved before running. Save now?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.save_file_as()
                else:
                    return

        if not editor.file_path:
            QMessageBox.warning(self, "No File", "Please save the file first.")
            return

        # Make sure terminal is visible
        self.terminal.setVisible(True)

        # Run the file
        self.terminal.run_plain_file(editor.file_path)

    def _show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, "About PLAIN IDE",
            "<h2>PLAIN IDE</h2>"
            "<p>Version 1.0.0</p>"
            "<p>A modern IDE for the PLAIN programming language.</p>"
            "<p>PLAIN - Programming Language, Able, Intuitive, and Natural</p>"
        )

    def closeEvent(self, event):
        """Handle window close"""
        # Check for unsaved files
        for editor in self.editors.values():
            if editor.is_modified():
                reply = QMessageBox.question(
                    self, "Unsaved Changes",
                    "You have unsaved changes. Are you sure you want to quit?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    event.ignore()
                    return
                break

        # Save window state
        ws = self.settings.settings.window
        ws.width = self.width()
        ws.height = self.height()
        ws.maximized = self.isMaximized()
        self.settings.save()

        event.accept()

    # Debug operations
    def _toggle_debug_panel(self):
        """Toggle debug panel visibility"""
        visible = not self.debug_panel.isVisible()
        self.debug_panel.setVisible(visible)
        if visible:
            self.main_splitter.setSizes([250, 550, 300])
        else:
            self.main_splitter.setSizes([250, 850, 0])

    def _toggle_breakpoint_at_cursor(self):
        """Toggle breakpoint at current cursor line"""
        editor = self.tab_widget.currentWidget()
        if isinstance(editor, CodeEditor):
            cursor = editor.textCursor()
            line = cursor.blockNumber() + 1
            editor.toggle_breakpoint(line)

    def _clear_all_breakpoints(self):
        """Clear all breakpoints in all editors"""
        for editor in self.editors.values():
            editor.clear_breakpoints()

    def debug_current_file(self):
        """Start debugging the current file"""
        editor = self.tab_widget.currentWidget()
        if not isinstance(editor, CodeEditor):
            QMessageBox.warning(self, "No File", "No file is open to debug.")
            return

        # Save first if modified
        if editor.is_modified():
            if editor.file_path:
                self._save_editor(editor, editor.file_path)
            else:
                reply = QMessageBox.question(
                    self, "Save File?",
                    "File must be saved before debugging. Save now?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.save_file_as()
                else:
                    return

        if not editor.file_path:
            QMessageBox.warning(self, "No File", "Please save the file first.")
            return

        # Show debug panel
        self.debug_panel.setVisible(True)
        self.main_splitter.setSizes([250, 550, 300])
        self.debug_panel.set_debugging_active(True)

        # Run with trace mode (simplified debugging)
        self._run_with_trace(editor.file_path, editor.get_breakpoints())

    def _run_with_trace(self, file_path: str, breakpoints: set):
        """Run file in debug mode with step-through debugging"""
        self.terminal.clear()
        self.terminal.write_line(f"🐛 Debug: {file_path}",
                                 self.theme_manager.get_current_theme().info)
        if breakpoints:
            self.terminal.write_line(f"   Breakpoints: lines {sorted(breakpoints)}")
        self.terminal.write_line("-" * 50)

        # Start debug session
        self.debug_panel.add_trace(f"Starting debug: {file_path}")
        if not self.debug_manager.start_debug(file_path, breakpoints):
            self.terminal.write_line("❌ Failed to start debug session",
                                    self.theme_manager.get_current_theme().error)
            self.debug_panel.set_debugging_active(False)
            return

        self.debug_panel.add_trace("Waiting for debugger...")

    def _debug_continue(self):
        """Continue execution until next breakpoint"""
        self.debug_panel.add_trace("Continue...")
        self.debug_panel.set_paused(False, "Running...")
        self.debug_manager.continue_execution()
        # Clear debug line while running
        editor = self.tab_widget.currentWidget()
        if isinstance(editor, CodeEditor):
            editor.clear_debug_line()

    def _debug_step_into(self):
        """Step into the next statement"""
        self.debug_panel.add_trace("Step into...")
        self.debug_manager.step_into()

    def _debug_step_over(self):
        """Step over the next statement"""
        self.debug_panel.add_trace("Step over...")
        self.debug_manager.step_over()

    def _debug_stop(self):
        """Stop debugging"""
        self.debug_manager.stop_debug()
        self.debug_panel.set_debugging_active(False)
        self.debug_panel.add_trace("Debug session stopped.")
        self.terminal.write_line("\n⏹ Debug session terminated.",
                                self.theme_manager.get_current_theme().warning)

        # Clear debug line in all editors
        for editor in self.editors.values():
            editor.clear_debug_line()

    # Debug event handlers
    def _on_debug_stopped(self, line: int, reason: str, call_stack: list):
        """Handle debugger stopped event"""
        self.debug_panel.set_paused(True, f"line {line}")
        self.debug_panel.add_trace(f"Stopped at line {line} ({reason})")

        # Highlight the current line in the editor
        editor = self.tab_widget.currentWidget()
        if isinstance(editor, CodeEditor):
            editor.set_debug_line(line)
            # Scroll to the debug line
            cursor = editor.textCursor()
            block = editor.document().findBlockByLineNumber(line - 1)
            cursor.setPosition(block.position())
            editor.setTextCursor(cursor)
            editor.centerCursor()

        # Update call stack display in trace
        if call_stack:
            self.debug_panel.add_trace(f"Call stack: {' -> '.join(f['name'] for f in call_stack)}")

    def _on_debug_terminated(self):
        """Handle debugger terminated event"""
        self.debug_panel.set_debugging_active(False)
        self.debug_panel.add_trace("Program terminated.")
        self.terminal.write_line("\n✓ Debug session finished.",
                                self.theme_manager.get_current_theme().success)

        # Clear debug line in all editors
        for editor in self.editors.values():
            editor.clear_debug_line()

    def _on_debug_variables(self, variables: dict):
        """Handle variables received from debugger"""
        self.debug_panel.update_variables(variables)

    def _on_debug_output(self, output: str):
        """Handle output from debugger"""
        self.terminal.write(output)

    def _on_debug_error(self, error: str):
        """Handle error from debugger"""
        self.terminal.write_line(error, self.theme_manager.get_current_theme().error)
        self.debug_panel.add_trace(f"Error: {error}")

