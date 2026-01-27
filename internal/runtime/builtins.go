package runtime

import (
	"bufio"
	"fmt"
	"math"
	"math/rand"
	"os"
	"sort"
	"strings"
	"time"
)

func init() {
	rand.Seed(time.Now().UnixNano())
}

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
		// ============================================================
		// Console I/O
		// ============================================================
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

		// ============================================================
		// Type Checking
		// ============================================================
		"is_int": {
			Name: "is_int",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("is_int() takes exactly 1 argument")
				}
				_, ok := args[0].(*IntegerValue)
				return NewBoolean(ok)
			},
		},
		"is_float": {
			Name: "is_float",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("is_float() takes exactly 1 argument")
				}
				_, ok := args[0].(*FloatValue)
				return NewBoolean(ok)
			},
		},
		"is_string": {
			Name: "is_string",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("is_string() takes exactly 1 argument")
				}
				_, ok := args[0].(*StringValue)
				return NewBoolean(ok)
			},
		},
		"is_bool": {
			Name: "is_bool",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("is_bool() takes exactly 1 argument")
				}
				_, ok := args[0].(*BooleanValue)
				return NewBoolean(ok)
			},
		},
		"is_list": {
			Name: "is_list",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("is_list() takes exactly 1 argument")
				}
				_, ok := args[0].(*ListValue)
				return NewBoolean(ok)
			},
		},
		"is_table": {
			Name: "is_table",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("is_table() takes exactly 1 argument")
				}
				_, ok := args[0].(*TableValue)
				return NewBoolean(ok)
			},
		},
		"is_null": {
			Name: "is_null",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("is_null() takes exactly 1 argument")
				}
				_, ok := args[0].(*NullValue)
				return NewBoolean(ok)
			},
		},

		// ============================================================
		// Type Conversion
		// ============================================================
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
		"to_bool": {
			Name: "to_bool",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("to_bool() takes exactly 1 argument")
				}
				switch arg := args[0].(type) {
				case *BooleanValue:
					return arg
				case *IntegerValue:
					return NewBoolean(arg.Val != 0)
				case *FloatValue:
					return NewBoolean(arg.Val != 0)
				case *StringValue:
					// Empty string is false, non-empty is true
					return NewBoolean(arg.Val != "")
				case *NullValue:
					return NewBoolean(false)
				case *ListValue:
					return NewBoolean(len(arg.Elements) > 0)
				case *TableValue:
					return NewBoolean(len(arg.Pairs) > 0)
				default:
					return NewBoolean(true)
				}
			},
		},

		// ============================================================
		// String Operations
		// ============================================================
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
		"upper": {
			Name: "upper",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("upper() takes exactly 1 argument")
				}
				str, ok := args[0].(*StringValue)
				if !ok {
					return NewError("upper() argument must be a string")
				}
				return NewString(strings.ToUpper(str.Val))
			},
		},
		"lower": {
			Name: "lower",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("lower() takes exactly 1 argument")
				}
				str, ok := args[0].(*StringValue)
				if !ok {
					return NewError("lower() argument must be a string")
				}
				return NewString(strings.ToLower(str.Val))
			},
		},
		"trim": {
			Name: "trim",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("trim() takes exactly 1 argument")
				}
				str, ok := args[0].(*StringValue)
				if !ok {
					return NewError("trim() argument must be a string")
				}
				return NewString(strings.TrimSpace(str.Val))
			},
		},
		"split": {
			Name: "split",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("split() takes exactly 2 arguments")
				}
				str, ok := args[0].(*StringValue)
				if !ok {
					return NewError("split() first argument must be a string")
				}
				delim, ok := args[1].(*StringValue)
				if !ok {
					return NewError("split() second argument must be a string")
				}
				parts := strings.Split(str.Val, delim.Val)
				elements := make([]Value, len(parts))
				for i, p := range parts {
					elements[i] = NewString(p)
				}
				return &ListValue{Elements: elements}
			},
		},
		"join": {
			Name: "join",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("join() takes exactly 2 arguments")
				}
				lst, ok := args[0].(*ListValue)
				if !ok {
					return NewError("join() first argument must be a list")
				}
				sep, ok := args[1].(*StringValue)
				if !ok {
					return NewError("join() second argument must be a string")
				}
				strs := make([]string, len(lst.Elements))
				for i, elem := range lst.Elements {
					strs[i] = elem.String()
				}
				return NewString(strings.Join(strs, sep.Val))
			},
		},
		"substring": {
			Name: "substring",
			Fn: func(args ...Value) Value {
				if len(args) != 3 {
					return NewError("substring() takes exactly 3 arguments")
				}
				str, ok := args[0].(*StringValue)
				if !ok {
					return NewError("substring() first argument must be a string")
				}
				start, ok := args[1].(*IntegerValue)
				if !ok {
					return NewError("substring() second argument must be an integer")
				}
				end, ok := args[2].(*IntegerValue)
				if !ok {
					return NewError("substring() third argument must be an integer")
				}
				s := str.Val
				startIdx := int(start.Val)
				endIdx := int(end.Val)
				if startIdx < 0 {
					startIdx = 0
				}
				if endIdx > len(s) {
					endIdx = len(s)
				}
				if startIdx > endIdx {
					return NewString("")
				}
				return NewString(s[startIdx:endIdx])
			},
		},
		"replace": {
			Name: "replace",
			Fn: func(args ...Value) Value {
				if len(args) != 3 {
					return NewError("replace() takes exactly 3 arguments")
				}
				str, ok := args[0].(*StringValue)
				if !ok {
					return NewError("replace() first argument must be a string")
				}
				old, ok := args[1].(*StringValue)
				if !ok {
					return NewError("replace() second argument must be a string")
				}
				new, ok := args[2].(*StringValue)
				if !ok {
					return NewError("replace() third argument must be a string")
				}
				return NewString(strings.ReplaceAll(str.Val, old.Val, new.Val))
			},
		},
		"contains": {
			Name: "contains",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("contains() takes exactly 2 arguments")
				}
				switch container := args[0].(type) {
				case *StringValue:
					search, ok := args[1].(*StringValue)
					if !ok {
						return NewError("contains() with string requires string search value")
					}
					return NewBoolean(strings.Contains(container.Val, search.Val))
				case *ListValue:
					for _, elem := range container.Elements {
						if valuesEqual(elem, args[1]) {
							return NewBoolean(true)
						}
					}
					return NewBoolean(false)
				default:
					return NewError("contains() first argument must be string or list")
				}
			},
		},
		"starts_with": {
			Name: "starts_with",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("starts_with() takes exactly 2 arguments")
				}
				str, ok := args[0].(*StringValue)
				if !ok {
					return NewError("starts_with() first argument must be a string")
				}
				prefix, ok := args[1].(*StringValue)
				if !ok {
					return NewError("starts_with() second argument must be a string")
				}
				return NewBoolean(strings.HasPrefix(str.Val, prefix.Val))
			},
		},
		"ends_with": {
			Name: "ends_with",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("ends_with() takes exactly 2 arguments")
				}
				str, ok := args[0].(*StringValue)
				if !ok {
					return NewError("ends_with() first argument must be a string")
				}
				suffix, ok := args[1].(*StringValue)
				if !ok {
					return NewError("ends_with() second argument must be a string")
				}
				return NewBoolean(strings.HasSuffix(str.Val, suffix.Val))
			},
		},

		// ============================================================
		// Math - Basic
		// ============================================================
		"abs": {
			Name: "abs",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("abs() takes exactly 1 argument")
				}
				switch arg := args[0].(type) {
				case *IntegerValue:
					if arg.Val < 0 {
						return NewInteger(-arg.Val)
					}
					return arg
				case *FloatValue:
					return NewFloat(math.Abs(arg.Val))
				default:
					return NewError("abs() argument must be a number")
				}
			},
		},
		"sqrt": {
			Name: "sqrt",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("sqrt() takes exactly 1 argument")
				}
				val := toFloat64(args[0])
				if val == nil {
					return NewError("sqrt() argument must be a number")
				}
				if *val < 0 {
					return NewError("sqrt() argument must be non-negative")
				}
				return NewFloat(math.Sqrt(*val))
			},
		},
		"sqr": {
			Name: "sqr",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("sqr() takes exactly 1 argument")
				}
				switch arg := args[0].(type) {
				case *IntegerValue:
					return NewInteger(arg.Val * arg.Val)
				case *FloatValue:
					return NewFloat(arg.Val * arg.Val)
				default:
					return NewError("sqr() argument must be a number")
				}
			},
		},
		"pow": {
			Name: "pow",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("pow() takes exactly 2 arguments")
				}
				base := toFloat64(args[0])
				exp := toFloat64(args[1])
				if base == nil || exp == nil {
					return NewError("pow() arguments must be numbers")
				}
				return NewFloat(math.Pow(*base, *exp))
			},
		},
		"round": {
			Name: "round",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("round() takes exactly 1 argument")
				}
				val := toFloat64(args[0])
				if val == nil {
					return NewError("round() argument must be a number")
				}
				return NewInteger(int64(math.Round(*val)))
			},
		},
		"floor": {
			Name: "floor",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("floor() takes exactly 1 argument")
				}
				val := toFloat64(args[0])
				if val == nil {
					return NewError("floor() argument must be a number")
				}
				return NewInteger(int64(math.Floor(*val)))
			},
		},
		"ceil": {
			Name: "ceil",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("ceil() takes exactly 1 argument")
				}
				val := toFloat64(args[0])
				if val == nil {
					return NewError("ceil() argument must be a number")
				}
				return NewInteger(int64(math.Ceil(*val)))
			},
		},
		"min": {
			Name: "min",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("min() takes exactly 2 arguments")
				}
				a := toFloat64(args[0])
				b := toFloat64(args[1])
				if a == nil || b == nil {
					return NewError("min() arguments must be numbers")
				}
				if *a <= *b {
					return args[0]
				}
				return args[1]
			},
		},
		"max": {
			Name: "max",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("max() takes exactly 2 arguments")
				}
				a := toFloat64(args[0])
				b := toFloat64(args[1])
				if a == nil || b == nil {
					return NewError("max() arguments must be numbers")
				}
				if *a >= *b {
					return args[0]
				}
				return args[1]
			},
		},
		"mod": {
			Name: "mod",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("mod() takes exactly 2 arguments")
				}
				switch a := args[0].(type) {
				case *IntegerValue:
					b, ok := args[1].(*IntegerValue)
					if !ok {
						return NewError("mod() arguments must be integers")
					}
					if b.Val == 0 {
						return NewError("mod() division by zero")
					}
					return NewInteger(a.Val % b.Val)
				default:
					return NewError("mod() arguments must be integers")
				}
			},
		},

		// ============================================================
		// Math - Trigonometry
		// ============================================================
		"sin": {
			Name: "sin",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("sin() takes exactly 1 argument")
				}
				val := toFloat64(args[0])
				if val == nil {
					return NewError("sin() argument must be a number")
				}
				return NewFloat(math.Sin(*val))
			},
		},
		"cos": {
			Name: "cos",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("cos() takes exactly 1 argument")
				}
				val := toFloat64(args[0])
				if val == nil {
					return NewError("cos() argument must be a number")
				}
				return NewFloat(math.Cos(*val))
			},
		},
		"tan": {
			Name: "tan",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("tan() takes exactly 1 argument")
				}
				val := toFloat64(args[0])
				if val == nil {
					return NewError("tan() argument must be a number")
				}
				return NewFloat(math.Tan(*val))
			},
		},
		"asin": {
			Name: "asin",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("asin() takes exactly 1 argument")
				}
				val := toFloat64(args[0])
				if val == nil {
					return NewError("asin() argument must be a number")
				}
				if *val < -1 || *val > 1 {
					return NewError("asin() argument must be between -1 and 1")
				}
				return NewFloat(math.Asin(*val))
			},
		},
		"acos": {
			Name: "acos",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("acos() takes exactly 1 argument")
				}
				val := toFloat64(args[0])
				if val == nil {
					return NewError("acos() argument must be a number")
				}
				if *val < -1 || *val > 1 {
					return NewError("acos() argument must be between -1 and 1")
				}
				return NewFloat(math.Acos(*val))
			},
		},
		"atan": {
			Name: "atan",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("atan() takes exactly 1 argument")
				}
				val := toFloat64(args[0])
				if val == nil {
					return NewError("atan() argument must be a number")
				}
				return NewFloat(math.Atan(*val))
			},
		},
		"atan2": {
			Name: "atan2",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("atan2() takes exactly 2 arguments")
				}
				y := toFloat64(args[0])
				x := toFloat64(args[1])
				if y == nil || x == nil {
					return NewError("atan2() arguments must be numbers")
				}
				return NewFloat(math.Atan2(*y, *x))
			},
		},

		// ============================================================
		// Math - Logarithmic
		// ============================================================
		"log": {
			Name: "log",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("log() takes exactly 1 argument")
				}
				val := toFloat64(args[0])
				if val == nil {
					return NewError("log() argument must be a number")
				}
				if *val <= 0 {
					return NewError("log() argument must be positive")
				}
				return NewFloat(math.Log(*val))
			},
		},
		"log10": {
			Name: "log10",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("log10() takes exactly 1 argument")
				}
				val := toFloat64(args[0])
				if val == nil {
					return NewError("log10() argument must be a number")
				}
				if *val <= 0 {
					return NewError("log10() argument must be positive")
				}
				return NewFloat(math.Log10(*val))
			},
		},
		"log2": {
			Name: "log2",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("log2() takes exactly 1 argument")
				}
				val := toFloat64(args[0])
				if val == nil {
					return NewError("log2() argument must be a number")
				}
				if *val <= 0 {
					return NewError("log2() argument must be positive")
				}
				return NewFloat(math.Log2(*val))
			},
		},
		"exp": {
			Name: "exp",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("exp() takes exactly 1 argument")
				}
				val := toFloat64(args[0])
				if val == nil {
					return NewError("exp() argument must be a number")
				}
				return NewFloat(math.Exp(*val))
			},
		},

		// ============================================================
		// Math - Random
		// ============================================================
		"random": {
			Name: "random",
			Fn: func(args ...Value) Value {
				if len(args) != 0 {
					return NewError("random() takes no arguments")
				}
				return NewFloat(rand.Float64())
			},
		},
		"random_int": {
			Name: "random_int",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("random_int() takes exactly 2 arguments")
				}
				min, ok := args[0].(*IntegerValue)
				if !ok {
					return NewError("random_int() first argument must be an integer")
				}
				max, ok := args[1].(*IntegerValue)
				if !ok {
					return NewError("random_int() second argument must be an integer")
				}
				if min.Val > max.Val {
					return NewError("random_int() min must be <= max")
				}
				return NewInteger(min.Val + rand.Int63n(max.Val-min.Val+1))
			},
		},
		"random_choice": {
			Name: "random_choice",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("random_choice() takes exactly 1 argument")
				}
				lst, ok := args[0].(*ListValue)
				if !ok {
					return NewError("random_choice() argument must be a list")
				}
				if len(lst.Elements) == 0 {
					return NewError("random_choice() list cannot be empty")
				}
				return lst.Elements[rand.Intn(len(lst.Elements))]
			},
		},

		// ============================================================
		// List Operations
		// ============================================================
		"append": {
			Name: "append",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("append() takes exactly 2 arguments")
				}
				lst, ok := args[0].(*ListValue)
				if !ok {
					return NewError("append() first argument must be a list")
				}
				lst.Elements = append(lst.Elements, args[1])
				return NULL
			},
		},
		"insert": {
			Name: "insert",
			Fn: func(args ...Value) Value {
				if len(args) != 3 {
					return NewError("insert() takes exactly 3 arguments")
				}
				lst, ok := args[0].(*ListValue)
				if !ok {
					return NewError("insert() first argument must be a list")
				}
				idx, ok := args[1].(*IntegerValue)
				if !ok {
					return NewError("insert() second argument must be an integer")
				}
				index := int(idx.Val)
				if index < 0 || index > len(lst.Elements) {
					return NewError("insert() index out of range")
				}
				lst.Elements = append(lst.Elements[:index], append([]Value{args[2]}, lst.Elements[index:]...)...)
				return NULL
			},
		},
		"remove": {
			Name: "remove",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("remove() takes exactly 2 arguments")
				}
				switch container := args[0].(type) {
				case *ListValue:
					// Remove first occurrence of item from list
					for i, elem := range container.Elements {
						if valuesEqual(elem, args[1]) {
							container.Elements = append(container.Elements[:i], container.Elements[i+1:]...)
							return NULL
						}
					}
					return NewError("remove() item not found in list")
				case *TableValue:
					// Remove key from table
					key, ok := args[1].(*StringValue)
					if !ok {
						return NewError("remove() table key must be a string")
					}
					if _, exists := container.Pairs[key.Val]; !exists {
						return NewError("remove() key not found in table")
					}
					delete(container.Pairs, key.Val)
					return NULL
				default:
					return NewError("remove() first argument must be list or table")
				}
			},
		},
		"pop": {
			Name: "pop",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("pop() takes exactly 2 arguments")
				}
				lst, ok := args[0].(*ListValue)
				if !ok {
					return NewError("pop() first argument must be a list")
				}
				idx, ok := args[1].(*IntegerValue)
				if !ok {
					return NewError("pop() second argument must be an integer")
				}
				index := int(idx.Val)
				if index < 0 || index >= len(lst.Elements) {
					return NewError("pop() index out of range")
				}
				item := lst.Elements[index]
				lst.Elements = append(lst.Elements[:index], lst.Elements[index+1:]...)
				return item
			},
		},
		"sort": {
			Name: "sort",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("sort() takes exactly 1 argument")
				}
				lst, ok := args[0].(*ListValue)
				if !ok {
					return NewError("sort() argument must be a list")
				}
				// Sort in place - supports homogeneous lists of integers, floats, or strings
				sort.Slice(lst.Elements, func(i, j int) bool {
					return compareValues(lst.Elements[i], lst.Elements[j]) < 0
				})
				return NULL
			},
		},
		"reverse": {
			Name: "reverse",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("reverse() takes exactly 1 argument")
				}
				lst, ok := args[0].(*ListValue)
				if !ok {
					return NewError("reverse() argument must be a list")
				}
				// Reverse in place
				for i, j := 0, len(lst.Elements)-1; i < j; i, j = i+1, j-1 {
					lst.Elements[i], lst.Elements[j] = lst.Elements[j], lst.Elements[i]
				}
				return NULL
			},
		},

		// ============================================================
		// Table Operations
		// ============================================================
		"keys": {
			Name: "keys",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("keys() takes exactly 1 argument")
				}
				tbl, ok := args[0].(*TableValue)
				if !ok {
					return NewError("keys() argument must be a table")
				}
				keys := make([]Value, 0, len(tbl.Pairs))
				for k := range tbl.Pairs {
					keys = append(keys, NewString(k))
				}
				return &ListValue{Elements: keys}
			},
		},
		"values": {
			Name: "values",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("values() takes exactly 1 argument")
				}
				tbl, ok := args[0].(*TableValue)
				if !ok {
					return NewError("values() argument must be a table")
				}
				values := make([]Value, 0, len(tbl.Pairs))
				for _, v := range tbl.Pairs {
					values = append(values, v)
				}
				return &ListValue{Elements: values}
			},
		},
		"has_key": {
			Name: "has_key",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("has_key() takes exactly 2 arguments")
				}
				tbl, ok := args[0].(*TableValue)
				if !ok {
					return NewError("has_key() first argument must be a table")
				}
				key, ok := args[1].(*StringValue)
				if !ok {
					return NewError("has_key() second argument must be a string")
				}
				_, exists := tbl.Pairs[key.Val]
				return NewBoolean(exists)
			},
		},
	}
}

// Helper function to convert Value to float64
func toFloat64(v Value) *float64 {
	switch val := v.(type) {
	case *IntegerValue:
		f := float64(val.Val)
		return &f
	case *FloatValue:
		return &val.Val
	default:
		return nil
	}
}

// Helper function to compare two values
func valuesEqual(a, b Value) bool {
	switch av := a.(type) {
	case *IntegerValue:
		if bv, ok := b.(*IntegerValue); ok {
			return av.Val == bv.Val
		}
		if bv, ok := b.(*FloatValue); ok {
			return float64(av.Val) == bv.Val
		}
	case *FloatValue:
		if bv, ok := b.(*FloatValue); ok {
			return av.Val == bv.Val
		}
		if bv, ok := b.(*IntegerValue); ok {
			return av.Val == float64(bv.Val)
		}
	case *StringValue:
		if bv, ok := b.(*StringValue); ok {
			return av.Val == bv.Val
		}
	case *BooleanValue:
		if bv, ok := b.(*BooleanValue); ok {
			return av.Val == bv.Val
		}
	case *NullValue:
		_, ok := b.(*NullValue)
		return ok
	}
	return false
}

// Helper function to compare values for sorting
func compareValues(a, b Value) int {
	switch av := a.(type) {
	case *IntegerValue:
		if bv, ok := b.(*IntegerValue); ok {
			if av.Val < bv.Val {
				return -1
			} else if av.Val > bv.Val {
				return 1
			}
			return 0
		}
		if bv, ok := b.(*FloatValue); ok {
			af := float64(av.Val)
			if af < bv.Val {
				return -1
			} else if af > bv.Val {
				return 1
			}
			return 0
		}
	case *FloatValue:
		if bv, ok := b.(*FloatValue); ok {
			if av.Val < bv.Val {
				return -1
			} else if av.Val > bv.Val {
				return 1
			}
			return 0
		}
		if bv, ok := b.(*IntegerValue); ok {
			bf := float64(bv.Val)
			if av.Val < bf {
				return -1
			} else if av.Val > bf {
				return 1
			}
			return 0
		}
	case *StringValue:
		if bv, ok := b.(*StringValue); ok {
			if av.Val < bv.Val {
				return -1
			} else if av.Val > bv.Val {
				return 1
			}
			return 0
		}
	}
	// Fallback: compare string representations
	as, bs := a.String(), b.String()
	if as < bs {
		return -1
	} else if as > bs {
		return 1
	}
	return 0
}
