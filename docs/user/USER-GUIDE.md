# PLAIN User Guide

> **Your complete reference for the PLAIN programming language** 📖

PLAIN — **Programming Language: Able, Intuitive, and Natural** — is a teaching-oriented programming language designed to make learning to program accessible and enjoyable. This guide covers everything you need to get started and work effectively with PLAIN.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Your First Program](#your-first-program)
4. [Using the REPL](#using-the-repl)
5. [Using the IDE](#using-the-ide)
6. [Command Line Reference](#command-line-reference)
7. [Language Basics](#language-basics)
8. [Control Flow](#control-flow)
9. [Working with Data](#working-with-data)
10. [Creating Tasks](#creating-tasks)
11. [Error Handling](#error-handling)
12. [Records](#records)
13. [Scope Rules](#scope-rules)
14. [Modules and Imports](#modules-and-imports)
15. [Debugging](#debugging)
16. [Best Practices](#best-practices)
17. [Advanced Console Output](#advanced-console-output)

---

## Introduction

### What is PLAIN?

PLAIN is a programming language built for **learning**. It was designed from the ground up with these principles:

- **Readable syntax** — Code reads almost like English. Keywords like `display`, `deliver`, `attempt`, and `choose` say what they mean.
- **Helpful guardrails** — Features like mandatory type prefixes, no variable shadowing, and immutable parameters prevent common beginner mistakes before they happen.
- **Complete toolset** — PLAIN comes with an interpreter, interactive REPL, and a full-featured IDE with debugging support.

### Who is PLAIN For?

- **Students** learning to program for the first time
- **Teachers** looking for a clean language to teach programming concepts
- **Self-learners** who want a friendly introduction to programming
- **Anyone** who appreciates clear, readable code

### Design Philosophy

PLAIN makes the programmer's **intent** explicit:

| PLAIN                       | Other Languages         | Why?                                           |
| --------------------------- | ----------------------- | ---------------------------------------------- |
| `task Greet with (name)`    | `def greet(name)`       | `with` means "procedure" — no return value     |
| `task Add using (a, b)`     | `def add(a, b)`         | `using` means "function" — must return a value |
| `deliver result`            | `return result`         | Clearer metaphor for producing a value         |
| `fxd PI as float = 3.14`    | `const PI = 3.14`       | `fxd` (fixed) — explicit, memorable            |
| `rem: this is a comment`    | `# this is a comment`   | `rem:` (remark) — no ambiguity                 |
| `attempt / handle / ensure` | `try / catch / finally` | Natural English words                          |

---

## Installation

### Prerequisites

- **Go** 1.21 or later (for the interpreter)
- **Python** 3.10+ with **PyQt6** (for the IDE, optional)

### Building from Source

```bash
# Clone the repository
git clone <repository-url>
cd PLAIN

# Build the interpreter
go build -o plain ./cmd/plain/

# Verify it works
./plain -help

# (Optional) Build the IDE
pip install PyQt6
```

### Verifying Your Installation

```bash
# Start the REPL
./plain
# You should see: "PLAIN Language REPL v0.1"
# Type :quit to exit

# Run a program
echo 'task Main()
    display("Hello!")' > test.plain
./plain test.plain
# Should display: Hello!
```

---

## Your First Program

Create a file called `hello.plain`:

```plain
rem: My first PLAIN program!

task Main()
    display("Hello, World!")
    display("I'm learning PLAIN!")
```

Run it:

```bash
go run ./cmd/plain/ hello.plain
```

Output:

```
Hello, World!
I'm learning PLAIN!
```

Every PLAIN program needs a `task Main()` — that's where execution begins. Everything inside Main must be **indented** (4 spaces recommended).

---

## Using the REPL

The **REPL** (Read-Eval-Print Loop) lets you try PLAIN code interactively without creating a file.

### Starting the REPL

```bash
go run ./cmd/plain/
# Or: go run ./cmd/plain/ -repl
```

### REPL Commands

| Command    | Shortcut | Description                             |
| ---------- | -------- | --------------------------------------- |
| `:help`    | `:h`     | Show available commands                 |
| `:quit`    | `:q`     | Exit the REPL                           |
| `:clear`   | `:c`     | Clear the screen                        |
| `:env`     | `:e`     | Show all current variables              |
| `:history` | `:hist`  | Show command history                    |
| `:reset`   | `:r`     | Reset environment (clear all variables) |

### Example Session

```
PLAIN Language REPL v0.1
Type :help for commands, :quit to exit

>>> var x = 42
>>> display(x * 2)
84
>>> var name = "PLAIN"
>>> display(v"Hello, {name}!")
Hello, PLAIN!
>>> :env
name = "PLAIN"
x = 42
>>> :quit
```

The REPL is great for experimenting with expressions, testing functions, and exploring the language.

---

## Using the IDE

PLAIN includes a full-featured IDE built with PyQt6.

### Launching the IDE

```bash
go run ./cmd/plain-ide/
# Or: python -m plain_ide.main
```

### Keyboard Shortcuts

| Shortcut       | Action               |
| -------------- | -------------------- |
| **File**       |                      |
| `Ctrl+N`       | New file             |
| `Ctrl+O`       | Open file            |
| `Ctrl+Shift+O` | Open folder          |
| `Ctrl+S`       | Save                 |
| `Ctrl+Shift+S` | Save as              |
| `Ctrl+Q`       | Quit                 |
| **Edit**       |                      |
| `Ctrl+Z`       | Undo                 |
| `Ctrl+Shift+Z` | Redo                 |
| `Ctrl+X`       | Cut                  |
| `Ctrl+C`       | Copy                 |
| `Ctrl+V`       | Paste                |
| `Ctrl+F`       | Find                 |
| `Ctrl+H`       | Find and Replace     |
| `Ctrl+,`       | Preferences          |
| **View**       |                      |
| `Ctrl+B`       | Toggle file browser  |
| `` Ctrl+` ``   | Toggle terminal      |
| `Ctrl+D`       | Toggle debug panel   |
| **Run**        |                      |
| `F5`           | Run program          |
| `Ctrl+F5`      | Run in External Term |
| `Shift+F5`     | Stop program         |
| **Debug**      |                      |
| `F6`           | Start debugging      |
| `F9`           | Toggle breakpoint    |
| `F10`          | Step over            |
| `F11`          | Step into            |
| `F8`           | Continue             |
| **Help**       |                      |
| `F1`           | Quick reference      |

### IDE Features

- **Syntax highlighting** with theme support (light and dark themes)
- **File browser** panel for navigating your project
- **Integrated terminal** for running programs
- **Find & Replace** with full search capabilities
- **Debugger** with breakpoints, stepping, and variable inspection
- **Session persistence** — remembers open files and layout
- **Bookmarks** for quick navigation within files

---

## Command Line Reference

```
Usage:
  plain                              Start interactive REPL
  plain <file.plain>                 Run a PLAIN program
  plain -repl, -i                    Start interactive REPL
  plain -lex <file.plain>            Show tokens (lexer output)
  plain -parse <file.plain>          Show AST (parser output)
  plain -analyze <file.plain>        Run semantic analysis
  plain --debug <file.plain>         Run in debug mode
  plain -help, -h                    Show help message
```

### Developer Flags

These flags are useful for understanding how PLAIN processes your code:

| Flag       | Description                                                  |
| ---------- | ------------------------------------------------------------ |
| `-lex`     | Shows how the lexer breaks your code into tokens             |
| `-parse`   | Shows the abstract syntax tree (AST) the parser builds       |
| `-analyze` | Runs semantic analysis to check for errors without executing |
| `--debug`  | Runs in debug mode with breakpoint support                   |

---

## Language Basics

### Variables

Create variables with `var` and constants with `fxd`:

```plain
var age = 25              rem: Mutable variable
var name = "Alice"        rem: Can be changed later
fxd PI as float = 3.14   rem: Constant — cannot be changed
```

### Type System

PLAIN has six data types:

| Type    | Keyword   | Prefix | Examples           |
| ------- | --------- | ------ | ------------------ |
| Integer | `integer` | `int`  | `42`, `-7`, `0`    |
| Float   | `float`   | `flt`  | `3.14`, `-0.5`     |
| String  | `string`  | `str`  | `"hello"`, `""`    |
| Boolean | `boolean` | `bln`  | `true`, `false`    |
| List    | `list`    | `lst`  | `[1, 2, 3]`        |
| Table   | `table`   | `tbl`  | `{"key": "value"}` |

### Type Inference with Prefixes

PLAIN can infer a variable's type from its name prefix:

```plain
var intCount = 0          rem: Integer (int prefix)
var fltPrice = 9.99       rem: Float (flt prefix)
var strName = "Alice"     rem: String (str prefix)
var blnReady = true       rem: Boolean (bln prefix)
var lstItems = [1, 2, 3]  rem: List (lst prefix)
var tblData = {}          rem: Table (tbl prefix)
```

### Explicit Types

Use `as` for explicit type declaration:

```plain
var score as integer = 95
var temperature as float = 72.5
var greeting as string = "Hello"
```

### Assignment Operators

```plain
x = 10        rem: Assignment
x += 5        rem: Add and assign (x = x + 5)
x -= 3        rem: Subtract and assign
x *= 2        rem: Multiply and assign
x /= 4        rem: Divide and assign
s &= "!"     rem: Concatenate and assign (strings)
```

### Swapping Values

You can swap the values of two variables using the `swap` statement:

```plain
var a = 1
var b = 2
swap a, b
rem: Now a is 2, b is 1
```

### Operators

**Arithmetic**: `+`, `-`, `*`, `/`, `%` (modulo), `**` (power)

**Comparison**: `==`, `!=`, `<`, `>`, `<=`, `>=`

**Logical**: `and`, `or`, `not`

**String**: `&` (concatenation)

### Strings

```plain
rem: Concatenation
var greeting = "Hello" & ", " & "World!"

rem: Interpolation
var name = "Alice"
display(v"Hello, {name}!")       rem: Hello, Alice!

rem: Escape sequences in display
display("Line 1\nLine 2")       rem: Note: \n handled at display level
```

---

## Control Flow

### If / Else

```plain
if temperature > 80
    display("It's hot!")
else
    display("Nice weather.")
```

PLAIN uses **nested if/else** for multiple branches (no `elif`):

```plain
if score >= 90
    display("A")
else
    if score >= 80
        display("B")
    else
        if score >= 70
            display("C")
        else
            display("F")
```

### Choose / Choice / Default

For matching a value against specific options:

```plain
choose day
    choice "Monday"
        display("Start of week")
    choice "Friday"
        display("Almost weekend!")
    default
        display("Regular day")
```

### Loops

**Counting loop:**

```plain
loop i from 1 to 10
    display(i)

loop i from 10 to 0 step -2
    display(i)
```

**Collection loop (for-each):**

```plain
var fruits = ["apple", "banana", "cherry"]
loop fruit in fruits
    display(fruit)
```

**Loop control:**

```plain
loop i from 1 to 100
    if i > 10
        exit           rem: Break out of the loop
    if i % 2 == 0
        continue       rem: Skip to next iteration
    display(i)
```

---

## Working with Data

### Lists

```plain
var colors = ["red", "green", "blue"]

rem: Access by index (0-based)
display(colors[0])             rem: "red"

rem: Modify
append(colors, "yellow")       rem: Add to end
insert(colors, 1, "orange")   rem: Insert at position
remove(colors, "green")        rem: Remove by value
var item = pop(colors, 0)      rem: Remove by index, return item

rem: Query
display(len(colors))           rem: Length
display(contains(colors, "blue"))  rem: true/false

rem: Transform
sort(colors)                   rem: Sort in place
reverse(colors)                rem: Reverse in place
```

### Tables

```plain
var person = {"name": "Alice", "age": 30, "city": "Portland"}

rem: Access
display(person["name"])         rem: "Alice"

rem: Modify
person["email"] = "alice@test.com"   rem: Add/update
remove(person, "city")               rem: Remove

rem: Query
display(has_key(person, "email"))    rem: true
var allKeys = keys(person)           rem: List of keys
var allVals = values(person)         rem: List of values
```

### Type Conversion

```plain
var s = "42"
var n = to_int(s)              rem: String → Integer
var f = to_float(s)            rem: String → Float
var str = to_string(42)        rem: Any → String
var b = to_bool(1)             rem: Any → Boolean

rem: Type checking
display(is_int(42))            rem: true
display(is_string("hi"))      rem: true
display(is_list([1,2]))       rem: true
```

---

## Creating Tasks

### Procedures (with)

Procedures perform actions but don't return values:

```plain
rem: No parameters
task SayHello()
    display("Hello!")

rem: With parameters
task Greet with (name)
    display("Hello, " & name & "!")

rem: Calling
SayHello()
Greet("Alice")
```

### Functions (using / deliver)

Functions compute and return values:

```plain
task Add using (a, b)
    deliver a + b

task IsPositive using (n)
    deliver n > 0

rem: Using return values
var sum = Add(5, 3)           rem: 8
if IsPositive(-5)
    display("Positive!")
```

### Parameter Rules

- Parameters declared with `with` or `using` are **immutable** — you cannot modify them inside the task
- To work with a modified version, copy to a local variable first
- Tasks can be defined in any order in the file

---

## Error Handling

### Attempt / Handle / Ensure

```plain
attempt
    rem: Code that might fail
    var result = risky_operation()
    display(result)
handle
    rem: Runs if an error occurs
    display("Something went wrong!")
ensure
    rem: Always runs (cleanup)
    display("Done.")
```

### Abort

Signal custom errors with `abort`:

```plain
task ValidateAge using (age)
    if age < 0
        abort "Age cannot be negative"
    if age > 150
        abort "Age seems unrealistic"
    deliver age
```

Errors from `abort` are caught by `handle` blocks in the calling code.

---

## Records

### Defining Records

```plain
record Student:
    name as string
    age as integer = 18
    grade as string = "A"
```

### Creating and Using Records

```plain
var s1 = Student(name: "Alice", age: 20, grade: "A")
var s2 = Student(name: "Bob")   rem: age=18, grade="A" (defaults)

display(s1.name)                rem: "Alice"
s2.grade = "B"                  rem: Modify a field
```

### Records in Collections

```plain
var students = [s1, s2]
loop s in students
    display(s.name & ": " & s.grade)
```

---

## Scope Rules

PLAIN has four scope levels:

1. **Global scope** — Variables defined at the top level of a file
2. **Task scope** — Variables defined inside a task
3. **Block scope** — Variables defined inside `if`, `loop`, `attempt`, etc.
4. **Parameter scope** — Parameters passed to tasks

### Key Rules

- **No shadowing** — You cannot create a variable with the same name as one in an outer scope. This prevents accidental mistakes.
- **Parameters are immutable** — You can read but not modify task parameters.
- **Variables are accessible** in the scope where they're declared and all inner scopes.

```plain
var x = 10           rem: Global scope

task Example with (y)
    rem: Can read x (global) and y (parameter)
    var z = x + y    rem: Task scope
    if z > 15
        var w = z    rem: Block scope
        display(w)
    rem: w is not accessible here (block scope ended)
```

---

## Modules and Imports

### Project Structure

```
my_project/
  main.plain              (entry point)
  utils.plain             (utility module)
  math/
    geometry.plain         (math.geometry module)
    statistics.plain       (math.statistics module)
```

### Import Syntax

```plain
use:
    assemblies:
        math                         rem: Import whole directory
    modules:
        math.geometry                rem: Import specific file
    tasks:
        math.statistics.Average      rem: Import specific task
```

### Access Patterns

| Import Level | Access Pattern               |
| ------------ | ---------------------------- |
| Assembly     | `math.geometry.CircleArea()` |
| Module       | `geometry.CircleArea()`      |
| Task         | `CircleArea()`               |

---

## Debugging

### IDE Debugger

The PLAIN IDE includes a visual debugger:

1. **Set breakpoints** — Click in the gutter or press `F9`
2. **Start debugging** — Press `F6`
3. **Step through** — `F10` (step over), `F11` (step into)
4. **Continue** — `F8` to run to the next breakpoint
5. **Inspect** — The debug panel shows current variables and their values

### Command-Line Debugging

```bash
go run ./cmd/plain/ --debug myprogram.plain
go run ./cmd/plain/ --debug myprogram.plain --breakpoints=5,10,15
```

---

## Best Practices

### Naming Conventions

- **Variables**: Use type prefixes for clarity: `intCount`, `strName`, `lstItems`
- **Constants**: Use UPPER_CASE: `fxd MAX_SIZE as integer = 100`
- **Tasks**: Use PascalCase: `CalculateAverage`, `DisplayReport`
- **Record types**: Use PascalCase: `record StudentRecord:`

### Code Organization

- Put `task Main()` near the top of your file
- Group related tasks together
- Use `rem:` comments to explain **why**, not just **what**
- Keep tasks short and focused — one task, one job

### Common Patterns

**Accumulating in loops** — always use `total = total + x`:

```plain
var total = 0
loop i from 1 to 10
    total = total + i    rem: Reliable accumulation
```

**Guard clauses** — validate early with `abort`:

```plain
task ProcessAge using (age)
    if age < 0
        abort "Invalid age"
    rem: ... rest of the logic
```

**Parallel lists** — use matching indices for related data:

```plain
var names = ["Alice", "Bob", "Charlie"]
var scores = [95, 87, 92]
loop i from 0 to len(names) - 1
    display(names[i] & ": " & scores[i])
```

---

---

## Advanced Console Output

### Controlling Float Precision

You can control the number of decimal places displayed for floating-point numbers using `set_float_precision(n)`. This affects all subsequent `display()` calls and string conversions.

```plain
set_float_precision(2)      rem: Show 2 decimal places
display(1.0/3.0)            rem: "0.33"

set_float_precision(-1)     rem: Reset to default (remove trailing zeros)
display(1.0/3.0)            rem: "0.3333333333333333"
```

### Writing Without Newlines

The standard `display()` function always prints a newline at the end. For advanced output like progress bars, you can write directly to standard output:

```plain
rem: Open stdout in append mode
var stdout = open("/dev/stdout", "a")

rem: Write without newline
write(stdout, "Loading...")
sleep(1000)
write(stdout, " Done!\n")

close(stdout)
```

### Overwriting Lines (Progress Bars)

Use the carriage return character `chr(13)` to move the cursor back to the start of the line:

```plain
var stdout = open("/dev/stdout", "a")
var total = 100

loop i from 0 to total
    rem: chr(13) moves cursor to start
    var bar = chr(13) & "Progress: " & i & "%"
    write(stdout, bar)
    sleep(50)

write(stdout, "\n")
close(stdout)
```

---

## Further Reading

- **[TUTORIAL.md](TUTORIAL.md)** — Step-by-step lessons with exercises
- **[LANGUAGE-REFERENCE.md](LANGUAGE-REFERENCE.md)** — Complete language specification
- **[STDLIB.md](STDLIB.md)** — Every built-in function documented
- **[CURRICULUM.md](CURRICULUM.md)** — Educator's guide for teaching PLAIN

Happy coding with PLAIN! 🎉
