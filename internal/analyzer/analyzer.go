package analyzer

import (
	"fmt"
	"plain/internal/ast"
	"plain/internal/scope"
)

// Analyzer performs semantic analysis on the AST
type Analyzer struct {
	currentScope *scope.Scope
	errors       []string
}

// New creates a new Analyzer
func New() *Analyzer {
	return &Analyzer{
		currentScope: nil,
		errors:       []string{},
	}
}

// Analyze performs semantic analysis on a parsed program
// Returns a list of semantic errors (empty if no errors)
func (a *Analyzer) Analyze(program *ast.Program) []string {
	// Start with a fresh module scope
	a.currentScope = scope.NewModuleScope()
	a.errors = []string{}

	for _, stmt := range program.Statements {
		a.analyzeStatement(stmt)
	}

	return a.errors
}

// Errors returns the list of semantic errors found
func (a *Analyzer) Errors() []string {
	return a.errors
}

// addError adds a semantic error to the error list
func (a *Analyzer) addError(line, column int, format string, args ...interface{}) {
	msg := fmt.Sprintf(format, args...)
	a.errors = append(a.errors, fmt.Sprintf("line %d, column %d: %s", line, column, msg))
}

// enterScope creates and enters a new scope
func (a *Analyzer) enterScope(level scope.ScopeLevel) {
	a.currentScope = scope.New(a.currentScope, level)
}

// exitScope returns to the parent scope
func (a *Analyzer) exitScope() {
	if a.currentScope.Parent() != nil {
		a.currentScope = a.currentScope.Parent()
	}
}

// defineSymbol attempts to define a symbol in the current scope
func (a *Analyzer) defineSymbol(name string, mutable bool, line, column int) {
	sym := &scope.Symbol{
		Name:    name,
		Mutable: mutable,
		Line:    line,
		Column:  column,
	}

	if err := a.currentScope.Define(sym); err != nil {
		a.addError(line, column, "%s", err.Error())
	}
}

// analyzeStatement dispatches to the appropriate statement analyzer
func (a *Analyzer) analyzeStatement(stmt ast.Statement) {
	switch s := stmt.(type) {
	case *ast.VarStatement:
		a.analyzeVarStatement(s)
	case *ast.FxdStatement:
		a.analyzeFxdStatement(s)
	case *ast.TaskStatement:
		a.analyzeTaskStatement(s)
	case *ast.AssignStatement:
		a.analyzeAssignStatement(s)
	case *ast.IfStatement:
		a.analyzeIfStatement(s)
	case *ast.LoopStatement:
		a.analyzeLoopStatement(s)
	case *ast.ChooseStatement:
		a.analyzeChooseStatement(s)
	case *ast.AttemptStatement:
		a.analyzeAttemptStatement(s)
	case *ast.BlockStatement:
		a.analyzeBlockStatement(s)
	case *ast.ExpressionStatement:
		a.analyzeExpression(s.Expression)
	case *ast.DeliverStatement:
		if s.ReturnValue != nil {
			a.analyzeExpression(s.ReturnValue)
		}
	case *ast.AbortStatement:
		if s.Message != nil {
			a.analyzeExpression(s.Message)
		}
	case *ast.RecordStatement:
		a.analyzeRecordStatement(s)
	case *ast.UseStatement:
		// Import statements don't need scope analysis in this phase
	case *ast.ExitStatement, *ast.ContinueStatement:
		// Control flow statements don't need scope analysis
	}
}

// analyzeVarStatement handles: var name = value
func (a *Analyzer) analyzeVarStatement(stmt *ast.VarStatement) {
	// First analyze the value expression (it may reference existing variables)
	if stmt.Value != nil {
		a.analyzeExpression(stmt.Value)
	}

	// Then define the new variable
	a.defineSymbol(stmt.Name.Value, true, stmt.Token.Line, stmt.Token.Column)
}

// analyzeFxdStatement handles: fxd name = value
func (a *Analyzer) analyzeFxdStatement(stmt *ast.FxdStatement) {
	// First analyze the value expression
	if stmt.Value != nil {
		a.analyzeExpression(stmt.Value)
	}

	// Define as immutable constant
	a.defineSymbol(stmt.Name.Value, false, stmt.Token.Line, stmt.Token.Column)
}

// analyzeTaskStatement handles task definitions
func (a *Analyzer) analyzeTaskStatement(stmt *ast.TaskStatement) {
	// Define the task name in the current (module) scope
	a.defineSymbol(stmt.Name.Value, false, stmt.Token.Line, stmt.Token.Column)

	// Enter task scope
	a.enterScope(scope.TaskScope)

	// Define parameters as immutable symbols
	for _, param := range stmt.Parameters {
		a.defineSymbol(param.Value, false, param.Token.Line, param.Token.Column)
	}

	// Analyze the task body
	if stmt.Body != nil {
		for _, s := range stmt.Body.Statements {
			a.analyzeStatement(s)
		}
	}

	// Exit task scope
	a.exitScope()
}

// analyzeAssignStatement handles: name = value
func (a *Analyzer) analyzeAssignStatement(stmt *ast.AssignStatement) {
	// First analyze the value expression
	a.analyzeExpression(stmt.Value)

	// Then check the assignment target
	a.analyzeAssignmentTarget(stmt.Name, stmt.Token.Line, stmt.Token.Column)
}

// analyzeAssignmentTarget checks if an expression can be assigned to
func (a *Analyzer) analyzeAssignmentTarget(expr ast.Expression, line, column int) {
	switch target := expr.(type) {
	case *ast.Identifier:
		sym, found := a.currentScope.Resolve(target.Value)
		if !found {
			a.addError(line, column, "undefined variable '%s'", target.Value)
			return
		}
		if !sym.Mutable {
			// Check if it's a parameter
			if a.isInTaskScope() {
				a.addError(line, column, "cannot assign to parameter '%s' (parameters are immutable)", target.Value)
			} else {
				a.addError(line, column, "cannot assign to constant '%s'", target.Value)
			}
		}
	case *ast.IndexExpression:
		// For array/table index assignment, analyze the collection and index
		a.analyzeExpression(target.Left)
		a.analyzeExpression(target.Index)
	case *ast.DotExpression:
		// For property assignment, analyze the object
		a.analyzeExpression(target.Left)
	}
}

// isInTaskScope checks if we're currently inside a task (not at module level)
func (a *Analyzer) isInTaskScope() bool {
	s := a.currentScope
	for s != nil {
		if s.Level() == scope.TaskScope || s.Level() == scope.ParameterScope {
			return true
		}
		s = s.Parent()
	}
	return false
}

// analyzeIfStatement handles if/else statements
func (a *Analyzer) analyzeIfStatement(stmt *ast.IfStatement) {
	// Analyze condition
	a.analyzeExpression(stmt.Condition)

	// Analyze consequence in new block scope
	a.enterScope(scope.BlockScope)
	if stmt.Consequence != nil {
		for _, s := range stmt.Consequence.Statements {
			a.analyzeStatement(s)
		}
	}
	a.exitScope()

	// Analyze alternative in new block scope
	if stmt.Alternative != nil {
		a.enterScope(scope.BlockScope)
		for _, s := range stmt.Alternative.Statements {
			a.analyzeStatement(s)
		}
		a.exitScope()
	}
}

// analyzeLoopStatement handles loop variants
func (a *Analyzer) analyzeLoopStatement(stmt *ast.LoopStatement) {
	// Analyze range expressions before entering loop scope
	if stmt.Start != nil {
		a.analyzeExpression(stmt.Start)
	}
	if stmt.End != nil {
		a.analyzeExpression(stmt.End)
	}
	if stmt.Step != nil {
		a.analyzeExpression(stmt.Step)
	}
	if stmt.Iterable != nil {
		a.analyzeExpression(stmt.Iterable)
	}

	// Enter loop block scope
	a.enterScope(scope.BlockScope)

	// Define loop variable (mutable within the loop)
	if stmt.Variable != nil {
		a.defineSymbol(stmt.Variable.Value, true, stmt.Variable.Token.Line, stmt.Variable.Token.Column)
	}

	// Analyze loop body
	if stmt.Body != nil {
		for _, s := range stmt.Body.Statements {
			a.analyzeStatement(s)
		}
	}

	a.exitScope()
}

// analyzeChooseStatement handles choose/choice/default
func (a *Analyzer) analyzeChooseStatement(stmt *ast.ChooseStatement) {
	// Analyze the value being matched
	a.analyzeExpression(stmt.Value)

	// Analyze each choice
	for _, choice := range stmt.Choices {
		// Analyze choice value
		a.analyzeExpression(choice.Value)

		// Analyze choice body in new scope
		a.enterScope(scope.BlockScope)
		if choice.Body != nil {
			for _, s := range choice.Body.Statements {
				a.analyzeStatement(s)
			}
		}
		a.exitScope()
	}

	// Analyze default case
	if stmt.Default != nil {
		a.enterScope(scope.BlockScope)
		for _, s := range stmt.Default.Statements {
			a.analyzeStatement(s)
		}
		a.exitScope()
	}
}

// analyzeAttemptStatement handles attempt/handle/ensure
func (a *Analyzer) analyzeAttemptStatement(stmt *ast.AttemptStatement) {
	// Analyze attempt block
	a.enterScope(scope.BlockScope)
	if stmt.Body != nil {
		for _, s := range stmt.Body.Statements {
			a.analyzeStatement(s)
		}
	}
	a.exitScope()

	// Analyze handle blocks
	for _, handler := range stmt.Handlers {
		a.enterScope(scope.BlockScope)
		if handler.Body != nil {
			for _, s := range handler.Body.Statements {
				a.analyzeStatement(s)
			}
		}
		a.exitScope()
	}

	// Analyze ensure block
	if stmt.Ensure != nil {
		a.enterScope(scope.BlockScope)
		for _, s := range stmt.Ensure.Statements {
			a.analyzeStatement(s)
		}
		a.exitScope()
	}
}

// analyzeBlockStatement handles generic block statements
func (a *Analyzer) analyzeBlockStatement(stmt *ast.BlockStatement) {
	a.enterScope(scope.BlockScope)
	for _, s := range stmt.Statements {
		a.analyzeStatement(s)
	}
	a.exitScope()
}

// analyzeRecordStatement handles record type definitions
func (a *Analyzer) analyzeRecordStatement(stmt *ast.RecordStatement) {
	// Define the record type name in current scope
	a.defineSymbol(stmt.Name.Value, false, stmt.Token.Line, stmt.Token.Column)

	// Record field analysis will be handled in Phase 4 (Type System)
}

// analyzeExpression dispatches to the appropriate expression analyzer
func (a *Analyzer) analyzeExpression(expr ast.Expression) {
	if expr == nil {
		return
	}

	switch e := expr.(type) {
	case *ast.Identifier:
		a.analyzeIdentifier(e)
	case *ast.InfixExpression:
		a.analyzeExpression(e.Left)
		a.analyzeExpression(e.Right)
	case *ast.PrefixExpression:
		a.analyzeExpression(e.Right)
	case *ast.CallExpression:
		a.analyzeCallExpression(e)
	case *ast.IndexExpression:
		a.analyzeExpression(e.Left)
		a.analyzeExpression(e.Index)
	case *ast.DotExpression:
		a.analyzeExpression(e.Left)
	case *ast.ListLiteral:
		for _, elem := range e.Elements {
			a.analyzeExpression(elem)
		}
	case *ast.TableLiteral:
		for key, value := range e.Pairs {
			a.analyzeExpression(key)
			a.analyzeExpression(value)
		}
	case *ast.RecordLiteral:
		for _, value := range e.Fields {
			a.analyzeExpression(value)
		}
	// Literal types don't need scope analysis
	case *ast.IntegerLiteral, *ast.FloatLiteral, *ast.StringLiteral,
		*ast.InterpolatedString, *ast.BooleanLiteral, *ast.NullLiteral:
		// No scope analysis needed for literals
	}
}

// analyzeIdentifier checks if an identifier is defined
func (a *Analyzer) analyzeIdentifier(ident *ast.Identifier) {
	// Skip if it looks like a built-in function (will be handled in Phase 5/6)
	// For now, we allow undefined identifiers that might be stdlib functions
	// A more complete implementation would have a list of built-in names
	if _, found := a.currentScope.Resolve(ident.Value); !found {
		// Only report error for identifiers that look like variables (not function calls)
		// This is a heuristic - proper handling comes in later phases
		// For now, we'll be permissive and not error on potential function names
	}
}

// analyzeCallExpression handles function/task calls
func (a *Analyzer) analyzeCallExpression(call *ast.CallExpression) {
	// Analyze the function expression (might be identifier or dot expression)
	a.analyzeExpression(call.Function)

	// Analyze all arguments
	for _, arg := range call.Arguments {
		a.analyzeExpression(arg)
	}
}
