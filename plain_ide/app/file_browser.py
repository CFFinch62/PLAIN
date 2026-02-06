"""
File Browser Widget for PLAIN IDE
Provides a file tree view for project navigation
"""

from pathlib import Path
from PyQt6.QtWidgets import QTreeView, QWidget, QVBoxLayout, QMenu
from PyQt6.QtCore import Qt, pyqtSignal, QDir
from PyQt6.QtGui import QFileSystemModel, QAction

from plain_ide.app.themes import Theme


class FileBrowserWidget(QWidget):
    """File browser widget with tree view"""
    
    file_double_clicked = pyqtSignal(str)  # Emits file path
    
    def __init__(self, parent=None, theme: Theme = None):
        super().__init__(parent)
        self.theme = theme
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the file browser UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create tree view
        self.tree_view = QTreeView()
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setAnimated(True)
        self.tree_view.setIndentation(16)
        self.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self._show_context_menu)
        self.tree_view.doubleClicked.connect(self._on_double_click)
        
        # Create file system model
        self.model = QFileSystemModel()
        self.model.setRootPath("")
        
        # Set name filters for PLAIN files (show all, but highlight .plain files)
        self.model.setNameFilters(["*.plain", "*.txt", "*"])
        self.model.setNameFilterDisables(False)
        
        # Set model on tree view
        self.tree_view.setModel(self.model)
        
        # Hide size, type, date columns - only show name
        self.tree_view.hideColumn(1)
        self.tree_view.hideColumn(2)
        self.tree_view.hideColumn(3)
        
        layout.addWidget(self.tree_view)
    
    def set_root_path(self, path: str):
        """Set the root directory for the file browser"""
        if path and Path(path).exists():
            self.model.setRootPath(path)
            self.tree_view.setRootIndex(self.model.index(path))
    
    def apply_theme(self, theme: Theme):
        """Apply theme to file browser"""
        self.theme = theme
        self.setStyleSheet(f"""
            QTreeView {{
                background-color: {theme.browser_background};
                color: {theme.foreground};
                border: none;
            }}
            QTreeView::item {{
                padding: 4px 8px;
            }}
            QTreeView::item:hover {{
                background-color: {theme.browser_item_hover};
            }}
            QTreeView::item:selected {{
                background-color: {theme.browser_item_selected};
            }}
        """)
    
    def _on_double_click(self, index):
        """Handle double-click on file"""
        path = self.model.filePath(index)
        if path and Path(path).is_file():
            self.file_double_clicked.emit(path)
    
    def _show_context_menu(self, position):
        """Show context menu for file operations"""
        index = self.tree_view.indexAt(position)
        if not index.isValid():
            return
        
        path = self.model.filePath(index)
        is_file = Path(path).is_file()
        
        menu = QMenu(self)
        
        if is_file:
            open_action = QAction("Open", self)
            open_action.triggered.connect(lambda: self.file_double_clicked.emit(path))
            menu.addAction(open_action)
        
        menu.addSeparator()
        
        # Show in file manager
        reveal_action = QAction("Reveal in File Manager", self)
        reveal_action.triggered.connect(lambda: self._reveal_in_file_manager(path))
        menu.addAction(reveal_action)
        
        menu.exec(self.tree_view.mapToGlobal(position))
    
    def _reveal_in_file_manager(self, path: str):
        """Open the file location in system file manager"""
        import subprocess
        import sys
        
        p = Path(path)
        if p.is_file():
            p = p.parent
        
        if sys.platform == "linux":
            subprocess.run(["xdg-open", str(p)])
        elif sys.platform == "darwin":
            subprocess.run(["open", str(p)])
        elif sys.platform == "win32":
            subprocess.run(["explorer", str(p)])

