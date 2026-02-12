"""
Main Window for PLAIN IDE
The primary application window containing all IDE components
"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTabWidget, QMenuBar, QMenu, QToolBar, QStatusBar, QFileDialog,
    QMessageBox, QLabel, QStyle
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QKeySequence, QIcon

import sys
import os

from plain_ide.app.settings import SettingsManager
from plain_ide.app.themes import ThemeManager
from plain_ide.app.editor import CodeEditor
from plain_ide.app.file_browser import FileBrowserWidget
from plain_ide.app.terminal import TerminalWidget
from plain_ide.app.debug_panel import DebugPanel
from plain_ide.app.debug_manager import DebugManager
from plain_ide.app.find_replace import FindReplaceWidget
from plain_ide.app.settings_dialog import SettingsDialog
from plain_ide.app.help_viewer import HelpViewer


class PlainIDEMainWindow(QMainWindow):
    """Main window for the PLAIN IDE"""

    def __init__(self, settings: SettingsManager, theme_manager: ThemeManager):
        super().__init__()
        self.settings = settings
        self.theme_manager = theme_manager
        self.editors = {}  # path -> CodeEditor
        self.debug_manager = DebugManager(self, self.settings)
        self.current_project_path = None
        self._terminal_position_before_debug = None  # Track position before debug mode
        
        self._setup_ui()
        self._setup_menus()
        self._setup_toolbar()
        self._setup_statusbar()
        self._apply_settings()
        self._apply_theme()
        self._restore_session()
    
    def _setup_ui(self):
        """Set up the main UI layout"""
        self.setWindowTitle("PLAIN IDE")
        
        # Set window icon
        icon_path = self._get_resource_path("images/plain_icon_256.png")
        if icon_path and Path(icon_path).exists():
            self.setWindowIcon(QIcon(icon_path))
        
        # Central widget with main layout
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Main horizontal splitter (file browser | editor + terminal)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # File browser (with bookmarks)
        # Note: file_browser, terminal, debug_panel, find_replace still use old Theme object
        # They don't need syntax highlighting, so we create a compatibility Theme object
        self.file_browser = FileBrowserWidget(
            theme=self._get_compat_theme(),
            settings=self.settings
        )
        self.file_browser.file_double_clicked.connect(self.open_file)
        self.file_browser.bookmark_navigated.connect(self._on_bookmark_navigated)
        self.main_splitter.addWidget(self.file_browser)
        
        # Middle: editor + terminal/debug in vertical splitter
        self.middle_splitter = QSplitter(Qt.Orientation.Vertical)

        # Editor area: tabs + find/replace bar
        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(0)

        # Tab widget for editors
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        editor_layout.addWidget(self.tab_widget)

        # Find/Replace bar (hidden by default)
        self.find_replace = FindReplaceWidget(theme=self._get_compat_theme())
        editor_layout.addWidget(self.find_replace)

        self.middle_splitter.addWidget(editor_container)

        # Terminal
        self.terminal = TerminalWidget(
            theme=self._get_compat_theme(),
            settings=self.settings
        )
        self.middle_splitter.addWidget(self.terminal)

        # Set splitter proportions
        self.middle_splitter.setSizes([600, 200])

        self.main_splitter.addWidget(self.middle_splitter)

        # Debug panel on the right
        self.debug_panel = DebugPanel(theme=self._get_compat_theme())
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
        
        new_action = QAction(self._std_icon(QStyle.StandardPixmap.SP_FileIcon), "New", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction(self._std_icon(QStyle.StandardPixmap.SP_DirOpenIcon), "Open File...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_action)

        open_folder_action = QAction(self._std_icon(QStyle.StandardPixmap.SP_DirIcon), "Open Folder...", self)
        open_folder_action.setShortcut("Ctrl+Shift+O")
        open_folder_action.triggered.connect(self.open_folder_dialog)
        file_menu.addAction(open_folder_action)

        file_menu.addSeparator()

        save_action = QAction(self._std_icon(QStyle.StandardPixmap.SP_DialogSaveButton), "Save", self)
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

        edit_menu.addSeparator()

        find_action = QAction("Find...", self)
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(self._show_find)
        edit_menu.addAction(find_action)

        replace_action = QAction("Replace...", self)
        replace_action.setShortcut("Ctrl+H")
        replace_action.triggered.connect(self._show_replace)
        edit_menu.addAction(replace_action)

        edit_menu.addSeparator()
        
        # Code editing actions
        indent_action = QAction("Indent Selection", self)
        indent_action.setShortcuts(["Tab", "Ctrl+]"])
        indent_action.triggered.connect(self._indent_selection)
        edit_menu.addAction(indent_action)
        
        dedent_action = QAction("Dedent Selection", self)
        dedent_action.setShortcuts(["Shift+Tab", "Ctrl+["])
        dedent_action.triggered.connect(self._dedent_selection)
        edit_menu.addAction(dedent_action)
        
        comment_action = QAction("Comment Selection", self)
        comment_action.setShortcut("Ctrl+/")
        comment_action.triggered.connect(self._comment_selection)
        edit_menu.addAction(comment_action)

        edit_menu.addSeparator()

        prefs_action = QAction("Preferences...", self)
        prefs_action.setShortcut("Ctrl+,")
        prefs_action.triggered.connect(self._show_preferences)
        edit_menu.addAction(prefs_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        toggle_browser = QAction(self._std_icon(QStyle.StandardPixmap.SP_DirIcon), "Toggle File Browser", self)
        toggle_browser.setShortcut("Ctrl+B")
        toggle_browser.triggered.connect(self._toggle_file_browser)
        view_menu.addAction(toggle_browser)

        toggle_terminal = QAction(self._std_icon(QStyle.StandardPixmap.SP_ComputerIcon), "Toggle Terminal", self)
        toggle_terminal.setShortcut("Ctrl+`")
        toggle_terminal.triggered.connect(self._toggle_terminal)
        view_menu.addAction(toggle_terminal)

        view_menu.addSeparator()

        # Theme submenu - now shows UI themes and syntax themes
        theme_menu = view_menu.addMenu("Theme")
        
        # UI Theme submenu
        ui_theme_menu = theme_menu.addMenu("UI Theme")
        for theme_name in self.theme_manager.get_available_ui_themes():
            theme_action = QAction(theme_name.replace('_', ' ').title(), self)
            theme_action.triggered.connect(lambda checked, n=theme_name: self._set_ui_theme(n))
            ui_theme_menu.addAction(theme_action)
        
        # Syntax Theme submenu
        syntax_theme_menu = theme_menu.addMenu("Syntax Theme")
        for theme_name in self.theme_manager.get_available_syntax_themes():
            theme_action = QAction(theme_name.replace('_', ' ').title(), self)
            theme_action.triggered.connect(lambda checked, n=theme_name: self._set_syntax_theme(n))
            syntax_theme_menu.addAction(theme_action)
        
        view_menu.addSeparator()
        
        # Terminal Position submenu
        terminal_pos_menu = view_menu.addMenu("Terminal Position")
        
        terminal_bottom_action = QAction("Bottom", self)
        terminal_bottom_action.triggered.connect(lambda: self._set_terminal_position("bottom"))
        terminal_pos_menu.addAction(terminal_bottom_action)
        
        terminal_right_action = QAction("Right", self)
        terminal_right_action.triggered.connect(lambda: self._set_terminal_position("right"))
        terminal_pos_menu.addAction(terminal_right_action)

        # Run menu
        run_menu = menubar.addMenu("&Run")

        run_action = QAction(self._std_icon(QStyle.StandardPixmap.SP_MediaPlay), "Run", self)
        run_action.setShortcut("F5")
        run_action.triggered.connect(self.run_current_file)
        run_menu.addAction(run_action)

        stop_action = QAction(self._std_icon(QStyle.StandardPixmap.SP_MediaStop), "Stop", self)
        stop_action.setShortcut("Shift+F5")
        stop_action.triggered.connect(self.terminal.stop_execution)
        run_menu.addAction(stop_action)

        run_menu.addSeparator()

        set_interpreter_action = QAction("Set Interpreter...", self)
        set_interpreter_action.triggered.connect(self._show_interpreter_settings)
        run_menu.addAction(set_interpreter_action)

        # Debug menu
        debug_menu = menubar.addMenu("&Debug")

        debug_run_action = QAction("Debug", self)
        debug_run_action.setShortcut("F6")
        debug_run_action.triggered.connect(self.debug_current_file)
        debug_menu.addAction(debug_run_action)

        debug_menu.addSeparator()

        step_into_action = QAction("Step Into", self)
        step_into_action.setShortcut("F11")
        step_into_action.triggered.connect(self._debug_step_into)
        debug_menu.addAction(step_into_action)

        step_over_action = QAction("Step Over", self)
        step_over_action.setShortcut("F10")
        step_over_action.triggered.connect(self._debug_step_over)
        debug_menu.addAction(step_over_action)

        continue_action = QAction(self._std_icon(QStyle.StandardPixmap.SP_MediaPlay), "Continue", self)
        continue_action.setShortcut("F8")
        continue_action.triggered.connect(self._debug_continue)
        debug_menu.addAction(continue_action)

        debug_menu.addSeparator()

        toggle_breakpoint_action = QAction("Toggle Breakpoint", self)
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

        quick_ref_action = QAction("PLAIN Quick Reference", self)
        quick_ref_action.setShortcut("F1")
        quick_ref_action.triggered.connect(self._show_quick_reference)
        help_menu.addAction(quick_ref_action)

        help_menu.addSeparator()

        about_action = QAction("About PLAIN IDE", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _std_icon(self, standard_pixmap):
        """Get a standard icon from the application style"""
        return self.style().standardIcon(standard_pixmap)

    def _setup_toolbar(self):
        """Set up the toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)

        # New file
        new_btn = QAction(self._std_icon(QStyle.StandardPixmap.SP_FileIcon), "New", self)
        new_btn.setToolTip("New File (Ctrl+N)")
        new_btn.triggered.connect(self.new_file)
        toolbar.addAction(new_btn)

        # Open
        open_btn = QAction(self._std_icon(QStyle.StandardPixmap.SP_DirOpenIcon), "Open", self)
        open_btn.setToolTip("Open File (Ctrl+O)")
        open_btn.triggered.connect(self.open_file_dialog)
        toolbar.addAction(open_btn)

        # Save
        save_btn = QAction(self._std_icon(QStyle.StandardPixmap.SP_DialogSaveButton), "Save", self)
        save_btn.setToolTip("Save (Ctrl+S)")
        save_btn.triggered.connect(self.save_file)
        toolbar.addAction(save_btn)

        toolbar.addSeparator()

        # Run
        run_btn = QAction(self._std_icon(QStyle.StandardPixmap.SP_MediaPlay), "Run", self)
        run_btn.setToolTip("Run (F5)")
        run_btn.triggered.connect(self.run_current_file)
        toolbar.addAction(run_btn)

        # Stop
        stop_btn = QAction(self._std_icon(QStyle.StandardPixmap.SP_MediaStop), "Stop", self)
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
        
        # Apply terminal position from settings
        terminal_position = self.settings.settings.terminal.position
        if terminal_position == "right":
            self._set_terminal_position("right")

    def _get_compat_theme(self):
        """Create a compatibility Theme object for components that don't use dual themes yet"""
        # Import here to avoid circular dependency
        from plain_ide.app.themes import Theme
        ui_theme = self.theme_manager.get_current_ui_theme()
        syntax_theme = self.theme_manager.get_current_syntax_theme()
        
        # Create a Theme object combining UI and syntax themes
        return Theme(
            name=ui_theme.name,
            is_dark=ui_theme.is_dark,
            background=ui_theme.background,
            foreground=ui_theme.foreground,
            accent=ui_theme.accent,
            accent_hover=ui_theme.accent_hover,
            panel_background=ui_theme.panel_background,
            panel_border=ui_theme.panel_border,
            editor_background=ui_theme.editor_background,
            editor_foreground=ui_theme.editor_foreground,
            editor_line_highlight=ui_theme.editor_line_highlight,
            editor_selection=ui_theme.editor_selection,
            editor_gutter_bg=ui_theme.editor_gutter_bg,
            editor_gutter_fg=ui_theme.editor_gutter_fg,
            tab_background=ui_theme.tab_background,
            tab_active_background=ui_theme.tab_active_background,
            tab_hover_background=ui_theme.tab_hover_background,
            tab_border=ui_theme.tab_border,
            browser_background=ui_theme.browser_background,
            browser_item_hover=ui_theme.browser_item_hover,
            browser_item_selected=ui_theme.browser_item_selected,
            terminal_background=ui_theme.terminal_background,
            terminal_foreground=ui_theme.terminal_foreground,
            scrollbar_background=ui_theme.scrollbar_background,
            scrollbar_handle=ui_theme.scrollbar_handle,
            scrollbar_handle_hover=ui_theme.scrollbar_handle_hover,
            button_background=ui_theme.button_background,
            button_foreground=ui_theme.button_foreground,
            button_hover=ui_theme.button_hover,
            button_pressed=ui_theme.button_pressed,
            input_background=ui_theme.input_background,
            input_border=ui_theme.input_border,
            input_focus_border=ui_theme.input_focus_border,
            success=ui_theme.success,
            warning=ui_theme.warning,
            error=ui_theme.error,
            info=ui_theme.info,
            syntax=syntax_theme,
        )
    
    def _apply_theme(self):
        """Apply the current theme to all components"""
        theme = self._get_compat_theme()
        self.file_browser.apply_theme(theme)
        self.terminal.apply_theme(theme)
        self.debug_panel.apply_theme(theme)
        self.find_replace.apply_theme(theme)

        # Apply to all open editors (dual theme)
        ui_theme = self.theme_manager.get_current_ui_theme()
        syntax_theme = self.theme_manager.get_current_syntax_theme()
        for editor in self.editors.values():
            editor.apply_ui_theme(ui_theme)
            editor.apply_syntax_theme(syntax_theme)

    def _restore_session(self):
        """Restore previous session state (open files, project folder)"""
        session = self.settings.settings.session

        # Restore project folder
        if session.project_path and Path(session.project_path).exists():
            self.file_browser.set_root_path(session.project_path)
            self.current_project_path = session.project_path

        # Restore open files
        for file_path in session.open_files:
            if Path(file_path).exists():
                self.open_file(file_path)

        # Restore active tab
        if session.active_file and session.active_file in self.editors:
            idx = self.tab_widget.indexOf(self.editors[session.active_file])
            if idx >= 0:
                self.tab_widget.setCurrentIndex(idx)

    def _set_ui_theme(self, name: str):
        """Set and apply a new UI theme"""
        self.theme_manager.set_ui_theme(name)
        from PyQt6.QtWidgets import QApplication
        QApplication.instance().setStyleSheet(self.theme_manager.get_current_stylesheet())
        self._apply_theme()
    
    def _set_syntax_theme(self, name: str):
        """Set and apply a new syntax theme"""
        self.theme_manager.set_syntax_theme(name)
        # Only update editors
        syntax_theme = self.theme_manager.get_current_syntax_theme()
        for editor in self.editors.values():
            editor.apply_syntax_theme(syntax_theme)

    # File operations
    def new_file(self):
        """Create a new empty file"""
        editor = CodeEditor(
            ui_theme=self.theme_manager.get_current_ui_theme(),
            syntax_theme=self.theme_manager.get_current_syntax_theme(),
            settings=self.settings
        )
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
            ui_theme=self.theme_manager.get_current_ui_theme(),
            syntax_theme=self.theme_manager.get_current_syntax_theme(),
            settings=self.settings
        )
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
        # Update find/replace to target the new editor
        if isinstance(editor, CodeEditor) and self.find_replace.isVisible():
            self.find_replace.set_editor(editor)

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
    
    def _set_terminal_position(self, position: str):
        """Set terminal position to 'bottom' or 'right'"""
        if position not in ["bottom", "right"]:
            return

        # Check if terminal is already in the desired position by checking
        # which splitter actually contains it
        terminal_in_middle = any(
            self.middle_splitter.widget(i) is self.terminal
            for i in range(self.middle_splitter.count())
        )
        if position == "bottom" and terminal_in_middle:
            return
        if position == "right" and not terminal_in_middle:
            return

        # Save the new position
        self.settings.settings.terminal.position = position
        self.settings.save()

        # Get current visibility state
        was_visible = self.terminal.isVisible()

        # Hide and detach terminal from its current splitter.
        # addWidget / insertWidget will automatically reparent the widget,
        # so we just need to hide it first to avoid visual glitches.
        self.terminal.hide()

        # Add terminal to new position (reparents automatically)
        if position == "bottom":
            self.middle_splitter.addWidget(self.terminal)
            self.middle_splitter.setSizes([600, 200])
        else:  # position == "right"
            # Insert before debug panel in the main splitter
            debug_index = -1
            for i in range(self.main_splitter.count()):
                if self.main_splitter.widget(i) is self.debug_panel:
                    debug_index = i
                    break

            if debug_index >= 0:
                self.main_splitter.insertWidget(debug_index, self.terminal)
            else:
                self.main_splitter.addWidget(self.terminal)

            # Adjust sizes: file_browser | middle | terminal | debug
            self.main_splitter.setSizes([250, 600, 400, 0])

        # Restore visibility
        self.terminal.setVisible(was_visible)

    def _on_bookmark_navigated(self, path: str):
        """Handle bookmark navigation - update project path"""
        self.current_project_path = path

    # Find/Replace operations
    def _show_find(self):
        """Show the find bar"""
        editor = self.tab_widget.currentWidget()
        if isinstance(editor, CodeEditor):
            self.find_replace.set_editor(editor)
            self.find_replace.show_find()

    def _show_replace(self):
        """Show the find and replace bar"""
        editor = self.tab_widget.currentWidget()
        if isinstance(editor, CodeEditor):
            self.find_replace.set_editor(editor)
            self.find_replace.show_find_replace()
    
    def _indent_selection(self):
        """Indent the selected lines in the current editor"""
        editor = self.tab_widget.currentWidget()
        if isinstance(editor, CodeEditor):
            editor.indent_selection()
    
    def _dedent_selection(self):
        """Dedent the selected lines in the current editor"""
        editor = self.tab_widget.currentWidget()
        if isinstance(editor, CodeEditor):
            editor.dedent_selection()
    
    def _comment_selection(self):
        """Convert selected lines to a note: comment block"""
        editor = self.tab_widget.currentWidget()
        if isinstance(editor, CodeEditor):
            editor.comment_selection()

    def _show_preferences(self):
        """Show the preferences/settings dialog"""
        dialog = SettingsDialog(self.settings, self.theme_manager, parent=self)

        # Connect signal to apply settings immediately when Apply/OK is clicked
        dialog.settings_applied.connect(self._apply_preferences_changes)

        dialog.exec()

    def _apply_preferences_changes(self):
        """Apply preference changes to all editors and components"""
        # Apply changed settings to all editors
        for editor in self.editors.values():
            editor.apply_settings()

        # Apply terminal settings
        self.terminal.apply_settings()

        # Apply theme if changed
        ui_theme_name = getattr(self.settings.settings.theme, 'ui_theme', 'dark')
        syntax_theme_name = getattr(self.settings.settings.theme, 'syntax_theme', 'default')
        
        # Get the currently cached theme name from theme manager (not the UITheme.name property)
        # The theme manager stores themes with lowercase keys, so we compare those
        current_ui_theme_key = getattr(self.settings.settings.theme, 'ui_theme', 'dark')
        
        # Always apply the theme when preferences change to ensure UI updates
        self._set_ui_theme(ui_theme_name)
        
        # Check if syntax theme changed by name (syntax themes are loaded from files)
        if syntax_theme_name not in self.theme_manager.get_available_syntax_themes():
            # Theme was removed, reset to default
            self._set_syntax_theme('default')
        else:
            self._set_syntax_theme(syntax_theme_name)

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

    def _show_interpreter_settings(self):
        """Open settings dialog directly to the Runtime tab"""
        dialog = SettingsDialog(self.settings, self.theme_manager, parent=self)
        dialog.settings_applied.connect(self._apply_preferences_changes)
        
        # Switch to Runtime tab (index 4)
        # 0=Editor, 1=Theme, 2=Terminal, 3=Shortcuts, 4=Runtime
        dialog.tabs.setCurrentIndex(4)
        
        dialog.exec()

    def _show_quick_reference(self):
        """Show the PLAIN quick reference help viewer"""
        viewer = HelpViewer(parent=self, theme=self._get_compat_theme())
        viewer.apply_theme(self.theme_manager.get_current_theme())
        viewer.exec()

    def _show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, "About PLAIN IDE",
            "<h2>PLAIN IDE</h2>"
            "<p>Version 1.0.0</p>"
            "<p>A modern IDE for the PLAIN programming language.</p>"
            "<p>PLAIN - Programming Language - Able, Intuitive, and Natural</p>"
            "<p>(c) 2026 Chuck Finch - Fragillidae Software"
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

        # Save session state
        session = self.settings.settings.session
        session.open_files = [
            path for path, editor in self.editors.items()
            if path and Path(path).exists()
        ]
        current_editor = self.tab_widget.currentWidget()
        if isinstance(current_editor, CodeEditor) and current_editor.file_path:
            session.active_file = current_editor.file_path
        else:
            session.active_file = ""
        session.project_path = self.current_project_path or ""

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

        # Save current terminal position and move to bottom for debugging
        self._terminal_position_before_debug = self.settings.settings.terminal.position
        if self._terminal_position_before_debug == "right":
            self._set_terminal_position("bottom")

        # Show debug panel
        self.debug_panel.setVisible(True)
        self.main_splitter.setSizes([250, 550, 300])
        self.debug_panel.set_debugging_active(True)

        # Run with trace mode (simplified debugging)
        self._run_with_trace(editor.file_path, editor.get_breakpoints())

    def _run_with_trace(self, file_path: str, breakpoints: set):
        """Run file in debug mode with step-through debugging"""
        self.terminal.clear()
        self.terminal.write_line(f"[DEBUG] {file_path}",
                                 self._get_compat_theme().info)
        if breakpoints:
            self.terminal.write_line(f"   Breakpoints: lines {sorted(breakpoints)}")
        self.terminal.write_line("-" * 50)

        # Start debug session
        self.debug_panel.add_trace(f"Starting debug: {file_path}")
        if not self.debug_manager.start_debug(file_path, breakpoints):
            self.terminal.write_line("[ERROR] Failed to start debug session",
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
        self.terminal.write_line("\n[STOPPED] Debug session terminated.",
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
        self.debug_panel.setVisible(False)
        self.debug_panel.set_debugging_active(False)
        self.debug_panel.add_trace("Program terminated.")
        self.terminal.write_line("\n[OK] Debug session finished.",
                                self.theme_manager.get_current_theme().success)

        # Clear debug line in all editors
        for editor in self.editors.values():
            editor.clear_debug_line()
        
        # Restore terminal position if it was changed for debugging
        if self._terminal_position_before_debug == "right":
            self._set_terminal_position("right")
            self._terminal_position_before_debug = None

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

    def _get_resource_path(self, relative_path: str) -> str:
        """Get absolute path to resource, works for dev and for PyInstaller"""
        if getattr(sys, 'frozen', False):
            # PyInstaller creates a temp folder and stores path in _MEIPASS,
            # or for onedir mode, it's relative to executable location (sys._MEIPASS may not be set in onedir?)
            # In onedir, sys._MEIPASS is NOT set usually, resources are next to exe?
            # actually for onedir, sys._MEIPASS IS set if using --onedir? 
            # Wait, for onedir, the files are just in the directory.
            # But PyInstaller loader sets sys._MEIPASS even for onedir?
            if hasattr(sys, '_MEIPASS'):
                 base_path = sys._MEIPASS
            else:
                 base_path = os.path.dirname(sys.executable)
        else:
            base_path = str(Path(__file__).parent.parent.parent)

        return str(Path(base_path) / relative_path)


