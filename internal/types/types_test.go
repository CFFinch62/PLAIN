package types

import (
	"plain/internal/ast"
	"plain/internal/token"
	"testing"
)

func TestTypeKindString(t *testing.T) {
	tests := []struct {
		kind     TypeKind
		expected string
	}{
		{TypeInteger, "integer"},
		{TypeFloat, "float"},
		{TypeString, "string"},
		{TypeBoolean, "boolean"},
		{TypeNull, "null"},
		{TypeList, "list"},
		{TypeTable, "table"},
		{TypeRecord, "record"},
		{TypeAny, "any"},
		{TypeUnknown, "unknown"},
	}

	for _, tt := range tests {
		if got := tt.kind.String(); got != tt.expected {
			t.Errorf("TypeKind(%d).String() = %s, want %s", tt.kind, got, tt.expected)
		}
	}
}

func TestInferFromPrefix(t *testing.T) {
	tests := []struct {
		name     string
		expected TypeKind
	}{
		{"intCount", TypeInteger},
		{"intAge", TypeInteger},
		{"fltTemperature", TypeFloat},
		{"fltPrice", TypeFloat},
		{"strName", TypeString},
		{"strMessage", TypeString},
		{"blnIsReady", TypeBoolean},
		{"blnActive", TypeBoolean},
		{"lstItems", TypeList},
		{"lstNumbers", TypeList},
		{"tblScores", TypeTable},
		{"tblData", TypeTable},
		{"userName", TypeUnknown}, // No prefix match
		{"counter", TypeUnknown},  // Too short for prefix
		{"ab", TypeUnknown},       // Too short
	}

	for _, tt := range tests {
		result := InferFromPrefix(tt.name)
		if tt.expected == TypeUnknown {
			if result != nil {
				t.Errorf("InferFromPrefix(%s) = %v, want nil", tt.name, result)
			}
		} else {
			if result == nil || result.Kind != tt.expected {
				t.Errorf("InferFromPrefix(%s) = %v, want %s", tt.name, result, tt.expected)
			}
		}
	}
}

func TestInferFromLiteral(t *testing.T) {
	tests := []struct {
		name     string
		expr     ast.Expression
		expected TypeKind
	}{
		{"integer", &ast.IntegerLiteral{Value: 42}, TypeInteger},
		{"float", &ast.FloatLiteral{Value: 3.14}, TypeFloat},
		{"string", &ast.StringLiteral{Value: "hello"}, TypeString},
		{"interpolated", &ast.InterpolatedString{Value: "hello {name}"}, TypeString},
		{"true", &ast.BooleanLiteral{Value: true}, TypeBoolean},
		{"false", &ast.BooleanLiteral{Value: false}, TypeBoolean},
		{"null", &ast.NullLiteral{}, TypeNull},
		{"empty list", &ast.ListLiteral{Elements: []ast.Expression{}}, TypeList},
		{"list with int", &ast.ListLiteral{Elements: []ast.Expression{
			&ast.IntegerLiteral{Value: 1},
		}}, TypeList},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := InferFromLiteral(tt.expr)
			if result == nil || result.Kind != tt.expected {
				t.Errorf("InferFromLiteral() = %v, want %s", result, tt.expected)
			}
		})
	}
}

func TestTypeFromName(t *testing.T) {
	tests := []struct {
		name     string
		expected TypeKind
	}{
		{"integer", TypeInteger},
		{"int", TypeInteger},
		{"float", TypeFloat},
		{"flt", TypeFloat},
		{"string", TypeString},
		{"str", TypeString},
		{"boolean", TypeBoolean},
		{"bool", TypeBoolean},
		{"list", TypeList},
		{"table", TypeTable},
		{"Person", TypeRecord}, // Unknown names become record types
	}

	for _, tt := range tests {
		result := TypeFromName(tt.name)
		if result == nil || result.Kind != tt.expected {
			t.Errorf("TypeFromName(%s) = %v, want %s", tt.name, result, tt.expected)
		}
	}
}

func TestCanAssign(t *testing.T) {
	tests := []struct {
		name     string
		target   *Type
		value    *Type
		expected bool
	}{
		{"int to int", IntegerType, IntegerType, true},
		{"float to float", FloatType, FloatType, true},
		{"int to float", FloatType, IntegerType, true},
		{"float to int", IntegerType, FloatType, false},
		{"string to string", StringType, StringType, true},
		{"string to int", IntegerType, StringType, false},
		{"null to list", NewListType(nil), NullType, true},
		{"null to table", NewTableType(nil, nil), NullType, true},
		{"null to int", IntegerType, NullType, false},
		{"any to any", AnyType, IntegerType, true},
		{"nil types", nil, nil, true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := CanAssign(tt.target, tt.value)
			if result != tt.expected {
				t.Errorf("CanAssign(%v, %v) = %v, want %v", tt.target, tt.value, result, tt.expected)
			}
		})
	}
}

func TestAreCompatible(t *testing.T) {
	tests := []struct {
		name       string
		left       *Type
		right      *Type
		operator   string
		resultKind TypeKind
		ok         bool
	}{
		// Arithmetic
		{"int + int", IntegerType, IntegerType, "+", TypeInteger, true},
		{"int + float", IntegerType, FloatType, "+", TypeFloat, true},
		{"float + float", FloatType, FloatType, "+", TypeFloat, true},
		{"string + int", StringType, IntegerType, "+", TypeUnknown, false},

		// String concatenation
		{"string & string", StringType, StringType, "&", TypeString, true},
		{"int & string", IntegerType, StringType, "&", TypeUnknown, false},

		// Comparison
		{"int == int", IntegerType, IntegerType, "==", TypeBoolean, true},
		{"int < float", IntegerType, FloatType, "<", TypeBoolean, true},
		{"string == string", StringType, StringType, "==", TypeBoolean, true},
		{"null == null", NullType, NullType, "==", TypeBoolean, true},

		// Logical
		{"bool and bool", BooleanType, BooleanType, "and", TypeBoolean, true},
		{"bool or bool", BooleanType, BooleanType, "or", TypeBoolean, true},
		{"int and bool", IntegerType, BooleanType, "and", TypeUnknown, false},

		// Integer division
		{"int // int", IntegerType, IntegerType, "//", TypeInteger, true},
		{"float // int", FloatType, IntegerType, "//", TypeInteger, true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result, ok := AreCompatible(tt.left, tt.right, tt.operator)
			if ok != tt.ok {
				t.Errorf("AreCompatible() ok = %v, want %v", ok, tt.ok)
			}
			if tt.ok && result != nil && result.Kind != tt.resultKind {
				t.Errorf("AreCompatible() result = %v, want %s", result, tt.resultKind)
			}
		})
	}
}

func TestUnaryResultType(t *testing.T) {
	tests := []struct {
		name       string
		operand    *Type
		operator   string
		resultKind TypeKind
		ok         bool
	}{
		{"-int", IntegerType, "-", TypeInteger, true},
		{"-float", FloatType, "-", TypeFloat, true},
		{"-string", StringType, "-", TypeUnknown, false},
		{"not bool", BooleanType, "not", TypeBoolean, true},
		{"not int", IntegerType, "not", TypeUnknown, false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result, ok := UnaryResultType(tt.operand, tt.operator)
			if ok != tt.ok {
				t.Errorf("UnaryResultType() ok = %v, want %v", ok, tt.ok)
			}
			if tt.ok && result != nil && result.Kind != tt.resultKind {
				t.Errorf("UnaryResultType() result = %v, want %s", result, tt.resultKind)
			}
		})
	}
}

func TestTypeEquals(t *testing.T) {
	tests := []struct {
		name     string
		t1       *Type
		t2       *Type
		expected bool
	}{
		{"same primitive", IntegerType, IntegerType, true},
		{"different primitive", IntegerType, FloatType, false},
		{"same list", NewListType(IntegerType), NewListType(IntegerType), true},
		{"different list", NewListType(IntegerType), NewListType(StringType), false},
		{"same record", NewRecordType("Person"), NewRecordType("Person"), true},
		{"different record", NewRecordType("Person"), NewRecordType("Animal"), false},
		{"nil types", nil, nil, true},
		{"one nil", IntegerType, nil, false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := tt.t1.Equals(tt.t2)
			if result != tt.expected {
				t.Errorf("Type.Equals() = %v, want %v", result, tt.expected)
			}
		})
	}
}

func TestNewListType(t *testing.T) {
	// Untyped list
	lst := NewListType(nil)
	if lst.Name != "list" {
		t.Errorf("NewListType(nil).Name = %s, want list", lst.Name)
	}

	// Typed list
	intList := NewListType(IntegerType)
	if intList.Name != "list of integer" {
		t.Errorf("NewListType(IntegerType).Name = %s, want 'list of integer'", intList.Name)
	}
}

func TestNewTableType(t *testing.T) {
	// Untyped table
	tbl := NewTableType(nil, nil)
	if tbl.Name != "table" {
		t.Errorf("NewTableType(nil, nil).Name = %s, want table", tbl.Name)
	}

	// Typed table
	strIntTable := NewTableType(StringType, IntegerType)
	if strIntTable.Name != "table of string to integer" {
		t.Errorf("NewTableType().Name = %s, want 'table of string to integer'", strIntTable.Name)
	}
}

// Helper to create token for tests
func makeToken(literal string) token.Token {
	return token.Token{Literal: literal, Line: 1, Column: 1}
}
