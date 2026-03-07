//go:build js && wasm

package main

import (
	"plain/internal/analyzer"
	"plain/internal/lexer"
	"plain/internal/parser"
	"plain/internal/runtime"
	"strings"
	"syscall/js"
)

// runPlain is the JS-callable entry point.
// JS call: runPlain(code, inputs)  → { output: string, error: string }
// inputs is a newline-separated list of pre-supplied answers for get() calls.
func runPlain(_ js.Value, args []js.Value) interface{} {
	// Extract arguments
	code := ""
	inputs := ""
	if len(args) >= 1 {
		code = args[0].String()
	}
	if len(args) >= 2 {
		inputs = args[1].String()
	}

	// Enable sandbox
	runtime.PlaygroundMode = true

	// Pre-load the input queue for any get() calls in the program
	inputLines := []string{}
	if inputs != "" {
		inputLines = strings.Split(inputs, "\n")
	}
	runtime.SetInputLines(inputLines)

	// --- Lex ---
	l := lexer.New(code)

	// --- Parse ---
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) > 0 {
		return js.ValueOf(map[string]interface{}{
			"output": "",
			"error":  "Parse errors:\n" + strings.Join(p.Errors(), "\n"),
		})
	}

	// --- Analyze ---
	a := analyzer.New()
	analysisErrors := a.Analyze(program)

	if len(analysisErrors) > 0 {
		return js.ValueOf(map[string]interface{}{
			"output": "",
			"error":  "Semantic errors:\n" + strings.Join(analysisErrors, "\n"),
		})
	}

	// --- Evaluate ---
	eval := runtime.New()
	env := runtime.NewEnvironment()
	result := eval.Eval(program, env)

	// Collect any output written via PrintFunc
	output := runtime.GetOutput()

	// Surface runtime errors
	if errVal, ok := result.(*runtime.ErrorValue); ok {
		return js.ValueOf(map[string]interface{}{
			"output": output,
			"error":  errVal.Message,
		})
	}

	return js.ValueOf(map[string]interface{}{
		"output": output,
		"error":  "",
	})
}

func main() {
	// Register the Go function on the JS global object
	js.Global().Set("runPlain", js.FuncOf(runPlain))

	// Keep the Go runtime alive so JS can call runPlain at any time
	select {}
}

