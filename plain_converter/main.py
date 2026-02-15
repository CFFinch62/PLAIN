#!/usr/bin/env python3
"""
Python ↔ PLAIN Code Converter - CLI Entry Point

Usage:
    plain-convert <direction> <input> [options]

Directions:
    python-to-plain (p2p)    Convert Python code to PLAIN
    plain-to-python (plain2py)  Convert PLAIN code to Python
"""

import argparse
import sys
import os
from pathlib import Path

from plain_converter import __version__


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="plain-convert",
        description="Bidirectional code converter between Python and PLAIN",
        epilog="Examples:\n"
               "  plain-convert p2p input.py -o output.plain\n"
               "  plain-convert plain2py input.plain -o output.py\n"
               "  plain-convert p2p src/ -o plain_src/ --recursive\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parser.add_argument(
        "--gui",
        action="store_true",
        default=False,
        help="Launch standalone graphical interface",
    )

    parser.add_argument(
        "direction",
        nargs="?",
        default=None,
        choices=["python-to-plain", "p2p", "plain-to-python", "plain2py"],
        help="Conversion direction",
    )

    parser.add_argument(
        "input",
        nargs="?",
        default=None,
        help="Input file or directory path",
    )

    # Output options
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument(
        "-o", "--output",
        help="Output file or directory path",
    )
    output_group.add_argument(
        "--stdout",
        action="store_true",
        default=False,
        help="Write output to stdout (default if no -o specified)",
    )
    output_group.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Overwrite existing files without prompting",
    )

    # Conversion options
    conv_group = parser.add_argument_group("Conversion Options")
    conv_group.add_argument(
        "--add-type-prefixes",
        action="store_true",
        default=False,
        help="Add type prefixes to PLAIN variables (e.g., intCount, strName)",
    )
    conv_group.add_argument(
        "--prefer-choose",
        action="store_true",
        default=False,
        help="Prefer choose/choice over if/elif for 3+ branches",
    )
    conv_group.add_argument(
        "--preserve-comments",
        action="store_true",
        default=True,
        help="Preserve all comments (default: true)",
    )
    conv_group.add_argument(
        "--no-format",
        action="store_true",
        default=False,
        help="Disable auto-formatting of output code",
    )

    # Processing options
    proc_group = parser.add_argument_group("Processing Options")
    proc_group.add_argument(
        "-r", "--recursive",
        action="store_true",
        default=False,
        help="Process directories recursively",
    )
    proc_group.add_argument(
        "--pattern",
        default=None,
        help="File pattern to match (default: *.py or *.plain)",
    )
    proc_group.add_argument(
        "--exclude",
        default=None,
        help="Exclude files matching pattern",
    )

    # Output control
    out_ctrl = parser.add_argument_group("Output Control")
    out_ctrl.add_argument(
        "-v", "--verbose",
        action="store_true",
        default=False,
        help="Verbose output",
    )
    out_ctrl.add_argument(
        "-q", "--quiet",
        action="store_true",
        default=False,
        help="Suppress non-error output",
    )
    out_ctrl.add_argument(
        "--no-warnings",
        action="store_true",
        default=False,
        help="Suppress conversion warnings",
    )
    out_ctrl.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Fail on unsupported features instead of warning",
    )

    # Other options
    other_group = parser.add_argument_group("Other Options")
    other_group.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Show what would be converted without writing files",
    )
    other_group.add_argument(
        "--stats",
        action="store_true",
        default=False,
        help="Show conversion statistics after completion",
    )

    return parser


def normalize_direction(direction: str) -> str:
    """Normalize direction aliases to full names."""
    aliases = {
        "p2p": "python-to-plain",
        "plain2py": "plain-to-python",
    }
    return aliases.get(direction, direction)


def get_default_pattern(direction: str) -> str:
    """Get the default file pattern for a conversion direction."""
    if direction == "python-to-plain":
        return "*.py"
    return "*.plain"


def get_output_extension(direction: str) -> str:
    """Get the output file extension for a conversion direction."""
    if direction == "python-to-plain":
        return ".plain"
    return ".py"


def collect_input_files(input_path: str, pattern: str, recursive: bool,
                        exclude: str | None = None) -> list[Path]:
    """Collect input files from a path (file or directory)."""
    path = Path(input_path)

    if path.is_file():
        return [path]

    if not path.is_dir():
        print(f"Error: '{input_path}' is not a file or directory", file=sys.stderr)
        sys.exit(3)

    if recursive:
        files = sorted(path.rglob(pattern))
    else:
        files = sorted(path.glob(pattern))

    if exclude:
        files = [f for f in files if not f.match(exclude)]

    if not files:
        print(f"Warning: No files matching '{pattern}' found in '{input_path}'",
              file=sys.stderr)

    return files


def convert_file(input_path: Path, direction: str, args: argparse.Namespace) -> str:
    """Convert a single file and return the converted code."""
    source_code = input_path.read_text(encoding="utf-8")

    if direction == "python-to-plain":
        # Import here to avoid circular imports
        from plain_converter.converter.python_to_plain import PythonToPlainConverter
        converter = PythonToPlainConverter(
            add_type_prefixes=args.add_type_prefixes,
            prefer_choose=args.prefer_choose,
            preserve_comments=args.preserve_comments,
            strict=args.strict,
        )
    else:
        from plain_converter.converter.plain_to_python import PlainToPythonConverter
        converter = PlainToPythonConverter(
            preserve_comments=args.preserve_comments,
            strict=args.strict,
        )

    result = converter.convert(source_code)

    # Check for errors
    if not result.success:
        raise RuntimeError(
            f"Conversion failed: {'; '.join(result.errors)}"
        )

    # Display warnings unless suppressed
    if not args.no_warnings and not args.quiet:
        for warning in result.warnings:
            print(f"  Warning: {warning}", file=sys.stderr)

    # Display stats if requested
    if args.stats and not args.quiet and result.stats:
        for key, val in result.stats.items():
            print(f"  Stat: {key} = {val}", file=sys.stderr)

    return result.code


def determine_output_path(input_path: Path, output_arg: str | None,
                          direction: str) -> Path | None:
    """Determine the output path for a converted file."""
    if output_arg is None:
        return None  # Will write to stdout

    output = Path(output_arg)
    ext = get_output_extension(direction)

    if output.is_dir() or output_arg.endswith("/"):
        output.mkdir(parents=True, exist_ok=True)
        return output / (input_path.stem + ext)

    return output


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)

    # Launch GUI mode
    if args.gui:
        from plain_converter.gui import run_gui
        run_gui()
        return 0

    # Validate required positional args for CLI mode
    if args.direction is None or args.input is None:
        parser.error("the following arguments are required: direction, input"
                     " (or use --gui for graphical mode)")

    direction = normalize_direction(args.direction)
    pattern = args.pattern or get_default_pattern(direction)
    input_files = collect_input_files(args.input, pattern, args.recursive,
                                      args.exclude)

    if not input_files:
        return 1

    converted_count = 0
    error_count = 0
    warning_count = 0

    for input_path in input_files:
        if args.verbose and not args.quiet:
            print(f"Converting: {input_path}", file=sys.stderr)

        if args.dry_run:
            output_path = determine_output_path(input_path, args.output, direction)
            target = str(output_path) if output_path else "stdout"
            print(f"  Would convert: {input_path} -> {target}")
            converted_count += 1
            continue

        try:
            result = convert_file(input_path, direction, args)
            output_path = determine_output_path(input_path, args.output, direction)

            if output_path is None or args.stdout:
                print(result)
            else:
                if output_path.exists() and not args.overwrite:
                    print(f"  Skipping: {output_path} already exists "
                          f"(use --overwrite to replace)", file=sys.stderr)
                    continue

                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(result, encoding="utf-8")

                if not args.quiet:
                    print(f"  Converted: {input_path} -> {output_path}",
                          file=sys.stderr)

            converted_count += 1

        except Exception as e:
            print(f"  Error converting {input_path}: {e}", file=sys.stderr)
            error_count += 1
            if args.strict:
                return 1

    if args.stats and not args.quiet:
        print(f"\nConversion Statistics:", file=sys.stderr)
        print(f"  Files processed: {len(input_files)}", file=sys.stderr)
        print(f"  Successfully converted: {converted_count}", file=sys.stderr)
        print(f"  Errors: {error_count}", file=sys.stderr)

    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

