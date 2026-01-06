# PLAIN Language Implementation Guide

**For AI Assistant Sessions**

This document provides structured guidance for AI assistants helping implement the PLAIN programming language. Use this to maintain context and consistency across multiple sessions.

---

## Quick Reference

**Language Name:** PLAIN (Programming Language - Able, Intuitive, and Natural)  
**Implementation Language:** Go  
**Architecture:** Interpreter with optional compilation/transpilation  
**Key Files:** See `language_spec.md` for complete specification  

---

## Session Startup Protocol

At the beginning of each AI assistance session, provide this context:

```
I am implementing PLAIN, a programming language designed to be able, intuitive, 
and natural. The complete specification is in language_spec.md. 

Today I want to work on: [SPECIFIC COMPONENT]

Key principles to remember:
- Clarity over cleverness
- Explicit over implicit  
- Natural language keywords
- Teaching-focused design
- No shadowing, no lambdas (v1.0)
```

---

## Implementation Phases

### Phase 1: Lexer (Tokenization)
**Goal:** Convert source code text into tokens

**Key Tasks:**
1. Implement token types for all PLAIN keywords
2. Handle whitespace-significant syntax (Python-style indentation)
3. Recognize literals (strings, numbers, booleans)
4. Handle comments (rem: and note:)
5. Track line and column numbers for error messages

**Prompt Template:**
```
I'm implementing the lexer for PLAIN. I need to tokenize [SPECIFIC ELEMENT].

According to the spec:
- [RELEVANT SPEC SECTION]

Please help me implement [SPECIFIC FUNCTION] that handles [REQUIREMENT].

Key considerations:
- Indentation is significant (like Python)
- String interpolation with v"..." prefix
- Comments: rem: (single line) and note: (multi-line with indentation)
```

**Test Cases Needed:**
- Basic keywords (var, task, if, loop, etc.)
- String literals (regular and interpolated)
- Numbers (integers, floats, scientific notation)
- Operators (all precedence levels)
- Comments (both types)
- Indentation levels
- Error cases (unterminated strings, invalid characters)

---

### Phase 2: Parser (AST Construction)
**Goal:** Build Abstract Syntax Tree from tokens

**Key Tasks:**
1. Implement grammar rules for all language constructs
2. Handle operator precedence correctly
3. Build AST nodes for each construct
4. Provide helpful error messages with location info
5. Handle indentation-based blocks

**Prompt Template:**
```
I'm implementing the parser for PLAIN. I need to parse [CONSTRUCT].

According to the spec:
- [RELEVANT SYNTAX RULES]

The AST node should represent:
- [REQUIRED FIELDS]

Error handling should:
- [SPECIFIC ERROR CASES]

Please help me implement the parsing function for [CONSTRUCT].
```

**Key Constructs to Parse:**
- Variable declarations (var/fxd with optional type)
- Task definitions (with/using/no params)
- Control flow (if/else, choose/choice, loop variants)
- Error handling (attempt/handle/ensure)
- Record definitions (with based on/with composition)
- Import statements (use: assemblies/modules/tasks)
- Expressions (with correct precedence)
- String interpolation

**Test Cases Needed:**
- Each control structure variant
- Nested blocks
- Complex expressions
- Record composition
- Module imports
- Error recovery

---

### Phase 3: Symbol Table & Scope Management
**Goal:** Track variables, tasks, and types with proper scoping

**Key Tasks:**
1. Implement scope stack (module, task, block, parameter)
2. Enforce no-shadowing rule
3. Track variable mutability (parameters are immutable)
4. Validate type constraints for records
5. Track module-level visibility

**Prompt Template:**
```
I'm implementing scope management for PLAIN. I need to handle [SCOPE ASPECT].

PLAIN's scope rules:
- No shadowing allowed
- Four levels: module, task, block, parameter
- Parameters are immutable
- Module variables not global (module-only visibility)

Please help me implement [SPECIFIC FUNCTION] that:
- [REQUIREMENT 1]
- [REQUIREMENT 2]

Error cases to handle:
- [ERROR SCENARIOS]
```

**Critical Rules:**
- Attempting to redeclare existing variable name = ERROR
- Assignment without declaration looks up outer scopes
- Parameters cannot be assigned to
- Module variables only visible within module

---

### Phase 4: Type System
**Goal:** Type checking and inference

**Key Tasks:**
1. Implement type inference from prefixes (int, flt, str, bln, lst, tbl)
2. Validate explicit types (as integer, as string, etc.)
3. Check record field types
4. Validate type constraints in collections (list of, table of)
5. Type checking for operations

**Prompt Template:**
```
I'm implementing type checking for PLAIN. I need to handle [TYPE ASPECT].

Type system rules:
- Inference from prefixes (intX, fltX, strX, blnX, lstX, tblX)
- Explicit types with 'as' keyword
- Records require type compliance
- Collections can be typed or untyped

Please help me implement type checking for [OPERATION/CONSTRUCT].

Should handle:
- [TYPE COMBINATIONS]
- [ERROR CASES]
```

**Type Rules:**
- Prefix inference: `var intCount = 0` → integer type
- Explicit: `var count as integer = 0` → integer type
- Records: all fields typed, composition must have compatible types
- Operations: check operand types match operator requirements

---

### Phase 5: Interpreter (Runtime)
**Goal:** Execute AST with PLAIN semantics

**Key Tasks:**
1. Implement task calls (with/using/no params)
2. Execute control flow (if, choose, loop variants)
3. Handle error system (abort/attempt/handle/ensure)
4. Manage variable storage and scope
5. Implement standard library functions
6. File I/O operations
7. Event system (timers, event loop)

**Prompt Template:**
```
I'm implementing runtime execution for PLAIN. I need to execute [CONSTRUCT].

Runtime requirements:
- [SEMANTIC RULES]
- [MEMORY MANAGEMENT]
- [ERROR HANDLING]

Please help me implement the execution of [CONSTRUCT].

Should handle:
- Normal execution path
- Error cases: [SPECIFIC ERRORS]
- Edge cases: [SPECIFIC EDGES]
```

**Critical Semantics:**
- `task using` must deliver a value
- `task with` cannot deliver
- `abort` throws error with message
- `attempt/handle/ensure` execution flow
- Timer callbacks execute in main thread
- File operations abort on errors

---

### Phase 6: Standard Library
**Goal:** Implement all built-in functions

**Prompt Template:**
```
I'm implementing standard library function: [FUNCTION_NAME]

Function signature: [SIGNATURE]
Behavior: [DESCRIPTION FROM SPEC]

Error cases:
- [ERROR CONDITIONS]

Please provide a Go implementation that:
- Validates inputs
- Aborts with clear messages on errors
- Returns correct type
```

**Implementation Checklist:**
- Console I/O: display, get
- String ops: len, upper, lower, trim, split, join, substring, replace, contains, starts_with, ends_with
- Math basic: abs, sqrt, sqr, pow, round, floor, ceil, min, max
- Math trig: sin, cos, tan, asin, acos, atan, atan2
- Math log: log, log10, log2, exp
- Random: random, random_int, random_choice
- List ops: len, append, insert, remove, pop, sort, reverse, contains
- Table ops: len, keys, values, has_key, remove
- Type conversion: to_string, to_int, to_float, to_bool
- Type checking: is_int, is_float, is_string, is_bool, is_list, is_table, is_null
- File I/O: (see spec for complete list)
- Timer/Events: sleep, create_timer, create_timeout, start_timer, stop_timer, cancel_timer, wait_for_events, run_events, stop_events

---

## Common Implementation Patterns

### Error Messages
PLAIN error messages should be clear and helpful:

```
Bad: "Invalid syntax"
Good: "Expected 'deliver' statement in task 'Calculate' (line 15)"

Bad: "Type error"
Good: "Cannot assign string to variable 'count' of type integer (line 23)"

Bad: "Name error"
Good: "Variable 'counter' already declared in outer scope at line 10 (line 18)"
```

**Error Message Template:**
```
[What went wrong] [where it happened] [(optional: why/how to fix)]
```

### Testing Strategy

For each component, create tests for:
1. **Happy path** - correct usage
2. **Error cases** - invalid input, violations
3. **Edge cases** - boundary conditions
4. **Integration** - component interaction

**Test Prompt Template:**
```
I need tests for [COMPONENT]. 

Please create test cases covering:
1. Valid usage: [EXAMPLES]
2. Error cases: [ERROR CONDITIONS]
3. Edge cases: [BOUNDARY CONDITIONS]

Each test should:
- Have descriptive name
- Test one thing
- Include assertion message
```

---

## Go-Specific Implementation Guidance

### Project Structure
```
plain/
├── cmd/
│   ├── plain/          # Main interpreter executable
│   └── plainc/         # Compiler (future)
├── internal/
│   ├── lexer/          # Tokenization
│   ├── parser/         # AST construction
│   ├── ast/            # AST node definitions
│   ├── types/          # Type system
│   ├── scope/          # Symbol tables
│   ├── runtime/        # Interpreter
│   ├── stdlib/         # Standard library
│   ├── fileio/         # File operations
│   └── events/         # Timer/event system
├── pkg/
│   └── plain/          # Public API
├── examples/           # Example PLAIN programs
├── tests/              # Test suite
└── docs/               # Documentation
```

### Leveraging Go Features

**For Concurrency (Event System):**
```
Use goroutines for timers
Use channels for event coordination
Callbacks execute in main goroutine (no race conditions)
```

**For Error Handling:**
```
PLAIN's abort → Go panic/recover or error returns
attempt/handle → similar to try/catch pattern
```

**For Type Safety:**
```
Use interface{} for PLAIN's dynamic typing
Type assertions with checking
Runtime type validation
```

**Prompt for Go-specific help:**
```
I'm implementing [FEATURE] in Go for PLAIN.

PLAIN semantics: [DESCRIPTION]

What's the idiomatic Go way to handle:
- [SPECIFIC CHALLENGE]
- [ANOTHER CHALLENGE]

Should I use [APPROACH A] or [APPROACH B]?
```

---

## Module System Implementation

### Import Resolution

**Prompt Template:**
```
I'm implementing PLAIN's import system.

Import structure:
use:
    assemblies: [list]
    modules: [list]  
    tasks: [list]

Resolution rules:
- Assemblies are directories
- Modules are .plain files
- Tasks are specific task names
- Only module-scoped, not global

Help me implement:
- Path resolution for [ASSEMBLY/MODULE]
- Namespace management for [IMPORTS]
- Error handling for [MISSING/CIRCULAR]
```

### File Organization
```
Project structure maps to:
- Package = root directory
- Assembly = subdirectory
- Module = .plain file

Example:
MyProject/
├── main.plain          → module "main"
├── io/                 → assembly "io"
│   ├── files.plain     → module "io.files"
│   └── serial.plain    → module "io.serial"
```

---

## REPL Implementation

### Interactive Mode Requirements
1. Read-eval-print loop
2. Multi-line input support (indentation-based)
3. Persistent state across commands
4. Helpful error messages
5. History and editing

**Prompt Template:**
```
I'm implementing the PLAIN REPL.

Features needed:
- Multi-line input detection (indentation)
- State persistence between evaluations
- Error recovery (don't crash on errors)
- [SPECIFIC FEATURE]

Please help me implement [COMPONENT] that:
- [REQUIREMENT]
- [REQUIREMENT]
```

---

## Compilation/Transpilation (Future)

When implementing compilation:

**Target Options:**
1. Go compilation → native binary
2. Transpile to Go → compile with go compiler
3. Transpile to C → compile with gcc
4. Bytecode → custom VM

**Prompt Template:**
```
I'm implementing PLAIN compilation to [TARGET].

PLAIN construct: [SOURCE CODE]
Should compile to: [TARGET EQUIVALENT]

How do I handle:
- [FEATURE MAPPING]
- [OPTIMIZATION]
- [RUNTIME REQUIREMENTS]
```

---

## Debugging and Tooling

### Debug Output
Implement debug mode showing:
- Tokens (lexer output)
- AST (parser output)
- Symbol table (scope state)
- Execution trace (runtime)

**Prompt:**
```
I need debug output for [PHASE].

Should show:
- [INFORMATION 1]
- [INFORMATION 2]

Format should be [HUMAN-READABLE/STRUCTURED]
```

### IDE Support (Future)
- Syntax highlighting definition
- Language server protocol
- Autocomplete
- Error checking

---

## Testing Approach

### Unit Tests
Test each component in isolation:
```
Lexer: token generation
Parser: AST correctness
Type checker: type validation
Runtime: execution behavior
Stdlib: function correctness
```

### Integration Tests
Test component interaction:
```
Lexer → Parser
Parser → Type Checker
Type Checker → Runtime
Full program execution
```

### End-to-End Tests
Real PLAIN programs:
```
examples/hello.plain
examples/fibonacci.plain
examples/file_processing.plain
examples/timer_example.plain
```

**Test Prompt:**
```
Create [UNIT/INTEGRATION/E2E] test for [COMPONENT].

Test scenario: [DESCRIPTION]

Should verify:
- [EXPECTED BEHAVIOR 1]
- [EXPECTED BEHAVIOR 2]

Test should [PASS/FAIL] because: [REASON]
```

---

## Performance Considerations

While PLAIN prioritizes clarity, reasonable performance matters:

**Optimization Opportunities:**
1. String interning for identifiers
2. Constant folding in expressions
3. Tail call optimization (if feasible)
4. Efficient symbol table lookups

**Prompt:**
```
I'm optimizing [COMPONENT] in PLAIN.

Current approach: [DESCRIPTION]
Performance issue: [PROBLEM]

Constraints:
- Must maintain PLAIN semantics
- Cannot break [FEATURE]

Suggestions for optimization?
```

---

## Version Control Strategy

**Commit Message Format:**
```
[COMPONENT] Brief description

- Detail 1
- Detail 2

Addresses: [SPEC_SECTION or ISSUE]
```

**Branch Strategy:**
```
main          → stable releases
develop       → integration
feature/X     → specific features
fix/X         → bug fixes
```

---

## Documentation as You Go

For each implemented feature, document:

1. **Code comments** - Why, not what
2. **Function docs** - Usage and examples  
3. **Test docs** - What's being tested
4. **Architecture docs** - Design decisions

**Documentation Prompt:**
```
I've implemented [FEATURE].

Please help me write:
- Code documentation for [FUNCTION/TYPE]
- Usage examples showing [USE_CASE]
- Architecture notes explaining [DESIGN_DECISION]

Target audience: [MAINTAINERS/USERS]
```

---

## Common Pitfalls to Avoid

### 1. Forgetting PLAIN's Constraints
```
❌ "Let's add lambda functions for convenience"
✓ "PLAIN doesn't have lambdas by design (v1.0)"

❌ "Allow variable shadowing like most languages"
✓ "PLAIN explicitly forbids shadowing for clarity"
```

### 2. Deviating from Spec
```
Always reference language_spec.md
When in doubt, quote the spec
If spec is unclear, ask for clarification
```

### 3. Over-Engineering
```
❌ Complex abstraction for simple feature
✓ Straightforward implementation matching semantics
```

### 4. Inconsistent Error Messages
```
❌ Different error styles across components
✓ Consistent format: [what] [where] [(why/fix)]
```

### 5. Ignoring Teaching Mission
```
❌ Terse error: "Parse error"
✓ Helpful error: "Expected ':' after task name 'Calculate' (line 5)"
```

---

## Session Handoff Template

At the end of each session, document:

```
## Session Summary: [DATE]

### Completed:
- [TASK 1]: [STATUS/NOTES]
- [TASK 2]: [STATUS/NOTES]

### In Progress:
- [TASK]: [CURRENT STATE]
- [TASK]: [NEXT STEPS]

### Issues/Questions:
- [ISSUE]: [DESCRIPTION]
- [QUESTION]: [NEEDS CLARIFICATION]

### Next Session Focus:
- [PRIORITY 1]
- [PRIORITY 2]

### Files Modified:
- [PATH]: [CHANGES]

### Tests Added:
- [TEST FILE]: [COVERAGE]
```

---

## Quick Command Reference

**Start New Component:**
```
"I'm implementing [COMPONENT] for PLAIN. According to language_spec.md, 
it should [BEHAVIOR]. Please help me [SPECIFIC_TASK]."
```

**Debug Issue:**
```
"I'm seeing [PROBLEM] in [COMPONENT]. Expected [BEHAVIOR] but getting 
[ACTUAL]. The spec says [RELEVANT_SECTION]. What's wrong?"
```

**Clarify Spec:**
```
"The spec says [QUOTE] for [FEATURE]. Does this mean [INTERPRETATION_A] 
or [INTERPRETATION_B]? Example: [CODE]"
```

**Review Code:**
```
"Please review this [COMPONENT] implementation. Does it correctly 
implement [SPEC_REQUIREMENT]? Are there edge cases I'm missing?"
```

**Write Tests:**
```
"I need tests for [FEATURE]. Spec says [REQUIREMENT]. Please create 
tests covering [SCENARIOS]."
```

---

## End of Implementation Guide

This guide should keep AI assistants on track across multiple sessions. Always:
1. Reference the spec (language_spec.md)
2. Follow PLAIN's design principles
3. Maintain consistency
4. Test thoroughly
5. Document decisions

Good luck building PLAIN!
