package lexer

import (
	"plain/internal/token"
	"testing"
)

func TestNextToken_Keywords(t *testing.T) {
	input := `task var fxd if then else choose choice default
loop from to in exit continue
attempt handle ensure
use: assemblies: modules: tasks:
record based on
integer float string boolean list table of
true false null
and or not
with using deliver abort`

	tests := []struct {
		expectedType    token.TokenType
		expectedLiteral string
	}{
		{token.TASK, "task"},
		{token.VAR, "var"},
		{token.FXD, "fxd"},
		{token.IF, "if"},
		{token.THEN, "then"},
		{token.ELSE, "else"},
		{token.CHOOSE, "choose"},
		{token.CHOICE, "choice"},
		{token.DEFAULT, "default"},
		{token.NEWLINE, "\n"},
		{token.LOOP, "loop"},
		{token.FROM, "from"},
		{token.TO, "to"},
		{token.IN, "in"},
		{token.EXIT, "exit"},
		{token.CONTINUE, "continue"},
		{token.NEWLINE, "\n"},
		{token.ATTEMPT, "attempt"},
		{token.HANDLE, "handle"},
		{token.ENSURE, "ensure"},
		{token.NEWLINE, "\n"},
		{token.USE, "use:"},
		{token.ASSEMBLIES, "assemblies:"},
		{token.MODULES, "modules:"},
		{token.TASKS, "tasks:"},
		{token.NEWLINE, "\n"},
		{token.RECORD, "record"},
		{token.BASED, "based"},
		{token.ON, "on"},
		{token.NEWLINE, "\n"},
		{token.INTEGER, "integer"},
		{token.FLOAT_TYPE, "float"},
		{token.STRING_TYPE, "string"},
		{token.BOOLEAN, "boolean"},
		{token.LIST, "list"},
		{token.TABLE, "table"},
		{token.OF, "of"},
		{token.NEWLINE, "\n"},
		{token.TRUE, "true"},
		{token.FALSE, "false"},
		{token.NULL, "null"},
		{token.NEWLINE, "\n"},
		{token.AND, "and"},
		{token.OR, "or"},
		{token.NOT, "not"},
		{token.NEWLINE, "\n"},
		{token.WITH, "with"},
		{token.USING, "using"},
		{token.DELIVER, "deliver"},
		{token.ABORT, "abort"},
		{token.EOF, ""},
	}

	l := New(input)

	for i, tt := range tests {
		tok := l.NextToken()

		if tok.Type != tt.expectedType {
			t.Fatalf("tests[%d] - tokentype wrong. expected=%q, got=%q (literal=%q)",
				i, tt.expectedType, tok.Type, tok.Literal)
		}

		if tok.Literal != tt.expectedLiteral {
			t.Fatalf("tests[%d] - literal wrong. expected=%q, got=%q",
				i, tt.expectedLiteral, tok.Literal)
		}
	}
}

func TestNextToken_Operators(t *testing.T) {
	input := `+ - * / // % **
== != < > <= >=
= += -= *= /= %= &=
& ( ) [ ] { } , : .`

	tests := []struct {
		expectedType    token.TokenType
		expectedLiteral string
	}{
		{token.PLUS, "+"},
		{token.MINUS, "-"},
		{token.ASTERISK, "*"},
		{token.SLASH, "/"},
		{token.INTDIV, "//"},
		{token.PERCENT, "%"},
		{token.POWER, "**"},
		{token.NEWLINE, "\n"},
		{token.EQ, "=="},
		{token.NEQ, "!="},
		{token.LT, "<"},
		{token.GT, ">"},
		{token.LTE, "<="},
		{token.GTE, ">="},
		{token.NEWLINE, "\n"},
		{token.ASSIGN, "="},
		{token.PLUS_EQ, "+="},
		{token.MINUS_EQ, "-="},
		{token.TIMES_EQ, "*="},
		{token.DIV_EQ, "/="},
		{token.MOD_EQ, "%="},
		{token.CONCAT_EQ, "&="},
		{token.NEWLINE, "\n"},
		{token.AMPERSAND, "&"},
		{token.LPAREN, "("},
		{token.RPAREN, ")"},
		{token.LBRACKET, "["},
		{token.RBRACKET, "]"},
		{token.LBRACE, "{"},
		{token.RBRACE, "}"},
		{token.COMMA, ","},
		{token.COLON, ":"},
		{token.DOT, "."},
		{token.EOF, ""},
	}

	l := New(input)

	for i, tt := range tests {
		tok := l.NextToken()

		if tok.Type != tt.expectedType {
			t.Fatalf("tests[%d] - tokentype wrong. expected=%q, got=%q",
				i, tt.expectedType, tok.Type)
		}

		if tok.Literal != tt.expectedLiteral {
			t.Fatalf("tests[%d] - literal wrong. expected=%q, got=%q",
				i, tt.expectedLiteral, tok.Literal)
		}
	}
}

func TestNextToken_Numbers(t *testing.T) {
	input := `42 3.14 2.5e10 1.5E-5 0 0.0`

	tests := []struct {
		expectedType    token.TokenType
		expectedLiteral string
	}{
		{token.INT, "42"},
		{token.FLOAT, "3.14"},
		{token.FLOAT, "2.5e10"},
		{token.FLOAT, "1.5E-5"},
		{token.INT, "0"},
		{token.FLOAT, "0.0"},
		{token.EOF, ""},
	}

	l := New(input)

	for i, tt := range tests {
		tok := l.NextToken()

		if tok.Type != tt.expectedType {
			t.Fatalf("tests[%d] - tokentype wrong. expected=%q, got=%q",
				i, tt.expectedType, tok.Type)
		}

		if tok.Literal != tt.expectedLiteral {
			t.Fatalf("tests[%d] - literal wrong. expected=%q, got=%q",
				i, tt.expectedLiteral, tok.Literal)
		}
	}
}

func TestNextToken_Strings(t *testing.T) {
	input := `"hello" "world with spaces" v"interpolated {name}"`

	tests := []struct {
		expectedType    token.TokenType
		expectedLiteral string
	}{
		{token.STRING, "hello"},
		{token.STRING, "world with spaces"},
		{token.VSTRING, "interpolated {name}"},
		{token.EOF, ""},
	}

	l := New(input)

	for i, tt := range tests {
		tok := l.NextToken()

		if tok.Type != tt.expectedType {
			t.Fatalf("tests[%d] - tokentype wrong. expected=%q, got=%q",
				i, tt.expectedType, tok.Type)
		}

		if tok.Literal != tt.expectedLiteral {
			t.Fatalf("tests[%d] - literal wrong. expected=%q, got=%q",
				i, tt.expectedLiteral, tok.Literal)
		}
	}
}

func TestNextToken_Identifiers(t *testing.T) {
	input := `myVar _private count123 MyTask`

	tests := []struct {
		expectedType    token.TokenType
		expectedLiteral string
	}{
		{token.IDENT, "myVar"},
		{token.IDENT, "_private"},
		{token.IDENT, "count123"},
		{token.IDENT, "MyTask"},
		{token.EOF, ""},
	}

	l := New(input)

	for i, tt := range tests {
		tok := l.NextToken()

		if tok.Type != tt.expectedType {
			t.Fatalf("tests[%d] - tokentype wrong. expected=%q, got=%q",
				i, tt.expectedType, tok.Type)
		}

		if tok.Literal != tt.expectedLiteral {
			t.Fatalf("tests[%d] - literal wrong. expected=%q, got=%q",
				i, tt.expectedLiteral, tok.Literal)
		}
	}
}

func TestNextToken_Comments(t *testing.T) {
	input := `var x = 5
rem: this is a comment
var y = 10`

	tests := []struct {
		expectedType    token.TokenType
		expectedLiteral string
	}{
		{token.VAR, "var"},
		{token.IDENT, "x"},
		{token.ASSIGN, "="},
		{token.INT, "5"},
		{token.NEWLINE, "\n"},
		// rem: comment should be skipped
		{token.VAR, "var"},
		{token.IDENT, "y"},
		{token.ASSIGN, "="},
		{token.INT, "10"},
		{token.EOF, ""},
	}

	l := New(input)

	for i, tt := range tests {
		tok := l.NextToken()

		if tok.Type != tt.expectedType {
			t.Fatalf("tests[%d] - tokentype wrong. expected=%q, got=%q (literal=%q)",
				i, tt.expectedType, tok.Type, tok.Literal)
		}

		if tok.Literal != tt.expectedLiteral {
			t.Fatalf("tests[%d] - literal wrong. expected=%q, got=%q",
				i, tt.expectedLiteral, tok.Literal)
		}
	}
}

func TestNextToken_Indentation(t *testing.T) {
	input := `task Main()
    var x = 5
    if x > 0
        display(x)
    var y = 10`

	tests := []struct {
		expectedType    token.TokenType
		expectedLiteral string
	}{
		{token.TASK, "task"},
		{token.IDENT, "Main"},
		{token.LPAREN, "("},
		{token.RPAREN, ")"},
		{token.NEWLINE, "\n"},
		{token.INDENT, ""},
		{token.VAR, "var"},
		{token.IDENT, "x"},
		{token.ASSIGN, "="},
		{token.INT, "5"},
		{token.NEWLINE, "\n"},
		{token.IF, "if"},
		{token.IDENT, "x"},
		{token.GT, ">"},
		{token.INT, "0"},
		{token.NEWLINE, "\n"},
		{token.INDENT, ""},
		{token.IDENT, "display"},
		{token.LPAREN, "("},
		{token.IDENT, "x"},
		{token.RPAREN, ")"},
		{token.NEWLINE, "\n"},
		{token.DEDENT, ""},
		{token.VAR, "var"},
		{token.IDENT, "y"},
		{token.ASSIGN, "="},
		{token.INT, "10"},
		{token.DEDENT, ""},
		{token.EOF, ""},
	}

	l := New(input)

	for i, tt := range tests {
		tok := l.NextToken()

		if tok.Type != tt.expectedType {
			t.Fatalf("tests[%d] - tokentype wrong. expected=%q, got=%q (literal=%q)",
				i, tt.expectedType, tok.Type, tok.Literal)
		}
	}
}

func TestNextToken_CompleteProgram(t *testing.T) {
	input := `task Calculate using (intNum)
    var result = intNum * 2
    deliver result

task Main()
    var x = 5
    var y = Calculate(x)
    display(y)`

	l := New(input)

	// Just make sure we can tokenize the whole program without errors
	for {
		tok := l.NextToken()
		if tok.Type == token.EOF {
			break
		}
		if tok.Type == token.ILLEGAL {
			t.Fatalf("Encountered ILLEGAL token: %q at line %d, column %d",
				tok.Literal, tok.Line, tok.Column)
		}
	}
}
