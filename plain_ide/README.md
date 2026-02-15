# PLAIN IDE

A modern, feature-rich IDE for the PLAIN programming language with integrated debugging support.

## Features

- **Syntax Highlighting** - Color-coded PLAIN syntax
- **Integrated Debugger** - Step through code, set breakpoints, inspect variables
- **Code Editor** - Modern editing with line numbers, auto-indent, code folding
- **Project Management** - Organize and manage PLAIN projects
- **Python ↔ PLAIN Converter** - Convert files between Python and PLAIN via Tools → Convert File (`Ctrl+Shift+C`)
- **Bookmarks** - Mark and navigate important code locations
- **Find/Replace** - Powerful search and replace
- **Themes** - Multiple color themes
- **Session Persistence** - Remembers your open files and settings

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Install Dependencies

```bash
# Navigate to the IDE directory
cd plain_ide

# Install required packages
pip install -r requirements.txt
```

### Run the IDE

```bash
# From the plain_ide directory
python main.py

# Or from the parent directory
python -m plain_ide.main
```

### First-Time Setup

1. **Configure Interpreter Path:**
   - Settings → Preferences → Interpreter
   - Set path to the PLAIN interpreter executable
   - Default locations:
     - Linux/macOS: `./plain` or `/usr/local/bin/plain`
     - Windows: `plain.exe` or `C:\Program Files\PLAIN\plain.exe`

2. **Choose Theme:**
   - Settings → Preferences → Appearance
   - Select from available themes

## Usage

### Creating a New File

1. File → New (Ctrl/Cmd+N)
2. Write your PLAIN code
3. File → Save (Ctrl/Cmd+S)
4. Choose `.plain` extension

### Running Code

1. Run → Run Program (F5)
2. Or click the ▶️ Run button in toolbar

### Debugging

1. Set breakpoints by clicking in the line number gutter
2. Debug → Start Debugging (F9)
3. Use toolbar to:
   - Step Over (F10)
   - Step Into (F11)
   - Step Out (Shift+F11)
   - Continue (F5)
   - Stop (Shift+F5)

### Keyboard Shortcuts

| Action | Windows/Linux | macOS |
|--------|---------------|-------|
| New File | Ctrl+N | Cmd+N |
| Open File | Ctrl+O | Cmd+O |
| Save | Ctrl+S | Cmd+S |
| Save As | Ctrl+Shift+S | Cmd+Shift+S |
| Run | F5 | F5 |
| Debug | F9 | F9 |
| Step Over | F10 | F10 |
| Step Into | F11 | F11 |
| Find | Ctrl+F | Cmd+F |
| Replace | Ctrl+H | Cmd+H |
| Comment/Uncomment | Ctrl+/ | Cmd+/ |

## Troubleshooting

### "No module named PyQt6"

Install dependencies:
```bash
pip install -r requirements.txt
```

### "Cannot find PLAIN interpreter"

1. Check interpreter path in Settings → Preferences
2. Ensure PLAIN binary is in your PATH or specify full path
3. Test interpreter: `plain --version`

### IDE Won't Start

```bash
# Check Python version (needs 3.8+)
python --version

# Try running with verbose output
python main.py --verbose
```

### High DPI Display Issues

The IDE automatically detects high DPI displays. If you experience scaling issues:

1. Settings → Preferences → Appearance
2. Adjust font size
3. Restart IDE

## Development

### Project Structure

```
plain_ide/
├── app/                # Main application code
│   ├── main_window.py  # Main window
│   ├── editor.py       # Code editor
│   ├── debugger.py     # Debug integration
│   └── settings.py     # Settings management
├── editor/             # Editor components
├── shared/             # Shared utilities
├── main.py             # Entry point
└── requirements.txt    # Dependencies
```

### Building Standalone Executable

To create a standalone executable (no Python required):

```bash
# Install PyInstaller
pip install pyinstaller

# Linux/macOS
pyinstaller --name="PLAIN-IDE" \
            --windowed \
            --add-data="app:app" \
            --add-data="editor:editor" \
            --add-data="shared:shared" \
            main.py

# Windows
pyinstaller --name="PLAIN-IDE" ^
            --windowed ^
            --add-data="app;app" ^
            --add-data="editor;editor" ^
            --add-data="shared;shared" ^
            main.py

# Executable will be in dist/PLAIN-IDE/
```

## Support

For issues, feature requests, or questions:
- GitHub Issues: https://github.com/CFFinch62/plain-language/issues
- Email: info@fragillidaesoftware.com

## License

Proprietary - See LICENSE file in the parent directory.

Copyright (c) 2026 Fragillidae Software
