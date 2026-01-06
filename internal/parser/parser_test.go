package parser

import (
	"plain/internal/lexer"
	"testing"
)

func TestVarStatements(t *testing.T) {
	input := `var x = 5
var y = 10
var name = "Chuck"
var pi as float = 3.14159`

	l := lexer.New(input)
	p := New(l)

	program := p.ParseProgram()
	checkParserErrors(t, p)

	if program == nil {
		t.Fatalf("ParseProgram() returned nil")
	}

	if len(program.Statements) != 4 {
		t.Fatalf("program.Statements does not contain 4 statements. got=%d",
			len(program.Statements))
	}
}

func TestFxdStatements(t *testing.T) {
	input := `fxd MAX_SIZE as int = 100
fxd PI as float = 3.14159`

	l := lexer.New(input)
	p := New(l)

	program := p.ParseProgram()
	checkParserErrors(t, p)

	if program == nil {
		t.Fatalf("ParseProgram() returned nil")
	}

	if len(program.Statements) != 2 {
		t.Fatalf("program.Statements does not contain 2 statements. got=%d",
			len(program.Statements))
	}
}

func TestIntegerLiteralExpression(t *testing.T) {
	input := "5"

	l := lexer.New(input)
	p := New(l)
	program := p.ParseProgram()
	checkParserErrors(t, p)

	if len(program.Statements) != 1 {
		t.Fatalf("program has not enough statements. got=%d",
			len(program.Statements))
	}
}

func TestInfixExpressions(t *testing.T) {
	infixTests := []struct {
		input    string
		expected string
	}{
		{"5 + 5", "(5 + 5)"},
		{"5 - 5", "(5 - 5)"},
		{"5 * 5", "(5 * 5)"},
		{"5 / 5", "(5 / 5)"},
		{"5 > 5", "(5 > 5)"},
		{"5 < 5", "(5 < 5)"},
		{"5 == 5", "(5 == 5)"},
		{"5 != 5", "(5 != 5)"},
		{"5 ** 2", "(5 ** 2)"},
		{"2 ** 3 ** 2", "(2 ** (3 ** 2))"}, // Right associative
	}

	for _, tt := range infixTests {
		l := lexer.New(tt.input)
		p := New(l)
		program := p.ParseProgram()
		checkParserErrors(t, p)

		if len(program.Statements) != 1 {
			t.Fatalf("program.Statements does not contain 1 statement. got=%d",
				len(program.Statements))
		}
	}
}

func TestOperatorPrecedence(t *testing.T) {
	tests := []struct {
		input    string
		expected string
	}{
		{"-a * b", "((-a) * b)"},
		{"a + b + c", "((a + b) + c)"},
		{"a + b - c", "((a + b) - c)"},
		{"a * b * c", "((a * b) * c)"},
		{"a * b / c", "((a * b) / c)"},
		{"a + b / c", "(a + (b / c))"},
		{"a + b * c + d / e - f", "(((a + (b * c)) + (d / e)) - f)"},
		{"3 + 4 * 5 == 3 * 1 + 4 * 5", "((3 + (4 * 5)) == ((3 * 1) + (4 * 5)))"},
	}

	for _, tt := range tests {
		l := lexer.New(tt.input)
		p := New(l)
		program := p.ParseProgram()
		checkParserErrors(t, p)

		if len(program.Statements) != 1 {
			t.Fatalf("program.Statements does not contain 1 statement. got=%d",
				len(program.Statements))
		}
	}
}

func TestIfStatement(t *testing.T) {
	input := `if x > 5
    var y = 10`

	l := lexer.New(input)
	p := New(l)

	program := p.ParseProgram()
	checkParserErrors(t, p)

	if len(program.Statements) != 1 {
		t.Fatalf("program.Statements does not contain 1 statement. got=%d",
			len(program.Statements))
	}
}

func TestTaskStatement(t *testing.T) {
	input := `task Greet with (name)
    show("Hello, " & name)`

	l := lexer.New(input)
	p := New(l)

	program := p.ParseProgram()
	checkParserErrors(t, p)

	if len(program.Statements) != 1 {
		t.Fatalf("program.Statements does not contain 1 statement. got=%d",
			len(program.Statements))
	}
}

func TestTaskVariants(t *testing.T) {
	tests := []struct {
		name     string
		input    string
		expected int // number of statements
	}{
		{
			"procedure no args",
			`task DoSomething()
    display("Hello")`,
			1,
		},
		{
			"procedure with args",
			`task Greet with (name, age)
    display(name)`,
			1,
		},
		{
			"function using args",
			`task Add using (a, b)
    deliver a + b`,
			1,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			l := lexer.New(tt.input)
			p := New(l)
			program := p.ParseProgram()
			checkParserErrors(t, p)

			if len(program.Statements) != tt.expected {
				t.Fatalf("expected %d statements, got=%d", tt.expected, len(program.Statements))
			}
		})
	}
}

func TestLoopStatements(t *testing.T) {
	tests := []struct {
		name  string
		input string
	}{
		{
			"loop from to",
			`loop i from 1 to 10
    display(i)`,
		},
		{
			"loop from to step",
			`loop i from 0 to 100 step 10
    display(i)`,
		},
		{
			"loop in collection",
			`loop item in items
    display(item)`,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			l := lexer.New(tt.input)
			p := New(l)
			program := p.ParseProgram()
			checkParserErrors(t, p)

			if len(program.Statements) != 1 {
				t.Fatalf("expected 1 statement, got=%d", len(program.Statements))
			}
		})
	}
}

func TestChooseStatement(t *testing.T) {
	input := `choose score
    choice 90
        display("A")
    choice 80
        display("B")
    default
        display("F")`

	l := lexer.New(input)
	p := New(l)
	program := p.ParseProgram()
	checkParserErrors(t, p)

	if len(program.Statements) != 1 {
		t.Fatalf("expected 1 statement, got=%d", len(program.Statements))
	}
}

func TestAttemptHandleEnsure(t *testing.T) {
	tests := []struct {
		name  string
		input string
	}{
		{
			"attempt with handle",
			`attempt
    var result = divide(10, 0)
handle
    display("Error occurred")`,
		},
		{
			"attempt with pattern handle",
			`attempt
    var result = divide(10, 0)
handle "division by zero"
    display("Cannot divide by zero")`,
		},
		{
			"attempt with ensure",
			`attempt
    var result = divide(10, 2)
    deliver result
handle
    display("Error")
ensure
    display("Cleanup")`,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			l := lexer.New(tt.input)
			p := New(l)
			program := p.ParseProgram()
			checkParserErrors(t, p)

			if len(program.Statements) != 1 {
				t.Fatalf("expected 1 statement, got=%d", len(program.Statements))
			}
		})
	}
}

func TestRecordDefinitions(t *testing.T) {
	tests := []struct {
		name  string
		input string
	}{
		{
			"simple record",
			`record Person:
    name as string
    age as int`,
		},
		{
			"record with defaults",
			`record Person:
    name as string = ""
    age as int = 0`,
		},
		{
			"record with inheritance",
			`record Employee:
    based on Person
    salary as float`,
		},
		{
			"record with composition",
			`record Manager:
    based on Employee
    with Department
    team_size as int`,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			l := lexer.New(tt.input)
			p := New(l)
			program := p.ParseProgram()
			checkParserErrors(t, p)

			if len(program.Statements) != 1 {
				t.Fatalf("expected 1 statement, got=%d", len(program.Statements))
			}
		})
	}
}

func TestRecordLiterals(t *testing.T) {
	input := `var person = Person(name: "Chuck", age: 63, email: "chuck@plain.org")`

	l := lexer.New(input)
	p := New(l)
	program := p.ParseProgram()
	checkParserErrors(t, p)

	if len(program.Statements) != 1 {
		t.Fatalf("expected 1 statement, got=%d", len(program.Statements))
	}
}

func TestUseStatements(t *testing.T) {
	tests := []struct {
		name  string
		input string
	}{
		{
			"assemblies only",
			`use:
    assemblies:
        System
        System.Collections`,
		},
		{
			"modules only",
			`use:
    modules:
        io
        io.files
        math`,
		},
		{
			"tasks only",
			`use:
    tasks:
        io.files.ReadBinary
        math.advanced.CalculatePI`,
		},
		{
			"all three types",
			`use:
    assemblies:
        System
    modules:
        io
        math
    tasks:
        io.files.ReadBinary`,
		},
		{
			"module with type keyword",
			`use:
    modules:
        string.utils
        int.helpers`,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			l := lexer.New(tt.input)
			p := New(l)
			program := p.ParseProgram()
			checkParserErrors(t, p)

			if len(program.Statements) != 1 {
				t.Fatalf("expected 1 statement, got=%d", len(program.Statements))
			}
		})
	}
}

func TestStringInterpolation(t *testing.T) {
	input := `var greeting = v"Hello, {name}!"`

	l := lexer.New(input)
	p := New(l)
	program := p.ParseProgram()
	checkParserErrors(t, p)

	if len(program.Statements) != 1 {
		t.Fatalf("expected 1 statement, got=%d", len(program.Statements))
	}
}

func TestListAndTableLiterals(t *testing.T) {
	tests := []struct {
		name  string
		input string
	}{
		{
			"list literal",
			`var numbers = [1, 2, 3, 4, 5]`,
		},
		{
			"table literal",
			`var person = {"name": "Chuck", "age": 63}`,
		},
		{
			"nested structures",
			`var data = {"items": [1, 2, 3], "count": 3}`,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			l := lexer.New(tt.input)
			p := New(l)
			program := p.ParseProgram()
			checkParserErrors(t, p)

			if len(program.Statements) != 1 {
				t.Fatalf("expected 1 statement, got=%d", len(program.Statements))
			}
		})
	}
}

func TestNestedBlocks(t *testing.T) {
	input := `if x > 0
    if y > 0
        display("Both positive")
    else
        display("X positive, Y not")
else
    display("X not positive")`

	l := lexer.New(input)
	p := New(l)
	program := p.ParseProgram()
	checkParserErrors(t, p)

	if len(program.Statements) != 1 {
		t.Fatalf("expected 1 statement, got=%d", len(program.Statements))
	}
}

func TestDotExpression(t *testing.T) {
	tests := []struct {
		name  string
		input string
	}{
		{
			"simple dot",
			`var name = person.name`,
		},
		{
			"chained dot",
			`var city = person.address.city`,
		},
		{
			"dot with method call",
			`var result = math.sqrt(16)`,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			l := lexer.New(tt.input)
			p := New(l)
			program := p.ParseProgram()
			checkParserErrors(t, p)

			if len(program.Statements) != 1 {
				t.Fatalf("expected 1 statement, got=%d", len(program.Statements))
			}
		})
	}
}

func TestIndexExpression(t *testing.T) {
	tests := []struct {
		name  string
		input string
	}{
		{
			"array index",
			`var first = numbers[0]`,
		},
		{
			"table index",
			`var name = person["name"]`,
		},
		{
			"chained index",
			`var value = data[0][1]`,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			l := lexer.New(tt.input)
			p := New(l)
			program := p.ParseProgram()
			checkParserErrors(t, p)

			if len(program.Statements) != 1 {
				t.Fatalf("expected 1 statement, got=%d", len(program.Statements))
			}
		})
	}
}

func TestControlFlowStatements(t *testing.T) {
	tests := []struct {
		name  string
		input string
	}{
		{
			"deliver statement",
			`task GetValue using ()
    deliver 42`,
		},
		{
			"abort statement",
			`task CheckValue with (x)
    if x < 0
        abort "Negative value"`,
		},
		{
			"exit statement",
			`loop i from 1 to 100
    if i == 50
        exit`,
		},
		{
			"continue statement",
			`loop i from 1 to 10
    if i % 2 == 0
        continue
    display(i)`,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			l := lexer.New(tt.input)
			p := New(l)
			program := p.ParseProgram()
			checkParserErrors(t, p)

			if len(program.Statements) != 1 {
				t.Fatalf("expected 1 statement, got=%d", len(program.Statements))
			}
		})
	}
}

func TestComplexExpressions(t *testing.T) {
	tests := []struct {
		name  string
		input string
	}{
		{
			"string concatenation",
			`var message = "Hello, " & name & "!"`,
		},
		{
			"boolean operators",
			`var result = x > 0 and y < 10 or z == 5`,
		},
		{
			"mixed operators",
			`var calc = (a + b) * c / d - e`,
		},
		{
			"function call in expression",
			`var result = sqrt(x * x + y * y)`,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			l := lexer.New(tt.input)
			p := New(l)
			program := p.ParseProgram()
			checkParserErrors(t, p)

			if len(program.Statements) != 1 {
				t.Fatalf("expected 1 statement, got=%d", len(program.Statements))
			}
		})
	}
}

func TestAssignmentOperators(t *testing.T) {
	tests := []struct {
		name  string
		input string
	}{
		{"simple assign", `x = 10`},
		{"plus assign", `x += 5`},
		{"minus assign", `x -= 3`},
		{"times assign", `x *= 2`},
		{"div assign", `x /= 4`},
		{"mod assign", `x %= 3`},
		{"concat assign", `message &= " world"`},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			l := lexer.New(tt.input)
			p := New(l)
			program := p.ParseProgram()
			checkParserErrors(t, p)

			if len(program.Statements) != 1 {
				t.Fatalf("expected 1 statement, got=%d", len(program.Statements))
			}
		})
	}
}

func checkParserErrors(t *testing.T, p *Parser) {
	errors := p.Errors()
	if len(errors) == 0 {
		return
	}

	t.Errorf("parser has %d errors", len(errors))
	for _, msg := range errors {
		t.Errorf("parser error: %q", msg)
	}
	t.FailNow()
}
