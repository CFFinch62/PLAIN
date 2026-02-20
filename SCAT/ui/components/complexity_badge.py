"""
Complexity badge widget for SCAT (Source Code Analysis Tool).

This module provides widgets for displaying complexity information
in a visually appealing badge format.
"""

from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGroupBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont
from ui.themes import SCATTheme


class ComplexityBadge(QWidget):
    """Widget for displaying complexity as a colored badge."""

    def __init__(self, complexity="O(1)", badge_type="time", parent=None):
        super().__init__(parent)
        self.complexity = complexity
        self.badge_type = badge_type  # "time" or "space"
        self.setFixedSize(80, 30)

    def set_complexity(self, complexity):
        """Set the complexity value."""
        self.complexity = complexity
        self.update()

    def set_type(self, badge_type):
        """Set the badge type (time or space)."""
        self.badge_type = badge_type
        self.update()

    def paintEvent(self, event):
        """Paint the complexity badge."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get color for complexity
        color_hex = SCATTheme.get_complexity_color(self.complexity)
        color = QColor(color_hex)

        # Ensure color is valid
        if not color.isValid():
            color = QColor("#F44336")  # Default to red if invalid

        # Draw background with border
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(QColor("#FFFFFF"), 1))  # White border for visibility
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 4, 4)

        # Draw text with better contrast
        # Use black text on light backgrounds, white on dark
        if color.lightness() > 128:
            text_color = QColor("#000000")  # Black text on light background
        else:
            text_color = QColor("#FFFFFF")  # White text on dark background

        painter.setPen(QPen(text_color))
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.complexity)


class ComplexityDisplay(QWidget):
    """Widget for displaying both time and space complexity."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Time complexity
        time_layout = QHBoxLayout()
        self.time_label = QLabel("Time:")
        self.time_label.setMinimumWidth(40)
        self.time_badge = ComplexityBadge("O(1)", "time")

        time_layout.addWidget(self.time_label)
        time_layout.addWidget(self.time_badge)
        time_layout.addStretch()

        # Space complexity
        space_layout = QHBoxLayout()
        self.space_label = QLabel("Space:")
        self.space_label.setMinimumWidth(40)
        self.space_badge = ComplexityBadge("O(1)", "space")

        space_layout.addWidget(self.space_label)
        space_layout.addWidget(self.space_badge)
        space_layout.addStretch()

        layout.addLayout(time_layout)
        layout.addLayout(space_layout)

    def set_complexity(self, time_complexity, space_complexity):
        """Set both time and space complexity."""
        self.time_badge.set_complexity(time_complexity)
        self.space_badge.set_complexity(space_complexity)

    def get_time_complexity(self):
        """Get the current time complexity."""
        return self.time_badge.complexity

    def get_space_complexity(self):
        """Get the current space complexity."""
        return self.space_badge.complexity


class QualityScoreWidget(QWidget):
    """Widget for displaying quality score with color coding."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.score = 0.0
        self.rating = "Unknown"
        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface."""
        layout = QHBoxLayout(self)

        self.score_label = QLabel("0.0")
        self.score_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.score_label.setMinimumWidth(50)

        self.rating_label = QLabel("Unknown")
        self.rating_label.setFont(QFont("Segoe UI", 10))

        layout.addWidget(self.score_label)
        layout.addWidget(QLabel("/100"))
        layout.addWidget(self.rating_label)
        layout.addStretch()

    def set_score(self, score, rating):
        """Set the quality score and rating."""
        self.score = score
        self.rating = rating

        # Update display
        self.score_label.setText(f"{score:.1f}")
        self.rating_label.setText(rating)

        # Update colors
        color = SCATTheme.get_quality_color(score)
        self.score_label.setStyleSheet(f"color: {color};")
        self.rating_label.setStyleSheet(f"color: {color};")

    def get_score(self):
        """Get the current score."""
        return self.score

    def get_rating(self):
        """Get the current rating."""
        return self.rating


class AnalysisSummaryWidget(QWidget):
    """Widget for displaying analysis summary information."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface."""
        layout = QHBoxLayout(self)  # Main horizontal layout
        layout.setSpacing(12)  # Space between containers

        # Complexity container
        complexity_container = QGroupBox("Complexity")
        complexity_layout = QHBoxLayout(complexity_container)
        complexity_layout.setSpacing(8)

        # Time complexity
        time_label = QLabel("Time:")
        time_label.setMinimumWidth(35)
        self.time_badge = ComplexityBadge("O(?)", "time")

        # Space complexity
        space_label = QLabel("Space:")
        space_label.setMinimumWidth(40)
        self.space_badge = ComplexityBadge("O(?)", "space")

        complexity_layout.addWidget(time_label)
        complexity_layout.addWidget(self.time_badge)
        complexity_layout.addWidget(space_label)
        complexity_layout.addWidget(self.space_badge)
        complexity_layout.addStretch()

        # Quality container
        quality_container = QGroupBox("Quality")
        quality_layout = QHBoxLayout(quality_container)
        quality_layout.setSpacing(8)

        self.quality_widget = QualityScoreWidget()
        quality_layout.addWidget(self.quality_widget)
        quality_layout.addStretch()

        # Add containers to main layout
        layout.addWidget(complexity_container)
        layout.addWidget(quality_container)
        layout.addStretch()

    def update_from_report(self, report):
        """Update the display from an analysis report."""
        # Update time complexity badge
        self.time_badge.set_complexity(report.overall_time_complexity)
        self.time_badge.set_type("time")

        # Update space complexity badge
        self.space_badge.set_complexity(report.overall_space_complexity)
        self.space_badge.set_type("space")

        # Update quality score
        self.quality_widget.set_score(report.quality_score, report.performance_rating)

    def clear(self):
        """Clear the display."""
        self.time_badge.set_complexity("O(?)")
        self.space_badge.set_complexity("O(?)")
        self.quality_widget.set_score(0.0, "Unknown")
