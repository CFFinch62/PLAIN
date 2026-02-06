package repl

import (
	"bytes"
	"strings"
	"testing"
)

func TestREPLBasicExpression(t *testing.T) {
	input := "5 + 3\n:quit\n"
	in := strings.NewReader(input)
	out := &bytes.Buffer{}

	r := New(in, out)
	r.Start()

	output := out.String()
	if !strings.Contains(output, "=> 8") {
		t.Errorf("Expected output to contain '=> 8', got: %s", output)
	}
}

func TestREPLVariableDeclaration(t *testing.T) {
	input := "var intX = 42\nintX\n:quit\n"
	in := strings.NewReader(input)
	out := &bytes.Buffer{}

	r := New(in, out)
	r.Start()

	output := out.String()
	if !strings.Contains(output, "=> 42") {
		t.Errorf("Expected output to contain '=> 42', got: %s", output)
	}
}

func TestREPLPersistentEnvironment(t *testing.T) {
	input := "var intA = 10\nvar intB = 20\nintA + intB\n:quit\n"
	in := strings.NewReader(input)
	out := &bytes.Buffer{}

	r := New(in, out)
	r.Start()

	output := out.String()
	if !strings.Contains(output, "=> 30") {
		t.Errorf("Expected output to contain '=> 30', got: %s", output)
	}
}

func TestREPLHelpCommand(t *testing.T) {
	input := ":help\n:quit\n"
	in := strings.NewReader(input)
	out := &bytes.Buffer{}

	r := New(in, out)
	r.Start()

	output := out.String()
	if !strings.Contains(output, "PLAIN REPL Commands") {
		t.Errorf("Expected help output, got: %s", output)
	}
	if !strings.Contains(output, ":quit") {
		t.Errorf("Expected :quit in help, got: %s", output)
	}
}

func TestREPLResetCommand(t *testing.T) {
	input := "var intX = 5\n:reset\nintX\n:quit\n"
	in := strings.NewReader(input)
	out := &bytes.Buffer{}

	r := New(in, out)
	r.Start()

	output := out.String()
	if !strings.Contains(output, "Environment reset") {
		t.Errorf("Expected 'Environment reset', got: %s", output)
	}
	// After reset, intX should be undefined
	if !strings.Contains(output, "undefined identifier: intX") {
		t.Errorf("Expected undefined error after reset, got: %s", output)
	}
}

func TestREPLHistoryCommand(t *testing.T) {
	input := "var intA = 1\nvar intB = 2\n:history\n:quit\n"
	in := strings.NewReader(input)
	out := &bytes.Buffer{}

	r := New(in, out)
	r.Start()

	output := out.String()
	if !strings.Contains(output, "Command History") {
		t.Errorf("Expected 'Command History', got: %s", output)
	}
}

func TestREPLParserError(t *testing.T) {
	input := "var = 5\n:quit\n"
	in := strings.NewReader(input)
	out := &bytes.Buffer{}

	r := New(in, out)
	r.Start()

	output := out.String()
	if !strings.Contains(output, "Parser errors") {
		t.Errorf("Expected parser error message, got: %s", output)
	}
}

func TestREPLDisplay(t *testing.T) {
	// Note: display() outputs to os.Stdout, not the REPL's output writer
	// This test verifies display() runs without errors
	input := "display(\"Hello\")\n:quit\n"
	in := strings.NewReader(input)
	out := &bytes.Buffer{}

	r := New(in, out)
	r.Start()

	output := out.String()
	// Should not contain error messages
	if strings.Contains(output, "error") || strings.Contains(output, "Error") {
		t.Errorf("Expected no errors, got: %s", output)
	}
}

func TestREPLMultiLineTask(t *testing.T) {
	input := "task double using (intN)\n    deliver intN * 2\n\ndouble(5)\n:quit\n"
	in := strings.NewReader(input)
	out := &bytes.Buffer{}

	r := New(in, out)
	r.Start()

	output := out.String()
	if !strings.Contains(output, "=> 10") {
		t.Errorf("Expected '=> 10' from task call, got: %s", output)
	}
}
