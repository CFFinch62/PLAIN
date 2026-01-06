package main

import (
	"fmt"
	"os"
	"plain/internal/lexer"
	"plain/internal/parser"
	"plain/internal/token"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Println("PLAIN Language Interpreter")
		fmt.Println("Usage: plain <file.plain>")
		fmt.Println("       plain -lex <file.plain>    (show tokens)")
		fmt.Println("       plain -parse <file.plain>  (show AST)")
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

	// Normal execution (not yet implemented)
	fmt.Println("Interpreter not yet implemented. Use -lex or -parse to analyze code.")
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
		if tok.Type == token.NEWLINE {
			literal = "\\n"
		} else if tok.Type == token.INDENT {
			literal = "<INDENT>"
		} else if tok.Type == token.DEDENT {
			literal = "<DEDENT>"
		} else if tok.Type == token.EOF {
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
