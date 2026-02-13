package runtime

import (
	"bufio"
	"fmt"
	"io"
	"io/ioutil"
	"math"
	"math/rand"
	"net"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
	"time"

	"go.bug.st/serial"
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
		"clear": {
			Name: "clear",
			Fn: func(args ...Value) Value {
				// ANSI escape code to clear screen and move cursor home
				// \033[2J clears the entire screen
				// \033[H moves cursor to top-left
				fmt.Print("\033[2J\033[H")
				return NULL
			},
		},

		// ============================================================
		// Enhanced Text Output (Phase 1 TUI)
		// ============================================================
		"text_at": {
			Name: "text_at",
			Fn: func(args ...Value) Value {
				if len(args) < 3 {
					return NewError("text_at() takes 3 arguments: x, y, text")
				}

				// Get x coordinate
				xVal, ok := args[0].(*IntegerValue)
				if !ok {
					return NewError("text_at() x must be an integer")
				}

				// Get y coordinate
				yVal, ok := args[1].(*IntegerValue)
				if !ok {
					return NewError("text_at() y must be an integer")
				}

				// Get text (convert to string if needed)
				text := args[2].String()

				// ANSI escape code to position cursor: \033[y;xH
				// Note: ANSI coordinates are 1-based, so we add 1
				fmt.Printf("\033[%d;%dH%s", yVal.Val, xVal.Val, text)
				return NULL
			},
		},

		"text_color": {
			Name: "text_color",
			Fn: func(args ...Value) Value {
				if len(args) < 1 || len(args) > 2 {
					return NewError("text_color() takes 1 or 2 arguments: foreground [, background]")
				}

				// Color name to ANSI code mapping
				colorMap := map[string]int{
					"black":   0,
					"red":     1,
					"green":   2,
					"yellow":  3,
					"blue":    4,
					"magenta": 5,
					"cyan":    6,
					"white":   7,
					"default": 9,
				}

				// Get foreground color
				fgStr, ok := args[0].(*StringValue)
				if !ok {
					return NewError("text_color() foreground must be a string")
				}
				fgCode, ok := colorMap[strings.ToLower(fgStr.Val)]
				if !ok {
					return NewError("text_color() invalid color: %s (use black, red, green, yellow, blue, magenta, cyan, white, default)", fgStr.Val)
				}

				// Set foreground color (30-37 for normal, 90-97 for bright)
				fmt.Printf("\033[%dm", 30+fgCode)

				// Set background color if provided
				if len(args) == 2 {
					bgStr, ok := args[1].(*StringValue)
					if !ok {
						return NewError("text_color() background must be a string")
					}
					bgCode, ok := colorMap[strings.ToLower(bgStr.Val)]
					if !ok {
						return NewError("text_color() invalid color: %s (use black, red, green, yellow, blue, magenta, cyan, white, default)", bgStr.Val)
					}
					// Set background color (40-47)
					fmt.Printf("\033[%dm", 40+bgCode)
				}

				return NULL
			},
		},

		"draw_line": {
			Name: "draw_line",
			Fn: func(args ...Value) Value {
				if len(args) < 4 {
					return NewError("draw_line() takes 4 or 5 arguments: x, y, length, direction [, char]")
				}

				// Get x coordinate
				xVal, ok := args[0].(*IntegerValue)
				if !ok {
					return NewError("draw_line() x must be an integer")
				}

				// Get y coordinate
				yVal, ok := args[1].(*IntegerValue)
				if !ok {
					return NewError("draw_line() y must be an integer")
				}

				// Get length
				lengthVal, ok := args[2].(*IntegerValue)
				if !ok {
					return NewError("draw_line() length must be an integer")
				}

				// Get direction
				dirStr, ok := args[3].(*StringValue)
				if !ok {
					return NewError("draw_line() direction must be a string")
				}
				direction := strings.ToLower(dirStr.Val)
				if direction != "h" && direction != "v" && direction != "horizontal" && direction != "vertical" {
					return NewError("draw_line() direction must be 'h', 'v', 'horizontal', or 'vertical'")
				}

				// Get character (default to appropriate line character)
				char := "-"
				if direction == "v" || direction == "vertical" {
					char = "|"
				}
				if len(args) >= 5 {
					charStr, ok := args[4].(*StringValue)
					if !ok {
						return NewError("draw_line() char must be a string")
					}
					if len(charStr.Val) > 0 {
						char = string([]rune(charStr.Val)[0]) // Get first character
					}
				}

				// Draw the line
				if direction == "h" || direction == "horizontal" {
					// Horizontal line
					fmt.Printf("\033[%d;%dH", yVal.Val, xVal.Val)
					for i := int64(0); i < lengthVal.Val; i++ {
						fmt.Print(char)
					}
				} else {
					// Vertical line
					for i := int64(0); i < lengthVal.Val; i++ {
						fmt.Printf("\033[%d;%dH%s", yVal.Val+i, xVal.Val, char)
					}
				}

				return NULL
			},
		},

		"draw_box": {
			Name: "draw_box",
			Fn: func(args ...Value) Value {
				if len(args) < 4 {
					return NewError("draw_box() takes 4 or 5 arguments: x, y, width, height [, title]")
				}

				// Get x coordinate
				xVal, ok := args[0].(*IntegerValue)
				if !ok {
					return NewError("draw_box() x must be an integer")
				}

				// Get y coordinate
				yVal, ok := args[1].(*IntegerValue)
				if !ok {
					return NewError("draw_box() y must be an integer")
				}

				// Get width
				widthVal, ok := args[2].(*IntegerValue)
				if !ok {
					return NewError("draw_box() width must be an integer")
				}

				// Get height
				heightVal, ok := args[3].(*IntegerValue)
				if !ok {
					return NewError("draw_box() height must be an integer")
				}

				// Get optional title
				title := ""
				if len(args) >= 5 {
					title = args[4].String()
				}

				x := xVal.Val
				y := yVal.Val
				width := widthVal.Val
				height := heightVal.Val

				// Box drawing characters
				topLeft := "┌"
				topRight := "┐"
				bottomLeft := "└"
				bottomRight := "┘"
				horizontal := "─"
				vertical := "│"

				// Draw top border
				fmt.Printf("\033[%d;%dH%s", y, x, topLeft)
				for i := int64(1); i < width-1; i++ {
					fmt.Print(horizontal)
				}
				fmt.Print(topRight)

				// Draw title if provided
				if title != "" && width > int64(len(title)+4) {
					titleX := x + (width-int64(len(title)))/2
					fmt.Printf("\033[%d;%dH %s ", y, titleX, title)
				}

				// Draw sides
				for i := int64(1); i < height-1; i++ {
					fmt.Printf("\033[%d;%dH%s", y+i, x, vertical)
					fmt.Printf("\033[%d;%dH%s", y+i, x+width-1, vertical)
				}

				// Draw bottom border
				fmt.Printf("\033[%d;%dH%s", y+height-1, x, bottomLeft)
				for i := int64(1); i < width-1; i++ {
					fmt.Print(horizontal)
				}
				fmt.Print(bottomRight)

				return NULL
			},
		},

		// ============================================================
		// Type Checking
		// ============================================================
		"set_float_precision": {
			Name: "set_float_precision",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("set_float_precision() takes exactly 1 argument")
				}
				precision, ok := args[0].(*IntegerValue)
				if !ok {
					return NewError("set_float_precision() argument must be an integer")
				}
				FloatPrecision = int(precision.Val)
				return NULL
			},
		},
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
					s := strings.TrimSpace(arg.Val)
					if strings.HasPrefix(s, "0b") || strings.HasPrefix(s, "0B") {
						i, err := strconv.ParseInt(s[2:], 2, 64)
						if err != nil {
							return NewError("cannot convert '%s' to integer", arg.Val)
						}
						return NewInteger(i)
					}
					if strings.HasPrefix(s, "0x") || strings.HasPrefix(s, "0X") {
						i, err := strconv.ParseInt(s[2:], 16, 64)
						if err != nil {
							return NewError("cannot convert '%s' to integer", arg.Val)
						}
						return NewInteger(i)
					}
					var i int64
					_, err := fmt.Sscanf(s, "%d", &i)
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
				// Auto-detect binary/hex byte sequences when input is a string
				if strVal, ok := args[0].(*StringValue); ok {
					s := strVal.Val
					if decoded, ok := decodeBinaryBytes(s); ok {
						return NewString(decoded)
					}
					if decoded, ok := decodeHexBytes(s); ok {
						return NewString(decoded)
					}
					return NewString(s)
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
		"to_bin": {
			Name: "to_bin",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("to_bin() takes exactly 1 argument")
				}
				switch arg := args[0].(type) {
				case *IntegerValue:
					if arg.Val < 0 {
						return NewString("-" + strconv.FormatInt(-arg.Val, 2))
					}
					return NewString(strconv.FormatInt(arg.Val, 2))
				case *BooleanValue:
					if arg.Val {
						return NewString("1")
					}
					return NewString("0")
				case *StringValue:
					if len(arg.Val) == 0 {
						return NewString("")
					}
					parts := make([]string, len(arg.Val))
					for i, ch := range arg.Val {
						parts[i] = fmt.Sprintf("%08b", ch)
					}
					return NewString(strings.Join(parts, " "))
				default:
					return NewError("to_bin() argument must be an integer, boolean, or string")
				}
			},
		},
		"to_hex": {
			Name: "to_hex",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("to_hex() takes exactly 1 argument")
				}
				switch arg := args[0].(type) {
				case *IntegerValue:
					if arg.Val < 0 {
						return NewString("-" + strings.ToUpper(strconv.FormatInt(-arg.Val, 16)))
					}
					return NewString(strings.ToUpper(strconv.FormatInt(arg.Val, 16)))
				case *BooleanValue:
					if arg.Val {
						return NewString("1")
					}
					return NewString("0")
				case *StringValue:
					if len(arg.Val) == 0 {
						return NewString("")
					}
					parts := make([]string, len(arg.Val))
					for i, ch := range arg.Val {
						parts[i] = fmt.Sprintf("%02X", ch)
					}
					return NewString(strings.Join(parts, " "))
				default:
					return NewError("to_hex() argument must be an integer, boolean, or string")
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
		"chr": {
			Name: "chr",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("chr() takes exactly 1 argument")
				}
				code, ok := args[0].(*IntegerValue)
				if !ok {
					return NewError("chr() argument must be an integer")
				}
				return NewString(string(rune(code.Val)))
			},
		},
		"ord": {
			Name: "ord",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("ord() takes exactly 1 argument")
				}
				str, ok := args[0].(*StringValue)
				if !ok {
					return NewError("ord() argument must be a string")
				}
				if len(str.Val) == 0 {
					return NewError("ord() argument cannot be empty")
				}
				return NewInteger(int64([]rune(str.Val)[0]))
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

		// ============================================================
		// File I/O - Simple Operations
		// ============================================================
		"read_file": {
			Name: "read_file",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("read_file() takes exactly 1 argument")
				}
				path, ok := args[0].(*StringValue)
				if !ok {
					return NewError("read_file() argument must be a string")
				}
				content, err := ioutil.ReadFile(path.Val)
				if err != nil {
					return NewError("read_file() failed: %s", err.Error())
				}
				return NewString(string(content))
			},
		},
		"write_file": {
			Name: "write_file",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("write_file() takes exactly 2 arguments")
				}
				path, ok := args[0].(*StringValue)
				if !ok {
					return NewError("write_file() first argument must be a string")
				}
				content, ok := args[1].(*StringValue)
				if !ok {
					return NewError("write_file() second argument must be a string")
				}
				err := ioutil.WriteFile(path.Val, []byte(content.Val), 0644)
				if err != nil {
					return NewError("write_file() failed: %s", err.Error())
				}
				return NULL
			},
		},
		"append_file": {
			Name: "append_file",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("append_file() takes exactly 2 arguments")
				}
				path, ok := args[0].(*StringValue)
				if !ok {
					return NewError("append_file() first argument must be a string")
				}
				content, ok := args[1].(*StringValue)
				if !ok {
					return NewError("append_file() second argument must be a string")
				}
				f, err := os.OpenFile(path.Val, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
				if err != nil {
					return NewError("append_file() failed: %s", err.Error())
				}
				defer f.Close()
				_, err = f.WriteString(content.Val)
				if err != nil {
					return NewError("append_file() failed: %s", err.Error())
				}
				return NULL
			},
		},
		"read_lines": {
			Name: "read_lines",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("read_lines() takes exactly 1 argument")
				}
				path, ok := args[0].(*StringValue)
				if !ok {
					return NewError("read_lines() argument must be a string")
				}
				content, err := ioutil.ReadFile(path.Val)
				if err != nil {
					return NewError("read_lines() failed: %s", err.Error())
				}
				text := strings.TrimSuffix(string(content), "\n")
				if text == "" {
					return &ListValue{Elements: []Value{}}
				}
				lines := strings.Split(text, "\n")
				elements := make([]Value, len(lines))
				for i, line := range lines {
					elements[i] = NewString(line)
				}
				return &ListValue{Elements: elements}
			},
		},
		"write_lines": {
			Name: "write_lines",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("write_lines() takes exactly 2 arguments")
				}
				path, ok := args[0].(*StringValue)
				if !ok {
					return NewError("write_lines() first argument must be a string")
				}
				lst, ok := args[1].(*ListValue)
				if !ok {
					return NewError("write_lines() second argument must be a list")
				}
				lines := make([]string, len(lst.Elements))
				for i, elem := range lst.Elements {
					lines[i] = elem.String()
				}
				content := strings.Join(lines, "\n") + "\n"
				err := ioutil.WriteFile(path.Val, []byte(content), 0644)
				if err != nil {
					return NewError("write_lines() failed: %s", err.Error())
				}
				return NULL
			},
		},
		"read_binary": {
			Name: "read_binary",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("read_binary() takes exactly 1 argument")
				}
				path, ok := args[0].(*StringValue)
				if !ok {
					return NewError("read_binary() argument must be a string")
				}
				data, err := ioutil.ReadFile(path.Val)
				if err != nil {
					return NewError("read_binary() failed: %s", err.Error())
				}
				return &BytesValue{Data: data}
			},
		},
		"write_binary": {
			Name: "write_binary",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("write_binary() takes exactly 2 arguments")
				}
				path, ok := args[0].(*StringValue)
				if !ok {
					return NewError("write_binary() first argument must be a string")
				}
				bytes, ok := args[1].(*BytesValue)
				if !ok {
					return NewError("write_binary() second argument must be bytes")
				}
				err := ioutil.WriteFile(path.Val, bytes.Data, 0644)
				if err != nil {
					return NewError("write_binary() failed: %s", err.Error())
				}
				return NULL
			},
		},
		"append_binary": {
			Name: "append_binary",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("append_binary() takes exactly 2 arguments")
				}
				path, ok := args[0].(*StringValue)
				if !ok {
					return NewError("append_binary() first argument must be a string")
				}
				bytes, ok := args[1].(*BytesValue)
				if !ok {
					return NewError("append_binary() second argument must be bytes")
				}
				f, err := os.OpenFile(path.Val, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
				if err != nil {
					return NewError("append_binary() failed: %s", err.Error())
				}
				defer f.Close()
				_, err = f.Write(bytes.Data)
				if err != nil {
					return NewError("append_binary() failed: %s", err.Error())
				}
				return NULL
			},
		},

		// ============================================================
		// File I/O - Handle-based Operations
		// ============================================================
		"open": {
			Name: "open",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("open() takes exactly 2 arguments")
				}
				path, ok := args[0].(*StringValue)
				if !ok {
					return NewError("open() first argument must be a string")
				}
				mode, ok := args[1].(*StringValue)
				if !ok {
					return NewError("open() second argument must be a string")
				}
				var file *os.File
				var err error
				isBinary := false
				switch mode.Val {
				case "r":
					file, err = os.Open(path.Val)
				case "w":
					file, err = os.Create(path.Val)
				case "a":
					file, err = os.OpenFile(path.Val, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
				case "rb":
					file, err = os.Open(path.Val)
					isBinary = true
				case "wb":
					file, err = os.Create(path.Val)
					isBinary = true
				case "ab":
					file, err = os.OpenFile(path.Val, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
					isBinary = true
				default:
					return NewError("open() invalid mode '%s' (use r, w, a, rb, wb, ab)", mode.Val)
				}
				if err != nil {
					return NewError("open() failed: %s", err.Error())
				}
				return &FileHandleValue{Path: path.Val, Mode: mode.Val, Handle: file, IsBinary: isBinary}
			},
		},
		"close": {
			Name: "close",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("close() takes exactly 1 argument")
				}
				handle, ok := args[0].(*FileHandleValue)
				if !ok {
					return NewError("close() argument must be a file handle")
				}
				if handle.Handle == nil {
					return NewError("close() file already closed")
				}
				file := handle.Handle.(*os.File)
				err := file.Close()
				handle.Handle = nil
				if err != nil {
					return NewError("close() failed: %s", err.Error())
				}
				return NULL
			},
		},
		"read": {
			Name: "read",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("read() takes exactly 1 argument")
				}
				handle, ok := args[0].(*FileHandleValue)
				if !ok {
					return NewError("read() argument must be a file handle")
				}
				if handle.Handle == nil {
					return NewError("read() file is closed")
				}
				file := handle.Handle.(*os.File)
				content, err := io.ReadAll(file)
				if err != nil {
					return NewError("read() failed: %s", err.Error())
				}
				if handle.IsBinary {
					return &BytesValue{Data: content}
				}
				return NewString(string(content))
			},
		},
		"read_line": {
			Name: "read_line",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("read_line() takes exactly 1 argument")
				}
				handle, ok := args[0].(*FileHandleValue)
				if !ok {
					return NewError("read_line() argument must be a file handle")
				}
				if handle.Handle == nil {
					return NewError("read_line() file is closed")
				}
				file := handle.Handle.(*os.File)
				reader := bufio.NewReader(file)
				line, err := reader.ReadString('\n')
				if err != nil {
					if err == io.EOF {
						if line == "" {
							return NULL
						}
						return NewString(line)
					}
					return NewError("read_line() failed: %s", err.Error())
				}
				return NewString(strings.TrimSuffix(line, "\n"))
			},
		},
		"read_bytes": {
			Name: "read_bytes",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("read_bytes() takes exactly 2 arguments")
				}
				handle, ok := args[0].(*FileHandleValue)
				if !ok {
					return NewError("read_bytes() first argument must be a file handle")
				}
				count, ok := args[1].(*IntegerValue)
				if !ok {
					return NewError("read_bytes() second argument must be an integer")
				}
				if handle.Handle == nil {
					return NewError("read_bytes() file is closed")
				}
				file := handle.Handle.(*os.File)
				buf := make([]byte, count.Val)
				n, err := file.Read(buf)
				if err != nil && err != io.EOF {
					return NewError("read_bytes() failed: %s", err.Error())
				}
				return &BytesValue{Data: buf[:n]}
			},
		},
		"write": {
			Name: "write",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("write() takes exactly 2 arguments")
				}
				handle, ok := args[0].(*FileHandleValue)
				if !ok {
					return NewError("write() first argument must be a file handle")
				}
				if handle.Handle == nil {
					return NewError("write() file is closed")
				}
				file := handle.Handle.(*os.File)
				var err error
				switch content := args[1].(type) {
				case *StringValue:
					_, err = file.WriteString(content.Val)
				case *BytesValue:
					_, err = file.Write(content.Data)
				default:
					return NewError("write() second argument must be string or bytes")
				}
				if err != nil {
					return NewError("write() failed: %s", err.Error())
				}
				return NULL
			},
		},
		"write_line": {
			Name: "write_line",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("write_line() takes exactly 2 arguments")
				}
				handle, ok := args[0].(*FileHandleValue)
				if !ok {
					return NewError("write_line() first argument must be a file handle")
				}
				content, ok := args[1].(*StringValue)
				if !ok {
					return NewError("write_line() second argument must be a string")
				}
				if handle.Handle == nil {
					return NewError("write_line() file is closed")
				}
				file := handle.Handle.(*os.File)
				_, err := file.WriteString(content.Val + "\n")
				if err != nil {
					return NewError("write_line() failed: %s", err.Error())
				}
				return NULL
			},
		},

		// ============================================================
		// File System Operations
		// ============================================================
		"file_exists": {
			Name: "file_exists",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("file_exists() takes exactly 1 argument")
				}
				path, ok := args[0].(*StringValue)
				if !ok {
					return NewError("file_exists() argument must be a string")
				}
				info, err := os.Stat(path.Val)
				if os.IsNotExist(err) {
					return NewBoolean(false)
				}
				if err != nil {
					return NewBoolean(false)
				}
				return NewBoolean(!info.IsDir())
			},
		},
		"delete_file": {
			Name: "delete_file",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("delete_file() takes exactly 1 argument")
				}
				path, ok := args[0].(*StringValue)
				if !ok {
					return NewError("delete_file() argument must be a string")
				}
				err := os.Remove(path.Val)
				if err != nil {
					return NewError("delete_file() failed: %s", err.Error())
				}
				return NULL
			},
		},
		"rename_file": {
			Name: "rename_file",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("rename_file() takes exactly 2 arguments")
				}
				oldPath, ok := args[0].(*StringValue)
				if !ok {
					return NewError("rename_file() first argument must be a string")
				}
				newPath, ok := args[1].(*StringValue)
				if !ok {
					return NewError("rename_file() second argument must be a string")
				}
				err := os.Rename(oldPath.Val, newPath.Val)
				if err != nil {
					return NewError("rename_file() failed: %s", err.Error())
				}
				return NULL
			},
		},
		"copy_file": {
			Name: "copy_file",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("copy_file() takes exactly 2 arguments")
				}
				src, ok := args[0].(*StringValue)
				if !ok {
					return NewError("copy_file() first argument must be a string")
				}
				dst, ok := args[1].(*StringValue)
				if !ok {
					return NewError("copy_file() second argument must be a string")
				}
				data, err := ioutil.ReadFile(src.Val)
				if err != nil {
					return NewError("copy_file() failed reading source: %s", err.Error())
				}
				err = ioutil.WriteFile(dst.Val, data, 0644)
				if err != nil {
					return NewError("copy_file() failed writing destination: %s", err.Error())
				}
				return NULL
			},
		},
		"file_size": {
			Name: "file_size",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("file_size() takes exactly 1 argument")
				}
				path, ok := args[0].(*StringValue)
				if !ok {
					return NewError("file_size() argument must be a string")
				}
				info, err := os.Stat(path.Val)
				if err != nil {
					return NewError("file_size() failed: %s", err.Error())
				}
				return NewInteger(info.Size())
			},
		},
		"dir_exists": {
			Name: "dir_exists",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("dir_exists() takes exactly 1 argument")
				}
				path, ok := args[0].(*StringValue)
				if !ok {
					return NewError("dir_exists() argument must be a string")
				}
				info, err := os.Stat(path.Val)
				if os.IsNotExist(err) {
					return NewBoolean(false)
				}
				if err != nil {
					return NewBoolean(false)
				}
				return NewBoolean(info.IsDir())
			},
		},
		"create_dir": {
			Name: "create_dir",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("create_dir() takes exactly 1 argument")
				}
				path, ok := args[0].(*StringValue)
				if !ok {
					return NewError("create_dir() argument must be a string")
				}
				err := os.Mkdir(path.Val, 0755)
				if err != nil {
					return NewError("create_dir() failed: %s", err.Error())
				}
				return NULL
			},
		},
		"delete_dir": {
			Name: "delete_dir",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("delete_dir() takes exactly 1 argument")
				}
				path, ok := args[0].(*StringValue)
				if !ok {
					return NewError("delete_dir() argument must be a string")
				}
				err := os.Remove(path.Val)
				if err != nil {
					return NewError("delete_dir() failed: %s", err.Error())
				}
				return NULL
			},
		},
		"list_dir": {
			Name: "list_dir",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("list_dir() takes exactly 1 argument")
				}
				path, ok := args[0].(*StringValue)
				if !ok {
					return NewError("list_dir() argument must be a string")
				}
				entries, err := ioutil.ReadDir(path.Val)
				if err != nil {
					return NewError("list_dir() failed: %s", err.Error())
				}
				elements := make([]Value, len(entries))
				for i, entry := range entries {
					elements[i] = NewString(entry.Name())
				}
				return &ListValue{Elements: elements}
			},
		},

		// ============================================================
		// Path Operations
		// ============================================================
		"join_path": {
			Name: "join_path",
			Fn: func(args ...Value) Value {
				if len(args) < 1 {
					return NewError("join_path() requires at least 1 argument")
				}
				parts := make([]string, len(args))
				for i, arg := range args {
					str, ok := arg.(*StringValue)
					if !ok {
						return NewError("join_path() all arguments must be strings")
					}
					parts[i] = str.Val
				}
				return NewString(filepath.Join(parts...))
			},
		},
		"split_path": {
			Name: "split_path",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("split_path() takes exactly 1 argument")
				}
				path, ok := args[0].(*StringValue)
				if !ok {
					return NewError("split_path() argument must be a string")
				}
				dir, file := filepath.Split(path.Val)
				// Remove trailing separator from dir
				dir = strings.TrimSuffix(dir, string(filepath.Separator))
				return &ListValue{Elements: []Value{NewString(dir), NewString(file)}}
			},
		},
		"get_extension": {
			Name: "get_extension",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("get_extension() takes exactly 1 argument")
				}
				path, ok := args[0].(*StringValue)
				if !ok {
					return NewError("get_extension() argument must be a string")
				}
				return NewString(filepath.Ext(path.Val))
			},
		},
		"absolute_path": {
			Name: "absolute_path",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("absolute_path() takes exactly 1 argument")
				}
				path, ok := args[0].(*StringValue)
				if !ok {
					return NewError("absolute_path() argument must be a string")
				}
				abs, err := filepath.Abs(path.Val)
				if err != nil {
					return NewError("absolute_path() failed: %s", err.Error())
				}
				return NewString(abs)
			},
		},

		// ============================================================
		// Events & Timers
		// ============================================================
		"sleep": {
			Name: "sleep",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("sleep() takes exactly 1 argument")
				}
				ms, ok := args[0].(*IntegerValue)
				if !ok {
					return NewError("sleep() argument must be an integer (milliseconds)")
				}
				time.Sleep(time.Duration(ms.Val) * time.Millisecond)
				return NULL
			},
		},
		// ============================================================
		// Time and Date
		// ============================================================
		"time": {
			Name: "time",
			Fn: func(args ...Value) Value {
				if len(args) != 0 {
					return NewError("time() takes no arguments")
				}
				return NewInteger(time.Now().UnixMilli())
			},
		},
		"date": {
			Name: "date",
			Fn: func(args ...Value) Value {
				if len(args) != 0 {
					return NewError("date() takes no arguments")
				}
				now := time.Now()
				pairs := make(map[string]Value)
				pairs["year"] = NewInteger(int64(now.Year()))
				pairs["month"] = NewInteger(int64(now.Month()))
				pairs["day"] = NewInteger(int64(now.Day()))
				pairs["hour"] = NewInteger(int64(now.Hour()))
				pairs["minute"] = NewInteger(int64(now.Minute()))
				pairs["second"] = NewInteger(int64(now.Second()))
				return &TableValue{Pairs: pairs}
			},
		},

		"create_timer": {
			Name: "create_timer",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("create_timer() takes exactly 2 arguments")
				}
				intervalMs, ok := args[0].(*IntegerValue)
				if !ok {
					return NewError("create_timer() first argument must be an integer (milliseconds)")
				}
				callback, ok := args[1].(*TaskValue)
				if !ok {
					return NewError("create_timer() second argument must be a task")
				}
				return GetEventLoop().CreateTimer(intervalMs.Val, callback)
			},
		},
		"create_timeout": {
			Name: "create_timeout",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("create_timeout() takes exactly 2 arguments")
				}
				delayMs, ok := args[0].(*IntegerValue)
				if !ok {
					return NewError("create_timeout() first argument must be an integer (milliseconds)")
				}
				callback, ok := args[1].(*TaskValue)
				if !ok {
					return NewError("create_timeout() second argument must be a task")
				}
				return GetEventLoop().CreateTimeout(delayMs.Val, callback)
			},
		},
		"start_timer": {
			Name: "start_timer",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("start_timer() takes exactly 1 argument")
				}
				timer, ok := args[0].(*TimerValue)
				if !ok {
					return NewError("start_timer() argument must be a timer")
				}
				GetEventLoop().StartTimer(timer)
				return NULL
			},
		},
		"stop_timer": {
			Name: "stop_timer",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("stop_timer() takes exactly 1 argument")
				}
				timer, ok := args[0].(*TimerValue)
				if !ok {
					return NewError("stop_timer() argument must be a timer")
				}
				GetEventLoop().StopTimer(timer)
				return NULL
			},
		},
		"cancel_timer": {
			Name: "cancel_timer",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("cancel_timer() takes exactly 1 argument")
				}
				timer, ok := args[0].(*TimerValue)
				if !ok {
					return NewError("cancel_timer() argument must be a timer")
				}
				GetEventLoop().CancelTimer(timer)
				return NULL
			},
		},
		"wait_for_events": {
			Name: "wait_for_events",
			Fn: func(args ...Value) Value {
				if len(args) != 0 {
					return NewError("wait_for_events() takes no arguments")
				}
				GetEventLoop().WaitForEvents()
				return NULL
			},
		},
		"run_events": {
			Name: "run_events",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("run_events() takes exactly 1 argument")
				}
				durationMs, ok := args[0].(*IntegerValue)
				if !ok {
					return NewError("run_events() argument must be an integer (milliseconds)")
				}
				GetEventLoop().RunEvents(durationMs.Val)
				return NULL
			},
		},
		"stop_events": {
			Name: "stop_events",
			Fn: func(args ...Value) Value {
				if len(args) != 0 {
					return NewError("stop_events() takes no arguments")
				}
				GetEventLoop().StopEvents()
				return NULL
			},
		},

		// ============================================================
		// Serial Port I/O
		// ============================================================
		"serial_ports": {
			Name: "serial_ports",
			Fn: func(args ...Value) Value {
				if len(args) != 0 {
					return NewError("serial_ports() takes no arguments")
				}
				ports, err := serial.GetPortsList()
				if err != nil {
					return NewError("serial_ports() failed: %s", err.Error())
				}
				elements := make([]Value, len(ports))
				for i, p := range ports {
					elements[i] = NewString(p)
				}
				return NewList(elements)
			},
		},
		"serial_open": {
			Name: "serial_open",
			Fn: func(args ...Value) Value {
				if len(args) < 2 || len(args) > 3 {
					return NewError("serial_open() takes 2 or 3 arguments (port, baud [, config])")
				}
				portName, ok := args[0].(*StringValue)
				if !ok {
					return NewError("serial_open() first argument must be a string (port name)")
				}
				baudArg, ok := args[1].(*IntegerValue)
				if !ok {
					return NewError("serial_open() second argument must be an integer (baud rate)")
				}
				configStr := "8N1"
				if len(args) == 3 {
					cfgVal, ok := args[2].(*StringValue)
					if !ok {
						return NewError("serial_open() third argument must be a string (config, e.g. \"8N1\")")
					}
					configStr = cfgVal.Val
				}
				// Parse config string (e.g. "8N1")
				if len(configStr) != 3 {
					return NewError("serial_open() config must be 3 characters: data_bits + parity + stop_bits (e.g. \"8N1\")")
				}
				var dataBits int
				switch configStr[0] {
				case '5':
					dataBits = 5
				case '6':
					dataBits = 6
				case '7':
					dataBits = 7
				case '8':
					dataBits = 8
				default:
					return NewError("serial_open() invalid data bits '%c' (use 5, 6, 7, or 8)", configStr[0])
				}
				var parity serial.Parity
				switch configStr[1] {
				case 'N', 'n':
					parity = serial.NoParity
				case 'E', 'e':
					parity = serial.EvenParity
				case 'O', 'o':
					parity = serial.OddParity
				case 'M', 'm':
					parity = serial.MarkParity
				case 'S', 's':
					parity = serial.SpaceParity
				default:
					return NewError("serial_open() invalid parity '%c' (use N, E, O, M, or S)", configStr[1])
				}
				var stopBits serial.StopBits
				switch configStr[2] {
				case '1':
					stopBits = serial.OneStopBit
				case '2':
					stopBits = serial.TwoStopBits
				default:
					return NewError("serial_open() invalid stop bits '%c' (use 1 or 2)", configStr[2])
				}
				mode := &serial.Mode{
					BaudRate: int(baudArg.Val),
					DataBits: dataBits,
					Parity:   parity,
					StopBits: stopBits,
				}
				port, err := serial.Open(portName.Val, mode)
				if err != nil {
					return NewError("serial_open() failed: %s", err.Error())
				}
				reader := bufio.NewReader(port)
				return &SerialPortValue{
					PortName: portName.Val,
					BaudRate: int(baudArg.Val),
					Config:   configStr,
					Handle:   port,
					Reader:   reader,
					IsOpen:   true,
				}
			},
		},
		"serial_close": {
			Name: "serial_close",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("serial_close() takes exactly 1 argument")
				}
				sp, ok := args[0].(*SerialPortValue)
				if !ok {
					return NewError("serial_close() argument must be a serial port handle")
				}
				if !sp.IsOpen {
					return NewError("serial_close() port already closed")
				}
				port := sp.Handle.(serial.Port)
				err := port.Close()
				sp.IsOpen = false
				sp.Handle = nil
				sp.Reader = nil
				if err != nil {
					return NewError("serial_close() failed: %s", err.Error())
				}
				return NULL
			},
		},
		"serial_write": {
			Name: "serial_write",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("serial_write() takes exactly 2 arguments (port, data)")
				}
				sp, ok := args[0].(*SerialPortValue)
				if !ok {
					return NewError("serial_write() first argument must be a serial port handle")
				}
				if !sp.IsOpen {
					return NewError("serial_write() port is closed")
				}
				port := sp.Handle.(serial.Port)
				var data []byte
				switch v := args[1].(type) {
				case *StringValue:
					data = []byte(v.Val)
				case *BytesValue:
					data = v.Data
				default:
					return NewError("serial_write() second argument must be a string or bytes")
				}
				n, err := port.Write(data)
				if err != nil {
					return NewError("serial_write() failed: %s", err.Error())
				}
				return NewInteger(int64(n))
			},
		},
		"serial_read": {
			Name: "serial_read",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("serial_read() takes exactly 2 arguments (port, count)")
				}
				sp, ok := args[0].(*SerialPortValue)
				if !ok {
					return NewError("serial_read() first argument must be a serial port handle")
				}
				if !sp.IsOpen {
					return NewError("serial_read() port is closed")
				}
				count, ok := args[1].(*IntegerValue)
				if !ok {
					return NewError("serial_read() second argument must be an integer (byte count)")
				}
				if count.Val <= 0 {
					return NewError("serial_read() count must be positive")
				}
				port := sp.Handle.(serial.Port)
				buf := make([]byte, count.Val)
				n, err := port.Read(buf)
				if err != nil {
					return NewError("serial_read() failed: %s", err.Error())
				}
				return NewString(string(buf[:n]))
			},
		},
		"serial_read_line": {
			Name: "serial_read_line",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("serial_read_line() takes exactly 1 argument")
				}
				sp, ok := args[0].(*SerialPortValue)
				if !ok {
					return NewError("serial_read_line() argument must be a serial port handle")
				}
				if !sp.IsOpen {
					return NewError("serial_read_line() port is closed")
				}
				reader := sp.Reader.(*bufio.Reader)
				line, err := reader.ReadString('\n')
				if err != nil {
					return NewError("serial_read_line() failed: %s", err.Error())
				}
				// Trim trailing \r\n or \n
				line = strings.TrimRight(line, "\r\n")
				return NewString(line)
			},
		},
		"serial_available": {
			Name: "serial_available",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("serial_available() takes exactly 1 argument")
				}
				sp, ok := args[0].(*SerialPortValue)
				if !ok {
					return NewError("serial_available() argument must be a serial port handle")
				}
				if !sp.IsOpen {
					return NewError("serial_available() port is closed")
				}
				reader := sp.Reader.(*bufio.Reader)
				return NewBoolean(reader.Buffered() > 0)
			},
		},
		"serial_set_timeout": {
			Name: "serial_set_timeout",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("serial_set_timeout() takes exactly 2 arguments (port, milliseconds)")
				}
				sp, ok := args[0].(*SerialPortValue)
				if !ok {
					return NewError("serial_set_timeout() first argument must be a serial port handle")
				}
				if !sp.IsOpen {
					return NewError("serial_set_timeout() port is closed")
				}
				ms, ok := args[1].(*IntegerValue)
				if !ok {
					return NewError("serial_set_timeout() second argument must be an integer (milliseconds)")
				}
				port := sp.Handle.(serial.Port)
				var timeout time.Duration
				if ms.Val < 0 {
					// Negative = block forever (effectively very long timeout)
					timeout = time.Duration(0)
				} else if ms.Val == 0 {
					// Zero = non-blocking: use 1ms minimum
					timeout = time.Millisecond
				} else {
					timeout = time.Duration(ms.Val) * time.Millisecond
				}
				err := port.SetReadTimeout(timeout)
				if err != nil {
					return NewError("serial_set_timeout() failed: %s", err.Error())
				}
				return NULL
			},
		},
		"serial_flush": {
			Name: "serial_flush",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("serial_flush() takes exactly 1 argument")
				}
				sp, ok := args[0].(*SerialPortValue)
				if !ok {
					return NewError("serial_flush() argument must be a serial port handle")
				}
				if !sp.IsOpen {
					return NewError("serial_flush() port is closed")
				}
				port := sp.Handle.(serial.Port)
				err := port.ResetInputBuffer()
				if err != nil {
					return NewError("serial_flush() failed to flush input: %s", err.Error())
				}
				err = port.ResetOutputBuffer()
				if err != nil {
					return NewError("serial_flush() failed to flush output: %s", err.Error())
				}
				// Also reset the buffered reader since we flushed the input
				sp.Reader = bufio.NewReader(port)
				return NULL
			},
		},
		"serial_set_dtr": {
			Name: "serial_set_dtr",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("serial_set_dtr() takes exactly 2 arguments (port, state)")
				}
				sp, ok := args[0].(*SerialPortValue)
				if !ok {
					return NewError("serial_set_dtr() first argument must be a serial port handle")
				}
				if !sp.IsOpen {
					return NewError("serial_set_dtr() port is closed")
				}
				state, ok := args[1].(*BooleanValue)
				if !ok {
					return NewError("serial_set_dtr() second argument must be a boolean")
				}
				port := sp.Handle.(serial.Port)
				err := port.SetDTR(state.Val)
				if err != nil {
					return NewError("serial_set_dtr() failed: %s", err.Error())
				}
				return NULL
			},
		},
		"serial_set_rts": {
			Name: "serial_set_rts",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("serial_set_rts() takes exactly 2 arguments (port, state)")
				}
				sp, ok := args[0].(*SerialPortValue)
				if !ok {
					return NewError("serial_set_rts() first argument must be a serial port handle")
				}
				if !sp.IsOpen {
					return NewError("serial_set_rts() port is closed")
				}
				state, ok := args[1].(*BooleanValue)
				if !ok {
					return NewError("serial_set_rts() second argument must be a boolean")
				}
				port := sp.Handle.(serial.Port)
				err := port.SetRTS(state.Val)
				if err != nil {
					return NewError("serial_set_rts() failed: %s", err.Error())
				}
				return NULL
			},
		},
		"serial_get_signals": {
			Name: "serial_get_signals",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("serial_get_signals() takes exactly 1 argument")
				}
				sp, ok := args[0].(*SerialPortValue)
				if !ok {
					return NewError("serial_get_signals() argument must be a serial port handle")
				}
				if !sp.IsOpen {
					return NewError("serial_get_signals() port is closed")
				}
				port := sp.Handle.(serial.Port)
				status, err := port.GetModemStatusBits()
				if err != nil {
					return NewError("serial_get_signals() failed: %s", err.Error())
				}
				pairs := map[string]Value{
					"cts": NewBoolean(status.CTS),
					"dsr": NewBoolean(status.DSR),
					"ri":  NewBoolean(status.RI),
					"dcd": NewBoolean(status.DCD),
				}
				return NewTable(pairs)
			},
		},

		// ============================================================
		// Network I/O (TCP/UDP)
		// ============================================================
		"net_connect": {
			Name: "net_connect",
			Fn: func(args ...Value) Value {
				if len(args) < 2 || len(args) > 3 {
					return NewError("net_connect() takes 2 or 3 arguments (host, port [, protocol])")
				}
				host, ok := args[0].(*StringValue)
				if !ok {
					return NewError("net_connect() first argument must be a string (host)")
				}
				portArg, ok := args[1].(*IntegerValue)
				if !ok {
					return NewError("net_connect() second argument must be an integer (port)")
				}
				protocol := "tcp"
				if len(args) == 3 {
					protoVal, ok := args[2].(*StringValue)
					if !ok {
						return NewError("net_connect() third argument must be a string (protocol: \"tcp\" or \"udp\")")
					}
					protocol = strings.ToLower(protoVal.Val)
					if protocol != "tcp" && protocol != "udp" {
						return NewError("net_connect() protocol must be \"tcp\" or \"udp\"")
					}
				}
				address := fmt.Sprintf("%s:%d", host.Val, portArg.Val)
				conn, err := net.Dial(protocol, address)
				if err != nil {
					return NewError("net_connect() failed: %s", err.Error())
				}
				reader := bufio.NewReader(conn)
				return &NetConnValue{
					Address:  address,
					Protocol: protocol,
					Handle:   conn,
					Reader:   reader,
					IsOpen:   true,
					IsServer: false,
				}
			},
		},
		"net_close": {
			Name: "net_close",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("net_close() takes exactly 1 argument")
				}
				nc, ok := args[0].(*NetConnValue)
				if !ok {
					return NewError("net_close() argument must be a network connection handle")
				}
				if !nc.IsOpen {
					return NewError("net_close() connection already closed")
				}
				conn := nc.Handle.(net.Conn)
				nc.IsOpen = false
				nc.Handle = nil
				nc.Reader = nil
				err := conn.Close()
				if err != nil {
					return NewError("net_close() failed: %s", err.Error())
				}
				return NULL
			},
		},
		"net_write": {
			Name: "net_write",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("net_write() takes exactly 2 arguments (conn, data)")
				}
				nc, ok := args[0].(*NetConnValue)
				if !ok {
					return NewError("net_write() first argument must be a network connection handle")
				}
				if !nc.IsOpen {
					return NewError("net_write() connection is closed")
				}
				conn := nc.Handle.(net.Conn)
				var data []byte
				switch v := args[1].(type) {
				case *StringValue:
					data = []byte(v.Val)
				case *BytesValue:
					data = v.Data
				default:
					return NewError("net_write() second argument must be a string or bytes")
				}
				n, err := conn.Write(data)
				if err != nil {
					return NewError("net_write() failed: %s", err.Error())
				}
				return NewInteger(int64(n))
			},
		},
		"net_read": {
			Name: "net_read",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("net_read() takes exactly 2 arguments (conn, count)")
				}
				nc, ok := args[0].(*NetConnValue)
				if !ok {
					return NewError("net_read() first argument must be a network connection handle")
				}
				if !nc.IsOpen {
					return NewError("net_read() connection is closed")
				}
				count, ok := args[1].(*IntegerValue)
				if !ok {
					return NewError("net_read() second argument must be an integer (byte count)")
				}
				if count.Val <= 0 {
					return NewError("net_read() count must be positive")
				}
				conn := nc.Handle.(net.Conn)
				buf := make([]byte, count.Val)
				n, err := conn.Read(buf)
				if err != nil {
					return NewError("net_read() failed: %s", err.Error())
				}
				return NewString(string(buf[:n]))
			},
		},
		"net_read_line": {
			Name: "net_read_line",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("net_read_line() takes exactly 1 argument")
				}
				nc, ok := args[0].(*NetConnValue)
				if !ok {
					return NewError("net_read_line() argument must be a network connection handle")
				}
				if !nc.IsOpen {
					return NewError("net_read_line() connection is closed")
				}
				reader := nc.Reader.(*bufio.Reader)
				line, err := reader.ReadString('\n')
				if err != nil {
					return NewError("net_read_line() failed: %s", err.Error())
				}
				// Trim trailing \r\n or \n
				line = strings.TrimRight(line, "\r\n")
				return NewString(line)
			},
		},
		"net_set_timeout": {
			Name: "net_set_timeout",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("net_set_timeout() takes exactly 2 arguments (conn, milliseconds)")
				}
				nc, ok := args[0].(*NetConnValue)
				if !ok {
					return NewError("net_set_timeout() first argument must be a network connection handle")
				}
				if !nc.IsOpen {
					return NewError("net_set_timeout() connection is closed")
				}
				ms, ok := args[1].(*IntegerValue)
				if !ok {
					return NewError("net_set_timeout() second argument must be an integer (milliseconds)")
				}
				conn := nc.Handle.(net.Conn)
				var timeout time.Duration
				if ms.Val < 0 {
					// -1 means block forever (no timeout)
					timeout = 0
				} else if ms.Val == 0 {
					// 0 means non-blocking (immediate timeout)
					timeout = 1 * time.Nanosecond
				} else {
					timeout = time.Duration(ms.Val) * time.Millisecond
				}
				err := conn.SetReadDeadline(time.Now().Add(timeout))
				if err != nil {
					return NewError("net_set_timeout() failed: %s", err.Error())
				}
				return NULL
			},
		},
		"net_listen": {
			Name: "net_listen",
			Fn: func(args ...Value) Value {
				if len(args) < 1 || len(args) > 2 {
					return NewError("net_listen() takes 1 or 2 arguments (port [, protocol])")
				}
				portArg, ok := args[0].(*IntegerValue)
				if !ok {
					return NewError("net_listen() first argument must be an integer (port)")
				}
				protocol := "tcp"
				if len(args) == 2 {
					protoVal, ok := args[1].(*StringValue)
					if !ok {
						return NewError("net_listen() second argument must be a string (protocol: \"tcp\" or \"udp\")")
					}
					protocol = strings.ToLower(protoVal.Val)
					if protocol != "tcp" && protocol != "udp" {
						return NewError("net_listen() protocol must be \"tcp\" or \"udp\"")
					}
				}
				address := fmt.Sprintf(":%d", portArg.Val)
				listener, err := net.Listen(protocol, address)
				if err != nil {
					return NewError("net_listen() failed: %s", err.Error())
				}
				return &NetConnValue{
					Address:  address,
					Protocol: protocol,
					Handle:   listener,
					Reader:   nil,
					IsOpen:   true,
					IsServer: true,
				}
			},
		},
		"net_accept": {
			Name: "net_accept",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("net_accept() takes exactly 1 argument")
				}
				nc, ok := args[0].(*NetConnValue)
				if !ok {
					return NewError("net_accept() argument must be a network connection handle")
				}
				if !nc.IsServer {
					return NewError("net_accept() can only be called on a listener")
				}
				if !nc.IsOpen {
					return NewError("net_accept() listener is closed")
				}
				listener := nc.Handle.(net.Listener)
				conn, err := listener.Accept()
				if err != nil {
					return NewError("net_accept() failed: %s", err.Error())
				}
				reader := bufio.NewReader(conn)
				return &NetConnValue{
					Address:  conn.RemoteAddr().String(),
					Protocol: nc.Protocol,
					Handle:   conn,
					Reader:   reader,
					IsOpen:   true,
					IsServer: false,
				}
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

// decodeBinaryBytes checks if a string is space-separated 8-digit binary bytes
// and decodes them to the corresponding text string.
func decodeBinaryBytes(s string) (string, bool) {
	if len(s) == 0 {
		return "", false
	}
	parts := strings.Split(s, " ")
	if len(parts) < 1 {
		return "", false
	}
	var result []byte
	for _, part := range parts {
		if len(part) != 8 {
			return "", false
		}
		val, err := strconv.ParseUint(part, 2, 8)
		if err != nil {
			return "", false
		}
		result = append(result, byte(val))
	}
	return string(result), true
}

// decodeHexBytes checks if a string is space-separated 2-digit hex bytes
// and decodes them to the corresponding text string.
func decodeHexBytes(s string) (string, bool) {
	if len(s) == 0 {
		return "", false
	}
	parts := strings.Split(s, " ")
	if len(parts) < 1 {
		return "", false
	}
	var result []byte
	for _, part := range parts {
		if len(part) != 2 {
			return "", false
		}
		val, err := strconv.ParseUint(part, 16, 8)
		if err != nil {
			return "", false
		}
		result = append(result, byte(val))
	}
	return string(result), true
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
