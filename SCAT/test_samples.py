#!/usr/bin/env python3
"""
Quick test to verify sample code is available for all languages.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from ui.components.code_editor import CodeEditor

def test_sample_code():
    """Test that sample code exists for all languages."""
    editor = CodeEditor()
    
    # Languages to test
    languages = ['python', 'ruby', 'lua', 'basic', 'pseudocode', 'plain', 'steps']
    
    print("Testing sample code availability...\n")
    
    for lang in languages:
        editor.insert_sample_code(lang)
        code = editor.toPlainText()
        
        if code:
            lines = len(code.split('\n'))
            print(f"✓ {lang.upper():12} - {lines} lines of sample code")
        else:
            print(f"✗ {lang.upper():12} - NO SAMPLE CODE FOUND!")
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    # Note: This requires PyQt6 to be installed
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication(sys.argv)
        test_sample_code()
    except ImportError:
        print("PyQt6 not installed. Cannot test GUI components.")
        print("Install with: pip install PyQt6")

