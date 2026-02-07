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
