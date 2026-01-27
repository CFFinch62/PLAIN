package runtime

import (
	"fmt"
	"strings"
)

// Value represents a runtime value in PLAIN
type Value interface {
	Type() string
	String() string
	IsTruthy() bool
}

// ============================================================================
// Primitive Values
// ============================================================================

// IntegerValue represents an integer
type IntegerValue struct {
	Val int64
}

func (v *IntegerValue) Type() string   { return "integer" }
func (v *IntegerValue) String() string { return fmt.Sprintf("%d", v.Val) }
func (v *IntegerValue) IsTruthy() bool { return v.Val != 0 }

// FloatValue represents a float
type FloatValue struct {
	Val float64
}

func (v *FloatValue) Type() string   { return "float" }
func (v *FloatValue) String() string { return fmt.Sprintf("%g", v.Val) }
func (v *FloatValue) IsTruthy() bool { return v.Val != 0 }

// StringValue represents a string
type StringValue struct {
	Val string
}

func (v *StringValue) Type() string   { return "string" }
func (v *StringValue) String() string { return v.Val }
func (v *StringValue) IsTruthy() bool { return v.Val != "" }

// BooleanValue represents a boolean
type BooleanValue struct {
	Val bool
}

func (v *BooleanValue) Type() string   { return "boolean" }
func (v *BooleanValue) String() string { return fmt.Sprintf("%t", v.Val) }
func (v *BooleanValue) IsTruthy() bool { return v.Val }

// NullValue represents null
type NullValue struct{}

func (v *NullValue) Type() string   { return "null" }
func (v *NullValue) String() string { return "null" }
func (v *NullValue) IsTruthy() bool { return false }

// Singleton null value
var NULL = &NullValue{}
var TRUE = &BooleanValue{Val: true}
var FALSE = &BooleanValue{Val: false}

// ============================================================================
// Collection Values
// ============================================================================

// ListValue represents a list
type ListValue struct {
	Elements []Value
}

func (v *ListValue) Type() string { return "list" }
func (v *ListValue) String() string {
	elements := make([]string, len(v.Elements))
	for i, elem := range v.Elements {
		elements[i] = elem.String()
	}
	return "[" + strings.Join(elements, ", ") + "]"
}
func (v *ListValue) IsTruthy() bool { return len(v.Elements) > 0 }

// TableValue represents a table (dictionary)
type TableValue struct {
	Pairs map[string]Value
}

func (v *TableValue) Type() string { return "table" }
func (v *TableValue) String() string {
	pairs := make([]string, 0, len(v.Pairs))
	for key, val := range v.Pairs {
		pairs = append(pairs, fmt.Sprintf("%q: %s", key, val.String()))
	}
	return "{" + strings.Join(pairs, ", ") + "}"
}
func (v *TableValue) IsTruthy() bool { return len(v.Pairs) > 0 }

// ============================================================================
// Special Values
// ============================================================================

// TaskValue represents a task definition
type TaskValue struct {
	Name       string
	Parameters []string
	Body       interface{} // *ast.BlockStatement
	Env        *Environment
}

func (v *TaskValue) Type() string   { return "task" }
func (v *TaskValue) String() string { return fmt.Sprintf("<task %s>", v.Name) }
func (v *TaskValue) IsTruthy() bool { return true }

// ReturnValue wraps a value being returned from a task
type ReturnValue struct {
	Val Value
}

func (v *ReturnValue) Type() string   { return "return" }
func (v *ReturnValue) String() string { return v.Val.String() }
func (v *ReturnValue) IsTruthy() bool { return v.Val.IsTruthy() }

// ErrorValue represents a runtime error
type ErrorValue struct {
	Message string
}

func (v *ErrorValue) Type() string   { return "error" }
func (v *ErrorValue) String() string { return "ERROR: " + v.Message }
func (v *ErrorValue) IsTruthy() bool { return false }

// BreakValue signals loop exit
type BreakValue struct{}

func (v *BreakValue) Type() string   { return "break" }
func (v *BreakValue) String() string { return "<break>" }
func (v *BreakValue) IsTruthy() bool { return false }

// ContinueValue signals loop continue
type ContinueValue struct{}

func (v *ContinueValue) Type() string   { return "continue" }
func (v *ContinueValue) String() string { return "<continue>" }
func (v *ContinueValue) IsTruthy() bool { return false }

// ============================================================================
// Helper constructors
// ============================================================================

// NewInteger creates a new integer value
func NewInteger(val int64) *IntegerValue {
	return &IntegerValue{Val: val}
}

// NewFloat creates a new float value
func NewFloat(val float64) *FloatValue {
	return &FloatValue{Val: val}
}

// NewString creates a new string value
func NewString(val string) *StringValue {
	return &StringValue{Val: val}
}

// NewBoolean returns TRUE or FALSE singleton
func NewBoolean(val bool) *BooleanValue {
	if val {
		return TRUE
	}
	return FALSE
}

// NewList creates a new list value
func NewList(elements []Value) *ListValue {
	return &ListValue{Elements: elements}
}

// NewTable creates a new table value
func NewTable(pairs map[string]Value) *TableValue {
	return &TableValue{Pairs: pairs}
}

// NewError creates a new error value
func NewError(format string, args ...interface{}) *ErrorValue {
	return &ErrorValue{Message: fmt.Sprintf(format, args...)}
}

// IsError checks if a value is an error
func IsError(v Value) bool {
	_, ok := v.(*ErrorValue)
	return ok
}
