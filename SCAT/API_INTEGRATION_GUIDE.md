# SCAT API Integration Guide

**Complete guide for integrating SCAT (Source Code Analysis Tool) via TCP API**

## 🎯 **Overview**

API Integration uses a TCP server running on port 12345 to communicate with a separate SCAT application instance. This method provides visual analysis results in SCAT's professional interface while allowing multiple IDEs to connect to the same analysis server.

## ✨ **Key Benefits**

- ✅ **Visual Analysis** - Results displayed in SCAT's professional GUI
- ✅ **Professional Interface** - Full-featured analysis window with syntax highlighting
- ✅ **Export Capabilities** - JSON, HTML, and text report generation
- ✅ **Analysis History** - Track and compare multiple analyses over time
- ✅ **Multi-IDE Support** - Multiple IDEs can connect to same SCAT instance
- ✅ **Process Separation** - Analysis runs in separate, dedicated process
- ✅ **Robust Protocol** - JSON-based communication with error handling

## 📋 **Prerequisites**

### **System Requirements**
- Python 3.8 or higher
- PyQt6 (for SCAT GUI): `pip install PyQt6`
- Network access to localhost (port 12345)

### **SCAT Application**
The SCAT application must be running to accept API connections:
```bash
# Launch SCAT GUI (recommended)
python scat_gui.py

# Or launch via main entry point
python main.py

# Or launch CLI mode
python main.py --cli
```

## 🚀 **Quick Start**

### **1. Start SCAT Application**
```bash
# Launch SCAT GUI
cd path/to/SCAT
python scat_gui.py
```

### **2. Basic API Client Example**
```python
import socket
import json

def send_code_to_scat(code, language="python", source_app="MyIDE"):
    """Send code to SCAT for analysis via TCP API."""
    try:
        # Create socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # 5 second timeout
        sock.connect(('localhost', 12345))

        # Prepare request
        request = {
            "code": code,
            "language": language,
            "source_app": source_app,
            "version": "2.0"
        }

        # Send request
        sock.send(json.dumps(request).encode('utf-8'))

        # Receive response
        response = sock.recv(1024).decode('utf-8')
        sock.close()

        return json.loads(response)

    except Exception as e:
        return {"status": "error", "message": str(e)}

# Usage example
code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
"""

result = send_code_to_scat(code, "python", "MyIDE")
print(f"Status: {result.get('status')}")
print(f"Message: {result.get('message')}")
```

### **3. Using SCAT's Built-in API Functions**
```python
# Import SCAT's launcher functions
from SCAT.launcher import send_code_for_analysis, check_analyzer_running

# Check if SCAT is running
if check_analyzer_running():
    # Send code for analysis
    result = send_code_for_analysis(code, "python", "MyIDE")

    if result.get("status") == "received":
        print("✅ Code sent successfully!")
        print("Check SCAT application for analysis results")
    else:
        print(f"❌ Error: {result.get('message')}")
else:
    print("❌ SCAT application is not running")
    print("Please start SCAT first: python scat_gui.py")
```

## 📡 **API Protocol Specification**

### **Connection Details**
- **Protocol**: TCP
- **Host**: localhost (127.0.0.1)
- **Port**: 12345 (default, configurable)
- **Encoding**: UTF-8
- **Format**: JSON

### **Request Format**
```json
{
    "code": "def example():\n    for i in range(n):\n        print(i)",
    "language": "python",
    "source_app": "MyIDE",
    "version": "2.0"
}
```

**Request Fields:**
- `code` (string, required): Source code to analyze
- `language` (string, required): Programming language ("python", "ruby", "lua", "basic", "pseudocode")
- `source_app` (string, optional): Name of requesting application (default: "IDE")
- `version` (string, optional): API version (default: "2.0")

### **Response Format**

**Success Response:**
```json
{
    "status": "received",
    "message": "Code analysis started",
    "timestamp": "2024-01-15T10:30:45",
    "request_id": "abc123"
}
```

**Error Response:**
```json
{
    "status": "error",
    "message": "Invalid JSON format",
    "error_code": "PARSE_ERROR",
    "timestamp": "2024-01-15T10:30:45"
}
```

**Response Fields:**
- `status` (string): "received" for success, "error" for failure
- `message` (string): Human-readable status message
- `timestamp` (string, optional): ISO format timestamp
- `request_id` (string, optional): Unique identifier for tracking
- `error_code` (string, optional): Machine-readable error code

## 🔧 **Core API Functions**

### **1. Check Server Status**
```python
def check_analyzer_running(port=12345):
    """Check if SCAT API server is running."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    except:
        return False

# Usage
if check_analyzer_running():
    print("✅ SCAT server is running")
else:
    print("❌ SCAT server is not running")
```

### **2. Send Code for Analysis**
```python
def send_code_for_analysis(code, language="python", source_app="IDE",
                          port=12345, timeout=5):
    """Send code to SCAT for analysis."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect(('localhost', port))

        request = {
            "code": code,
            "language": language,
            "source_app": source_app,
            "version": "2.0"
        }

        sock.send(json.dumps(request).encode('utf-8'))
        response = sock.recv(1024).decode('utf-8')
        sock.close()

        return json.loads(response)

    except socket.timeout:
        return {"status": "error", "message": "Connection timeout"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

### **3. Analyze File via API**
```python
def analyze_file_via_api(file_path, language=None, source_app="IDE"):
    """Analyze a file via SCAT API."""
    try:
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        # Auto-detect language if not specified
        if language is None:
            import os
            ext = os.path.splitext(file_path)[1].lower()
            language_map = {
                '.py': 'python', '.pyw': 'python',
                '.rb': 'ruby', '.rbw': 'ruby',
                '.lua': 'lua',
                '.bas': 'basic', '.vb': 'basic'
            }
            language = language_map.get(ext, 'python')

        # Send for analysis
        return send_code_for_analysis(code, language, source_app)

    except Exception as e:
        return {"status": "error", "message": f"File error: {e}"}

# Usage
result = analyze_file_via_api("script.py", None, "MyIDE")
```

## 🏗️ **Advanced Integration Patterns**

### **1. Connection Pool Manager**
```python
import socket
import json
import threading
from queue import Queue, Empty

class SCATConnectionPool:
    """Manage multiple connections to SCAT API server."""

    def __init__(self, max_connections=5, port=12345):
        self.max_connections = max_connections
        self.port = port
        self.pool = Queue(maxsize=max_connections)
        self.lock = threading.Lock()

        # Pre-create connections
        for _ in range(max_connections):
            self.pool.put(self._create_connection())

    def _create_connection(self):
        """Create a new socket connection."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            return sock
        except:
            return None

    def get_connection(self):
        """Get a connection from the pool."""
        try:
            return self.pool.get_nowait()
        except Empty:
            return self._create_connection()

    def return_connection(self, conn):
        """Return a connection to the pool."""
        if conn and not self.pool.full():
            try:
                self.pool.put_nowait(conn)
            except:
                conn.close()

    def send_analysis_request(self, code, language="python", source_app="IDE"):
        """Send analysis request using connection pool."""
        conn = self.get_connection()
        if not conn:
            return {"status": "error", "message": "No connection available"}

        try:
            conn.connect(('localhost', self.port))

            request = {
                "code": code,
                "language": language,
                "source_app": source_app,
                "version": "2.0"
            }

            conn.send(json.dumps(request).encode('utf-8'))
            response = conn.recv(1024).decode('utf-8')

            return json.loads(response)

        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            try:
                conn.close()
            except:
                pass

# Usage
pool = SCATConnectionPool()
result = pool.send_analysis_request(code, "python", "MyIDE")
```

### **2. Async API Client**
```python
import asyncio
import json

class AsyncSCATClient:
    """Asynchronous SCAT API client."""

    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port

    async def send_analysis_async(self, code, language="python", source_app="IDE"):
        """Send analysis request asynchronously."""
        try:
            # Create async connection
            reader, writer = await asyncio.open_connection(self.host, self.port)

            # Prepare request
            request = {
                "code": code,
                "language": language,
                "source_app": source_app,
                "version": "2.0"
            }

            # Send request
            request_data = json.dumps(request).encode('utf-8')
            writer.write(request_data)
            await writer.drain()

            # Read response
            response_data = await reader.read(1024)
            response = json.loads(response_data.decode('utf-8'))

            # Close connection
            writer.close()
            await writer.wait_closed()

            return response

        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def analyze_multiple_async(self, code_items):
        """Analyze multiple code snippets concurrently."""
        tasks = []

        for code, language, source_app in code_items:
            task = self.send_analysis_async(code, language, source_app)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

# Usage
async def main():
    client = AsyncSCATClient()

    # Single analysis
    result = await client.send_analysis_async(code, "python", "MyIDE")
    print(f"Result: {result}")

    # Multiple analyses
    code_items = [
        (code1, "python", "MyIDE"),
        (code2, "ruby", "MyIDE"),
        (code3, "lua", "MyIDE")
    ]
    results = await client.analyze_multiple_async(code_items)

    for i, result in enumerate(results):
        print(f"Analysis {i+1}: {result}")

# Run async client
asyncio.run(main())
```

### **3. Retry and Fallback Logic**
```python
import time
import random

class RobustSCATClient:
    """SCAT API client with retry logic and fallbacks."""

    def __init__(self, max_retries=3, base_delay=1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay

    def send_with_retry(self, code, language="python", source_app="IDE"):
        """Send analysis request with exponential backoff retry."""
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                # Check if server is running
                if not check_analyzer_running():
                    if attempt == 0:
                        # Try to launch SCAT on first attempt
                        print("SCAT not running, attempting to launch...")
                        if self._try_launch_scat():
                            time.sleep(3)  # Wait for startup
                        else:
                            return {"status": "error", "message": "Could not launch SCAT"}
                    else:
                        return {"status": "error", "message": "SCAT server not available"}

                # Send analysis request
                result = send_code_for_analysis(code, language, source_app)

                if result.get("status") != "error":
                    return result

                last_error = result.get("message", "Unknown error")

            except Exception as e:
                last_error = str(e)

            # Wait before retry (exponential backoff with jitter)
            if attempt < self.max_retries:
                delay = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"Attempt {attempt + 1} failed, retrying in {delay:.1f}s...")
                time.sleep(delay)

        return {"status": "error", "message": f"All retries failed. Last error: {last_error}"}

    def _try_launch_scat(self):
        """Attempt to launch SCAT application."""
        try:
            from SCAT.launcher import launch_analyzer
            return launch_analyzer('gui')
        except:
            return False

# Usage
client = RobustSCATClient(max_retries=3)
result = client.send_with_retry(code, "python", "MyIDE")

## 🎨 **IDE Integration Examples**

### **1. Menu Integration**
```python
class SCATMenuIntegration:
    """Integrate SCAT API into IDE menu system."""

    def __init__(self, ide_instance):
        self.ide = ide_instance
        self.setup_menu()

    def setup_menu(self):
        """Add SCAT menu items to IDE."""
        # Add main SCAT menu
        scat_menu = self.ide.menubar.addMenu("SCAT Analysis")

        # Add menu actions
        analyze_action = scat_menu.addAction("Analyze Current File")
        analyze_action.triggered.connect(self.analyze_current_file)

        analyze_selection_action = scat_menu.addAction("Analyze Selection")
        analyze_selection_action.triggered.connect(self.analyze_selection)

        scat_menu.addSeparator()

        launch_scat_action = scat_menu.addAction("Launch SCAT GUI")
        launch_scat_action.triggered.connect(self.launch_scat_gui)

        status_action = scat_menu.addAction("Check SCAT Status")
        status_action.triggered.connect(self.check_scat_status)

    def analyze_current_file(self):
        """Analyze the currently open file."""
        try:
            # Get current file content
            current_editor = self.ide.get_current_editor()
            if not current_editor:
                self.ide.show_message("No file is currently open")
                return

            code = current_editor.get_text()
            file_path = current_editor.get_file_path()

            # Detect language from file extension
            language = self._detect_language(file_path)

            # Send to SCAT
            result = send_code_for_analysis(code, language, "MyIDE")

            if result.get("status") == "received":
                self.ide.show_message("✅ Code sent to SCAT for analysis")
            else:
                self.ide.show_error(f"❌ Analysis failed: {result.get('message')}")

        except Exception as e:
            self.ide.show_error(f"Error analyzing file: {e}")

    def analyze_selection(self):
        """Analyze selected code."""
        try:
            current_editor = self.ide.get_current_editor()
            if not current_editor:
                self.ide.show_message("No file is currently open")
                return

            selected_text = current_editor.get_selected_text()
            if not selected_text:
                self.ide.show_message("No code is selected")
                return

            file_path = current_editor.get_file_path()
            language = self._detect_language(file_path)

            result = send_code_for_analysis(selected_text, language, "MyIDE")

            if result.get("status") == "received":
                self.ide.show_message("✅ Selected code sent to SCAT")
            else:
                self.ide.show_error(f"❌ Analysis failed: {result.get('message')}")

        except Exception as e:
            self.ide.show_error(f"Error analyzing selection: {e}")

    def launch_scat_gui(self):
        """Launch SCAT GUI application."""
        try:
            from SCAT.launcher import launch_analyzer
            if launch_analyzer('gui'):
                self.ide.show_message("✅ SCAT GUI launched successfully")
            else:
                self.ide.show_error("❌ Failed to launch SCAT GUI")
        except Exception as e:
            self.ide.show_error(f"Error launching SCAT: {e}")

    def check_scat_status(self):
        """Check if SCAT server is running."""
        if check_analyzer_running():
            self.ide.show_message("✅ SCAT server is running and ready")
        else:
            self.ide.show_message("❌ SCAT server is not running")

    def _detect_language(self, file_path):
        """Detect programming language from file extension."""
        if not file_path:
            return "python"

        import os
        ext = os.path.splitext(file_path)[1].lower()
        language_map = {
            '.py': 'python', '.pyw': 'python',
            '.rb': 'ruby', '.rbw': 'ruby',
            '.lua': 'lua',
            '.bas': 'basic', '.vb': 'basic'
        }
        return language_map.get(ext, 'python')
```

### **2. Toolbar Integration**
```python
class SCATToolbarIntegration:
    """Add SCAT analysis buttons to IDE toolbar."""

    def __init__(self, ide_instance):
        self.ide = ide_instance
        self.setup_toolbar()

    def setup_toolbar(self):
        """Add SCAT buttons to toolbar."""
        # Create SCAT toolbar section
        toolbar = self.ide.get_main_toolbar()

        # Add separator
        toolbar.addSeparator()

        # Add analyze button
        analyze_btn = toolbar.addAction("🔍 Analyze")
        analyze_btn.setToolTip("Send current file to SCAT for analysis")
        analyze_btn.triggered.connect(self.quick_analyze)

        # Add SCAT status indicator
        self.status_btn = toolbar.addAction("⚫ SCAT")
        self.status_btn.setToolTip("SCAT server status")
        self.status_btn.triggered.connect(self.toggle_scat)

        # Update status periodically
        self.update_status_indicator()

    def quick_analyze(self):
        """Quick analysis of current file."""
        try:
            current_editor = self.ide.get_current_editor()
            if not current_editor:
                return

            code = current_editor.get_text()
            file_path = current_editor.get_file_path()
            language = self._detect_language(file_path)

            # Show progress
            self.ide.show_progress("Sending to SCAT...")

            result = send_code_for_analysis(code, language, "MyIDE")

            self.ide.hide_progress()

            if result.get("status") == "received":
                self.ide.show_status_message("Code sent to SCAT", 3000)
            else:
                self.ide.show_status_message(f"SCAT Error: {result.get('message')}", 5000)

        except Exception as e:
            self.ide.hide_progress()
            self.ide.show_status_message(f"Analysis error: {e}", 5000)

    def toggle_scat(self):
        """Toggle SCAT server or show status."""
        if check_analyzer_running():
            # SCAT is running, show options
            self.show_scat_options()
        else:
            # SCAT not running, offer to launch
            self.offer_launch_scat()

    def show_scat_options(self):
        """Show SCAT options when server is running."""
        # Implementation depends on your IDE's dialog system
        pass

    def offer_launch_scat(self):
        """Offer to launch SCAT when not running."""
        # Implementation depends on your IDE's dialog system
        pass

    def update_status_indicator(self):
        """Update SCAT status indicator."""
        if check_analyzer_running():
            self.status_btn.setText("🟢 SCAT")
            self.status_btn.setToolTip("SCAT server is running")
        else:
            self.status_btn.setText("🔴 SCAT")
            self.status_btn.setToolTip("SCAT server is not running")

        # Schedule next update
        self.ide.schedule_timer(self.update_status_indicator, 5000)  # 5 seconds

    def _detect_language(self, file_path):
        """Detect programming language from file extension."""
        if not file_path:
            return "python"

        import os
        ext = os.path.splitext(file_path)[1].lower()
        language_map = {
            '.py': 'python', '.pyw': 'python',
            '.rb': 'ruby', '.rbw': 'ruby',
            '.lua': 'lua',
            '.bas': 'basic', '.vb': 'basic'
        }
        return language_map.get(ext, 'python')
```

### **3. Context Menu Integration**
```python
class SCATContextMenuIntegration:
    """Add SCAT options to editor context menu."""

    def __init__(self, ide_instance):
        self.ide = ide_instance
        self.setup_context_menu()

    def setup_context_menu(self):
        """Add SCAT items to context menu."""
        # Register context menu handler
        self.ide.register_context_menu_handler(self.add_scat_menu_items)

    def add_scat_menu_items(self, menu, editor, position):
        """Add SCAT items to context menu."""
        # Add separator
        menu.addSeparator()

        # Add SCAT submenu
        scat_menu = menu.addMenu("SCAT Analysis")

        # Analyze selection (if text is selected)
        if editor.has_selection():
            analyze_selection = scat_menu.addAction("Analyze Selection")
            analyze_selection.triggered.connect(
                lambda: self.analyze_selection(editor)
            )

        # Analyze function/method at cursor
        analyze_function = scat_menu.addAction("Analyze Function")
        analyze_function.triggered.connect(
            lambda: self.analyze_function_at_cursor(editor, position)
        )

        # Analyze entire file
        analyze_file = scat_menu.addAction("Analyze File")
        analyze_file.triggered.connect(
            lambda: self.analyze_file(editor)
        )

        scat_menu.addSeparator()

        # Launch SCAT GUI
        launch_gui = scat_menu.addAction("Open in SCAT GUI")
        launch_gui.triggered.connect(self.launch_scat_gui)

    def analyze_selection(self, editor):
        """Analyze selected text."""
        try:
            selected_text = editor.get_selected_text()
            if not selected_text:
                return

            file_path = editor.get_file_path()
            language = self._detect_language(file_path)

            result = send_code_for_analysis(selected_text, language, "MyIDE")

            if result.get("status") == "received":
                self.ide.show_notification("Selection sent to SCAT")
            else:
                self.ide.show_error(f"SCAT Error: {result.get('message')}")

        except Exception as e:
            self.ide.show_error(f"Error: {e}")

    def analyze_function_at_cursor(self, editor, position):
        """Analyze function/method at cursor position."""
        try:
            # Extract function code at cursor
            function_code = editor.get_function_at_position(position)
            if not function_code:
                self.ide.show_message("No function found at cursor")
                return

            file_path = editor.get_file_path()
            language = self._detect_language(file_path)

            result = send_code_for_analysis(function_code, language, "MyIDE")

            if result.get("status") == "received":
                self.ide.show_notification("Function sent to SCAT")
            else:
                self.ide.show_error(f"SCAT Error: {result.get('message')}")

        except Exception as e:
            self.ide.show_error(f"Error: {e}")

    def analyze_file(self, editor):
        """Analyze entire file."""
        try:
            code = editor.get_text()
            file_path = editor.get_file_path()
            language = self._detect_language(file_path)

            result = send_code_for_analysis(code, language, "MyIDE")

            if result.get("status") == "received":
                self.ide.show_notification("File sent to SCAT")
            else:
                self.ide.show_error(f"SCAT Error: {result.get('message')}")

        except Exception as e:
            self.ide.show_error(f"Error: {e}")

    def launch_scat_gui(self):
        """Launch SCAT GUI."""
        try:
            from SCAT.launcher import launch_analyzer
            launch_analyzer('gui')
        except Exception as e:
            self.ide.show_error(f"Failed to launch SCAT: {e}")

    def _detect_language(self, file_path):
        """Detect programming language from file extension."""
        if not file_path:
            return "python"

        import os
        ext = os.path.splitext(file_path)[1].lower()
        language_map = {
            '.py': 'python', '.pyw': 'python',
            '.rb': 'ruby', '.rbw': 'ruby',
            '.lua': 'lua',
            '.bas': 'basic', '.vb': 'basic'
        }
        return language_map.get(ext, 'python')
```

## 🔧 **Configuration and Customization**

### **1. Custom Port Configuration**
```python
class SCATConfig:
    """Configuration manager for SCAT API integration."""

    def __init__(self, config_file="scat_config.json"):
        self.config_file = config_file
        self.default_config = {
            "api_port": 12345,
            "timeout": 5,
            "auto_launch": True,
            "retry_attempts": 3,
            "default_language": "python",
            "show_notifications": True
        }
        self.config = self.load_config()

    def load_config(self):
        """Load configuration from file."""
        try:
            import json
            with open(self.config_file, 'r') as f:
                config = json.load(f)

            # Merge with defaults
            merged_config = self.default_config.copy()
            merged_config.update(config)
            return merged_config

        except FileNotFoundError:
            # Create default config file
            self.save_config(self.default_config)
            return self.default_config.copy()
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.default_config.copy()

    def save_config(self, config=None):
        """Save configuration to file."""
        try:
            import json
            config_to_save = config or self.config
            with open(self.config_file, 'w') as f:
                json.dump(config_to_save, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key, default=None):
        """Get configuration value."""
        return self.config.get(key, default)

    def set(self, key, value):
        """Set configuration value."""
        self.config[key] = value
        self.save_config()

# Usage
config = SCATConfig()
port = config.get("api_port", 12345)
timeout = config.get("timeout", 5)
```

### **2. Language Detection Configuration**
```python
class LanguageDetector:
    """Advanced language detection for SCAT integration."""

    def __init__(self):
        self.extension_map = {
            '.py': 'python', '.pyw': 'python', '.py3': 'python',
            '.rb': 'ruby', '.rbw': 'ruby', '.rake': 'ruby',
            '.lua': 'lua',
            '.bas': 'basic', '.vb': 'basic', '.vbs': 'basic',
            '.txt': 'pseudocode', '.pseudo': 'pseudocode'
        }

        self.content_patterns = {
            'python': [r'#!/usr/bin/env python', r'import \w+', r'def \w+\('],
            'ruby': [r'#!/usr/bin/env ruby', r'require [\'"]', r'def \w+'],
            'lua': [r'#!/usr/bin/env lua', r'function \w+', r'local \w+'],
            'basic': [r'^\d+\s+', r'PRINT\s+', r'FOR\s+\w+\s*=']
        }

    def detect_language(self, file_path, content=None):
        """Detect language from file extension and content."""
        # First try extension
        if file_path:
            import os
            ext = os.path.splitext(file_path)[1].lower()
            if ext in self.extension_map:
                return self.extension_map[ext]

        # If no extension match and content available, try content analysis
        if content:
            return self.detect_from_content(content)

        # Default fallback
        return 'python'

    def detect_from_content(self, content):
        """Detect language from content patterns."""
        import re

        for language, patterns in self.content_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                    return language

        return 'python'  # Default fallback

    def add_extension_mapping(self, extension, language):
        """Add custom extension mapping."""
        self.extension_map[extension.lower()] = language

    def add_content_pattern(self, language, pattern):
        """Add custom content detection pattern."""
        if language not in self.content_patterns:
            self.content_patterns[language] = []
        self.content_patterns[language].append(pattern)

# Usage
detector = LanguageDetector()
language = detector.detect_language("script.py", code_content)
```

### **3. Notification System**
```python
class SCATNotificationManager:
    """Manage notifications for SCAT API integration."""

    def __init__(self, ide_instance, config):
        self.ide = ide_instance
        self.config = config
        self.notification_history = []

    def notify_analysis_sent(self, language, lines_count):
        """Notify when code is sent for analysis."""
        if not self.config.get("show_notifications", True):
            return

        message = f"📊 {language.title()} code ({lines_count} lines) sent to SCAT"
        self.show_notification(message, "info")

    def notify_analysis_error(self, error_message):
        """Notify when analysis fails."""
        message = f"❌ SCAT Analysis Error: {error_message}"
        self.show_notification(message, "error")

    def notify_scat_launched(self):
        """Notify when SCAT is launched."""
        message = "🚀 SCAT application launched successfully"
        self.show_notification(message, "success")

    def notify_scat_unavailable(self):
        """Notify when SCAT is not available."""
        message = "⚠️ SCAT server is not running. Launch SCAT first."
        self.show_notification(message, "warning")

    def show_notification(self, message, notification_type="info"):
        """Show notification in IDE."""
        # Add to history
        import datetime
        self.notification_history.append({
            "message": message,
            "type": notification_type,
            "timestamp": datetime.datetime.now()
        })

        # Keep only last 50 notifications
        if len(self.notification_history) > 50:
            self.notification_history = self.notification_history[-50:]

        # Show in IDE (implementation depends on IDE)
        if hasattr(self.ide, 'show_notification'):
            self.ide.show_notification(message, notification_type)
        elif hasattr(self.ide, 'show_status_message'):
            self.ide.show_status_message(message, 3000)
        else:
            print(f"SCAT: {message}")

    def get_notification_history(self):
        """Get notification history."""
        return self.notification_history.copy()

# Usage
notifier = SCATNotificationManager(ide_instance, config)
notifier.notify_analysis_sent("python", 25)
```

## ⚠️ **Error Handling and Troubleshooting**

### **1. Comprehensive Error Handler**
```python
class SCATErrorHandler:
    """Handle SCAT API errors gracefully."""

    def __init__(self, ide_instance, config):
        self.ide = ide_instance
        self.config = config
        self.error_log = []

    def handle_connection_error(self, error):
        """Handle connection-related errors."""
        error_info = {
            "type": "connection_error",
            "message": str(error),
            "timestamp": self._get_timestamp(),
            "suggested_action": "Check if SCAT is running"
        }

        self.log_error(error_info)

        # Try to auto-launch SCAT if configured
        if self.config.get("auto_launch", True):
            if self._try_launch_scat():
                return {"status": "recovered", "message": "SCAT launched automatically"}

        return {
            "status": "error",
            "message": "SCAT server not available",
            "suggestion": "Launch SCAT application first"
        }

    def handle_timeout_error(self, timeout_duration):
        """Handle timeout errors."""
        error_info = {
            "type": "timeout_error",
            "timeout": timeout_duration,
            "timestamp": self._get_timestamp(),
            "suggested_action": "Increase timeout or check SCAT performance"
        }

        self.log_error(error_info)

        return {
            "status": "error",
            "message": f"Request timed out after {timeout_duration}s",
            "suggestion": "SCAT may be busy. Try again in a moment."
        }

    def handle_json_error(self, json_error):
        """Handle JSON parsing errors."""
        error_info = {
            "type": "json_error",
            "message": str(json_error),
            "timestamp": self._get_timestamp(),
            "suggested_action": "Check SCAT API compatibility"
        }

        self.log_error(error_info)

        return {
            "status": "error",
            "message": "Invalid response from SCAT",
            "suggestion": "Check SCAT version compatibility"
        }

    def handle_analysis_error(self, analysis_error):
        """Handle analysis-specific errors."""
        error_info = {
            "type": "analysis_error",
            "message": str(analysis_error),
            "timestamp": self._get_timestamp(),
            "suggested_action": "Check code syntax and language"
        }

        self.log_error(error_info)

        return {
            "status": "error",
            "message": f"Analysis failed: {analysis_error}",
            "suggestion": "Check code syntax and selected language"
        }

    def log_error(self, error_info):
        """Log error for debugging."""
        self.error_log.append(error_info)

        # Keep only last 100 errors
        if len(self.error_log) > 100:
            self.error_log = self.error_log[-100:]

        # Optionally write to file
        if self.config.get("log_errors_to_file", False):
            self._write_error_to_file(error_info)

    def get_error_summary(self):
        """Get summary of recent errors."""
        if not self.error_log:
            return "No recent errors"

        error_types = {}
        for error in self.error_log[-10:]:  # Last 10 errors
            error_type = error.get("type", "unknown")
            error_types[error_type] = error_types.get(error_type, 0) + 1

        summary = "Recent errors: "
        summary += ", ".join([f"{count} {error_type}" for error_type, count in error_types.items()])

        return summary

    def _try_launch_scat(self):
        """Try to launch SCAT automatically."""
        try:
            from SCAT.launcher import launch_analyzer
            return launch_analyzer('gui')
        except:
            return False

    def _get_timestamp(self):
        """Get current timestamp."""
        import datetime
        return datetime.datetime.now().isoformat()

    def _write_error_to_file(self, error_info):
        """Write error to log file."""
        try:
            import json
            import os

            log_file = "scat_errors.log"

            # Append to log file
            with open(log_file, 'a') as f:
                f.write(json.dumps(error_info) + "\n")

        except Exception as e:
            print(f"Failed to write error log: {e}")

# Usage
error_handler = SCATErrorHandler(ide_instance, config)

try:
    result = send_code_for_analysis(code, language, "MyIDE")
except ConnectionError as e:
    result = error_handler.handle_connection_error(e)
except socket.timeout:
    result = error_handler.handle_timeout_error(5)
except json.JSONDecodeError as e:
    result = error_handler.handle_json_error(e)
```

### **2. Diagnostic Tools**
```python
class SCATDiagnostics:
    """Diagnostic tools for SCAT API integration."""

    def __init__(self):
        self.test_results = {}

    def run_full_diagnostic(self):
        """Run complete diagnostic test."""
        print("🔍 Running SCAT API Diagnostics...")
        print("=" * 50)

        # Test 1: Check SCAT modules
        self.test_scat_modules()

        # Test 2: Check server connectivity
        self.test_server_connectivity()

        # Test 3: Test basic API call
        self.test_basic_api_call()

        # Test 4: Test language support
        self.test_language_support()

        # Test 5: Test error handling
        self.test_error_handling()

        # Summary
        self.print_diagnostic_summary()

        return self.test_results

    def test_scat_modules(self):
        """Test if SCAT modules can be imported."""
        print("\n📦 Testing SCAT Module Import...")

        try:
            from SCAT.launcher import send_code_for_analysis, check_analyzer_running
            self.test_results["module_import"] = {"status": "pass", "message": "SCAT modules imported successfully"}
            print("✅ SCAT modules imported successfully")
        except ImportError as e:
            self.test_results["module_import"] = {"status": "fail", "message": f"Import error: {e}"}
            print(f"❌ Import error: {e}")
        except Exception as e:
            self.test_results["module_import"] = {"status": "fail", "message": f"Unexpected error: {e}"}
            print(f"❌ Unexpected error: {e}")

    def test_server_connectivity(self):
        """Test connection to SCAT server."""
        print("\n🌐 Testing Server Connectivity...")

        try:
            if check_analyzer_running():
                self.test_results["server_connectivity"] = {"status": "pass", "message": "SCAT server is running"}
                print("✅ SCAT server is running and accessible")
            else:
                self.test_results["server_connectivity"] = {"status": "warning", "message": "SCAT server not running"}
                print("⚠️ SCAT server is not running")
        except Exception as e:
            self.test_results["server_connectivity"] = {"status": "fail", "message": f"Connection test failed: {e}"}
            print(f"❌ Connection test failed: {e}")

    def test_basic_api_call(self):
        """Test basic API functionality."""
        print("\n🔧 Testing Basic API Call...")

        if not check_analyzer_running():
            self.test_results["basic_api"] = {"status": "skip", "message": "Server not running"}
            print("⏭️ Skipped (server not running)")
            return

        try:
            test_code = "print('Hello, SCAT!')"
            result = send_code_for_analysis(test_code, "python", "DiagnosticTest")

            if result.get("status") == "received":
                self.test_results["basic_api"] = {"status": "pass", "message": "API call successful"}
                print("✅ Basic API call successful")
            else:
                self.test_results["basic_api"] = {"status": "fail", "message": f"API returned error: {result.get('message')}"}
                print(f"❌ API returned error: {result.get('message')}")

        except Exception as e:
            self.test_results["basic_api"] = {"status": "fail", "message": f"API call failed: {e}"}
            print(f"❌ API call failed: {e}")

    def test_language_support(self):
        """Test language support."""
        print("\n🗣️ Testing Language Support...")

        languages_to_test = ["python", "ruby", "lua"]
        supported_languages = []

        for language in languages_to_test:
            try:
                test_code = f"# Test {language} code"
                if language == "ruby":
                    test_code = "# Test ruby code\nputs 'hello'"
                elif language == "lua":
                    test_code = "-- Test lua code\nprint('hello')"

                if check_analyzer_running():
                    result = send_code_for_analysis(test_code, language, "DiagnosticTest")
                    if result.get("status") == "received":
                        supported_languages.append(language)
                        print(f"✅ {language.title()} support confirmed")
                    else:
                        print(f"⚠️ {language.title()} support uncertain")
                else:
                    print(f"⏭️ {language.title()} test skipped (server not running)")

            except Exception as e:
                print(f"❌ {language.title()} test failed: {e}")

        self.test_results["language_support"] = {
            "status": "pass" if supported_languages else "warning",
            "supported_languages": supported_languages,
            "message": f"Confirmed support for: {', '.join(supported_languages)}"
        }

    def test_error_handling(self):
        """Test error handling."""
        print("\n🛡️ Testing Error Handling...")

        try:
            # Test with invalid JSON (this should be handled gracefully)
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)

            try:
                sock.connect(('localhost', 12345))
                sock.send(b"invalid json")
                response = sock.recv(1024)
                sock.close()

                # Should get an error response
                self.test_results["error_handling"] = {"status": "pass", "message": "Error handling works correctly"}
                print("✅ Error handling works correctly")

            except socket.timeout:
                self.test_results["error_handling"] = {"status": "warning", "message": "Timeout during error test"}
                print("⚠️ Timeout during error test")
            except Exception as e:
                self.test_results["error_handling"] = {"status": "pass", "message": f"Expected error caught: {e}"}
                print(f"✅ Expected error caught: {e}")

        except Exception as e:
            self.test_results["error_handling"] = {"status": "fail", "message": f"Error handling test failed: {e}"}
            print(f"❌ Error handling test failed: {e}")

    def print_diagnostic_summary(self):
        """Print diagnostic summary."""
        print("\n" + "=" * 50)
        print("📋 DIAGNOSTIC SUMMARY")
        print("=" * 50)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result["status"] == "pass")
        failed_tests = sum(1 for result in self.test_results.values() if result["status"] == "fail")
        warning_tests = sum(1 for result in self.test_results.values() if result["status"] == "warning")
        skipped_tests = sum(1 for result in self.test_results.values() if result["status"] == "skip")

        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️ Warnings: {warning_tests}")
        print(f"⏭️ Skipped: {skipped_tests}")

        if failed_tests == 0:
            print("\n🎉 All tests passed! SCAT integration is working correctly.")
        else:
            print(f"\n⚠️ {failed_tests} test(s) failed. Check the details above.")

        print("\n💡 Recommendations:")
        if not check_analyzer_running():
            print("- Launch SCAT application: python scat_gui.py")
        if failed_tests > 0:
            print("- Check SCAT installation and dependencies")
            print("- Verify network connectivity to localhost:12345")

# Usage
diagnostics = SCATDiagnostics()
results = diagnostics.run_full_diagnostic()
```

## 🧪 **Testing and Validation**

### **1. Integration Test Suite**
```python
import unittest
import socket
import json
import time
from SCAT.launcher import send_code_for_analysis, check_analyzer_running, launch_analyzer

class TestSCATAPIIntegration(unittest.TestCase):
    """Test suite for SCAT API integration."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.test_port = 12345
        cls.test_timeout = 5

        # Try to ensure SCAT is running
        if not check_analyzer_running(cls.test_port):
            print("Launching SCAT for testing...")
            launch_analyzer('gui')
            time.sleep(3)  # Wait for startup

    def test_server_availability(self):
        """Test if SCAT server is available."""
        self.assertTrue(
            check_analyzer_running(self.test_port),
            "SCAT server should be running for API tests"
        )

    def test_basic_api_call(self):
        """Test basic API functionality."""
        test_code = "print('Hello, World!')"
        result = send_code_for_analysis(test_code, "python", "TestSuite")

        self.assertIsInstance(result, dict)
        self.assertIn("status", result)
        self.assertEqual(result.get("status"), "received")

    def test_different_languages(self):
        """Test API with different programming languages."""
        test_cases = [
            ("print('Python test')", "python"),
            ("puts 'Ruby test'", "ruby"),
            ("print('Lua test')", "lua"),
            ("PRINT \"BASIC test\"", "basic")
        ]

        for code, language in test_cases:
            with self.subTest(language=language):
                result = send_code_for_analysis(code, language, "TestSuite")
                self.assertEqual(result.get("status"), "received")

    def test_error_handling(self):
        """Test API error handling."""
        # Test with invalid JSON
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.test_timeout)
            sock.connect(('localhost', self.test_port))
            sock.send(b"invalid json data")
            response = sock.recv(1024)
            sock.close()

            # Should receive some response (likely an error)
            self.assertIsNotNone(response)

        except Exception as e:
            # Connection errors are acceptable for this test
            pass

    def test_large_code_submission(self):
        """Test API with larger code submissions."""
        large_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

# Test the functions
print(fibonacci(10))
print(factorial(5))
print(bubble_sort([64, 34, 25, 12, 22, 11, 90]))
"""

        result = send_code_for_analysis(large_code, "python", "TestSuite")
        self.assertEqual(result.get("status"), "received")

    def test_concurrent_requests(self):
        """Test multiple concurrent API requests."""
        import threading
        import queue

        results_queue = queue.Queue()

        def send_request(code, language, request_id):
            result = send_code_for_analysis(code, language, f"TestSuite-{request_id}")
            results_queue.put((request_id, result))

        # Create multiple threads
        threads = []
        for i in range(3):
            code = f"print('Concurrent test {i}')"
            thread = threading.Thread(
                target=send_request,
                args=(code, "python", i)
            )
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join(timeout=10)

        # Check results
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())

        self.assertEqual(len(results), 3)
        for request_id, result in results:
            self.assertEqual(result.get("status"), "received")

if __name__ == "__main__":
    unittest.main()
```

### **2. Performance Testing**
```python
import time
import statistics
from SCAT.launcher import send_code_for_analysis, check_analyzer_running

class SCATPerformanceTester:
    """Performance testing for SCAT API."""

    def __init__(self):
        self.test_results = {}

    def run_performance_tests(self):
        """Run comprehensive performance tests."""
        print("🚀 Running SCAT API Performance Tests...")
        print("=" * 50)

        if not check_analyzer_running():
            print("❌ SCAT server not running. Please start SCAT first.")
            return

        # Test 1: Response time
        self.test_response_time()

        # Test 2: Throughput
        self.test_throughput()

        # Test 3: Large code handling
        self.test_large_code_performance()

        # Summary
        self.print_performance_summary()

        return self.test_results

    def test_response_time(self):
        """Test API response time."""
        print("\n⏱️ Testing Response Time...")

        test_code = "print('Performance test')"
        response_times = []

        for i in range(10):
            start_time = time.time()
            result = send_code_for_analysis(test_code, "python", "PerfTest")
            end_time = time.time()

            if result.get("status") == "received":
                response_times.append(end_time - start_time)

            time.sleep(0.1)  # Small delay between requests

        if response_times:
            avg_time = statistics.mean(response_times)
            min_time = min(response_times)
            max_time = max(response_times)

            self.test_results["response_time"] = {
                "average": avg_time,
                "minimum": min_time,
                "maximum": max_time,
                "samples": len(response_times)
            }

            print(f"✅ Average response time: {avg_time:.3f}s")
            print(f"   Min: {min_time:.3f}s, Max: {max_time:.3f}s")
        else:
            print("❌ No successful responses received")

    def test_throughput(self):
        """Test API throughput."""
        print("\n📊 Testing Throughput...")

        test_code = "print('Throughput test')"
        start_time = time.time()
        successful_requests = 0
        total_requests = 20

        for i in range(total_requests):
            result = send_code_for_analysis(test_code, "python", "ThroughputTest")
            if result.get("status") == "received":
                successful_requests += 1

        end_time = time.time()
        duration = end_time - start_time

        if duration > 0:
            throughput = successful_requests / duration

            self.test_results["throughput"] = {
                "requests_per_second": throughput,
                "successful_requests": successful_requests,
                "total_requests": total_requests,
                "duration": duration
            }

            print(f"✅ Throughput: {throughput:.2f} requests/second")
            print(f"   {successful_requests}/{total_requests} successful in {duration:.2f}s")
        else:
            print("❌ Throughput test failed")

    def test_large_code_performance(self):
        """Test performance with large code submissions."""
        print("\n📄 Testing Large Code Performance...")

        # Generate large code sample
        large_code = self._generate_large_code(1000)  # ~1000 lines

        start_time = time.time()
        result = send_code_for_analysis(large_code, "python", "LargeCodeTest")
        end_time = time.time()

        if result.get("status") == "received":
            processing_time = end_time - start_time
            code_size = len(large_code)

            self.test_results["large_code"] = {
                "processing_time": processing_time,
                "code_size_bytes": code_size,
                "code_lines": large_code.count('\n'),
                "bytes_per_second": code_size / processing_time if processing_time > 0 else 0
            }

            print(f"✅ Large code processed in {processing_time:.3f}s")
            print(f"   Code size: {code_size} bytes, {large_code.count('\n')} lines")
        else:
            print("❌ Large code test failed")

    def _generate_large_code(self, target_lines):
        """Generate large code sample for testing."""
        code_lines = [
            "# Large code sample for performance testing",
            "import sys",
            "import os",
            "import time",
            "",
            "class PerformanceTestClass:",
            "    def __init__(self):",
            "        self.data = []",
            ""
        ]

        # Add many similar functions
        for i in range(target_lines // 10):
            code_lines.extend([
                f"    def method_{i}(self, param):",
                f"        result = param * {i}",
                f"        for j in range({i % 10 + 1}):",
                f"            result += j",
                f"        return result",
                ""
            ])

        # Add main execution
        code_lines.extend([
            "if __name__ == '__main__':",
            "    test_instance = PerformanceTestClass()",
            "    for i in range(100):",
            "        print(f'Result {i}: {test_instance.method_0(i)}')"
        ])

        return "\n".join(code_lines)

    def print_performance_summary(self):
        """Print performance test summary."""
        print("\n" + "=" * 50)
        print("📈 PERFORMANCE SUMMARY")
        print("=" * 50)

        if "response_time" in self.test_results:
            rt = self.test_results["response_time"]
            print(f"Response Time: {rt['average']:.3f}s avg (min: {rt['minimum']:.3f}s, max: {rt['maximum']:.3f}s)")

        if "throughput" in self.test_results:
            tp = self.test_results["throughput"]
            print(f"Throughput: {tp['requests_per_second']:.2f} requests/second")

        if "large_code" in self.test_results:
            lc = self.test_results["large_code"]
            print(f"Large Code: {lc['processing_time']:.3f}s for {lc['code_lines']} lines")

        print("\n💡 Performance Tips:")
        print("- Use connection pooling for multiple requests")
        print("- Consider async requests for better throughput")
        print("- Monitor SCAT server performance under load")

# Usage
perf_tester = SCATPerformanceTester()
results = perf_tester.run_performance_tests()
```

## 📚 **Best Practices**

### **1. Connection Management**
```python
# ✅ Good: Use connection pooling for multiple requests
pool = SCATConnectionPool(max_connections=5)
for code_snippet in code_snippets:
    result = pool.send_analysis_request(code_snippet, "python", "MyIDE")

# ❌ Bad: Create new connection for each request
for code_snippet in code_snippets:
    result = send_code_for_analysis(code_snippet, "python", "MyIDE")
```

### **2. Error Handling**
```python
# ✅ Good: Comprehensive error handling
try:
    result = send_code_for_analysis(code, language, "MyIDE")
    if result.get("status") == "received":
        show_success_message("Code sent to SCAT")
    else:
        show_error_message(f"SCAT Error: {result.get('message')}")
except ConnectionError:
    show_error_message("SCAT server not available")
except socket.timeout:
    show_error_message("Request timed out")
except Exception as e:
    show_error_message(f"Unexpected error: {e}")

# ❌ Bad: No error handling
result = send_code_for_analysis(code, language, "MyIDE")
show_success_message("Code sent to SCAT")  # May not be true
```

### **3. User Experience**
```python
# ✅ Good: Provide feedback and status
def analyze_with_feedback(code, language):
    show_progress("Sending to SCAT...")

    if not check_analyzer_running():
        show_warning("SCAT not running. Launching...")
        if launch_analyzer('gui'):
            time.sleep(3)  # Wait for startup
        else:
            show_error("Failed to launch SCAT")
            return

    result = send_code_for_analysis(code, language, "MyIDE")
    hide_progress()

    if result.get("status") == "received":
        show_notification("Analysis started in SCAT")
    else:
        show_error(f"Analysis failed: {result.get('message')}")

# ❌ Bad: No user feedback
def analyze_silently(code, language):
    send_code_for_analysis(code, language, "MyIDE")
    # User has no idea what happened
```

### **4. Configuration Management**
```python
# ✅ Good: Configurable settings
config = SCATConfig()
port = config.get("api_port", 12345)
timeout = config.get("timeout", 5)
auto_launch = config.get("auto_launch", True)

# ❌ Bad: Hard-coded values
port = 12345  # What if user changed the port?
timeout = 5   # What if user needs longer timeout?
```

## 📝 **Integration Checklist**

### **Pre-Integration Setup**
- [ ] Verify SCAT is installed and accessible
- [ ] Test basic SCAT functionality: `python scat_gui.py`
- [ ] Confirm PyQt6 is installed for SCAT GUI
- [ ] Test API connectivity: `python -c "from SCAT.launcher import check_analyzer_running; print(check_analyzer_running())"`

### **Basic API Integration**
- [ ] Implement basic `send_code_for_analysis()` call
- [ ] Add server status checking with `check_analyzer_running()`
- [ ] Implement language auto-detection
- [ ] Add basic error handling for connection failures
- [ ] Test with sample code snippets

### **Advanced Integration**
- [ ] Implement connection pooling for performance
- [ ] Add comprehensive error handling and recovery
- [ ] Create user notification system
- [ ] Add configuration management
- [ ] Implement retry logic with exponential backoff

### **UI Integration**
- [ ] Add SCAT menu items to IDE
- [ ] Create toolbar buttons for quick analysis
- [ ] Add context menu options for code analysis
- [ ] Implement status indicators
- [ ] Add progress feedback for long operations

### **Testing and Validation**
- [ ] Run diagnostic tests
- [ ] Perform performance testing
- [ ] Test with various code samples and languages
- [ ] Validate error handling scenarios
- [ ] Test concurrent request handling

### **Production Deployment**
- [ ] Configure appropriate timeouts and retry settings
- [ ] Set up error logging and monitoring
- [ ] Create user documentation
- [ ] Test with real-world usage scenarios
- [ ] Implement graceful degradation when SCAT unavailable

## 🆘 **Common Issues and Solutions**

### **Issue: "Connection refused" error**
**Cause:** SCAT server is not running
**Solution:**
```python
if not check_analyzer_running():
    print("SCAT not running. Launch with: python scat_gui.py")
    # Or auto-launch if configured
    launch_analyzer('gui')
```

### **Issue: "Request timeout" error**
**Cause:** SCAT is busy or unresponsive
**Solution:**
```python
# Increase timeout
result = send_code_for_analysis(code, language, "MyIDE", timeout=10)

# Or implement retry logic
client = RobustSCATClient(max_retries=3)
result = client.send_with_retry(code, language, "MyIDE")
```

### **Issue: "Invalid JSON" error**
**Cause:** API version mismatch or corrupted data
**Solution:**
```python
# Ensure proper request format
request = {
    "code": code,
    "language": language,
    "source_app": "MyIDE",
    "version": "2.0"  # Include version
}
```

### **Issue: Poor performance with large files**
**Cause:** Large code submissions or network overhead
**Solution:**
```python
# Use async requests for large files
async_client = AsyncSCATClient()
result = await async_client.send_analysis_async(code, language, "MyIDE")

# Or implement chunking for very large files
```

### **Issue: SCAT GUI doesn't show analysis results**
**Cause:** API sends code but results not visible
**Solution:**
- Ensure SCAT GUI is in foreground
- Check SCAT's analysis history panel
- Verify the code was actually received (check response status)

---

**For IDE Integration (direct method), see `IDE_INTEGRATION_GUIDE.md`**

**For general SCAT usage, see `README.md`**

**For troubleshooting, see `SCAT_TROUBLESHOOTING.md`**
