# PLAIN Language Quick Reference

**Version:** 1.0  
**For:** AI Implementation Assistance

---

## Core Principles

1. **Clarity over cleverness**
2. **Explicit over implicit**
3. **Natural language keywords**
4. **No shadowing** (variables cannot be redeclared in inner scopes)
5. **No lambdas** (v1.0 - use named tasks)
6. **Indentation-based blocks** (like Python)

---

## Keywords at a Glance

```
task            deliver         abort
swap            with            using
on              var             fxd
as              if              then
else            choose          choice
default         loop            from
to              in              exit
continue        attempt         handle
ensure          use:            assemblies:
modules:        tasks:          record
rem:            note:           int/integer
flt/float       str/string      bln/boolean
lst/list        tbl/table       of
null            and             or
not             true            false
```

---

## Task Signatures

```
task Name()                          rem: no params, no return
task Name with (param1, param2)      rem: params, no return (procedure)
task Name using (input1, input2)     rem: params, must deliver (function)
```

**Rules:**
- `with` = procedure (side effects)
- `using` = function (must `deliver`)
- Parameters are immutable

---

## Variable Declaration

```
rem: Type inference with prefix
var intCount = 0
var fltPrice = 9.99
var strName = "text"
var blnFlag = true
var lstItems = [1, 2, 3]
var tblData = {"key": "value"}

rem: Explicit typing
var count as integer = 0
var price as float = 9.99
var name as string = "text"

rem: Typed collections
var numbers as list of integer = [1, 2, 3]
var scores as table of string to integer = {"alice": 95}

rem: Constants
fxd PI as float = 3.14159
fxd MAX_SIZE as integer = 100
```

---

## Control Flow

### If/Else (binary only)
```
if condition
    statements
else
    statements

rem: Single-line
if condition then statement
if condition then statement else statement
```

### Choose/Choice (3+ options)
```
choose value
    choice "option1"
        statements
    choice "option2"
        statements
    default
        statements
```

### Loop (all variants)
```
loop                        rem: infinite
loop condition              rem: while-style
loop i from 1 to 10        rem: counting
loop item in collection     rem: for-each

exit                        rem: break out of loop
continue                    rem: skip to next iteration
```

---

## Error Handling

```
attempt
    risky_operation()
handle "specific error message"
    handle_specific()
handle error
    handle_generic(error)
ensure
    cleanup()    rem: always runs
```

**Rules:**
- `handle` blocks evaluated in order
- First match wins
- `ensure` always executes
- If callback aborts, timer stops

---

## Records (Custom Types)

```
record Person:
    name as string              rem: required (first field)
    age as integer = 0          rem: optional with default
    email as string = ""

rem: Create instance (all fields named)
var person = Person(name: "Chuck", age: 63, email: "chuck@example.com")

rem: Access fields
var userName = person.name
person.age = 64
```

### Record Composition
```
record FullInfo:
    based on Contact            rem: includes all fields, preserves required
    with Address                rem: includes all fields, makes optional
    phone as string = ""

rem: 'based on' = keeps requirements
rem: 'with' = makes all optional
```

---

## Modules and Imports

```
use:
    assemblies:
        io                       rem: makes assembly available
    modules:
        utils                    rem: import from root
        io.files                 rem: import from assembly
    tasks:
        utils.FormatDate         rem: specific task

rem: Usage
FormatDate()                     rem: imported task (direct)
utils.Log("message")             rem: module task (qualified)
io.serial.Connect()              rem: assembly path (full)
```

---

## Operators

### Precedence (high to low)
1. `**` (exponentiation, right-associative)
2. `*` `/` `//` `%` (mult, div, int-div, mod)
3. `+` `-` (add, subtract)
4. `&` (string concat)
5. `==` `!=` `<` `>` `<=` `>=` (comparison)
6. `not` (logical NOT)
7. `and` (logical AND)
8. `or` (logical OR)

### Assignment Shortcuts
```
counter += 1
total -= 5
value *= 2
text &= " more"

rem: Swap Values
swap a, b
```

---

## String Operations

```
rem: Regular string
var str = "Hello"

rem: Interpolated string (v prefix)
var msg = v"Hello {name}, you are {age} years old"

rem: Concatenation
var full = "Hello" & " " & "World"
```

---

## Comments

### Single-line Comments
```
rem: This is a single-line comment
var intCount = 10    rem: Inline comment
```

### Multi-line Comments
```
note:
    This is a multi-line comment block.
    All indented lines following note: are part of the comment.
    The comment ends when indentation returns to the same level.

var intCount = 10    rem: This is not part of the note block
```

**Rules:**
- `rem:` for single-line comments
- `note:` for multi-line comment blocks
- Multi-line comments use indentation to define scope
- Comment ends when a line returns to the same or lesser indentation as the `note:` line

---


## Standard Library (Selected)

### Console
```
display(value)              rem: output to console
get(prompt)                 rem: input from user
```

### String
```
len(str) upper(str) lower(str) trim(str)
split(str, delim) join(lst, sep) 
substring(str, start, end) replace(str, old, new)
contains(str, search) starts_with(str, prefix) ends_with(str, suffix)
chr(code) ord(str)
```

### Math
```
abs(n) sqrt(n) sqr(n) pow(base, exp)
round(n) floor(n) ceil(n) min(a,b) max(a,b)
sin(a) cos(a) tan(a) asin(v) acos(v) atan(v) atan2(y,x)
log(n) log10(n) log2(n) exp(n)
random() random_int(min, max) random_choice(lst)
```

### List
```
len(lst) append(lst, item) insert(lst, idx, item)
remove(lst, item) pop(lst, idx)
sort(lst) reverse(lst) contains(lst, item)
```

### Table
```
len(tbl) keys(tbl) values(tbl)
has_key(tbl, key) remove(tbl, key)
```

### Type Conversion
```
to_string(v) to_int(v) to_float(v) to_bool(v)
```

### Type Checking
```
is_int(v) is_float(v) is_string(v) is_bool(v)
is_list(v) is_table(v) is_null(v)
```

---

## File I/O

### Simple Operations
```
rem: Text files
content = read_file(path)
write_file(path, content)
append_file(path, content)
lstLines = read_lines(path)
write_lines(path, lstLines)

rem: Binary files
data = read_binary(path)
write_binary(path, data)
append_binary(path, data)
```

### Handle-based
```
rem: Modes: "r" "w" "a" "rb" "wb" "ab"
file = open(path, mode)
content = read(file)
line = read_line(file)
bytes = read_bytes(file, count)
write(file, content)
write_line(file, line)
close(file)
```

### File System
```
file_exists(path) delete_file(path)
rename_file(old, new) copy_file(src, dest)
file_size(path)
dir_exists(path) create_dir(path)
delete_dir(path) list_dir(path)
join_path(part1, part2) split_path(path)
get_extension(path) absolute_path(path)
```

---

## Events and Timers

### Basic Timing
```
sleep(milliseconds)              rem: blocking pause
time()                           rem: current timestamp (ms)
date()                           rem: current date table
```

### Timers
```
timer = create_timer(interval, callback)     rem: repeating
timeout = create_timeout(delay, callback)    rem: one-shot
start_timer(timer)
stop_timer(timer)
cancel_timer(timer)
```

### Event Loop
```
wait_for_events()                rem: run until done
run_events(duration)             rem: run for time
stop_events()                    rem: stop from callback
```

### Callbacks
```
task OnTick()                    rem: simple
task OnTick with (timer, elapsed)    rem: with info
```

---

## Scope Rules

### Four Levels
1. **Module** - file-level, not global
2. **Task** - function-level
3. **Block** - control structure level
4. **Parameter** - task parameters (immutable)

### Key Rules
- **No shadowing** - cannot redeclare in inner scope
- `var name = value` - declares new variable
- `name = value` - assigns to existing variable
- Inner scopes can access and mutate outer variables
- Block variables don't leak outside

---

## Common Patterns

### Safe File Operation
```
task SafeRead using (path)
    var file = null
    
    attempt
        file = open(path, "r")
        var content = read(file)
        deliver content
    handle error
        display(v"Error: {error}")
        deliver null
    ensure
        if not is_null(file)
            close(file)
```

### Timer with Auto-Stop
```
var count = 0

task OnTick with (timer, elapsed)
    count += 1
    display(v"Count: {count}")
    
    if count >= 10
        cancel_timer(timer)
        stop_events()

task Main()
    var timer = create_timer(1000, OnTick)
    start_timer(timer)
    wait_for_events()
```

### Record with Composition
```
record Contact:
    name as string
    email as string = ""

record Employee:
    based on Contact           rem: name required
    with Department            rem: all dept fields optional
    salary as float = 0.0

var emp = Employee(
    name: "Chuck",
    email: "chuck@example.com",
    salary: 75000.0
)
```

---

## Error Messages Format

```
[What went wrong] [where] [(optional: why/fix)]

Examples:
"Expected 'deliver' statement in task 'Calculate' (line 15)"
"Variable 'counter' already declared in outer scope at line 10 (line 18)"
"Cannot assign string to variable 'count' of type integer (line 23)"
"File not found: data.txt"
```

---

## Implementation Reminders

### For Go Implementation
- Use goroutines for timer system
- Callbacks execute in main event loop (no races)
- Indentation tracking for parser
- Symbol table with scope stack
- Runtime type checking with interface{}

### Testing Priorities
1. Lexer: all token types
2. Parser: each construct + precedence
3. Type system: inference + validation
4. Runtime: execution + errors
5. Stdlib: each function
6. Integration: full programs

### Debug Modes
- Show tokens (lexer)
- Show AST (parser)
- Show symbol table (scope)
- Trace execution (runtime)

---

## Quick Checklist for New Feature

- [ ] Update spec if needed
- [ ] Implement lexer support
- [ ] Implement parser support
- [ ] Update AST nodes
- [ ] Implement type checking
- [ ] Implement runtime behavior
- [ ] Add standard library functions (if applicable)
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Add example programs
- [ ] Document in code
- [ ] Update this quick reference

---

**Remember:** When in doubt, consult `language_spec.md` - it's the source of truth!
