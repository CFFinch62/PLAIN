"""
Main window for SCAT (Source Code Analysis Tool).

This module provides the main application window that integrates all
UI components and coordinates the analysis workflow.
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QSplitter, QPushButton, QFileDialog,
                            QMessageBox, QStatusBar, QProgressBar, QLabel,
                            QApplication, QGroupBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QAction, QFont, QIcon

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.analyzer import CodeAnalyzer
from core.models import AnalysisConfig
from ui.themes import SCATTheme
from ui.components.code_editor import CodeEditor
from ui.components.language_selector import LanguageSelector
from ui.components.analysis_display import AnalysisDisplayWidget
from ui.components.results_table import ResultsTable
from ui.components.complexity_badge import AnalysisSummaryWidget


class AnalysisWorker(QThread):
    """Worker thread for performing code analysis."""

    analysisComplete = pyqtSignal(object)  # Emits analysis report
    analysisError = pyqtSignal(str)        # Emits error message

    def __init__(self, analyzer, code, language):
        super().__init__()
        self.analyzer = analyzer
        self.code = code
        self.language = language

    def run(self):
        """Run the analysis in a separate thread."""
        try:
            report = self.analyzer.analyze_code(self.code, self.language)
            self.analysisComplete.emit(report)
        except Exception as e:
            self.analysisError.emit(str(e))


class SCATMainWindow(QMainWindow):
    """Main window for SCAT application."""

    def __init__(self):
        super().__init__()
        self.analyzer = None
        self.current_file = None
        self.analysis_worker = None

        self.setup_analyzer()
        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()
        self.setup_connections()

        # Apply theme
        self.setStyleSheet(SCATTheme.get_stylesheet())

        # Set window properties
        self.setWindowTitle("SCAT - Source Code Analysis Tool")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Set application icon
        icon_path = str(Path(__file__).parent.parent / "scat.png")
        self.setWindowIcon(QIcon(icon_path))

        # Show welcome message
        self.show_welcome_message()

    def setup_analyzer(self):
        """Setup the code analyzer."""
        try:
            config = AnalysisConfig()
            self.analyzer = CodeAnalyzer(config)
            print("✅ Code analyzer initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize analyzer: {e}")
            self.analyzer = None

    def setup_ui(self):
        """Setup the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)

        # Create main splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel (code editor and controls)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(8)  # Reduce spacing between elements

        # Language selector (more compact)
        self.language_selector = LanguageSelector()
        if self.analyzer:
            self.language_selector.update_from_analyzer(self.analyzer)

        # Code editor group (expanded to fill available space)
        editor_group = QGroupBox("Code Editor")
        editor_layout = QVBoxLayout(editor_group)
        editor_layout.setSpacing(8)

        # Editor controls
        controls_layout = QHBoxLayout()

        self.analyze_button = QPushButton("🔍 Analyze Code")
        self.analyze_button.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.analyze_button.setMinimumHeight(35)

        self.clear_button = QPushButton("Clear")
        self.clear_button.setProperty("class", "secondary")

        controls_layout.addWidget(self.analyze_button)
        controls_layout.addWidget(self.clear_button)
        controls_layout.addStretch()

        # Code editor (expanded to fill space)
        self.code_editor = CodeEditor()

        editor_layout.addLayout(controls_layout)
        editor_layout.addWidget(self.code_editor)

        # Add widgets with proper stretch factors
        left_layout.addWidget(self.language_selector, 0)  # Fixed size
        left_layout.addWidget(editor_group, 1)  # Expand to fill available space

        # Right panel (results)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(8)  # Reduce spacing between elements

        # Analysis summary (compact, single row)
        self.summary_widget = AnalysisSummaryWidget()

        # Results tabs (expanded to fill more space)
        results_splitter = QSplitter(Qt.Orientation.Vertical)

        # Detailed results table (larger area)
        self.results_table = ResultsTable()

        # Analysis display (warnings, suggestions, etc.)
        self.analysis_display = AnalysisDisplayWidget()

        results_splitter.addWidget(self.results_table)
        results_splitter.addWidget(self.analysis_display)
        # Give much more space to results table since analysis display is now compact
        results_splitter.setSizes([600, 150])

        # Add widgets with proper stretch factors
        right_layout.addWidget(self.summary_widget, 0)  # Fixed size (compact)
        right_layout.addWidget(results_splitter, 1)  # Expand to fill available space

        # Add panels to main splitter
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([600, 800])  # Give more space to results

        main_layout.addWidget(main_splitter)

    def setup_menu(self):
        """Setup the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        # New file
        new_action = QAction("&New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        # Open file
        open_action = QAction("&Open...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        # Save file
        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        # Save as
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        # Exit
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")

        # Clear editor
        clear_action = QAction("&Clear Editor", self)
        clear_action.triggered.connect(self.clear_editor)
        edit_menu.addAction(clear_action)

        # Insert sample code
        sample_menu = edit_menu.addMenu("Insert &Sample Code")

        python_sample = QAction("Python Sample", self)
        python_sample.triggered.connect(lambda: self.insert_sample_code('python'))
        sample_menu.addAction(python_sample)

        ruby_sample = QAction("Ruby Sample", self)
        ruby_sample.triggered.connect(lambda: self.insert_sample_code('ruby'))
        sample_menu.addAction(ruby_sample)

        lua_sample = QAction("Lua Sample", self)
        lua_sample.triggered.connect(lambda: self.insert_sample_code('lua'))
        sample_menu.addAction(lua_sample)

        # Analysis menu
        analysis_menu = menubar.addMenu("&Analysis")

        # Analyze code
        analyze_action = QAction("&Analyze Code", self)
        analyze_action.setShortcut("F5")
        analyze_action.triggered.connect(self.analyze_code)
        analysis_menu.addAction(analyze_action)

        # Clear results
        clear_results_action = QAction("&Clear Results", self)
        clear_results_action.triggered.connect(self.clear_results)
        analysis_menu.addAction(clear_results_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        # About
        about_action = QAction("&About SCAT", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_status_bar(self):
        """Setup the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Status label
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

        # Language indicator
        self.language_indicator = QLabel("Python")
        self.status_bar.addPermanentWidget(self.language_indicator)

    def setup_connections(self):
        """Setup signal connections."""
        # Language selector
        self.language_selector.languageChanged.connect(self.on_language_changed)
        self.language_selector.sampleCodeRequested.connect(self.insert_sample_code)

        # Code editor
        self.code_editor.textChanged.connect(self.on_code_changed)

        # Buttons
        self.analyze_button.clicked.connect(self.analyze_code)
        self.clear_button.clicked.connect(self.clear_editor)

        # Results table
        self.results_table.itemDoubleClicked.connect(self.goto_line)

        # Analysis display
        self.analysis_display.lineRequested.connect(self.goto_line)

    def show_welcome_message(self):
        """Show welcome message in the code editor."""
        welcome_text = '''# Welcome to SCAT - Source Code Analysis Tool!
#
# SCAT analyzes code complexity across multiple programming languages:
# • Python (AST-based analysis)
# • Ruby (pattern-based analysis)
# • Lua (pattern-based analysis)
# • BASIC (pattern-based analysis)
# • Pseudocode (structured analysis)
#
# To get started:
# 1. Select a programming language from the dropdown
# 2. Write or paste your code in this editor
# 3. Click "Analyze Code" or press F5
# 4. View results in the panels on the right
#
# You can also:
# • Open existing files (Ctrl+O)
# • Insert sample code (Edit menu)
# • Export analysis results
#
# Happy coding! 🚀

def example_function():
    """This is a sample function to analyze."""
    numbers = [3, 1, 4, 1, 5, 9, 2, 6, 5]

    # O(n²) bubble sort - not efficient for large datasets
    for i in range(len(numbers)):
        for j in range(len(numbers) - 1):
            if numbers[j] > numbers[j + 1]:
                numbers[j], numbers[j + 1] = numbers[j + 1], numbers[j]

    return numbers

# Try analyzing this code to see SCAT in action!'''

        self.code_editor.setPlainText(welcome_text)
        self.status_label.setText("Welcome to SCAT! Load code and click Analyze to get started.")

    def insert_sample_code(self, language):
        """Insert sample code for the specified language."""
        self.language_selector.set_selected_language(language)
        self.code_editor.insert_sample_code(language)
        self.status_label.setText(f"Inserted {language.title()} sample code")

    def on_language_changed(self, language):
        """Handle language selection change."""
        self.code_editor.set_language(language)
        self.language_indicator.setText(language.title())
        self.status_label.setText(f"Language changed to {language.title()}")

    def on_code_changed(self):
        """Handle code editor changes."""
        # Enable analyze button if there's code
        has_code = bool(self.code_editor.toPlainText().strip())
        self.analyze_button.setEnabled(has_code and self.analyzer is not None)

    def analyze_code(self):
        """Analyze the code in the editor."""
        if not self.analyzer:
            QMessageBox.warning(self, "Error", "Code analyzer not available")
            return

        code = self.code_editor.toPlainText().strip()
        if not code:
            QMessageBox.information(self, "No Code", "Please enter some code to analyze")
            return

        language = self.language_selector.get_selected_language()
        if not language:
            QMessageBox.warning(self, "No Language", "Please select a programming language")
            return

        # Start analysis in worker thread
        self.start_analysis(code, language)

    def start_analysis(self, code, language):
        """Start code analysis in a worker thread."""
        # Update UI for analysis
        self.analyze_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.status_label.setText("Analyzing code...")

        # Create and start worker thread
        self.analysis_worker = AnalysisWorker(self.analyzer, code, language)
        self.analysis_worker.analysisComplete.connect(self.on_analysis_complete)
        self.analysis_worker.analysisError.connect(self.on_analysis_error)
        self.analysis_worker.start()

    def on_analysis_complete(self, report):
        """Handle completed analysis."""
        # Update UI
        self.analyze_button.setEnabled(True)
        self.progress_bar.setVisible(False)

        # Display results
        self.summary_widget.update_from_report(report)
        self.results_table.set_results(report.detailed_results)
        self.analysis_display.update_from_report(report)

        # Update status
        complexity = report.overall_time_complexity
        quality = report.quality_score
        self.status_label.setText(
            f"Analysis complete: {complexity} complexity, {quality:.1f}/100 quality score"
        )

        # Clean up worker
        self.analysis_worker = None

    def on_analysis_error(self, error_message):
        """Handle analysis error."""
        # Update UI
        self.analyze_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Analysis failed")

        # Show error message
        QMessageBox.critical(self, "Analysis Error", f"Failed to analyze code:\n\n{error_message}")

        # Clean up worker
        self.analysis_worker = None

    def clear_results(self):
        """Clear all analysis results."""
        self.summary_widget.clear()
        self.results_table.clear()
        self.analysis_display.clear_results()
        self.status_label.setText("Results cleared")

    def clear_editor(self):
        """Clear the code editor."""
        self.code_editor.clear()
        self.clear_results()
        self.status_label.setText("Editor cleared")

    def goto_line(self, line_number):
        """Go to a specific line in the code editor."""
        self.code_editor.goto_line(line_number)
        self.code_editor.setFocus()
        self.status_label.setText(f"Jumped to line {line_number}")

    def new_file(self):
        """Create a new file."""
        if self.confirm_unsaved_changes():
            self.clear_editor()
            self.current_file = None
            self.setWindowTitle("SCAT - Source Code Analysis Tool")
            self.status_label.setText("New file created")

    def open_file(self):
        """Open a code file."""
        if not self.confirm_unsaved_changes():
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Code File",
            "",
            "All Supported (*.py *.rb *.lua);;Python Files (*.py *.pyw);;Ruby Files (*.rb *.rbw);;Lua Files (*.lua);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                self.code_editor.setPlainText(content)
                self.current_file = file_path

                # Auto-detect language
                ext = Path(file_path).suffix.lower()
                if ext in ['.py', '.pyw']:
                    self.language_selector.set_selected_language('python')
                elif ext in ['.rb', '.rbw']:
                    self.language_selector.set_selected_language('ruby')
                elif ext == '.lua':
                    self.language_selector.set_selected_language('lua')

                self.setWindowTitle(f"SCAT - {Path(file_path).name}")
                self.status_label.setText(f"Opened: {file_path}")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file:\n\n{str(e)}")

    def save_file(self):
        """Save the current file."""
        if self.current_file:
            self.save_to_file(self.current_file)
        else:
            self.save_file_as()

    def save_file_as(self):
        """Save the file with a new name."""
        language = self.language_selector.get_selected_language()

        # Set default extension based on language
        if language == 'python':
            default_filter = "Python Files (*.py)"
            default_ext = ".py"
        elif language == 'ruby':
            default_filter = "Ruby Files (*.rb)"
            default_ext = ".rb"
        elif language == 'lua':
            default_filter = "Lua Files (*.lua)"
            default_ext = ".lua"
        elif language == 'basic':
            default_filter = "BASIC Files (*.bas)"
            default_ext = ".bas"
        elif language == 'pseudocode':
            default_filter = "Pseudocode Files (*.pseudo)"
            default_ext = ".pseudo"
        else:
            default_filter = "Text Files (*.txt)"
            default_ext = ".txt"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Code File",
            f"untitled{default_ext}",
            f"{default_filter};;All Files (*)"
        )

        if file_path:
            self.save_to_file(file_path)
            self.current_file = file_path
            self.setWindowTitle(f"SCAT - {Path(file_path).name}")

    def save_to_file(self, file_path):
        """Save content to the specified file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.code_editor.toPlainText())
            self.status_label.setText(f"Saved: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file:\n\n{str(e)}")

    def confirm_unsaved_changes(self):
        """Confirm if user wants to discard unsaved changes."""
        # For now, just return True. In a full implementation,
        # you'd check if the file has been modified and ask the user.
        return True

    def show_about(self):
        """Show about dialog."""
        about_text = """
        <h2>SCAT - Source Code Analysis Tool</h2>
        <p><b>Version:</b> 2.0.0</p>
        <p><b>Description:</b> Multi-language code complexity analyzer</p>

        <h3>Supported Languages:</h3>
        <ul>
        <li>🐍 Python (AST-based analysis)</li>
        <li>💎 Ruby (pattern-based analysis)</li>
        <li>🌙 Lua (pattern-based analysis)</li>
        <li>📟 BASIC (pattern-based analysis)</li>
        <li>📝 Pseudocode (structured analysis)</li>
        </ul>

        <h3>Features:</h3>
        <ul>
        <li>Time and space complexity analysis</li>
        <li>Quality scoring and performance ratings</li>
        <li>Detailed suggestions for optimization</li>
        <li>Modular architecture for easy extension</li>
        </ul>

        <p><b>Part of the IDE Suite project</b></p>
        <p>Designed for educational and professional development environments.</p>
        """

        # Create about dialog with icon
        about_dialog = QMessageBox(self)
        about_dialog.setWindowTitle("About SCAT")
        about_dialog.setText(about_text)
        about_dialog.setTextFormat(Qt.TextFormat.RichText)
        
        # Set the icon for the about dialog
        icon_path = str(Path(__file__).parent.parent / "scat.png")
        about_dialog.setIconPixmap(QIcon(icon_path).pixmap(64, 64))
        
        about_dialog.exec()

    def closeEvent(self, event):
        """Handle application close event."""
        if self.confirm_unsaved_changes():
            # Clean up worker thread if running
            if self.analysis_worker and self.analysis_worker.isRunning():
                self.analysis_worker.terminate()
                self.analysis_worker.wait()
            event.accept()
        else:
            event.ignore()


def main():
    """Main function to run the SCAT GUI application."""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("SCAT")
    app.setApplicationDisplayName("Source Code Analysis Tool")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("IDE Suite")

    # Create and show main window
    window = SCATMainWindow()
    window.show()

    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
