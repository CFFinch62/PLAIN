package runtime

import (
	"fmt"
	"plain/internal/ast"
)

// Evaluator executes PLAIN programs
type Evaluator struct {
	builtins map[string]*BuiltinValue
}

// New creates a new Evaluator
func New() *Evaluator {
	return &Evaluator{
		builtins: GetBuiltins(),
	}
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
		// Record definitions are handled at parse time
		return NULL

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
	val := e.Eval(stmt.Value, env)
	if IsError(val) {
		return val
	}

	switch target := stmt.Name.(type) {
	case *ast.Identifier:
		if !env.Set(target.Value, val) {
			return NewError("undefined variable: %s", target.Value)
		}
	case *ast.IndexExpression:
		return e.evalIndexAssignment(target, val, env)
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
	default:
		return NewError("index not supported for %s", left.Type())
	}
}

// evalDotExpression handles object.property
func (e *Evaluator) evalDotExpression(expr *ast.DotExpression, env *Environment) Value {
	left := e.Eval(expr.Left, env)
	if IsError(left) {
		return left
	}

	if table, ok := left.(*TableValue); ok {
		if val, exists := table.Pairs[expr.Right.Value]; exists {
			return val
		}
		return NULL
	}

	return NewError("property access not supported for %s", left.Type())
}

// evalInterpolatedString handles v"..." strings
func (e *Evaluator) evalInterpolatedString(str *ast.InterpolatedString, env *Environment) Value {
	// For now, just return the string as-is
	// Full interpolation would require parsing the {expr} parts
	result := str.Value

	// Simple variable interpolation: replace {varname} with value
	// This is a simplified implementation
	for {
		start := -1
		end := -1
		for i, ch := range result {
			if ch == '{' {
				start = i
			} else if ch == '}' && start >= 0 {
				end = i
				break
			}
		}
		if start < 0 || end < 0 {
			break
		}

		varName := result[start+1 : end]
		val, ok := env.Get(varName)
		if ok {
			result = result[:start] + val.String() + result[end+1:]
		} else {
			result = result[:start] + "{" + varName + "}" + result[end+1:]
			break
		}
	}

	return NewString(result)
}

// Run is a convenience function to parse and execute PLAIN code
func Run(code string) (Value, error) {
	// Import lexer and parser
	// This creates a circular dependency, so we'll need the caller to do parsing
	return nil, fmt.Errorf("use Eval with parsed AST instead")
}
