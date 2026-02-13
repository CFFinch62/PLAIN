# PLAIN Language Specification

**PLAIN - Programming Language - Able, Intuitive, and Natural**

**Version:** 0.1 (Draft)  
**Date:** January 5, 2026  
**Status:** In Development

---

## Mission Statement

PLAIN is a programming language designed to be approachable without sacrificing competence. It prioritizes clear thinking over clever syntax, natural readability over terse notation, and honest capability over complex features. PLAIN is for getting real work done with straightforward, understandable code.

## Design Philosophy

PLAIN is designed with the following principles:

1. **Readability First** - Code should be easily understandable at a glance
2. **Natural Language Orientation** - Syntax should flow like English where possible
3. **Minimal Mental Noise** - Language mechanisms should not distract from thinking
4. **Clear Intent** - The purpose of code should be immediately visible
5. **Explicit Over Implicit** - Clarity over brevity when they conflict

---

## Core Keywords

### Task Definitions

Tasks are the fundamental units of executable code. There are two types:

- **Procedures** (side effects): `task name()` or `task name with (params)`
- **Functions** (return values): `task name using (inputs)`

**Syntax:**
```
task TaskName()
    rem: Parameterless procedure
    
task TaskName with (param1, param2)
    rem: Procedure with parameters - performs side effects
    
task TaskName using (input1, input2)
    rem: Function with inputs - must deliver a result
    deliver result
```

**Rules:**
- Tasks using `using` keyword MUST include a `deliver` statement
- Tasks using `with` keyword or no parameters do NOT deliver values
- Task names should use PascalCase by convention

---

## Task Control Flow

### Deliver
Returns a value from a task defined with `using`. Can appear multiple times for early returns.

**Syntax:**
```
deliver expression
```

**Example:**
```
task CalculateTax using (amount)
    if amount < 0
        abort "Amount cannot be negative"
    
    if amount == 0
        deliver 0
    
    taxAmount = amount * 0.08
    deliver taxAmount
```

### Abort
Exits a task with an error. Always requires an error message.

**Syntax:**
```
abort "error message"
```

**Example:**
```
task UpdateRecord with (id, data)
    if id < 0
        abort "Invalid ID: must be positive"
    
    if not database.isConnected()
        abort "Database connection unavailable"
    
    database.update(id, data)
```

---

## Variables and Constants

### Variable Declaration

**Syntax - Type Inference with Prefix:**
```
var <prefix><name> = <value>
```

**Syntax - Explicit Type:**
```
var <name> as <type> = <value>
```

**Type Prefixes:**
- `int` - Integer
- `flt` - Float
- `str` - String
- `bln` - Boolean
- `lst` - List (mixed types)
- `tbl` - Table/Dictionary (mixed types)

**Full Type Names:**
- `integer`
- `float`
- `string`
- `boolean`
- `list`
- `table`

**Examples:**
```
rem: Type inference with prefix
var intAge = 63
var fltTemperature = 98.6
var strName = "Chuck"
var blnIsReady = true
var lstNumbers = [1, 2, 3]
var tblScores = {"alice": 95, "bob": 87}

rem: Explicit typing
var age as integer = 63
var temperature as float = 98.6
var name as string = "Chuck"
var isReady as boolean = true
```

### Typed Collections

Collections can be constrained to specific types:

**Syntax:**
```
var <name> as list of <type> = <value>
var <name> as table of <keytype> to <valuetype> = <value>
```

**Examples:**
```
rem: Homogeneous list - integers only
var numbers as list of integer = [1, 2, 3]

rem: Heterogeneous list - any types
var lstMixed = [1, "hello", 3.14, true]

rem: Typed table
var scores as table of string to integer = {"alice": 95, "bob": 87}

rem: Mixed table
var tblData = {"count": 42, "name": "test", "value": 3.14}
```

### Constants

**Syntax:**
```
fxd <name> as <type> = <value>
```

**Examples:**
```
fxd pi as float = 3.14159
fxd maxUsers as integer = 100
fxd companyName as string = "Acme Corp"
```

**Rules:**
- Constants cannot be modified after initialization
- Keyword `fxd` is short for "fixed"
- Type specification follows same rules as variables

### Null Values

The `null` keyword represents the absence of a value.

**Example:**
```
var result = null
if customer == null
    abort "Customer not found"
```

---

## Operators

### Arithmetic Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `+` | Addition | `a + b` |
| `-` | Subtraction | `a - b` |
| `*` | Multiplication | `a * b` |
| `/` | Division (float result) | `a / b` |
| `//` | Integer division | `a // b` |
| `%` | Modulo | `a % b` |
| `**` | Exponentiation | `a ** b` |

### Comparison Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `==` | Equals | `a == b` |
| `!=` | Not equals | `a != b` |
| `<` | Less than | `a < b` |
| `>` | Greater than | `a > b` |
| `<=` | Less than or equal | `a <= b` |
| `>=` | Greater than or equal | `a >= b` |

### Logical Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `and` | Logical AND | `a and b` |
| `or` | Logical OR | `a or b` |
| `not` | Logical NOT | `not a` |

### Assignment Operators

| Operator | Description | Example | Equivalent |
|----------|-------------|---------|------------|
| `=` | Assignment | `a = 5` | - |
| `+=` | Add and assign | `a += 5` | `a = a + 5` |
| `-=` | Subtract and assign | `a -= 5` | `a = a - 5` |
| `*=` | Multiply and assign | `a *= 5` | `a = a * 5` |
| `/=` | Divide and assign | `a /= 5` | `a = a / 5` |
| `%=` | Modulo and assign | `a %= 5` | `a = a % 5` |
| `&=` | Concatenate and assign | `s &= "x"` | `s = s & "x"` |

### String Concatenation

The `&` operator concatenates strings.

**Example:**
```
var greeting = "Hello" & " " & "World"
var message = "User " & strName & " logged in"
```

### String Interpolation

Strings prefixed with `v` support variable interpolation using `{}`.

**Syntax:**
```
v"text {variable} more text"
```

**Examples:**
```
var strName = "Chuck"
var intAge = 63

rem: Regular string - no interpolation
var literal = "Hello {strName}"
rem: Output: "Hello {strName}"

rem: Interpolated string
var greeting = v"Hello {strName}, you are {intAge} years old"
rem: Output: "Hello Chuck, you are 63 years old"

rem: Expressions allowed
var report = v"Tax: {amount * 0.08}"
var formatted = v"Total: {total // 100} dollars and {total % 100} cents"
```

---

## Operator Precedence

PLAIN evaluates expressions using standard mathematical precedence rules. Operators at the same precedence level are evaluated left-to-right, except for exponentiation which is right-associative.

### Precedence Table

From highest to lowest precedence:

| Level | Operators | Description | Associativity |
|-------|-----------|-------------|---------------|
| 1 | `**` | Exponentiation | Right |
| 2 | `*` `/` `//` `%` | Multiplication, Division, Integer Division, Modulo | Left |
| 3 | `+` `-` | Addition, Subtraction | Left |
| 4 | `&` | String Concatenation | Left |
| 5 | `==` `!=` `<` `>` `<=` `>=` | Comparison | Left |
| 6 | `not` | Logical NOT | Right |
| 7 | `and` | Logical AND | Left |
| 8 | `or` | Logical OR | Left |

### Precedence Examples

**Arithmetic operations:**
```
var result = 2 + 3 * 4        rem: 14 (not 20 - multiplication first)
var result = 10 - 5 - 2       rem: 3 (left-to-right: (10 - 5) - 2)
var result = 10 / 5 / 2       rem: 1.0 (left-to-right: (10 / 5) / 2)
```

**Exponentiation (right-associative):**
```
var result = 2 ** 3 ** 2      rem: 512 (right-to-left: 2 ** (3 ** 2))
var result = 4 ** 3           rem: 64
var result = 2 ** 3 * 4       rem: 32 (exponentiation before multiplication)
```

**Mixed operations:**
```
var result = 2 + 3 * 4 ** 2   rem: 50 (4**2=16, 3*16=48, 2+48=50)
var result = 10 // 3 * 2      rem: 6 (left-to-right: (10 // 3) * 2)
var result = 10 % 3 + 1       rem: 2 (10 % 3 = 1, then 1 + 1 = 2)
```

**String concatenation:**
```
var result = "Hello" & " " & "World"    rem: "Hello World"
var result = "Value: " & to_string(42)  rem: "Value: 42"
```

**Comparison operations:**
```
var result = 5 + 3 > 7        rem: true (8 > 7)
var result = 10 / 2 == 5      rem: true (5.0 == 5)
var result = 3 * 4 != 11      rem: true (12 != 11)
```

**Logical operations:**
```
var result = not false        rem: true
var result = true and false   rem: false
var result = true or false    rem: true
var result = not true or false    rem: false (not has higher precedence)
```

**Complex expressions:**
```
var result = 5 > 3 and 10 < 20           rem: true (both comparisons true)
var result = 2 + 3 == 5 or 10 / 2 == 4   rem: true (first comparison true)
var result = not 5 > 10 and 3 < 7        rem: true
```

### Parentheses Override Precedence

Use parentheses `()` to explicitly control evaluation order:

```
var result = (2 + 3) * 4      rem: 20 (parentheses force addition first)
var result = 2 ** (3 ** 2)    rem: 512 (same as default, but explicit)
var result = (10 - 5) - 2     rem: 3 (same as default left-to-right)
var result = 10 - (5 - 2)     rem: 7 (forces right evaluation first)
```

**Best practice:** Use parentheses for clarity even when not strictly needed:
```
rem: Both equivalent, but second is clearer
var result = a * b + c * d
var result = (a * b) + (c * d)
```

### Short-Circuit Evaluation

Logical operators `and` and `or` use short-circuit evaluation:

**`and` stops at first false:**
```
if file_exists(path) and read_file(path) != ""
    rem: read_file only called if file_exists returns true
```

**`or` stops at first true:**
```
if useCache or computeExpensiveValue()
    rem: computeExpensiveValue only called if useCache is false
```

**Practical example:**
```
task SafeDivide using (numerator, denominator)
    if denominator != 0 and numerator / denominator > 10
        rem: Division only happens if denominator != 0
        deliver true
    else
        deliver false
```

### Common Precedence Mistakes

**Mistake 1: Forgetting multiplication precedence**
```
rem: Wrong mental model
var area = length + width * 2    rem: adds length to (width * 2)

rem: Correct
var area = (length + width) * 2  rem: multiply sum by 2
```

**Mistake 2: Chaining comparisons**
```
rem: This doesn't work as expected
if 0 < x < 10    rem: ERROR - invalid syntax

rem: Correct
if x > 0 and x < 10
```

**Mistake 3: Logical NOT scope**
```
rem: Not what you might expect
if not x == 5    rem: same as (not x) == 5, probably wrong

rem: Correct
if not (x == 5)  rem: or use !=
if x != 5
```

**Mistake 4: Exponentiation associativity**
```
rem: Be careful with exponents
var result = 2 ** 3 ** 2    rem: 512, not 64!

rem: Make intent clear
var result = (2 ** 3) ** 2  rem: 64
var result = 2 ** (3 ** 2)  rem: 512
```

---

## Control Structures

All control structures use indentation to define blocks (Python-style).

### Conditional: If/Else

Binary decisions only. For multiple choices, use `choose/choice`.

**Syntax:**
```
if condition
    statements
else
    statements
```

**Single-line form:**
```
if condition then statement
if condition then statement else statement
```

**Examples:**
```
if temperature > 100
    cool()
else
    heat()

if isValid then process() else abort "Invalid data"

rem: No elseif - use choose for multiple conditions
```

**Rules:**
- `if` is for binary decisions only
- No `elseif` keyword exists
- Multiple conditions should use `choose/choice` instead

### Conditional: Choose/Choice

Multi-way branching for three or more alternatives.

**Syntax:**
```
choose expression
    choice value1
        statements
    choice value2
        statements
    default
        statements
```

**Example:**
```
choose grade
    choice "A"
        celebrate()
    choice "B"
        smile()
    choice "C"
        study()
    default
        panic()
```

**Rules:**
- Use for three or more alternatives
- `default` case is optional but recommended
- Each `choice` can have multiple statements via indentation

### Loops

Single `loop` keyword with multiple forms, inspired by Go's approach.

#### Infinite Loop

**Syntax:**
```
loop
    statements
```

**Example:**
```
loop
    work()
    if done
        exit
```

#### Conditional Loop (While-style)

**Syntax:**
```
loop condition
    statements
```

**Example:**
```
loop temperature < 100
    heat()
    measure()
```

#### Counting Loop

**Syntax:**
```
loop variable from start to end
    statements

loop variable from start to end step increment
    statements
```

**Examples:**
```
loop i from 1 to 10
    process(i)

loop count from 100 to 1
    countdown(count)

loop i from 0 to 100 step 5
    display(i)    rem: prints 0, 5, 10, 15, ..., 100

loop x from 10 to 1 step -2
    display(x)    rem: prints 10, 8, 6, 4, 2
```

**Notes:**
- The `step` keyword is optional; default step is 1 (or -1 if start > end)
- Step can be positive or negative
- Loop includes both start and end values (inclusive range)

#### Collection Iteration

**Syntax:**
```
loop variable in collection
    statements
```

**Example:**
```
loop item in lstItems
    if item == null
        continue
    process(item)

loop key in tblScores
    print(v"{key}: {tblScores[key]}")
```

### Loop Control

| Keyword | Description | Usage |
|---------|-------------|-------|
| `exit` | Exit the loop immediately | Loop control only |
| `continue` | Skip to next iteration | Loop control only |

**Examples:**
```
loop i from 1 to 100
    if i % 15 == 0
        continue
    if i > 50
        exit
    work(i)

loop i from 0 to 100 step 10
    if i == 50
        continue    rem: skip 50
    display(i)      rem: prints 0, 10, 20, 30, 40, 60, 70, 80, 90, 100
```

**Rules:**
- `exit` terminates the loop entirely
- `continue` skips remaining statements and goes to next iteration
- Both keywords only work within loops
- For nested loops, they affect the innermost loop only

---

## Comments

### Single-line Comments

**Syntax:**
```
rem: comment text
```

**Example:**
```
var intAge = 63    rem: User's age in years
rem: This initializes the counter
var intCounter = 0
```

### Multi-line Comments

**Syntax:**
```
note:
    comment text
    spanning multiple lines
```

**Example:**
```
note:
    This task calculates the shipping cost based on
    weight, distance, and service level.
    Returns the cost in dollars.

task CalculateShipping using (weight, distance, service)
    rem: implementation here
```

**Rules:**
- `note:` keyword starts the comment block
- Indentation defines the comment content
- Comment ends when indentation returns to original level
- Consistent with PLAIN's indentation-based block structure

---

## Reserved Keywords

The following keywords are reserved and cannot be used as identifiers:

**Task-related:**
- `task`
- `with`
- `using`
- `deliver`
- `abort`

**Variables:**
- `var`
- `fxd`
- `as`
- `null`

**Types:**
- `integer`, `int`
- `float`, `flt`
- `string`, `str`
- `boolean`, `bln`
- `list`, `lst`
- `table`, `tbl`
- `of`, `to`

**Control Flow:**
- `if`, `then`, `else`
- `choose`, `choice`, `default`
- `loop`, `from`, `to`, `step`, `in`
- `exit`, `continue`

**Error Handling:**
- `attempt`
- `handle`
- `ensure`

**Modules and Imports:**
- `use:`
- `assemblies:`
- `modules:`
- `tasks:`

**Custom Types:**
- `record`
- `based`
- `on`

**Operators (word form):**
- `and`
- `or`
- `not`

**Comments:**
- `rem:`
- `note:`

---

## Naming Conventions

### Recommended Conventions

- **Tasks:** PascalCase - `CalculateTax`, `UpdateRecord`
- **Variables:** camelCase or with type prefix - `userName` or `strUserName`
- **Constants:** PascalCase or UPPER_CASE - `MaxRetries` or `MAX_RETRIES`

### Rules

- Identifiers must start with a letter or underscore
- Can contain letters, digits, and underscores
- Cannot be a reserved keyword
- Case-sensitive

---

## Code Organization

### Indentation

- Use consistent indentation (recommended: 4 spaces)
- Indentation defines block scope
- No explicit block terminators (no `end`, `}`, etc.)

### Example of Proper Indentation

```
task ProcessOrder using (orderId)
    if orderId < 0
        abort "Invalid order ID"
    
    order = database.fetch(orderId)
    
    if order == null
        deliver null
    
    loop item in order.items
        if item.quantity > 0
            total += item.price * item.quantity
    
    deliver total
```

---

## Error Handling

PLAIN uses an `attempt/handle/ensure` structure for managing errors thrown by `abort`.

### Attempt Block

The `attempt` keyword begins a block of code that might abort with an error.

**Syntax:**
```
attempt
    statements
handle error_pattern
    statements
ensure
    statements
```

### Handle Block

The `handle` keyword catches errors. Multiple handlers can be specified and are checked in order from top to bottom.

**Syntax - Generic handler:**
```
handle error
    statements
```

**Syntax - Custom error name:**
```
handle err
    statements
```

**Syntax - With type:**
```
handle err as string
    statements
```

**Syntax - Specific error matching:**
```
handle "exact error message"
    statements
```

### Ensure Block

The `ensure` keyword (optional) specifies code that always runs, whether the attempt succeeds or fails.

**Rules:**
- `ensure` block executes regardless of success, error, or early return
- Typically used for cleanup (closing files, releasing resources)
- Cannot be used without an `attempt` block
- `ensure` runs after `handle` blocks

### Complete Example

```
task ProcessFile using (filename)
    attempt
        data = readFile(filename)
        result = parse(data)
        deliver result
    handle "File not found"
        log(v"File {filename} does not exist")
        deliver null
    handle "Permission denied"
        log(v"Access denied for {filename}")
        deliver null
    handle err
        log(v"Unexpected error: {err}")
        abort "Failed to process file"
    ensure
        closeResources()
```

### Error Matching Rules

- Handlers are evaluated in the order they appear
- First matching handler executes, then execution continues after the attempt block
- String literals match exact error messages from `abort`
- Generic handlers (without a string literal) catch any error not matched by previous handlers
- If no handler matches, the error propagates to the calling task
- Error variables can be typed for comparison with constants

### Using Error Constants

```
note:
    Define common error constants for system errors

fxd FILE_NOT_FOUND as string = "File not found"
fxd PERMISSION_DENIED as string = "Permission denied"
fxd INVALID_INPUT as string = "Invalid input"

task SafeRead using (filename)
    attempt
        data = readFile(filename)
        deliver data
    handle err as string
        if err == FILE_NOT_FOUND
            deliver ""
        else if err == PERMISSION_DENIED
            log("Access issue")
            deliver ""
        else
            abort err
```

### No Re-throwing

PLAIN does not support re-throwing errors. Once an error is caught in a `handle` block, it must be resolved:
- Fix the problem and continue
- Log the error and deliver a safe value
- Call `abort` with a NEW error message (not re-throwing the original)

This design prevents the anti-pattern of catching errors without properly handling them.

---

## Modules and Imports

PLAIN organizes code into a three-tier hierarchy designed to scale from simple scripts to complex applications while maintaining clarity and supporting visual development tools.

### Code Organization Hierarchy

**Package** - The main project (root directory)
- Contains the project configuration and entry point
- Top-level organizational unit

**Assembly** - A subdirectory grouping related modules
- Organizes modules by feature or domain (e.g., `io`, `data`, `network`)
- Optional for small projects where all modules reside in the root

**Module** - A single `.plain` file
- Contains related tasks, variables, and constants
- The fundamental unit of code reusability

### Example Project Structure

```
MyProject/                  (Package)
├── main.plain             (Module in root)
├── utils.plain            (Module in root)
├── io/                    (Assembly)
│   ├── files.plain        (Module)
│   ├── network.plain      (Module)
│   └── serial.plain       (Module)
└── data/                  (Assembly)
    ├── parser.plain       (Module)
    └── validator.plain    (Module)
```

### Import Syntax

The `use:` section appears at the top of a file and specifies dependencies with three optional subsections.

**Syntax:**
```
use:
    assemblies:
        assembly_name
        
    modules:
        module_name
        assembly.module_name
        
    tasks:
        module.TaskName
        assembly.module.TaskName
```

### Import Levels

**Assembly Level** - Makes an assembly available
```
use:
    assemblies:
        io
        data
```
- All modules within the assembly become accessible
- Modules must still be explicitly imported or referenced with full path
- Useful for making large subsystems available

**Module Level** - Imports entire module
```
use:
    modules:
        utils
        io.files
        data.parser
```
- All tasks in the module become accessible via `module.TaskName`
- Module from root: just the module name
- Module from assembly: `assembly.module` notation

**Task Level** - Imports specific tasks
```
use:
    tasks:
        io.files.ReadBinary
        io.files.WriteBinary
        utils.FormatDate
```
- Imported tasks callable directly without prefix
- Provides finest control over namespace
- Automatically makes parent module and assembly available

### Complete Examples

**Minimal import (tasks only):**
```
use:
    tasks:
        io.files.ReadBinary
        utils.FormatDate

task Main()
    rem: Direct call - imported as task
    data = ReadBinary("input.dat")
    timestamp = FormatDate()
```

**Mixed granularity:**
```
use:
    assemblies:
        data
    
    modules:
        io.files
    
    tasks:
        utils.FormatDate

task ProcessData()
    rem: Direct call - imported as task
    timestamp = FormatDate()
    
    rem: Module prefix - imported as module
    content = io.files.ReadBinary("data.bin")
    
    rem: Full path - only assembly imported
    result = data.parser.ParseJSON(content)
```

**Module-level import:**
```
use:
    modules:
        io.files
        data.parser

task Main()
    raw = io.files.ReadBinary("input.dat")
    parsed = data.parser.ParseJSON(raw)
```

### Import Rules

1. **Location:** The `use:` section must appear at the top of the file, before any task definitions, variables, or constants

2. **Optional sections:** Any combination of `assemblies`, `modules`, and `tasks` subsections is valid. Omit sections you don't need.

3. **No aliasing:** PLAIN does not support import aliasing. If name collisions occur, import at the module level and use qualified names.

4. **Explicit dependencies:** Only explicitly imported items are available. This makes dependencies clear and supports compiler optimization.

5. **Transitive availability:** Importing a task automatically makes its module and assembly available for qualified access.

### Namespace Control

The three-tier system provides precise namespace control:

**Prevent collisions:**
```
use:
    modules:
        io.files
        network.files

task Main()
    rem: No collision - both modules accessible with prefix
    localData = io.files.ReadBinary("local.dat")
    remoteData = network.files.Download("url")
```

**Minimize imports:**
```
use:
    tasks:
        io.files.ReadBinary

task QuickScript()
    rem: Only one task imported, minimal footprint
    data = ReadBinary("file.dat")
```

**Clear dependencies:**
```
use:
    assemblies:
        io
    
    modules:
        data.parser
    
    tasks:
        utils.Log

rem: Reading this, you know:
rem: - We use the io assembly broadly
rem: - We specifically need the parser module
rem: - We only need Log from utils
```

### Benefits for Development Tools

This structure explicitly supports visual development environments:

- **Assembly view:** High-level architecture diagram showing major subsystems
- **Module view:** Detailed component relationships within assemblies  
- **Task view:** Specific dependency graphs between individual tasks
- **Import analysis:** Exact dependency chains for any file
- **Dead code detection:** Unused assemblies/modules/tasks easily identified

### Project Organization Requirements

PLAIN encourages (and tooling may enforce) a minimal organizational structure:

**Small projects:**
- All modules in root directory acceptable
- Encouraged to use assemblies once you have 5+ modules

**Medium/Large projects:**
- Standard assemblies recommended: `io`, `data`, `network`, `ui`
- Domain-specific assemblies as needed
- New developers guided to use proper structure from the start

This "forced organization" teaches good architectural habits and ensures projects remain maintainable as they grow.

---

## Custom Types (Records)

PLAIN uses records to define structured data types with named fields. Records are essentially typed tables with schemas that provide type safety and documentation while maintaining the flexibility of PLAIN's table type.

### Record Definition

**Syntax:**
```
record RecordName:
    fieldName as type
    fieldName as type = defaultValue
```

**Rules:**
- The first field is always required (no default value)
- All subsequent fields must have default values
- Default values ensure data integrity even when fields are omitted
- Field names must be unique within a record

**Example:**
```
record Person:
    name as string              rem: required - first field
    age as integer = 0          rem: optional with default
    email as string = ""
    active as boolean = true
```

### Creating Record Instances

**Syntax - All fields named explicitly:**
```
var instanceName = RecordName(fieldName: value, fieldName: value)
```

**Examples:**
```
rem: Provide all fields
var person = Person(
    name: "Chuck",
    age: 63,
    email: "chuck@example.com",
    active: true
)

rem: Only required field - others use defaults
var minimal = Person(name: "Alice")

rem: Mix of required and some optional fields
var partial = Person(name: "Bob", age: 45)
```

**Rules:**
- All field names must be explicitly specified (no positional arguments)
- The required field (first field) must always be provided
- Optional fields use their default values if omitted
- Field order in construction doesn't matter

### Accessing Record Fields

**Syntax - Dot notation (recommended):**
```
value = instance.fieldName
instance.fieldName = value
```

**Syntax - Table notation (also valid):**
```
value = instance["fieldName"]
instance["fieldName"] = value
```

**Example:**
```
var userName = person.name
var userAge = person["age"]

person.email = "newemail@example.com"
person["active"] = false
```

### Record Composition

Records can be composed from other records using `based on` and `with` keywords, providing precise control over data integrity requirements.

**Syntax:**
```
record ComposedRecord:
    based on RecordName
    with RecordName
    additionalField as type = defaultValue
```

**Semantics:**

- **`based on RecordName`** - Includes ALL fields from RecordName and PRESERVES required field status
- **`with RecordName`** - Includes ALL fields from RecordName but makes them ALL optional (even if originally required)

**Example:**
```
record Contact:
    name as string              rem: required
    email as string = ""

record Address:
    street as string            rem: required
    city as string = ""
    zip as string = ""

record Employment:
    company as string           rem: required
    title as string = ""

rem: Strict composition - multiple required fields
record StrictEmployee:
    based on Contact            rem: 'name' required
    based on Address            rem: 'street' required  
    based on Employment         rem: 'company' required
    phone as string = ""

rem: Valid - provides all three required fields
var emp = StrictEmployee(
    name: "Chuck",
    street: "123 Main St",
    company: "Acme Corp",
    phone: "555-1234"
)

rem: Relaxed composition - only one required field
record FlexibleContact:
    based on Contact            rem: 'name' required
    with Address                rem: 'street' becomes optional
    with Employment             rem: 'company' becomes optional
    phone as string = ""

rem: Valid - only name required
var contact = FlexibleContact(name: "Alice")

rem: Can still provide optional fields
var detailed = FlexibleContact(
    name: "Bob",
    street: "456 Oak Ave",
    company: "Tech Inc",
    email: "bob@example.com"
)
```

### Composition Rules

1. **Multiple `based on` allowed:** Each adds its required fields to the composed record
2. **Multiple `with` allowed:** Each adds fields as optional, regardless of original status
3. **Mix `based on` and `with`:** Provides fine-grained control over data integrity
4. **Field name conflicts prohibited:** If two records share a field name, they cannot be composed
5. **Order matters:** Fields from earlier records override later ones (though conflicts are errors)

**Field Conflict Example:**
```
record Contact:
    name as string
    id as integer = 0

record Product:
    name as string              rem: conflict!
    price as float = 0.0

record Invalid:
    based on Contact
    with Product                rem: ERROR at compile/interpret time

rem: Error message:
rem: "Cannot compose records: field 'name' exists in both Contact and Product"
```

### Records vs Untyped Tables

PLAIN allows both typed records and untyped tables for maximum flexibility.

**Typed Record:**
```
record Person:
    name as string
    age as integer = 0

var person as Person = Person(name: "Chuck", age: 63)
rem: Type-checked, documented schema
```

**Untyped Table:**
```
var config = {"debug": true, "port": 8080, "timeout": 30}
rem: Flexible dictionary, no schema enforcement
```

**When to use each:**

- **Records:** When data structure is known and consistent (domain objects, API responses, database rows)
- **Tables:** When structure is dynamic or ad-hoc (configuration, JSON parsing, temporary data)

### Type Validation

**Interpreted mode (REPL/scripts):**
- Type checking occurs at runtime
- Clear error messages when types don't match
- Field requirements validated at record creation

**Compiled mode:**
- Type checking at compile time where possible
- Field requirements validated statically
- Better performance, earlier error detection

**Example validation:**
```
record Person:
    name as string
    age as integer = 0

rem: Runtime/compile error - wrong type
var person = Person(name: "Chuck", age: "sixty-three")
rem: Error: Field 'age' expects integer, got string

rem: Runtime/compile error - missing required field
var person = Person(age: 63)
rem: Error: Required field 'name' not provided
```

### Complete Example

```
note:
    Define employee records with varying levels of detail

record BasicInfo:
    employeeId as string        rem: required
    name as string = ""
    email as string = ""

record Department:
    deptName as string          rem: required
    manager as string = ""
    location as string = ""

record Salary:
    amount as float             rem: required
    currency as string = "USD"
    effectiveDate as string = ""

rem: Full employee requires all core data
record Employee:
    based on BasicInfo          rem: employeeId required
    based on Department         rem: deptName required
    based on Salary             rem: amount required
    startDate as string = ""
    active as boolean = true

rem: Contractor has flexible department assignment
record Contractor:
    based on BasicInfo          rem: employeeId required
    with Department             rem: deptName optional
    with Salary                 rem: amount optional
    endDate as string = ""

task CreateEmployee using (id, name, dept, salary)
    var emp = Employee(
        employeeId: id,
        name: name,
        deptName: dept,
        amount: salary
    )
    deliver emp

task CreateContractor using (id, name)
    var contractor = Contractor(
        employeeId: id,
        name: name
    )
    deliver contractor
```

---

## Scope Rules

PLAIN uses clear, predictable scoping rules that prevent surprises and make code easy to understand. Variables are visible within their defining scope and all nested scopes, but not outside.

### Scope Levels

PLAIN has four scope levels:

1. **Module Scope** - Variables declared at the file level
2. **Task Scope** - Variables declared within a task
3. **Block Scope** - Variables declared within control structures (if, loop, attempt, etc.)
4. **Parameter Scope** - Task parameters

### Module Scope

Variables and constants declared at the top level of a file (outside any task) are visible throughout that module only.

**Example:**
```
rem: Module-level declarations
var moduleCounter = 0
fxd MODULE_NAME = "utils"

task IncrementCounter()
    moduleCounter += 1    rem: can access module-level variable
    deliver moduleCounter

task GetModuleName using ()
    deliver MODULE_NAME   rem: can access module-level constant
```

**Rules:**
- Module-level variables are NOT global - only visible within their own module
- Other modules cannot directly access these variables
- To share data between modules, use task parameters and return values
- Module-level variables persist for the lifetime of the program

### Task Scope

Variables declared within a task are visible only within that task and its nested blocks.

**Example:**
```
task ProcessData using (input)
    var result = 0
    var lstItems = parseInput(input)
    
    loop item in lstItems
        result += item    rem: can access task-level 'result'
    
    deliver result

task OtherTask()
    var x = result    rem: ERROR - 'result' not visible here
```

**Rules:**
- Task-level variables exist from declaration until task completion
- Not visible to other tasks
- Not visible outside the task

### Block Scope

Variables declared inside control structures (if, loop, attempt, choose) are visible only within that block and its nested blocks.

**Example:**
```
task Example()
    var outer = 10
    
    if outer > 5
        var inner = 20
        print(inner)       rem: OK - inner is visible here
        print(outer)       rem: OK - outer is visible here
    
    print(outer)           rem: OK - outer still visible
    print(inner)           rem: ERROR - inner not visible outside if block

task LoopExample()
    var total = 0
    
    loop i from 1 to 10
        var squared = i * i    rem: squared only exists in loop
        total += squared       rem: can access outer 'total'
    
    print(total)               rem: OK
    print(squared)             rem: ERROR - squared not visible here
```

**Rules:**
- Block variables are created when the block executes
- Block variables are destroyed when the block exits
- Block variables don't leak outside their block
- Nested blocks can access variables from outer blocks

### Parameter Scope

Task parameters are immutable (read-only) variables visible throughout the task.

**Example:**
```
task Calculate using (value)
    var result = value * 2    rem: can read parameter
    value = 10                rem: ERROR - cannot modify parameter
    deliver result

task Process with (id, data)
    print(id)                 rem: can read parameter
    id = id + 1               rem: ERROR - cannot modify parameter
    updateDatabase(id, data)
```

**Rules:**
- Parameters are read-only throughout the task
- To modify a value, assign it to a local variable first
- Parameters exist for the entire task execution

**Workaround for mutable values:**
```
task Process with (value)
    var mutableValue = value    rem: copy to local variable
    mutableValue += 10          rem: can modify local copy
    deliver mutableValue
```

### Variable Declaration vs Assignment

PLAIN distinguishes between declaring new variables and assigning to existing ones.

**Declaration (creates new variable):**
```
var variableName = value
```

**Assignment (mutates existing variable):**
```
variableName = value
```

**Example:**
```
task Example()
    var counter = 0           rem: declaration - creates new variable
    
    loop i from 1 to 10
        counter = counter + 1 rem: assignment - mutates existing variable
    
    print(counter)            rem: 10
```

### No Shadowing

PLAIN does not allow variable shadowing. Once a variable name is used in an outer scope, it cannot be redeclared in an inner scope.

**Invalid - shadowing attempt:**
```
task Example()
    var counter = 0
    
    loop i from 1 to 10
        var counter = i       rem: ERROR - 'counter' already declared
```

**Error message:**
```
Variable 'counter' already declared in outer scope at line X
```

**Valid - use different name:**
```
task Example()
    var counter = 0
    
    loop i from 1 to 10
        var loopValue = i     rem: OK - different name
        counter = counter + loopValue
```

**Valid - mutate existing:**
```
task Example()
    var counter = 0
    
    loop i from 1 to 10
        counter = i           rem: OK - assignment to existing variable
    
    print(counter)            rem: 10
```

### Scope Access Rules

**Inner scopes can access outer scopes:**
```
task Example()
    var outer = 10
    
    if true
        var inner = 20
        print(outer)          rem: OK - can read outer variable
        outer = 30            rem: OK - can mutate outer variable
    
    print(outer)              rem: 30 - was mutated by inner scope
    print(inner)              rem: ERROR - inner not visible
```

**Outer scopes cannot access inner scopes:**
```
task Example()
    if true
        var temp = 10
    
    print(temp)               rem: ERROR - temp not visible here
```

**Sibling scopes are isolated:**
```
task Example()
    if condition1
        var value1 = 10
    
    if condition2
        var value2 = 20
        print(value1)         rem: ERROR - value1 not visible here
```

### Variable Lifetime

**Module-level variables:**
- Created when program starts or module is loaded
- Destroyed when program ends
- Persist across multiple task calls

**Task-level variables:**
- Created when task is called
- Destroyed when task returns
- Do not persist between task calls

**Block-level variables:**
- Created when block is entered
- Destroyed when block exits
- Recreated on each iteration (for loops)

**Example of variable lifetime:**
```
var moduleCount = 0           rem: persists for entire program

task IncrementCount()
    var taskCount = 0         rem: created fresh each call
    taskCount += 1
    moduleCount += 1
    
    print(v"Task: {taskCount}, Module: {moduleCount}")

rem: First call prints: "Task: 1, Module: 1"
rem: Second call prints: "Task: 1, Module: 2"
rem: Third call prints: "Task: 1, Module: 3"
```

### Best Practices

1. **Declare variables in the narrowest scope possible**
   - Makes code easier to understand
   - Reduces accidental mutations
   - Improves memory usage

2. **Use descriptive names to avoid confusion**
   - Since shadowing is not allowed, good names prevent conflicts
   - `totalPrice` vs `itemPrice` vs `finalPrice`

3. **Copy parameters if you need to modify them**
   ```
   task Process with (value)
       var workingValue = value
       workingValue += 10
       deliver workingValue
   ```

4. **Initialize module variables carefully**
   - They persist for the entire program
   - Consider thread safety if concurrency is added later

---

## Standard Library

PLAIN includes a comprehensive standard library of built-in tasks that are always available without imports. All standard library tasks use lowercase names with underscores for multi-word names.

### Console I/O

**display(value)**
- Outputs a value to the console
- Automatically converts non-string values to strings
- Adds newline after output

**get(prompt)**
- Displays prompt and reads a line of input from the user
- Returns the input as a string
- Trailing newline is removed

**clear()**
- Clears the console screen and moves cursor to top-left
- Uses ANSI escape codes

**text_at(x, y, text)**
- Positions cursor at column x, row y (1-based coordinates)
- Prints the text at that position
- Useful for creating text-based UIs and dashboards

**text_color(foreground [, background])**
- Sets text color for subsequent output
- Valid colors: "black", "red", "green", "yellow", "blue", "magenta", "cyan", "white", "default"
- Use "default" to reset colors

**draw_line(x, y, length, direction [, char])**
- Draws a horizontal or vertical line
- Direction: "h", "horizontal", "v", or "vertical"
- Optional char parameter to customize line character

**draw_box(x, y, width, height [, title])**
- Draws a bordered box using Unicode box-drawing characters
- Optional title displayed centered in top border
- Useful for creating panels and UI elements

**Examples:**
```
display("Hello, World!")
display(42)
display(v"Result: {total}")

var name = get("Enter your name: ")
var age = to_int(get("Enter your age: "))

rem: Text graphics examples
clear()
text_color("cyan")
draw_box(1, 1, 60, 10, "Dashboard")
text_color("default")
text_at(3, 3, "Temperature: 72.5°F")
draw_line(3, 5, 50, "h")
```

### String Operations

**len(str)** - Returns the length of a string
```
var length = len("Hello")    rem: 5
```

**upper(str)** - Converts string to uppercase
```
var loud = upper("hello")    rem: "HELLO"
```

**lower(str)** - Converts string to lowercase
```
var quiet = lower("HELLO")   rem: "hello"
```

**trim(str)** - Removes leading and trailing whitespace
```
var clean = trim("  hello  ")    rem: "hello"
```

**split(str, delimiter)** - Splits string into list of substrings
```
var parts = split("a,b,c", ",")    rem: ["a", "b", "c"]
```

**join(lst, separator)** - Joins list of strings with separator
```
var text = join(["a", "b", "c"], "-")    rem: "a-b-c"
```

**substring(str, start, end)** - Extracts portion of string
```
var sub = substring("Hello", 1, 4)    rem: "ell" (0-indexed)
```

**replace(str, old, new)** - Replaces all occurrences
```
var fixed = replace("hello", "l", "r")    rem: "herro"
```

**contains(str, search)** - Checks if string contains substring
```
var has = contains("hello", "ell")    rem: true
```

**starts_with(str, prefix)** - Checks if string starts with prefix
```
var starts = starts_with("hello", "he")    rem: true
```

**ends_with(str, suffix)** - Checks if string ends with suffix
```
var ends = ends_with("hello", "lo")    rem: true
```

### Math Operations

**Basic Math:**

**abs(number)** - Absolute value
```
var positive = abs(-5)    rem: 5
```

**sqrt(number)** - Square root
```
var root = sqrt(16)    rem: 4.0
```

**sqr(number)** - Square (number × number)
```
var squared = sqr(5)    rem: 25
```

**pow(base, exponent)** - Power (alternative to ** operator)
```
var result = pow(2, 8)    rem: 256
```

**round(number)** - Round to nearest integer
```
var rounded = round(3.7)    rem: 4
```

**floor(number)** - Round down
```
var down = floor(3.7)    rem: 3
```

**ceil(number)** - Round up
```
var up = ceil(3.2)    rem: 4
```

**min(a, b)** - Minimum of two values
```
var smallest = min(5, 3)    rem: 3
```

**max(a, b)** - Maximum of two values
```
var largest = max(5, 3)    rem: 5
```

**Trigonometric Functions:**
(All angles in radians)

**sin(angle)** - Sine
```
var result = sin(3.14159 / 2)    rem: 1.0
```

**cos(angle)** - Cosine
```
var result = cos(0)    rem: 1.0
```

**tan(angle)** - Tangent
```
var result = tan(0.785398)    rem: ~1.0 (45 degrees)
```

**asin(value)** - Arc sine (inverse sine)
```
var angle = asin(1.0)    rem: 1.5708 (π/2)
```

**acos(value)** - Arc cosine (inverse cosine)
```
var angle = acos(1.0)    rem: 0.0
```

**atan(value)** - Arc tangent (inverse tangent)
```
var angle = atan(1.0)    rem: 0.7854 (π/4)
```

**atan2(y, x)** - Arc tangent of y/x (handles quadrants correctly)
```
var angle = atan2(1.0, 1.0)    rem: 0.7854 (π/4)
```

**Logarithmic Functions:**

**log(number)** - Natural logarithm (base e)
```
var result = log(2.71828)    rem: ~1.0
```

**log10(number)** - Base 10 logarithm
```
var result = log10(100)    rem: 2.0
```

**log2(number)** - Base 2 logarithm
```
var result = log2(8)    rem: 3.0
```

**exp(number)** - e raised to power
```
var result = exp(1)    rem: 2.71828
```

**Random Functions:**

**random()** - Random float between 0.0 and 1.0 (exclusive of 1.0)
```
var value = random()    rem: e.g., 0.7234891
```

**random_int(min, max)** - Random integer in range (inclusive)
```
var dice = random_int(1, 6)    rem: 1, 2, 3, 4, 5, or 6
```

**random_choice(lst)** - Random item from list
```
var item = random_choice(["red", "green", "blue"])
```

### List Operations

**len(lst)** - Number of items in list
```
var count = len([1, 2, 3])    rem: 3
```

**append(lst, item)** - Add item to end of list
```
var lstNumbers = [1, 2, 3]
append(lstNumbers, 4)    rem: lstNumbers is now [1, 2, 3, 4]
```

**insert(lst, index, item)** - Insert item at specific position
```
var lstItems = ["a", "c"]
insert(lstItems, 1, "b")    rem: ["a", "b", "c"]
```

**remove(lst, item)** - Remove first occurrence of item
```
var lstItems = ["a", "b", "a"]
remove(lstItems, "a")    rem: ["b", "a"]
```

**pop(lst, index)** - Remove and return item at index
```
var lstItems = ["a", "b", "c"]
var item = pop(lstItems, 1)    rem: item is "b", lst is ["a", "c"]
```

**sort(lst)** - Sort list in place
```
var lstNumbers = [3, 1, 2]
sort(lstNumbers)    rem: [1, 2, 3]
```

**reverse(lst)** - Reverse list in place
```
var lstItems = [1, 2, 3]
reverse(lstItems)    rem: [3, 2, 1]
```

**contains(lst, item)** - Check if item exists in list
```
var has = contains([1, 2, 3], 2)    rem: true
```

### Table Operations

**len(tbl)** - Number of key-value pairs
```
var count = len({"a": 1, "b": 2})    rem: 2
```

**keys(tbl)** - List of all keys
```
var lstKeys = keys({"a": 1, "b": 2})    rem: ["a", "b"]
```

**values(tbl)** - List of all values
```
var lstValues = values({"a": 1, "b": 2})    rem: [1, 2]
```

**has_key(tbl, key)** - Check if key exists
```
var exists = has_key({"a": 1}, "a")    rem: true
```

**remove(tbl, key)** - Remove key-value pair
```
var tblData = {"a": 1, "b": 2}
remove(tblData, "a")    rem: {"b": 2}
```

### Type Conversion

**to_string(value)** - Convert value to string
```
var str = to_string(42)       rem: "42"
var str = to_string(3.14)     rem: "3.14"
var str = to_string(true)     rem: "true"
```

**to_int(value)** - Convert to integer (aborts if invalid)
```
var num = to_int("42")        rem: 42
var num = to_int(3.7)         rem: 3
var num = to_int("abc")       rem: aborts with error
```

**to_float(value)** - Convert to float (aborts if invalid)
```
var num = to_float("3.14")    rem: 3.14
var num = to_float(42)        rem: 42.0
var num = to_float("abc")     rem: aborts with error
```

**to_bool(value)** - Convert to boolean
```
var flag = to_bool(1)         rem: true
var flag = to_bool(0)         rem: false
var flag = to_bool("yes")     rem: true
var flag = to_bool("")        rem: false
```

### Type Checking

**is_int(value)** - Returns true if value is an integer
```
var check = is_int(42)        rem: true
var check = is_int(3.14)      rem: false
```

**is_float(value)** - Returns true if value is a float
```
var check = is_float(3.14)    rem: true
var check = is_float(42)      rem: false
```

**is_string(value)** - Returns true if value is a string
```
var check = is_string("hello")    rem: true
var check = is_string(42)         rem: false
```

**is_bool(value)** - Returns true if value is a boolean
```
var check = is_bool(true)     rem: true
var check = is_bool(1)        rem: false
```

**is_list(value)** - Returns true if value is a list
```
var check = is_list([1, 2, 3])    rem: true
var check = is_list("abc")        rem: false
```

**is_table(value)** - Returns true if value is a table
```
var check = is_table({"a": 1})    rem: true
var check = is_table([1, 2])      rem: false
```

**is_null(value)** - Returns true if value is null
```
var check = is_null(null)     rem: true
var check = is_null(0)        rem: false
```

### Usage Examples

**String processing:**
```
task ProcessName using (fullName)
    var cleaned = trim(fullName)
    var parts = split(cleaned, " ")
    
    if len(parts) < 2
        abort "Name must have first and last parts"
    
    var first = upper(parts[0])
    var last = upper(parts[1])
    
    deliver v"{first} {last}"
```

**Math calculations:**
```
task CalculateDistance using (x1, y1, x2, y2)
    var dx = x2 - x1
    var dy = y2 - y1
    var distance = sqrt(sqr(dx) + sqr(dy))
    deliver distance
```

**List manipulation:**
```
task GetTopScores using (lstScores, count)
    sort(lstScores)
    reverse(lstScores)
    
    var lstTop = []
    loop i from 0 to min(count, len(lstScores)) - 1
        append(lstTop, lstScores[i])
    
    deliver lstTop
```

**Type checking and conversion:**
```
task SafeAdd using (a, b)
    if not is_int(a) and not is_float(a)
        a = to_float(a)
    
    if not is_int(b) and not is_float(b)
        b = to_float(b)
    
    deliver a + b
```

---

## File I/O

PLAIN provides comprehensive file input/output operations with two approaches: simple operations for common cases and handle-based operations for more control. All file operations abort with descriptive error messages on failure (file not found, permission denied, etc.).

### Simple File Operations

These operations handle the entire file in one call - ideal for small to medium files and common use cases.

**Text File Operations:**

**read_file(path)** - Read entire file as string
```
var content = read_file("data.txt")
rem: Aborts if file doesn't exist or can't be read
```

**write_file(path, content)** - Write string to file (overwrites if exists)
```
write_file("output.txt", "Hello, World!")
rem: Creates file if it doesn't exist
rem: Aborts if can't write (permission denied, etc.)
```

**append_file(path, content)** - Append string to end of file
```
append_file("log.txt", v"{timestamp}: Event logged\n")
rem: Creates file if it doesn't exist
rem: Aborts on write errors
```

**read_lines(path)** - Read file as list of lines
```
var lstLines = read_lines("data.txt")
rem: Returns list of strings, one per line
rem: Line endings are removed
```

**write_lines(path, lstLines)** - Write list of strings as lines
```
var lstData = ["Line 1", "Line 2", "Line 3"]
write_lines("output.txt", lstData)
rem: Automatically adds line endings
rem: Overwrites if file exists
```

**Binary File Operations:**

**read_binary(path)** - Read entire file as bytes
```
var data = read_binary("image.png")
rem: Returns binary data
rem: Aborts if file doesn't exist
```

**write_binary(path, data)** - Write bytes to file (overwrites if exists)
```
write_binary("output.bin", data)
rem: Creates file if it doesn't exist
rem: Aborts on write errors
```

**append_binary(path, data)** - Append bytes to end of file
```
append_binary("data.bin", additionalData)
rem: Creates file if it doesn't exist
```

### Handle-based Operations

For streaming large files, reading line-by-line, or when you need more control over file operations.

**Opening Files:**

**open(path, mode)** - Open file and return handle
```
var file = open("data.txt", "r")
```

**File Modes:**
- `"r"` - Read text (file must exist)
- `"w"` - Write text (creates or overwrites)
- `"a"` - Append text (creates if doesn't exist)
- `"rb"` - Read binary (file must exist)
- `"wb"` - Write binary (creates or overwrites)
- `"ab"` - Append binary (creates if doesn't exist)

**Reading from Handles:**

**read(handle)** - Read entire remaining content
```
var file = open("data.txt", "r")
var content = read(file)
close(file)
```

**read_line(handle)** - Read one line from text file
```
var file = open("data.txt", "r")
var line = read_line(file)    rem: returns null at end of file
close(file)
```

**read_bytes(handle, count)** - Read specified number of bytes
```
var file = open("data.bin", "rb")
var chunk = read_bytes(file, 1024)    rem: read 1KB
close(file)
```

**Writing to Handles:**

**write(handle, content)** - Write string or bytes to file
```
var file = open("output.txt", "w")
write(file, "Hello, World!")
close(file)
```

**write_line(handle, content)** - Write string with newline
```
var file = open("output.txt", "w")
write_line(file, "First line")
write_line(file, "Second line")
close(file)
```

**Closing Files:**

**close(handle)** - Close file handle
```
close(file)
rem: Always close files when done
rem: Ensures data is flushed to disk
```

### File System Operations

**File Information and Management:**

**file_exists(path)** - Check if file exists
```
if file_exists("config.txt")
    config = read_file("config.txt")
else
    config = defaultConfig
```

**delete_file(path)** - Delete file
```
delete_file("temp.txt")
rem: Aborts if file doesn't exist or can't be deleted
```

**rename_file(old_path, new_path)** - Rename or move file
```
rename_file("old.txt", "new.txt")
rem: Can move between directories
rem: Aborts if source doesn't exist or destination can't be written
```

**copy_file(source, destination)** - Copy file
```
copy_file("template.txt", "instance.txt")
rem: Overwrites destination if it exists
rem: Aborts if source doesn't exist or can't copy
```

**file_size(path)** - Get file size in bytes
```
var bytes = file_size("data.bin")
rem: Aborts if file doesn't exist
```

**Directory Operations:**

**dir_exists(path)** - Check if directory exists
```
if not dir_exists("output")
    create_dir("output")
```

**create_dir(path)** - Create directory
```
create_dir("logs")
rem: Aborts if directory already exists or can't be created
rem: Does not create parent directories
```

**delete_dir(path)** - Delete empty directory
```
delete_dir("temp")
rem: Aborts if directory doesn't exist, isn't empty, or can't be deleted
```

**list_dir(path)** - List files and directories
```
var lstItems = list_dir("data")
rem: Returns list of file/directory names (not full paths)
rem: Does not include "." or ".."
rem: Aborts if directory doesn't exist or can't be read
```

**Path Operations:**

**join_path(part1, part2, ...)** - Join path parts properly
```
var path = join_path("data", "files", "input.txt")
rem: Returns "data/files/input.txt" (or "data\files\input.txt" on Windows)
rem: Handles platform-specific path separators
```

**split_path(path)** - Split into directory and filename
```
var parts = split_path("data/files/input.txt")
rem: Returns ["data/files", "input.txt"]
```

**get_extension(path)** - Get file extension
```
var ext = get_extension("data.txt")    rem: ".txt"
var ext = get_extension("archive.tar.gz")    rem: ".gz"
```

**absolute_path(path)** - Convert to absolute path
```
var abs = absolute_path("data.txt")
rem: Returns full path like "/home/user/project/data.txt"
```

### Error Handling

All file operations abort on errors. Use `attempt/handle` blocks to manage errors gracefully.

**Example - Safe file reading:**
```
task LoadConfig using (path)
    var config = null
    
    attempt
        config = read_file(path)
    handle "File not found"
        display("Config not found, using defaults")
        config = defaultConfig()
    handle error
        display(v"Error loading config: {error}")
        abort "Cannot start without config"
    
    deliver config
```

**Example - Check before operating:**
```
task SafeDelete using (path)
    if file_exists(path)
        delete_file(path)
        deliver true
    else
        deliver false
```

### Complete Examples

**Reading and processing a text file:**
```
task ProcessLogFile using (path)
    var lstLines = read_lines(path)
    var errorCount = 0
    
    loop line in lstLines
        if contains(line, "ERROR")
            errorCount += 1
    
    deliver errorCount
```

**Writing data line by line:**
```
task WriteReport with (lstData, outputPath)
    var file = open(outputPath, "w")
    
    write_line(file, "=== Report ===")
    write_line(file, "")
    
    loop item in lstData
        write_line(file, v"Item: {item}")
    
    close(file)
```

**Processing large file with handles:**
```
task ProcessLargeFile using (inputPath, outputPath)
    var input = open(inputPath, "r")
    var output = open(outputPath, "w")
    var count = 0
    
    loop
        var line = read_line(input)
        if is_null(line)
            exit
        
        if contains(line, "IMPORTANT")
            write_line(output, line)
            count += 1
    
    close(input)
    close(output)
    
    deliver count
```

**Working with binary files:**
```
task CopyWithHeader using (sourcePath, destPath)
    rem: Read original file
    var data = read_binary(sourcePath)
    
    rem: Create header
    var header = "MYFORMAT"
    
    rem: Write header + data
    var output = open(destPath, "wb")
    write(output, header)
    write(output, data)
    close(output)
```

**Directory operations:**
```
task BackupFiles with (sourceDir, backupDir)
    if not dir_exists(backupDir)
        create_dir(backupDir)
    
    var lstFiles = list_dir(sourceDir)
    
    loop filename in lstFiles
        var source = join_path(sourceDir, filename)
        var dest = join_path(backupDir, filename)
        
        if file_exists(source)
            copy_file(source, dest)
            display(v"Backed up: {filename}")
```

**Safe file handling pattern:**
```
task SafeFileOperation using (path)
    var file = null
    
    attempt
        file = open(path, "r")
        var content = read(file)
        rem: process content...
        deliver content
    handle error
        display(v"Error: {error}")
        deliver null
    ensure
        if not is_null(file)
            close(file)
```

### Best Practices

1. **Always close file handles** - Use `ensure` blocks to guarantee cleanup
2. **Check file existence** before operations when appropriate
3. **Use simple operations** for small files, handles for large files
4. **Handle errors explicitly** with `attempt/handle` blocks
5. **Use path operations** for cross-platform compatibility
6. **Prefer `read_lines`** over manual line-by-line reading for small files
7. **Close files in `ensure` blocks** to guarantee cleanup even on errors

---

---

## Concurrency and Events

PLAIN provides event-driven programming through a simple timer-based model. This allows periodic task execution, timeouts, and responsive programs without the complexity of full multi-threading. Implementation in Go provides efficient concurrency under the hood while maintaining PLAIN's simplicity.

### Design Philosophy

PLAIN uses a single event loop model:
- One main event loop coordinates all timers
- Timer callbacks execute when triggered
- No manual thread management
- Go's goroutines handle concurrency internally

This provides practical concurrency for:
- Periodic sensor reading
- Timeout handling
- Simple state machines
- Interactive programs
- Background tasks

### Basic Timing (Blocking)

**sleep(milliseconds)** - Pause execution for specified duration
```
task CountDown()
    loop i from 10 to 1
        display(i)
        sleep(1000)    rem: wait 1 second
    display("Launch!")
```

**Use cases:**
- Simple delays between operations
- Rate limiting
- Animation timing
- Polling with delays

### Timers (Non-blocking)

Timers execute callbacks at specified intervals without blocking the main program flow.

**create_timer(interval, callback)** - Create repeating timer
```
var timer = create_timer(1000, OnTick)
rem: Calls OnTick every 1000ms (1 second)
rem: Timer is created in stopped state
```

**create_timeout(delay, callback)** - Create one-shot timer
```
var timeout = create_timeout(5000, OnTimeout)
rem: Calls OnTimeout once after 5000ms (5 seconds)
rem: Timer is created in stopped state
```

**start_timer(timer)** - Start or resume timer
```
start_timer(timer)
rem: Starts firing at specified interval
rem: If already started, has no effect
```

**stop_timer(timer)** - Pause timer
```
stop_timer(timer)
rem: Stops firing, but timer still exists
rem: Can be restarted with start_timer
```

**cancel_timer(timer)** - Stop and destroy timer
```
cancel_timer(timer)
rem: Stops timer and frees resources
rem: Timer cannot be reused after canceling
```

### Timer Callbacks

Callbacks can have two signatures - PLAIN automatically detects which to use:

**Simple callback (no parameters):**
```
task OnTick()
    display("Tick!")
```

**Callback with timer info:**
```
task OnTickWithInfo with (timer, elapsed)
    display(v"Elapsed: {elapsed}ms")
    
    if elapsed > 10000
        stop_timer(timer)
```

**Callback parameters:**
- `timer` - The timer that triggered (can be used to stop/cancel self)
- `elapsed` - Total milliseconds since timer was started

### Event Loop

The event loop coordinates all active timers. There is only one event loop per program.

**wait_for_events()** - Run event loop until all timers complete
```
task Main()
    var timer = create_timer(1000, OnTick)
    start_timer(timer)
    
    wait_for_events()    rem: blocks here until no active timers
    display("All timers finished")
```

**run_events(duration)** - Run event loop for specified time
```
task Main()
    var timer = create_timer(100, OnTick)
    start_timer(timer)
    
    run_events(5000)    rem: run for 5 seconds then return
    display("5 seconds elapsed")
```

**stop_events()** - Stop event loop from within a callback
```
var count = 0

task OnTick()
    count += 1
    display(v"Tick {count}")
    
    if count >= 10
        stop_events()    rem: stops the event loop

task Main()
    var timer = create_timer(1000, OnTick)
    start_timer(timer)
    
    wait_for_events()
    display("Done after 10 ticks")
```

### Error Handling in Callbacks

If a timer callback aborts:
1. The specific timer is automatically stopped and removed
2. An error message is displayed showing which timer and what error
3. Other active timers continue running normally
4. The event loop continues (unless this was the last timer)

**Example:**
```
task ProblematicCallback()
    display("Running...")
    abort "Something went wrong"

task SafeCallback()
    display("Still running")

task Main()
    var bad = create_timer(1000, ProblematicCallback)
    var good = create_timer(500, SafeCallback)
    
    start_timer(bad)
    start_timer(good)
    
    wait_for_events()
    
    rem: Output:
    rem: "Still running" (at 500ms)
    rem: "Running..." (at 1000ms)
    rem: "Timer error in ProblematicCallback: Something went wrong"
    rem: "Still running" (at 1000ms)
    rem: "Still running" (at 1500ms)
    rem: ... (good timer continues)
```

### Complete Examples

**Simple periodic task:**
```
var tickCount = 0

task OnTick()
    tickCount += 1
    display(v"Tick {tickCount}")

task Main()
    var timer = create_timer(1000, OnTick)
    start_timer(timer)
    
    rem: Let it run for 10 seconds
    run_events(10000)
    
    cancel_timer(timer)
    display(v"Completed {tickCount} ticks")
```

**Timeout pattern:**
```
var dataReceived = false

task WaitForData()
    display("Waiting for data...")
    rem: Simulate data reception
    sleep(3000)
    dataReceived = true

task OnTimeout()
    if not dataReceived
        display("Timeout: No data received")
        stop_events()

task Main()
    rem: Start data wait in background
    var timeout = create_timeout(5000, OnTimeout)
    start_timer(timeout)
    
    WaitForData()
    
    if dataReceived
        cancel_timer(timeout)
        display("Data received successfully")
    else
        wait_for_events()
```

**Multiple timers:**
```
task FastTick()
    display("Fast")

task SlowTick()
    display("Slow")

task Main()
    var fast = create_timer(500, FastTick)
    var slow = create_timer(2000, SlowTick)
    
    start_timer(fast)
    start_timer(slow)
    
    rem: Run for 10 seconds
    run_events(10000)
    
    cancel_timer(fast)
    cancel_timer(slow)
```

**Self-canceling timer:**
```
task OnTick with (timer, elapsed)
    display(v"Elapsed: {elapsed}ms")
    
    if elapsed >= 5000
        display("Time's up!")
        cancel_timer(timer)
        stop_events()

task Main()
    var timer = create_timer(1000, OnTick)
    start_timer(timer)
    wait_for_events()
```

**Sensor reading simulation:**
```
var readings = []
var maxReadings = 100

task ReadSensor with (timer, elapsed)
    var value = random_int(0, 100)
    append(readings, value)
    
    display(v"Reading {len(readings)}: {value}")
    
    if len(readings) >= maxReadings
        display("Collection complete")
        cancel_timer(timer)
        stop_events()

task Main()
    display("Starting sensor collection...")
    
    var sensor = create_timer(100, ReadSensor)
    start_timer(sensor)
    
    wait_for_events()
    
    rem: Process readings
    var total = 0
    loop value in readings
        total += value
    
    var average = total / len(readings)
    display(v"Average reading: {average}")
```

**State machine with timing:**
```
var state = "idle"
var stateTimer = null

task OnIdle()
    display("State: Idle")
    state = "working"
    cancel_timer(stateTimer)
    stateTimer = create_timer(2000, OnWorking)
    start_timer(stateTimer)

task OnWorking()
    display("State: Working")
    state = "done"
    cancel_timer(stateTimer)
    stateTimer = create_timeout(1000, OnDone)
    start_timer(stateTimer)

task OnDone()
    display("State: Done")
    stop_events()

task Main()
    stateTimer = create_timeout(1000, OnIdle)
    start_timer(stateTimer)
    wait_for_events()
```

**Graceful shutdown:**
```
var running = true
var operationTimer = null
var shutdownTimer = null

task DoWork()
    if running
        display("Working...")
    else
        display("Shutting down...")
        cancel_timer(operationTimer)

task InitiateShutdown()
    display("Shutdown initiated")
    running = false
    
    rem: Give 3 seconds for cleanup
    var cleanup = create_timeout(3000, FinalShutdown)
    start_timer(cleanup)

task FinalShutdown()
    display("Final shutdown")
    stop_events()

task Main()
    operationTimer = create_timer(1000, DoWork)
    shutdownTimer = create_timeout(10000, InitiateShutdown)
    
    start_timer(operationTimer)
    start_timer(shutdownTimer)
    
    wait_for_events()
    display("Program complete")
```

### Best Practices

1. **Always cancel timers when done** - Prevents resource leaks
   ```
   cancel_timer(timer)
   ```

2. **Use timeouts for safety** - Prevent infinite waiting
   ```
   var timeout = create_timeout(5000, OnTimeout)
   ```

3. **Check state in callbacks** - Callbacks may fire after state changes
   ```
   task OnTick()
       if stillNeeded
           doWork()
       else
           stop_timer(currentTimer)
   ```

4. **Use stop_events() for clean exit** - Better than letting program hang
   ```
   if done
       stop_events()
   ```

5. **Handle errors in callbacks** - Use attempt/handle to prevent timer abortion
   ```
   task SafeCallback()
       attempt
           riskyOperation()
       handle error
           display(v"Error handled: {error}")
   ```

6. **Module variables for timer handles** - Allows callbacks to control timers
   ```
   var mainTimer = null
   
   task OnTick()
       if condition
           cancel_timer(mainTimer)
   ```

7. **Use run_events() for testing** - Run for fixed duration instead of indefinitely
   ```
   run_events(5000)    rem: easier to test than wait_for_events()
   ```

### Implementation Notes

PLAIN's event system is implemented using Go's goroutines and channels:
- Each timer runs in its own goroutine
- The event loop coordinates all timers
- Callbacks execute in the main event thread (no race conditions)
- Timer precision depends on system scheduling (~1ms typical)
- Callbacks should complete quickly to avoid blocking other timers

---

## Future Considerations

All major language features have been defined. Future enhancements might include:

- Network operations (HTTP, TCP/UDP, WebSocket)
- Database connectivity
- JSON/XML parsing and generation
- Regular expressions
- Command-line argument parsing
- Environment variables
- Process execution
- Advanced data structures (sets, queues, stacks)

---

## Appendix: Complete Example

```
note:
    Calculate compound interest over time
    Principal: initial amount
    Rate: annual interest rate (decimal)
    Years: number of years

task CalculateCompoundInterest using (principal, rate, years)
    if principal <= 0
        abort "Principal must be positive"
    if rate < 0
        abort "Rate cannot be negative"
    if years <= 0
        abort "Years must be positive"
    
    var fltAmount = principal * ((1 + rate) ** years)
    deliver fltAmount

task Main()
    rem: Example usage
    fxd initialAmount as float = 1000.0
    fxd interestRate as float = 0.05
    fxd numYears as integer = 10
    
    var result = CalculateCompoundInterest(initialAmount, interestRate, numYears)
    
    var message = v"After {numYears} years at {interestRate * 100}% interest:"
    var details = v"${initialAmount} grows to ${result}"
    
    display(message)
    display(details)
```

---

**End of PLAIN Language Specification v0.1**

*PLAIN - Programming Language - Able, Intuitive, and Natural*
