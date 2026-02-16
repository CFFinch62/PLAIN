package main

import (
	"fmt"
	"os"
	"path/filepath"
	"plain/internal/analyzer"
	"plain/internal/lexer"
	"plain/internal/parser"
	"plain/internal/repl"
	"plain/internal/runtime"
	"plain/internal/token"
	"strconv"
	"strings"
)

func main() {
	// No arguments - start REPL
	if len(os.Args) < 2 {
		repl.StartDefault()
		return
	}

	// Parse global flags (--project-root)
	projectRoot := ""
	args := os.Args[1:]
	filteredArgs := []string{}

	for i := 0; i < len(args); i++ {
		if strings.HasPrefix(args[i], "--project-root=") {
			projectRoot = strings.TrimPrefix(args[i], "--project-root=")
		} else if args[i] == "--project-root" {
			if i+1 < len(args) {
				projectRoot = args[i+1]
				i++ // Skip next arg
			} else {
				fmt.Println("Error: --project-root requires a directory path")
				os.Exit(1)
			}
		} else {
			filteredArgs = append(filteredArgs, args[i])
		}
	}

	// Reconstruct os.Args with filtered arguments
	os.Args = append([]string{os.Args[0]}, filteredArgs...)

	// No arguments after filtering - start REPL
	if len(os.Args) < 2 {
		repl.StartDefault()
		return
	}

	// Check for -repl flag to explicitly start REPL
	if os.Args[1] == "-repl" || os.Args[1] == "-i" {
		repl.StartDefault()
		return
	}

	// Check for -help flag
	if os.Args[1] == "-help" || os.Args[1] == "-h" || os.Args[1] == "--help" {
		printUsage()
		return
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

	// Check for --debug flag for debug mode
	if os.Args[1] == "--debug" {
		if len(os.Args) < 3 {
			fmt.Println("Error: --debug requires a filename")
			os.Exit(1)
		}
		// Parse optional breakpoints
		var breakpoints []int
		filename := os.Args[2]
		for i := 3; i < len(os.Args); i++ {
			if strings.HasPrefix(os.Args[i], "--breakpoints=") {
				bpStr := strings.TrimPrefix(os.Args[i], "--breakpoints=")
				breakpoints = parseBreakpoints(bpStr)
			}
		}
		runFileDebugWithRoot(filename, breakpoints, projectRoot)
		return
	}

	// Normal execution - run the PLAIN file
	if strings.HasSuffix(os.Args[1], ".plain") || !strings.HasPrefix(os.Args[1], "-") {
		runFileWithRoot(os.Args[1], projectRoot)
		return
	}

	fmt.Printf("Unknown option: %s\n", os.Args[1])
	printUsage()
	os.Exit(1)
}

func printUsage() {
	fmt.Println("PLAIN Language Interpreter")
	fmt.Println("")
	fmt.Println("Usage:")
	fmt.Println("  plain                          Start interactive REPL")
	fmt.Println("  plain <file.plain>             Run a PLAIN program")
	fmt.Println("  plain -repl, -i                Start interactive REPL")
	fmt.Println("  plain -lex <file.plain>        Show tokens (lexer output)")
	fmt.Println("  plain -parse <file.plain>      Show AST (parser output)")
	fmt.Println("  plain -analyze <file.plain>    Run semantic analysis")
	fmt.Println("  plain --debug <file.plain>     Run in debug mode (for IDE integration)")
	fmt.Println("  plain -help, -h                Show this help message")
	fmt.Println("")
	fmt.Println("Global options:")
	fmt.Println("  --project-root=<dir>           Set project root for module resolution")
	fmt.Println("  --project-root <dir>           (allows imports from project root instead of file directory)")
	fmt.Println("")
	fmt.Println("Debug options:")
	fmt.Println("  --breakpoints=1,5,10           Set initial breakpoints at lines 1, 5, 10")
	fmt.Println("")
	fmt.Println("Examples:")
	fmt.Println("  plain myfile.plain")
	fmt.Println("  plain --project-root=/path/to/project solutions/solution1.plain")
	fmt.Println("  plain --project-root=. solutions/solution1.plain")
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
	runFileWithRoot(filename, "")
}

func runFileWithRoot(filename string, projectRoot string) {
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

	// Determine base directory for module resolution
	var baseDir string
	if projectRoot != "" {
		// Use specified project root
		baseDir = projectRoot
	} else {
		// Default: use directory of the file being run
		baseDir = filepath.Dir(filename)
	}

	eval := runtime.NewWithBaseDir(baseDir)
	env := runtime.NewEnvironment()

	result := eval.Eval(program, env)

	// Check for runtime errors
	if errVal, ok := result.(*runtime.ErrorValue); ok {
		fmt.Printf("Runtime error: %s\n", errVal.Message)
		os.Exit(1)
	}
}

// parseBreakpoints parses a comma-separated list of line numbers
func parseBreakpoints(s string) []int {
	if s == "" {
		return nil
	}
	parts := strings.Split(s, ",")
	lines := make([]int, 0, len(parts))
	for _, p := range parts {
		p = strings.TrimSpace(p)
		if line, err := strconv.Atoi(p); err == nil && line > 0 {
			lines = append(lines, line)
		}
	}
	return lines
}

// runFileDebug runs a PLAIN file in debug mode
func runFileDebug(filename string, breakpoints []int) {
	runFileDebugWithRoot(filename, breakpoints, "")
}

func runFileDebugWithRoot(filename string, breakpoints []int, projectRoot string) {
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
		for _, msg := range errors {
			fmt.Printf("ERROR: %s\n", msg)
		}
		os.Exit(1)
	}

	// Determine base directory for module resolution
	var baseDir string
	if projectRoot != "" {
		// Use specified project root
		baseDir = projectRoot
	} else {
		// Default: use directory of the file being run
		baseDir = filepath.Dir(filename)
	}

	eval := runtime.NewWithBaseDir(baseDir)
	env := runtime.NewEnvironment()

	// Create debugger with breakpoints
	debugger := runtime.NewDebugger(eval)
	debugger.SetBreakpoints(breakpoints)

	// Run the program in debug mode
	result := debugger.Run(program, env)

	// Check for runtime errors
	if errVal, ok := result.(*runtime.ErrorValue); ok {
		fmt.Printf("Runtime error: %s\n", errVal.Message)
		os.Exit(1)
	}
}
