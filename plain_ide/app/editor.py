"""
Code Editor Widget for PLAIN IDE
Provides a code editor with line numbers, syntax highlighting, and breakpoint support
"""

from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit, QTabWidget
from PyQt6.QtCore import Qt, QRect, QSize, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QTextFormat, QFont, QTextCursor, QMouseEvent

from plain_ide.app.syntax import PlainHighlighter
from plain_ide.app.themes import Theme
from plain_ide.app.settings import SettingsManager


class LineNumberArea(QWidget):
    """Widget for displaying line numbers and breakpoints in the editor gutter"""

    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self) -> QSize:
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse click to toggle breakpoint"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Calculate which line was clicked
            block = self.editor.firstVisibleBlock()
            top = self.editor.blockBoundingGeometry(block).translated(
                self.editor.contentOffset()).top()

            while block.isValid():
                block_top = top
                block_bottom = top + self.editor.blockBoundingRect(block).height()

                if block_top <= event.position().y() < block_bottom:
                    line = block.blockNumber() + 1
                    self.editor.toggle_breakpoint(line)
                    break

                block = block.next()
                top = block_bottom


class CodeEditor(QPlainTextEdit):
    """Code editor with line numbers, syntax highlighting, and breakpoint support"""

    file_modified = pyqtSignal(bool)
    breakpoint_toggled = pyqtSignal(int)  # line number

    def __init__(self, parent=None, theme: Theme = None, settings: SettingsManager = None):
        super().__init__(parent)
        self.theme = theme
        self.settings = settings
        self.file_path = None
        self._modified = False
        self._breakpoints: set = set()  # Set of line numbers with breakpoints
        self._debug_line: int = -1  # Current debug execution line (-1 = none)

        # Create line number area
        self.line_number_area = LineNumberArea(self)

        # Create syntax highlighter
        self.highlighter = PlainHighlighter(self.document(), theme)

        # Connect signals
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.textChanged.connect(self._on_text_changed)

        # Initial setup
        self.update_line_number_area_width(0)
        self.highlight_current_line()
        self.apply_settings()
    
    def apply_settings(self):
        """Apply editor settings"""
        if self.settings:
            s = self.settings.settings.editor
            font = QFont(s.font_family, s.font_size)
            font.setStyleHint(QFont.StyleHint.Monospace)
            self.setFont(font)
            self.setTabStopDistance(s.tab_width * self.fontMetrics().horizontalAdvance(' '))
            self.setLineWrapMode(
                QPlainTextEdit.LineWrapMode.WidgetWidth if s.word_wrap 
                else QPlainTextEdit.LineWrapMode.NoWrap
            )
    
    def apply_theme(self, theme: Theme):
        """Apply theme to editor"""
        self.theme = theme
        self.highlighter.set_theme(theme)
        
        # Set editor colors
        self.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {theme.editor_background};
                color: {theme.editor_foreground};
                selection-background-color: {theme.editor_selection};
                border: none;
            }}
        """)
        
        self.highlight_current_line()
        self.viewport().update()
        self.line_number_area.update()
    
    def line_number_area_width(self) -> int:
        """Calculate width needed for line number area (includes breakpoint margin)"""
        digits = len(str(max(1, self.blockCount())))
        # 20px for breakpoint circle + padding + line numbers
        space = 28 + self.fontMetrics().horizontalAdvance('9') * digits
        return space
    
    def update_line_number_area_width(self, _):
        """Update editor margins for line number area"""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
    
    def update_line_number_area(self, rect, dy):
        """Update line number area when editor scrolls"""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)
    
    def resizeEvent(self, event):
        """Handle resize events"""
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), 
                                                 self.line_number_area_width(), cr.height()))
    
    def line_number_area_paint_event(self, event):
        """Paint line numbers and breakpoint markers in the gutter"""
        painter = QPainter(self.line_number_area)

        if self.theme:
            painter.fillRect(event.rect(), QColor(self.theme.editor_gutter_bg))
            text_color = QColor(self.theme.editor_gutter_fg)
            breakpoint_color = QColor(self.theme.error)
            debug_line_color = QColor(self.theme.warning)
        else:
            painter.fillRect(event.rect(), QColor("#1e1e2e"))
            text_color = QColor("#6c7086")
            breakpoint_color = QColor("#f38ba8")
            debug_line_color = QColor("#f9e2af")

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                line_num = block_number + 1

                # Draw breakpoint marker (red circle)
                if line_num in self._breakpoints:
                    painter.setBrush(breakpoint_color)
                    painter.setPen(Qt.PenStyle.NoPen)
                    circle_size = 10
                    circle_y = top + (self.fontMetrics().height() - circle_size) // 2
                    painter.drawEllipse(4, int(circle_y), circle_size, circle_size)

                # Highlight current debug line
                if line_num == self._debug_line:
                    painter.fillRect(0, top, self.line_number_area.width(),
                                    self.fontMetrics().height(), debug_line_color)
                    painter.setPen(QColor("#000000"))
                else:
                    painter.setPen(text_color)

                # Draw line number
                number = str(line_num)
                painter.drawText(18, top, self.line_number_area.width() - 22,
                               self.fontMetrics().height(),
                               Qt.AlignmentFlag.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1
    
    def highlight_current_line(self):
        """Highlight the current line"""
        extra_selections = []
        
        if not self.isReadOnly() and self.theme:
            selection = QTextEdit.ExtraSelection()
            line_color = QColor(self.theme.editor_line_highlight)
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        
        self.setExtraSelections(extra_selections)
    
    def _on_text_changed(self):
        """Handle text changes"""
        if not self._modified:
            self._modified = True
            self.file_modified.emit(True)
    
    def set_modified(self, modified: bool):
        """Set the modified state"""
        self._modified = modified
        self.file_modified.emit(modified)
    
    def is_modified(self) -> bool:
        """Check if document has been modified"""
        return self._modified

    # Breakpoint methods
    def toggle_breakpoint(self, line: int):
        """Toggle a breakpoint at the given line"""
        if line in self._breakpoints:
            self._breakpoints.remove(line)
        else:
            self._breakpoints.add(line)
        self.line_number_area.update()
        self.breakpoint_toggled.emit(line)

    def get_breakpoints(self) -> set:
        """Get the set of breakpoint line numbers"""
        return self._breakpoints.copy()

    def clear_breakpoints(self):
        """Clear all breakpoints"""
        self._breakpoints.clear()
        self.line_number_area.update()

    def set_debug_line(self, line: int):
        """Set the current debug execution line (-1 to clear)"""
        self._debug_line = line
        self.line_number_area.update()

        # Scroll to the debug line if set
        if line > 0:
            block = self.document().findBlockByLineNumber(line - 1)
            cursor = QTextCursor(block)
            self.setTextCursor(cursor)
            self.centerCursor()

    def clear_debug_line(self):
        """Clear the debug line highlight"""
        self._debug_line = -1
        self.line_number_area.update()

