"""
Code editor widget for SCAT (Source Code Analysis Tool).

This module provides a syntax-highlighted code editor with line numbers
and language-specific features.
"""

from PyQt6.QtWidgets import QWidget, QTextEdit
from PyQt6.QtCore import Qt, pyqtSignal, QRect
from PyQt6.QtGui import QFont, QPainter, QColor, QTextFormat

# Import the modular syntax highlighting system
from .syntax_highlighting import SyntaxHighlighterFactory


class LineNumberArea(QWidget):
    """Line number area for the code editor."""

    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return self.code_editor.line_number_area_width()

    def paintEvent(self, event):
        self.code_editor.line_number_area_paint_event(event)





class CodeEditor(QTextEdit):
    """Code editor with syntax highlighting and line numbers."""

    textChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Setup editor
        self.setFont(QFont('Consolas', 11))
        # Set tab width (PyQt6 uses setTabStopDistance)
        try:
            self.setTabStopDistance(40)  # 4 spaces
        except AttributeError:
            # Fallback for older PyQt versions
            self.setTabStopWidth(40)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

        # Line number area
        self.line_number_area = LineNumberArea(self)

        # Connect signals (PyQt6 compatible)
        try:
            # Try PyQt6 style first
            self.document().blockCountChanged.connect(self.update_line_number_area_width)
            self.verticalScrollBar().valueChanged.connect(self.update_line_number_area_scroll)
        except AttributeError:
            # Fallback for older PyQt versions
            try:
                self.blockCountChanged.connect(self.update_line_number_area_width)
                self.updateRequest.connect(self.update_line_number_area)
            except AttributeError:
                pass  # Skip if signals don't exist

        self.cursorPositionChanged.connect(self.highlight_current_line)

        # Setup syntax highlighting
        self.highlighter = None
        self.set_language('python')

        # Initial setup
        self.update_line_number_area_width()
        self.highlight_current_line()

    def set_language(self, language):
        """Set syntax highlighting for the specified language."""
        # Remove existing highlighter
        if self.highlighter:
            self.highlighter.setDocument(None)

        # Create new highlighter using the factory
        self.highlighter = SyntaxHighlighterFactory.create_highlighter(language, self.document())

        if not self.highlighter:
            print(f"Warning: No syntax highlighter available for language '{language}'")
            print(f"Supported languages: {', '.join(SyntaxHighlighterFactory.get_supported_languages())}")

    def line_number_area_width(self):
        """Calculate the width needed for line numbers."""
        digits = 1
        # Use document().blockCount() instead of blockCount()
        max_num = max(1, self.document().blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1

        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, *_):
        """Update the width of the line number area."""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area_scroll(self):
        """Update line number area when scrolling."""
        self.line_number_area.update()

    def update_line_number_area(self, rect, dy):
        """Update the line number area when scrolling."""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(),
                                       self.line_number_area.width(),
                                       rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        """Handle resize events."""
        super().resizeEvent(event)

        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(),
                  self.line_number_area_width(), cr.height())
        )

    def line_number_area_paint_event(self, event):
        """Paint the line number area."""
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#2D2D30"))

        # Use document() methods for PyQt6 compatibility
        try:
            block = self.firstVisibleBlock()
        except AttributeError:
            # Fallback: just paint line numbers for visible area
            painter.setPen(QColor("#858585"))
            height = self.fontMetrics().height()
            y = event.rect().top()
            line_num = 1
            while y < event.rect().bottom():
                painter.drawText(0, y, self.line_number_area.width(), height,
                               Qt.AlignmentFlag.AlignRight, str(line_num))
                y += height
                line_num += 1
            return

        block_number = block.blockNumber()
        try:
            top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
            bottom = top + self.blockBoundingRect(block).height()
        except AttributeError:
            # Simplified fallback
            top = 0
            bottom = self.fontMetrics().height()

        height = self.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                number = str(block_number + 1)
                painter.setPen(QColor("#858585"))
                painter.drawText(0, int(top), self.line_number_area.width(), height,
                               Qt.AlignmentFlag.AlignRight, number)

            block = block.next()
            top = bottom
            try:
                bottom = top + self.blockBoundingRect(block).height()
            except AttributeError:
                bottom = top + height
            block_number += 1

    def highlight_current_line(self):
        """Highlight the current line."""
        extra_selections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()

            line_color = QColor("#2D2D30").lighter(120)
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)

        self.setExtraSelections(extra_selections)

    def get_current_line_number(self):
        """Get the current line number (1-based)."""
        cursor = self.textCursor()
        return cursor.blockNumber() + 1

    def goto_line(self, line_number):
        """Go to a specific line number (1-based)."""
        cursor = self.textCursor()
        cursor.movePosition(cursor.MoveOperation.Start)
        for _ in range(line_number - 1):
            cursor.movePosition(cursor.MoveOperation.Down)
        self.setTextCursor(cursor)
        self.centerCursor()

    def insert_sample_code(self, language):
        """Insert sample code for the specified language."""
        samples = {
            'python': '''def bubble_sort(arr):
    """Bubble sort algorithm - O(n²) time complexity"""
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

def fibonacci(n):
    """Recursive Fibonacci - O(2ⁿ) time complexity"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Test the functions
numbers = [64, 34, 25, 12, 22, 11, 90]
sorted_numbers = bubble_sort(numbers)
print(f"Sorted: {sorted_numbers}")
print(f"Fibonacci(10): {fibonacci(10)}")''',

            'ruby': '''def bubble_sort(arr)
  # Bubble sort algorithm - O(n²) time complexity
  n = arr.length
  for i in 0...n
    for j in 0...(n - i - 1)
      if arr[j] > arr[j + 1]
        arr[j], arr[j + 1] = arr[j + 1], arr[j]
      end
    end
  end
  arr
end

def fibonacci(n)
  # Recursive Fibonacci - O(2ⁿ) time complexity
  return n if n <= 1
  fibonacci(n-1) + fibonacci(n-2)
end

# Test the functions
numbers = [64, 34, 25, 12, 22, 11, 90]
sorted_numbers = bubble_sort(numbers)
puts "Sorted: #{sorted_numbers}"
puts "Fibonacci(10): #{fibonacci(10)}"''',

            'lua': '''function bubble_sort(arr)
  -- Bubble sort algorithm - O(n²) time complexity
  local n = #arr
  for i = 1, n do
    for j = 1, n - i do
      if arr[j] > arr[j + 1] then
        arr[j], arr[j + 1] = arr[j + 1], arr[j]
      end
    end
  end
  return arr
end

function fibonacci(n)
  -- Recursive Fibonacci - O(2ⁿ) time complexity
  if n <= 1 then
    return n
  else
    return fibonacci(n-1) + fibonacci(n-2)
  end
end

-- Test the functions
local numbers = {64, 34, 25, 12, 22, 11, 90}
local sorted_numbers = bubble_sort(numbers)
print("Sorted: " .. table.concat(sorted_numbers, ", "))
print("Fibonacci(10): " .. fibonacci(10))''',

            'basic': '''REM Bubble Sort Algorithm - O(n²) time complexity
DIM numbers(7) AS INTEGER
DIM i AS INTEGER, j AS INTEGER, n AS INTEGER, temp AS INTEGER

REM Initialize array
numbers(1) = 64: numbers(2) = 34: numbers(3) = 25: numbers(4) = 12
numbers(5) = 22: numbers(6) = 11: numbers(7) = 90
n = 7

REM Bubble sort implementation
FOR i = 1 TO n
    FOR j = 1 TO n - i
        IF numbers(j) > numbers(j + 1) THEN
            temp = numbers(j)
            numbers(j) = numbers(j + 1)
            numbers(j + 1) = temp
        END IF
    NEXT j
NEXT i

REM Display sorted array
PRINT "Sorted array:"
FOR i = 1 TO n
    PRINT numbers(i);
    IF i < n THEN PRINT ", ";
NEXT i
PRINT

REM Fibonacci function (recursive approach)
FUNCTION fibonacci(n AS INTEGER) AS INTEGER
    IF n <= 1 THEN
        fibonacci = n
    ELSE
        fibonacci = fibonacci(n - 1) + fibonacci(n - 2)
    END IF
END FUNCTION

REM Test fibonacci
PRINT "Fibonacci(10): "; fibonacci(10)''',

            'pseudocode': '''// Bubble sort algorithm - O(n²) time complexity
DECLARE numbers : ARRAY[1:7] OF INTEGER
DECLARE i, j, temp : INTEGER

// Initialize test data
numbers[1] ← 64
numbers[2] ← 34
numbers[3] ← 25
numbers[4] ← 12
numbers[5] ← 22
numbers[6] ← 11
numbers[7] ← 90

// Bubble sort implementation
FOR i ← 1 TO 7
    FOR j ← 1 TO 7 - i
        IF numbers[j] > numbers[j + 1]
            THEN
                temp ← numbers[j]
                numbers[j] ← numbers[j + 1]
                numbers[j + 1] ← temp
        ENDIF
    NEXT j
NEXT i

// Display sorted array
OUTPUT "Sorted array: "
FOR i ← 1 TO 7
    OUTPUT numbers[i], " "
NEXT i

// Fibonacci function example
FUNCTION Fibonacci(n : INTEGER) RETURNS INTEGER
    IF n <= 1
        THEN
            RETURN n
        ELSE
            RETURN Fibonacci(n-1) + Fibonacci(n-2)
    ENDIF
ENDFUNCTION

// Test fibonacci
OUTPUT "Fibonacci(10): ", Fibonacci(10)''',

            'plain': '''rem: Bubble sort algorithm - O(n²) time complexity
task BubbleSort using (lstNumbers)
    var intN = len(lstNumbers)

    loop i from 0 to intN - 1
        loop j from 0 to intN - i - 2
            if lstNumbers[j] > lstNumbers[j + 1]
                var temp = lstNumbers[j]
                lstNumbers[j] = lstNumbers[j + 1]
                lstNumbers[j + 1] = temp

    deliver lstNumbers

rem: Recursive Fibonacci - O(2ⁿ) time complexity
task Fibonacci using (intN)
    if intN <= 1
        deliver intN

    var a = Fibonacci(intN - 1)
    var b = Fibonacci(intN - 2)
    deliver a + b''',

            'steps': '''note: Bubble Sort Algorithm - O(n²) time complexity
step: bubble_sort
    belongs to: main
    expects: items as list
    returns: list

    declare: n as number
    declare: i as number
    declare: temp as number

    do:
        set n to length of items
        repeat n times
            repeat for each i in items
                if i is greater than items[i + 1]
                    set temp to items[i]
                    set items[i] to items[i + 1]
                    set items[i + 1] to temp
        return items

note: Fibonacci - O(2ⁿ) recursive
step: fibonacci
    expects: n as number
    returns: number
    do:
        if n is less than or equal to 1
            return n
        call fibonacci with n - 1 storing result in a
        call fibonacci with n - 2 storing result in b
        return a + b

note: Test the steps
set numbers to [64, 34, 25, 12, 22, 11, 90]
call bubble_sort with numbers storing result in sorted_list
display "Sorted: " added to sorted_list as text
call fibonacci with 10 storing result in fib
display "Fibonacci(10): " added to fib as text'''
        }

        sample = samples.get(language.lower(), '')
        if sample:
            self.setPlainText(sample)
            self.set_language(language)
