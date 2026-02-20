# SCAT - Source Code Analysis Tool (Formerly PyCAT)

**SCAT (Source Code Analysis Tool)** is a comprehensive, modular application for analyzing code complexity and performance across multiple programming languages. Now featuring a modern GUI interface!

## 🎯 **What is SCAT?**

SCAT provides professional-grade analysis for multiple programming languages, including:
- **Multi-Language Support** - Python, Ruby, Lua, BASIC, Pseudocode, PLAIN, STEPS (extensible architecture)
- **Time Complexity Analysis** - O(1), O(n), O(n²), O(2ⁿ), etc.
- **Space Complexity Analysis** - Memory usage and auxiliary space patterns
- **Quality Scoring** - 0-100 rating system with performance ratings
- **Modular Architecture** - Easy to add new languages via plugin system
- **Professional Reporting** - Detailed analysis with export capabilities
- **IDE Integration** - API interface for integration with development environments

## 📁 **Files in this Directory**

### **SCAT Architecture (v2.0)**
- **`scat_gui.py`** - GUI application launcher
- **`main.py`** - Main application entry point (CLI/GUI)
- **`launcher.py`** - IDE integration launcher and CLI tool
- **`core/`** - Core analysis engine and models
- **`languages/`** - Language-specific analyzers (Python, Ruby, Lua, BASIC, Pseudocode, PLAIN, STEPS)
- **`ui/`** - GUI components and interface
- **`tests/`** - Comprehensive testing suite

### **Legacy Files (v1.0)**
- **`code_analyzer_app.py`** - Legacy monolithic application (deprecated)
- **`launch_analyzer.py`** - Legacy launcher (deprecated)
- **`test_formal_analyzer.py`** - Legacy testing suite

### **Documentation**
- **`README.md`** - This file (main overview)
- **`SCAT_GUI_SUMMARY.md`** - Complete GUI implementation guide
- **`SCAT_TROUBLESHOOTING.md`** - Troubleshooting and help guide
- **`REFACTORING_SUMMARY.md`** - Modular architecture overview
- **`SYNTAX_HIGHLIGHTING.md`** - Modular syntax higlighting system overview
- **`DOCUMENTATION_STATUS.md`** - Documentation overview
- **`IDE_INTEGRATION_GUIDE.md`** - Detailed IDE Integration instructions
- **`API_INTEGRATION_GUIDE.md`** - Detailed API Integration instructions
- **`CODE_ANALYZER_PROFESSIONAL_README.md`** - Legacy documentation
- **`CODE_ANALYZER_FINAL_SUMMARY.md`** - Legacy project summary

## 🚀 **Quick Start**

### **Prerequisites**
```bash
# For CLI mode: No external dependencies required
# Python 3.8+ with standard library

# For GUI mode: Install PyQt6
pip install PyQt6
```

### **Run SCAT (Source Code Analysis Tool)**
```bash
# Launch GUI application (recommended)
python scat_gui.py
# OR
python main.py

# Launch interactive CLI
python main.py --cli

# Analyze a specific file
python main.py --file script.py
```

### **Test the Analysis Engine**
```bash
python tests/test_modular_analyzer.py
```

### **Use the Launcher for IDE Integration**
```bash
python launcher.py --help
```

## 🔌 **IDE Integration**

The Code Analysis Tool can be integrated into any IDE in your suite:

### **Launch Code Analysis Tool from IDE**
```python
from launcher import ide_launch_analyzer
ide_launch_analyzer('cli')  # or 'gui'
```

### **Analyze Code Directly (Recommended)**
```python
from launcher import ide_analyze_code
result = ide_analyze_code(code, "python", "MyIDE")
# Returns analysis results as dictionary
```

### **Analyze Files**
```python
from launcher import ide_analyze_file
success = ide_analyze_file("script.py", "python", "MyIDE")
```

### **Get Supported Languages**
```python
from launcher import ide_get_supported_languages
languages = ide_get_supported_languages()
```

## 📊 **Features**

### **Analysis Capabilities**
- ✅ **Multi-Language Support** - Python, Ruby, Lua (easily extensible)
- ✅ **Loop Detection** - Single, nested, and deeply nested loops
- ✅ **Recursion Analysis** - Exponential complexity detection
- ✅ **Built-in Functions** - Language-specific function complexity analysis
- ✅ **Data Structures** - Arrays, hashes, tables, and collections
- ✅ **Quality Scoring** - Professional code quality assessment
- ✅ **Modular Architecture** - Plugin-like system for adding languages

### **Interface Options**
- ✅ **Graphical User Interface** - Modern PyQt6-based GUI with syntax highlighting
- ✅ **Command-Line Interface** - Interactive CLI for terminal users
- ✅ **Direct Integration** - Programmatic API for IDE integration
- ✅ **File Analysis** - Batch processing of code files
- ✅ **Export Capabilities** - JSON and structured output formats

### **API Integration**
- ✅ **TCP Server** - Runs on port 12345 for IDE communication
- ✅ **JSON Protocol** - Standardized request/response format
- ✅ **Status Monitoring** - Check if analyzer is running
- ✅ **Error Handling** - Robust error management

## 🎓 **Educational Value**

### **For Students**
- Real-time complexity feedback as they write code
- Visual complexity indicators for immediate understanding
- Quality scoring to track improvement over time
- Professional tool preparation for industry

### **For Educators**
- Teaching aid for algorithm analysis courses
- Assignment grading with automated complexity assessment
- Progress tracking through analysis history
- Professional reporting for academic use

## 🔧 **Technical Details**

### **Language Support**
- **Python**: Full AST-based analysis with comprehensive pattern detection
- **Ruby**: Pattern-based analysis for loops, methods, blocks, and data structures
- **Lua**: Pattern-based analysis for functions, tables, and control structures
- **BASIC**: Pattern-based analysis for line numbers, control flow, and data operations
- **Pseudocode**: Structured analysis for algorithm design and logic flow
- **PLAIN**: Pattern-based analysis for tasks, loops, recursion, and data structures
- **STEPS**: Pattern-based analysis for steps, risers, loops, and error handling
- **Extensible**: Easy to add new languages through the plugin architecture

### **Analysis Engine**
- **Modular Architecture** - Separate analyzers for each language
- **AST-based parsing** for Python using `ast` module
- **Pattern recognition** for Ruby and Lua using regex
- **Confidence scoring** for result reliability
- **Plugin system** for adding new language analyzers

### **System Requirements**
- Python 3.8+
- No external dependencies for core functionality (CLI mode)
- PyQt6 (required for GUI mode: `pip install PyQt6`)

## 🎉 **Ready for Use**

The Code Analysis Tool is production-ready and provides:
- ✅ **Multi-language support** (Python, Ruby, Lua)
- ✅ **Modular architecture** for easy extension
- ✅ **Professional-grade analysis**
- ✅ **Easy IDE integration**
- ✅ **Comprehensive documentation**
- ✅ **Thorough testing**
- ✅ **No external dependencies** for core functionality

**Start using SCAT today to enhance your development workflow with professional complexity analysis across multiple programming languages!**

## 🔄 **Migration from PyCAT v1.0**

If you're upgrading from the original PyCAT:
- **New GUI**: Launch with `python scat_gui.py` for the modern interface
- **Legacy Support**: Old `code_analyzer_app.py` still works but is deprecated
- **New Entry Point**: Use `main.py` for CLI or GUI modes
- **Updated Integration**: Use `launcher.py` instead of `launch_analyzer.py`
- **Multi-language**: Now supports Ruby and Lua in addition to Python

## 🎨 **GUI Features**

SCAT now includes a comprehensive GUI with:
- **Modern Interface**: Dark theme with professional styling
- **Syntax Highlighting**: Color-coded Python syntax highlighting
- **Real-time Analysis**: Non-blocking analysis with progress indication
- **Interactive Results**: Click results to jump to specific code lines
- **File Operations**: Open, save, and manage code files
- **Multi-language Support**: Switch between Python, Ruby, and Lua

## 🔧 **Troubleshooting**

### **GUI Won't Start?**
```bash
# Install PyQt6
pip install PyQt6

# Use CLI mode as fallback
python main.py --cli

# Check detailed troubleshooting guide
# See SCAT_TROUBLESHOOTING.md
```

### **Common Issues:**
- **PyQt6 not installed**: `pip install PyQt6`
- **No display environment**: Use `python main.py --cli`
- **Import errors**: Check Python version (3.8+ required)

**For complete troubleshooting guide, see `SCAT_TROUBLESHOOTING.md`**

---

*SCAT is part of the IDE Suite project and designed for educational and professional multi-language development environments.*
