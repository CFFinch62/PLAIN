# SCAT Troubleshooting Guide

## 🚀 **Quick Launch Instructions**

### **Method 1: GUI Application (Recommended)**
```bash
python scat_gui.py
```

### **Method 2: Main Launcher**
```bash
python main.py          # GUI by default
python main.py --gui    # Explicit GUI
```

### **Method 3: CLI Mode (Always Works)**
```bash
python main.py --cli
```

---

## ❌ **Common Issues and Solutions**

### **Issue 1: "PyQt6 not found" or Import Errors**

**Error Messages:**
- `ModuleNotFoundError: No module named 'PyQt6'`
- `❌ PyQt6 is required for the GUI interface`

**Solutions:**
```bash
# Install PyQt6
pip install PyQt6

# Alternative methods
conda install pyqt
pip install -r requirements.txt

# Verify installation
python -c "import PyQt6; print('PyQt6 OK')"
```

### **Issue 2: "'CodeEditor' object has no attribute 'blockCountChanged'"**

**Status: FIXED ✅**
**This was a PyQt6 compatibility issue that has been resolved.**

**If you still see this error:**
1. Make sure you have the latest version of the files
2. The CodeEditor now has fallback compatibility for different PyQt versions
3. Try restarting your Python session

### **Issue 3: "'QWidget' object has no attribute 'insert_sample_code'"**

**Status: FIXED ✅**
**This was a signal connection issue that has been resolved.**

**The fix:**
- Added `sampleCodeRequested` signal to LanguageSelector
- Properly connected signal to main window
- Sample code button now works correctly

### **Issue 4: "No display detected" or GUI won't start**

**Error Messages:**
- `⚠️ No display detected. GUI requires a display environment.`
- GUI window doesn't appear

**Solutions:**
```bash
# Use CLI mode instead
python main.py --cli

# For remote/headless systems
export DISPLAY=:0  # If X11 forwarding is available

# For WSL users
# Install an X server like VcXsrv or use WSL2 with GUI support
```

### **Issue 5: "Failed to launch GUI" with other errors**

**General troubleshooting steps:**
1. **Check Python version**: Requires Python 3.8+
   ```bash
   python --version
   ```

2. **Verify file structure**: Make sure all files are present
   ```bash
   ls -la ui/
   ls -la core/
   ls -la languages/
   ```

3. **Test core functionality**:
   ```bash
   python -c "from core.analyzer import CodeAnalyzer; print('Core OK')"
   ```

4. **Test GUI components**:
   ```bash
   python -c "from ui.themes import SCATTheme; print('GUI OK')"
   ```

---

## 🔧 **Fallback Options**

### **Option 1: CLI Mode**
If GUI doesn't work, you can always use the CLI:
```bash
python main.py --cli
```

**CLI Features:**
- Interactive analysis
- File analysis
- All core functionality
- No GUI dependencies

### **Option 2: Direct Analysis**
For programmatic use:
```bash
python launcher.py --code "def test(): pass" --direct
python launcher.py --file script.py
```

### **Option 3: Legacy Version**
The original PyCAT is still available:
```bash
python code_analyzer_app.py  # If PyQt6 is installed
```

---

## 🐛 **Debugging Steps**

### **Step 1: Test Dependencies**
```bash
# Test Python
python --version

# Test PyQt6
python -c "import PyQt6; print('PyQt6:', PyQt6.QtCore.PYQT_VERSION_STR)"

# Test core modules
python -c "from core.analyzer import CodeAnalyzer; print('Core modules OK')"
```

### **Step 2: Test GUI Components**
```bash
# Test theme
python -c "from ui.themes import SCATTheme; print('Theme OK')"

# Test components
python -c "from ui.components.code_editor import CodeEditor; print('CodeEditor OK')"
```

### **Step 3: Test Analysis Engine**
```bash
# Test analysis
python -c "
from core.analyzer import CodeAnalyzer
from core.models import AnalysisConfig
analyzer = CodeAnalyzer(AnalysisConfig())
report = analyzer.analyze_code('def test(): pass', 'python')
print('Analysis OK:', report.overall_time_complexity)
"
```

### **Step 4: Verbose Error Information**
```bash
# Run with Python's verbose mode
python -v scat_gui.py

# Or with traceback
python -c "
import traceback
try:
    from ui.main_window import main
    main()
except Exception as e:
    traceback.print_exc()
"
```

---

## 🖥️ **Platform-Specific Issues**

### **Windows**
- Make sure you're using Command Prompt or PowerShell
- PyQt6 should work out of the box
- If using Anaconda, try: `conda install pyqt`

### **macOS**
- PyQt6 should work with pip installation
- If issues with display, try running from Terminal.app
- For M1 Macs, make sure you have compatible PyQt6

### **Linux**
- Install system dependencies if needed:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install python3-pyqt6

  # Or use pip
  pip install PyQt6
  ```
- Make sure you're in a desktop environment (not SSH without X11)
- For headless servers, use CLI mode

### **WSL (Windows Subsystem for Linux)**
- Install an X server (VcXsrv, Xming)
- Or use WSL2 with GUI support
- Set DISPLAY environment variable
- Alternative: Use CLI mode

---

## 📞 **Getting Help**

### **If GUI Still Doesn't Work:**
1. **Use CLI Mode**: `python main.py --cli` - Full functionality without GUI
2. **Check Error Messages**: Look for specific error details
3. **Verify Environment**: Make sure you're in a desktop environment
4. **Test Components**: Use the debugging steps above

### **Reporting Issues:**
When reporting issues, please include:
1. Operating system and version
2. Python version (`python --version`)
3. PyQt6 version (if installed)
4. Complete error message
5. Output of: `python -c "import PyQt6; print('OK')"`

### **Alternative Usage:**
Remember that SCAT works perfectly in CLI mode:
```bash
# Interactive CLI
python main.py --cli

# Direct file analysis
python main.py --file your_script.py

# IDE integration
python launcher.py --code "your code here" --direct
```

---

## ✅ **Success Indicators**

**GUI Working Correctly:**
- Window opens with dark theme
- Code editor has syntax highlighting
- Language selector shows Python 🐍, Ruby 💎, Lua 🌙
- Analysis button is clickable
- Results display properly

**CLI Working Correctly:**
- Interactive prompt appears
- Commands respond properly
- Analysis produces results
- File operations work

**Core Working Correctly:**
- Analysis engine loads
- Multiple languages supported
- Results include complexity information
- Suggestions are generated

---

**Remember: Even if GUI doesn't work, SCAT's powerful analysis engine is fully available through CLI mode!**
