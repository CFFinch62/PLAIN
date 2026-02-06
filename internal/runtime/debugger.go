package runtime

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"plain/internal/ast"
	"sort"
	"strings"
	"sync"
	"time"
)

// DebugMode represents the current debugging mode
type DebugMode int

const (
	DebugRun        DebugMode = iota // Run until breakpoint or end
	DebugStepInto                    // Step into function calls
	DebugStepOver                    // Step over function calls
	DebugStepOut                     // Step out of current function
	DebugPaused                      // Paused at breakpoint
	DebugTerminated                  // Debugging terminated
)

// DebugCommand represents a command from the IDE
type DebugCommand struct {
	Command     string `json:"command"` // "continue", "step_into", "step_over", "step_out", "set_breakpoint", "clear_breakpoint", "get_variables", "quit"
	Line        int    `json:"line,omitempty"`
	Breakpoints []int  `json:"breakpoints,omitempty"`
}

// DebugEvent represents an event sent to the IDE
type DebugEvent struct {
	Event     string                 `json:"event"` // "stopped", "terminated", "output", "variables"
	Line      int                    `json:"line,omitempty"`
	Reason    string                 `json:"reason,omitempty"` // "breakpoint", "step", "entry"
	Variables map[string]interface{} `json:"variables,omitempty"`
	CallStack []StackFrame           `json:"call_stack,omitempty"`
	Output    string                 `json:"output,omitempty"`
}

// StackFrame represents a frame in the call stack
type StackFrame struct {
	Name string `json:"name"`
	Line int    `json:"line"`
}

// Debugger wraps an Evaluator with debugging capabilities
type Debugger struct {
	evaluator   *Evaluator
	breakpoints map[int]bool // line -> enabled
	mode        DebugMode
	currentLine int
	callStack   []StackFrame
	stepDepth   int // For step over/out
	reader      *bufio.Reader
	env         *Environment // Current environment for variable inspection

	// Stdout capture for debug mode
	origStdout   *os.File
	pipeReader   *os.File
	pipeWriter   *os.File
	outputBuffer bytes.Buffer
	outputMu     sync.Mutex
	outputDone   chan struct{}
}

// NewDebugger creates a new debugger wrapping an evaluator
func NewDebugger(evaluator *Evaluator) *Debugger {
	return &Debugger{
		evaluator:   evaluator,
		breakpoints: make(map[int]bool),
		mode:        DebugPaused, // Start paused
		callStack:   []StackFrame{{Name: "<main>", Line: 1}},
		reader:      bufio.NewReader(os.Stdin),
	}
}

// SetBreakpoints sets the breakpoint lines
func (d *Debugger) SetBreakpoints(lines []int) {
	d.breakpoints = make(map[int]bool)
	for _, line := range lines {
		d.breakpoints[line] = true
	}
}

// startOutputCapture redirects stdout to capture program output
func (d *Debugger) startOutputCapture() error {
	var err error
	d.origStdout = os.Stdout
	d.pipeReader, d.pipeWriter, err = os.Pipe()
	if err != nil {
		return err
	}
	os.Stdout = d.pipeWriter
	d.outputDone = make(chan struct{})

	// Goroutine to read from pipe and buffer output
	go func() {
		defer close(d.outputDone)
		buf := make([]byte, 1024)
		for {
			n, err := d.pipeReader.Read(buf)
			if n > 0 {
				d.outputMu.Lock()
				d.outputBuffer.Write(buf[:n])
				d.outputMu.Unlock()
			}
			if err == io.EOF || err != nil {
				break
			}
		}
	}()

	return nil
}

// stopOutputCapture restores stdout and returns captured output
func (d *Debugger) stopOutputCapture() {
	if d.pipeWriter != nil {
		d.pipeWriter.Close()
	}
	if d.outputDone != nil {
		<-d.outputDone
	}
	if d.pipeReader != nil {
		d.pipeReader.Close()
	}
	if d.origStdout != nil {
		os.Stdout = d.origStdout
	}
}

// flushOutput sends any buffered output as a debug event
func (d *Debugger) flushOutput() {
	// Sync the pipe writer to ensure data is written
	if d.pipeWriter != nil {
		d.pipeWriter.Sync()
	}

	// Brief pause to allow the reader goroutine to process the data
	time.Sleep(10 * time.Millisecond)

	d.outputMu.Lock()
	output := d.outputBuffer.String()
	d.outputBuffer.Reset()
	d.outputMu.Unlock()

	if output != "" {
		d.sendEventToOrigStdout(DebugEvent{
			Event:  "output",
			Output: output,
		})
	}
}

// sendEvent sends a debug event to the original stdout as JSON
func (d *Debugger) sendEvent(event DebugEvent) {
	d.sendEventToOrigStdout(event)
}

// sendEventToOrigStdout writes directly to original stdout (not captured)
func (d *Debugger) sendEventToOrigStdout(event DebugEvent) {
	data, _ := json.Marshal(event)
	if d.origStdout != nil {
		fmt.Fprintln(d.origStdout, string(data))
	} else {
		fmt.Println(string(data))
	}
}

// readCommand reads a debug command from stdin
func (d *Debugger) readCommand() (*DebugCommand, error) {
	line, err := d.reader.ReadString('\n')
	if err != nil {
		return nil, err
	}
	line = strings.TrimSpace(line)

	var cmd DebugCommand
	if err := json.Unmarshal([]byte(line), &cmd); err != nil {
		return nil, err
	}
	return &cmd, nil
}

// waitForCommand pauses and waits for a debug command
func (d *Debugger) waitForCommand() {
	for {
		cmd, err := d.readCommand()
		if err != nil {
			d.mode = DebugTerminated
			return
		}

		switch cmd.Command {
		case "continue":
			d.mode = DebugRun
			return
		case "step_into":
			d.mode = DebugStepInto
			return
		case "step_over":
			d.mode = DebugStepOver
			d.stepDepth = len(d.callStack)
			return
		case "step_out":
			d.mode = DebugStepOut
			d.stepDepth = len(d.callStack) - 1
			return
		case "set_breakpoints":
			d.SetBreakpoints(cmd.Breakpoints)
		case "get_variables":
			d.sendVariables()
		case "quit":
			d.mode = DebugTerminated
			return
		}
	}
}

// sendVariables sends current variable state to IDE
func (d *Debugger) sendVariables() {
	vars := make(map[string]interface{})
	if d.env != nil {
		for name, val := range d.env.store {
			vars[name] = map[string]interface{}{
				"value": val.String(),
				"type":  getTypeName(val),
			}
		}
	}
	d.sendEvent(DebugEvent{
		Event:     "variables",
		Variables: vars,
		CallStack: d.callStack,
	})
}

// getTypeName returns a human-readable type name
func getTypeName(v Value) string {
	switch v.(type) {
	case *IntegerValue:
		return "integer"
	case *FloatValue:
		return "float"
	case *StringValue:
		return "string"
	case *BooleanValue:
		return "boolean"
	case *ListValue:
		return "list"
	case *TableValue:
		return "table"
	case *NullValue:
		return "null"
	case *TaskValue:
		return "task"
	default:
		return "unknown"
	}
}

// shouldStop checks if we should stop at the current line
func (d *Debugger) shouldStop(line int) bool {
	if d.mode == DebugTerminated {
		return false
	}

	// Always stop at breakpoints
	if d.breakpoints[line] {
		return true
	}

	switch d.mode {
	case DebugStepInto:
		return true
	case DebugStepOver:
		return len(d.callStack) <= d.stepDepth
	case DebugStepOut:
		return len(d.callStack) < d.stepDepth
	case DebugRun:
		return false
	}
	return false
}

// onStatement is called before each statement is executed
func (d *Debugger) onStatement(node ast.Node, env *Environment) bool {
	if d.mode == DebugTerminated {
		return false // Signal to stop execution
	}

	line := d.getNodeLine(node)
	if line == 0 || line == d.currentLine {
		return true // Continue execution
	}

	d.currentLine = line
	d.env = env

	if d.shouldStop(line) {
		reason := "step"
		if d.breakpoints[line] {
			reason = "breakpoint"
		}

		// Flush any program output before pausing
		d.flushOutput()

		d.sendEvent(DebugEvent{
			Event:     "stopped",
			Line:      line,
			Reason:    reason,
			CallStack: d.callStack,
		})

		d.mode = DebugPaused
		d.waitForCommand()
	}

	return d.mode != DebugTerminated
}

// getNodeLine extracts the line number from an AST node
func (d *Debugger) getNodeLine(node ast.Node) int {
	switch n := node.(type) {
	case *ast.VarStatement:
		return n.Token.Line
	case *ast.FxdStatement:
		return n.Token.Line
	case *ast.AssignStatement:
		return n.Token.Line
	case *ast.ExpressionStatement:
		return n.Token.Line
	case *ast.IfStatement:
		return n.Token.Line
	case *ast.LoopStatement:
		return n.Token.Line
	case *ast.ChooseStatement:
		return n.Token.Line
	case *ast.DeliverStatement:
		return n.Token.Line
	case *ast.ExitStatement:
		return n.Token.Line
	case *ast.ContinueStatement:
		return n.Token.Line
	case *ast.AbortStatement:
		return n.Token.Line
	case *ast.AttemptStatement:
		return n.Token.Line
	case *ast.TaskStatement:
		return n.Token.Line
	case *ast.RecordStatement:
		return n.Token.Line
	case *ast.UseStatement:
		return n.Token.Line
	}
	return 0
}

// pushCall adds a frame to the call stack
func (d *Debugger) pushCall(name string, line int) {
	d.callStack = append(d.callStack, StackFrame{Name: name, Line: line})
}

// popCall removes a frame from the call stack
func (d *Debugger) popCall() {
	if len(d.callStack) > 1 {
		d.callStack = d.callStack[:len(d.callStack)-1]
	}
}

// Run starts debugging a program
func (d *Debugger) Run(program *ast.Program, env *Environment) Value {
	// Start capturing stdout so program output doesn't mix with JSON events
	if err := d.startOutputCapture(); err != nil {
		d.sendEvent(DebugEvent{Event: "output", Output: "Warning: could not capture stdout: " + err.Error()})
	}
	defer d.stopOutputCapture()

	// Send initial stopped event
	d.sendEvent(DebugEvent{
		Event:     "stopped",
		Line:      1,
		Reason:    "entry",
		CallStack: d.callStack,
	})

	// Wait for initial command
	d.waitForCommand()

	if d.mode == DebugTerminated {
		d.flushOutput()
		d.sendEvent(DebugEvent{Event: "terminated"})
		return NULL
	}

	// Run the program with debug hooks
	result := d.evalProgramDebug(program, env)

	// Flush any remaining output
	d.flushOutput()

	// Send terminated event
	d.sendEvent(DebugEvent{Event: "terminated"})

	return result
}

// evalProgramDebug evaluates a program with debug hooks
func (d *Debugger) evalProgramDebug(program *ast.Program, env *Environment) Value {
	var result Value = NULL

	// First pass: register all tasks
	for _, stmt := range program.Statements {
		if taskStmt, ok := stmt.(*ast.TaskStatement); ok {
			d.evaluator.Eval(taskStmt, env)
		}
	}

	// Second pass: execute non-task statements
	for _, stmt := range program.Statements {
		if _, ok := stmt.(*ast.TaskStatement); ok {
			continue
		}

		if !d.onStatement(stmt, env) {
			return result
		}

		result = d.evalStatementDebug(stmt, env)

		if isControlFlow(result) {
			return result
		}
	}

	// Auto-call Main() if it exists
	if mainVal, ok := env.Get("Main"); ok {
		if mainTask, ok := mainVal.(*TaskValue); ok {
			if len(mainTask.Parameters) == 0 {
				d.pushCall("Main", d.currentLine)
				result = d.applyFunctionDebug(mainTask, []Value{}, env)
				d.popCall()
			}
		}
	}

	return result
}

// evalStatementDebug evaluates a statement with debug hooks
func (d *Debugger) evalStatementDebug(stmt ast.Statement, env *Environment) Value {
	switch s := stmt.(type) {
	case *ast.BlockStatement:
		return d.evalBlockDebug(s, env)
	case *ast.IfStatement:
		return d.evalIfDebug(s, env)
	case *ast.LoopStatement:
		return d.evalLoopDebug(s, env)
	case *ast.ChooseStatement:
		return d.evalChooseDebug(s, env)
	default:
		return d.evaluator.Eval(stmt, env)
	}
}

// evalBlockDebug evaluates a block with debug hooks
func (d *Debugger) evalBlockDebug(block *ast.BlockStatement, env *Environment) Value {
	var result Value = NULL

	for _, stmt := range block.Statements {
		if !d.onStatement(stmt, env) {
			return result
		}

		result = d.evalStatementDebug(stmt, env)

		if isControlFlow(result) {
			return result
		}
	}

	return result
}

// isControlFlow checks if a value is a control flow value
func isControlFlow(v Value) bool {
	switch v.(type) {
	case *ReturnValue, *BreakValue, *ContinueValue, *ErrorValue:
		return true
	}
	return false
}

// evalIfDebug evaluates an if statement with debug hooks
func (d *Debugger) evalIfDebug(stmt *ast.IfStatement, env *Environment) Value {
	condition := d.evaluator.Eval(stmt.Condition, env)
	if isError(condition) {
		return condition
	}

	if isTruthy(condition) {
		return d.evalBlockDebug(stmt.Consequence, env)
	} else if stmt.Alternative != nil {
		return d.evalBlockDebug(stmt.Alternative, env)
	}

	return NULL
}

// evalLoopDebug evaluates a loop with debug hooks
func (d *Debugger) evalLoopDebug(stmt *ast.LoopStatement, env *Environment) Value {
	// Delegate to evaluator for loop setup, but we need to handle the body ourselves
	// This is complex - for now, use the regular evaluator
	// TODO: Implement full loop debugging with step-through
	return d.evaluator.Eval(stmt, env)
}

// evalChooseDebug evaluates a choose statement with debug hooks
func (d *Debugger) evalChooseDebug(stmt *ast.ChooseStatement, env *Environment) Value {
	// Evaluate the value being matched
	value := d.evaluator.Eval(stmt.Value, env)
	if isError(value) {
		return value
	}

	// Check each choice
	for _, choice := range stmt.Choices {
		caseResult := d.evaluator.Eval(choice.Value, env)
		if isError(caseResult) {
			return caseResult
		}
		if debugValuesEqual(value, caseResult) {
			return d.evalBlockDebug(choice.Body, env)
		}
	}

	// Default case
	if stmt.Default != nil {
		return d.evalBlockDebug(stmt.Default, env)
	}

	return NULL
}

// applyFunctionDebug applies a function with debug hooks
func (d *Debugger) applyFunctionDebug(fn *TaskValue, args []Value, outerEnv *Environment) Value {
	// Create new environment for function
	funcEnv := NewEnclosedEnvironment(fn.Env)

	// Bind parameters
	for i, param := range fn.Parameters {
		if i < len(args) {
			funcEnv.Set(param, args[i])
		} else {
			funcEnv.Set(param, NULL)
		}
	}

	// Evaluate body with debug hooks
	body, ok := fn.Body.(*ast.BlockStatement)
	if !ok {
		return NULL
	}
	result := d.evalBlockDebug(body, funcEnv)

	// Unwrap return value
	if ret, ok := result.(*ReturnValue); ok {
		return ret.Val
	}

	return result
}

// Helper functions
func isError(v Value) bool {
	_, ok := v.(*ErrorValue)
	return ok
}

func isTruthy(v Value) bool {
	switch val := v.(type) {
	case *NullValue:
		return false
	case *BooleanValue:
		return val.Val
	case *IntegerValue:
		return val.Val != 0
	case *FloatValue:
		return val.Val != 0
	case *StringValue:
		return val.Val != ""
	default:
		return true
	}
}

func debugValuesEqual(a, b Value) bool {
	switch av := a.(type) {
	case *IntegerValue:
		if bv, ok := b.(*IntegerValue); ok {
			return av.Val == bv.Val
		}
	case *FloatValue:
		if bv, ok := b.(*FloatValue); ok {
			return av.Val == bv.Val
		}
	case *StringValue:
		if bv, ok := b.(*StringValue); ok {
			return av.Val == bv.Val
		}
	case *BooleanValue:
		if bv, ok := b.(*BooleanValue); ok {
			return av.Val == bv.Val
		}
	}
	return false
}

// GetAllVariables returns all variables in scope for debugging
func (d *Debugger) GetAllVariables() map[string]map[string]interface{} {
	result := make(map[string]map[string]interface{})

	if d.env == nil {
		return result
	}

	// Get local variables
	localVars := make(map[string]interface{})
	for name, val := range d.env.store {
		localVars[name] = map[string]interface{}{
			"value": val.String(),
			"type":  getTypeName(val),
		}
	}
	result["Local"] = localVars

	// Get global variables (from parent scopes)
	if d.env.parent != nil {
		globalVars := make(map[string]interface{})
		collectOuterVars(d.env.parent, globalVars, d.env.store)
		if len(globalVars) > 0 {
			result["Global"] = globalVars
		}
	}

	return result
}

func collectOuterVars(env *Environment, vars map[string]interface{}, exclude map[string]Value) {
	if env == nil {
		return
	}
	for name, val := range env.store {
		if _, exists := exclude[name]; !exists {
			if _, alreadyAdded := vars[name]; !alreadyAdded {
				vars[name] = map[string]interface{}{
					"value": val.String(),
					"type":  getTypeName(val),
				}
			}
		}
	}
	collectOuterVars(env.parent, vars, exclude)
}

// GetSortedVariableNames returns variable names sorted alphabetically
func GetSortedVariableNames(vars map[string]interface{}) []string {
	names := make([]string, 0, len(vars))
	for name := range vars {
		names = append(names, name)
	}
	sort.Strings(names)
	return names
}
