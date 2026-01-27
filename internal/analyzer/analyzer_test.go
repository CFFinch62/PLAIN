package analyzer

import (
	"plain/internal/lexer"
	"plain/internal/parser"
	"strings"
	"testing"
)

func TestVarDeclarations(t *testing.T) {
	input := `var x = 5
var y = 10
var name = "Chuck"`

	errors := analyzeSource(input)
	if len(errors) > 0 {
		t.Errorf("unexpected errors: %v", errors)
	}
}

func TestFxdDeclarations(t *testing.T) {
	input := `fxd MAX_SIZE as int = 100
fxd PI as float = 3.14159`

	errors := analyzeSource(input)
	if len(errors) > 0 {
		t.Errorf("unexpected errors: %v", errors)
	}
}

func TestNoShadowingSameScope(t *testing.T) {
	input := `var counter = 0
var counter = 1`

	errors := analyzeSource(input)
	if len(errors) != 1 {
		t.Fatalf("expected 1 error, got %d: %v", len(errors), errors)
	}
	if !strings.Contains(errors[0], "already declared") {
		t.Errorf("expected 'already declared' error, got: %s", errors[0])
	}
}

func TestNoShadowingNestedScope(t *testing.T) {
	input := `var counter = 0

task Example()
    var counter = 1`

	errors := analyzeSource(input)
	if len(errors) != 1 {
		t.Fatalf("expected 1 error, got %d: %v", len(errors), errors)
	}
	if !strings.Contains(errors[0], "outer scope") {
		t.Errorf("expected 'outer scope' error, got: %s", errors[0])
	}
}

func TestNoShadowingInBlock(t *testing.T) {
	input := `task Example()
    var total = 0
    if true
        var total = 1`

	errors := analyzeSource(input)
	if len(errors) != 1 {
		t.Fatalf("expected 1 error, got %d: %v", len(errors), errors)
	}
	if !strings.Contains(errors[0], "outer scope") {
		t.Errorf("expected 'outer scope' error, got: %s", errors[0])
	}
}

func TestParameterImmutability(t *testing.T) {
	input := `task Process with (value)
    value = 10`

	errors := analyzeSource(input)
	if len(errors) != 1 {
		t.Fatalf("expected 1 error, got %d: %v", len(errors), errors)
	}
	if !strings.Contains(errors[0], "cannot assign to parameter") {
		t.Errorf("expected 'cannot assign to parameter' error, got: %s", errors[0])
	}
}

func TestConstantImmutability(t *testing.T) {
	input := `fxd MAX_VALUE as int = 100
MAX_VALUE = 200`

	errors := analyzeSource(input)
	if len(errors) != 1 {
		t.Fatalf("expected 1 error, got %d: %v", len(errors), errors)
	}
	if !strings.Contains(errors[0], "cannot assign to constant") {
		t.Errorf("expected 'cannot assign to constant' error, got: %s", errors[0])
	}
}

func TestValidAssignment(t *testing.T) {
	input := `var counter = 0
counter = 10
counter = counter + 1`

	errors := analyzeSource(input)
	if len(errors) > 0 {
		t.Errorf("unexpected errors: %v", errors)
	}
}

func TestNestedScopeAccess(t *testing.T) {
	// Inner scopes should be able to access outer variables
	input := `var outer = 10

task Example()
    var inner = outer + 5
    if true
        var deep = inner + outer`

	errors := analyzeSource(input)
	if len(errors) > 0 {
		t.Errorf("unexpected errors: %v", errors)
	}
}

func TestLoopVariableScope(t *testing.T) {
	input := `task Example()
    loop i from 1 to 10
        display(i)`

	errors := analyzeSource(input)
	if len(errors) > 0 {
		t.Errorf("unexpected errors: %v", errors)
	}
}

func TestMultipleTasks(t *testing.T) {
	// Different tasks can have same local variable names
	input := `task TaskA()
    var result = 1

task TaskB()
    var result = 2`

	errors := analyzeSource(input)
	if len(errors) > 0 {
		t.Errorf("unexpected errors: %v", errors)
	}
}

func TestTaskWithParameters(t *testing.T) {
	input := `task Calculate using (a, b)
    var result = a + b
    deliver result`

	errors := analyzeSource(input)
	if len(errors) > 0 {
		t.Errorf("unexpected errors: %v", errors)
	}
}

func TestChooseStatement(t *testing.T) {
	input := `task Grade with (score)
    choose score
        choice 90
            var grade = "A"
        choice 80
            var grade = "B"
        default
            var grade = "F"`

	errors := analyzeSource(input)
	if len(errors) > 0 {
		t.Errorf("unexpected errors: %v", errors)
	}
}

func TestAttemptStatement(t *testing.T) {
	input := `task SafeOp()
    attempt
        var result = 10
    handle
        var error = "failed"
    ensure
        var cleanup = true`

	errors := analyzeSource(input)
	if len(errors) > 0 {
		t.Errorf("unexpected errors: %v", errors)
	}
}

func TestRecordDefinition(t *testing.T) {
	input := `record Person:
    name as string
    age as int`

	errors := analyzeSource(input)
	if len(errors) > 0 {
		t.Errorf("unexpected errors: %v", errors)
	}
}

func TestDuplicateRecordDefinition(t *testing.T) {
	input := `record Person:
    name as string

record Person:
    age as int`

	errors := analyzeSource(input)
	if len(errors) != 1 {
		t.Fatalf("expected 1 error, got %d: %v", len(errors), errors)
	}
	if !strings.Contains(errors[0], "already declared") {
		t.Errorf("expected 'already declared' error, got: %s", errors[0])
	}
}

func TestDuplicateTaskDefinition(t *testing.T) {
	input := `task Greet()
    display("Hello")

task Greet()
    display("Hi")`

	errors := analyzeSource(input)
	if len(errors) != 1 {
		t.Fatalf("expected 1 error, got %d: %v", len(errors), errors)
	}
	if !strings.Contains(errors[0], "already declared") {
		t.Errorf("expected 'already declared' error, got: %s", errors[0])
	}
}

func TestParameterShadowsModuleVar(t *testing.T) {
	input := `var value = 10

task Process with (value)
    display(value)`

	errors := analyzeSource(input)
	if len(errors) != 1 {
		t.Fatalf("expected 1 error, got %d: %v", len(errors), errors)
	}
	if !strings.Contains(errors[0], "outer scope") {
		t.Errorf("expected 'outer scope' error, got: %s", errors[0])
	}
}

func TestComplexNesting(t *testing.T) {
	input := `var moduleVar = 0

task Process with (param)
    var taskVar = param
    
    loop i from 1 to 10
        var loopVar = i
        if loopVar > 5
            var ifVar = loopVar * 2`

	errors := analyzeSource(input)
	if len(errors) > 0 {
		t.Errorf("unexpected errors: %v", errors)
	}
}

func TestCompoundAssignment(t *testing.T) {
	input := `var counter = 0
counter += 1
counter -= 1
counter *= 2`

	errors := analyzeSource(input)
	if len(errors) > 0 {
		t.Errorf("unexpected errors: %v", errors)
	}
}

// Helper function to parse and analyze source code
func analyzeSource(input string) []string {
	l := lexer.New(input)
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) > 0 {
		return p.Errors()
	}

	a := New()
	return a.Analyze(program)
}
