# PLAIN Programming Language

**PLAIN** = **P**rogramming **L**anguage - **A**ble, **I**ntuitive, and **N**atural

A programming language designed to be approachable without sacrificing competence. PLAIN prioritizes clear thinking over clever syntax, natural readability over terse notation, and honest capability over complex features.

## Status

🔒 **Private Beta** - All Core Features Complete

- ✅ Lexer with full tokenization support
- ✅ Parser with complete AST construction
- ✅ Type system & scope management
- ✅ Runtime/Interpreter with full language support
- ✅ Standard library (core modules)
- ✅ Integrated IDE with debugging support
- ✅ Bidirectional Python ↔ PLAIN code converter
- ✅ Comprehensive documentation and curriculum

## Features

- **Natural syntax** - Reads like plain English
- **Indentation-based blocks** - Python-style syntax
- **Clear type system** - Type inference with prefixes (int, flt, str, bln, lst, tbl)
- **Explicit over implicit** - `var` declares, no `var` assigns
- **No shadowing** - Variables cannot be redeclared in inner scopes
- **Task-based functions** - Clear distinction between procedures and functions
- **Built-in error handling** - `attempt`/`handle`/`ensure` blocks
- **String interpolation** - `v"Hello {name}!"` syntax
- **Serial port I/O** - Full support for RS-232/RS-485 and virtual COM ports
- **Network I/O** - TCP/UDP client and server support for IP-based communication
- **Comprehensive standard library** - 93+ built-in functions for real-world tasks
- **Python ↔ PLAIN converter** - Bidirectional code translation with CLI, GUI, and IDE integration

## Quick Example

```plain
rem: Calculate Fibonacci numbers

task Fibonacci using (intN)
    if intN <= 1
        deliver intN
    
    var a = Fibonacci(intN - 1)
    var b = Fibonacci(intN - 2)
    deliver a + b

task Main()
    var intCount = 10
    
    loop i from 0 to intCount
        var result = Fibonacci(i)
        display(v"Fibonacci({i}) = {result}")
```

## Building

```bash
# Run tests
go test ./...

# Build the interpreter
go build -o plain cmd/plain/main.go

# View tokens from a PLAIN file
go run cmd/plain/main.go -lex examples/hello.plain
```

## Documentation

See the `docs/` directory for complete documentation:

- **[language_spec.md](docs/language_spec.md)** - Complete language specification
- **[implementation_guide.md](docs/implementation_guide.md)** - Implementation roadmap
- **[quick_reference.md](docs/quick_reference.md)** - Syntax cheat sheet
- **[testing_strategy.md](docs/testing_strategy.md)** - Testing approach
- **[session_log.md](docs/session_log.md)** - Development progress tracker
- **[USER-GUIDE.md](docs/user/USER-GUIDE.md)** - Complete user guide

## Project Structure

```
PLAIN/
├── cmd/plain/              # Interpreter executable (Go)
├── internal/
│   ├── lexer/             # Tokenization (✅ complete)
│   ├── token/             # Token definitions (✅ complete)
│   ├── parser/            # AST construction (✅ complete)
│   ├── ast/               # AST node definitions (✅ complete)
│   ├── types/             # Type system (✅ complete)
│   └── runtime/           # Interpreter (✅ complete)
├── plain_ide/              # Integrated IDE (Python/PyQt6)
├── plain_converter/        # Python ↔ PLAIN code converter
│   ├── converter/         # Core conversion engines
│   ├── stdlib_mapping/    # Standard library mapping (JSON)
│   ├── utils/             # Naming, formatting, warning utilities
│   └── tests/             # 238 unit tests
├── examples/               # Example PLAIN programs
├── docs/                   # Complete documentation
└── tests/                  # Interpreter test files
```

## Python ↔ PLAIN Converter

PLAIN includes a bidirectional code converter that translates between Python and PLAIN:

```bash
# Convert Python to PLAIN
python3 -m plain_converter py2plain script.py -o script.plain

# Convert PLAIN to Python
python3 -m plain_converter plain2py program.plain -o program.py

# Batch convert a directory
python3 -m plain_converter py2plain src/ -o plain_src/ --recursive

# Launch the GUI
python3 -m plain_converter --gui
```

The converter handles variables, functions/tasks, control flow, error handling, records/dataclasses, standard library mapping, type annotations, imports/modules, and comments. It is also integrated into the IDE via **Tools → Convert File** (`Ctrl+Shift+C`).

## Design Philosophy

1. **Readability First** - Code should be easily understandable at a glance
2. **Natural Language Orientation** - Syntax should flow like English where possible
3. **Minimal Mental Noise** - Language mechanisms should not distract from thinking
4. **Clear Intent** - The purpose of code should be immediately visible
5. **Explicit Over Implicit** - Clarity over brevity when they conflict

## Target Users

- Students learning programming
- Educators teaching fundamentals
- Developers wanting clarity over cleverness
- Marine electronics applications (creator's domain)

## Implementation Language

Go - chosen for its simplicity, performance, and excellent tooling.

## License

**Proprietary - Private Beta**

This is confidential beta software. See [LICENSE](LICENSE) for terms.

For licensing inquiries: info@fragillidaesoftware.com

## Author

Chuck Finch - Fragillidae Software (c) 2026

---
