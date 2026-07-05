"""
Proof of concept: nested colored scope boxes rendered behind code text,
BlueJ-style, using PyQt6.

The scope ranges below are HARDCODED (not parsed) — this is purely to test
whether the visual approach reads the way it's intended before building a
real incremental parser for Steps / Plain / Forge.

Run with:
    pip install PyQt6
    python scope_box_poc.py
"""

import sys

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath
from PyQt6.QtWidgets import QApplication, QPlainTextEdit, QVBoxLayout, QWidget

SAMPLE_CODE = """def calculate_total(prices, tax_rate):
    total = 0
    for price in prices:
        if price > 0:
            total += price
        else:
            print("Skipping invalid price")
    tax = total * tax_rate
    return total + tax


def main():
    prices = [10, 20, -5, 30]
    result = calculate_total(prices, 0.08)
    print(result)
"""

# Fake scope model: (start_line, end_line, depth), 0-indexed to match
# QTextDocument block numbers. A real version of this comes from parsing
# Steps/Plain/Forge source and walking the resulting block tree.
FAKE_SCOPES = [
    (0, 8, 0),    # def calculate_total(...): ... return total + tax
    (2, 6, 1),    # for price in prices: ... (through the print in else)
    (3, 6, 2),    # if price > 0: ... else: ... print(...)
    (11, 14, 0),  # def main(...): ... print(result)
]

DEPTH_COLORS = [
    QColor(255, 205, 130, 130),  # depth 0 - amber
    QColor(140, 200, 255, 140),  # depth 1 - blue
    QColor(150, 230, 160, 150),  # depth 2 - green
    QColor(220, 170, 255, 160),  # depth 3 - purple
]


class ScopeBoxEditor(QPlainTextEdit):
    def __init__(self, scopes, parent=None):
        super().__init__(parent)
        self.scopes = sorted(scopes, key=lambda s: s[2])  # shallow first, deep on top

        font = QFont("Menlo")
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setPointSize(12)
        self.setFont(font)

        self.setStyleSheet(
            "QPlainTextEdit { background-color: #ffffff; color: #1a1a1a; "
            "border: none; padding: 4px; }"
        )
        self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(" "))

    def paintEvent(self, event):
        # Qt has already filled the plain white background at this point
        # (autoFillBackground). Draw the boxes now, BEFORE the text, so the
        # text renders crisp on top of the tinted background — same order
        # BlueJ uses. Normal alpha blending (not multiply) so colors stay
        # visible against a light background instead of collapsing to dark.
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        left_margin = 4
        inset_per_depth = 7

        for start_line, end_line, depth in self.scopes:
            start_block = self.document().findBlockByNumber(start_line)
            end_block = self.document().findBlockByNumber(end_line)
            if not start_block.isValid() or not end_block.isValid():
                continue

            top = self.blockBoundingGeometry(start_block).translated(self.contentOffset()).top()
            bottom = self.blockBoundingGeometry(end_block).translated(self.contentOffset()).bottom()

            x = left_margin + depth * inset_per_depth
            rect = QRectF(x, top + 1, self.viewport().width() - 2 * x, bottom - top - 2)

            path = QPainterPath()
            path.addRoundedRect(rect, 6, 6)

            color = DEPTH_COLORS[depth % len(DEPTH_COLORS)]
            painter.fillPath(path, color)

            border = QColor(color)
            border.setAlpha(220)
            painter.setPen(border)
            painter.drawPath(path)

        painter.end()

        # Now draw the text on top of the boxes we just painted.
        super().paintEvent(event)


def main():
    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle("Nested Scope Box — Proof of Concept")
    window.resize(760, 520)

    layout = QVBoxLayout(window)
    layout.setContentsMargins(0, 0, 0, 0)

    editor = ScopeBoxEditor(FAKE_SCOPES)
    editor.setPlainText(SAMPLE_CODE)
    layout.addWidget(editor)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
