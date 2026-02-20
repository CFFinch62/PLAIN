"""
Analysis display widget for SCAT (Source Code Analysis Tool).

This module provides widgets for displaying analysis results including
warnings, suggestions, and detailed information.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
                            QListWidget, QListWidgetItem, QTabWidget, QLabel,
                            QGroupBox, QScrollArea, QPushButton, QSplitter)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QColor
from ui.themes import SCATTheme


class WarningsWidget(QWidget):
    """Widget for displaying analysis warnings."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Header
        header_layout = QHBoxLayout()
        self.title_label = QLabel("⚠️ Warnings")
        self.title_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.count_label = QLabel("(0)")
        self.count_label.setStyleSheet("color: #9D9D9D;")

        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.count_label)
        header_layout.addStretch()

        # Warnings list
        self.warnings_list = QListWidget()
        self.warnings_list.setMaximumHeight(150)

        layout.addLayout(header_layout)
        layout.addWidget(self.warnings_list)

    def set_warnings(self, warnings):
        """Set the warnings to display."""
        self.warnings_list.clear()
        self.count_label.setText(f"({len(warnings)})")

        if not warnings:
            item = QListWidgetItem("No warnings found")
            item.setForeground(QColor(SCATTheme.COLORS['success']))
            self.warnings_list.addItem(item)
        else:
            for warning in warnings:
                item = QListWidgetItem(f"⚠️ {warning}")
                item.setForeground(QColor(SCATTheme.COLORS['warning']))
                self.warnings_list.addItem(item)

    def clear(self):
        """Clear all warnings."""
        self.warnings_list.clear()
        self.count_label.setText("(0)")


class SuggestionsWidget(QWidget):
    """Widget for displaying optimization suggestions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Header
        header_layout = QHBoxLayout()
        self.title_label = QLabel("💡 Suggestions")
        self.title_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.count_label = QLabel("(0)")
        self.count_label.setStyleSheet("color: #9D9D9D;")

        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.count_label)
        header_layout.addStretch()

        # Suggestions list
        self.suggestions_list = QListWidget()
        self.suggestions_list.setMaximumHeight(150)

        layout.addLayout(header_layout)
        layout.addWidget(self.suggestions_list)

    def set_suggestions(self, suggestions):
        """Set the suggestions to display."""
        self.suggestions_list.clear()
        self.count_label.setText(f"({len(suggestions)})")

        if not suggestions:
            item = QListWidgetItem("No suggestions available")
            item.setForeground(QColor(SCATTheme.COLORS['text_muted']))
            self.suggestions_list.addItem(item)
        else:
            for suggestion in suggestions:
                item = QListWidgetItem(f"💡 {suggestion}")
                item.setForeground(QColor(SCATTheme.COLORS['info']))
                self.suggestions_list.addItem(item)

    def clear(self):
        """Clear all suggestions."""
        self.suggestions_list.clear()
        self.count_label.setText("(0)")


class AnalysisInfoWidget(QWidget):
    """Widget for displaying general analysis information."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(4)  # Reduce spacing

        # Analysis metadata (compact single-line layout)
        info_group = QGroupBox("Analysis Information")
        info_layout = QHBoxLayout(info_group)  # Changed to horizontal layout
        info_layout.setSpacing(12)  # Space between items

        # Create info labels (more compact)
        self.timestamp_label = QLabel("Not analyzed")
        self.language_label = QLabel("Unknown")
        self.lines_label = QLabel("0 lines")
        self.patterns_label = QLabel("0 patterns")

        # Style the labels (smaller font)
        for label in [self.timestamp_label, self.language_label,
                     self.lines_label, self.patterns_label]:
            label.setFont(QFont("Segoe UI", 8))  # Smaller font
            label.setStyleSheet("color: #D4D4D4; padding: 1px;")

        # Add labels with separators in single row
        info_layout.addWidget(QLabel("Time:"))
        info_layout.addWidget(self.timestamp_label)
        info_layout.addWidget(QLabel("|"))
        info_layout.addWidget(QLabel("Lang:"))
        info_layout.addWidget(self.language_label)
        info_layout.addWidget(QLabel("|"))
        info_layout.addWidget(self.lines_label)
        info_layout.addWidget(QLabel("|"))
        info_layout.addWidget(self.patterns_label)
        info_layout.addStretch()

        layout.addWidget(info_group)

    def update_from_report(self, report):
        """Update the display from an analysis report."""
        # Format timestamp (compact)
        try:
            from datetime import datetime
            timestamp = datetime.fromisoformat(report.timestamp.replace('Z', '+00:00'))
            formatted_time = timestamp.strftime("%H:%M:%S")  # Just time, not date
        except:
            formatted_time = "Now"

        # Update with compact format
        self.timestamp_label.setText(formatted_time)
        self.language_label.setText(report.language.title())
        self.lines_label.setText(f"{report.code_length} lines")
        self.patterns_label.setText(f"{len(report.detailed_results)} patterns")

    def clear(self):
        """Clear the information display."""
        self.timestamp_label.setText("Not analyzed")
        self.language_label.setText("Unknown")
        self.lines_label.setText("0 lines")
        self.patterns_label.setText("0 patterns")


class AnalysisDisplayWidget(QWidget):
    """Main widget for displaying analysis results."""

    lineRequested = pyqtSignal(int)  # Emitted when user wants to go to a line

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_report = None
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Create tab widget for different views
        self.tab_widget = QTabWidget()

        # Overview tab
        overview_widget = QWidget()
        overview_layout = QVBoxLayout(overview_widget)

        # Analysis info
        self.info_widget = AnalysisInfoWidget()
        overview_layout.addWidget(self.info_widget)

        # Warnings and suggestions in a splitter
        feedback_splitter = QSplitter(Qt.Orientation.Vertical)

        self.warnings_widget = WarningsWidget()
        self.suggestions_widget = SuggestionsWidget()

        feedback_splitter.addWidget(self.warnings_widget)
        feedback_splitter.addWidget(self.suggestions_widget)
        feedback_splitter.setSizes([150, 150])

        overview_layout.addWidget(feedback_splitter)

        self.tab_widget.addTab(overview_widget, "📊 Overview")

        # Raw data tab (for debugging/export)
        self.raw_data_text = QTextEdit()
        self.raw_data_text.setFont(QFont("Consolas", 9))
        self.raw_data_text.setReadOnly(True)
        self.tab_widget.addTab(self.raw_data_text, "📄 Raw Data")

        layout.addWidget(self.tab_widget)

        # Action buttons
        buttons_layout = QHBoxLayout()

        self.export_button = QPushButton("Export Report")
        self.export_button.setEnabled(False)

        self.clear_button = QPushButton("Clear Results")
        self.clear_button.setEnabled(False)

        buttons_layout.addWidget(self.export_button)
        buttons_layout.addWidget(self.clear_button)
        buttons_layout.addStretch()

        layout.addLayout(buttons_layout)

    def setup_connections(self):
        """Setup signal connections."""
        self.export_button.clicked.connect(self.export_report)
        self.clear_button.clicked.connect(self.clear_results)

    def update_from_report(self, report):
        """Update the display from an analysis report."""
        self.current_report = report

        # Update overview tab
        self.info_widget.update_from_report(report)
        self.warnings_widget.set_warnings(report.warnings)
        self.suggestions_widget.set_suggestions(report.suggestions)

        # Update raw data tab
        self.raw_data_text.setPlainText(report.to_json())

        # Enable buttons
        self.export_button.setEnabled(True)
        self.clear_button.setEnabled(True)

    def clear_results(self):
        """Clear all analysis results."""
        self.current_report = None

        # Clear overview tab
        self.info_widget.clear()
        self.warnings_widget.clear()
        self.suggestions_widget.clear()

        # Clear raw data
        self.raw_data_text.clear()

        # Disable buttons
        self.export_button.setEnabled(False)
        self.clear_button.setEnabled(False)

    def export_report(self):
        """Export the current analysis report."""
        if not self.current_report:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "No Report", "No analysis report to export.")
            return

        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        from pathlib import Path

        # Ask user for file format and location
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Analysis Report",
            "analysis_report.json",
            "JSON Files (*.json);;HTML Files (*.html);;All Files (*)"
        )

        if not file_path:
            return

        try:
            file_ext = Path(file_path).suffix.lower()

            if file_ext == '.html' or 'HTML' in selected_filter:
                self._export_to_html(file_path)
            else:
                self._export_to_json(file_path)

            QMessageBox.information(
                self,
                "Export Successful",
                f"Report exported successfully to:\n{Path(file_path).name}"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"Failed to export report:\n{str(e)}"
            )

    def _export_to_json(self, file_path):
        """Export report to JSON format."""
        import json

        # Use the report's built-in JSON export
        with open(file_path, 'w', encoding='utf-8') as jsonfile:
            jsonfile.write(self.current_report.to_json())

    def _export_to_html(self, file_path):
        """Export report to HTML format."""
        from datetime import datetime

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SCAT Analysis Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .info-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .info-card {{ background: #ecf0f1; padding: 15px; border-radius: 5px; }}
        .info-label {{ font-weight: bold; color: #7f8c8d; }}
        .info-value {{ font-size: 1.1em; color: #2c3e50; }}
        .results-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .results-table th, .results-table td {{ border: 1px solid #bdc3c7; padding: 12px; text-align: left; }}
        .results-table th {{ background-color: #3498db; color: white; }}
        .results-table tr:nth-child(even) {{ background-color: #f8f9fa; }}
        .complexity-high {{ color: #e74c3c; font-weight: bold; }}
        .complexity-medium {{ color: #f39c12; font-weight: bold; }}
        .complexity-low {{ color: #27ae60; font-weight: bold; }}
        .warnings {{ background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .suggestions {{ background-color: #d1ecf1; border: 1px solid #bee5eb; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .footer {{ margin-top: 40px; text-align: center; color: #7f8c8d; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 SCAT Analysis Report</h1>

        <div class="info-grid">
            <div class="info-card">
                <div class="info-label">Language</div>
                <div class="info-value">{self.current_report.language.title()}</div>
            </div>
            <div class="info-card">
                <div class="info-label">Code Length</div>
                <div class="info-value">{self.current_report.code_length} lines</div>
            </div>
            <div class="info-card">
                <div class="info-label">Overall Time Complexity</div>
                <div class="info-value">{self.current_report.overall_time_complexity}</div>
            </div>
            <div class="info-card">
                <div class="info-label">Overall Space Complexity</div>
                <div class="info-value">{self.current_report.overall_space_complexity}</div>
            </div>
            <div class="info-card">
                <div class="info-label">Quality Score</div>
                <div class="info-value">{self.current_report.quality_score:.1f}/100</div>
            </div>
            <div class="info-card">
                <div class="info-label">Performance Rating</div>
                <div class="info-value">{self.current_report.performance_rating}</div>
            </div>
        </div>

        <h2>📊 Detailed Analysis Results</h2>
        <table class="results-table">
            <thead>
                <tr>
                    <th>Line</th>
                    <th>Type</th>
                    <th>Time Complexity</th>
                    <th>Space Complexity</th>
                    <th>Confidence</th>
                    <th>Description</th>
                </tr>
            </thead>
            <tbody>"""

        # Add detailed results
        for result in self.current_report.detailed_results:
            time_class = self._get_complexity_class(result.time_complexity)
            space_class = self._get_complexity_class(result.space_complexity)

            html_content += f"""
                <tr>
                    <td>{result.line_number}</td>
                    <td>{result.analysis_type}</td>
                    <td class="{time_class}">{result.time_complexity}</td>
                    <td class="{space_class}">{result.space_complexity}</td>
                    <td>{result.confidence:.1%}</td>
                    <td>{result.description}</td>
                </tr>"""

        html_content += """
            </tbody>
        </table>"""

        # Add warnings if any
        if self.current_report.warnings:
            html_content += """
        <h2>⚠️ Warnings</h2>
        <div class="warnings">
            <ul>"""
            for warning in self.current_report.warnings:
                html_content += f"<li>{warning}</li>"
            html_content += """
            </ul>
        </div>"""

        # Add suggestions if any
        if self.current_report.suggestions:
            html_content += """
        <h2>💡 Suggestions</h2>
        <div class="suggestions">
            <ul>"""
            for suggestion in self.current_report.suggestions:
                html_content += f"<li>{suggestion}</li>"
            html_content += """
            </ul>
        </div>"""

        html_content += f"""
        <div class="footer">
            <p>Report generated by SCAT (Source Code Analysis Tool) on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>"""

        with open(file_path, 'w', encoding='utf-8') as htmlfile:
            htmlfile.write(html_content)

    def _get_complexity_class(self, complexity):
        """Get CSS class for complexity level."""
        complexity_lower = complexity.lower()
        if any(term in complexity_lower for term in ['exponential', 'factorial', 'n!']):
            return 'complexity-high'
        elif any(term in complexity_lower for term in ['quadratic', 'cubic', 'n^2', 'n^3', 'n²', 'n³']):
            return 'complexity-high'
        elif any(term in complexity_lower for term in ['linearithmic', 'n log n', 'nlogn']):
            return 'complexity-medium'
        elif 'linear' in complexity_lower or 'n' in complexity_lower:
            return 'complexity-medium'
        else:
            return 'complexity-low'

    def get_current_report(self):
        """Get the current analysis report."""
        return self.current_report

    def has_results(self):
        """Check if there are analysis results."""
        return self.current_report is not None
