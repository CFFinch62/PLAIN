package repl

import (
	"bufio"
	"fmt"
	"io"
	"os"
	"strings"

	"plain/internal/analyzer"
	"plain/internal/lexer"
	"plain/internal/parser"
	"plain/internal/runtime"
)

const (
	PROMPT   = "plain> "
	CONTINUE = "  ...> "
	VERSION  = "0.1.0"
)

// REPL represents the Read-Eval-Print Loop
type REPL struct {
	eval    *runtime.Evaluator
	env     *runtime.Environment
	history []string
	in      io.Reader
	out     io.Writer
}

// New creates a new REPL instance
func New(in io.Reader, out io.Writer) *REPL {
	return &REPL{
		eval:    runtime.New(),
		env:     runtime.NewEnvironment(),
		history: make([]string, 0),
		in:      in,
		out:     out,
	}
}

// Start begins the REPL session
func (r *REPL) Start() {
	scanner := bufio.NewScanner(r.in)

	r.printWelcome()

	for {
		fmt.Fprint(r.out, PROMPT)

		if !scanner.Scan() {
			break
		}

		line := scanner.Text()

		// Handle REPL commands
		if strings.HasPrefix(line, ":") {
			if r.handleCommand(line) {
				continue
			}
			break // :quit was called
		}

		// Skip empty lines
		if strings.TrimSpace(line) == "" {
			continue
		}

		// Collect multi-line input if needed
		input := r.collectInput(line, scanner)

		// Add to history
		r.history = append(r.history, input)

		// Evaluate the input
		r.evaluate(input)
	}
}

// printWelcome displays the welcome message
func (r *REPL) printWelcome() {
	fmt.Fprintf(r.out, "PLAIN Language REPL v%s\n", VERSION)
	fmt.Fprintln(r.out, "Type :help for commands, :quit to exit")
	fmt.Fprintln(r.out, "")
}

// handleCommand processes REPL commands (returns false for :quit)
func (r *REPL) handleCommand(cmd string) bool {
	cmd = strings.TrimSpace(strings.ToLower(cmd))

	switch cmd {
	case ":quit", ":q", ":exit":
		fmt.Fprintln(r.out, "Goodbye!")
		return false

	case ":help", ":h":
		r.printHelp()

	case ":clear", ":c":
		r.clearScreen()

	case ":env", ":e":
		r.printEnvironment()

	case ":history", ":hist":
		r.printHistory()

	case ":reset", ":r":
		r.resetEnvironment()

	default:
		fmt.Fprintf(r.out, "Unknown command: %s (type :help for available commands)\n", cmd)
	}

	return true
}

// printHelp displays available commands
func (r *REPL) printHelp() {
	fmt.Fprintln(r.out, "PLAIN REPL Commands:")
	fmt.Fprintln(r.out, "  :help, :h      Show this help message")
	fmt.Fprintln(r.out, "  :quit, :q      Exit the REPL")
	fmt.Fprintln(r.out, "  :clear, :c     Clear the screen")
	fmt.Fprintln(r.out, "  :env, :e       Show current environment variables")
	fmt.Fprintln(r.out, "  :history       Show command history")
	fmt.Fprintln(r.out, "  :reset, :r     Reset the environment (clear all variables)")
	fmt.Fprintln(r.out, "")
	fmt.Fprintln(r.out, "Multi-line input:")
	fmt.Fprintln(r.out, "  Lines ending with ':' or containing indented blocks")
	fmt.Fprintln(r.out, "  will continue on the next line. Enter a blank line to execute.")
}

// clearScreen clears the terminal
func (r *REPL) clearScreen() {
	fmt.Fprint(r.out, "\033[2J\033[H")
}

// printEnvironment shows current variables
func (r *REPL) printEnvironment() {
	fmt.Fprintln(r.out, "Current Environment:")
	fmt.Fprintln(r.out, "  (Environment inspection coming soon)")
}

// printHistory shows command history
func (r *REPL) printHistory() {
	if len(r.history) == 0 {
		fmt.Fprintln(r.out, "No history yet.")
		return
	}
	fmt.Fprintln(r.out, "Command History:")
	for i, cmd := range r.history {
		fmt.Fprintf(r.out, "  %d: %s\n", i+1, strings.ReplaceAll(cmd, "\n", "\\n"))
	}
}

// resetEnvironment clears all variables
func (r *REPL) resetEnvironment() {
	r.env = runtime.NewEnvironment()
	fmt.Fprintln(r.out, "Environment reset.")
}

// collectInput gathers multi-line input when needed
func (r *REPL) collectInput(firstLine string, scanner *bufio.Scanner) string {
	var lines []string
	lines = append(lines, firstLine)

	// Check if we need to continue reading (block-starting keywords)
	if !r.needsContinuation(firstLine) {
		return firstLine
	}

	// Continue reading until we get a blank line or dedent
	for {
		fmt.Fprint(r.out, CONTINUE)

		if !scanner.Scan() {
			break
		}

		line := scanner.Text()

		// Empty line signals end of multi-line input
		if strings.TrimSpace(line) == "" {
			break
		}

		lines = append(lines, line)

		// Check if this line ends a block (no indentation and not continuing)
		if !strings.HasPrefix(line, "    ") && !strings.HasPrefix(line, "\t") {
			if !r.needsContinuation(line) {
				break
			}
		}
	}

	return strings.Join(lines, "\n")
}

// needsContinuation checks if a line starts a block that needs more input
func (r *REPL) needsContinuation(line string) bool {
	trimmed := strings.TrimSpace(line)

	// Lines ending with : typically start blocks
	if strings.HasSuffix(trimmed, ":") {
		return true
	}

	// Block-starting keywords
	blockKeywords := []string{
		"task ", "if ", "else", "loop ", "choose ", "choice ",
		"attempt", "handle", "ensure", "record ", "from ", "default",
	}

	for _, kw := range blockKeywords {
		if strings.HasPrefix(trimmed, kw) || trimmed == strings.TrimSpace(kw) {
			return true
		}
	}

	return false
}

// evaluate parses and executes the input
func (r *REPL) evaluate(input string) {
	// Create lexer and parser
	l := lexer.New(input)
	p := parser.New(l)

	// Parse the program
	program := p.ParseProgram()

	// Check for parser errors
	if len(p.Errors()) > 0 {
		r.printErrors("Parser", p.Errors())
		return
	}

	// Run semantic analysis (optional for REPL, but catches errors early)
	a := analyzer.New()
	errors := a.Analyze(program)

	if len(errors) > 0 {
		r.printErrors("Analysis", errors)
		return
	}

	// Evaluate with persistent environment
	result := r.eval.Eval(program, r.env)

	// Check for runtime errors
	if errVal, ok := result.(*runtime.ErrorValue); ok {
		fmt.Fprintf(r.out, "Runtime error: %s\n", errVal.Message)
		return
	}

	// Print result if it's not null
	if result != nil && result != runtime.NULL {
		fmt.Fprintf(r.out, "=> %s\n", result.String())
	}
}

// printErrors displays errors in a user-friendly format
func (r *REPL) printErrors(phase string, errors []string) {
	fmt.Fprintf(r.out, "%s errors:\n", phase)
	for _, msg := range errors {
		fmt.Fprintf(r.out, "  • %s\n", msg)
	}
}

// StartDefault starts REPL with stdin/stdout
func StartDefault() {
	repl := New(os.Stdin, os.Stdout)
	repl.Start()
}
