package runtime

import (
	"fmt"
	"math"
	"os"
	"plain/internal/ast"
	"plain/internal/lexer"
	"plain/internal/parser"
	"plain/internal/token"
)

// Evaluator executes PLAIN programs
type Evaluator struct {
	builtins      map[string]*BuiltinValue
	baseDir       string          // Base directory for module resolution
	loadedModules map[string]bool // Track loaded modules to prevent duplicates
}

// New creates a new Evaluator
func New() *Evaluator {
	return NewWithBaseDir("")
}

// NewWithBaseDir creates an Evaluator with a specific base directory for modules
func NewWithBaseDir(baseDir string) *Evaluator {
	e := &Evaluator{
		builtins:      GetBuiltins(),
		baseDir:       baseDir,
		loadedModules: make(map[string]bool),
	}
	// Register with event loop for timer callbacks
	GetEventLoop().SetEvaluator(e)
	return e
}

// Eval evaluates an AST node and returns a runtime value
func (e *Evaluator) Eval(node ast.Node, env *Environment) Value {
	switch n := node.(type) {
	// Program
	case *ast.Program:
		return e.evalProgram(n, env)

	// Statements
	case *ast.VarStatement:
		return e.evalVarStatement(n, env)
	case *ast.FxdStatement:
		return e.evalFxdStatement(n, env)
	case *ast.AssignStatement:
		return e.evalAssignStatement(n, env)
	case *ast.ExpressionStatement:
		return e.Eval(n.Expression, env)
	case *ast.BlockStatement:
		return e.evalBlockStatement(n, env)
	case *ast.IfStatement:
		return e.evalIfStatement(n, env)
	case *ast.LoopStatement:
		return e.evalLoopStatement(n, env)
	case *ast.ChooseStatement:
		return e.evalChooseStatement(n, env)
	case *ast.TaskStatement:
		return e.evalTaskStatement(n, env)
	case *ast.DeliverStatement:
		return e.evalDeliverStatement(n, env)
	case *ast.ExitStatement:
		return &BreakValue{}
	case *ast.ContinueStatement:
		return &ContinueValue{}
	case *ast.AbortStatement:
		return e.evalAbortStatement(n, env)
	case *ast.AttemptStatement:
		return e.evalAttemptStatement(n, env)
	case *ast.RecordStatement:
		return e.evalRecordStatement(n, env)
	case *ast.RecordLiteral:
		return e.evalRecordLiteral(n, env)
	case *ast.UseStatement:
		return e.evalUseStatement(n, env)

	// Expressions
	case *ast.Identifier:
		return e.evalIdentifier(n, env)
	case *ast.IntegerLiteral:
		return NewInteger(n.Value)
	case *ast.FloatLiteral:
		return NewFloat(n.Value)
	case *ast.StringLiteral:
		return NewString(n.Value)
	case *ast.InterpolatedString:
		return e.evalInterpolatedString(n, env)
	case *ast.BooleanLiteral:
		return NewBoolean(n.Value)
	case *ast.NullLiteral:
		return NULL
	case *ast.ListLiteral:
		return e.evalListLiteral(n, env)
	case *ast.TableLiteral:
		return e.evalTableLiteral(n, env)
	case *ast.PrefixExpression:
		return e.evalPrefixExpression(n, env)
	case *ast.InfixExpression:
		return e.evalInfixExpression(n, env)
	case *ast.CallExpression:
		return e.evalCallExpression(n, env)
	case *ast.IndexExpression:
		return e.evalIndexExpression(n, env)
	case *ast.DotExpression:
		return e.evalDotExpression(n, env)
	}

	return NULL
}

// evalProgram evaluates all statements in the program
func (e *Evaluator) evalProgram(program *ast.Program, env *Environment) Value {
	var result Value = NULL

	for _, stmt := range program.Statements {
		result = e.Eval(stmt, env)

		switch r := result.(type) {
		case *ReturnValue:
			return r.Val
		case *ErrorValue:
			return r
		}
	}

	// Auto-call Main() if it exists and hasn't been called
	if mainTask, ok := env.Get("Main"); ok {
		if taskVal, isTask := mainTask.(*TaskValue); isTask {
			// Only call if Main takes no parameters
			if len(taskVal.Parameters) == 0 {
				result = e.callTask(taskVal, []Value{})
				if errVal, isErr := result.(*ErrorValue); isErr {
					return errVal
				}
			}
		}
	}

	return result
}

// evalBlockStatement evaluates a block of statements
func (e *Evaluator) evalBlockStatement(block *ast.BlockStatement, env *Environment) Value {
	var result Value = NULL

	for _, stmt := range block.Statements {
		result = e.Eval(stmt, env)

		// Handle control flow
		switch result.(type) {
		case *ReturnValue, *ErrorValue, *BreakValue, *ContinueValue:
			return result
		}
	}

	return result
}

// evalVarStatement handles variable declarations
func (e *Evaluator) evalVarStatement(stmt *ast.VarStatement, env *Environment) Value {
	var val Value = NULL
	if stmt.Value != nil {
		val = e.Eval(stmt.Value, env)
		if IsError(val) {
			return val
		}
	}

	env.Define(stmt.Name.Value, val)
	return NULL
}

// evalFxdStatement handles constant declarations
func (e *Evaluator) evalFxdStatement(stmt *ast.FxdStatement, env *Environment) Value {
	var val Value = NULL
	if stmt.Value != nil {
		val = e.Eval(stmt.Value, env)
		if IsError(val) {
			return val
		}
	}

	env.Define(stmt.Name.Value, val)
	return NULL
}

// evalAssignStatement handles assignments
func (e *Evaluator) evalAssignStatement(stmt *ast.AssignStatement, env *Environment) Value {
	// For compound assignments (+=, -=, etc.), we need to:
	// 1. Get the current value
	// 2. Evaluate the right-hand side
	// 3. Perform the operation
	// 4. Assign the result

	var val Value

	// Check if this is a compound assignment
	isCompound := false
	var operator string

	switch stmt.Token.Type {
	case token.PLUS_EQ:
		isCompound = true
		operator = "+"
	case token.MINUS_EQ:
		isCompound = true
		operator = "-"
	case token.TIMES_EQ:
		isCompound = true
		operator = "*"
	case token.DIV_EQ:
		isCompound = true
		operator = "/"
	case token.MOD_EQ:
		isCompound = true
		operator = "%"
	case token.CONCAT_EQ:
		isCompound = true
		operator = "&"
	}

	if isCompound {
		// Get the current value of the variable
		var currentVal Value
		switch target := stmt.Name.(type) {
		case *ast.Identifier:
			var ok bool
			currentVal, ok = env.Get(target.Value)
			if !ok {
				return NewError("undefined variable: %s", target.Value)
			}
		case *ast.IndexExpression:
			currentVal = e.Eval(target, env)
			if IsError(currentVal) {
				return currentVal
			}
		case *ast.DotExpression:
			currentVal = e.Eval(target, env)
			if IsError(currentVal) {
				return currentVal
			}
		}

		// Evaluate the right-hand side
		rightVal := e.Eval(stmt.Value, env)
		if IsError(rightVal) {
			return rightVal
		}

		// Perform the operation
		val = e.evalBinaryOperation(currentVal, operator, rightVal)
		if IsError(val) {
			return val
		}
	} else {
		// Regular assignment - just evaluate the right-hand side
		val = e.Eval(stmt.Value, env)
		if IsError(val) {
			return val
		}
	}

	switch target := stmt.Name.(type) {
	case *ast.Identifier:
		if !env.Set(target.Value, val) {
			return NewError("undefined variable: %s", target.Value)
		}
	case *ast.IndexExpression:
		return e.evalIndexAssignment(target, val, env)
	case *ast.DotExpression:
		return e.evalDotAssignment(target, val, env)
	}

	return NULL
}

// evalIndexAssignment handles assignments to indexed values
func (e *Evaluator) evalIndexAssignment(expr *ast.IndexExpression, val Value, env *Environment) Value {
	left := e.Eval(expr.Left, env)
	if IsError(left) {
		return left
	}

	index := e.Eval(expr.Index, env)
	if IsError(index) {
		return index
	}

	switch container := left.(type) {
	case *ListValue:
		idx, ok := index.(*IntegerValue)
		if !ok {
			return NewError("list index must be integer")
		}
		if idx.Val < 0 || idx.Val >= int64(len(container.Elements)) {
			return NewError("list index out of range: %d", idx.Val)
		}
		container.Elements[idx.Val] = val
	case *TableValue:
		key, ok := index.(*StringValue)
		if !ok {
			return NewError("table key must be string")
		}
		container.Pairs[key.Val] = val
	case *RecordValue:
		key, ok := index.(*StringValue)
		if !ok {
			return NewError("record field name must be string")
		}
		// Verify field exists
		if _, exists := container.Fields[key.Val]; !exists {
			return NewError("record %s has no field '%s'", container.TypeName, key.Val)
		}
		container.Fields[key.Val] = val
	default:
		return NewError("index assignment not supported for %s", left.Type())
	}

	return NULL
}

// evalIdentifier looks up a variable or builtin
func (e *Evaluator) evalIdentifier(node *ast.Identifier, env *Environment) Value {
	// Check environment first
	if val, ok := env.Get(node.Value); ok {
		return val
	}

	// Check builtins
	if builtin, ok := e.builtins[node.Value]; ok {
		return builtin
	}

	return NewError("undefined identifier: %s", node.Value)
}

// evalPrefixExpression handles prefix expressions like -x, not x
func (e *Evaluator) evalPrefixExpression(expr *ast.PrefixExpression, env *Environment) Value {
	right := e.Eval(expr.Right, env)
	if IsError(right) {
		return right
	}

	switch expr.Operator {
	case "-":
		switch r := right.(type) {
		case *IntegerValue:
			return NewInteger(-r.Val)
		case *FloatValue:
			return NewFloat(-r.Val)
		default:
			return NewError("unknown operator: -%s", right.Type())
		}
	case "not":
		return NewBoolean(!right.IsTruthy())
	default:
		return NewError("unknown operator: %s%s", expr.Operator, right.Type())
	}
}

// evalInfixExpression handles binary expressions
func (e *Evaluator) evalInfixExpression(expr *ast.InfixExpression, env *Environment) Value {
	// Short-circuit evaluation for and/or
	if expr.Operator == "and" {
		left := e.Eval(expr.Left, env)
		if IsError(left) {
			return left
		}
		if !left.IsTruthy() {
			return FALSE
		}
		right := e.Eval(expr.Right, env)
		if IsError(right) {
			return right
		}
		return NewBoolean(right.IsTruthy())
	}

	if expr.Operator == "or" {
		left := e.Eval(expr.Left, env)
		if IsError(left) {
			return left
		}
		if left.IsTruthy() {
			return TRUE
		}
		right := e.Eval(expr.Right, env)
		if IsError(right) {
			return right
		}
		return NewBoolean(right.IsTruthy())
	}

	left := e.Eval(expr.Left, env)
	if IsError(left) {
		return left
	}

	right := e.Eval(expr.Right, env)
	if IsError(right) {
		return right
	}

	return e.evalBinaryOperation(left, expr.Operator, right)
}

// evalBinaryOperation handles the actual operation
func (e *Evaluator) evalBinaryOperation(left Value, op string, right Value) Value {
	// Integer operations
	if leftInt, ok := left.(*IntegerValue); ok {
		if rightInt, ok := right.(*IntegerValue); ok {
			return e.evalIntegerInfix(leftInt.Val, op, rightInt.Val)
		}
		if rightFloat, ok := right.(*FloatValue); ok {
			return e.evalFloatInfix(float64(leftInt.Val), op, rightFloat.Val)
		}
	}

	// Float operations
	if leftFloat, ok := left.(*FloatValue); ok {
		if rightInt, ok := right.(*IntegerValue); ok {
			return e.evalFloatInfix(leftFloat.Val, op, float64(rightInt.Val))
		}
		if rightFloat, ok := right.(*FloatValue); ok {
			return e.evalFloatInfix(leftFloat.Val, op, rightFloat.Val)
		}
	}

	// String operations
	if leftStr, ok := left.(*StringValue); ok {
		if rightStr, ok := right.(*StringValue); ok {
			return e.evalStringInfix(leftStr.Val, op, rightStr.Val)
		}
		// Auto-convert right side to string for concatenation
		if op == "&" {
			return NewString(leftStr.Val + right.String())
		}
	}
	// Also handle right side being string with & operator
	if op == "&" {
		if rightStr, ok := right.(*StringValue); ok {
			return NewString(left.String() + rightStr.Val)
		}
	}

	// Boolean operations
	if leftBool, ok := left.(*BooleanValue); ok {
		if rightBool, ok := right.(*BooleanValue); ok {
			return e.evalBooleanInfix(leftBool.Val, op, rightBool.Val)
		}
	}

	// Equality for nulls
	if op == "==" {
		if _, okL := left.(*NullValue); okL {
			if _, okR := right.(*NullValue); okR {
				return TRUE
			}
			return FALSE
		}
		if _, okR := right.(*NullValue); okR {
			return FALSE
		}
	}
	if op == "!=" {
		if _, okL := left.(*NullValue); okL {
			if _, okR := right.(*NullValue); okR {
				return FALSE
			}
			return TRUE
		}
		if _, okR := right.(*NullValue); okR {
			return TRUE
		}
	}

	return NewError("unknown operator: %s %s %s", left.Type(), op, right.Type())
}

func (e *Evaluator) evalIntegerInfix(left int64, op string, right int64) Value {
	switch op {
	case "+":
		return NewInteger(left + right)
	case "-":
		return NewInteger(left - right)
	case "*":
		return NewInteger(left * right)
	case "/":
		if right == 0 {
			return NewError("division by zero")
		}
		return NewFloat(float64(left) / float64(right))
	case "//":
		if right == 0 {
			return NewError("division by zero")
		}
		return NewInteger(left / right)
	case "%":
		if right == 0 {
			return NewError("modulo by zero")
		}
		return NewInteger(left % right)
	case "**":
		result := int64(1)
		for i := int64(0); i < right; i++ {
			result *= left
		}
		return NewInteger(result)
	case "<":
		return NewBoolean(left < right)
	case ">":
		return NewBoolean(left > right)
	case "<=":
		return NewBoolean(left <= right)
	case ">=":
		return NewBoolean(left >= right)
	case "==":
		return NewBoolean(left == right)
	case "!=":
		return NewBoolean(left != right)
	default:
		return NewError("unknown operator: integer %s integer", op)
	}
}

func (e *Evaluator) evalFloatInfix(left float64, op string, right float64) Value {
	switch op {
	case "+":
		return NewFloat(left + right)
	case "-":
		return NewFloat(left - right)
	case "*":
		return NewFloat(left * right)
	case "/":
		if right == 0 {
			return NewError("division by zero")
		}
		return NewFloat(left / right)
	case "//":
		if right == 0 {
			return NewError("division by zero")
		}
		return NewInteger(int64(left / right))
	case "%":
		if right == 0 {
			return NewError("modulo by zero")
		}
		return NewFloat(math.Mod(left, right))
	case "**":
		return NewFloat(math.Pow(left, right))
	case "<":
		return NewBoolean(left < right)
	case ">":
		return NewBoolean(left > right)
	case "<=":
		return NewBoolean(left <= right)
	case ">=":
		return NewBoolean(left >= right)
	case "==":
		return NewBoolean(left == right)
	case "!=":
		return NewBoolean(left != right)
	default:
		return NewError("unknown operator: float %s float", op)
	}
}

func (e *Evaluator) evalStringInfix(left string, op string, right string) Value {
	switch op {
	case "&":
		return NewString(left + right)
	case "+":
		return NewString(left + right)
	case "==":
		return NewBoolean(left == right)
	case "!=":
		return NewBoolean(left != right)
	case "<":
		return NewBoolean(left < right)
	case ">":
		return NewBoolean(left > right)
	case "<=":
		return NewBoolean(left <= right)
	case ">=":
		return NewBoolean(left >= right)
	default:
		return NewError("unknown operator: string %s string", op)
	}
}

func (e *Evaluator) evalBooleanInfix(left bool, op string, right bool) Value {
	switch op {
	case "==":
		return NewBoolean(left == right)
	case "!=":
		return NewBoolean(left != right)
	default:
		return NewError("unknown operator: boolean %s boolean", op)
	}
}

// evalIfStatement handles if/else
func (e *Evaluator) evalIfStatement(stmt *ast.IfStatement, env *Environment) Value {
	condition := e.Eval(stmt.Condition, env)
	if IsError(condition) {
		return condition
	}

	if condition.IsTruthy() {
		return e.evalBlockStatement(stmt.Consequence, NewEnclosedEnvironment(env))
	} else if stmt.Alternative != nil {
		return e.evalBlockStatement(stmt.Alternative, NewEnclosedEnvironment(env))
	}

	return NULL
}

// evalLoopStatement handles all loop variants
func (e *Evaluator) evalLoopStatement(stmt *ast.LoopStatement, env *Environment) Value {
	loopEnv := NewEnclosedEnvironment(env)

	// Counting loop: loop i from start to end [step n]
	if stmt.Variable != nil && stmt.Start != nil && stmt.End != nil {
		startVal := e.Eval(stmt.Start, env)
		if IsError(startVal) {
			return startVal
		}
		endVal := e.Eval(stmt.End, env)
		if IsError(endVal) {
			return endVal
		}

		start, ok1 := startVal.(*IntegerValue)
		end, ok2 := endVal.(*IntegerValue)
		if !ok1 || !ok2 {
			return NewError("loop range must be integers")
		}

		step := int64(1)
		if stmt.Step != nil {
			stepVal := e.Eval(stmt.Step, env)
			if stepInt, ok := stepVal.(*IntegerValue); ok {
				step = stepInt.Val
			}
		}

		for i := start.Val; (step > 0 && i <= end.Val) || (step < 0 && i >= end.Val); i += step {
			loopEnv.Define(stmt.Variable.Value, NewInteger(i))

			result := e.evalBlockStatement(stmt.Body, loopEnv)

			switch result.(type) {
			case *BreakValue:
				return NULL
			case *ContinueValue:
				continue
			case *ReturnValue, *ErrorValue:
				return result
			}
		}

		return NULL
	}

	// Iteration loop: loop item in collection
	if stmt.Variable != nil && stmt.Iterable != nil {
		iterVal := e.Eval(stmt.Iterable, env)
		if IsError(iterVal) {
			return iterVal
		}

		switch coll := iterVal.(type) {
		case *ListValue:
			for _, elem := range coll.Elements {
				loopEnv.Define(stmt.Variable.Value, elem)
				result := e.evalBlockStatement(stmt.Body, loopEnv)

				switch result.(type) {
				case *BreakValue:
					return NULL
				case *ContinueValue:
					continue
				case *ReturnValue, *ErrorValue:
					return result
				}
			}
		case *StringValue:
			for _, ch := range coll.Val {
				loopEnv.Define(stmt.Variable.Value, NewString(string(ch)))
				result := e.evalBlockStatement(stmt.Body, loopEnv)

				switch result.(type) {
				case *BreakValue:
					return NULL
				case *ContinueValue:
					continue
				case *ReturnValue, *ErrorValue:
					return result
				}
			}
		default:
			return NewError("cannot iterate over %s", iterVal.Type())
		}

		return NULL
	}

	// Conditional loop: loop condition
	if stmt.Condition != nil {
		for {
			condition := e.Eval(stmt.Condition, env)
			if IsError(condition) {
				return condition
			}
			if !condition.IsTruthy() {
				break
			}

			result := e.evalBlockStatement(stmt.Body, loopEnv)

			switch result.(type) {
			case *BreakValue:
				return NULL
			case *ContinueValue:
				continue
			case *ReturnValue, *ErrorValue:
				return result
			}
		}

		return NULL
	}

	// Infinite loop
	for {
		result := e.evalBlockStatement(stmt.Body, loopEnv)

		switch result.(type) {
		case *BreakValue:
			return NULL
		case *ContinueValue:
			continue
		case *ReturnValue, *ErrorValue:
			return result
		}
	}
}

// evalChooseStatement handles choose/choice/default
func (e *Evaluator) evalChooseStatement(stmt *ast.ChooseStatement, env *Environment) Value {
	testVal := e.Eval(stmt.Value, env)
	if IsError(testVal) {
		return testVal
	}

	for _, choice := range stmt.Choices {
		choiceVal := e.Eval(choice.Value, env)
		if IsError(choiceVal) {
			return choiceVal
		}

		// Compare values
		comparison := e.evalBinaryOperation(testVal, "==", choiceVal)
		if boolVal, ok := comparison.(*BooleanValue); ok && boolVal.Val {
			return e.evalBlockStatement(choice.Body, NewEnclosedEnvironment(env))
		}
	}

	// Default case
	if stmt.Default != nil {
		return e.evalBlockStatement(stmt.Default, NewEnclosedEnvironment(env))
	}

	return NULL
}

// evalTaskStatement defines a task
func (e *Evaluator) evalTaskStatement(stmt *ast.TaskStatement, env *Environment) Value {
	params := make([]string, len(stmt.Parameters))
	for i, p := range stmt.Parameters {
		params[i] = p.Value
	}

	task := &TaskValue{
		Name:       stmt.Name.Value,
		Parameters: params,
		Body:       stmt.Body,
		Env:        env,
	}

	env.Define(stmt.Name.Value, task)
	return NULL
}

// evalDeliverStatement handles return statements
func (e *Evaluator) evalDeliverStatement(stmt *ast.DeliverStatement, env *Environment) Value {
	if stmt.ReturnValue == nil {
		return &ReturnValue{Val: NULL}
	}

	val := e.Eval(stmt.ReturnValue, env)
	if IsError(val) {
		return val
	}

	return &ReturnValue{Val: val}
}

// evalAbortStatement handles abort (throw error)
func (e *Evaluator) evalAbortStatement(stmt *ast.AbortStatement, env *Environment) Value {
	if stmt.Message == nil {
		return NewError("abort")
	}

	msg := e.Eval(stmt.Message, env)
	if IsError(msg) {
		return msg
	}

	return NewError(msg.String())
}

// evalAttemptStatement handles attempt/handle/ensure
func (e *Evaluator) evalAttemptStatement(stmt *ast.AttemptStatement, env *Environment) Value {
	result := e.evalBlockStatement(stmt.Body, NewEnclosedEnvironment(env))

	// If error occurred, try handlers
	if errVal, isErr := result.(*ErrorValue); isErr && len(stmt.Handlers) > 0 {
		// Execute first matching handler (simple handler without pattern matching)
		handler := stmt.Handlers[0]
		handlerEnv := NewEnclosedEnvironment(env)
		if handler.ErrorName != nil {
			handlerEnv.Define(handler.ErrorName.Value, NewString(errVal.Message))
		}
		result = e.evalBlockStatement(handler.Body, handlerEnv)
	}

	// Always run ensure block
	if stmt.Ensure != nil {
		e.evalBlockStatement(stmt.Ensure, NewEnclosedEnvironment(env))
	}

	// Don't return error if it was handled
	if _, isErr := result.(*ErrorValue); isErr {
		return NULL
	}

	return result
}

// evalCallExpression handles task/function calls
func (e *Evaluator) evalCallExpression(call *ast.CallExpression, env *Environment) Value {
	fn := e.Eval(call.Function, env)
	if IsError(fn) {
		return fn
	}

	args := []Value{}
	for _, arg := range call.Arguments {
		argVal := e.Eval(arg, env)
		if IsError(argVal) {
			return argVal
		}
		args = append(args, argVal)
	}

	return e.applyFunction(fn, args)
}

// applyFunction executes a function with arguments
func (e *Evaluator) applyFunction(fn Value, args []Value) Value {
	switch f := fn.(type) {
	case *TaskValue:
		if len(args) != len(f.Parameters) {
			return NewError("wrong number of arguments: got=%d, want=%d",
				len(args), len(f.Parameters))
		}

		taskEnv := NewEnclosedEnvironment(f.Env)
		for i, param := range f.Parameters {
			taskEnv.Define(param, args[i])
		}

		body, ok := f.Body.(*ast.BlockStatement)
		if !ok {
			return NewError("invalid task body")
		}

		result := e.evalBlockStatement(body, taskEnv)
		if returnVal, ok := result.(*ReturnValue); ok {
			return returnVal.Val
		}
		return result

	case *BuiltinValue:
		return f.Fn(args...)

	default:
		return NewError("not a function: %s", fn.Type())
	}
}

// evalListLiteral evaluates a list literal
func (e *Evaluator) evalListLiteral(list *ast.ListLiteral, env *Environment) Value {
	elements := []Value{}
	for _, elem := range list.Elements {
		val := e.Eval(elem, env)
		if IsError(val) {
			return val
		}
		elements = append(elements, val)
	}
	return NewList(elements)
}

// evalTableLiteral evaluates a table literal
func (e *Evaluator) evalTableLiteral(table *ast.TableLiteral, env *Environment) Value {
	pairs := make(map[string]Value)
	for keyExpr, valExpr := range table.Pairs {
		key := e.Eval(keyExpr, env)
		if IsError(key) {
			return key
		}
		keyStr, ok := key.(*StringValue)
		if !ok {
			return NewError("table key must be string, got %s", key.Type())
		}

		val := e.Eval(valExpr, env)
		if IsError(val) {
			return val
		}
		pairs[keyStr.Val] = val
	}
	return NewTable(pairs)
}

// evalIndexExpression handles array[index] and table[key]
func (e *Evaluator) evalIndexExpression(expr *ast.IndexExpression, env *Environment) Value {
	left := e.Eval(expr.Left, env)
	if IsError(left) {
		return left
	}

	index := e.Eval(expr.Index, env)
	if IsError(index) {
		return index
	}

	switch container := left.(type) {
	case *ListValue:
		idx, ok := index.(*IntegerValue)
		if !ok {
			return NewError("list index must be integer")
		}
		if idx.Val < 0 || idx.Val >= int64(len(container.Elements)) {
			return NULL
		}
		return container.Elements[idx.Val]
	case *TableValue:
		key, ok := index.(*StringValue)
		if !ok {
			return NewError("table key must be string")
		}
		if val, exists := container.Pairs[key.Val]; exists {
			return val
		}
		return NULL
	case *StringValue:
		idx, ok := index.(*IntegerValue)
		if !ok {
			return NewError("string index must be integer")
		}
		if idx.Val < 0 || idx.Val >= int64(len(container.Val)) {
			return NULL
		}
		return NewString(string(container.Val[idx.Val]))
	case *RecordValue:
		key, ok := index.(*StringValue)
		if !ok {
			return NewError("record field name must be string")
		}
		if val, exists := container.Fields[key.Val]; exists {
			return val
		}
		return NewError("record %s has no field '%s'", container.TypeName, key.Val)
	default:
		return NewError("index not supported for %s", left.Type())
	}
}

// evalDotExpression handles object.property
func (e *Evaluator) evalDotExpression(expr *ast.DotExpression, env *Environment) Value {
	// First, try to resolve as a qualified module name (e.g., "io.files")
	qualifiedName := e.dotExpressionToQualifiedName(expr)
	if qualifiedName != "" {
		if val, ok := env.Get(qualifiedName); ok {
			return val
		}
	}

	left := e.Eval(expr.Left, env)
	if IsError(left) {
		return left
	}

	// If left is NULL, try a qualified name lookup for nested modules
	if left == NULL || left == nil {
		// The identifier wasn't found directly, but the full path might be registered
		if qualifiedName != "" {
			return NewError("module or property not found: %s", qualifiedName)
		}
	}

	if table, ok := left.(*TableValue); ok {
		if val, exists := table.Pairs[expr.Right.Value]; exists {
			return val
		}
		return NULL
	}

	// Handle record field access
	if record, ok := left.(*RecordValue); ok {
		if val, exists := record.Fields[expr.Right.Value]; exists {
			return val
		}
		return NewError("record %s has no field '%s'", record.TypeName, expr.Right.Value)
	}

	return NewError("property access not supported for %s", left.Type())
}

// dotExpressionToQualifiedName converts a dot expression to a qualified string name
func (e *Evaluator) dotExpressionToQualifiedName(expr *ast.DotExpression) string {
	parts := []string{}

	var walk func(node ast.Expression) bool
	walk = func(node ast.Expression) bool {
		switch n := node.(type) {
		case *ast.DotExpression:
			if !walk(n.Left) {
				return false
			}
			parts = append(parts, n.Right.Value)
			return true
		case *ast.Identifier:
			parts = append(parts, n.Value)
			return true
		default:
			return false
		}
	}

	if !walk(expr) {
		return ""
	}

	result := ""
	for i, p := range parts {
		if i > 0 {
			result += "."
		}
		result += p
	}
	return result
}

// evalDotAssignment handles assignment to object.property
func (e *Evaluator) evalDotAssignment(expr *ast.DotExpression, val Value, env *Environment) Value {
	left := e.Eval(expr.Left, env)
	if IsError(left) {
		return left
	}

	if table, ok := left.(*TableValue); ok {
		table.Pairs[expr.Right.Value] = val
		return NULL
	}

	if record, ok := left.(*RecordValue); ok {
		// Verify field exists
		if _, exists := record.Fields[expr.Right.Value]; !exists {
			return NewError("record %s has no field '%s'", record.TypeName, expr.Right.Value)
		}
		record.Fields[expr.Right.Value] = val
		return NULL
	}

	return NewError("property assignment not supported for %s", left.Type())
}

// evalRecordStatement registers a record type definition
func (e *Evaluator) evalRecordStatement(stmt *ast.RecordStatement, env *Environment) Value {
	fields := make([]*RecordFieldDef, 0, len(stmt.Fields))

	// Process based on (inheritance) - these fields keep their required status
	for _, basedOnIdent := range stmt.BasedOn {
		baseType, ok := env.Get(basedOnIdent.Value)
		if !ok {
			return NewError("unknown record type: %s", basedOnIdent.Value)
		}
		baseRecordType, ok := baseType.(*RecordTypeValue)
		if !ok {
			return NewError("%s is not a record type", basedOnIdent.Value)
		}
		// Copy fields from base type, preserving required status
		for _, field := range baseRecordType.Fields {
			fieldCopy := &RecordFieldDef{
				Name:         field.Name,
				TypeName:     field.TypeName,
				DefaultValue: field.DefaultValue,
				Required:     field.Required,
			}
			fields = append(fields, fieldCopy)
		}
	}

	// Process with (composition) - all fields become optional
	for _, withIdent := range stmt.With {
		withType, ok := env.Get(withIdent.Value)
		if !ok {
			return NewError("unknown record type: %s", withIdent.Value)
		}
		withRecordType, ok := withType.(*RecordTypeValue)
		if !ok {
			return NewError("%s is not a record type", withIdent.Value)
		}
		// Copy fields from with type, making all optional with null default
		for _, field := range withRecordType.Fields {
			defaultVal := field.DefaultValue
			if defaultVal == nil {
				defaultVal = NULL
			}
			fieldCopy := &RecordFieldDef{
				Name:         field.Name,
				TypeName:     field.TypeName,
				DefaultValue: defaultVal,
				Required:     false, // with makes all fields optional
			}
			fields = append(fields, fieldCopy)
		}
	}

	// Process own fields - first field is required, rest need defaults
	for i, field := range stmt.Fields {
		var defaultVal Value
		isRequired := (i == 0 && len(stmt.BasedOn) == 0) // First field is required unless we have based on

		if field.DefaultValue != nil {
			defaultVal = e.Eval(field.DefaultValue, env)
			if IsError(defaultVal) {
				return defaultVal
			}
			isRequired = false
		}

		typeName := ""
		if field.TypeName != nil {
			typeName = field.TypeName.Value
		}

		fieldDef := &RecordFieldDef{
			Name:         field.Name.Value,
			TypeName:     typeName,
			DefaultValue: defaultVal,
			Required:     isRequired,
		}
		fields = append(fields, fieldDef)
	}

	recordType := &RecordTypeValue{
		Name:   stmt.Name.Value,
		Fields: fields,
	}

	env.Define(stmt.Name.Value, recordType)
	return NULL
}

// evalRecordLiteral creates a record instance
func (e *Evaluator) evalRecordLiteral(lit *ast.RecordLiteral, env *Environment) Value {
	// Look up the record type
	recordTypeVal, ok := env.Get(lit.Type.Value)
	if !ok {
		return NewError("unknown record type: %s", lit.Type.Value)
	}

	recordType, ok := recordTypeVal.(*RecordTypeValue)
	if !ok {
		return NewError("%s is not a record type", lit.Type.Value)
	}

	// Create instance with field values
	instance := &RecordValue{
		TypeName: recordType.Name,
		Fields:   make(map[string]Value),
	}

	// First, set all default values
	for _, fieldDef := range recordType.Fields {
		if fieldDef.DefaultValue != nil {
			instance.Fields[fieldDef.Name] = fieldDef.DefaultValue
		}
	}

	// Then, set provided values
	for fieldName, expr := range lit.Fields {
		val := e.Eval(expr, env)
		if IsError(val) {
			return val
		}

		// Verify field exists in type
		found := false
		for _, fieldDef := range recordType.Fields {
			if fieldDef.Name == fieldName {
				found = true
				break
			}
		}
		if !found {
			return NewError("record %s has no field '%s'", recordType.Name, fieldName)
		}

		instance.Fields[fieldName] = val
	}

	// Check all required fields are provided
	for _, fieldDef := range recordType.Fields {
		if fieldDef.Required {
			if _, exists := instance.Fields[fieldDef.Name]; !exists {
				return NewError("required field '%s' not provided for record %s", fieldDef.Name, recordType.Name)
			}
		}
	}

	return instance
}

// evalUseStatement handles import statements
func (e *Evaluator) evalUseStatement(stmt *ast.UseStatement, env *Environment) Value {
	// Process task-level imports (most specific - import specific tasks directly)
	for _, taskExpr := range stmt.Tasks {
		pathParts := e.dotExpressionToPath(taskExpr)
		if len(pathParts) < 2 {
			return NewError("task import requires at least module.TaskName format")
		}

		taskName := pathParts[len(pathParts)-1]
		modulePath := pathParts[:len(pathParts)-1]

		// Load the module
		result := e.loadModule(modulePath, env)
		if IsError(result) {
			return result
		}

		// Get the module's namespace and extract the specific task
		moduleKey := e.pathToModuleKey(modulePath)
		if moduleNS, ok := env.Get(moduleKey); ok {
			if nsTable, ok := moduleNS.(*TableValue); ok {
				if taskVal, exists := nsTable.Pairs[taskName]; exists {
					// Register task directly in environment (no prefix needed)
					env.Define(taskName, taskVal)
				} else {
					return NewError("task '%s' not found in module '%s'", taskName, moduleKey)
				}
			}
		}
	}

	// Process module-level imports
	for _, modExpr := range stmt.Modules {
		modulePath := e.dotExpressionToPath(modExpr)

		// Load the module
		result := e.loadModule(modulePath, env)
		if IsError(result) {
			return result
		}
	}

	// Process assembly-level imports (just mark as available)
	// Assemblies don't need to load anything upfront - they enable access to modules within
	for _, asmExpr := range stmt.Assemblies {
		asmPath := e.dotExpressionToPath(asmExpr)
		// Register assembly as available for qualified access
		asmKey := e.pathToModuleKey(asmPath)
		if _, ok := env.Get(asmKey); !ok {
			env.Define(asmKey, NewString("assembly:"+asmKey))
		}
	}

	return NULL
}

// dotExpressionToPath converts a DotExpression to a path slice
func (e *Evaluator) dotExpressionToPath(expr *ast.DotExpression) []string {
	parts := []string{}

	var walk func(node ast.Expression)
	walk = func(node ast.Expression) {
		switch n := node.(type) {
		case *ast.DotExpression:
			walk(n.Left)
			parts = append(parts, n.Right.Value)
		case *ast.Identifier:
			parts = append(parts, n.Value)
		}
	}
	walk(expr)
	return parts
}

// pathToModuleKey converts a path to a module key (e.g., ["io", "files"] -> "io.files")
func (e *Evaluator) pathToModuleKey(path []string) string {
	result := ""
	for i, p := range path {
		if i > 0 {
			result += "."
		}
		result += p
	}
	return result
}

// loadModule loads a module file and evaluates it
func (e *Evaluator) loadModule(modulePath []string, env *Environment) Value {
	moduleKey := e.pathToModuleKey(modulePath)

	// Check if already loaded
	if e.loadedModules[moduleKey] {
		return NULL
	}

	// Build file path
	filePath := e.resolveModulePath(modulePath)
	if filePath == "" {
		return NewError("module not found: %s", moduleKey)
	}

	// Read the file
	content, err := e.readFile(filePath)
	if err != nil {
		return NewError("failed to load module '%s': %s", moduleKey, err.Error())
	}

	// Parse the module
	program, parseErr := e.parseModule(content)
	if parseErr != nil {
		return NewError("failed to parse module '%s': %s", moduleKey, parseErr.Error())
	}

	// Create a new environment for the module
	moduleEnv := NewEnvironment()
	// Module gets its own scope but shares parent chain for access to builtins

	// Evaluate the module
	result := e.Eval(program, moduleEnv)
	if IsError(result) {
		return result
	}

	// Mark as loaded
	e.loadedModules[moduleKey] = true

	// Create namespace table with all module exports
	exports := NewTable(make(map[string]Value))
	for name, val := range moduleEnv.store {
		exports.Pairs[name] = val
	}

	// Register module namespace in environment
	env.Define(moduleKey, exports)

	// Also register intermediate paths for qualified access
	for i := 1; i < len(modulePath); i++ {
		partialKey := e.pathToModuleKey(modulePath[:i])
		if _, ok := env.Get(partialKey); !ok {
			env.Define(partialKey, NewTable(make(map[string]Value)))
		}
	}

	return NULL
}

// resolveModulePath finds the file path for a module
func (e *Evaluator) resolveModulePath(modulePath []string) string {
	// Try as a direct .plain file in base dir
	// e.g., ["utils"] -> "utils.plain"
	// e.g., ["io", "files"] -> "io/files.plain"

	baseDir := e.baseDir
	if baseDir == "" {
		baseDir = "."
	}

	// Build path from parts
	pathStr := baseDir
	for i, part := range modulePath {
		if i < len(modulePath)-1 {
			// Directory part
			pathStr = e.joinPath(pathStr, part)
		} else {
			// Last part is the filename
			pathStr = e.joinPath(pathStr, part+".plain")
		}
	}

	// Check if file exists
	if e.fileExists(pathStr) {
		return pathStr
	}

	return ""
}

// joinPath joins path segments
func (e *Evaluator) joinPath(base, segment string) string {
	if base == "" || base == "." {
		return segment
	}
	return base + "/" + segment
}

// fileExists checks if a file exists
func (e *Evaluator) fileExists(path string) bool {
	_, err := e.readFile(path)
	return err == nil
}

// readFile reads a file from disk
func (e *Evaluator) readFile(path string) (string, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return "", err
	}
	return string(data), nil
}

// parseModule parses PLAIN source code into an AST
func (e *Evaluator) parseModule(source string) (*ast.Program, error) {
	l := lexer.New(source)
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) > 0 {
		return nil, fmt.Errorf("%s", p.Errors()[0])
	}
	return program, nil
}

// evalInterpolatedString handles v"..." strings
func (e *Evaluator) evalInterpolatedString(str *ast.InterpolatedString, env *Environment) Value {
	result := str.Value

	// Parse and evaluate expressions in {expr} format
	for {
		start := -1
		end := -1
		braceDepth := 0

		// Find the next {expr} to interpolate
		for i, ch := range result {
			if ch == '{' {
				if start < 0 {
					start = i
					braceDepth = 1
				} else {
					braceDepth++
				}
			} else if ch == '}' && start >= 0 {
				braceDepth--
				if braceDepth == 0 {
					end = i
					break
				}
			}
		}

		if start < 0 || end < 0 {
			break
		}

		exprStr := result[start+1 : end]

		// Parse the expression by wrapping it in a minimal program
		// We create "task Main()\n    display(expr)" and extract the expression from the AST
		programStr := "task Main()\n    display(" + exprStr + ")"
		lex := lexer.New(programStr)
		p := parser.New(lex)
		program := p.ParseProgram()

		if len(p.Errors()) > 0 || len(program.Statements) == 0 {
			// If parsing failed, leave it as literal text
			result = result[:start] + "{" + exprStr + "}" + result[end+1:]
			break
		}

		// Extract the expression from the display() call
		var expr ast.Expression
		if taskStmt, ok := program.Statements[0].(*ast.TaskStatement); ok {
			if len(taskStmt.Body.Statements) > 0 {
				if exprStmt, ok := taskStmt.Body.Statements[0].(*ast.ExpressionStatement); ok {
					if callExpr, ok := exprStmt.Expression.(*ast.CallExpression); ok {
						if len(callExpr.Arguments) > 0 {
							expr = callExpr.Arguments[0]
						}
					}
				}
			}
		}

		if expr == nil {
			// Couldn't extract expression, leave as literal
			result = result[:start] + "{" + exprStr + "}" + result[end+1:]
			break
		}

		// Evaluate the expression
		val := e.Eval(expr, env)
		if IsError(val) {
			// If evaluation failed, leave it as literal text
			result = result[:start] + "{" + exprStr + "}" + result[end+1:]
			break
		}

		// Replace {expr} with the string representation of the value
		result = result[:start] + val.String() + result[end+1:]
	}

	return NewString(result)
}

// Run is a convenience function to parse and execute PLAIN code
func Run(code string) (Value, error) {
	// Import lexer and parser
	// This creates a circular dependency, so we'll need the caller to do parsing
	return nil, fmt.Errorf("use Eval with parsed AST instead")
}

// callTask is used by the event system to invoke timer callbacks
func (e *Evaluator) callTask(task *TaskValue, args []Value) Value {
	// Adjust args to match parameter count if needed
	if len(args) > len(task.Parameters) {
		args = args[:len(task.Parameters)]
	}
	if len(args) < len(task.Parameters) {
		// Pad with nulls if fewer args (shouldn't normally happen)
		for len(args) < len(task.Parameters) {
			args = append(args, NULL)
		}
	}
	return e.applyFunction(task, args)
}

// output prints text (used by event system for error messages)
func (e *Evaluator) output(msg string) {
	fmt.Print(msg)
}
