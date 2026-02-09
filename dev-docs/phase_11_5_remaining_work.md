# Phase 11.5 Polish - Remaining Work Guide

## Status: What's Already Done (Steps 1-5 Complete)

All these changes are already in your working directory (uncommitted):

### Step 1: Bookmarks Feature - DONE
- `settings.py` - Added `bookmarks: List[str]` to Settings, `SessionSettings` dataclass, `add_bookmark()`/`remove_bookmark()` methods
- `file_browser.py` - Complete rewrite with bookmarks sidebar above file tree, context menu "Add to Bookmarks" on folders, bookmark persistence
- `main_window.py` - Passes `settings` to file browser, connects `bookmark_navigated` signal

### Step 2: Session Persistence - DONE
- `settings.py` - Added `SessionSettings` dataclass (open_files, active_file, project_path)
- `main_window.py` - `_restore_session()` called on startup, `closeEvent()` saves session state

### Step 3: Find/Replace - DONE
- `find_replace.py` - NEW FILE. Full find/replace widget with regex, case-sensitive, whole word options, match highlighting, replace/replace all
- `main_window.py` - Find (Ctrl+F) and Replace (Ctrl+H) in Edit menu, connected to current editor

### Step 4: Additional Themes - DONE
- `themes.py` - Added Monokai, Nord, Dracula, Solarized Dark themes (4 new themes, 6 total)

### Step 5: Settings Dialog - DONE
- `settings_dialog.py` - NEW FILE. Preferences dialog with Editor, Theme, Terminal, and Shortcuts tabs
- `main_window.py` - Preferences (Ctrl+,) in Edit menu, applies settings on OK

---

## What Still Needs To Be Done (Steps 6-7)

### Step 6: Help/Documentation Viewer

Create a new file: `plain_ide/app/help_viewer.py`

```python
"""
Help Viewer for PLAIN IDE
Displays PLAIN language quick reference and documentation
"""

import re
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextBrowser,
    QLineEdit, QPushButton, QLabel
)
from PyQt6.QtCore import Qt

from plain_ide.app.themes import Theme


class HelpViewer(QDialog):
    """Help/documentation viewer dialog"""

    def __init__(self, parent=None, theme: Theme = None):
        super().__init__(parent)
        self.theme = theme
        self.setWindowTitle("PLAIN Quick Reference")
        self.setMinimumSize(700, 500)
        self._setup_ui()
        self._load_content()

    def _setup_ui(self):
        """Set up the help viewer UI"""
        layout = QVBoxLayout(self)

        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        search_layout.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search documentation...")
        self.search_input.textChanged.connect(self._on_search)
        search_layout.addWidget(self.search_input)

        layout.addLayout(search_layout)

        # Content browser
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(False)
        layout.addWidget(self.browser)

        # Close button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def _load_content(self):
        """Load the quick reference markdown and convert to HTML"""
        # Try to find the docs directory relative to the package
        doc_paths = [
            Path(__file__).parent.parent.parent / "docs" / "quick_reference.md",
            Path.cwd() / "docs" / "quick_reference.md",
        ]

        content = ""
        for doc_path in doc_paths:
            if doc_path.exists():
                content = doc_path.read_text(encoding='utf-8')
                break

        if not content:
            content = "# PLAIN Quick Reference\n\nDocumentation file not found."

        html = self._markdown_to_html(content)
        self._full_html = html
        self.browser.setHtml(html)

    def _markdown_to_html(self, md: str) -> str:
        """Simple markdown to HTML conversion"""
        lines = md.split('\n')
        html_lines = []
        in_code_block = False
        in_list = False

        for line in lines:
            # Code blocks
            if line.strip().startswith('```'):
                if in_code_block:
                    html_lines.append('</pre>')
                    in_code_block = False
                else:
                    html_lines.append('<pre style="background-color: #2a2a3c; color: #cdd6f4; padding: 12px; border-radius: 6px; font-family: monospace; font-size: 12px; overflow-x: auto;">')
                    in_code_block = True
                continue

            if in_code_block:
                # Escape HTML in code blocks
                line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                html_lines.append(line)
                continue

            # Close list if needed
            if in_list and not line.strip().startswith(('-', '*', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
                if not line.strip().startswith(' '):
                    html_lines.append('</ul>')
                    in_list = False

            # Headings
            if line.startswith('### '):
                html_lines.append(f'<h3>{line[4:]}</h3>')
            elif line.startswith('## '):
                html_lines.append(f'<h2>{line[3:]}</h2>')
            elif line.startswith('# '):
                html_lines.append(f'<h1>{line[2:]}</h1>')
            # Horizontal rule
            elif line.strip() == '---':
                html_lines.append('<hr>')
            # List items
            elif line.strip().startswith('- ') or line.strip().startswith('* '):
                if not in_list:
                    html_lines.append('<ul>')
                    in_list = True
                item = line.strip()[2:]
                item = self._inline_format(item)
                html_lines.append(f'<li>{item}</li>')
            # Numbered list
            elif re.match(r'^\d+\.\s', line.strip()):
                if not in_list:
                    html_lines.append('<ul>')
                    in_list = True
                item = re.sub(r'^\d+\.\s', '', line.strip())
                item = self._inline_format(item)
                html_lines.append(f'<li>{item}</li>')
            # Empty line
            elif not line.strip():
                html_lines.append('<br>')
            # Regular paragraph
            else:
                formatted = self._inline_format(line)
                html_lines.append(f'<p>{formatted}</p>')

        if in_list:
            html_lines.append('</ul>')
        if in_code_block:
            html_lines.append('</pre>')

        return '\n'.join(html_lines)

    def _inline_format(self, text: str) -> str:
        """Apply inline markdown formatting"""
        # Bold
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        # Italic
        text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
        # Inline code
        text = re.sub(r'`(.+?)`', r'<code style="background-color: #2a2a3c; padding: 2px 6px; border-radius: 3px; font-family: monospace;">\1</code>', text)
        return text

    def _on_search(self, text: str):
        """Search within the help content"""
        if not text:
            self.browser.setHtml(self._full_html)
            return

        # Use QTextBrowser's built-in find
        if not self.browser.find(text):
            # If not found, wrap around
            cursor = self.browser.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)
            self.browser.setTextCursor(cursor)
            self.browser.find(text)

    def apply_theme(self, theme: Theme):
        """Apply theme to the help viewer"""
        self.theme = theme
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme.background};
                color: {theme.foreground};
            }}
            QTextBrowser {{
                background-color: {theme.editor_background};
                color: {theme.editor_foreground};
                border: 1px solid {theme.panel_border};
                border-radius: 6px;
                padding: 12px;
                font-size: 13px;
            }}
            QLineEdit {{
                background-color: {theme.input_background};
                color: {theme.foreground};
                border: 1px solid {theme.input_border};
                border-radius: 4px;
                padding: 6px 10px;
            }}
            QLineEdit:focus {{
                border-color: {theme.input_focus_border};
            }}
            QPushButton {{
                background-color: {theme.button_background};
                color: {theme.button_foreground};
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
            }}
            QPushButton:hover {{
                background-color: {theme.button_hover};
            }}
            QLabel {{
                color: {theme.foreground};
            }}
        """)
```

Then add these changes to `main_window.py`:

**Add import at top of file (after the other imports around line 23):**
```python
from plain_ide.app.help_viewer import HelpViewer
```

**Add Help menu items (replace the existing Help menu section around lines 292-297):**
```python
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
```

**Add the `_show_quick_reference` method (add it near `_show_about`, around line 671):**
```python
    def _show_quick_reference(self):
        """Show the PLAIN quick reference help viewer"""
        viewer = HelpViewer(parent=self, theme=self.theme_manager.get_current_theme())
        viewer.apply_theme(self.theme_manager.get_current_theme())
        viewer.exec()
```

---

### Step 7: Final Polish & Session Log Update

1. **Test the IDE** by running:
   ```bash
   cd /home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/PLAIN
   cd plain_ide && python -m plain_ide.app.main
   ```

2. **Test each feature:**
   - Bookmarks: Open a folder, click "+" to bookmark it, close/reopen IDE, click bookmark
   - Session: Open 2-3 files, close IDE, reopen - files should restore
   - Find/Replace: Ctrl+F to find, Ctrl+H to replace
   - Themes: View > Theme menu, try all 6 themes
   - Settings: Edit > Preferences, change font size, click OK
   - Help: Press F1 to open quick reference

3. **Update session_log.md** - Add a Phase 11.5 completion entry:

   ```markdown
   ### Phase 11.5: Polish (Completed)

   **Features Added:**
   - Bookmarks: Sidebar section above file tree for quick folder navigation
     - Add/remove bookmarks via "+" button or right-click context menu
     - Persistent across IDE restarts via settings.json
   - Session Persistence: Remembers open files, active tab, and project folder
   - Find/Replace: Ctrl+F/Ctrl+H with regex, case-sensitive, whole word options
   - 4 New Themes: Monokai, Nord, Dracula, Solarized Dark (6 total)
   - Settings Dialog: Ctrl+, opens preferences with Editor, Theme, Terminal, Shortcuts tabs
   - Keyboard Shortcuts Reference: Read-only table in Settings > Shortcuts tab
   - Help Viewer: F1 opens PLAIN Quick Reference with search

   **Files Modified:**
   - `plain_ide/app/settings.py` - BookmarkSettings, SessionSettings, bookmark methods
   - `plain_ide/app/file_browser.py` - Bookmarks section, context menu enhancements
   - `plain_ide/app/main_window.py` - Session restore, find/replace, preferences, help
   - `plain_ide/app/themes.py` - Added Monokai, Nord, Dracula, Solarized themes

   **Files Created:**
   - `plain_ide/app/find_replace.py` - Find/Replace widget
   - `plain_ide/app/settings_dialog.py` - Preferences dialog
   - `plain_ide/app/help_viewer.py` - Help documentation viewer
   ```

4. **Commit** when everything works:
   ```bash
   git add plain_ide/app/settings.py plain_ide/app/file_browser.py plain_ide/app/main_window.py plain_ide/app/themes.py plain_ide/app/find_replace.py plain_ide/app/settings_dialog.py plain_ide/app/help_viewer.py docs/session_log.md
   git commit -m "Phase 11.5: IDE Polish - bookmarks, session persistence, find/replace, themes, settings, help"
   ```

---

## Summary of All Files

| File | Status | Description |
|------|--------|-------------|
| `settings.py` | Modified | Bookmarks, session state, bookmark methods |
| `file_browser.py` | Modified | Bookmarks sidebar, context menus |
| `main_window.py` | Modified | Session restore, find/replace, preferences, help |
| `themes.py` | Modified | 4 new themes (Monokai, Nord, Dracula, Solarized) |
| `find_replace.py` | NEW | Find/Replace widget |
| `settings_dialog.py` | NEW | Preferences dialog |
| `help_viewer.py` | TO CREATE | Help documentation viewer (Step 6 above) |

**Only `help_viewer.py` needs to be created, and `main_window.py` needs the help menu additions.**
