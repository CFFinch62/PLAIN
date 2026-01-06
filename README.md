# PLAIN Programming Language

**PLAIN** = **P**rogramming **L**anguage - **A**ble, **I**ntuitive, and **N**atural

A programming language designed to be approachable without sacrificing competence. PLAIN prioritizes clear thinking over clever syntax, natural readability over terse notation, and honest capability over complex features.

## Status

🚧 **In Development** - Phase 2 (Parser) Complete

- ✅ Lexer with full tokenization support
- ✅ Parser with complete AST construction
- ⏳ Type system & scope management (next phase)
- ⏳ Runtime/Interpreter
- ⏳ Standard library

## Features

- **Natural syntax** - Reads like plain English
- **Indentation-based blocks** - Python-style syntax
- **Clear type system** - Type inference with prefixes (int, flt, str, bln, lst, tbl)
- **Explicit over implicit** - `var` declares, no `var` assigns
- **No shadowing** - Variables cannot be redeclared in inner scopes
- **Task-based functions** - Clear distinction between procedures and functions
- **Built-in error handling** - `attempt`/`handle`/`ensure` blocks
- **String interpolation** - `v"Hello {name}!"` syntax

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

## Project Structure

```
plain/
├── cmd/plain/          # Interpreter executable
├── internal/
│   ├── lexer/         # Tokenization (✅ complete)
│   ├── token/         # Token definitions (✅ complete)
│   ├── parser/        # AST construction (✅ complete)
│   ├── ast/           # AST node definitions (✅ complete)
│   ├── types/         # Type system (⏳ next)
│   └── runtime/       # Interpreter (⏳ planned)
├── examples/          # Example PLAIN programs
├── docs/              # Complete documentation
└── tests/             # Test files
```

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

[To be determined]

## Author

Chuck - January 2026

---

**Current Phase:** Parser (Complete)
**Next Phase:** Type System & Scope Management
**Test Coverage:** Lexer 82.8%, Parser 100% (all tests passing)

