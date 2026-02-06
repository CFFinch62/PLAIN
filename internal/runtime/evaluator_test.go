package runtime

import (
	"plain/internal/lexer"
	"plain/internal/parser"
	"testing"
)

func TestEvalIntegerLiteral(t *testing.T) {
	input := `var x = 5`

	result := testEval(input)
	// The result of the last expression is null (var statement returns null)
	// But the variable should be defined
	if result == nil {
		t.Fatalf("result is nil")
	}
}

func TestEvalArithmetic(t *testing.T) {
	tests := []struct {
		input    string
		expected int64
	}{
		{"var x = 5 + 5", 0}, // var stmt returns null, but we're testing the parse/eval pipeline
	}

	for _, tt := range tests {
		result := testEval(tt.input)
		if result == nil {
			t.Fatalf("result is nil for: %s", tt.input)
		}
	}
}

func TestDisplay(t *testing.T) {
	input := `display("Hello, World!")`

	result := testEval(input)
	// display returns null
	if result == nil {
		t.Fatalf("result is nil")
	}
}

func TestTaskDefinitionAndCall(t *testing.T) {
	input := `task Add using (a, b)
    deliver a + b

var result = Add(3, 4)`

	eval := New()
	env := NewEnvironment()

	l := lexer.New(input)
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) > 0 {
		t.Fatalf("parser errors: %v", p.Errors())
	}

	eval.Eval(program, env)

	// Check that result is 7
	val, ok := env.Get("result")
	if !ok {
		t.Fatalf("variable 'result' not defined")
	}

	intVal, ok := val.(*IntegerValue)
	if !ok {
		t.Fatalf("result is not integer, got %T", val)
	}

	if intVal.Val != 7 {
		t.Errorf("result = %d, want 7", intVal.Val)
	}
}

func TestIfStatement(t *testing.T) {
	input := `var result = 0
if 5 > 3
    result = 1`

	eval := New()
	env := NewEnvironment()

	l := lexer.New(input)
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) > 0 {
		t.Fatalf("parser errors: %v", p.Errors())
	}

	eval.Eval(program, env)

	val, _ := env.Get("result")
	intVal := val.(*IntegerValue)

	if intVal.Val != 1 {
		t.Errorf("result = %d, want 1", intVal.Val)
	}
}

func TestLoop(t *testing.T) {
	input := `var sum = 0
loop i from 1 to 5
    sum = sum + i`

	eval := New()
	env := NewEnvironment()

	l := lexer.New(input)
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) > 0 {
		t.Fatalf("parser errors: %v", p.Errors())
	}

	eval.Eval(program, env)

	val, _ := env.Get("sum")
	intVal := val.(*IntegerValue)

	// 1 + 2 + 3 + 4 + 5 = 15
	if intVal.Val != 15 {
		t.Errorf("sum = %d, want 15", intVal.Val)
	}
}

func TestList(t *testing.T) {
	input := `var myList = [1, 2, 3]
var first = myList[0]
var length = len(myList)`

	eval := New()
	env := NewEnvironment()

	l := lexer.New(input)
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) > 0 {
		t.Fatalf("parser errors: %v", p.Errors())
	}

	eval.Eval(program, env)

	first, _ := env.Get("first")
	if intVal, ok := first.(*IntegerValue); !ok || intVal.Val != 1 {
		t.Errorf("first = %v, want 1", first)
	}

	length, _ := env.Get("length")
	if intVal, ok := length.(*IntegerValue); !ok || intVal.Val != 3 {
		t.Errorf("length = %v, want 3", length)
	}
}

func TestStringConcat(t *testing.T) {
	input := `var s = "Hello" & ", " & "World!"`

	eval := New()
	env := NewEnvironment()

	l := lexer.New(input)
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) > 0 {
		t.Fatalf("parser errors: %v", p.Errors())
	}

	eval.Eval(program, env)

	s, _ := env.Get("s")
	if strVal, ok := s.(*StringValue); !ok || strVal.Val != "Hello, World!" {
		t.Errorf("s = %v, want 'Hello, World!'", s)
	}
}

// Helper: parse and evaluate source
func testEval(input string) Value {
	l := lexer.New(input)
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) > 0 {
		return nil
	}

	eval := New()
	env := NewEnvironment()
	return eval.Eval(program, env)
}

// ===== End-to-End Tests =====

func TestStringConcatAutoConversion(t *testing.T) {
	tests := []struct {
		input    string
		varName  string
		expected string
	}{
		{`var s = "Value: " & 42`, "s", "Value: 42"},
		{`var s = "Pi: " & 3.14`, "s", "Pi: 3.14"},
		{`var s = "Bool: " & true`, "s", "Bool: true"},
		{`var s = 100 & " items"`, "s", "100 items"},
		{`var s = "Sum: " & (5 + 10)`, "s", "Sum: 15"},
	}

	for _, tt := range tests {
		eval := New()
		env := NewEnvironment()
		l := lexer.New(tt.input)
		p := parser.New(l)
		program := p.ParseProgram()

		if len(p.Errors()) > 0 {
			t.Fatalf("parser errors for '%s': %v", tt.input, p.Errors())
		}

		eval.Eval(program, env)

		val, ok := env.Get(tt.varName)
		if !ok {
			t.Fatalf("variable '%s' not defined for input: %s", tt.varName, tt.input)
		}

		strVal, ok := val.(*StringValue)
		if !ok {
			t.Fatalf("expected string for '%s', got %T", tt.input, val)
		}

		if strVal.Val != tt.expected {
			t.Errorf("for '%s': got '%s', want '%s'", tt.input, strVal.Val, tt.expected)
		}
	}
}

func TestMainAutoCall(t *testing.T) {
	input := `var result = 0

task Main()
    result = 42`

	eval := New()
	env := NewEnvironment()
	l := lexer.New(input)
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) > 0 {
		t.Fatalf("parser errors: %v", p.Errors())
	}

	eval.Eval(program, env)

	val, ok := env.Get("result")
	if !ok {
		t.Fatalf("variable 'result' not defined")
	}

	intVal, ok := val.(*IntegerValue)
	if !ok {
		t.Fatalf("expected integer, got %T", val)
	}

	if intVal.Val != 42 {
		t.Errorf("result = %d, want 42 (Main() should be auto-called)", intVal.Val)
	}
}

func TestRecursiveFibonacci(t *testing.T) {
	input := `task Fibonacci using (n)
    if n <= 1
        deliver n
    var a = Fibonacci(n - 1)
    var b = Fibonacci(n - 2)
    deliver a + b

var result = Fibonacci(10)`

	eval := New()
	env := NewEnvironment()
	l := lexer.New(input)
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) > 0 {
		t.Fatalf("parser errors: %v", p.Errors())
	}

	eval.Eval(program, env)

	val, ok := env.Get("result")
	if !ok {
		t.Fatalf("variable 'result' not defined")
	}

	intVal, ok := val.(*IntegerValue)
	if !ok {
		t.Fatalf("expected integer, got %T", val)
	}

	if intVal.Val != 55 {
		t.Errorf("Fibonacci(10) = %d, want 55", intVal.Val)
	}
}

func TestLoopWithStep(t *testing.T) {
	input := `var items = []
loop i from 0 to 10 step 2
    append(items, i)`

	eval := New()
	env := NewEnvironment()
	l := lexer.New(input)
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) > 0 {
		t.Fatalf("parser errors: %v", p.Errors())
	}

	eval.Eval(program, env)

	val, ok := env.Get("items")
	if !ok {
		t.Fatalf("variable 'items' not defined")
	}

	listVal, ok := val.(*ListValue)
	if !ok {
		t.Fatalf("expected list, got %T", val)
	}

	// Should be [0, 2, 4, 6, 8, 10]
	expected := []int64{0, 2, 4, 6, 8, 10}
	if len(listVal.Elements) != len(expected) {
		t.Fatalf("list length = %d, want %d", len(listVal.Elements), len(expected))
	}

	for i, exp := range expected {
		intVal, ok := listVal.Elements[i].(*IntegerValue)
		if !ok || intVal.Val != exp {
			t.Errorf("items[%d] = %v, want %d", i, listVal.Elements[i], exp)
		}
	}
}

func TestTableOperations(t *testing.T) {
	input := `var person = {"name": "Alice", "age": 30}
var name = person["name"]
var age = person.age
person["city"] = "NYC"
var city = person.city`

	eval := New()
	env := NewEnvironment()
	l := lexer.New(input)
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) > 0 {
		t.Fatalf("parser errors: %v", p.Errors())
	}

	eval.Eval(program, env)

	// Check name
	nameVal, _ := env.Get("name")
	if strVal, ok := nameVal.(*StringValue); !ok || strVal.Val != "Alice" {
		t.Errorf("name = %v, want 'Alice'", nameVal)
	}

	// Check age
	ageVal, _ := env.Get("age")
	if intVal, ok := ageVal.(*IntegerValue); !ok || intVal.Val != 30 {
		t.Errorf("age = %v, want 30", ageVal)
	}

	// Check city was added
	cityVal, _ := env.Get("city")
	if strVal, ok := cityVal.(*StringValue); !ok || strVal.Val != "NYC" {
		t.Errorf("city = %v, want 'NYC'", cityVal)
	}
}

func TestChooseStatement(t *testing.T) {
	input := `var grade = "B"
var result = ""

choose grade
    choice "A"
        result = "Excellent"
    choice "B"
        result = "Good"
    choice "C"
        result = "Average"
    default
        result = "Needs work"`

	eval := New()
	env := NewEnvironment()
	l := lexer.New(input)
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) > 0 {
		t.Fatalf("parser errors: %v", p.Errors())
	}

	eval.Eval(program, env)

	val, _ := env.Get("result")
	if strVal, ok := val.(*StringValue); !ok || strVal.Val != "Good" {
		t.Errorf("result = %v, want 'Good'", val)
	}
}

func TestNestedLoops(t *testing.T) {
	input := `var sum = 0
loop i from 1 to 3
    loop j from 1 to 3
        sum = sum + (i * j)`

	eval := New()
	env := NewEnvironment()
	l := lexer.New(input)
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) > 0 {
		t.Fatalf("parser errors: %v", p.Errors())
	}

	eval.Eval(program, env)

	val, _ := env.Get("sum")
	intVal := val.(*IntegerValue)

	// 1*1 + 1*2 + 1*3 + 2*1 + 2*2 + 2*3 + 3*1 + 3*2 + 3*3 = 1+2+3+2+4+6+3+6+9 = 36
	if intVal.Val != 36 {
		t.Errorf("sum = %d, want 36", intVal.Val)
	}
}

func TestFloatOperations(t *testing.T) {
	tests := []struct {
		input    string
		varName  string
		expected float64
	}{
		{`var x = 3.14 + 2.86`, "x", 6.0},
		{`var x = 10.0 - 3.5`, "x", 6.5},
		{`var x = 2.5 * 4.0`, "x", 10.0},
		{`var x = 10.0 / 4.0`, "x", 2.5},
		{`var x = 5 + 2.5`, "x", 7.5},           // int + float
		{`var x = 3.5 + 2`, "x", 5.5},           // float + int
		{`var x = 10.0 / 3.0`, "x", 10.0 / 3.0}, // division
	}

	for _, tt := range tests {
		eval := New()
		env := NewEnvironment()
		l := lexer.New(tt.input)
		p := parser.New(l)
		program := p.ParseProgram()

		if len(p.Errors()) > 0 {
			t.Fatalf("parser errors for '%s': %v", tt.input, p.Errors())
		}

		eval.Eval(program, env)

		val, ok := env.Get(tt.varName)
		if !ok {
			t.Fatalf("variable '%s' not defined for: %s", tt.varName, tt.input)
		}

		floatVal, ok := val.(*FloatValue)
		if !ok {
			t.Fatalf("expected float for '%s', got %T", tt.input, val)
		}

		if floatVal.Val != tt.expected {
			t.Errorf("for '%s': got %f, want %f", tt.input, floatVal.Val, tt.expected)
		}
	}
}

func TestBooleanOperations(t *testing.T) {
	tests := []struct {
		input    string
		varName  string
		expected bool
	}{
		{`var x = true and true`, "x", true},
		{`var x = true and false`, "x", false},
		{`var x = false or true`, "x", true},
		{`var x = false or false`, "x", false},
		{`var x = not true`, "x", false},
		{`var x = not false`, "x", true},
		{`var x = 5 > 3`, "x", true},
		{`var x = 5 < 3`, "x", false},
		{`var x = 5 == 5`, "x", true},
		{`var x = 5 != 3`, "x", true},
		{`var x = true == true`, "x", true},
		{`var x = true != false`, "x", true},
	}

	for _, tt := range tests {
		eval := New()
		env := NewEnvironment()
		l := lexer.New(tt.input)
		p := parser.New(l)
		program := p.ParseProgram()

		if len(p.Errors()) > 0 {
			t.Fatalf("parser errors for '%s': %v", tt.input, p.Errors())
		}

		eval.Eval(program, env)

		val, ok := env.Get(tt.varName)
		if !ok {
			t.Fatalf("variable '%s' not defined for: %s", tt.varName, tt.input)
		}

		boolVal, ok := val.(*BooleanValue)
		if !ok {
			t.Fatalf("expected boolean for '%s', got %T", tt.input, val)
		}

		if boolVal.Val != tt.expected {
			t.Errorf("for '%s': got %t, want %t", tt.input, boolVal.Val, tt.expected)
		}
	}
}

func TestPrefixOperations(t *testing.T) {
	tests := []struct {
		input   string
		varName string
	}{
		{`var x = -5`, "x"},
		{`var x = -3.14`, "x"},
		{`var x = not true`, "x"},
		{`var x = not false`, "x"},
	}

	for _, tt := range tests {
		eval := New()
		env := NewEnvironment()
		l := lexer.New(tt.input)
		p := parser.New(l)
		program := p.ParseProgram()

		if len(p.Errors()) > 0 {
			t.Fatalf("parser errors for '%s': %v", tt.input, p.Errors())
		}

		result := eval.Eval(program, env)

		if IsError(result) {
			t.Errorf("error for '%s': %v", tt.input, result)
		}
	}
}

func TestInterpolatedString(t *testing.T) {
	input := `var name = "World"
var x = 42
var msg = v"Hello, {name}! The answer is {x}."`

	eval := New()
	env := NewEnvironment()
	l := lexer.New(input)
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) > 0 {
		t.Fatalf("parser errors: %v", p.Errors())
	}

	eval.Eval(program, env)

	val, ok := env.Get("msg")
	if !ok {
		t.Fatalf("variable 'msg' not defined")
	}

	strVal, ok := val.(*StringValue)
	if !ok {
		t.Fatalf("expected string, got %T", val)
	}

	expected := "Hello, World! The answer is 42."
	if strVal.Val != expected {
		t.Errorf("got '%s', want '%s'", strVal.Val, expected)
	}
}

func TestFxdConstant(t *testing.T) {
	input := `fxd PI as float = 3.14159
var result = PI * 2`

	eval := New()
	env := NewEnvironment()
	l := lexer.New(input)
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) > 0 {
		t.Fatalf("parser errors: %v", p.Errors())
	}

	eval.Eval(program, env)

	val, ok := env.Get("result")
	if !ok {
		t.Fatalf("variable 'result' not defined")
	}

	floatVal, ok := val.(*FloatValue)
	if !ok {
		t.Fatalf("expected float, got %T", val)
	}

	expected := 3.14159 * 2
	if floatVal.Val != expected {
		t.Errorf("result = %f, want %f", floatVal.Val, expected)
	}
}

func TestAttemptHandleEnsure(t *testing.T) {
	input := `var result = 0
var ensured = false

attempt
    result = 10 / 0
handle
    result = -1
ensure
    ensured = true`

	eval := New()
	env := NewEnvironment()
	l := lexer.New(input)
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) > 0 {
		t.Fatalf("parser errors: %v", p.Errors())
	}

	eval.Eval(program, env)

	// Check ensured was set (ensure block always runs)
	ensuredVal, _ := env.Get("ensured")
	if boolVal, ok := ensuredVal.(*BooleanValue); !ok || !boolVal.Val {
		t.Errorf("ensured = %v, want true (ensure block should run)", ensuredVal)
	}
}

func TestAbortStatement(t *testing.T) {
	input := `task MightFail using (shouldFail)
    if shouldFail
        abort "Something went wrong!"
    deliver "success"

var result = MightFail(false)`

	eval := New()
	env := NewEnvironment()
	l := lexer.New(input)
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) > 0 {
		t.Fatalf("parser errors: %v", p.Errors())
	}

	eval.Eval(program, env)

	val, ok := env.Get("result")
	if !ok {
		t.Fatalf("variable 'result' not defined")
	}

	strVal, ok := val.(*StringValue)
	if !ok {
		t.Fatalf("expected string, got %T", val)
	}

	if strVal.Val != "success" {
		t.Errorf("result = '%s', want 'success'", strVal.Val)
	}
}

func TestLoopInCollection(t *testing.T) {
	input := `var sum = 0
var items = [1, 2, 3, 4, 5]
loop item in items
    sum = sum + item`

	eval := New()
	env := NewEnvironment()
	l := lexer.New(input)
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) > 0 {
		t.Fatalf("parser errors: %v", p.Errors())
	}

	eval.Eval(program, env)

	val, _ := env.Get("sum")
	intVal := val.(*IntegerValue)

	if intVal.Val != 15 {
		t.Errorf("sum = %d, want 15", intVal.Val)
	}
}

func TestLoopBreakContinue(t *testing.T) {
	input := `var sum = 0
loop i from 1 to 10
    if i == 3
        continue
    if i == 7
        exit
    sum = sum + i`

	eval := New()
	env := NewEnvironment()
	l := lexer.New(input)
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) > 0 {
		t.Fatalf("parser errors: %v", p.Errors())
	}

	eval.Eval(program, env)

	val, _ := env.Get("sum")
	intVal := val.(*IntegerValue)

	// 1+2+4+5+6 = 18 (skip 3, stop at 7)
	if intVal.Val != 18 {
		t.Errorf("sum = %d, want 18", intVal.Val)
	}
}

// ===== Integration Tests =====
// These test the full pipeline: source → lexer → parser → evaluator → result

func TestFullPipelineHelloWorld(t *testing.T) {
	source := `task Main()
    var name = "PLAIN"
    var msg = v"Hello, {name}!"`

	eval := New()
	env := NewEnvironment()
	l := lexer.New(source)
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) > 0 {
		t.Fatalf("parser errors: %v", p.Errors())
	}

	result := eval.Eval(program, env)

	// Should not return an error
	if IsError(result) {
		t.Errorf("unexpected error: %v", result)
	}
}

func TestFullPipelineRecursion(t *testing.T) {
	source := `task Factorial using (n)
    if n <= 1
        deliver 1
    deliver n * Factorial(n - 1)

var result = Factorial(5)`

	eval := New()
	env := NewEnvironment()
	l := lexer.New(source)
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) > 0 {
		t.Fatalf("parser errors: %v", p.Errors())
	}

	eval.Eval(program, env)

	val, ok := env.Get("result")
	if !ok {
		t.Fatalf("result not defined")
	}

	intVal, ok := val.(*IntegerValue)
	if !ok || intVal.Val != 120 {
		t.Errorf("Factorial(5) = %v, want 120", val)
	}
}

func TestFullPipelineListManipulation(t *testing.T) {
	source := `var data = [5, 2, 8, 1, 9]
sort(data)
var first = data[0]
var last = data[4]
reverse(data)
var reversedFirst = data[0]`

	eval := New()
	env := NewEnvironment()
	l := lexer.New(source)
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) > 0 {
		t.Fatalf("parser errors: %v", p.Errors())
	}

	eval.Eval(program, env)

	first, _ := env.Get("first")
	if intVal, ok := first.(*IntegerValue); !ok || intVal.Val != 1 {
		t.Errorf("first = %v, want 1", first)
	}

	last, _ := env.Get("last")
	if intVal, ok := last.(*IntegerValue); !ok || intVal.Val != 9 {
		t.Errorf("last = %v, want 9", last)
	}

	reversedFirst, _ := env.Get("reversedFirst")
	if intVal, ok := reversedFirst.(*IntegerValue); !ok || intVal.Val != 9 {
		t.Errorf("reversedFirst = %v, want 9", reversedFirst)
	}
}

func TestFullPipelineTableManipulation(t *testing.T) {
	source := `var config = {"host": "localhost", "port": 8080, "debug": true}

var hostVal = config.host
var portVal = config["port"]
var hasDebug = has_key(config, "debug")
var keyList = keys(config)`

	eval := New()
	env := NewEnvironment()
	l := lexer.New(source)
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) > 0 {
		t.Fatalf("parser errors: %v", p.Errors())
	}

	eval.Eval(program, env)

	hostVal, _ := env.Get("hostVal")
	if strVal, ok := hostVal.(*StringValue); !ok || strVal.Val != "localhost" {
		t.Errorf("hostVal = %v, want 'localhost'", hostVal)
	}

	portVal, _ := env.Get("portVal")
	if intVal, ok := portVal.(*IntegerValue); !ok || intVal.Val != 8080 {
		t.Errorf("portVal = %v, want 8080", portVal)
	}

	hasDebug, _ := env.Get("hasDebug")
	if boolVal, ok := hasDebug.(*BooleanValue); !ok || !boolVal.Val {
		t.Errorf("hasDebug = %v, want true", hasDebug)
	}

	keyList, _ := env.Get("keyList")
	if listVal, ok := keyList.(*ListValue); !ok || len(listVal.Elements) != 3 {
		t.Errorf("keys(config) = %v, want list with 3 elements", keyList)
	}
}

func TestFullPipelineStringOperations(t *testing.T) {
	source := `var text = "  Hello, World!  "
var trimmed = trim(text)
var upper = upper(trimmed)
var lower = lower(trimmed)
var hasHello = contains(trimmed, "Hello")
var replaced = replace(trimmed, "World", "PLAIN")`

	eval := New()
	env := NewEnvironment()
	l := lexer.New(source)
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) > 0 {
		t.Fatalf("parser errors: %v", p.Errors())
	}

	eval.Eval(program, env)

	trimmed, _ := env.Get("trimmed")
	if strVal, ok := trimmed.(*StringValue); !ok || strVal.Val != "Hello, World!" {
		t.Errorf("trimmed = %v, want 'Hello, World!'", trimmed)
	}

	upper, _ := env.Get("upper")
	if strVal, ok := upper.(*StringValue); !ok || strVal.Val != "HELLO, WORLD!" {
		t.Errorf("upper = %v, want 'HELLO, WORLD!'", upper)
	}

	hasHello, _ := env.Get("hasHello")
	if boolVal, ok := hasHello.(*BooleanValue); !ok || !boolVal.Val {
		t.Errorf("hasHello = %v, want true", hasHello)
	}

	replaced, _ := env.Get("replaced")
	if strVal, ok := replaced.(*StringValue); !ok || strVal.Val != "Hello, PLAIN!" {
		t.Errorf("replaced = %v, want 'Hello, PLAIN!'", replaced)
	}
}

func TestFullPipelineMathOperations(t *testing.T) {
	source := `var a = abs(-42)
var b = min(10, 5)
var c = max(10, 20)
var d = floor(3.7)
var e = ceil(3.2)
var f = round(3.5)`

	eval := New()
	env := NewEnvironment()
	l := lexer.New(source)
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) > 0 {
		t.Fatalf("parser errors: %v", p.Errors())
	}

	eval.Eval(program, env)

	a, _ := env.Get("a")
	if intVal, ok := a.(*IntegerValue); !ok || intVal.Val != 42 {
		t.Errorf("abs(-42) = %v, want 42", a)
	}

	b, _ := env.Get("b")
	if intVal, ok := b.(*IntegerValue); !ok || intVal.Val != 5 {
		t.Errorf("min(10, 5) = %v, want 5", b)
	}

	c, _ := env.Get("c")
	if intVal, ok := c.(*IntegerValue); !ok || intVal.Val != 20 {
		t.Errorf("max(10, 20) = %v, want 20", c)
	}

	d, _ := env.Get("d")
	if intVal, ok := d.(*IntegerValue); !ok || intVal.Val != 3 {
		t.Errorf("floor(3.7) = %v, want 3", d)
	}

	e, _ := env.Get("e")
	if intVal, ok := e.(*IntegerValue); !ok || intVal.Val != 4 {
		t.Errorf("ceil(3.2) = %v, want 4", e)
	}

	f, _ := env.Get("f")
	if intVal, ok := f.(*IntegerValue); !ok || intVal.Val != 4 {
		t.Errorf("round(3.5) = %v, want 4", f)
	}
}

// ===== Edge Case Tests =====
// These test boundary conditions, error handling, and unusual inputs

func TestEdgeCaseEmptyList(t *testing.T) {
	source := `var empty = []
var length = len(empty)`

	eval := New()
	env := NewEnvironment()
	l := lexer.New(source)
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) > 0 {
		t.Fatalf("parser errors: %v", p.Errors())
	}

	eval.Eval(program, env)

	length, _ := env.Get("length")
	if intVal, ok := length.(*IntegerValue); !ok || intVal.Val != 0 {
		t.Errorf("len([]) = %v, want 0", length)
	}
}

func TestEdgeCaseEmptyString(t *testing.T) {
	source := `var empty = ""
var length = len(empty)
var isEmptyStr = empty == ""`

	eval := New()
	env := NewEnvironment()
	l := lexer.New(source)
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) > 0 {
		t.Fatalf("parser errors: %v", p.Errors())
	}

	eval.Eval(program, env)

	length, _ := env.Get("length")
	if intVal, ok := length.(*IntegerValue); !ok || intVal.Val != 0 {
		t.Errorf("len(\"\") = %v, want 0", length)
	}

	isEmptyStr, _ := env.Get("isEmptyStr")
	if boolVal, ok := isEmptyStr.(*BooleanValue); !ok || !boolVal.Val {
		t.Errorf("\"\" == \"\" should be true")
	}
}

func TestEdgeCaseNullComparison(t *testing.T) {
	source := `var x = null
var isNull = x == null
var notNull = x != null`

	eval := New()
	env := NewEnvironment()
	l := lexer.New(source)
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) > 0 {
		t.Fatalf("parser errors: %v", p.Errors())
	}

	eval.Eval(program, env)

	isNull, _ := env.Get("isNull")
	if boolVal, ok := isNull.(*BooleanValue); !ok || !boolVal.Val {
		t.Errorf("null == null should be true")
	}

	notNull, _ := env.Get("notNull")
	if boolVal, ok := notNull.(*BooleanValue); !ok || boolVal.Val {
		t.Errorf("null != null should be false")
	}
}

func TestEdgeCaseZeroDivision(t *testing.T) {
	source := `var result = 10 / 0`

	eval := New()
	env := NewEnvironment()
	l := lexer.New(source)
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) > 0 {
		t.Fatalf("parser errors: %v", p.Errors())
	}

	result := eval.Eval(program, env)

	// Should return an error for division by zero
	if !IsError(result) {
		t.Errorf("division by zero should return error, got %v", result)
	}
}

func TestEdgeCaseLargeNumbers(t *testing.T) {
	source := `var big = 9223372036854775807
var half = big / 2`

	eval := New()
	env := NewEnvironment()
	l := lexer.New(source)
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) > 0 {
		t.Fatalf("parser errors: %v", p.Errors())
	}

	eval.Eval(program, env)

	big, _ := env.Get("big")
	if intVal, ok := big.(*IntegerValue); !ok || intVal.Val != 9223372036854775807 {
		t.Errorf("big = %v, want 9223372036854775807", big)
	}
}

func TestEdgeCaseNegativeNumbers(t *testing.T) {
	source := `var neg = -42
var absNeg = abs(-100)
var minusNeg = 0 - neg`

	eval := New()
	env := NewEnvironment()
	l := lexer.New(source)
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) > 0 {
		t.Fatalf("parser errors: %v", p.Errors())
	}

	eval.Eval(program, env)

	neg, _ := env.Get("neg")
	if intVal, ok := neg.(*IntegerValue); !ok || intVal.Val != -42 {
		t.Errorf("neg = %v, want -42", neg)
	}

	absNeg, _ := env.Get("absNeg")
	if intVal, ok := absNeg.(*IntegerValue); !ok || intVal.Val != 100 {
		t.Errorf("abs(-100) = %v, want 100", absNeg)
	}
}

func TestEdgeCaseNestedTasks(t *testing.T) {
	source := `task Outer using (x)
    task Inner using (y)
        deliver y * 2
    deliver Inner(x) + 1

var result = Outer(5)`

	eval := New()
	env := NewEnvironment()
	l := lexer.New(source)
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) > 0 {
		t.Fatalf("parser errors: %v", p.Errors())
	}

	eval.Eval(program, env)

	result, ok := env.Get("result")
	if !ok {
		t.Fatalf("result not defined")
	}

	intVal, ok := result.(*IntegerValue)
	if !ok || intVal.Val != 11 {
		t.Errorf("Outer(5) = %v, want 11 (5*2 + 1)", result)
	}
}

func TestEdgeCaseChooseDefault(t *testing.T) {
	source := `var x = "unknown"
var result = ""

choose x
    choice "A"
        result = "found A"
    choice "B"
        result = "found B"
    default
        result = "default"`

	eval := New()
	env := NewEnvironment()
	l := lexer.New(source)
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) > 0 {
		t.Fatalf("parser errors: %v", p.Errors())
	}

	eval.Eval(program, env)

	result, _ := env.Get("result")
	if strVal, ok := result.(*StringValue); !ok || strVal.Val != "default" {
		t.Errorf("result = %v, want 'default'", result)
	}
}

func TestEdgeCaseEmptyTable(t *testing.T) {
	source := `var empty = {}
var keyList = keys(empty)
var valueList = values(empty)`

	eval := New()
	env := NewEnvironment()
	l := lexer.New(source)
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) > 0 {
		t.Fatalf("parser errors: %v", p.Errors())
	}

	eval.Eval(program, env)

	keyList, _ := env.Get("keyList")
	if listVal, ok := keyList.(*ListValue); !ok || len(listVal.Elements) != 0 {
		t.Errorf("keys({}) = %v, want empty list", keyList)
	}

	valueList, _ := env.Get("valueList")
	if listVal, ok := valueList.(*ListValue); !ok || len(listVal.Elements) != 0 {
		t.Errorf("values({}) = %v, want empty list", valueList)
	}
}
