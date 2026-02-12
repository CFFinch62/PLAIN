"""
File Browser Widget for PLAIN IDE
Provides a file tree view for project navigation with bookmarks
"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QTreeView, QWidget, QVBoxLayout, QHBoxLayout, QMenu,
    QListWidget, QListWidgetItem, QPushButton, QLabel, QFrame,
    QFileDialog, QInputDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QDir
from PyQt6.QtGui import QFileSystemModel, QAction

from plain_ide.app.themes import Theme
from plain_ide.app.settings import SettingsManager


class FileBrowserWidget(QWidget):
    """File browser widget with bookmarks and tree view"""

    file_double_clicked = pyqtSignal(str)  # Emits file path
    bookmark_navigated = pyqtSignal(str)   # Emits folder path when bookmark clicked

    def __init__(self, parent=None, theme: Theme = None, settings: SettingsManager = None):
        super().__init__(parent)
        self.theme = theme
        self.settings = settings
        self._current_root = str(Path.home())
        self._setup_ui()
        self._load_bookmarks()

    def _setup_ui(self):
        """Set up the file browser UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Bookmarks section
        self._setup_bookmarks_section(layout)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFixedHeight(1)
        layout.addWidget(separator)

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

    def _setup_bookmarks_section(self, parent_layout):
        """Set up the bookmarks panel above the file tree"""
        # Header row with label and add button
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(8, 6, 8, 2)

        header_label = QLabel("Bookmarks")
        header_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        header_layout.addWidget(header_label)

        header_layout.addStretch()

        self.add_bookmark_btn = QPushButton("+")
        self.add_bookmark_btn.setFixedSize(22, 22)
        self.add_bookmark_btn.setToolTip("Bookmark current folder")
        self.add_bookmark_btn.clicked.connect(self._add_current_folder_bookmark)
        header_layout.addWidget(self.add_bookmark_btn)

        parent_layout.addLayout(header_layout)

        # Bookmark list
        self.bookmark_list = QListWidget()
        self.bookmark_list.setMaximumHeight(120)
        self.bookmark_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.bookmark_list.customContextMenuRequested.connect(self._show_bookmark_context_menu)
        self.bookmark_list.itemClicked.connect(self._on_bookmark_clicked)
        parent_layout.addWidget(self.bookmark_list)

    def _load_bookmarks(self):
        """Load bookmarks from settings into the list widget"""
        self.bookmark_list.clear()
        if self.settings:
            for path in self.settings.settings.bookmarks:
                self._add_bookmark_item(path)

    def _add_bookmark_item(self, path: str):
        """Add a single bookmark item to the list"""
        folder_name = Path(path).name or path
        item = QListWidgetItem(f"  {folder_name}")
        item.setData(Qt.ItemDataRole.UserRole, path)
        item.setToolTip(path)
        self.bookmark_list.addItem(item)

    def _add_current_folder_bookmark(self):
        """Add the current file browser root folder as a bookmark"""
        if self._current_root:
            self.add_bookmark(self._current_root)

    def add_bookmark(self, path: str):
        """Add a folder path to bookmarks"""
        if self.settings:
            if path not in self.settings.settings.bookmarks:
                self.settings.add_bookmark(path)
                self._add_bookmark_item(path)

    def remove_bookmark(self, path: str):
        """Remove a folder path from bookmarks"""
        if self.settings:
            self.settings.remove_bookmark(path)
            # Remove from list widget
            for i in range(self.bookmark_list.count()):
                item = self.bookmark_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == path:
                    self.bookmark_list.takeItem(i)
                    break

    def _on_bookmark_clicked(self, item: QListWidgetItem):
        """Navigate to bookmarked folder"""
        path = item.data(Qt.ItemDataRole.UserRole)
        if path and Path(path).exists():
            self.set_root_path(path)
            self.bookmark_navigated.emit(path)

    def _show_bookmark_context_menu(self, position):
        """Show context menu for bookmark items"""
        item = self.bookmark_list.itemAt(position)
        if not item:
            return

        path = item.data(Qt.ItemDataRole.UserRole)
        menu = QMenu(self)

        open_action = QAction("Open", self)
        open_action.triggered.connect(lambda: self._on_bookmark_clicked(item))
        menu.addAction(open_action)

        menu.addSeparator()

        remove_action = QAction("Remove Bookmark", self)
        remove_action.triggered.connect(lambda: self.remove_bookmark(path))
        menu.addAction(remove_action)

        menu.exec(self.bookmark_list.mapToGlobal(position))

    def set_root_path(self, path: str):
        """Set the root directory for the file browser"""
        if path and Path(path).exists():
            self._current_root = path
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
            QListWidget {{
                background-color: {theme.browser_background};
                color: {theme.foreground};
                border: none;
                font-size: 12px;
            }}
            QListWidget::item {{
                padding: 3px 6px;
                border-radius: 3px;
            }}
            QListWidget::item:hover {{
                background-color: {theme.browser_item_hover};
            }}
            QListWidget::item:selected {{
                background-color: {theme.browser_item_selected};
            }}
            QLabel {{
                color: {theme.foreground};
            }}
            QPushButton {{
                background-color: {theme.button_background};
                color: {theme.button_foreground};
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {theme.button_hover};
            }}
            QFrame {{
                background-color: {theme.panel_border};
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
        path = ""
        target_dir = self._current_root
        
        if index.isValid():
            path = self.model.filePath(index)
            is_file = Path(path).is_file()
            is_dir = Path(path).is_dir()
            
            if is_dir:
                target_dir = path
            elif is_file:
                target_dir = str(Path(path).parent)
        else:
            # If clicked on empty space, use root
            pass

        menu = QMenu(self)

        # File operations
        new_file_action = QAction("New File...", self)
        new_file_action.triggered.connect(lambda: self._create_new_file(target_dir))
        menu.addAction(new_file_action)

        new_folder_action = QAction("New Folder...", self)
        new_folder_action.triggered.connect(lambda: self._create_new_folder(target_dir))
        menu.addAction(new_folder_action)
        
        menu.addSeparator()

        if index.isValid() and Path(path).is_file():
            open_action = QAction("Open", self)
            open_action.triggered.connect(lambda: self.file_double_clicked.emit(path))
            menu.addAction(open_action)

        if index.isValid() and Path(path).is_dir():
            bookmark_action = QAction("Add to Bookmarks", self)
            bookmark_action.triggered.connect(lambda: self.add_bookmark(path))
            menu.addAction(bookmark_action)

        menu.addSeparator()

        # Show in file manager
        if path:
            reveal_action = QAction("Reveal in File Manager", self)
            reveal_action.triggered.connect(lambda: self._reveal_in_file_manager(path))
            menu.addAction(reveal_action)

        menu.exec(self.tree_view.mapToGlobal(position))

    def _create_new_file(self, target_dir: str):
        """Create a new file in the target directory"""
        filename, ok = QInputDialog.getText(self, "New File", "Enter filename:")
        if ok and filename:
            new_path = Path(target_dir) / filename
            if new_path.exists():
                QMessageBox.warning(self, "Error", "File already exists!")
                return
                
            try:
                new_path.touch()
                self.file_double_clicked.emit(str(new_path))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not create file: {e}")

    def _create_new_folder(self, target_dir: str):
        """Create a new folder in the target directory"""
        foldername, ok = QInputDialog.getText(self, "New Folder", "Enter folder name:")
        if ok and foldername:
            new_path = Path(target_dir) / foldername
            if new_path.exists():
                QMessageBox.warning(self, "Error", "Folder already exists!")
                return
                
            try:
                new_path.mkdir()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not create folder: {e}")

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
