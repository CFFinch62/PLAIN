#!/usr/bin/env python3
"""
Launcher script for the modular Code Analysis Tool.

This script provides IDE integration capabilities for the new modular
code analysis tool, supporting multiple programming languages.
"""

import sys
import os
import subprocess
import socket
import json
import argparse
from pathlib import Path
from typing import Optional, Dict, Any


def check_analyzer_running(port: int = 12345) -> bool:
    """Check if Code Analysis Tool is already running."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    except:
        return False


def launch_analyzer(mode: str = 'gui') -> bool:
    """Launch Code Analysis Tool."""
    script_dir = Path(__file__).parent
    main_script = script_dir / "main.py"
    
    if not main_script.exists():
        print(f"Error: Code Analysis Tool not found at {main_script}")
        return False
    
    try:
        # Launch the analyzer
        if mode == 'cli':
            subprocess.Popen([sys.executable, str(main_script), '--cli'])
        else:
            subprocess.Popen([sys.executable, str(main_script)])
        
        print(f"Code Analysis Tool launched successfully in {mode} mode")
        return True
    except Exception as e:
        print(f"Error launching Code Analysis Tool: {e}")
        return False


def send_code_for_analysis(code: str, language: str = "python", 
                          source_app: str = "IDE", port: int = 12345,
                          timeout: int = 5) -> Dict[str, Any]:
    """Send code to running analyzer for analysis."""
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


def analyze_file(file_path: str, language: Optional[str] = None, 
                source_app: str = "IDE") -> bool:
    """Analyze a code file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Auto-detect language if not specified
        if language is None:
            ext = Path(file_path).suffix.lower()
            language_map = {
                '.py': 'python',
                '.pyw': 'python',
                '.rb': 'ruby',
                '.rbw': 'ruby',
                '.lua': 'lua',
                '.js': 'javascript',
                '.java': 'java',
                '.cpp': 'cpp',
                '.c': 'c',
                '.cs': 'csharp'
            }
            language = language_map.get(ext, 'python')
        
        # Check if analyzer is running
        if not check_analyzer_running():
            print("Code Analysis Tool is not running. Launching...")
            if not launch_analyzer():
                return False
            
            # Wait a moment for the analyzer to start
            import time
            time.sleep(3)
        
        # Send code for analysis
        result = send_code_for_analysis(code, language, source_app)
        
        if result.get("status") == "received":
            print(f"✅ Code from {file_path} sent for analysis")
            print("Check Code Analysis Tool for results")
            return True
        else:
            print(f"❌ Error: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"Error analyzing file: {e}")
        return False


def analyze_code_direct(code: str, language: str = "python") -> Optional[Dict[str, Any]]:
    """Analyze code directly without GUI (for IDE integration)."""
    try:
        # Import the analyzer directly
        sys.path.insert(0, str(Path(__file__).parent))
        
        from core.analyzer import CodeAnalyzer
        from core.models import AnalysisConfig
        
        # Create analyzer and analyze code
        config = AnalysisConfig()
        analyzer = CodeAnalyzer(config)
        report = analyzer.analyze_code(code, language)
        
        # Return results as dictionary
        return report.to_dict()
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Analysis error: {str(e)}",
            "language": language
        }


def get_supported_languages() -> Dict[str, Dict[str, Any]]:
    """Get information about supported languages."""
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        
        from core.analyzer import CodeAnalyzer
        from core.models import AnalysisConfig
        
        config = AnalysisConfig()
        analyzer = CodeAnalyzer(config)
        languages = analyzer.get_supported_languages()
        
        # Convert to serializable format
        return {name: info.to_dict() for name, info in languages.items()}
        
    except Exception as e:
        return {"error": str(e)}


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(
        description="Launch Code Analysis Tool or send code for analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  launcher.py --launch                     # Launch GUI
  launcher.py --launch-cli                 # Launch CLI
  launcher.py --file script.py             # Analyze file
  launcher.py --code "print('hello')"      # Analyze code string
  launcher.py --languages                  # List supported languages
        """
    )
    
    parser.add_argument(
        '--launch', '-l',
        action='store_true',
        help='Launch Code Analysis Tool GUI'
    )
    
    parser.add_argument(
        '--launch-cli',
        action='store_true',
        help='Launch Code Analysis Tool CLI'
    )
    
    parser.add_argument(
        '--file', '-f',
        type=str,
        help='Analyze a specific file'
    )
    
    parser.add_argument(
        '--language',
        type=str,
        choices=['python', 'ruby', 'lua'],
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
        '--direct',
        action='store_true',
        help='Analyze code directly without launching GUI (for IDE integration)'
    )
    
    parser.add_argument(
        '--status', '-s',
        action='store_true',
        help='Check if Code Analysis Tool is running'
    )
    
    parser.add_argument(
        '--languages',
        action='store_true',
        help='List supported programming languages'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=12345,
        help='Port number for API communication (default: 12345)'
    )
    
    args = parser.parse_args()
    
    # Handle different commands
    if args.status:
        if check_analyzer_running(args.port):
            print("✅ Code Analysis Tool is running")
        else:
            print("❌ Code Analysis Tool is not running")
        return
    
    if args.languages:
        languages = get_supported_languages()
        if "error" in languages:
            print(f"❌ Error getting languages: {languages['error']}")
        else:
            print(f"Supported languages ({len(languages)}):")
            for name, info in languages.items():
                print(f"  • {info['name']}: {', '.join(info['extensions'])}")
                print(f"    {info['description']}")
        return
    
    if args.launch:
        launch_analyzer('gui')
        return
    
    if args.launch_cli:
        launch_analyzer('cli')
        return
    
    if args.file:
        analyze_file(args.file, args.language, args.source_app)
        return
    
    if args.code:
        language = args.language or 'python'
        
        if args.direct:
            # Direct analysis for IDE integration
            result = analyze_code_direct(args.code, language)
            if result:
                print(json.dumps(result, indent=2))
        else:
            # Send to running analyzer
            if not check_analyzer_running(args.port):
                print("Code Analysis Tool is not running. Launching...")
                if not launch_analyzer():
                    return
                
                # Wait a moment for the analyzer to start
                import time
                time.sleep(3)
            
            # Send code for analysis
            result = send_code_for_analysis(args.code, language, args.source_app, args.port)
            
            if result.get("status") == "received":
                print("✅ Code sent for analysis")
                print("Check Code Analysis Tool for results")
            else:
                print(f"❌ Error: {result.get('message', 'Unknown error')}")
        return
    
    # No specific command, show help
    parser.print_help()


# IDE integration functions
def ide_launch_analyzer(mode: str = 'gui') -> bool:
    """Simple function for IDEs to launch the analyzer."""
    return launch_analyzer(mode)


def ide_analyze_code(code: str, language: str = "python", ide_name: str = "IDE") -> Dict[str, Any]:
    """Simple function for IDEs to analyze code directly."""
    return analyze_code_direct(code, language) or {
        "status": "error", 
        "message": "Analysis failed"
    }


def ide_analyze_file(file_path: str, language: Optional[str] = None, ide_name: str = "IDE") -> bool:
    """Simple function for IDEs to analyze a file."""
    return analyze_file(file_path, language, ide_name)


def ide_get_supported_languages() -> Dict[str, Dict[str, Any]]:
    """Simple function for IDEs to get supported languages."""
    return get_supported_languages()


if __name__ == "__main__":
    main()
