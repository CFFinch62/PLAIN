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

// FloatPrecision controls the number of decimal places for float display
// -1 means default formatting (standard Go %g)
// >= 0 means fixed precision
var FloatPrecision int = -1

func (v *FloatValue) Type() string   { return "float" }
func (v *FloatValue) String() string {
	if FloatPrecision < 0 {
		return fmt.Sprintf("%g", v.Val)
	}
	return fmt.Sprintf("%.*f", FloatPrecision, v.Val)
}
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

// FileHandleValue represents an open file handle
type FileHandleValue struct {
	Path     string
	Mode     string
	Handle   interface{} // *os.File
	IsBinary bool
}

func (v *FileHandleValue) Type() string   { return "file_handle" }
func (v *FileHandleValue) String() string { return fmt.Sprintf("<file %s mode=%s>", v.Path, v.Mode) }
func (v *FileHandleValue) IsTruthy() bool { return v.Handle != nil }

// BytesValue represents binary data
type BytesValue struct {
	Data []byte
}

func (v *BytesValue) Type() string   { return "bytes" }
func (v *BytesValue) String() string { return fmt.Sprintf("<bytes len=%d>", len(v.Data)) }
func (v *BytesValue) IsTruthy() bool { return len(v.Data) > 0 }

// TimerValue represents a timer handle
type TimerValue struct {
	ID        int
	Interval  int64       // milliseconds
	Callback  interface{} // *TaskValue
	IsOneShot bool        // true for timeout, false for repeating timer
	Running   bool
	Cancelled bool
}

func (v *TimerValue) Type() string   { return "timer" }
func (v *TimerValue) String() string { return fmt.Sprintf("<timer id=%d>", v.ID) }
func (v *TimerValue) IsTruthy() bool { return !v.Cancelled }

// ============================================================================
// Record Values
// ============================================================================

// RecordFieldDef defines a field in a record type
type RecordFieldDef struct {
	Name         string
	TypeName     string
	DefaultValue Value // nil for required fields
	Required     bool
}

// RecordTypeValue represents a record type definition (schema)
type RecordTypeValue struct {
	Name   string
	Fields []*RecordFieldDef
}

func (v *RecordTypeValue) Type() string   { return "record_type" }
func (v *RecordTypeValue) String() string { return fmt.Sprintf("<record type %s>", v.Name) }
func (v *RecordTypeValue) IsTruthy() bool { return true }

// RecordValue represents an instance of a record
type RecordValue struct {
	TypeName string
	Fields   map[string]Value
}

func (v *RecordValue) Type() string { return "record" }
func (v *RecordValue) String() string {
	pairs := make([]string, 0, len(v.Fields))
	for key, val := range v.Fields {
		pairs = append(pairs, fmt.Sprintf("%s: %s", key, val.String()))
	}
	return fmt.Sprintf("%s(%s)", v.TypeName, strings.Join(pairs, ", "))
}
func (v *RecordValue) IsTruthy() bool { return true }

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
