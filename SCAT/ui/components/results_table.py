"""
Results table widget for SCAT (Source Code Analysis Tool).

This module provides a table widget for displaying detailed analysis results
with sorting, filtering, and export capabilities.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                            QTableWidgetItem, QHeaderView, QPushButton, QLineEdit,
                            QLabel, QComboBox, QGroupBox, QAbstractItemView)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from ui.themes import SCATTheme


class ResultsTable(QWidget):
    """Widget for displaying analysis results in a table format."""

    itemDoubleClicked = pyqtSignal(int)  # Emitted when a row is double-clicked

    def __init__(self, parent=None):
        super().__init__(parent)
        self.results = []
        self.filtered_results = []
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Controls
        controls_group = QGroupBox("Results")
        controls_layout = QVBoxLayout(controls_group)

        # Filter and search
        filter_layout = QHBoxLayout()

        # Search box
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search results...")
        self.search_input.setMaximumWidth(200)

        # Filter by type
        self.type_filter = QComboBox()
        self.type_filter.addItems(["All Types", "Loop", "Recursion", "Built-in Function",
                                  "Built-in Method", "Assignment", "Comprehension",
                                  "Data Structure", "Iterator", "Table Access",
                                  "String Operation"])
        self.type_filter.setMaximumWidth(150)

        # Filter by complexity
        self.complexity_filter = QComboBox()
        self.complexity_filter.addItems(["All Complexities", "O(1)", "O(log n)", "O(n)",
                                       "O(n log n)", "O(n²)", "O(n³)", "O(2ⁿ)", "O(n!)"])
        self.complexity_filter.setMaximumWidth(150)

        # Clear button
        self.clear_button = QPushButton("Clear")
        self.clear_button.setMaximumWidth(80)

        filter_layout.addWidget(QLabel("Search:"))
        filter_layout.addWidget(self.search_input)
        filter_layout.addWidget(QLabel("Type:"))
        filter_layout.addWidget(self.type_filter)
        filter_layout.addWidget(QLabel("Complexity:"))
        filter_layout.addWidget(self.complexity_filter)
        filter_layout.addWidget(self.clear_button)
        filter_layout.addStretch()

        controls_layout.addLayout(filter_layout)

        # Results table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Line", "Type", "Time Complexity", "Space Complexity",
            "Confidence", "Description"
        ])

        # Configure table
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)

        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # Line
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Type
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Time
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Space
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)  # Confidence
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)  # Description

        self.table.setColumnWidth(0, 60)   # Line
        self.table.setColumnWidth(4, 80)   # Confidence

        controls_layout.addWidget(self.table)

        # Summary
        summary_layout = QHBoxLayout()
        self.summary_label = QLabel("No results")
        self.export_button = QPushButton("Export Results")
        self.export_button.setEnabled(False)

        summary_layout.addWidget(self.summary_label)
        summary_layout.addStretch()
        summary_layout.addWidget(self.export_button)

        controls_layout.addLayout(summary_layout)

        layout.addWidget(controls_group)

    def setup_connections(self):
        """Setup signal connections."""
        self.search_input.textChanged.connect(self.apply_filters)
        self.type_filter.currentTextChanged.connect(self.apply_filters)
        self.complexity_filter.currentTextChanged.connect(self.apply_filters)
        self.clear_button.clicked.connect(self.clear_filters)
        self.table.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.export_button.clicked.connect(self.export_results)

    def set_results(self, results):
        """Set the analysis results to display."""
        self.results = results
        self.filtered_results = results.copy()
        self.populate_table()
        self.update_summary()

    def populate_table(self):
        """Populate the table with filtered results."""
        self.table.setRowCount(len(self.filtered_results))

        for row, result in enumerate(self.filtered_results):
            # Line number
            line_item = QTableWidgetItem(str(result.line_number))
            line_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, line_item)

            # Analysis type
            type_item = QTableWidgetItem(result.analysis_type)
            self.table.setItem(row, 1, type_item)

            # Time complexity
            time_item = QTableWidgetItem(result.time_complexity)
            time_item.setForeground(QColor(SCATTheme.get_complexity_color(result.time_complexity)))
            time_item.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
            self.table.setItem(row, 2, time_item)

            # Space complexity
            space_item = QTableWidgetItem(result.space_complexity)
            space_item.setForeground(QColor(SCATTheme.get_complexity_color(result.space_complexity)))
            space_item.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
            self.table.setItem(row, 3, space_item)

            # Confidence
            confidence_item = QTableWidgetItem(f"{result.confidence:.1%}")
            confidence_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # Color code confidence
            if result.confidence >= 0.8:
                confidence_item.setForeground(QColor(SCATTheme.COLORS['success']))
            elif result.confidence >= 0.6:
                confidence_item.setForeground(QColor(SCATTheme.COLORS['warning']))
            else:
                confidence_item.setForeground(QColor(SCATTheme.COLORS['error']))

            self.table.setItem(row, 4, confidence_item)

            # Description
            desc_item = QTableWidgetItem(result.description)
            desc_item.setToolTip(result.description)
            self.table.setItem(row, 5, desc_item)

        # Enable/disable export button
        self.export_button.setEnabled(len(self.filtered_results) > 0)

    def apply_filters(self):
        """Apply search and filter criteria."""
        search_text = self.search_input.text().lower()
        type_filter = self.type_filter.currentText()
        complexity_filter = self.complexity_filter.currentText()

        self.filtered_results = []

        for result in self.results:
            # Apply search filter
            if search_text and search_text not in result.description.lower():
                continue

            # Apply type filter
            if type_filter != "All Types" and result.analysis_type != type_filter:
                continue

            # Apply complexity filter
            if (complexity_filter != "All Complexities" and
                result.time_complexity != complexity_filter and
                result.space_complexity != complexity_filter):
                continue

            self.filtered_results.append(result)

        self.populate_table()
        self.update_summary()

    def clear_filters(self):
        """Clear all filters and search."""
        self.search_input.clear()
        self.type_filter.setCurrentIndex(0)
        self.complexity_filter.setCurrentIndex(0)
        self.filtered_results = self.results.copy()
        self.populate_table()
        self.update_summary()

    def update_summary(self):
        """Update the summary label."""
        total = len(self.results)
        filtered = len(self.filtered_results)

        if total == 0:
            self.summary_label.setText("No results")
        elif filtered == total:
            self.summary_label.setText(f"Showing all {total} results")
        else:
            self.summary_label.setText(f"Showing {filtered} of {total} results")

    def on_item_double_clicked(self, item):
        """Handle item double-click."""
        row = item.row()
        if 0 <= row < len(self.filtered_results):
            result = self.filtered_results[row]
            self.itemDoubleClicked.emit(result.line_number)

    def export_results(self):
        """Export results to a file."""
        if not self.filtered_results:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "No Results", "No results to export.")
            return

        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        from pathlib import Path

        # Ask user for file format and location
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Results",
            "analysis_results.csv",
            "CSV Files (*.csv);;JSON Files (*.json);;All Files (*)"
        )

        if not file_path:
            return

        try:
            file_ext = Path(file_path).suffix.lower()

            if file_ext == '.json' or 'JSON' in selected_filter:
                self._export_to_json(file_path)
            else:
                self._export_to_csv(file_path)

            QMessageBox.information(
                self,
                "Export Successful",
                f"Results exported successfully to:\n{Path(file_path).name}"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"Failed to export results:\n{str(e)}"
            )

    def _export_to_csv(self, file_path):
        """Export results to CSV format."""
        import csv

        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # Write header
            writer.writerow([
                'Line Number',
                'Analysis Type',
                'Time Complexity',
                'Space Complexity',
                'Confidence',
                'Description'
            ])

            # Write data
            for result in self.filtered_results:
                writer.writerow([
                    result.line_number,
                    result.analysis_type,
                    result.time_complexity,
                    result.space_complexity,
                    f"{result.confidence:.1%}",
                    result.description
                ])

    def _export_to_json(self, file_path):
        """Export results to JSON format."""
        import json
        from datetime import datetime

        # Convert results to dictionary format
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'total_results': len(self.filtered_results),
            'results': []
        }

        for result in self.filtered_results:
            export_data['results'].append({
                'line_number': result.line_number,
                'analysis_type': result.analysis_type,
                'time_complexity': result.time_complexity,
                'space_complexity': result.space_complexity,
                'confidence': result.confidence,
                'description': result.description
            })

        with open(file_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)

    def clear(self):
        """Clear all results."""
        self.results = []
        self.filtered_results = []
        self.table.setRowCount(0)
        self.update_summary()
        self.export_button.setEnabled(False)

    def get_selected_result(self):
        """Get the currently selected result."""
        current_row = self.table.currentRow()
        if 0 <= current_row < len(self.filtered_results):
            return self.filtered_results[current_row]
        return None

    def select_result_by_line(self, line_number):
        """Select a result by line number."""
        for row, result in enumerate(self.filtered_results):
            if result.line_number == line_number:
                self.table.selectRow(row)
                self.table.scrollToItem(self.table.item(row, 0))
                break
