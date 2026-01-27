package main

import (
	"fmt"
	"os"
	"plain/internal/analyzer"
	"plain/internal/lexer"
	"plain/internal/parser"
	"plain/internal/runtime"
	"plain/internal/token"
	"strings"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Println("PLAIN Language Interpreter")
		fmt.Println("Usage: plain <file.plain>")
		fmt.Println("       plain -lex <file.plain>     (show tokens)")
		fmt.Println("       plain -parse <file.plain>   (show AST)")
		fmt.Println("       plain -analyze <file.plain> (run semantic analysis)")
		os.Exit(1)
	}

	// Check for -lex flag to show tokens
	if os.Args[1] == "-lex" {
		if len(os.Args) < 3 {
			fmt.Println("Error: -lex requires a filename")
			os.Exit(1)
		}
		showTokens(os.Args[2])
		return
	}

	// Check for -parse flag to show AST
	if os.Args[1] == "-parse" {
		if len(os.Args) < 3 {
			fmt.Println("Error: -parse requires a filename")
			os.Exit(1)
		}
		parseFile(os.Args[2])
		return
	}

	// Check for -analyze flag to run semantic analysis
	if os.Args[1] == "-analyze" {
		if len(os.Args) < 3 {
			fmt.Println("Error: -analyze requires a filename")
			os.Exit(1)
		}
		analyzeFile(os.Args[2])
		return
	}

	// Normal execution - run the PLAIN file
	if strings.HasSuffix(os.Args[1], ".plain") || !strings.HasPrefix(os.Args[1], "-") {
		runFile(os.Args[1])
		return
	}

	fmt.Printf("Unknown option: %s\n", os.Args[1])
	os.Exit(1)
}

func showTokens(filename string) {
	// Read the file
	content, err := os.ReadFile(filename)
	if err != nil {
		fmt.Printf("Error reading file: %v\n", err)
		os.Exit(1)
	}

	// Create lexer
	l := lexer.New(string(content))

	// Print header
	fmt.Printf("Tokens for: %s\n", filename)
	fmt.Println("=====================================")
	fmt.Printf("%-4s %-4s %-15s %s\n", "Line", "Col", "Type", "Literal")
	fmt.Println("-------------------------------------")

	// Tokenize and print
	for {
		tok := l.NextToken()

		// Format literal for display
		literal := tok.Literal
		switch tok.Type {
		case token.NEWLINE:
			literal = "\\n"
		case token.INDENT:
			literal = "<INDENT>"
		case token.DEDENT:
			literal = "<DEDENT>"
		case token.EOF:
			literal = "<EOF>"
		}

		fmt.Printf("%-4d %-4d %-15s %s\n", tok.Line, tok.Column, tok.Type, literal)

		if tok.Type == token.EOF {
			break
		}
	}
}

func parseFile(filename string) {
	// Read the file
	content, err := os.ReadFile(filename)
	if err != nil {
		fmt.Printf("Error reading file: %v\n", err)
		os.Exit(1)
	}

	// Create lexer and parser
	l := lexer.New(string(content))
	p := parser.New(l)

	// Parse the program
	program := p.ParseProgram()

	// Check for parser errors
	if len(p.Errors()) > 0 {
		fmt.Printf("Parser errors for: %s\n", filename)
		fmt.Println("=====================================")
		for _, msg := range p.Errors() {
			fmt.Printf("ERROR: %s\n", msg)
		}
		os.Exit(1)
	}

	// Print the AST
	fmt.Printf("AST for: %s\n", filename)
	fmt.Println("=====================================")
	fmt.Println(program.String())
	fmt.Println("=====================================")
	fmt.Printf("Successfully parsed %d statements\n", len(program.Statements))
}

func analyzeFile(filename string) {
	// Read the file
	content, err := os.ReadFile(filename)
	if err != nil {
		fmt.Printf("Error reading file: %v\n", err)
		os.Exit(1)
	}

	// Create lexer and parser
	l := lexer.New(string(content))
	p := parser.New(l)

	// Parse the program
	program := p.ParseProgram()

	// Check for parser errors
	if len(p.Errors()) > 0 {
		fmt.Printf("Parser errors for: %s\n", filename)
		fmt.Println("=====================================")
		for _, msg := range p.Errors() {
			fmt.Printf("ERROR: %s\n", msg)
		}
		os.Exit(1)
	}

	// Run semantic analysis
	a := analyzer.New()
	errors := a.Analyze(program)

	if len(errors) > 0 {
		fmt.Printf("Semantic errors for: %s\n", filename)
		fmt.Println("=====================================")
		for _, msg := range errors {
			fmt.Printf("ERROR: %s\n", msg)
		}
		os.Exit(1)
	}

	fmt.Printf("Analysis for: %s\n", filename)
	fmt.Println("=====================================")
	fmt.Printf("Successfully analyzed %d statements\n", len(program.Statements))
	fmt.Println("No semantic errors found.")
}

func runFile(filename string) {
	// Read the file
	content, err := os.ReadFile(filename)
	if err != nil {
		fmt.Printf("Error reading file: %v\n", err)
		os.Exit(1)
	}

	// Create lexer and parser
	l := lexer.New(string(content))
	p := parser.New(l)

	// Parse the program
	program := p.ParseProgram()

	// Check for parser errors
	if len(p.Errors()) > 0 {
		fmt.Printf("Parser errors for: %s\n", filename)
		fmt.Println("=====================================")
		for _, msg := range p.Errors() {
			fmt.Printf("ERROR: %s\n", msg)
		}
		os.Exit(1)
	}

	// Run semantic analysis (optional - could be skipped for performance)
	a := analyzer.New()
	errors := a.Analyze(program)

	if len(errors) > 0 {
		fmt.Printf("Semantic errors for: %s\n", filename)
		fmt.Println("=====================================")
		for _, msg := range errors {
			fmt.Printf("ERROR: %s\n", msg)
		}
		os.Exit(1)
	}

	// Create runtime evaluator and execute
	eval := runtime.New()
	env := runtime.NewEnvironment()

	result := eval.Eval(program, env)

	// Check for runtime errors
	if errVal, ok := result.(*runtime.ErrorValue); ok {
		fmt.Printf("Runtime error: %s\n", errVal.Message)
		os.Exit(1)
	}
}
