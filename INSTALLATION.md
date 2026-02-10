# PLAIN Installation Guide

Complete installation instructions for PLAIN interpreter and IDE.

## Quick Start

1. Download the appropriate package for your platform
2. Extract the archive
3. Install the interpreter
4. (Optional) Set up the IDE

---

## Interpreter Installation

### Linux

```bash
# Download and extract
tar -xzf plain-v1.0.0-beta1-linux-amd64.tar.gz
cd plain-v1.0.0-beta1-linux-amd64

# Install to system (optional)
sudo cp plain /usr/local/bin/
sudo chmod +x /usr/local/bin/plain

# Or add to PATH in current directory
export PATH="$PWD:$PATH"

# Verify installation
plain --version
```

### macOS

```bash
# Download and extract
tar -xzf plain-v1.0.0-beta1-darwin-amd64.tar.gz  # Intel
# OR
tar -xzf plain-v1.0.0-beta1-darwin-arm64.tar.gz  # Apple Silicon

cd plain-v1.0.0-beta1-darwin-*

# Install to system (optional)
sudo cp plain /usr/local/bin/
sudo chmod +x /usr/local/bin/plain

# If you get "unverified developer" warning:
sudo xattr -d com.apple.quarantine /usr/local/bin/plain

# Or add to PATH in current directory
export PATH="$PWD:$PATH"

# Verify installation
plain --version
```

### Windows

```powershell
# Extract the ZIP file
# Right-click → Extract All → Choose location

# Option 1: Add to PATH via System Properties
# 1. Right-click "This PC" → Properties
# 2. Advanced system settings → Environment Variables
# 3. Under "User variables", select "Path" → Edit
# 4. New → Browse to extracted folder
# 5. OK → OK → OK

# Option 2: Copy to existing PATH location
# Move plain.exe to C:\Windows or C:\Windows\System32

# Option 3: Use from current directory
cd path\to\extracted\folder

# Verify installation
plain.exe --version
```

---

## IDE Installation

The IDE is included in all packages. It requires Python 3.8 or higher.

### 1. Install Python (if not already installed)

**Windows:**
- Download from https://www.python.org/downloads/
- ✅ Check "Add Python to PATH" during installation

**macOS:**
```bash
# Using Homebrew
brew install python3
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip

# Fedora/RHEL
sudo dnf install python3 python3-pip
```

### 2. Install IDE Dependencies

```bash
# Navigate to the extracted package
cd plain-v1.0.0-beta1-*/

# Install dependencies
pip3 install -r plain_ide/requirements.txt

# Or if pip3 doesn't work:
python3 -m pip install -r plain_ide/requirements.txt
```

### 3. Run the IDE

```bash
# From the package directory
python3 plain_ide/main.py

# Or
python3 -m plain_ide.main
```

### 4. First-Time IDE Setup

When you first launch the IDE:

1. **Set Interpreter Path:**
   - Go to: Settings → Preferences → Interpreter
   - Click "Browse" and select the `plain` executable
   - If you installed system-wide:
     - Linux/macOS: `/usr/local/bin/plain`
     - Windows: `C:\Windows\plain.exe` or wherever you installed it
   - If using from package: select `./plain` (or `.\plain.exe` on Windows)

2. **Choose a Theme (Optional):**
   - Settings → Preferences → Appearance
   - Select your preferred color theme

3. **Test the Setup:**
   - File → New (Ctrl/Cmd+N)
   - Type: `task Main()` and press Enter, then `    display("Hello, PLAIN!")`
   - Save the file as `test.plain`
   - Click Run (F5)
   - You should see "Hello, PLAIN!" in the output panel

---

## Creating a Desktop Shortcut (Optional)

### Linux

Create `~/.local/share/applications/plain-ide.desktop`:

```desktop
[Desktop Entry]
Name=PLAIN IDE
Comment=PLAIN Programming Language IDE
Exec=/path/to/plain-v1.0.0-beta1-linux-amd64/plain_ide/main.py
Icon=accessories-text-editor
Terminal=false
Type=Application
Categories=Development;IDE;
```

### macOS

Create an Automator application:
1. Open Automator
2. New Document → Application
3. Add "Run Shell Script" action
4. Script: `cd /path/to/plain && python3 plain_ide/main.py`
5. Save as "PLAIN IDE" in Applications

### Windows

1. Right-click desktop → New → Shortcut
2. Location: `C:\Python3\python.exe "C:\path\to\plain_ide\main.py"`
3. Name: "PLAIN IDE"
4. (Optional) Right-click shortcut → Properties → Change Icon

---

## Troubleshooting

### "plain: command not found"

The interpreter is not in your PATH. Either:
- Install to `/usr/local/bin` (Linux/macOS)
- Add the directory to PATH
- Use full path: `/path/to/plain yourfile.plain`

### "No module named PyQt6"

IDE dependencies not installed:
```bash
pip3 install PyQt6 PyQt6-QScintilla
```

### "Cannot find PLAIN interpreter" (IDE)

1. Check Settings → Preferences → Interpreter path
2. Verify the interpreter works in terminal: `plain --version`
3. Use absolute path in IDE settings

### Permission Denied (Linux/macOS)

Make the interpreter executable:
```bash
chmod +x plain
```

### macOS Security Warning

```bash
sudo xattr -d com.apple.quarantine /path/to/plain
```

### Windows SmartScreen Warning

1. Click "More info"
2. Click "Run anyway"
3. (This happens because the executable is not code-signed)

---

## Uninstallation

### Interpreter

**Linux/macOS:**
```bash
sudo rm /usr/local/bin/plain
```

**Windows:**
- Remove from PATH environment variable
- Delete the folder

### IDE

```bash
# Just delete the package folder
rm -rf plain-v1.0.0-beta1-*
```

If you installed Python dependencies system-wide:
```bash
pip3 uninstall PyQt6 PyQt6-QScintilla
```

---

## Getting Started

After installation:

1. **Read the Tutorial:**
   - Open `docs/TUTORIAL.md` in the package
   - Follow along with the examples

2. **Try Example Programs:**
   - The `examples/` folder contains sample programs
   - Run them: `plain examples/fibonacci.plain`

3. **Read the Language Reference:**
   - `docs/LANGUAGE-REFERENCE.md` - Complete language documentation
   - `docs/STDLIB.md` - Standard library reference

4. **Watch for Updates:**
   - Check https://github.com/CFFinch62/plain-language for new releases

---

## Next Steps

- 📖 Read the [Tutorial](docs/TUTORIAL.md)
- 📚 Review the [Language Reference](docs/LANGUAGE-REFERENCE.md)
- 💡 Explore [Example Programs](examples/)
- 🐛 Report bugs via GitHub Issues
- 📧 Contact: info@fragillidaesoftware.com

---

## System Requirements

### Interpreter
- **Linux:** glibc 2.31+ (Ubuntu 20.04+, similar for other distros)
- **macOS:** 10.15 Catalina or later
- **Windows:** Windows 10 or later
- **Architecture:** x64 or ARM64

### IDE
- **Python:** 3.8 or higher
- **RAM:** 512 MB minimum, 1 GB recommended
- **Disk:** 100 MB for IDE + dependencies
- **Display:** 1024x768 minimum, 1920x1080 recommended

---

Copyright © 2026 Fragillidae Software. All rights reserved.
