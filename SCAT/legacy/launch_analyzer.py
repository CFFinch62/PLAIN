#!/usr/bin/env python3
"""
Launcher script for Code Analysis Professional
This script can be called from any IDE to launch the analyzer.
"""

import sys
import os
import subprocess
import socket
import json
import argparse
from pathlib import Path


def check_analyzer_running():
    """Check if Code Analysis Professional is already running."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 12345))
        sock.close()
        return result == 0
    except:
        return False


def launch_analyzer():
    """Launch Code Analysis Professional."""
    script_dir = Path(__file__).parent
    analyzer_script = script_dir / "code_analyzer_app.py"
    
    if not analyzer_script.exists():
        print(f"Error: Code Analysis Professional not found at {analyzer_script}")
        return False
    
    try:
        # Launch the analyzer
        subprocess.Popen([sys.executable, str(analyzer_script)])
        print("Code Analysis Professional launched successfully")
        return True
    except Exception as e:
        print(f"Error launching Code Analysis Professional: {e}")
        return False


def send_code_for_analysis(code, language="python", source_app="IDE", timeout=5):
    """Send code to running analyzer for analysis."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect(('localhost', 12345))
        
        request = {
            "code": code,
            "language": language,
            "source_app": source_app
        }
        
        sock.send(json.dumps(request).encode('utf-8'))
        response = sock.recv(1024).decode('utf-8')
        sock.close()
        
        return json.loads(response)
        
    except socket.timeout:
        return {"status": "error", "message": "Connection timeout"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def analyze_file(file_path, language=None, source_app="IDE"):
    """Analyze a code file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Auto-detect language if not specified
        if language is None:
            ext = Path(file_path).suffix.lower()
            language_map = {
                '.py': 'python',
                '.js': 'javascript',
                '.java': 'java',
                '.cpp': 'cpp',
                '.c': 'c',
                '.cs': 'csharp'
            }
            language = language_map.get(ext, 'python')
        
        # Check if analyzer is running
        if not check_analyzer_running():
            print("Code Analysis Professional is not running. Launching...")
            if not launch_analyzer():
                return False
            
            # Wait a moment for the analyzer to start
            import time
            time.sleep(2)
        
        # Send code for analysis
        result = send_code_for_analysis(code, language, source_app)
        
        if result["status"] == "received":
            print(f"✅ Code from {file_path} sent for analysis")
            print("Check Code Analysis Professional for results")
            return True
        else:
            print(f"❌ Error: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"Error analyzing file: {e}")
        return False


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(
        description="Launch Code Analysis Professional or send code for analysis"
    )
    
    parser.add_argument(
        '--launch', '-l',
        action='store_true',
        help='Launch Code Analysis Professional'
    )
    
    parser.add_argument(
        '--file', '-f',
        type=str,
        help='Analyze a specific file'
    )
    
    parser.add_argument(
        '--language',
        type=str,
        choices=['python', 'javascript', 'java', 'cpp', 'c', 'csharp'],
        help='Programming language (auto-detected if not specified)'
    )
    
    parser.add_argument(
        '--source-app',
        type=str,
        default='CLI',
        help='Name of the source application (default: CLI)'
    )
    
    parser.add_argument(
        '--code', '-c',
        type=str,
        help='Analyze code directly from command line'
    )
    
    parser.add_argument(
        '--status', '-s',
        action='store_true',
        help='Check if Code Analysis Professional is running'
    )
    
    args = parser.parse_args()
    
    # Handle different commands
    if args.status:
        if check_analyzer_running():
            print("✅ Code Analysis Professional is running")
        else:
            print("❌ Code Analysis Professional is not running")
        return
    
    if args.launch:
        launch_analyzer()
        return
    
    if args.file:
        analyze_file(args.file, args.language, args.source_app)
        return
    
    if args.code:
        language = args.language or 'python'
        
        # Check if analyzer is running
        if not check_analyzer_running():
            print("Code Analysis Professional is not running. Launching...")
            if not launch_analyzer():
                return
            
            # Wait a moment for the analyzer to start
            import time
            time.sleep(2)
        
        # Send code for analysis
        result = send_code_for_analysis(args.code, language, args.source_app)
        
        if result["status"] == "received":
            print("✅ Code sent for analysis")
            print("Check Code Analysis Professional for results")
        else:
            print(f"❌ Error: {result.get('message', 'Unknown error')}")
        return
    
    # No specific command, show help
    parser.print_help()


# Example usage functions for IDE integration
def ide_launch_analyzer():
    """Simple function for IDEs to launch the analyzer."""
    return launch_analyzer()


def ide_analyze_code(code, language="python", ide_name="IDE"):
    """Simple function for IDEs to send code for analysis."""
    # Launch analyzer if not running
    if not check_analyzer_running():
        if not launch_analyzer():
            return {"status": "error", "message": "Failed to launch analyzer"}
        
        # Wait for startup
        import time
        time.sleep(2)
    
    # Send code
    return send_code_for_analysis(code, language, ide_name)


if __name__ == "__main__":
    main()
