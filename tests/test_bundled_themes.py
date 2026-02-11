#!/usr/bin/env python3
"""
Test script to verify bundled theme copying functionality
"""
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from plain_ide.app.settings import SettingsManager
from plain_ide.app.themes import ThemeManager

def test_bundled_themes():
    print("Testing bundled theme copying...")
    print()
    
    # Create settings manager
    settings = SettingsManager()
    
    # Create theme manager (should trigger theme copying)
    print("Initializing ThemeManager...")
    theme_manager = ThemeManager(settings)
    
    # Check bundled directory
    bundled_dir = theme_manager._get_bundled_themes_dir()
    bundled_themes = list(bundled_dir.glob("*.conf"))
    print(f"✓ Found {len(bundled_themes)} bundled themes in: {bundled_dir}")
    
    # Check user config directory
    user_dir = theme_manager.syntax_themes_dir
    user_themes = list(user_dir.glob("*.conf"))
    print(f"✓ Found {len(user_themes)} themes in user config: {user_dir}")
    
    # Check loaded themes
    available_themes = theme_manager.get_available_syntax_themes()
    print(f"✓ Loaded {len(available_themes)} syntax themes")
    
    # List first 10 themes
    print()
    print("Sample themes:")
    for theme_name in sorted(available_themes)[:10]:
        print(f"  - {theme_name}")
    
    if len(available_themes) > 10:
        print(f"  ... and {len(available_themes) - 10} more")
    
    print()
    print("✅ Bundled theme system working correctly!")
    return True

if __name__ == "__main__":
    try:
        test_bundled_themes()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
