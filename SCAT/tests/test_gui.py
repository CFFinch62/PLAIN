#!/usr/bin/env python3
"""
Test script for SCAT GUI components.

This script tests the GUI components to ensure they work correctly
without actually launching the full GUI (for automated testing).
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_gui_imports():
    """Test that GUI components can be imported."""
    print("🧪 Testing GUI Imports")
    print("-" * 30)
    
    try:
        import PyQt6
        print("✅ PyQt6 available")
    except ImportError:
        print("❌ PyQt6 not available - GUI tests skipped")
        return False
    
    try:
        from ui.themes import SCATTheme
        print("✅ SCATTheme imported")
    except ImportError as e:
        print(f"❌ Failed to import SCATTheme: {e}")
        return False
    
    try:
        from ui.components.code_editor import CodeEditor
        print("✅ CodeEditor imported")
    except ImportError as e:
        print(f"❌ Failed to import CodeEditor: {e}")
        return False
    
    try:
        from ui.components.language_selector import LanguageSelector
        print("✅ LanguageSelector imported")
    except ImportError as e:
        print(f"❌ Failed to import LanguageSelector: {e}")
        return False
    
    try:
        from ui.components.complexity_badge import ComplexityBadge
        print("✅ ComplexityBadge imported")
    except ImportError as e:
        print(f"❌ Failed to import ComplexityBadge: {e}")
        return False
    
    try:
        from ui.components.results_table import ResultsTable
        print("✅ ResultsTable imported")
    except ImportError as e:
        print(f"❌ Failed to import ResultsTable: {e}")
        return False
    
    try:
        from ui.components.analysis_display import AnalysisDisplayWidget
        print("✅ AnalysisDisplayWidget imported")
    except ImportError as e:
        print(f"❌ Failed to import AnalysisDisplayWidget: {e}")
        return False
    
    try:
        from ui.main_window import SCATMainWindow
        print("✅ SCATMainWindow imported")
    except ImportError as e:
        print(f"❌ Failed to import SCATMainWindow: {e}")
        return False
    
    return True


def test_theme_functionality():
    """Test theme functionality."""
    print("\n🎨 Testing Theme Functionality")
    print("-" * 30)
    
    try:
        from ui.themes import SCATTheme
        
        # Test color access
        colors = SCATTheme.COLORS
        print(f"✅ Colors defined: {len(colors)} colors")
        
        # Test specific colors
        required_colors = ['primary', 'background', 'text_primary', 'success', 'error']
        for color in required_colors:
            if color in colors:
                print(f"✅ {color}: {colors[color]}")
            else:
                print(f"❌ Missing color: {color}")
                return False
        
        # Test stylesheet generation
        stylesheet = SCATTheme.get_stylesheet()
        if stylesheet and len(stylesheet) > 100:
            print(f"✅ Stylesheet generated: {len(stylesheet)} characters")
        else:
            print("❌ Stylesheet generation failed")
            return False
        
        # Test complexity colors
        test_complexities = ['O(1)', 'O(n)', 'O(n²)', 'O(2ⁿ)']
        for complexity in test_complexities:
            color = SCATTheme.get_complexity_color(complexity)
            print(f"✅ {complexity}: {color}")
        
        return True
        
    except Exception as e:
        print(f"❌ Theme test failed: {e}")
        return False


def test_component_creation():
    """Test that GUI components can be created."""
    print("\n🧩 Testing Component Creation")
    print("-" * 30)
    
    try:
        from PyQt6.QtWidgets import QApplication
        from ui.components.code_editor import CodeEditor
        from ui.components.language_selector import LanguageSelector
        from ui.components.complexity_badge import ComplexityBadge, ComplexityDisplay
        
        # Create QApplication (required for Qt widgets)
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Test CodeEditor
        try:
            editor = CodeEditor()
            print("✅ CodeEditor created")
            
            # Test basic functionality
            editor.setPlainText("def test(): pass")
            if editor.toPlainText().strip():
                print("✅ CodeEditor text operations work")
            
            editor.set_language('python')
            print("✅ CodeEditor language setting works")
            
        except Exception as e:
            print(f"❌ CodeEditor creation failed: {e}")
            return False
        
        # Test LanguageSelector
        try:
            selector = LanguageSelector()
            print("✅ LanguageSelector created")
            
            # Test language operations
            languages = selector.get_all_languages()
            if languages:
                print(f"✅ LanguageSelector has {len(languages)} languages")
            
        except Exception as e:
            print(f"❌ LanguageSelector creation failed: {e}")
            return False
        
        # Test ComplexityBadge
        try:
            badge = ComplexityBadge("O(n)", "time")
            print("✅ ComplexityBadge created")
            
            display = ComplexityDisplay()
            print("✅ ComplexityDisplay created")
            
            display.set_complexity("O(n)", "O(1)")
            print("✅ ComplexityDisplay operations work")
            
        except Exception as e:
            print(f"❌ ComplexityBadge creation failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Component creation test failed: {e}")
        return False


def test_integration_with_analyzer():
    """Test GUI integration with the analysis engine."""
    print("\n🔗 Testing Analyzer Integration")
    print("-" * 30)
    
    try:
        from PyQt6.QtWidgets import QApplication
        from core.analyzer import CodeAnalyzer
        from core.models import AnalysisConfig
        from ui.components.language_selector import LanguageSelector
        from ui.components.analysis_display import AnalysisDisplayWidget
        from ui.components.results_table import ResultsTable
        
        # Create QApplication if needed
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Create analyzer
        config = AnalysisConfig()
        analyzer = CodeAnalyzer(config)
        print("✅ Analyzer created")
        
        # Test language selector integration
        selector = LanguageSelector()
        selector.update_from_analyzer(analyzer)
        print("✅ LanguageSelector updated from analyzer")
        
        # Test analysis with GUI components
        test_code = '''
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
        '''
        
        report = analyzer.analyze_code(test_code, 'python')
        print("✅ Analysis completed")
        
        # Test results display
        results_table = ResultsTable()
        results_table.set_results(report.detailed_results)
        print("✅ ResultsTable updated with analysis results")
        
        # Test analysis display
        analysis_display = AnalysisDisplayWidget()
        analysis_display.update_from_report(report)
        print("✅ AnalysisDisplayWidget updated with report")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False


def main():
    """Run all GUI tests."""
    print("🧪 SCAT GUI Component Tests")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_gui_imports),
        ("Theme Tests", test_theme_functionality),
        ("Component Creation", test_component_creation),
        ("Analyzer Integration", test_integration_with_analyzer),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✅ {test_name}: PASSED")
            else:
                print(f"\n❌ {test_name}: FAILED")
        except Exception as e:
            print(f"\n💥 {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All GUI tests passed!")
        print("\nThe SCAT GUI is ready to use!")
        print("Run: python scat_gui.py")
    else:
        print("⚠️  Some GUI tests failed")
        print("Check the error messages above for details")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
