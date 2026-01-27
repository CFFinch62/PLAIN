package runtime

import (
	"math"
	"testing"
)

// ============================================================
// Type Checking Tests
// ============================================================

func TestIsInt(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["is_int"].Fn

	tests := []struct {
		input    Value
		expected bool
	}{
		{NewInteger(42), true},
		{NewFloat(3.14), false},
		{NewString("hello"), false},
		{NewBoolean(true), false},
		{NULL, false},
	}

	for _, tt := range tests {
		result := fn(tt.input)
		boolVal, ok := result.(*BooleanValue)
		if !ok {
			t.Fatalf("expected BooleanValue, got %T", result)
		}
		if boolVal.Val != tt.expected {
			t.Errorf("is_int(%v) = %v, want %v", tt.input, boolVal.Val, tt.expected)
		}
	}
}

func TestIsFloat(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["is_float"].Fn

	tests := []struct {
		input    Value
		expected bool
	}{
		{NewFloat(3.14), true},
		{NewInteger(42), false},
		{NewString("hello"), false},
	}

	for _, tt := range tests {
		result := fn(tt.input)
		boolVal := result.(*BooleanValue)
		if boolVal.Val != tt.expected {
			t.Errorf("is_float(%v) = %v, want %v", tt.input, boolVal.Val, tt.expected)
		}
	}
}

func TestIsString(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["is_string"].Fn

	result := fn(NewString("hello"))
	if !result.(*BooleanValue).Val {
		t.Error("is_string('hello') should be true")
	}

	result = fn(NewInteger(42))
	if result.(*BooleanValue).Val {
		t.Error("is_string(42) should be false")
	}
}

func TestIsBool(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["is_bool"].Fn

	result := fn(NewBoolean(true))
	if !result.(*BooleanValue).Val {
		t.Error("is_bool(true) should be true")
	}

	result = fn(NewInteger(1))
	if result.(*BooleanValue).Val {
		t.Error("is_bool(1) should be false")
	}
}

func TestIsList(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["is_list"].Fn

	list := &ListValue{Elements: []Value{NewInteger(1), NewInteger(2)}}
	result := fn(list)
	if !result.(*BooleanValue).Val {
		t.Error("is_list([1,2]) should be true")
	}
}

func TestIsTable(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["is_table"].Fn

	table := &TableValue{Pairs: map[string]Value{"a": NewInteger(1)}}
	result := fn(table)
	if !result.(*BooleanValue).Val {
		t.Error("is_table should be true for tables")
	}
}

func TestIsNull(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["is_null"].Fn

	result := fn(NULL)
	if !result.(*BooleanValue).Val {
		t.Error("is_null(null) should be true")
	}

	result = fn(NewInteger(0))
	if result.(*BooleanValue).Val {
		t.Error("is_null(0) should be false")
	}
}

// ============================================================
// Type Conversion Tests
// ============================================================

func TestToBool(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["to_bool"].Fn

	tests := []struct {
		input    Value
		expected bool
	}{
		{NewInteger(1), true},
		{NewInteger(0), false},
		{NewFloat(1.0), true},
		{NewFloat(0.0), false},
		{NewString("hello"), true},
		{NewString(""), false},
		{NULL, false},
		{NewBoolean(true), true},
		{NewBoolean(false), false},
	}

	for _, tt := range tests {
		result := fn(tt.input)
		boolVal := result.(*BooleanValue)
		if boolVal.Val != tt.expected {
			t.Errorf("to_bool(%v) = %v, want %v", tt.input, boolVal.Val, tt.expected)
		}
	}
}

// ============================================================
// String Operation Tests
// ============================================================

func TestUpper(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["upper"].Fn

	result := fn(NewString("hello"))
	if result.(*StringValue).Val != "HELLO" {
		t.Error("upper('hello') should be 'HELLO'")
	}
}

func TestLower(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["lower"].Fn

	result := fn(NewString("HELLO"))
	if result.(*StringValue).Val != "hello" {
		t.Error("lower('HELLO') should be 'hello'")
	}
}

func TestTrim(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["trim"].Fn

	result := fn(NewString("  hello  "))
	if result.(*StringValue).Val != "hello" {
		t.Error("trim should remove whitespace")
	}
}

func TestSplit(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["split"].Fn

	result := fn(NewString("a,b,c"), NewString(","))
	list := result.(*ListValue)
	if len(list.Elements) != 3 {
		t.Errorf("split should return 3 elements, got %d", len(list.Elements))
	}
}

func TestJoin(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["join"].Fn

	list := &ListValue{Elements: []Value{NewString("x"), NewString("y"), NewString("z")}}
	result := fn(list, NewString("-"))
	if result.(*StringValue).Val != "x-y-z" {
		t.Error("join should produce 'x-y-z'")
	}
}

func TestSubstring(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["substring"].Fn

	result := fn(NewString("Hello"), NewInteger(1), NewInteger(4))
	if result.(*StringValue).Val != "ell" {
		t.Errorf("substring('Hello', 1, 4) should be 'ell', got '%s'", result.(*StringValue).Val)
	}
}

func TestReplace(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["replace"].Fn

	result := fn(NewString("hello"), NewString("l"), NewString("r"))
	if result.(*StringValue).Val != "herro" {
		t.Error("replace should produce 'herro'")
	}
}

func TestContains(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["contains"].Fn

	// String contains
	result := fn(NewString("hello"), NewString("ell"))
	if !result.(*BooleanValue).Val {
		t.Error("contains('hello', 'ell') should be true")
	}

	// List contains
	list := &ListValue{Elements: []Value{NewInteger(1), NewInteger(2), NewInteger(3)}}
	result = fn(list, NewInteger(2))
	if !result.(*BooleanValue).Val {
		t.Error("contains([1,2,3], 2) should be true")
	}
}

func TestStartsWith(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["starts_with"].Fn

	result := fn(NewString("hello"), NewString("he"))
	if !result.(*BooleanValue).Val {
		t.Error("starts_with('hello', 'he') should be true")
	}
}

func TestEndsWith(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["ends_with"].Fn

	result := fn(NewString("hello"), NewString("lo"))
	if !result.(*BooleanValue).Val {
		t.Error("ends_with('hello', 'lo') should be true")
	}
}

// ============================================================
// Math Basic Tests
// ============================================================

func TestAbs(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["abs"].Fn

	result := fn(NewInteger(-5))
	if result.(*IntegerValue).Val != 5 {
		t.Error("abs(-5) should be 5")
	}

	result = fn(NewFloat(-3.14))
	if math.Abs(result.(*FloatValue).Val-3.14) > 0.001 {
		t.Error("abs(-3.14) should be 3.14")
	}
}

func TestSqrt(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["sqrt"].Fn

	result := fn(NewInteger(16))
	if result.(*FloatValue).Val != 4.0 {
		t.Error("sqrt(16) should be 4.0")
	}
}

func TestSqr(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["sqr"].Fn

	result := fn(NewInteger(5))
	if result.(*IntegerValue).Val != 25 {
		t.Error("sqr(5) should be 25")
	}
}

func TestPow(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["pow"].Fn

	result := fn(NewInteger(2), NewInteger(8))
	if result.(*FloatValue).Val != 256.0 {
		t.Error("pow(2, 8) should be 256.0")
	}
}

func TestRound(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["round"].Fn

	result := fn(NewFloat(3.7))
	if result.(*IntegerValue).Val != 4 {
		t.Error("round(3.7) should be 4")
	}

	result = fn(NewFloat(3.2))
	if result.(*IntegerValue).Val != 3 {
		t.Error("round(3.2) should be 3")
	}
}

func TestFloor(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["floor"].Fn

	result := fn(NewFloat(3.7))
	if result.(*IntegerValue).Val != 3 {
		t.Error("floor(3.7) should be 3")
	}
}

func TestCeil(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["ceil"].Fn

	result := fn(NewFloat(3.2))
	if result.(*IntegerValue).Val != 4 {
		t.Error("ceil(3.2) should be 4")
	}
}

func TestMinMax(t *testing.T) {
	builtins := GetBuiltins()
	minFn := builtins["min"].Fn
	maxFn := builtins["max"].Fn

	result := minFn(NewInteger(5), NewInteger(3))
	if result.(*IntegerValue).Val != 3 {
		t.Error("min(5, 3) should be 3")
	}

	result = maxFn(NewInteger(5), NewInteger(3))
	if result.(*IntegerValue).Val != 5 {
		t.Error("max(5, 3) should be 5")
	}
}

func TestMod(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["mod"].Fn

	result := fn(NewInteger(10), NewInteger(3))
	if result.(*IntegerValue).Val != 1 {
		t.Error("mod(10, 3) should be 1")
	}
}

// ============================================================
// Math Trig Tests
// ============================================================

func TestSinCosTan(t *testing.T) {
	builtins := GetBuiltins()

	result := builtins["sin"].Fn(NewInteger(0))
	if result.(*FloatValue).Val != 0 {
		t.Error("sin(0) should be 0")
	}

	result = builtins["cos"].Fn(NewInteger(0))
	if result.(*FloatValue).Val != 1 {
		t.Error("cos(0) should be 1")
	}

	result = builtins["tan"].Fn(NewInteger(0))
	if result.(*FloatValue).Val != 0 {
		t.Error("tan(0) should be 0")
	}
}

func TestAtan2(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["atan2"].Fn

	result := fn(NewFloat(1.0), NewFloat(1.0))
	expected := math.Atan2(1.0, 1.0)
	if math.Abs(result.(*FloatValue).Val-expected) > 0.0001 {
		t.Errorf("atan2(1, 1) should be approximately %f", expected)
	}
}

// ============================================================
// Math Log Tests
// ============================================================

func TestLog(t *testing.T) {
	builtins := GetBuiltins()

	result := builtins["log10"].Fn(NewInteger(100))
	if result.(*FloatValue).Val != 2.0 {
		t.Error("log10(100) should be 2.0")
	}

	result = builtins["log2"].Fn(NewInteger(8))
	if result.(*FloatValue).Val != 3.0 {
		t.Error("log2(8) should be 3.0")
	}
}

func TestExp(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["exp"].Fn

	result := fn(NewInteger(0))
	if result.(*FloatValue).Val != 1.0 {
		t.Error("exp(0) should be 1.0")
	}
}

// ============================================================
// Math Random Tests
// ============================================================

func TestRandom(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["random"].Fn

	for i := 0; i < 10; i++ {
		result := fn()
		val := result.(*FloatValue).Val
		if val < 0 || val >= 1 {
			t.Errorf("random() should be in [0, 1), got %f", val)
		}
	}
}

func TestRandomInt(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["random_int"].Fn

	for i := 0; i < 20; i++ {
		result := fn(NewInteger(1), NewInteger(6))
		val := result.(*IntegerValue).Val
		if val < 1 || val > 6 {
			t.Errorf("random_int(1, 6) should be in [1, 6], got %d", val)
		}
	}
}

func TestRandomChoice(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["random_choice"].Fn

	list := &ListValue{Elements: []Value{NewString("a"), NewString("b"), NewString("c")}}
	for i := 0; i < 10; i++ {
		result := fn(list)
		str := result.(*StringValue).Val
		if str != "a" && str != "b" && str != "c" {
			t.Errorf("random_choice should return element from list, got %s", str)
		}
	}
}

// ============================================================
// List Operation Tests
// ============================================================

func TestAppend(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["append"].Fn

	list := &ListValue{Elements: []Value{NewInteger(1), NewInteger(2)}}
	fn(list, NewInteger(3))
	if len(list.Elements) != 3 {
		t.Error("append should add element to list")
	}
}

func TestInsert(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["insert"].Fn

	list := &ListValue{Elements: []Value{NewString("a"), NewString("c")}}
	fn(list, NewInteger(1), NewString("b"))
	if list.Elements[1].(*StringValue).Val != "b" {
		t.Error("insert should insert at correct position")
	}
}

func TestRemove(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["remove"].Fn

	// Test list remove
	list := &ListValue{Elements: []Value{NewInteger(1), NewInteger(2), NewInteger(3)}}
	fn(list, NewInteger(2))
	if len(list.Elements) != 2 {
		t.Error("remove should remove element from list")
	}

	// Test table remove
	table := &TableValue{Pairs: map[string]Value{"a": NewInteger(1), "b": NewInteger(2)}}
	fn(table, NewString("a"))
	if len(table.Pairs) != 1 {
		t.Error("remove should remove key from table")
	}
}

func TestPop(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["pop"].Fn

	list := &ListValue{Elements: []Value{NewString("a"), NewString("b"), NewString("c")}}
	result := fn(list, NewInteger(1))
	if result.(*StringValue).Val != "b" {
		t.Error("pop should return popped element")
	}
	if len(list.Elements) != 2 {
		t.Error("pop should remove element from list")
	}
}

func TestSort(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["sort"].Fn

	list := &ListValue{Elements: []Value{NewInteger(3), NewInteger(1), NewInteger(2)}}
	fn(list)
	if list.Elements[0].(*IntegerValue).Val != 1 {
		t.Error("sort should sort list in ascending order")
	}
}

func TestReverse(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["reverse"].Fn

	list := &ListValue{Elements: []Value{NewInteger(1), NewInteger(2), NewInteger(3)}}
	fn(list)
	if list.Elements[0].(*IntegerValue).Val != 3 {
		t.Error("reverse should reverse list")
	}
}

// ============================================================
// Table Operation Tests
// ============================================================

func TestKeys(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["keys"].Fn

	table := &TableValue{Pairs: map[string]Value{"a": NewInteger(1), "b": NewInteger(2)}}
	result := fn(table)
	list := result.(*ListValue)
	if len(list.Elements) != 2 {
		t.Error("keys should return all keys")
	}
}

func TestValues(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["values"].Fn

	table := &TableValue{Pairs: map[string]Value{"a": NewInteger(1), "b": NewInteger(2)}}
	result := fn(table)
	list := result.(*ListValue)
	if len(list.Elements) != 2 {
		t.Error("values should return all values")
	}
}

func TestHasKey(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["has_key"].Fn

	table := &TableValue{Pairs: map[string]Value{"a": NewInteger(1)}}
	result := fn(table, NewString("a"))
	if !result.(*BooleanValue).Val {
		t.Error("has_key should return true for existing key")
	}

	result = fn(table, NewString("x"))
	if result.(*BooleanValue).Val {
		t.Error("has_key should return false for non-existing key")
	}
}

// ============================================================
// Error Handling Tests
// ============================================================

func TestArgumentErrors(t *testing.T) {
	builtins := GetBuiltins()

	// Test wrong number of arguments
	result := builtins["upper"].Fn()
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("upper() with no args should return error")
	}

	result = builtins["split"].Fn(NewString("a"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("split() with 1 arg should return error")
	}

	// Test wrong type
	result = builtins["upper"].Fn(NewInteger(42))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("upper(42) should return error")
	}
}
