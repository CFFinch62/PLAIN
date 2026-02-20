#!/usr/bin/env python3
"""
SCAT GUI Launcher - Source Code Analysis Tool

This script launches the SCAT GUI application directly.
It's a standalone launcher for the graphical interface.

Usage:
    python scat_gui.py

Requirements:
    - Python 3.8+
    - PyQt6
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))


def check_dependencies():
    """Check if required dependencies are available."""
    try:
        import PyQt6
        return True
    except ImportError:
        return False


def install_dependencies():
    """Provide instructions for installing dependencies."""
    print("❌ PyQt6 is required for the GUI interface")
    print("\n📦 To install PyQt6:")
    print("   pip install PyQt6")
    print("\n🔧 Alternative installation methods:")
    print("   conda install pyqt")
    print("   pip install -r requirements.txt")
    print("\n💡 For CLI-only usage (no GUI), use:")
    print("   python main.py --cli")


def main():
    """Main function to launch SCAT GUI."""
    print("🚀 SCAT - Source Code Analysis Tool")
    print("=" * 50)

    # Check dependencies
    if not check_dependencies():
        install_dependencies()
        sys.exit(1)

    try:
        # Import and launch GUI
        from ui.main_window import main as gui_main
        print("✅ Dependencies found")
        print("🎨 Launching GUI interface...")

        # Check if we're in a headless environment
        if os.environ.get('DISPLAY') is None and os.name != 'nt':
            print("⚠️  No display detected. GUI requires a display environment.")
            print("💡 Try running in a desktop environment or use CLI mode:")
            print("   python main.py --cli")
            sys.exit(1)

        # Launch GUI (QApplication will be created in main_window.main())
        gui_main()

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure PyQt6 is installed: pip install PyQt6")
        print("2. Check Python version (3.8+ required)")
        print("3. Try running from the correct directory")
        print("4. For CLI mode: python main.py --cli")
        sys.exit(1)

    except Exception as e:
        print(f"❌ Failed to launch GUI: {e}")
        print(f"Error details: {type(e).__name__}: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("1. Check if all files are present")
        print("2. Try CLI mode: python main.py --cli")
        print("3. Check if you're in a desktop environment")
        print("4. Try: python -c 'import PyQt6; print(\"PyQt6 OK\")'")

        # Offer CLI fallback
        print("\n💡 Would you like to try CLI mode instead?")
        try:
            response = input("Type 'y' for CLI mode, or any other key to exit: ").lower()
            if response == 'y':
                print("\n🔄 Switching to CLI mode...")
                os.system("python main.py --cli")
        except (KeyboardInterrupt, EOFError):
            pass

        sys.exit(1)


if __name__ == "__main__":
    main()
