package runtime

import (
	"bufio"
	"fmt"
	"os"
)

// BuiltinFunc represents a built-in function
type BuiltinFunc func(args ...Value) Value

// BuiltinValue wraps a built-in function
type BuiltinValue struct {
	Name string
	Fn   BuiltinFunc
}

func (v *BuiltinValue) Type() string   { return "builtin" }
func (v *BuiltinValue) String() string { return fmt.Sprintf("<builtin %s>", v.Name) }
func (v *BuiltinValue) IsTruthy() bool { return true }

// Scanner for input
var inputScanner = bufio.NewScanner(os.Stdin)

// GetBuiltins returns a map of built-in functions
func GetBuiltins() map[string]*BuiltinValue {
	return map[string]*BuiltinValue{
		"display": {
			Name: "display",
			Fn: func(args ...Value) Value {
				for i, arg := range args {
					if i > 0 {
						fmt.Print(" ")
					}
					fmt.Print(arg.String())
				}
				fmt.Println()
				return NULL
			},
		},
		"get": {
			Name: "get",
			Fn: func(args ...Value) Value {
				if len(args) > 0 {
					fmt.Print(args[0].String())
				}
				if inputScanner.Scan() {
					return NewString(inputScanner.Text())
				}
				return NewString("")
			},
		},
		"len": {
			Name: "len",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("len() takes exactly 1 argument")
				}
				switch arg := args[0].(type) {
				case *StringValue:
					return NewInteger(int64(len(arg.Val)))
				case *ListValue:
					return NewInteger(int64(len(arg.Elements)))
				case *TableValue:
					return NewInteger(int64(len(arg.Pairs)))
				default:
					return NewError("len() argument must be string, list, or table")
				}
			},
		},
		"type_of": {
			Name: "type_of",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("type_of() takes exactly 1 argument")
				}
				return NewString(args[0].Type())
			},
		},
		"to_int": {
			Name: "to_int",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("to_int() takes exactly 1 argument")
				}
				switch arg := args[0].(type) {
				case *IntegerValue:
					return arg
				case *FloatValue:
					return NewInteger(int64(arg.Val))
				case *StringValue:
					var i int64
					_, err := fmt.Sscanf(arg.Val, "%d", &i)
					if err != nil {
						return NewError("cannot convert '%s' to integer", arg.Val)
					}
					return NewInteger(i)
				case *BooleanValue:
					if arg.Val {
						return NewInteger(1)
					}
					return NewInteger(0)
				default:
					return NewError("cannot convert %s to integer", arg.Type())
				}
			},
		},
		"to_float": {
			Name: "to_float",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("to_float() takes exactly 1 argument")
				}
				switch arg := args[0].(type) {
				case *IntegerValue:
					return NewFloat(float64(arg.Val))
				case *FloatValue:
					return arg
				case *StringValue:
					var f float64
					_, err := fmt.Sscanf(arg.Val, "%f", &f)
					if err != nil {
						return NewError("cannot convert '%s' to float", arg.Val)
					}
					return NewFloat(f)
				default:
					return NewError("cannot convert %s to float", arg.Type())
				}
			},
		},
		"to_string": {
			Name: "to_string",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("to_string() takes exactly 1 argument")
				}
				return NewString(args[0].String())
			},
		},
	}
}
