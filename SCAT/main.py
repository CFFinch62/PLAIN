#!/usr/bin/env python3
"""
Main entry point for the Code Analysis Tool.

This is the new modular version of PyCAT, refactored to support
multiple programming languages through a plugin-like architecture.

Usage:
    python main.py                    # Launch GUI application
    python main.py --cli              # Command-line interface
    python main.py --file <path>      # Analyze a specific file
    python main.py --help             # Show help
"""

import sys
import argparse
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core.analyzer import CodeAnalyzer
from core.models import AnalysisConfig
from core.registry import LanguageRegistry


def setup_analyzers():
    """Setup and register language analyzers."""
    registry = LanguageRegistry()

    # Register Python analyzer
    try:
        from languages.python_analyzer import PythonAnalyzer
        registry.register_analyzer(
            'python',
            PythonAnalyzer,
            ['.py', '.pyw'],
            'Python programming language',
            ['loops', 'recursion', 'built-ins', 'comprehensions', 'data-structures']
        )
        print("✓ Python analyzer registered")
    except ImportError as e:
        print(f"⚠ Failed to register Python analyzer: {e}")

    # Register Ruby analyzer
    try:
        from languages.ruby_analyzer import RubyAnalyzer
        registry.register_analyzer(
            'ruby',
            RubyAnalyzer,
            ['.rb', '.rbw'],
            'Ruby programming language',
            ['loops', 'iterators', 'built-ins', 'blocks', 'data-structures']
        )
        print("✓ Ruby analyzer registered")
    except ImportError as e:
        print(f"⚠ Failed to register Ruby analyzer: {e}")

    # Register Lua analyzer
    try:
        from languages.lua_analyzer import LuaAnalyzer
        registry.register_analyzer(
            'lua',
            LuaAnalyzer,
            ['.lua'],
            'Lua programming language',
            ['loops', 'functions', 'tables', 'strings', 'built-ins']
        )
        print("✓ Lua analyzer registered")
    except ImportError as e:
        print(f"⚠ Failed to register Lua analyzer: {e}")

    # Register BASIC analyzer
    try:
        from languages.basic_analyzer import BasicAnalyzer
        registry.register_analyzer(
            'basic',
            BasicAnalyzer,
            ['.bas', '.basic'],
            'BASIC programming language',
            ['loops', 'functions', 'arrays', 'strings', 'built-ins', 'control-flow']
        )
        print("✓ BASIC analyzer registered")
    except ImportError as e:
        print(f"⚠ Failed to register BASIC analyzer: {e}")

    # Register Pseudocode analyzer
    try:
        from languages.pseudocode_analyzer import PseudocodeAnalyzer
        registry.register_analyzer(
            'pseudocode',
            PseudocodeAnalyzer,
            ['.pseudo', '.txt'],
            'Pseudocode algorithm notation',
            ['loops', 'algorithms', 'data-structures', 'complexity-analysis']
        )
        print("✓ Pseudocode analyzer registered")
    except ImportError as e:
        print(f"⚠ Failed to register Pseudocode analyzer: {e}")

    # Register PLAIN analyzer
    try:
        from languages.plain_analyzer import PlainAnalyzer
        registry.register_analyzer(
            'plain',
            PlainAnalyzer,
            ['.plain'],
            'PLAIN programming language',
            ['loops', 'tasks', 'recursion', 'built-ins', 'data-structures', 'collections']
        )
        print("✓ PLAIN analyzer registered")
    except ImportError as e:
        print(f"⚠ Failed to register PLAIN analyzer: {e}")

    # Register STEPS analyzer
    try:
        from languages.steps_analyzer import StepsAnalyzer
        registry.register_analyzer(
            'steps',
            StepsAnalyzer,
            ['.step', '.building', '.floor'],
            'Steps educational programming language',
            ['loops', 'steps', 'risers', 'built-ins', 'data-structures', 'error-handling']
        )
        print("✓ STEPS analyzer registered")
    except ImportError as e:
        print(f"⚠ Failed to register STEPS analyzer: {e}")

    return registry


def analyze_file_cli(file_path: str, language: str = None):
    """Analyze a file from command line."""
    try:
        # Setup analyzer
        config = AnalysisConfig()
        analyzer = CodeAnalyzer(config)

        # Analyze file
        print(f"\n🔍 Analyzing file: {file_path}")
        report = analyzer.analyze_file(file_path, language)

        # Display results
        print("\n" + "="*60)
        print("📊 ANALYSIS RESULTS")
        print("="*60)
        print(f"Language: {report.language}")
        print(f"Lines of code: {report.code_length}")
        print(f"Time complexity: {report.overall_time_complexity}")
        print(f"Space complexity: {report.overall_space_complexity}")
        print(f"Quality score: {report.quality_score:.1f}/100")
        print(f"Performance rating: {report.performance_rating}")

        if report.warnings:
            print(f"\n⚠️  WARNINGS ({len(report.warnings)}):")
            for warning in report.warnings:
                print(f"  • {warning}")

        if report.suggestions:
            print(f"\n💡 SUGGESTIONS ({len(report.suggestions)}):")
            for suggestion in report.suggestions:
                print(f"  • {suggestion}")

        if report.detailed_results:
            print(f"\n🔍 DETAILED ANALYSIS ({len(report.detailed_results)} patterns found):")
            for result in report.detailed_results:
                print(f"  Line {result.line_number} [{result.analysis_type}]: "
                      f"Time {result.time_complexity}, Space {result.space_complexity}")
                print(f"    {result.description}")

        print("\n" + "="*60)

    except Exception as e:
        print(f"❌ Error analyzing file: {e}")
        return False

    return True


def interactive_cli():
    """Interactive command-line interface."""
    print("🔍 Code Analysis Tool - Interactive Mode")
    print("Type 'help' for commands, 'quit' to exit")

    config = AnalysisConfig()
    analyzer = CodeAnalyzer(config)

    while True:
        try:
            command = input("\n> ").strip()

            if command.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break

            elif command.lower() == 'help':
                print("\nAvailable commands:")
                print("  analyze <file>     - Analyze a code file")
                print("  languages          - List supported languages")
                print("  config             - Show current configuration")
                print("  help               - Show this help")
                print("  quit               - Exit the program")

            elif command.lower() == 'languages':
                languages = analyzer.get_supported_languages()
                print(f"\nSupported languages ({len(languages)}):")
                for lang, info in languages.items():
                    print(f"  • {info.name}: {', '.join(info.extensions)}")

            elif command.lower() == 'config':
                print(f"\nCurrent configuration:")
                print(f"  Max depth: {config.max_depth}")
                print(f"  Include space analysis: {config.include_space_analysis}")
                print(f"  Generate suggestions: {config.generate_suggestions}")
                print(f"  Confidence threshold: {config.confidence_threshold}")

            elif command.startswith('analyze '):
                file_path = command[8:].strip()
                if file_path:
                    analyze_file_cli(file_path)
                else:
                    print("Please specify a file path")

            else:
                print("Unknown command. Type 'help' for available commands.")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


def launch_gui():
    """Launch the GUI application."""
    try:
        # Import GUI components
        from ui.main_window import main as gui_main
        print("🚀 Launching SCAT GUI application...")
        gui_main()
        return True
    except ImportError as e:
        print("❌ GUI dependencies not available")
        print("Install PyQt6: pip install PyQt6")
        print(f"Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Failed to launch GUI: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Code Analysis Tool - Multi-language complexity analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                           # Launch GUI
  python main.py --cli                     # Interactive CLI
  python main.py --file script.py         # Analyze Python file
  python main.py --file script.rb --lang ruby  # Analyze Ruby file
        """
    )

    parser.add_argument(
        '--cli', '-c',
        action='store_true',
        help='Launch interactive command-line interface'
    )

    parser.add_argument(
        '--file', '-f',
        type=str,
        help='Analyze a specific file'
    )

    parser.add_argument(
        '--language', '--lang', '-l',
        type=str,
        choices=['python', 'ruby', 'lua'],
        help='Programming language (auto-detected if not specified)'
    )

    parser.add_argument(
        '--list-languages',
        action='store_true',
        help='List supported programming languages'
    )

    parser.add_argument(
        '--version', '-v',
        action='version',
        version='Code Analysis Tool 2.0.0'
    )

    args = parser.parse_args()

    # Setup analyzers
    print("🔧 Setting up language analyzers...")
    registry = setup_analyzers()

    # Handle different modes
    if args.list_languages:
        languages = registry.get_all_languages()
        print(f"\nSupported languages ({len(languages)}):")
        for lang, info in languages.items():
            print(f"  • {info.name}: {', '.join(info.extensions)}")
            print(f"    {info.description}")
            print(f"    Features: {', '.join(info.supported_features)}")
        return

    if args.file:
        success = analyze_file_cli(args.file, args.language)
        sys.exit(0 if success else 1)

    if args.cli:
        interactive_cli()
        return

    # Default: try to launch GUI
    if not launch_gui():
        print("\nFalling back to interactive CLI mode...")
        interactive_cli()


if __name__ == "__main__":
    main()
