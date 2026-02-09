# PLAIN Language Testing Strategy

**For AI-Assisted Implementation**

This document provides a comprehensive testing approach for implementing PLAIN.

---

## Testing Philosophy

**Goals:**
1. Verify correctness against specification
2. Catch regressions early
3. Document expected behavior
4. Support refactoring with confidence
5. Provide examples for users

**Principles:**
- Test behavior, not implementation
- One assertion per test when possible
- Descriptive test names
- Isolated tests (no dependencies)
- Fast execution

---

## Test Categories

### 1. Unit Tests
Test individual components in isolation.

**Components to test:**
- Lexer (tokenization)
- Parser (AST generation)
- Type checker (type validation)
- Scope manager (variable tracking)
- Runtime (execution)
- Each stdlib function

**Example Test Structure:**
```go
func TestLexerTokenizesInteger(t *testing.T) {
    input := "42"
    tokens := Tokenize(input)
    
    if len(tokens) != 1 {
        t.Fatalf("Expected 1 token, got %d", len(tokens))
    }
    
    if tokens[0].Type != INTEGER {
        t.Errorf("Expected INTEGER token, got %v", tokens[0].Type)
    }
    
    if tokens[0].Value != "42" {
        t.Errorf("Expected value '42', got '%s'", tokens[0].Value)
    }
}
```

### 2. Integration Tests
Test component interactions.

**Integration Points:**
- Lexer → Parser
- Parser → Type Checker
- Type Checker → Runtime
- Runtime → Stdlib
- Full pipeline (source → execution)

### 3. End-to-End Tests
Test complete PLAIN programs.

**Example Programs:**
- Hello World
- Fibonacci sequence
- File processing
- Timer/event examples
- Record composition
- Module imports

### 4. Error Tests
Test error handling and messages.

**Error Categories:**
- Syntax errors
- Type errors
- Scope errors
- Runtime errors
- File I/O errors

---

## Test Case Templates

### Lexer Test Template

```go
func TestLexer[Feature](t *testing.T) {
    testCases := []struct{
        name     string
        input    string
        expected []Token
    }{
        {
            name: "[description]",
            input: "[PLAIN code]",
            expected: []Token{
                {Type: [TYPE], Value: "[value]"},
                // ...
            },
        },
    }
    
    for _, tc := range testCases {
        t.Run(tc.name, func(t *testing.T) {
            tokens := Tokenize(tc.input)
            
            if !equalTokens(tokens, tc.expected) {
                t.Errorf("Got %v, expected %v", tokens, tc.expected)
            }
        })
    }
}
```

**Lexer Test Cases:**

```
Feature: Keywords
Input: "var task if loop"
Expected: [VAR, TASK, IF, LOOP]

Feature: Integer literals
Input: "42 -17 0"
Expected: [INTEGER(42), INTEGER(-17), INTEGER(0)]

Feature: Float literals
Input: "3.14 -2.5 0.0"
Expected: [FLOAT(3.14), FLOAT(-2.5), FLOAT(0.0)]

Feature: String literals
Input: '"hello" "world"'
Expected: [STRING("hello"), STRING("world")]

Feature: Interpolated strings
Input: 'v"Hello {name}"'
Expected: [INTERP_START, STRING("Hello "), LBRACE, IDENT("name"), RBRACE, INTERP_END]

Feature: Comments
Input: "var x rem: comment\nvar y"
Expected: [VAR, IDENT("x"), NEWLINE, VAR, IDENT("y")]

Feature: Indentation
Input: "if true\n    x = 1\n    y = 2\nz = 3"
Expected: [IF, TRUE, NEWLINE, INDENT, IDENT("x"), ..., DEDENT, ...]

Feature: Operators
Input: "+ - * / // % ** & == != < > <= >="
Expected: [PLUS, MINUS, MULT, DIV, INTDIV, MOD, POW, CONCAT, EQ, NEQ, LT, GT, LE, GE]

Feature: Multi-line comment
Input: "note:\n    comment\n    text\nvar x"
Expected: [VAR, IDENT("x")]
```

### Parser Test Template

```go
func TestParser[Construct](t *testing.T) {
    input := `
    [PLAIN code]
    `
    
    ast, err := Parse(input)
    if err != nil {
        t.Fatalf("Parse error: %v", err)
    }
    
    // Verify AST structure
    if [condition] {
        t.Errorf("Expected [structure], got [actual]")
    }
}
```

**Parser Test Cases:**

```
Feature: Variable declaration with inference
Input: "var intCount = 42"
AST: VarDecl{Name: "intCount", Type: IntegerType, Value: IntLiteral(42)}

Feature: Variable declaration with explicit type
Input: "var count as integer = 42"
AST: VarDecl{Name: "count", Type: IntegerType, Value: IntLiteral(42)}

Feature: Task with no parameters
Input: "task Hello()\n    display('Hi')"
AST: TaskDecl{Name: "Hello", Params: [], Body: [...]}

Feature: Task with 'with' parameters
Input: "task Process with (x, y)\n    display(x)"
AST: TaskDecl{Name: "Process", ParamType: With, Params: ["x", "y"], ...}

Feature: Task with 'using' parameters
Input: "task Add using (a, b)\n    deliver a + b"
AST: TaskDecl{Name: "Add", ParamType: Using, Params: ["a", "b"], ...}

Feature: If statement
Input: "if x > 5\n    y = 10"
AST: IfStmt{Condition: BinOp(...), ThenBlock: [...], ElseBlock: nil}

Feature: If-else statement  
Input: "if x > 5\n    y = 10\nelse\n    y = 0"
AST: IfStmt{Condition: ..., ThenBlock: [...], ElseBlock: [...]}

Feature: Choose statement
Input: "choose x\n    choice 'a'\n        y = 1\n    default\n        y = 0"
AST: ChooseStmt{Expr: Ident("x"), Cases: [...], Default: [...]}

Feature: Loop infinite
Input: "loop\n    work()"
AST: LoopStmt{Type: Infinite, Body: [...]}

Feature: Loop conditional
Input: "loop x < 10\n    work()"
AST: LoopStmt{Type: Conditional, Condition: BinOp(...), Body: [...]}

Feature: Loop counting
Input: "loop i from 1 to 10\n    work()"
AST: LoopStmt{Type: Counting, Var: "i", From: 1, To: 10, Body: [...]}

Feature: Loop collection
Input: "loop item in items\n    work(item)"
AST: LoopStmt{Type: Collection, Var: "item", Collection: Ident("items"), Body: [...]}

Feature: Attempt/handle
Input: "attempt\n    risky()\nhandle error\n    fix()"
AST: TryStmt{Body: [...], Handlers: [...], Ensure: nil}

Feature: Record definition
Input: "record Person:\n    name as string\n    age as integer = 0"
AST: RecordDecl{Name: "Person", Fields: [...]}

Feature: Record composition
Input: "record Full:\n    based on Contact\n    with Address"
AST: RecordDecl{Name: "Full", BasedOn: ["Contact"], With: ["Address"], ...}

Feature: Operator precedence
Input: "x = 2 + 3 * 4"
AST: Assign{Var: "x", Value: BinOp{Op: PLUS, Left: 2, Right: BinOp{Op: MULT, Left: 3, Right: 4}}}

Feature: Exponentiation associativity  
Input: "x = 2 ** 3 ** 2"
AST: Assign{Var: "x", Value: BinOp{Op: POW, Left: 2, Right: BinOp{Op: POW, Left: 3, Right: 2}}}
```

### Type Checker Test Template

```go
func TestTypeChecker[Feature](t *testing.T) {
    input := `[PLAIN code]`
    
    ast, _ := Parse(input)
    typeChecker := NewTypeChecker()
    
    err := typeChecker.Check(ast)
    
    if [should_pass] && err != nil {
        t.Errorf("Expected to pass, got error: %v", err)
    }
    
    if [should_fail] && err == nil {
        t.Error("Expected type error, got none")
    }
}
```

**Type Checker Test Cases:**

```
Feature: Type inference from prefix
Input: "var intCount = 42"
Result: PASS (infers integer type)

Feature: Type mismatch in assignment
Input: "var intCount = 'text'"
Result: FAIL (string assigned to integer variable)

Feature: Explicit type validation
Input: "var count as integer = 42"
Result: PASS

Feature: Explicit type mismatch
Input: "var count as integer = 'text'"
Result: FAIL

Feature: Record field types
Input: "record Person:\n    name as string\nvar p = Person(name: 42)"
Result: FAIL (integer passed to string field)

Feature: Typed list validation
Input: "var nums as list of integer = [1, 2, 'three']"
Result: FAIL (string in integer list)

Feature: Operation type checking
Input: "var x = 'hello' + 5"
Result: FAIL (cannot add string and integer)

Feature: Task using must deliver
Input: "task Add using (a, b)\n    var c = a + b"
Result: FAIL (missing deliver statement)

Feature: Task with cannot deliver
Input: "task Process with (x)\n    deliver x"
Result: FAIL (with task cannot deliver)

Feature: No shadowing
Input: "var x = 1\nif true\n    var x = 2"
Result: FAIL (x already declared in outer scope)

Feature: Parameter immutability
Input: "task Test with (x)\n    x = x + 1"
Result: FAIL (cannot assign to parameter)

Feature: Record composition type conflict
Input: "record A:\n    name as string\nrecord B:\n    name as integer\nrecord C:\n    based on A\n    with B"
Result: FAIL (field 'name' has conflicting types)
```

### Runtime Test Template

```go
func TestRuntime[Feature](t *testing.T) {
    input := `[PLAIN code]`
    
    result, err := Execute(input)
    
    if err != nil {
        t.Fatalf("Runtime error: %v", err)
    }
    
    if result != [expected] {
        t.Errorf("Expected %v, got %v", [expected], result)
    }
}
```

**Runtime Test Cases:**

```
Feature: Variable assignment
Input: "var x = 42\ndeliver x"
Output: 42

Feature: Arithmetic operations
Input: "deliver 2 + 3 * 4"
Output: 14

Feature: String concatenation
Input: "deliver 'Hello' & ' ' & 'World'"
Output: "Hello World"

Feature: String interpolation
Input: "var name = 'Chuck'\ndeliver v'Hello {name}'"
Output: "Hello Chuck"

Feature: If statement true
Input: "var x = 0\nif true\n    x = 10\ndeliver x"
Output: 10

Feature: If statement false
Input: "var x = 0\nif false\n    x = 10\ndeliver x"
Output: 0

Feature: Loop counting
Input: "var sum = 0\nloop i from 1 to 5\n    sum += i\ndeliver sum"
Output: 15

Feature: Loop collection
Input: "var sum = 0\nloop n in [1,2,3]\n    sum += n\ndeliver sum"
Output: 6

Feature: Task call
Input: "task Add using (a, b)\n    deliver a + b\ndeliver Add(2, 3)"
Output: 5

Feature: Record creation
Input: "record Person:\n    name as string\n    age as integer = 0\nvar p = Person(name: 'Chuck')\ndeliver p.age"
Output: 0

Feature: Abort handling
Input: "attempt\n    abort 'error'\nhandle 'error'\n    deliver 42"
Output: 42

Feature: Ensure execution
Input: "var x = 0\nattempt\n    deliver 1\nensure\n    x = 99"
Note: x should be 99 after execution

Feature: Scope isolation
Input: "var x = 1\nif true\n    var y = 2\ndeliver x"
Output: 1 (y not accessible)

Feature: Scope mutation
Input: "var x = 1\nif true\n    x = 2\ndeliver x"
Output: 2 (x mutated)
```

### Standard Library Test Template

```go
func TestStdlib[Function](t *testing.T) {
    testCases := []struct{
        name     string
        input    interface{}
        expected interface{}
        shouldErr bool
    }{
        {
            name: "[description]",
            input: [value],
            expected: [result],
            shouldErr: false,
        },
    }
    
    for _, tc := range testCases {
        t.Run(tc.name, func(t *testing.T) {
            result, err := [Function](tc.input)
            
            if tc.shouldErr && err == nil {
                t.Error("Expected error, got none")
            }
            
            if !tc.shouldErr && err != nil {
                t.Errorf("Unexpected error: %v", err)
            }
            
            if result != tc.expected {
                t.Errorf("Expected %v, got %v", tc.expected, result)
            }
        })
    }
}
```

**Standard Library Test Cases:**

```
Function: len(string)
Input: "hello"
Output: 5

Function: upper(string)
Input: "hello"
Output: "HELLO"

Function: split(string, delimiter)
Input: "a,b,c", ","
Output: ["a", "b", "c"]

Function: abs(number)
Input: -5
Output: 5

Function: sqrt(number)
Input: 16
Output: 4.0

Function: round(number)
Input: 3.7
Output: 4

Function: to_int(string)
Input: "42"
Output: 42

Function: to_int(invalid)
Input: "abc"
Error: "Cannot convert 'abc' to integer"

Function: append(list, item)
Input: [1, 2], 3
Output: [1, 2, 3]

Function: keys(table)
Input: {"a": 1, "b": 2}
Output: ["a", "b"]

Function: file_exists(path)
Input: "nonexistent.txt"
Output: false
```

---

## Error Message Testing

**Template:**
```go
func TestError[Scenario](t *testing.T) {
    input := `[PLAIN code that should error]`
    
    _, err := Execute(input)
    
    if err == nil {
        t.Fatal("Expected error, got none")
    }
    
    if !strings.Contains(err.Error(), "[expected message part]") {
        t.Errorf("Error message missing expected content: %v", err)
    }
}
```

**Error Message Test Cases:**

```
Scenario: Missing deliver in 'using' task
Input: "task Add using (a, b)\n    var c = a + b"
Expected: "Expected 'deliver' statement in task 'Add'"

Scenario: Shadowing attempt
Input: "var x = 1\nif true\n    var x = 2"
Expected: "Variable 'x' already declared"

Scenario: Type mismatch
Input: "var intCount = 'text'"
Expected: "Cannot assign string to variable 'intCount' of type integer"

Scenario: File not found
Input: "read_file('nonexistent.txt')"
Expected: "File not found: nonexistent.txt"

Scenario: Parameter mutation
Input: "task Test with (x)\n    x = 5"
Expected: "Cannot assign to parameter 'x'"

Scenario: Undefined variable
Input: "deliver undefinedVar"
Expected: "Undefined variable 'undefinedVar'"

Scenario: Record field conflict
Input: "record A:\n    name as string\nrecord B:\n    name as integer\nrecord C:\n    based on A\n    with B"
Expected: "field 'name' exists in both"
```

---

## End-to-End Test Examples

### Example 1: Hello World
```plain
task Main()
    display("Hello, World!")
```
**Expected:** Outputs "Hello, World!"

### Example 2: Fibonacci
```plain
task Fibonacci using (n)
    if n <= 1
        deliver n
    deliver Fibonacci(n - 1) + Fibonacci(n - 2)

task Main()
    loop i from 0 to 10
        display(v"Fib({i}) = {Fibonacci(i)}")
```
**Expected:** Outputs Fibonacci sequence 0-10

### Example 3: File Processing
```plain
task Main()
    var lstLines = read_lines("data.txt")
    var count = 0
    
    loop line in lstLines
        if contains(line, "ERROR")
            count += 1
    
    display(v"Found {count} errors")
```
**Expected:** Counts "ERROR" in file

### Example 4: Timer Example
```plain
var tickCount = 0

task OnTick()
    tickCount += 1
    display(v"Tick {tickCount}")
    
    if tickCount >= 5
        stop_events()

task Main()
    var timer = create_timer(1000, OnTick)
    start_timer(timer)
    wait_for_events()
    display("Done!")
```
**Expected:** Ticks 5 times then stops

### Example 5: Record Usage
```plain
record Person:
    name as string
    age as integer = 0

task Main()
    var person = Person(name: "Chuck", age: 63)
    display(v"{person.name} is {person.age} years old")
```
**Expected:** Outputs "Chuck is 63 years old"

---

## Test Coverage Goals

### Minimum Coverage
- [ ] All keywords tokenized
- [ ] All syntax constructs parsed
- [ ] All type rules enforced
- [ ] All control flow executed
- [ ] All stdlib functions tested
- [ ] All error cases handled

### Comprehensive Coverage
- [ ] Edge cases for each feature
- [ ] Integration between features
- [ ] Performance benchmarks
- [ ] Stress tests (deep nesting, large files)
- [ ] Concurrent timer execution
- [ ] Memory leak detection

---

## Performance Testing

### Benchmarks to Create

```go
func BenchmarkLexer(b *testing.B) {
    input := [large source code]
    for i := 0; i < b.N; i++ {
        Tokenize(input)
    }
}

func BenchmarkParser(b *testing.B) {
    tokens := [pre-tokenized]
    for i := 0; i < b.N; i++ {
        Parse(tokens)
    }
}

func BenchmarkExecution(b *testing.B) {
    ast := [pre-parsed]
    for i := 0; i < b.N; i++ {
        Execute(ast)
    }
}
```

**Performance Goals:**
- Lexer: >10k lines/sec
- Parser: >5k lines/sec
- Execution: Comparable to Python

---

## Test Automation

### Continuous Integration
```yaml
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-go@v2
      - run: go test ./...
      - run: go test -race ./...
      - run: go test -coverprofile=coverage.out ./...
```

### Pre-commit Hooks
```bash
#!/bin/bash
go fmt ./...
go vet ./...
go test ./...
```

---

## AI Assistance Prompts for Testing

### Generate Tests
```
I need tests for [COMPONENT/FEATURE].

According to the spec:
[RELEVANT SPECIFICATION]

Please create tests covering:
1. Happy path: [NORMAL USAGE]
2. Error cases: [FAILURE SCENARIOS]
3. Edge cases: [BOUNDARY CONDITIONS]

Use the test template from testing_strategy.md.
```

### Review Test Coverage
```
Here are my current tests for [COMPONENT]:
[LIST OF TESTS]

According to the spec, [COMPONENT] should handle:
[REQUIREMENTS]

What test cases am I missing?
```

### Debug Failing Test
```
This test is failing:
[TEST CODE]

Expected: [EXPECTED BEHAVIOR]
Actual: [ACTUAL BEHAVIOR]

The spec says: [RELEVANT SECTION]

What's wrong?
```

---

## Test Documentation

Each test should include:

```go
// TestFeatureName verifies that [component] correctly [behavior]
// according to [spec section].
//
// Example:
//   Input:  [sample input]
//   Output: [expected output]
//
// Error cases:
//   - [error scenario 1]
//   - [error scenario 2]
func TestFeatureName(t *testing.T) {
    // ...
}
```

---

## Quick Test Checklist

For each new feature:

- [ ] Write tests FIRST (TDD when possible)
- [ ] Test happy path
- [ ] Test error cases
- [ ] Test edge cases
- [ ] Test integration with other features
- [ ] Verify error messages are helpful
- [ ] Check test coverage (aim for >80%)
- [ ] Add to CI pipeline
- [ ] Document test rationale

---

**Remember:** Good tests are the specification in executable form!
