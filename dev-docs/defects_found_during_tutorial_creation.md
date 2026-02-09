# PLAIN Language — Defects Found During Tutorial Creation

> **Date**: 2026-02-07
> **Context**: These defects were discovered while writing 18 tutorial example programs
> for the user documentation. Each was confirmed by running test cases through
> `go run ./cmd/plain/`. Workarounds were used in the tutorial examples, but these
> should be fixed in the interpreter before first release.

---

## Summary

| # | Severity | Component | Description |
|---|----------|-----------|-------------|
| 1 | **Critical** | Runtime/Evaluator | Compound assignment operators (`+=`, `&=`, etc.) don't accumulate inside loop bodies |
| 2 | **Critical** | Parser | `attempt/handle/ensure` consumes extra DEDENT, silently skips following statement |
| 3 | **High** | Parser/Runtime | `handle error` — no way to capture the error message in a variable |
| 4 | **High** | Runtime | `exit` (break) inside infinite `loop` exits the `if` block, not the loop |
| 5 | **High** | Runtime | `loop` with condition (while-style) doesn't work at runtime |
| 6 | **Medium** | Lexer | `\n` and other escape sequences in string literals are not processed |
| 7 | **Medium** | Parser | String interpolation `v"..."` fails with index/key expressions inside braces |
| 8 | **Medium** | Analyzer | Type-prefixed variables can't be assigned from function return values |
| 9 | ~~**Low**~~ **FIXED** | Parser | `if ... then ...` single-line form doesn't parse despite `then` being a keyword |
| 10 | ~~**Low**~~ **FIXED** | Parser | Multi-line literals (lists, records, function calls spanning lines) cause parse errors |

---

## Defect 1 — Compound Assignment Operators Broken in Loops

**Severity**: Critical
**Component**: `internal/runtime/evaluator.go` (likely)
**Affects**: `+=`, `-=`, `*=`, `/=`, `&=` inside any `loop` body

### Description

When a compound assignment operator like `+=` is used inside a loop body to
accumulate a value, the variable does not retain its updated value across
iterations. Instead, it appears to reset to its pre-loop value each iteration,
so only the last iteration's contribution is kept.

### Reproduction

```plain
task Main()
    var total = 0
    loop i from 1 to 4
        total += i
    display(total)
```

**Expected output**: `10` (1+2+3+4)
**Actual output**: `4` (only the last value)

The same bug affects `&=` for string concatenation:

```plain
task Main()
    var result = ""
    loop i from 1 to 3
        result &= "x"
    display(result)
```

**Expected output**: `xxx`
**Actual output**: `x`

### Proof that the underlying operation works

Using the expanded form `total = total + i` works correctly:

```plain
task Main()
    var total = 0
    loop i from 1 to 4
        total = total + i
    display(total)
```

**Output**: `10` (correct)

### Likely Cause

The compound assignment may be creating a new local binding in the loop body's
scope rather than modifying the variable in the enclosing scope. Or the
implementation may be reading the original value from the outer scope but
writing to a loop-local copy.

### Workaround Used in Tutorials

Replaced all `x += y` with `x = x + y` and `s &= t` with `s = s & t` inside
loop bodies. This affects lessons 5, 6, 7, 9, 11, and 16.

---

## Defect 2 — attempt/handle/ensure Skips the Following Statement

**Severity**: Critical
**Component**: `internal/parser/statements.go`, `parseAttemptStatement()` (~line 211)
**Affects**: Any code following an `attempt/handle` or `attempt/handle/ensure` block

### Description

After an `attempt/handle` block, the **first statement that follows** is
silently skipped (never executed). This also means that if a task's body ends
with an `attempt/handle` block, any task defined after it in the file gets
"swallowed" into the preceding task and becomes unreachable.

### Reproduction — Statement is skipped

```plain
task Main()
    display("before")
    attempt
        display("  in attempt")
    handle
        display("  in handle")
    display("THIS IS SKIPPED")
    display("this prints fine")
```

**Expected output**:
```
before
  in attempt
THIS IS SKIPPED
this prints fine
```

**Actual output**:
```
before
  in attempt
this prints fine
```

The `display("THIS IS SKIPPED")` line is silently lost.

### Reproduction — Tasks swallowed

```plain
task Main()
    display("start")
    TaskA()
    TaskB()

task TaskA()
    attempt
        display("A")
    handle
        display("error")

task TaskB()
    display("B")
```

**Expected output**:
```
start
A
B
```

**Actual output**:
```
start
A
```

Running with `-parse` shows "Successfully parsed 2 statements" — `TaskB` is
parsed as part of `TaskA`'s body. Calling `TaskB()` gives "undefined identifier".

### Root Cause

In `parseAttemptStatement()` (statements.go ~line 259), after parsing each
handler body, the function consumes a DEDENT token to check for additional
`handle` or `ensure` clauses. When there are no more clauses, the function
returns with `curToken` positioned at the **next statement** (one token too
far). Back in `parseBlockStatement()` (parser.go line 721), the standard
`p.nextToken()` call after `parseStatement()` then skips **another** token,
causing the first post-attempt statement to be lost.

Compare with `parseIfStatement()` which correctly leaves `curToken` at the
DEDENT without consuming it, letting `parseBlockStatement` advance past it.

### Workaround Used in Tutorials

1. Placed a sacrificial `display("")` after every `attempt/handle` block
2. Defined all `abort`-throwing tasks **before** `Main()`, and put all
   `attempt/handle` blocks directly inside `Main()` (no separate tasks
   containing `attempt/handle`)

---

## Defect 3 — Cannot Capture Error Message in Handle Block

**Severity**: High
**Component**: `internal/parser/statements.go` (~line 229-246) and `internal/runtime/evaluator.go` (~line 765)
**Affects**: Error handling — ability to display or act on error messages

### Description

There is no working syntax to capture the error message in a `handle` block:

- `handle error` — Parses `error` as a **pattern** (match string), not as a
  variable binding. The handler runs on any error, but the error message is
  not accessible.
- `handle err as string` — Fails to parse because `string` is a `STRING_TYPE`
  token, not an `IDENT` token. The parser at line 238 calls
  `expectPeek(token.IDENT)` which rejects type keywords.

### Reproduction

```plain
task Main()
    attempt
        abort "something bad"
    handle err
        display("caught: " & err)
    display("")
    display("done")
```

**Expected output**:
```
caught: something bad
done
```

**Actual output**:
```
done
```

The handler runs but `err` is undefined inside it, so the display silently
fails, and only "done" prints.

```plain
task Main()
    attempt
        abort "something bad"
    handle err as string
        display("caught: " & err)
    display("")
    display("done")
```

**Output**: Parser error — `Expected next token to be IDENT, got STRING_TYPE`

### Root Cause

Two issues:

1. **Parser**: `handle err` parses `err` as `handler.Pattern` (a match
   expression), not `handler.ErrorName` (a variable binding). The
   `ErrorName` path requires `as TYPE` to follow, but type keywords are not
   IDENT tokens.

2. **Evaluator**: At line 762-768, the evaluator only binds the error message
   when `handler.ErrorName != nil`, which never happens due to issue 1.

### Suggested Fix

Either:
- Accept type keywords (`string`, `integer`, etc.) as valid after `as` in
  handle clauses (change `expectPeek(token.IDENT)` to also accept type tokens)
- Or treat `handle varname` (single identifier, no `as`) as a variable binding
  rather than a pattern match

### Workaround Used in Tutorials

Used `handle` with no variable — the error is caught but the message cannot
be displayed. Tutorial lesson 13 shows generic "Error was caught!" messages
instead of the actual error text.

---

## Defect 4 — `exit` Inside Infinite Loop Exits the Wrong Block

**Severity**: High
**Component**: `internal/runtime/evaluator.go`
**Affects**: `exit` (break) inside `loop` (infinite loop form)

### Description

When `exit` is used inside an `if` block within an infinite `loop`, it exits
the `if` block rather than the loop, causing an infinite loop.

### Reproduction

```plain
task Main()
    var count = 0
    loop
        count = count + 1
        if count >= 5
            exit
        display(count)
    display("Done")
```

**Expected output**:
```
1
2
3
4
Done
```

**Actual output**: Infinite loop — the program never terminates. The `exit`
breaks out of the `if` block and the loop continues forever.

### Likely Cause

The `exit` signal may be caught by the `if` statement evaluator before the
loop evaluator can see it. The `if` block probably returns a normal value
after seeing `exit`, swallowing the break signal.

### Workaround Used in Tutorials

Avoided all infinite `loop` + `exit` patterns entirely. Used only counting
loops (`loop i from ... to ...`) and collection loops (`loop item in list`).

---

## Defect 5 — While-Style Conditional Loop Doesn't Work

**Severity**: High
**Component**: `internal/runtime/evaluator.go` or `internal/parser/`
**Affects**: `loop` with a boolean condition (while-loop form)

### Description

The language spec describes a conditional loop form (`loop condition`), but
it doesn't execute correctly at runtime — it either causes an infinite loop
or doesn't execute the body.

### Reproduction

```plain
task Main()
    var count = 0
    loop count < 5
        display(count)
        count = count + 1
    display("Done")
```

**Expected output**:
```
0
1
2
3
4
Done
```

**Actual output**: Infinite loop or no output (behavior varied during testing).

### Workaround Used in Tutorials

Used counting loops for all bounded repetition. The tutorial does not
demonstrate while-style loops.

---

## Defect 6 — String Escape Sequences Not Processed

**Severity**: Medium
**Component**: `internal/lexer/lexer.go` (string literal parsing)
**Affects**: `\n`, `\t`, `\\`, `\"` and other escape sequences in string literals

### Description

Escape sequences like `\n` and `\t` inside string literals are stored as
the literal two characters `\` and `n` rather than being converted to the
actual newline or tab character.

### Reproduction

```plain
task Main()
    var msg = "Line 1\nLine 2"
    display(msg)
```

**Expected output**:
```
Line 1
Line 2
```

**Actual output**:
```
Line 1\nLine 2
```

Similarly, `\t` displays as `\t` instead of a tab character.

### Workaround Used in Tutorials

- Used `write_lines()` with a list of strings instead of `write_file()` with
  `\n`-separated content
- Avoided `\t` in the multiplication table; used spaces instead
- Used multiple `display()` calls instead of multi-line strings

---

## Defect 7 — String Interpolation Fails with Index/Key Expressions

**Severity**: Medium
**Component**: `internal/lexer/lexer.go` or `internal/parser/` (interpolation parsing)
**Affects**: `v"..."` strings containing `{list[0]}`, `{table["key"]}`, or `{obj.field}`

### Description

String interpolation with `v"..."` works for simple variable names like
`{name}` but fails when the expression inside braces involves indexing
or member access. The expression is rendered literally instead of being
evaluated.

### Reproduction

```plain
task Main()
    var colors = ["red", "green", "blue"]
    display(v"First color: {colors[0]}")
```

**Expected output**: `First color: red`
**Actual output**: `First color: {colors[0]}` (literal text)

### Workaround Used in Tutorials

Used `&` concatenation instead of interpolation for any expression involving
index access:

```plain
var color = colors[0]
display("First color: " & color)
```

Or extracted to a local variable first, then used that in interpolation.

---

## Defect 8 — Type-Prefixed Variables Can't Hold Function Return Values

**Severity**: Medium
**Component**: `internal/analyzer/analyzer.go`
**Affects**: Variables with type prefixes (`int`, `flt`, `str`, `lst`, `tbl`, `bln`) assigned from function calls

### Description

When a variable with a type prefix is assigned the return value of a function,
the semantic analyzer rejects it because it cannot determine the function's
return type at analysis time. The variable's prefix implies a type, but the
analyzer sees the right-hand side as "unknown" type.

### Reproduction

```plain
task GetName using ()
    deliver "Alice"

task Main()
    var strName = GetName()
    display(strName)
```

**Expected**: Runs fine, displays "Alice"
**Actual**: Semantic error — `cannot assign unknown to string variable`

### Workaround Used in Tutorials

Used un-prefixed variable names when assigning from function return values:

```plain
var name = GetName()       rem: Works
var result = Add(5, 3)     rem: Works
var strName = GetName()    rem: ERROR — analyzer rejects this
```

This is unfortunate because it means the naming convention breaks down when
using functions. Either the analyzer needs return-type inference, or it should
allow assigning unknown types to prefixed variables (deferring type checking
to runtime).

---

## Defect 9 — Single-Line `if ... then ...` Not Supported

**Severity**: Low
**Component**: `internal/parser/statements.go`
**Affects**: `if condition then statement` syntax

### Description

The keyword `then` is reserved in the token list, suggesting a planned
single-line `if` form, but the parser doesn't implement it. Using `then`
causes a parse error.

### Reproduction

```plain
task Main()
    var x = 10
    if x > 5 then display("big")
```

**Output**: Parser error

### Workaround Used in Tutorials

Used the block form for all conditionals:

```plain
if x > 5
    display("big")
```

### Note

This is low priority — the block form works fine. But if `then` is a reserved
keyword, it should either be implemented or removed from the keyword list to
avoid confusion.

---

## Defect 10 — Multi-Line Literals Cause Parse Errors

**Severity**: Low
**Component**: `internal/parser/` (expression parsing across newlines)
**Affects**: List literals, record creation, and function calls that span multiple lines

### Description

The parser does not support expressions that span multiple lines. A list
literal or record creation that is split across lines causes a parse error.

### Reproduction

```plain
task Main()
    var colors = [
        "red",
        "green",
        "blue"
    ]
    display(colors)
```

**Output**: Parser error — `No prefix parse function for NEWLINE`

### Workaround Used in Tutorials

Kept all list literals, record creation expressions, and function calls on
a single line:

```plain
var colors = ["red", "green", "blue"]
var student = Student(name: "Alice", age: 20, grade: "A")
```

### Note

This is low priority for short programs but becomes a readability issue for
longer lists or records with many fields.

---

## Priority Recommendation

For the first release, I recommend fixing in this order:

1. **Defect 1** (compound assignment in loops) — This is the most impactful bug.
   Every program that accumulates values in a loop will hit it. It undermines
   trust in basic language operations.

2. **Defect 2** (attempt/handle DEDENT) — This makes error handling nearly
   unusable. Tasks with attempt/handle cause all subsequent tasks to become
   unreachable.

3. **Defect 3** (error message capture) — Without this, error handling is
   limited to "an error happened" with no details. Essential for real programs.

4. **Defects 4 & 5** (loop exit/while) — These prevent two of the four loop
   forms from working. The counting and collection loops work, but infinite
   and conditional loops are broken.

5. **Defect 6** (escape sequences) — Important for any string-heavy program
   or file I/O. Without `\n`, you can't build multi-line strings.

6. **Defects 7 & 8** (interpolation/type prefixes) — Usability issues that
   force awkward workarounds.

7. **Defects 9 & 10** (single-line if/multi-line literals) — Nice to have
   but not blocking.

---

## Fixes Applied

### Defect 9 — Single-Line `if ... then ...` — FIXED (2026-02-09)

**Status**: Fixed and tested

**Files Modified**:
- `internal/parser/statements.go` — `parseIfStatement()` function (lines 8-64)

**Implementation**:
The single-line `if ... then ...` form was already implemented but not documented as working. The parser correctly handles:
- `if condition then statement` — single-line form
- `if condition then statement else statement` — single-line form with else
- Block form continues to work as before

**Test Coverage**:
- `tests/test_defect9_if_then.plain` — Basic single-line if forms
- `tests/test_defects_9_10_comprehensive.plain` — Integration with multi-line literals

---

### Defect 10 — Multi-Line Literals — FIXED (2026-02-09)

**Status**: Fixed and tested

**Files Modified**:
- `internal/parser/parser.go`:
  - `skipNewlines()` (line 187-191) — Enhanced to skip NEWLINE, INDENT, and DEDENT tokens
  - `parseExpressionList()` (line 377-403) — Refactored to handle multi-line expressions
  - `parseTableLiteral()` (line 405-447) — Refactored to handle multi-line table literals

**Root Cause**:
When the lexer encountered indented content inside delimiters (`[`, `{`, `(`), it produced INDENT and DEDENT tokens along with NEWLINE tokens. The parser's `skipNewlines()` function only skipped NEWLINE tokens, causing "No prefix parse function for NEWLINE/INDENT/DEDENT" errors.

**Implementation**:
1. Enhanced `skipNewlines()` to skip NEWLINE, INDENT, and DEDENT tokens
2. Refactored `parseExpressionList()` to properly advance through tokens and skip whitespace at the right points
3. Refactored `parseTableLiteral()` to follow the same pattern

**Supported Multi-Line Forms**:
```plain
# List literals
var colors = [
    "red",
    "green",
    "blue"
]

# Table literals
var person = {
    "name": "Alice",
    "age": 30
}

# Nested structures
var data = [
    {
        "id": 1,
        "name": "Alice"
    },
    {
        "id": 2,
        "name": "Bob"
    }
]

# Function calls
display(
    "This is a long message"
)
```

**Test Coverage**:
- `tests/test_defect10_multiline.plain` — Multi-line lists, tables, and function calls
- `tests/test_defects_9_10_comprehensive.plain` — Nested multi-line structures, empty lists, integration with single-line if
- All existing defect tests continue to pass, confirming no regressions

**Limitations**:
- Trailing commas are not supported (intentional design decision)
- Multi-line structures must be properly indented according to PLAIN's indentation rules
