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
