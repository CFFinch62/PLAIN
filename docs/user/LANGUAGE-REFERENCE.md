# PLAIN Language Reference

> **The complete specification for the PLAIN programming language** 📐

This document is the definitive reference for every feature of the PLAIN language. It covers syntax, semantics, and behavior in precise detail. For a gentler introduction, see the [User Guide](USER-GUIDE.md) or [Tutorial](TUTORIAL.md).

---

## Table of Contents

1. [Lexical Structure](#1-lexical-structure)
2. [Data Types](#2-data-types)
3. [Variables and Constants](#3-variables-and-constants)
4. [Operators](#4-operators)
5. [Expressions](#5-expressions)
6. [Statements](#6-statements)
7. [Control Flow](#7-control-flow)
8. [Tasks](#8-tasks)
9. [Records](#9-records)
10. [Error Handling](#10-error-handling)
11. [Modules and Imports](#11-modules-and-imports)
12. [Scope Rules](#12-scope-rules)
13. [Reserved Words](#13-reserved-words)
14. [Appendix A: Grammar Summary](#appendix-a-grammar-summary)
15. [Appendix B: Common Error Messages](#appendix-b-common-error-messages)

---

## 1. Lexical Structure

### 1.1 Source Encoding

PLAIN source files are UTF-8 encoded text files. The conventional file extension is `.plain`.

### 1.2 Line Structure

PLAIN is a **line-oriented** language. Each statement occupies one line. There is no statement terminator character (no semicolons). Blank lines are ignored and may be used freely for readability.

```plain
display("line one")
display("line two")

display("after blank line")
```

> **Note:** Expressions and literals must be contained on a single line. Multi-line literals (lists, records, or function calls split across lines) are not supported.

### 1.3 Indentation

PLAIN uses **indentation** to define blocks, similar to Python. The indentation level determines which statements belong to which block.

- Use **consistent indentation** within a block (spaces are recommended; 4 spaces is conventional).
- A block begins when the indentation level **increases** after a block-introducing statement.
- A block ends when the indentation level **returns** to the previous level.

```plain
task Main()
    if true
        display("indented twice")    rem: inside the if block
    display("indented once")         rem: inside Main, after the if
```

Block-introducing statements include: `task`, `if`, `else`, `choose`, `choice`, `default`, `loop`, `attempt`, `handle`, and `ensure`.

### 1.4 Comments

PLAIN has two comment styles. Both extend from the keyword to the end of the line.

| Keyword | Purpose                                       | Convention                            |
| ------- | --------------------------------------------- | ------------------------------------- |
| `rem:`  | **Remark** — explains *what* the code does    | Used for inline documentation         |
| `note:` | **Note** — explains *why* or provides context | Used for rationale, caveats, warnings |

```plain
rem: Calculate the average of all scores
var total = 0                       rem: running total
loop score in scores
    total = total + score
var avg = total / len(scores)       note: len() returns 0 for empty lists — caller must check
```

Comments can appear on their own line or at the end of a code line. They have no effect on program execution.

### 1.5 Tokens

The lexer produces the following token categories:

| Category                 | Examples                                                                     |
| ------------------------ | ---------------------------------------------------------------------------- |
| **Keywords**             | `task`, `var`, `if`, `loop`, `deliver`, etc. (see [§13](#13-reserved-words)) |
| **Identifiers**          | `myVar`, `CalculateTotal`, `strName`                                         |
| **Integer literals**     | `0`, `42`, `-17`                                                             |
| **Float literals**       | `3.14`, `0.5`, `-2.7`                                                        |
| **String literals**      | `"hello"`, `""`                                                              |
| **Interpolated strings** | `v"Hello {name}"`                                                            |
| **Boolean literals**     | `true`, `false`                                                              |
| **Null literal**         | `null`                                                                       |
| **Operators**            | `+`, `-`, `*`, `/`, `==`, `&`, etc.                                          |
| **Delimiters**           | `(`, `)`, `[`, `]`, `{`, `}`, `,`, `:`, `.`                                  |
| **Indentation**          | INDENT (increase), DEDENT (decrease)                                         |

### 1.6 Identifiers

Identifiers name variables, constants, tasks, records, and parameters. An identifier:

- Starts with a letter (a–z, A–Z) or underscore (`_`)
- Continues with letters, digits (0–9), or underscores
- Is **case-sensitive** (`myVar` and `MyVar` are different identifiers)
- Cannot be a reserved word

**Naming conventions:**

| Element    | Convention                             | Example                        |
| ---------- | -------------------------------------- | ------------------------------ |
| Variables  | camelCase, optionally with type prefix | `count`, `intCount`, `strName` |
| Constants  | UPPER_SNAKE_CASE                       | `MAX_SIZE`, `PI`               |
| Tasks      | PascalCase                             | `CalculateTotal`, `Main`       |
| Records    | PascalCase                             | `Person`, `StudentRecord`      |
| Parameters | camelCase                              | `firstName`, `maxRetries`      |

### 1.7 String Literals

**Regular strings** are enclosed in double quotes:

```plain
"Hello, world!"
"She said \"hello\""
""                          rem: empty string
```

**Interpolated strings** are prefixed with `v` and can contain expressions in braces:

```plain
v"Hello, {name}!"
v"The answer is {a + b}"
v"Score: {score} / {total}"
```

Inside `v"..."`, any text between `{` and `}` is evaluated as an expression and its result is converted to a string. The expression must be a simple variable name or arithmetic expression — indexing (`list[0]`) and dot access (`record.field`) inside braces are not currently supported.

---

## 2. Data Types

PLAIN has eight built-in data types.

### 2.1 Integer

Whole numbers with no fractional part. Internally stored as 64-bit signed integers.

```plain
var count = 42
var negative = -17
var zero = 0
```

**Range:** approximately -9.2 × 10¹⁸ to 9.2 × 10¹⁸

### 2.2 Float

Numbers with a decimal point. Internally stored as 64-bit IEEE 754 floating-point.

```plain
var pi = 3.14159
var temperature = -40.0
var tiny = 0.001
```

**Note:** Floating-point arithmetic may produce small rounding errors. For example, `0.1 + 0.2` may not equal exactly `0.3`. Use `round()` when exact decimal values are needed.

The display precision of floating-point numbers can be controlled globally using `set_float_precision(n)`. See [STDLIB.md](STDLIB.md#set_float_precision) for details.

### 2.3 String

A sequence of characters enclosed in double quotes.

```plain
var greeting = "Hello, world!"
var empty = ""
var name = "Alice"
```

Strings are **immutable** — string operations return new strings rather than modifying the original.

**String concatenation** uses the `&` operator:

```plain
var full = "Hello" & " " & "World"    rem: "Hello World"
```

### 2.4 Boolean

A logical value — either `true` or `false`.

```plain
var isReady = true
var hasError = false
```

Boolean values are produced by comparison operators and used in conditions.

### 2.5 Null

Represents the absence of a value.

```plain
var result = null
```

Use `is_null(value)` to check for null. Null is distinct from `0`, `""`, and `false`.

### 2.6 List

An ordered collection of values. Lists can contain values of any type, and elements can be mixed types.

```plain
var numbers = [1, 2, 3, 4, 5]
var names = ["Alice", "Bob", "Carol"]
var mixed = [1, "two", true, null]
var empty = []
```

Lists are **zero-indexed** — the first element is at index `0`:

```plain
var first = numbers[0]      rem: 1
var last = numbers[4]       rem: 5
numbers[0] = 99             rem: modifies the list
```

### 2.7 Table

An unordered collection of key-value pairs. Keys are strings; values can be any type.

```plain
var person = {"name": "Alice", "age": 30}
var empty = {}
```

Access values by key:

```plain
var name = person["name"]       rem: "Alice"
person["email"] = "alice@example.com"   rem: add new key
```

### 2.8 Record

A user-defined structured type with named, typed fields. Records are defined with the `record` keyword and instantiated by calling the record name with named arguments. See [§9 Records](#9-records) for full details.

```plain
record Person:
    name as string
    age as integer = 0

var p = Person(name: "Alice", age: 30)
display(p.name)     rem: "Alice"
```

### 2.9 Type Compatibility

| Operation               | Allowed Types             | Result Type                                |
| ----------------------- | ------------------------- | ------------------------------------------ |
| `+`, `-`, `*`, `/`      | integer, float            | integer (if both integer), float otherwise |
| `//` (integer division) | integer, float            | integer                                    |
| `%` (modulo)            | integer, float            | integer (if both integer), float otherwise |
| `**` (power)            | integer, float            | float                                      |
| `&` (concatenation)     | any (converted to string) | string                                     |
| `==`, `!=`              | any pair of same type     | boolean                                    |
| `<`, `>`, `<=`, `>=`    | integer, float, string    | boolean                                    |
| `and`, `or`, `not`      | boolean                   | boolean                                    |

---

## 3. Variables and Constants

### 3.1 Variable Declaration

Variables are declared with `var` and must be initialized:

```plain
var name = "Alice"
var count = 0
var prices = [9.99, 14.50, 3.25]
```

A variable's type is determined at declaration and cannot change:

```plain
var x = 42
x = 100        rem: OK — still an integer
x = "hello"    rem: ERROR — cannot assign string to integer variable
```

### 3.2 Type Inference from Prefixes

Variable names can include a **type prefix** that tells both the reader and the analyzer what type the variable holds:

| Prefix | Full Name | Type    | Example                        |
| ------ | --------- | ------- | ------------------------------ |
| `int`  | `integer` | Integer | `var intCount = 0`             |
| `flt`  | `float`   | Float   | `var fltPrice = 9.99`          |
| `str`  | `string`  | String  | `var strName = "Alice"`        |
| `bln`  | `boolean` | Boolean | `var blnReady = true`          |
| `lst`  | `list`    | List    | `var lstItems = [1, 2, 3]`     |
| `tbl`  | `table`   | Table   | `var tblScores = {"math": 95}` |

The prefix is part of the variable name — `intCount` is a single identifier. The analyzer uses the prefix to verify that the assigned value matches the expected type.

> **Note:** Type-prefixed variables cannot currently be assigned from function return values, because the analyzer cannot determine the function's return type at analysis time. Use un-prefixed names when assigning from function calls.

### 3.3 Explicit Type Annotation

The `as` keyword provides an explicit type annotation:

```plain
var count as integer = 0
var name as string = "Alice"
var price as float = 9.99
var flag as boolean = true
```

For collections, you can specify the element type:

```plain
var numbers as list of integer = [1, 2, 3]
var scores as table of string to integer = {"alice": 95, "bob": 87}
```

### 3.4 Constants

Constants are declared with `fxd` (fixed) and **require** an explicit type:

```plain
fxd PI as float = 3.14159
fxd MAX_STUDENTS as integer = 30
fxd GREETING as string = "Welcome!"
```

Constants cannot be reassigned after declaration:

```plain
fxd LIMIT as integer = 100
LIMIT = 200    rem: ERROR — cannot reassign a constant
```

### 3.5 Assignment

Assignment uses `=` and modifies an existing variable:

```plain
var x = 10
x = 20         rem: reassign x
```

Compound assignment operators provide shorthand:

| Operator   | Equivalent    | Description            |
| ---------- | ------------- | ---------------------- |
| `x += 5`   | `x = x + 5`   | Add and assign         |
| `x -= 3`   | `x = x - 3`   | Subtract and assign    |
| `x *= 2`   | `x = x * 2`   | Multiply and assign    |
| `x /= 4`   | `x = x / 4`   | Divide and assign      |
| `x %= 3`   | `x = x % 3`   | Modulo and assign      |
| `s &= "!"` | `s = s & "!"` | Concatenate and assign |

You can also assign to list elements and table entries:

```plain
var list = [1, 2, 3]
list[0] = 99               rem: list is now [99, 2, 3]

var table = {"a": 1}
table["b"] = 2              rem: table is now {"a": 1, "b": 2}
```

---

## 4. Operators

### 4.1 Precedence Table

Operators are listed from **highest** to **lowest** precedence. Operators on the same row have the same precedence and are evaluated left-to-right (except `**` which is right-to-left).

| Precedence  | Operator(s)                 | Description                                        | Associativity  |
| ----------- | --------------------------- | -------------------------------------------------- | -------------- |
| 1 (highest) | `**`                        | Exponentiation                                     | Right-to-left  |
| 2           | `*` `/` `//` `%`            | Multiplication, division, integer division, modulo | Left-to-right  |
| 3           | `+` `-`                     | Addition, subtraction                              | Left-to-right  |
| 4           | `&`                         | String concatenation                               | Left-to-right  |
| 5           | `==` `!=` `<` `>` `<=` `>=` | Comparison                                         | Left-to-right  |
| 6           | `not`                       | Logical NOT                                        | Unary (prefix) |
| 7           | `and`                       | Logical AND                                        | Left-to-right  |
| 8 (lowest)  | `or`                        | Logical OR                                         | Left-to-right  |

Parentheses can be used to override precedence:

```plain
var result = (2 + 3) * 4       rem: 20, not 14
```

### 4.2 Arithmetic Operators

| Operator     | Name             | Example   | Result     |
| ------------ | ---------------- | --------- | ---------- |
| `+`          | Addition         | `7 + 3`   | `10`       |
| `-`          | Subtraction      | `7 - 3`   | `4`        |
| `*`          | Multiplication   | `7 * 3`   | `21`       |
| `/`          | Division         | `7 / 3`   | `2.333...` |
| `//`         | Integer division | `7 // 3`  | `2`        |
| `%`          | Modulo           | `7 % 3`   | `1`        |
| `**`         | Exponentiation   | `2 ** 10` | `1024`     |
| `-` (prefix) | Negation         | `-42`     | `-42`      |

**Division behavior:**
- `/` always produces a float result if either operand is a float
- `//` truncates toward zero and returns an integer
- Division by zero causes a runtime error

### 4.3 Comparison Operators

All comparison operators return a boolean value.

| Operator | Meaning               | Example  |
| -------- | --------------------- | -------- |
| `==`     | Equal to              | `x == 5` |
| `!=`     | Not equal to          | `x != 5` |
| `<`      | Less than             | `x < 5`  |
| `>`      | Greater than          | `x > 5`  |
| `<=`     | Less than or equal    | `x <= 5` |
| `>=`     | Greater than or equal | `x >= 5` |

Comparisons work on numbers (integer and float) and strings (lexicographic ordering).

### 4.4 Logical Operators

| Operator | Meaning            | Example             |
| -------- | ------------------ | ------------------- |
| `and`    | Both must be true  | `x > 0 and x < 100` |
| `or`     | Either can be true | `x < 0 or x > 100`  |
| `not`    | Inverts boolean    | `not isDone`        |

Logical operators use **short-circuit evaluation**: `and` stops if the left side is false; `or` stops if the left side is true.

### 4.5 String Operator

| Operator | Name          | Example                   | Result          |
| -------- | ------------- | ------------------------- | --------------- |
| `&`      | Concatenation | `"Hello" & " " & "World"` | `"Hello World"` |

The `&` operator converts non-string values to strings automatically:

```plain
display("Score: " & 95)        rem: "Score: 95"
display("Ready: " & true)      rem: "Ready: true"
```

### 4.6 Assignment Operators

See [§3.5 Assignment](#35-assignment) for the full table of assignment operators (`=`, `+=`, `-=`, `*=`, `/=`, `%=`, `&=`).

---

## 5. Expressions

### 5.1 Literal Expressions

Literal values that appear directly in code:

```plain
42              rem: integer literal
3.14            rem: float literal
"hello"         rem: string literal
v"Hi {name}"    rem: interpolated string literal
true            rem: boolean literal
null            rem: null literal
[1, 2, 3]      rem: list literal
{"a": 1}        rem: table literal
```

### 5.2 Identifiers

A variable or constant name used as an expression evaluates to its current value:

```plain
var x = 42
display(x)      rem: displays 42
```

### 5.3 Function Calls

A task name followed by parenthesized arguments:

```plain
display("hello")
var result = Add(5, 3)
var name = upper("alice")
```

Arguments are evaluated left-to-right and passed by value.

### 5.4 Index Expressions

Square brackets access elements of lists and tables:

```plain
var item = myList[0]           rem: first list element
var value = myTable["key"]     rem: table lookup
```

List indices are zero-based integers. Table keys are strings. Out-of-bounds access causes a runtime error.

### 5.5 Dot Expressions

The dot operator accesses record fields and qualified names:

```plain
var name = person.name         rem: record field access
person.age = 31                rem: record field assignment
utils.FormatDate()             rem: qualified task call
```

### 5.6 Prefix Expressions

The unary minus and `not` operators:

```plain
var neg = -x
var opposite = not isReady
```

### 5.7 Infix Expressions

Binary operators with two operands:

```plain
var sum = a + b
var result = x * 2 + y * 3
var match = name == "Alice" and age >= 18
```

Evaluation follows the precedence rules in [§4.1](#41-precedence-table).

### 5.8 String Interpolation

Interpolated strings (prefixed with `v`) evaluate expressions inside braces:

```plain
var name = "Alice"
var age = 30
display(v"Name: {name}, Age: {age}")     rem: "Name: Alice, Age: 30"
display(v"Sum: {10 + 20}")               rem: "Sum: 30"
```

The expression result is converted to a string using the same rules as the `&` operator.

### 5.9 Record Creation

Records are instantiated by calling the record name with named arguments:

```plain
var p = Person(name: "Alice", age: 30)
```

All required fields (those without default values) must be provided. Fields with defaults can be omitted:

```plain
record Student:
    name as string          rem: required — no default
    grade as string = "A"   rem: optional — has default

var s1 = Student(name: "Bob")                   rem: grade defaults to "A"
var s2 = Student(name: "Carol", grade: "B+")    rem: grade explicitly set
```

---

## 6. Statements

### 6.1 Variable Declaration

```plain
var name = expression
var name as type = expression
```

Declares a new variable in the current scope. See [§3 Variables and Constants](#3-variables-and-constants).

### 6.2 Constant Declaration

```plain
fxd NAME as type = expression
```

Declares an immutable constant. An explicit type is required.

### 6.3 Assignment

```plain
name = expression
name += expression
list[index] = expression
table[key] = expression
record.field = expression
```

Assigns a value to an existing variable, list element, table entry, or record field. The target must already exist. See [§3.5 Assignment](#35-assignment).

### 6.4 Expression Statements

Any expression can be used as a statement. This is typically used for task calls that don't return values (procedures):

```plain
display("hello")
SayGreeting()
DrawLine()
```

### 6.5 Deliver Statement

```plain
deliver expression
```

Returns a value from a function (a task declared with `using`). Immediately exits the task. See [§8.3 Functions](#83-functions-using).

### 6.6 Abort Statement

```plain
abort "error message"
```

Raises an error that can be caught by `attempt/handle`. The message must be a string expression. See [§10 Error Handling](#10-error-handling).

### 6.7 Exit Statement

```plain
exit
```

Immediately exits the innermost enclosing `loop`. See [§7.4 Exit and Continue](#74-exit-and-continue).

### 6.8 Continue Statement

```plain
continue
```

Skips the rest of the current loop iteration and proceeds to the next iteration. See [§7.4 Exit and Continue](#74-exit-and-continue).

---

## 7. Control Flow

### 7.1 If / Else

The `if` statement executes a block conditionally. The `else` clause is optional.

```plain
if condition
    statements

if condition
    statements
else
    statements
```

The condition must evaluate to a boolean. PLAIN's `if/else` is **binary only** — for three or more branches, use `choose/choice` (§7.2) or nested `if/else`.

```plain
var score = 85

if score >= 60
    display("Pass")
else
    display("Fail")
```

**Nested if/else** for multiple conditions:

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

> **Tip:** When branching on a single value with many options, `choose/choice` is cleaner than nested `if/else`. See §7.2.

### 7.2 Choose / Choice / Default

The `choose` statement matches a value against multiple options. It replaces `switch/case` from other languages.

```plain
choose expression
    choice value1
        statements
    choice value2
        statements
    default
        statements
```

The expression is evaluated once, then compared with each `choice` value in order. The first match executes its block. If no choice matches, the `default` block runs (if present).

```plain
var day = "Monday"
choose day
    choice "Monday"
        display("Start of the week")
    choice "Friday"
        display("Almost weekend!")
    choice "Saturday"
        display("Weekend!")
    choice "Sunday"
        display("Weekend!")
    default
        display("Midweek")
```

**Rules:**
- Each `choice` value should be a literal (string, integer, etc.)
- Only the first matching choice executes (no fall-through)
- The `default` clause is optional but recommended
- There is no limit on the number of `choice` clauses

### 7.3 Loop

PLAIN has four loop variants, all using the `loop` keyword.

#### Infinite Loop

```plain
loop
    statements
```

Repeats forever until `exit` is reached or an error occurs.

#### Conditional Loop (While-Style)

```plain
loop condition
    statements
```

Evaluates the condition before each iteration. The loop continues as long as the condition is `true`.

```plain
var count = 0
loop count < 5
    display(count)
    count = count + 1
```

#### Counting Loop (For-Style)

```plain
loop variable from start to end
    statements

loop variable from start to end step increment
    statements
```

The variable is automatically declared and takes successive values from `start` to `end` (inclusive). The optional `step` specifies the increment (default is 1). Use a negative step to count downward.

```plain
loop i from 1 to 5
    display(i)              rem: displays 1, 2, 3, 4, 5

loop i from 10 to 1 step -2
    display(i)              rem: displays 10, 8, 6, 4, 2
```

The loop variable is **read-only** within the loop body and ceases to exist after the loop ends.

#### Collection Loop (For-Each)

```plain
loop variable in collection
    statements
```

Iterates over each element of a list, or each key of a table.

```plain
var fruits = ["apple", "banana", "cherry"]
loop fruit in fruits
    display(fruit)          rem: displays each fruit

var ages = {"Alice": 30, "Bob": 25}
loop name in keys(ages)
    display(name & ": " & ages[name])
```

### 7.4 Exit and Continue

**`exit`** — Immediately exits the innermost enclosing loop:

```plain
loop i from 1 to 100
    if i > 5
        exit
    display(i)
rem: displays 1, 2, 3, 4, 5
```

**`continue`** — Skips the rest of the current iteration and proceeds to the next:

```plain
loop i from 1 to 10
    if i % 2 == 0
        continue
    display(i)
rem: displays 1, 3, 5, 7, 9 (odd numbers only)
```

Both `exit` and `continue` apply to the **innermost** loop when loops are nested.

---

## 8. Tasks

Tasks are PLAIN's equivalent of functions and procedures. Every PLAIN program must contain a task named `Main` which serves as the entry point.

### 8.1 Procedures (No Parameters)

```plain
task Name()
    statements
```

A simple task with no parameters and no return value. Call it by name with empty parentheses:

```plain
task SayHello()
    display("Hello!")

task Main()
    SayHello()
```

### 8.2 Procedures with Parameters (`with`)

```plain
task Name with (param1, param2, ...)
    statements
```

The `with` keyword indicates a **procedure** — a task that receives parameters but does **not** return a value. Parameters are **immutable** — they cannot be reassigned inside the task body.

```plain
task Greet with (name)
    display("Hello, " & name & "!")

task Main()
    Greet("Alice")
    Greet("Bob")
```

### 8.3 Functions (`using`)

```plain
task Name using (param1, param2, ...)
    statements
    deliver expression
```

The `using` keyword indicates a **function** — a task that receives parameters and **must** return a value via `deliver`. Every code path in a function must reach a `deliver` statement.

```plain
task Add using (a, b)
    deliver a + b

task IsEven using (n)
    deliver n % 2 == 0

task Main()
    var sum = Add(5, 3)         rem: sum = 8
    if IsEven(sum)
        display("even")
```

### 8.4 The `deliver` Statement

`deliver` exits the current function immediately and returns the given value to the caller:

```plain
task Absolute using (n)
    if n < 0
        deliver -n
    deliver n
```

**Rules:**
- `deliver` can only be used inside a task declared with `using`
- A `using` task **must** deliver a value — failing to do so is an error
- `deliver` immediately exits the task; any code after it in the same block is unreachable

### 8.5 The `abort` Statement

`abort` raises a runtime error that propagates up the call stack until caught by `attempt/handle`:

```plain
task Divide using (a, b)
    if b == 0
        abort "Division by zero"
    deliver a / b
```

See [§10 Error Handling](#10-error-handling) for how to catch aborted errors.

### 8.6 Parameter Passing

- Parameters are passed **by value** — modifying a parameter inside the task does not affect the caller's variable
- Parameters are **immutable** — attempting to reassign a parameter is a compile-time error
- PLAIN does not support default parameter values or variable-length argument lists

```plain
task Example with (x)
    x = 5       rem: ERROR — parameters are immutable
```

### 8.7 Task Naming and Definition Order

- Task names follow PascalCase convention: `CalculateAverage`, `IsValid`, `ProcessOrder`
- Tasks can be defined in any order in a file — a task can call another task defined later
- The special task `Main()` is the program's entry point and is called automatically

---

## 9. Records

Records define custom data types with named, typed fields.

### 9.1 Record Definition

```plain
record Name:
    field1 as type
    field2 as type = defaultValue
```

Fields without a default value are **required** — they must be provided when creating an instance. Fields with a default value are **optional**.

```plain
record Person:
    name as string              rem: required
    age as integer = 0          rem: optional, defaults to 0
    email as string = ""        rem: optional, defaults to ""
```

### 9.2 Record Creation

Create a record instance by calling the record name with named arguments:

```plain
var p = Person(name: "Alice", age: 30, email: "alice@example.com")
var q = Person(name: "Bob")     rem: age=0, email="" from defaults
```

**Rules:**
- All **required** fields must be provided (those without defaults)
- Optional fields can be omitted (they get their default values)
- Arguments are named (`field: value`) — positional arguments are not supported
- All arguments must be on a single line

### 9.3 Field Access

Use the dot operator to read and write record fields:

```plain
display(p.name)     rem: "Alice"
display(p.age)      rem: 30

p.age = 31          rem: modify the field
```

### 9.4 Field Types

Record fields support all PLAIN types:

| Type keyword | Field type |
| ------------ | ---------- |
| `string`     | String     |
| `integer`    | Integer    |
| `float`      | Float      |
| `boolean`    | Boolean    |
| `list`       | List       |
| `table`      | Table      |

### 9.5 Record Composition

Records can include fields from other records using `based on` and `with`.

#### `based on` — Inherit with Requirements Preserved

```plain
record Employee:
    based on Person
    salary as float = 0.0
    department as string = ""
```

`based on` includes all fields from the parent record and **preserves** their required/optional status. If `Person.name` is required, it is still required in `Employee`.

#### `with` — Include as All Optional

```plain
record Report:
    title as string
    with Person
    with Address
```

`with` includes all fields from the named record but makes them **all optional** (with their original defaults, or type-appropriate defaults if they had none).

#### Combining Composition

A record can use multiple `based on` and `with` clauses, and define its own fields:

```plain
record Contact:
    name as string
    email as string = ""

record Address:
    street as string = ""
    city as string = ""
    state as string = ""

record FullProfile:
    based on Contact             rem: name required, email optional
    with Address                 rem: street, city, state all optional
    phone as string = ""         rem: own field
```

---

## 10. Error Handling

PLAIN uses `attempt/handle/ensure` for structured error handling, similar to try/catch/finally in other languages.

### 10.1 Basic Structure

```plain
attempt
    statements              rem: code that might fail
handle
    statements              rem: runs if an error occurs
```

The `handle` block executes if any statement in the `attempt` block raises an error (via `abort` or a runtime error like division by zero).

```plain
attempt
    var result = 10 / 0
handle
    display("An error occurred")
```

### 10.2 Pattern Matching Handlers

Multiple `handle` clauses can match specific error messages:

```plain
attempt
    riskyOperation()
handle "file not found"
    display("The file doesn't exist")
handle "permission denied"
    display("Access not allowed")
handle
    display("Some other error occurred")
```

**Rules:**
- Handlers are evaluated in order — the first match wins
- A handler with a string pattern matches if the error message **contains** that string
- A bare `handle` (no pattern) matches any error — use it as a catch-all
- Place specific handlers before general ones

### 10.3 The `ensure` Clause

The `ensure` block always runs, whether or not an error occurred:

```plain
var file = open("data.txt", "r")
attempt
    var content = read(file)
    display(content)
handle
    display("Error reading file")
ensure
    close(file)             rem: always runs — cleanup guaranteed
```

`ensure` is optional. When present, it runs after either the `attempt` body completes normally or after a `handle` block executes.

### 10.4 The `abort` Statement

`abort` raises an error with a message string:

```plain
task ValidateAge with (age)
    if age < 0
        abort "Age cannot be negative"
    if age > 150
        abort "Age seems unrealistic"
```

The error propagates up the call stack until caught by an `attempt/handle` block. If uncaught, the program terminates with an error message.

### 10.5 Nesting

`attempt/handle` blocks can be nested:

```plain
attempt
    attempt
        riskyOperation()
    handle
        display("Inner handler")
        abort "re-raising"
handle
    display("Outer handler")
```

---

## 11. Modules and Imports

### 11.1 Program Structure

A PLAIN program is organized into three levels:

| Level        | Description                   | Analogy           |
| ------------ | ----------------------------- | ----------------- |
| **Assembly** | A package of related modules  | A library/package |
| **Module**   | A single `.plain` source file | A file/module     |
| **Task**     | A function or procedure       | A function        |

### 11.2 The `use:` Statement

The `use:` block at the top of a file declares imports:

```plain
use:
    assemblies:
        io
    modules:
        utils
        io.files
    tasks:
        utils.FormatDate
```

The `use:` block has three optional sections:

| Section       | Purpose                             | Example             |
| ------------- | ----------------------------------- | ------------------- |
| `assemblies:` | Import an entire assembly (package) | `io`                |
| `modules:`    | Import a specific module            | `io.files`, `utils` |
| `tasks:`      | Import a specific task              | `utils.FormatDate`  |

### 11.3 Qualified Names

After importing, you access items using dot notation:

```plain
rem: If you imported the 'utils' module:
utils.FormatDate()
utils.Log("message")

rem: If you imported from an assembly:
io.files.ReadAll("data.txt")

rem: If you imported a specific task:
FormatDate()                rem: can use directly without module prefix
```

### 11.4 File Organization

Organize larger projects into multiple files:

```
my_project/
    main.plain              rem: contains Main() task
    utils.plain             rem: utility functions
    math/
        geometry.plain      rem: geometry functions
        statistics.plain    rem: statistics functions
```

---

## 12. Scope Rules

### 12.1 Scope Levels

PLAIN has four scope levels:

| Level         | Where                               | Lifetime                     |
| ------------- | ----------------------------------- | ---------------------------- |
| **Module**    | Top level of a file                 | Entire program execution     |
| **Task**      | Inside a task body                  | While the task is executing  |
| **Block**     | Inside `if`, `loop`, `choose`, etc. | While the block is executing |
| **Parameter** | Task parameter list                 | While the task is executing  |

### 12.2 No Shadowing

PLAIN prohibits **variable shadowing** — you cannot declare a variable with the same name as one in an enclosing scope:

```plain
var x = 10

task Main()
    var x = 20     rem: ERROR — 'x' already declared in outer scope
```

This prevents a common source of bugs in other languages.

### 12.3 Inner Scope Access

Inner scopes can **read** and **modify** variables from enclosing scopes:

```plain
task Main()
    var count = 0
    loop i from 1 to 5
        count = count + i      rem: modifies Main's 'count'
    display(count)              rem: 15
```

### 12.4 Block Scope Containment

Variables declared inside a block do not exist outside it:

```plain
task Main()
    if true
        var temp = 42
    display(temp)              rem: ERROR — 'temp' not defined here
```

### 12.5 Parameter Immutability

Task parameters are immutable — they cannot be reassigned:

```plain
task Double with (n)
    n = n * 2                  rem: ERROR — cannot reassign parameter
    display(n)
```

To work with a modified copy, declare a local variable:

```plain
task Double with (n)
    var result = n * 2
    display(result)
```

### 12.6 Module Scope

Variables and constants declared at the top level of a file are in **module scope**. They are accessible from all tasks in the same file but are **not global** — they are not visible to other files.

```plain
var version = "1.0"            rem: module-level variable

task Main()
    display(version)           rem: OK — can read module variable
    version = "1.1"            rem: OK — can modify module variable
```

---

## 13. Reserved Words

The following identifiers are reserved and cannot be used as variable, constant, task, or record names:

### Keywords

| Keyword       | Purpose                              |
| ------------- | ------------------------------------ |
| `task`        | Define a task (function/procedure)   |
| `with`        | Declare procedure parameters         |
| `using`       | Declare function parameters          |
| `deliver`     | Return a value from a function       |
| `abort`       | Raise an error                       |
| `var`         | Declare a variable                   |
| `fxd`         | Declare a constant                   |
| `as`          | Specify a type annotation            |
| `if`          | Conditional branch                   |
| `then`        | (Reserved for future single-line if) |
| `else`        | Alternative branch                   |
| `choose`      | Multi-way branch                     |
| `choice`      | A branch option in choose            |
| `default`     | Fallback branch in choose            |
| `loop`        | Start a loop                         |
| `from`        | Start value in counting loop         |
| `to`          | End value in counting loop           |
| `step`        | Increment in counting loop           |
| `in`          | Collection iteration                 |
| `exit`        | Break out of a loop                  |
| `continue`    | Skip to next iteration               |
| `attempt`     | Begin error handling block           |
| `handle`      | Error handler clause                 |
| `ensure`      | Always-execute clause                |
| `use:`        | Begin imports block                  |
| `assemblies:` | Import assemblies                    |
| `modules:`    | Import modules                       |
| `tasks:`      | Import specific tasks                |
| `record`      | Define a record type                 |
| `based`       | Inherit record fields                |
| `on`          | Used with `based`                    |
| `of`          | Element type in typed collections    |
| `rem:`        | Comment (remark)                     |
| `note:`       | Comment (note)                       |

### Type Keywords

| Keyword   | Short Form | Type                   |
| --------- | ---------- | ---------------------- |
| `integer` | `int`      | Integer numbers        |
| `float`   | `flt`      | Floating-point numbers |
| `string`  | `str`      | Text strings           |
| `boolean` | `bln`      | True/false values      |
| `list`    | `lst`      | Ordered collections    |
| `table`   | `tbl`      | Key-value collections  |

### Literal Keywords

| Keyword | Meaning          |
| ------- | ---------------- |
| `true`  | Boolean true     |
| `false` | Boolean false    |
| `null`  | Absence of value |

### Logical Operator Keywords

| Keyword | Meaning     |
| ------- | ----------- |
| `and`   | Logical AND |
| `or`    | Logical OR  |
| `not`   | Logical NOT |

---

## Appendix A: Grammar Summary

This is a simplified grammar for the PLAIN language using EBNF-style notation.

### Program Structure

```
Program        = { Statement NEWLINE } ;
Statement      = TaskDef | RecordDef | VarDecl | FxdDecl | Assignment
               | IfStmt | ChooseStmt | LoopStmt | AttemptStmt
               | DeliverStmt | AbortStmt | ExitStmt | ContinueStmt
               | UseStmt | ExprStmt ;
```

### Declarations

```
VarDecl        = "var" IDENT [ "as" TypeExpr ] "=" Expression ;
FxdDecl        = "fxd" IDENT "as" TypeExpr "=" Expression ;
TypeExpr       = TypeName [ "of" TypeName [ "to" TypeName ] ] ;
TypeName       = "integer" | "float" | "string" | "boolean" | "list" | "table" ;
```

### Task Definitions

```
TaskDef        = "task" IDENT TaskParams NEWLINE INDENT Block DEDENT ;
TaskParams     = "()" | "with" "(" ParamList ")" | "using" "(" ParamList ")" ;
ParamList      = IDENT { "," IDENT } ;
```

### Record Definitions

```
RecordDef      = "record" IDENT ":" NEWLINE INDENT RecordBody DEDENT ;
RecordBody     = { BasedOn | WithClause | FieldDef } ;
BasedOn        = "based" "on" IDENT NEWLINE ;
WithClause     = "with" IDENT NEWLINE ;
FieldDef       = IDENT "as" TypeName [ "=" Expression ] NEWLINE ;
```

### Control Flow

```
IfStmt         = "if" Expression NEWLINE INDENT Block DEDENT
                 [ "else" NEWLINE INDENT Block DEDENT ] ;

ChooseStmt     = "choose" Expression NEWLINE INDENT
                 { "choice" Expression NEWLINE INDENT Block DEDENT }
                 [ "default" NEWLINE INDENT Block DEDENT ]
                 DEDENT ;

LoopStmt       = "loop" LoopSpec NEWLINE INDENT Block DEDENT ;
LoopSpec       = (* empty — infinite loop *)
               | Expression                          (* conditional *)
               | IDENT "from" Expr "to" Expr [ "step" Expr ]  (* counting *)
               | IDENT "in" Expression               (* collection *) ;
```

### Error Handling

```
AttemptStmt    = "attempt" NEWLINE INDENT Block DEDENT
                 { HandleClause }
                 [ "ensure" NEWLINE INDENT Block DEDENT ] ;
HandleClause   = "handle" [ Pattern ] NEWLINE INDENT Block DEDENT ;
Pattern        = STRING | IDENT ;
```

### Imports

```
UseStmt        = "use:" NEWLINE INDENT
                 [ "assemblies:" NEWLINE INDENT { QualName NEWLINE } DEDENT ]
                 [ "modules:" NEWLINE INDENT { QualName NEWLINE } DEDENT ]
                 [ "tasks:" NEWLINE INDENT { QualName NEWLINE } DEDENT ]
                 DEDENT ;
QualName       = IDENT { "." IDENT } ;
```

### Simple Statements

```
Assignment     = LValue AssignOp Expression ;
LValue         = IDENT | IDENT "[" Expression "]" | IDENT "." IDENT ;
AssignOp       = "=" | "+=" | "-=" | "*=" | "/=" | "%=" | "&=" ;
DeliverStmt    = "deliver" Expression ;
AbortStmt      = "abort" Expression ;
ExitStmt       = "exit" ;
ContinueStmt   = "continue" ;
ExprStmt       = Expression ;
```

### Expressions (by precedence, lowest to highest)

```
Expression     = OrExpr ;
OrExpr         = AndExpr { "or" AndExpr } ;
AndExpr        = NotExpr { "and" NotExpr } ;
NotExpr        = "not" NotExpr | Comparison ;
Comparison     = Concat { CompOp Concat } ;
CompOp         = "==" | "!=" | "<" | ">" | "<=" | ">=" ;
Concat         = AddExpr { "&" AddExpr } ;
AddExpr        = MulExpr { ("+" | "-") MulExpr } ;
MulExpr        = Power { ("*" | "/" | "//" | "%") Power } ;
Power          = Unary { "**" Unary } ;
Unary          = "-" Unary | Primary ;
Primary        = INT | FLOAT | STRING | VSTRING | "true" | "false" | "null"
               | IDENT [ "(" [ ArgList ] ")" ]
               | IDENT [ "[" Expression "]" ]
               | IDENT [ "." IDENT ]
               | "(" Expression ")"
               | "[" [ ExprList ] "]"
               | "{" [ PairList ] "}" ;
ArgList        = Expression { "," Expression }
               | IDENT ":" Expression { "," IDENT ":" Expression } ;
ExprList       = Expression { "," Expression } ;
PairList       = Expression ":" Expression { "," Expression ":" Expression } ;
```

### Block

```
Block          = { Statement NEWLINE } ;
```

---

## Appendix B: Common Error Messages

### Parser Errors

| Error Message                        | Meaning                                                            | Fix                                                   |
| ------------------------------------ | ------------------------------------------------------------------ | ----------------------------------------------------- |
| `Expected next token to be X, got Y` | The parser expected a specific token but found something else      | Check syntax near the indicated line                  |
| `No prefix parse function for X`     | An unexpected token appeared where an expression was expected      | Check for misplaced operators or missing values       |
| `Expected INDENT after ...`          | A block-introducing statement wasn't followed by an indented block | Add an indented body after `if`, `loop`, `task`, etc. |

### Analyzer Errors

| Error Message                               | Meaning                                                                    | Fix                                                     |
| ------------------------------------------- | -------------------------------------------------------------------------- | ------------------------------------------------------- |
| `Variable 'X' already declared`             | Attempted to declare a variable that already exists (no shadowing allowed) | Use a different name or assign to the existing variable |
| `Cannot assign Y to variable 'X' of type Z` | Type mismatch on assignment                                                | Ensure the value matches the variable's type            |
| `Variable 'X' not declared`                 | Used a variable that hasn't been declared with `var`                       | Add a `var` declaration before first use                |
| `Cannot assign to parameter 'X'`            | Attempted to modify a task parameter                                       | Copy to a local variable: `var local = X`               |
| `Expected 'deliver' statement in task 'X'`  | A `using` task doesn't return a value on all paths                         | Add `deliver` statements to all code paths              |

### Runtime Errors

| Error Message             | Meaning                                             | Fix                                           |
| ------------------------- | --------------------------------------------------- | --------------------------------------------- |
| `Division by zero`        | Attempted to divide by zero                         | Check the divisor before dividing             |
| `Index out of range`      | List index is negative or >= length                 | Verify index is within `0` to `len(list) - 1` |
| `Key not found: 'X'`      | Table doesn't contain the specified key             | Use `has_key()` to check before accessing     |
| `undefined identifier: X` | Called a task or used a variable that doesn't exist | Check spelling and ensure it's defined        |
| `File not found: X`       | The specified file doesn't exist                    | Verify the file path with `file_exists()`     |
| `Type mismatch`           | An operation received an unexpected type            | Check the types of your operands              |

---

*This is the complete language reference for PLAIN version 1.0. For standard library functions, see [STDLIB.md](STDLIB.md). For tutorial examples, see [TUTORIAL.md](TUTORIAL.md).*
