#!/usr/bin/env python3
"""
DEPRECATED: This file is being refactored into a modular architecture.
Please use main.py for the new modular code analysis tool.

Legacy Formal Code Analysis Application
A comprehensive standalone tool for analyzing code complexity, performance, and quality.

Features:
- Time and space complexity analysis
- Multi-language support (extensible)
- API interface for IDE integration
- Professional reporting
- Export capabilities
"""

import sys
import os
import json
import ast
import re
import traceback
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QTextEdit, QPushButton, QLabel,
                            QSplitter, QTabWidget, QListWidget, QListWidgetItem,
                            QGroupBox, QScrollArea, QProgressBar, QMenuBar,
                            QMenu, QFileDialog, QMessageBox, QComboBox,
                            QSpinBox, QCheckBox, QTableWidget, QTableWidgetItem,
                            QHeaderView, QFrame, QGridLayout, QTextBrowser)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QObject
from PyQt6.QtNetwork import QTcpServer, QTcpSocket
from PyQt6.QtGui import QFont, QTextCharFormat, QColor, QAction, QPixmap, QIcon


@dataclass
class ComplexityResult:
    """Data class for complexity analysis results."""
    time_complexity: str
    space_complexity: str
    line_number: int
    description: str
    analysis_type: str
    confidence: float
    suggestions: List[str]


@dataclass
class AnalysisReport:
    """Complete analysis report for a code snippet."""
    timestamp: str
    language: str
    code_length: int
    overall_time_complexity: str
    overall_space_complexity: str
    detailed_results: List[ComplexityResult]
    warnings: List[str]
    suggestions: List[str]
    quality_score: float
    performance_rating: str


class AdvancedComplexityAnalyzer:
    """Advanced code complexity analyzer with time and space analysis."""

    def __init__(self):
        self.time_patterns = {
            'O(1)': {'weight': 1, 'description': 'Constant time - excellent performance'},
            'O(log n)': {'weight': 2, 'description': 'Logarithmic time - very good performance'},
            'O(n)': {'weight': 3, 'description': 'Linear time - good performance'},
            'O(n log n)': {'weight': 4, 'description': 'Linearithmic time - acceptable performance'},
            'O(n²)': {'weight': 5, 'description': 'Quadratic time - poor performance for large inputs'},
            'O(n³)': {'weight': 6, 'description': 'Cubic time - very poor performance'},
            'O(2ⁿ)': {'weight': 7, 'description': 'Exponential time - extremely poor performance'},
            'O(n!)': {'weight': 8, 'description': 'Factorial time - impractical for large inputs'}
        }

        self.space_patterns = {
            'O(1)': {'weight': 1, 'description': 'Constant space - excellent memory efficiency'},
            'O(log n)': {'weight': 2, 'description': 'Logarithmic space - very good memory efficiency'},
            'O(n)': {'weight': 3, 'description': 'Linear space - acceptable memory usage'},
            'O(n²)': {'weight': 4, 'description': 'Quadratic space - poor memory efficiency'},
            'O(2ⁿ)': {'weight': 5, 'description': 'Exponential space - extremely poor memory efficiency'}
        }

        # Built-in function complexities
        self.builtin_complexities = {
            'sorted': {'time': 'O(n log n)', 'space': 'O(n)'},
            'max': {'time': 'O(n)', 'space': 'O(1)'},
            'min': {'time': 'O(n)', 'space': 'O(1)'},
            'sum': {'time': 'O(n)', 'space': 'O(1)'},
            'len': {'time': 'O(1)', 'space': 'O(1)'},
            'list': {'time': 'O(n)', 'space': 'O(n)'},
            'dict': {'time': 'O(n)', 'space': 'O(n)'},
            'set': {'time': 'O(n)', 'space': 'O(n)'},
        }

    def analyze_code(self, code: str, language: str = 'python') -> AnalysisReport:
        """Perform comprehensive code analysis."""
        try:
            if language.lower() != 'python':
                raise NotImplementedError(f"Language '{language}' not yet supported")

            tree = ast.parse(code)

            # Initialize analysis state
            analysis_state = {
                'detailed_results': [],
                'warnings': [],
                'suggestions': [],
                'overall_time': 'O(1)',
                'overall_space': 'O(1)',
                'quality_issues': []
            }

            # Perform analysis
            self._analyze_ast_node(tree, analysis_state, depth=0)

            # Calculate quality score
            quality_score = self._calculate_quality_score(analysis_state)
            performance_rating = self._get_performance_rating(
                analysis_state['overall_time'],
                analysis_state['overall_space']
            )

            # Create report
            report = AnalysisReport(
                timestamp=datetime.now().isoformat(),
                language=language,
                code_length=len(code.splitlines()),
                overall_time_complexity=analysis_state['overall_time'],
                overall_space_complexity=analysis_state['overall_space'],
                detailed_results=analysis_state['detailed_results'],
                warnings=analysis_state['warnings'],
                suggestions=analysis_state['suggestions'],
                quality_score=quality_score,
                performance_rating=performance_rating
            )

            return report

        except SyntaxError as e:
            return self._create_error_report(f"Syntax Error: {str(e)}", language, code)
        except Exception as e:
            return self._create_error_report(f"Analysis Error: {str(e)}", language, code)

    def _analyze_ast_node(self, node, state, depth=0, in_loop=False):
        """Recursively analyze AST nodes for complexity patterns."""
        if isinstance(node, (ast.For, ast.While)):
            self._analyze_loop(node, state, depth, in_loop)
            # Analyze loop body with increased depth
            for child in ast.iter_child_nodes(node):
                self._analyze_ast_node(child, state, depth + 1, True)

        elif isinstance(node, ast.FunctionDef):
            self._analyze_function(node, state, depth)
            # Analyze function body
            for child in ast.iter_child_nodes(node):
                self._analyze_ast_node(child, state, depth, in_loop)

        elif isinstance(node, ast.Call):
            self._analyze_function_call(node, state, depth, in_loop)
            # Analyze call arguments
            for child in ast.iter_child_nodes(node):
                self._analyze_ast_node(child, state, depth, in_loop)

        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            self._analyze_assignment(node, state, depth, in_loop)
            # Analyze assignment value
            for child in ast.iter_child_nodes(node):
                self._analyze_ast_node(child, state, depth, in_loop)

        elif isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp)):
            self._analyze_comprehension(node, state, depth, in_loop)
            # Analyze comprehension components
            for child in ast.iter_child_nodes(node):
                self._analyze_ast_node(child, state, depth, in_loop)

        else:
            # Recursively analyze child nodes
            for child in ast.iter_child_nodes(node):
                self._analyze_ast_node(child, state, depth, in_loop)

    def _analyze_loop(self, node, state, depth, in_loop):
        """Analyze loop complexity (time and space)."""
        line_num = getattr(node, 'lineno', 'Unknown')

        # Time complexity based on nesting depth
        if depth == 0:
            time_complexity = 'O(n)'
            time_desc = "Single loop - linear time complexity"
        elif depth == 1:
            time_complexity = 'O(n²)'
            time_desc = "Nested loop - quadratic time complexity"
            state['warnings'].append("Nested loops can cause performance issues with large datasets")
        else:
            time_complexity = f'O(n^{depth + 1})'
            time_desc = f"Multiple nested loops (depth {depth + 1}) - polynomial time complexity"
            state['warnings'].append(f"Deep nesting (depth {depth + 1}) causes severe performance degradation")

        # Space complexity (loops themselves don't typically add space)
        space_complexity = 'O(1)'
        space_desc = "Loop variables use constant space"

        # Create result
        result = ComplexityResult(
            time_complexity=time_complexity,
            space_complexity=space_complexity,
            line_number=line_num,
            description=f"{time_desc}. {space_desc}",
            analysis_type="Loop",
            confidence=0.9,
            suggestions=self._get_loop_suggestions(depth)
        )

        state['detailed_results'].append(result)

        # Update overall complexity
        self._update_overall_complexity(state, time_complexity, space_complexity)

    def _analyze_function(self, node, state, depth):
        """Analyze function definition for recursion."""
        func_name = node.name
        line_num = getattr(node, 'lineno', 'Unknown')

        # Check for recursion
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                if child.func.id == func_name:
                    # Recursive function detected
                    time_complexity = 'O(2ⁿ)'
                    space_complexity = 'O(n)'  # Call stack depth

                    result = ComplexityResult(
                        time_complexity=time_complexity,
                        space_complexity=space_complexity,
                        line_number=line_num,
                        description=f"Recursive function '{func_name}' - exponential time, linear space (call stack)",
                        analysis_type="Recursion",
                        confidence=0.8,
                        suggestions=[
                            f"Consider memoization for '{func_name}' to improve time complexity",
                            f"Consider iterative approach to reduce space complexity",
                            "Use dynamic programming if applicable"
                        ]
                    )

                    state['detailed_results'].append(result)
                    state['warnings'].append(f"Recursive function '{func_name}' may have exponential complexity")

                    self._update_overall_complexity(state, time_complexity, space_complexity)
                    break

    def _analyze_function_call(self, node, state, depth, in_loop):
        """Analyze function calls for known complexity patterns."""
        line_num = getattr(node, 'lineno', 'Unknown')

        func_name = None
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        if func_name and func_name in self.builtin_complexities:
            complexity_info = self.builtin_complexities[func_name]
            time_complexity = complexity_info['time']
            space_complexity = complexity_info['space']

            # Adjust complexity if inside loop
            if in_loop and time_complexity != 'O(1)':
                time_complexity = self._multiply_complexity(time_complexity, 'O(n)')

            result = ComplexityResult(
                time_complexity=time_complexity,
                space_complexity=space_complexity,
                line_number=line_num,
                description=f"Built-in function '{func_name}()' call",
                analysis_type="Built-in Function",
                confidence=0.95,
                suggestions=self._get_builtin_suggestions(func_name, in_loop)
            )

            state['detailed_results'].append(result)
            self._update_overall_complexity(state, time_complexity, space_complexity)

    def _analyze_assignment(self, node, state, depth, in_loop):
        """Analyze variable assignments for space complexity."""
        line_num = getattr(node, 'lineno', 'Unknown')

        # Check if assignment creates new data structures
        if isinstance(node.value, (ast.List, ast.Dict, ast.Set)):
            space_complexity = 'O(n)' if len(getattr(node.value, 'elts', getattr(node.value, 'keys', []))) > 0 else 'O(1)'
            time_complexity = 'O(1)'

            result = ComplexityResult(
                time_complexity=time_complexity,
                space_complexity=space_complexity,
                line_number=line_num,
                description="Data structure creation",
                analysis_type="Assignment",
                confidence=0.8,
                suggestions=["Consider memory usage for large data structures"]
            )

            state['detailed_results'].append(result)
            self._update_overall_complexity(state, time_complexity, space_complexity)

    def _analyze_comprehension(self, node, state, depth, in_loop):
        """Analyze list/dict/set comprehensions."""
        line_num = getattr(node, 'lineno', 'Unknown')

        # Comprehensions are typically O(n) time and O(n) space
        time_complexity = 'O(n)'
        space_complexity = 'O(n)'

        comp_type = type(node).__name__.replace('Comp', ' comprehension')

        result = ComplexityResult(
            time_complexity=time_complexity,
            space_complexity=space_complexity,
            line_number=line_num,
            description=f"{comp_type} - creates new collection",
            analysis_type="Comprehension",
            confidence=0.9,
            suggestions=["Consider generator expressions for memory efficiency if full list not needed"]
        )

        state['detailed_results'].append(result)
        self._update_overall_complexity(state, time_complexity, space_complexity)

    def _update_overall_complexity(self, state, time_complexity, space_complexity):
        """Update overall complexity with worse of current and new."""
        if self._is_worse_complexity(time_complexity, state['overall_time']):
            state['overall_time'] = time_complexity

        if self._is_worse_complexity(space_complexity, state['overall_space']):
            state['overall_space'] = space_complexity

    def _is_worse_complexity(self, new_complexity, current_complexity):
        """Compare complexities and return True if new is worse."""
        time_order = ['O(1)', 'O(log n)', 'O(n)', 'O(n log n)', 'O(n²)', 'O(n³)', 'O(2ⁿ)', 'O(n!)']

        try:
            new_index = time_order.index(new_complexity)
        except ValueError:
            return True  # Unknown complexity, assume worse

        try:
            current_index = time_order.index(current_complexity)
        except ValueError:
            return False  # Current is unknown, keep new

        return new_index > current_index

    def _multiply_complexity(self, complexity1, complexity2):
        """Multiply two complexity expressions (for nested operations)."""
        # Simplified complexity multiplication
        if complexity1 == 'O(1)':
            return complexity2
        if complexity2 == 'O(1)':
            return complexity1
        if complexity1 == 'O(n)' and complexity2 == 'O(n)':
            return 'O(n²)'
        if 'O(n²)' in [complexity1, complexity2]:
            return 'O(n²)'
        return 'O(n²)'  # Conservative estimate

    def _get_loop_suggestions(self, depth):
        """Get optimization suggestions for loops."""
        suggestions = []
        if depth == 1:
            suggestions.extend([
                "Consider if the inner loop can be eliminated",
                "Look for opportunities to use hash tables or sets for O(1) lookups",
                "Consider sorting data first if it enables more efficient algorithms"
            ])
        elif depth > 1:
            suggestions.extend([
                "Deep nesting indicates potential for significant optimization",
                "Consider breaking down into separate functions",
                "Look for dynamic programming opportunities"
            ])
        return suggestions

    def _get_builtin_suggestions(self, func_name, in_loop):
        """Get suggestions for built-in function usage."""
        suggestions = []
        if in_loop and func_name in ['sorted', 'max', 'min', 'sum']:
            suggestions.append(f"Calling {func_name}() inside a loop increases overall complexity")
        if func_name == 'sorted':
            suggestions.append("Consider if data can be kept sorted to avoid repeated sorting")
        return suggestions

    def _calculate_quality_score(self, state):
        """Calculate overall code quality score (0-100)."""
        base_score = 100

        # Deduct points for complexity
        time_weight = self.time_patterns.get(state['overall_time'], {}).get('weight', 5)
        space_weight = self.space_patterns.get(state['overall_space'], {}).get('weight', 3)

        complexity_penalty = (time_weight - 1) * 10 + (space_weight - 1) * 5

        # Deduct points for warnings
        warning_penalty = len(state['warnings']) * 5

        # Deduct points for quality issues
        quality_penalty = len(state['quality_issues']) * 3

        final_score = max(0, base_score - complexity_penalty - warning_penalty - quality_penalty)
        return final_score

    def _get_performance_rating(self, time_complexity, space_complexity):
        """Get human-readable performance rating."""
        time_weight = self.time_patterns.get(time_complexity, {}).get('weight', 5)
        space_weight = self.space_patterns.get(space_complexity, {}).get('weight', 3)

        avg_weight = (time_weight + space_weight) / 2

        if avg_weight <= 2:
            return "Excellent"
        elif avg_weight <= 3:
            return "Good"
        elif avg_weight <= 4:
            return "Fair"
        elif avg_weight <= 5:
            return "Poor"
        else:
            return "Very Poor"

    def _create_error_report(self, error_msg, language, code):
        """Create error report for failed analysis."""
        return AnalysisReport(
            timestamp=datetime.now().isoformat(),
            language=language,
            code_length=len(code.splitlines()) if code else 0,
            overall_time_complexity="Error",
            overall_space_complexity="Error",
            detailed_results=[],
            warnings=[error_msg],
            suggestions=["Fix syntax errors and try again"],
            quality_score=0.0,
            performance_rating="Unable to analyze"
        )


class CodeAnalysisAPI(QObject):
    """API interface for receiving code from IDEs."""

    analysis_received = pyqtSignal(str, str, str)  # code, language, source_app

    def __init__(self, port=12345):
        super().__init__()
        self.port = port
        self.server = QTcpServer()
        self.server.newConnection.connect(self.handle_new_connection)

    def start_server(self):
        """Start the API server."""
        if self.server.listen(port=self.port):
            print(f"Code Analysis API server started on port {self.port}")
            return True
        else:
            print(f"Failed to start server on port {self.port}")
            return False

    def stop_server(self):
        """Stop the API server."""
        self.server.close()
        print("Code Analysis API server stopped")

    def handle_new_connection(self):
        """Handle new connection from IDE."""
        socket = self.server.nextPendingConnection()
        socket.readyRead.connect(lambda: self.read_data(socket))

    def read_data(self, socket):
        """Read data from connected socket."""
        try:
            data = socket.readAll().data().decode('utf-8')
            request = json.loads(data)

            code = request.get('code', '')
            language = request.get('language', 'python')
            source_app = request.get('source_app', 'Unknown')

            self.analysis_received.emit(code, language, source_app)

            # Send acknowledgment
            response = json.dumps({"status": "received", "message": "Code analysis started"})
            socket.write(response.encode('utf-8'))
            socket.disconnectFromHost()

        except Exception as e:
            error_response = json.dumps({"status": "error", "message": str(e)})
            socket.write(error_response.encode('utf-8'))
            socket.disconnectFromHost()


class AnalysisWorker(QThread):
    """Worker thread for performing code analysis."""

    analysis_complete = pyqtSignal(object)  # AnalysisReport
    analysis_progress = pyqtSignal(str)  # Progress message

    def __init__(self, analyzer, code, language):
        super().__init__()
        self.analyzer = analyzer
        self.code = code
        self.language = language

    def run(self):
        """Perform analysis in background thread."""
        try:
            self.analysis_progress.emit("Starting analysis...")
            report = self.analyzer.analyze_code(self.code, self.language)
            self.analysis_progress.emit("Analysis complete")
            self.analysis_complete.emit(report)
        except Exception as e:
            error_report = self.analyzer._create_error_report(str(e), self.language, self.code)
            self.analysis_complete.emit(error_report)


class CodeAnalyzerMainWindow(QMainWindow):
    """Main window for the formal code analysis application."""

    def __init__(self):
        super().__init__()
        self.analyzer = AdvancedComplexityAnalyzer()
        self.api = CodeAnalysisAPI()
        self.current_report = None
        self.analysis_history = []

        self.init_ui()
        self.setup_api()
        self.setup_connections()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Code Analysis Professional - Complexity & Performance Analyzer")
        self.setGeometry(100, 100, 1600, 1000)

        # Set application icon
        self.setWindowIcon(QIcon("analyzer_icon.png"))  # You can add an icon file

        # Apply professional dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1E1E;
                color: #FFFFFF;
            }
            QMenuBar {
                background-color: #2D2D30;
                color: #FFFFFF;
                border-bottom: 1px solid #3C3C3C;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 12px;
            }
            QMenuBar::item:selected {
                background-color: #0E639C;
            }
            QMenu {
                background-color: #2D2D30;
                color: #FFFFFF;
                border: 1px solid #3C3C3C;
            }
            QMenu::item:selected {
                background-color: #0E639C;
            }
            QTabWidget::pane {
                border: 1px solid #3C3C3C;
                background-color: #1E1E1E;
            }
            QTabBar::tab {
                background-color: #2D2D30;
                color: #FFFFFF;
                border: 1px solid #3C3C3C;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #0E639C;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3C3C3C;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
                color: #FFFFFF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #0E639C;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1177BB;
            }
            QPushButton:pressed {
                background-color: #005A9E;
            }
            QTextEdit, QListWidget, QTableWidget {
                background-color: #1E1E1E;
                color: #D4D4D4;
                border: 1px solid #3C3C3C;
                selection-background-color: #264F78;
            }
            QHeaderView::section {
                background-color: #2D2D30;
                color: #FFFFFF;
                border: 1px solid #3C3C3C;
                padding: 8px;
            }
        """)

        # Create menu bar
        self.create_menu_bar()

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Create toolbar
        toolbar_layout = self.create_toolbar()
        main_layout.addLayout(toolbar_layout)

        # Create main content area
        content_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - Code input and settings
        left_panel = self.create_left_panel()
        content_splitter.addWidget(left_panel)

        # Right panel - Analysis results
        right_panel = self.create_right_panel()
        content_splitter.addWidget(right_panel)

        # Set splitter sizes
        content_splitter.setSizes([600, 1000])

        main_layout.addWidget(content_splitter)

        # Create status bar
        self.create_status_bar()

    def create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('File')

        # Open file action
        open_action = QAction('Open File...', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        # Save report action
        save_report_action = QAction('Save Report...', self)
        save_report_action.setShortcut('Ctrl+S')
        save_report_action.triggered.connect(self.save_report)
        file_menu.addAction(save_report_action)

        file_menu.addSeparator()

        # Export actions
        export_menu = file_menu.addMenu('Export')

        export_json_action = QAction('Export as JSON...', self)
        export_json_action.triggered.connect(lambda: self.export_report('json'))
        export_menu.addAction(export_json_action)

        export_html_action = QAction('Export as HTML...', self)
        export_html_action.triggered.connect(lambda: self.export_report('html'))
        export_menu.addAction(export_html_action)

        file_menu.addSeparator()

        # Exit action
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Analysis menu
        analysis_menu = menubar.addMenu('Analysis')

        # Analyze action
        analyze_action = QAction('Analyze Code', self)
        analyze_action.setShortcut('F5')
        analyze_action.triggered.connect(self.analyze_code)
        analysis_menu.addAction(analyze_action)

        # Clear action
        clear_action = QAction('Clear Results', self)
        clear_action.triggered.connect(self.clear_results)
        analysis_menu.addAction(clear_action)

        analysis_menu.addSeparator()

        # Settings action
        settings_action = QAction('Settings...', self)
        settings_action.triggered.connect(self.show_settings)
        analysis_menu.addAction(settings_action)

        # API menu
        api_menu = menubar.addMenu('API')

        # Start API server action
        start_api_action = QAction('Start API Server', self)
        start_api_action.triggered.connect(self.start_api_server)
        api_menu.addAction(start_api_action)

        # Stop API server action
        stop_api_action = QAction('Stop API Server', self)
        stop_api_action.triggered.connect(self.stop_api_server)
        api_menu.addAction(stop_api_action)

        # Help menu
        help_menu = menubar.addMenu('Help')

        # About action
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        # User guide action
        guide_action = QAction('User Guide', self)
        guide_action.triggered.connect(self.show_user_guide)
        help_menu.addAction(guide_action)

    def create_toolbar(self):
        """Create the main toolbar."""
        toolbar_layout = QHBoxLayout()

        # Language selection
        language_label = QLabel("Language:")
        language_label.setStyleSheet("color: #FFFFFF; font-weight: bold;")
        toolbar_layout.addWidget(language_label)

        self.language_combo = QComboBox()
        self.language_combo.addItems(['Python', 'JavaScript', 'Java', 'C++', 'C#'])
        self.language_combo.setCurrentText('Python')
        self.language_combo.setStyleSheet("""
            QComboBox {
                background-color: #2D2D30;
                color: #FFFFFF;
                border: 1px solid #3C3C3C;
                padding: 5px;
                min-width: 100px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #FFFFFF;
            }
        """)
        toolbar_layout.addWidget(self.language_combo)

        toolbar_layout.addSpacing(20)

        # Analysis controls
        self.analyze_button = QPushButton("🔍 Analyze Code")
        self.analyze_button.clicked.connect(self.analyze_code)
        toolbar_layout.addWidget(self.analyze_button)

        self.clear_button = QPushButton("🗑️ Clear")
        self.clear_button.clicked.connect(self.clear_results)
        toolbar_layout.addWidget(self.clear_button)

        toolbar_layout.addSpacing(20)

        # API status
        api_status_label = QLabel("API Status:")
        api_status_label.setStyleSheet("color: #FFFFFF; font-weight: bold;")
        toolbar_layout.addWidget(api_status_label)

        self.api_status_indicator = QLabel("●")
        self.api_status_indicator.setStyleSheet("color: #F44336; font-size: 16px;")  # Red by default
        self.api_status_indicator.setToolTip("API Server Status")
        toolbar_layout.addWidget(self.api_status_indicator)

        toolbar_layout.addStretch()

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3C3C3C;
                border-radius: 3px;
                text-align: center;
                color: #FFFFFF;
            }
            QProgressBar::chunk {
                background-color: #0E639C;
                border-radius: 2px;
            }
        """)
        toolbar_layout.addWidget(self.progress_bar)

        return toolbar_layout

    def create_left_panel(self):
        """Create the left panel with code input and settings."""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Code input section
        code_group = QGroupBox("Code Input")
        code_layout = QVBoxLayout(code_group)

        # Code editor
        self.code_editor = QTextEdit()
        self.code_editor.setFont(QFont("Consolas", 11))
        self.code_editor.setPlaceholderText("Paste your code here or open a file...")
        code_layout.addWidget(self.code_editor)

        # File controls
        file_controls = QHBoxLayout()

        open_file_btn = QPushButton("📁 Open File")
        open_file_btn.clicked.connect(self.open_file)
        file_controls.addWidget(open_file_btn)

        paste_btn = QPushButton("📋 Paste")
        paste_btn.clicked.connect(self.paste_code)
        file_controls.addWidget(paste_btn)

        clear_code_btn = QPushButton("🗑️ Clear")
        clear_code_btn.clicked.connect(self.clear_code)
        file_controls.addWidget(clear_code_btn)

        file_controls.addStretch()
        code_layout.addLayout(file_controls)

        left_layout.addWidget(code_group)

        # Analysis settings section
        settings_group = QGroupBox("Analysis Settings")
        settings_layout = QGridLayout(settings_group)

        # Analysis depth
        settings_layout.addWidget(QLabel("Analysis Depth:"), 0, 0)
        self.depth_spin = QSpinBox()
        self.depth_spin.setRange(1, 10)
        self.depth_spin.setValue(5)
        self.depth_spin.setToolTip("Maximum recursion depth for analysis")
        settings_layout.addWidget(self.depth_spin, 0, 1)

        # Include space analysis
        self.space_analysis_check = QCheckBox("Include Space Complexity")
        self.space_analysis_check.setChecked(True)
        settings_layout.addWidget(self.space_analysis_check, 1, 0, 1, 2)

        # Include suggestions
        self.suggestions_check = QCheckBox("Generate Optimization Suggestions")
        self.suggestions_check.setChecked(True)
        settings_layout.addWidget(self.suggestions_check, 2, 0, 1, 2)

        # Confidence threshold
        settings_layout.addWidget(QLabel("Confidence Threshold:"), 3, 0)
        self.confidence_spin = QSpinBox()
        self.confidence_spin.setRange(50, 100)
        self.confidence_spin.setValue(80)
        self.confidence_spin.setSuffix("%")
        self.confidence_spin.setToolTip("Minimum confidence level for results")
        settings_layout.addWidget(self.confidence_spin, 3, 1)

        left_layout.addWidget(settings_group)

        # Analysis history section
        history_group = QGroupBox("Analysis History")
        history_layout = QVBoxLayout(history_group)

        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(150)
        self.history_list.itemClicked.connect(self.load_from_history)
        history_layout.addWidget(self.history_list)

        history_controls = QHBoxLayout()

        clear_history_btn = QPushButton("Clear History")
        clear_history_btn.clicked.connect(self.clear_history)
        history_controls.addWidget(clear_history_btn)

        export_history_btn = QPushButton("Export History")
        export_history_btn.clicked.connect(self.export_history)
        history_controls.addWidget(export_history_btn)

        history_controls.addStretch()
        history_layout.addLayout(history_controls)

        left_layout.addWidget(history_group)

        left_layout.addStretch()

        return left_widget

    def create_right_panel(self):
        """Create the right panel with analysis results."""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Results tab widget
        self.results_tabs = QTabWidget()

        # Overview tab
        overview_tab = self.create_overview_tab()
        self.results_tabs.addTab(overview_tab, "📊 Overview")

        # Detailed analysis tab
        detailed_tab = self.create_detailed_tab()
        self.results_tabs.addTab(detailed_tab, "🔍 Detailed Analysis")

        # Suggestions tab
        suggestions_tab = self.create_suggestions_tab()
        self.results_tabs.addTab(suggestions_tab, "💡 Suggestions")

        # Report tab
        report_tab = self.create_report_tab()
        self.results_tabs.addTab(report_tab, "📄 Report")

        right_layout.addWidget(self.results_tabs)

        return right_widget

    def create_overview_tab(self):
        """Create the overview tab."""
        overview_widget = QWidget()
        overview_layout = QVBoxLayout(overview_widget)

        # Overall complexity display
        complexity_frame = QFrame()
        complexity_frame.setStyleSheet("""
            QFrame {
                background-color: #2D2D30;
                border: 2px solid #3C3C3C;
                border-radius: 8px;
                padding: 20px;
                margin: 10px;
            }
        """)
        complexity_layout = QGridLayout(complexity_frame)

        # Time complexity
        time_label = QLabel("Time Complexity:")
        time_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        complexity_layout.addWidget(time_label, 0, 0)

        self.time_complexity_value = QLabel("Not analyzed")
        self.time_complexity_value.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        complexity_layout.addWidget(self.time_complexity_value, 0, 1)

        # Space complexity
        space_label = QLabel("Space Complexity:")
        space_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        complexity_layout.addWidget(space_label, 1, 0)

        self.space_complexity_value = QLabel("Not analyzed")
        self.space_complexity_value.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        complexity_layout.addWidget(self.space_complexity_value, 1, 1)

        # Quality score
        quality_label = QLabel("Quality Score:")
        quality_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        complexity_layout.addWidget(quality_label, 2, 0)

        self.quality_score_value = QLabel("Not analyzed")
        self.quality_score_value.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        complexity_layout.addWidget(self.quality_score_value, 2, 1)

        # Performance rating
        rating_label = QLabel("Performance Rating:")
        rating_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        complexity_layout.addWidget(rating_label, 3, 0)

        self.performance_rating_value = QLabel("Not analyzed")
        self.performance_rating_value.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        complexity_layout.addWidget(self.performance_rating_value, 3, 1)

        overview_layout.addWidget(complexity_frame)

        # Analysis summary
        summary_group = QGroupBox("Analysis Summary")
        summary_layout = QVBoxLayout(summary_group)

        self.summary_text = QTextBrowser()
        self.summary_text.setMaximumHeight(200)
        summary_layout.addWidget(self.summary_text)

        overview_layout.addWidget(summary_group)

        overview_layout.addStretch()

        return overview_widget

    def create_detailed_tab(self):
        """Create the detailed analysis tab."""
        detailed_widget = QWidget()
        detailed_layout = QVBoxLayout(detailed_widget)

        # Detailed results table
        self.detailed_table = QTableWidget()
        self.detailed_table.setColumnCount(6)
        self.detailed_table.setHorizontalHeaderLabels([
            "Line", "Type", "Time Complexity", "Space Complexity", "Confidence", "Description"
        ])

        # Set column widths
        header = self.detailed_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Line
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Type
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Time
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Space
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Confidence
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)  # Description

        detailed_layout.addWidget(self.detailed_table)

        return detailed_widget

    def create_suggestions_tab(self):
        """Create the suggestions tab."""
        suggestions_widget = QWidget()
        suggestions_layout = QVBoxLayout(suggestions_widget)

        # Warnings section
        warnings_group = QGroupBox("⚠️ Warnings")
        warnings_layout = QVBoxLayout(warnings_group)

        self.warnings_list = QListWidget()
        self.warnings_list.setMaximumHeight(150)
        warnings_layout.addWidget(self.warnings_list)

        suggestions_layout.addWidget(warnings_group)

        # Optimization suggestions section
        optimization_group = QGroupBox("💡 Optimization Suggestions")
        optimization_layout = QVBoxLayout(optimization_group)

        self.suggestions_list = QListWidget()
        optimization_layout.addWidget(self.suggestions_list)

        suggestions_layout.addWidget(optimization_group)

        return suggestions_widget

    def create_report_tab(self):
        """Create the report tab."""
        report_widget = QWidget()
        report_layout = QVBoxLayout(report_widget)

        # Report display
        self.report_text = QTextBrowser()
        self.report_text.setFont(QFont("Consolas", 10))
        report_layout.addWidget(self.report_text)

        # Report controls
        report_controls = QHBoxLayout()

        copy_report_btn = QPushButton("📋 Copy Report")
        copy_report_btn.clicked.connect(self.copy_report)
        report_controls.addWidget(copy_report_btn)

        save_report_btn = QPushButton("💾 Save Report")
        save_report_btn.clicked.connect(self.save_report)
        report_controls.addWidget(save_report_btn)

        export_html_btn = QPushButton("🌐 Export HTML")
        export_html_btn.clicked.connect(lambda: self.export_report('html'))
        report_controls.addWidget(export_html_btn)

        report_controls.addStretch()
        report_layout.addLayout(report_controls)

        return report_widget

    def create_status_bar(self):
        """Create the status bar."""
        status_bar = self.statusBar()

        # Main status message
        self.status_message = QLabel("Ready")
        status_bar.addWidget(self.status_message)

        # Analysis time
        self.analysis_time_label = QLabel()
        status_bar.addPermanentWidget(self.analysis_time_label)

        # API port info
        self.api_port_label = QLabel("API: Not running")
        status_bar.addPermanentWidget(self.api_port_label)

    def setup_api(self):
        """Setup the API server."""
        self.api.analysis_received.connect(self.handle_api_analysis)

    def setup_connections(self):
        """Setup signal connections."""
        pass  # Additional connections can be added here

    def analyze_code(self):
        """Analyze the current code."""
        code = self.code_editor.toPlainText().strip()

        if not code:
            QMessageBox.warning(self, "Warning", "Please enter some code to analyze.")
            return

        language = self.language_combo.currentText().lower()

        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.status_message.setText("Analyzing code...")

        # Start analysis in background thread
        self.analysis_worker = AnalysisWorker(self.analyzer, code, language)
        self.analysis_worker.analysis_complete.connect(self.handle_analysis_complete)
        self.analysis_worker.analysis_progress.connect(self.status_message.setText)
        self.analysis_worker.start()

    def handle_analysis_complete(self, report):
        """Handle completed analysis."""
        self.progress_bar.setVisible(False)
        self.current_report = report

        # Add to history
        self.add_to_history(report)

        # Display results
        self.display_analysis_results(report)

        self.status_message.setText("Analysis complete")

        # Show analysis time
        analysis_time = datetime.now().strftime("%H:%M:%S")
        self.analysis_time_label.setText(f"Last analysis: {analysis_time}")

    def display_analysis_results(self, report):
        """Display analysis results in the UI."""
        # Update overview tab
        self.update_overview_tab(report)

        # Update detailed tab
        self.update_detailed_tab(report)

        # Update suggestions tab
        self.update_suggestions_tab(report)

        # Update report tab
        self.update_report_tab(report)

    def update_overview_tab(self, report):
        """Update the overview tab with results."""
        # Set complexity values
        self.time_complexity_value.setText(report.overall_time_complexity)
        self.space_complexity_value.setText(report.overall_space_complexity)

        # Color code based on complexity
        time_color = self.get_complexity_color(report.overall_time_complexity)
        space_color = self.get_complexity_color(report.overall_space_complexity)

        self.time_complexity_value.setStyleSheet(f"color: {time_color};")
        self.space_complexity_value.setStyleSheet(f"color: {space_color};")

        # Set quality score
        self.quality_score_value.setText(f"{report.quality_score:.1f}/100")
        quality_color = self.get_quality_color(report.quality_score)
        self.quality_score_value.setStyleSheet(f"color: {quality_color};")

        # Set performance rating
        self.performance_rating_value.setText(report.performance_rating)
        rating_color = self.get_rating_color(report.performance_rating)
        self.performance_rating_value.setStyleSheet(f"color: {rating_color};")

        # Update summary
        summary_html = self.generate_summary_html(report)
        self.summary_text.setHtml(summary_html)

    def update_detailed_tab(self, report):
        """Update the detailed analysis tab."""
        self.detailed_table.setRowCount(len(report.detailed_results))

        for row, result in enumerate(report.detailed_results):
            # Line number
            line_item = QTableWidgetItem(str(result.line_number))
            self.detailed_table.setItem(row, 0, line_item)

            # Type
            type_item = QTableWidgetItem(result.analysis_type)
            self.detailed_table.setItem(row, 1, type_item)

            # Time complexity
            time_item = QTableWidgetItem(result.time_complexity)
            time_color = self.get_complexity_color(result.time_complexity)
            time_item.setForeground(QColor(time_color))
            self.detailed_table.setItem(row, 2, time_item)

            # Space complexity
            space_item = QTableWidgetItem(result.space_complexity)
            space_color = self.get_complexity_color(result.space_complexity)
            space_item.setForeground(QColor(space_color))
            self.detailed_table.setItem(row, 3, space_item)

            # Confidence
            confidence_item = QTableWidgetItem(f"{result.confidence:.1%}")
            self.detailed_table.setItem(row, 4, confidence_item)

            # Description
            desc_item = QTableWidgetItem(result.description)
            self.detailed_table.setItem(row, 5, desc_item)

    def update_suggestions_tab(self, report):
        """Update the suggestions tab."""
        # Clear previous items
        self.warnings_list.clear()
        self.suggestions_list.clear()

        # Add warnings
        for warning in report.warnings:
            item = QListWidgetItem(f"⚠️ {warning}")
            item.setForeground(QColor("#FF9800"))
            self.warnings_list.addItem(item)

        # Add suggestions
        for suggestion in report.suggestions:
            item = QListWidgetItem(f"💡 {suggestion}")
            item.setForeground(QColor("#4CAF50"))
            self.suggestions_list.addItem(item)

        # Add suggestions from detailed results
        for result in report.detailed_results:
            for suggestion in result.suggestions:
                item = QListWidgetItem(f"🎯 Line {result.line_number}: {suggestion}")
                item.setForeground(QColor("#2196F3"))
                self.suggestions_list.addItem(item)

    def update_report_tab(self, report):
        """Update the report tab."""
        report_html = self.generate_report_html(report)
        self.report_text.setHtml(report_html)

    def get_complexity_color(self, complexity):
        """Get color for complexity display."""
        color_map = {
            'O(1)': '#4CAF50',      # Green
            'O(log n)': '#8BC34A',  # Light Green
            'O(n)': '#FFC107',      # Amber
            'O(n log n)': '#FF9800', # Orange
            'O(n²)': '#FF5722',     # Deep Orange
            'O(n³)': '#F44336',     # Red
            'O(2ⁿ)': '#9C27B0',     # Purple
            'O(n!)': '#E91E63'      # Pink
        }
        return color_map.get(complexity, '#FFFFFF')

    def get_quality_color(self, score):
        """Get color for quality score."""
        if score >= 80:
            return '#4CAF50'  # Green
        elif score >= 60:
            return '#FFC107'  # Amber
        elif score >= 40:
            return '#FF9800'  # Orange
        else:
            return '#F44336'  # Red

    def get_rating_color(self, rating):
        """Get color for performance rating."""
        rating_colors = {
            'Excellent': '#4CAF50',
            'Good': '#8BC34A',
            'Fair': '#FFC107',
            'Poor': '#FF9800',
            'Very Poor': '#F44336'
        }
        return rating_colors.get(rating, '#FFFFFF')

    def generate_summary_html(self, report):
        """Generate HTML summary of the analysis."""
        html = f"""
        <html>
        <body style="color: #FFFFFF; background-color: #1E1E1E;">
        <h3>Analysis Summary</h3>
        <p><strong>Language:</strong> {report.language}</p>
        <p><strong>Code Length:</strong> {report.code_length} lines</p>
        <p><strong>Analysis Time:</strong> {report.timestamp}</p>

        <h4>Key Findings:</h4>
        <ul>
        """

        if report.detailed_results:
            html += f"<li>Found {len(report.detailed_results)} complexity patterns</li>"

        if report.warnings:
            html += f"<li>{len(report.warnings)} performance warnings identified</li>"

        if report.suggestions:
            html += f"<li>{len(report.suggestions)} optimization suggestions available</li>"

        html += """
        </ul>
        </body>
        </html>
        """

        return html

    def generate_report_html(self, report):
        """Generate full HTML report."""
        html = f"""
        <html>
        <head>
        <style>
        body {{ color: #FFFFFF; background-color: #1E1E1E; font-family: Arial, sans-serif; }}
        h1, h2, h3 {{ color: #569CD6; }}
        .complexity {{ font-weight: bold; font-size: 14px; }}
        .warning {{ color: #FF9800; }}
        .suggestion {{ color: #4CAF50; }}
        .detail {{ margin: 10px 0; padding: 10px; background-color: #2D2D30; border-radius: 5px; }}
        </style>
        </head>
        <body>

        <h1>Code Analysis Report</h1>

        <h2>Overview</h2>
        <div class="detail">
        <p><strong>Language:</strong> {report.language}</p>
        <p><strong>Analysis Time:</strong> {report.timestamp}</p>
        <p><strong>Code Length:</strong> {report.code_length} lines</p>
        <p><strong>Time Complexity:</strong> <span class="complexity">{report.overall_time_complexity}</span></p>
        <p><strong>Space Complexity:</strong> <span class="complexity">{report.overall_space_complexity}</span></p>
        <p><strong>Quality Score:</strong> {report.quality_score:.1f}/100</p>
        <p><strong>Performance Rating:</strong> {report.performance_rating}</p>
        </div>

        <h2>Detailed Analysis</h2>
        """

        for result in report.detailed_results:
            html += f"""
            <div class="detail">
            <p><strong>Line {result.line_number} [{result.analysis_type}]:</strong></p>
            <p>Time: {result.time_complexity}, Space: {result.space_complexity}</p>
            <p>Confidence: {result.confidence:.1%}</p>
            <p>{result.description}</p>
            </div>
            """

        if report.warnings:
            html += "<h2>Warnings</h2>"
            for warning in report.warnings:
                html += f'<p class="warning">⚠️ {warning}</p>'

        if report.suggestions:
            html += "<h2>Suggestions</h2>"
            for suggestion in report.suggestions:
                html += f'<p class="suggestion">💡 {suggestion}</p>'

        html += """
        </body>
        </html>
        """

        return html

    # Utility methods for file operations and API
    def open_file(self):
        """Open a code file for analysis."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Code File", "",
            "Python Files (*.py);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    code = file.read()
                    self.code_editor.setPlainText(code)
                    self.status_message.setText(f"Loaded: {Path(file_path).name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file: {str(e)}")

    def paste_code(self):
        """Paste code from clipboard."""
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text:
            self.code_editor.setPlainText(text)
            self.status_message.setText("Code pasted from clipboard")

    def clear_code(self):
        """Clear the code editor."""
        self.code_editor.clear()
        self.status_message.setText("Code editor cleared")

    def clear_results(self):
        """Clear all analysis results."""
        # Reset overview values
        self.time_complexity_value.setText("Not analyzed")
        self.space_complexity_value.setText("Not analyzed")
        self.quality_score_value.setText("Not analyzed")
        self.performance_rating_value.setText("Not analyzed")

        # Reset colors
        self.time_complexity_value.setStyleSheet("")
        self.space_complexity_value.setStyleSheet("")
        self.quality_score_value.setStyleSheet("")
        self.performance_rating_value.setStyleSheet("")

        # Clear other tabs
        self.summary_text.clear()
        self.detailed_table.setRowCount(0)
        self.warnings_list.clear()
        self.suggestions_list.clear()
        self.report_text.clear()

        self.current_report = None
        self.status_message.setText("Results cleared")

    def add_to_history(self, report):
        """Add analysis report to history."""
        self.analysis_history.append(report)

        # Add to history list
        timestamp = datetime.fromisoformat(report.timestamp).strftime("%H:%M:%S")
        item_text = f"{timestamp} - {report.language} ({report.overall_time_complexity})"

        item = QListWidgetItem(item_text)
        item.setData(Qt.ItemDataRole.UserRole, report)
        self.history_list.insertItem(0, item)  # Add to top

        # Limit history size
        if self.history_list.count() > 50:
            self.history_list.takeItem(50)
            self.analysis_history = self.analysis_history[-50:]

    def load_from_history(self, item):
        """Load analysis from history."""
        report = item.data(Qt.ItemDataRole.UserRole)
        if report:
            self.current_report = report
            self.display_analysis_results(report)
            self.status_message.setText("Loaded from history")

    def clear_history(self):
        """Clear analysis history."""
        self.history_list.clear()
        self.analysis_history.clear()
        self.status_message.setText("History cleared")

    def export_history(self):
        """Export analysis history."""
        if not self.analysis_history:
            QMessageBox.information(self, "Info", "No history to export.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export History", "analysis_history.json",
            "JSON Files (*.json);;All Files (*)"
        )

        if file_path:
            try:
                history_data = [asdict(report) for report in self.analysis_history]
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(history_data, file, indent=2)
                self.status_message.setText(f"History exported to {Path(file_path).name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export history: {str(e)}")

    def save_report(self):
        """Save current analysis report."""
        if not self.current_report:
            QMessageBox.information(self, "Info", "No analysis report to save.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Report", "analysis_report.json",
            "JSON Files (*.json);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(asdict(self.current_report), file, indent=2)
                self.status_message.setText(f"Report saved to {Path(file_path).name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save report: {str(e)}")

    def export_report(self, format_type):
        """Export report in specified format."""
        if not self.current_report:
            QMessageBox.information(self, "Info", "No analysis report to export.")
            return

        if format_type == 'json':
            self.save_report()
        elif format_type == 'html':
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export HTML Report", "analysis_report.html",
                "HTML Files (*.html);;All Files (*)"
            )

            if file_path:
                try:
                    html_content = self.generate_report_html(self.current_report)
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(html_content)
                    self.status_message.setText(f"HTML report exported to {Path(file_path).name}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to export HTML: {str(e)}")

    def copy_report(self):
        """Copy report to clipboard."""
        if not self.current_report:
            QMessageBox.information(self, "Info", "No analysis report to copy.")
            return

        # Generate text version of report
        report_text = f"""
Code Analysis Report
==================

Language: {self.current_report.language}
Analysis Time: {self.current_report.timestamp}
Code Length: {self.current_report.code_length} lines

Overall Complexity:
- Time: {self.current_report.overall_time_complexity}
- Space: {self.current_report.overall_space_complexity}

Quality Score: {self.current_report.quality_score:.1f}/100
Performance Rating: {self.current_report.performance_rating}

Detailed Analysis:
"""

        for result in self.current_report.detailed_results:
            report_text += f"""
Line {result.line_number} [{result.analysis_type}]:
  Time: {result.time_complexity}, Space: {result.space_complexity}
  Confidence: {result.confidence:.1%}
  Description: {result.description}
"""

        if self.current_report.warnings:
            report_text += "\nWarnings:\n"
            for warning in self.current_report.warnings:
                report_text += f"- {warning}\n"

        if self.current_report.suggestions:
            report_text += "\nSuggestions:\n"
            for suggestion in self.current_report.suggestions:
                report_text += f"- {suggestion}\n"

        clipboard = QApplication.clipboard()
        clipboard.setText(report_text)
        self.status_message.setText("Report copied to clipboard")

    def start_api_server(self):
        """Start the API server."""
        if self.api.start_server():
            self.api_status_indicator.setStyleSheet("color: #4CAF50; font-size: 16px;")  # Green
            self.api_port_label.setText(f"API: Running on port {self.api.port}")
            self.status_message.setText("API server started")
        else:
            QMessageBox.critical(self, "Error", "Failed to start API server")

    def stop_api_server(self):
        """Stop the API server."""
        self.api.stop_server()
        self.api_status_indicator.setStyleSheet("color: #F44336; font-size: 16px;")  # Red
        self.api_port_label.setText("API: Not running")
        self.status_message.setText("API server stopped")

    def handle_api_analysis(self, code, language, source_app):
        """Handle analysis request from API."""
        self.code_editor.setPlainText(code)
        self.language_combo.setCurrentText(language.title())
        self.status_message.setText(f"Analysis request from {source_app}")
        self.analyze_code()

    def show_settings(self):
        """Show settings dialog."""
        QMessageBox.information(self, "Settings", "Settings dialog not yet implemented.")

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(self, "About",
            "Code Analysis Professional v1.0\n\n"
            "A comprehensive tool for analyzing code complexity and performance.\n\n"
            "Features:\n"
            "• Time and space complexity analysis\n"
            "• Multi-language support\n"
            "• API interface for IDE integration\n"
            "• Professional reporting\n"
            "• Export capabilities")

    def show_user_guide(self):
        """Show user guide."""
        QMessageBox.information(self, "User Guide",
            "Code Analysis Professional - User Guide\n\n"
            "1. Enter or paste code in the left panel\n"
            "2. Select the programming language\n"
            "3. Click 'Analyze Code' or press F5\n"
            "4. View results in the tabs on the right\n"
            "5. Export reports as needed\n\n"
            "API Integration:\n"
            "• Start API server from API menu\n"
            "• IDEs can send code to port 12345\n"
            "• JSON format: {\"code\": \"...\", \"language\": \"python\"}")


def main():
    """Main function to run the Code Analysis Professional application."""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("Code Analysis Professional")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("IDE Suite")
    app.setOrganizationDomain("ide-suite.com")

    # Create and show main window
    window = CodeAnalyzerMainWindow()
    window.show()

    # Load sample code for demonstration
    sample_code = """# Sample code for analysis
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):          # O(n) - outer loop
        for j in range(0, n - i - 1):  # O(n) - inner loop = O(n²)
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)  # O(2^n) - exponential

# Example usage
data = [64, 34, 25, 12, 22, 11, 90]
sorted_data = bubble_sort(data)
print(f"Sorted: {sorted_data}")
print(f"Fibonacci(10): {fibonacci(10)}")"""

    window.code_editor.setPlainText(sample_code)
    window.status_message.setText("Ready - Sample code loaded for demonstration")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()