package types

import (
	"plain/internal/ast"
	"strings"
)

// TypeKind represents the category of a type
type TypeKind int

const (
	TypeUnknown TypeKind = iota
	TypeInteger
	TypeFloat
	TypeString
	TypeBoolean
	TypeNull
	TypeList
	TypeTable
	TypeRecord
	TypeAny // for untyped collections
)

// String returns a human-readable name for the type kind
func (k TypeKind) String() string {
	switch k {
	case TypeInteger:
		return "integer"
	case TypeFloat:
		return "float"
	case TypeString:
		return "string"
	case TypeBoolean:
		return "boolean"
	case TypeNull:
		return "null"
	case TypeList:
		return "list"
	case TypeTable:
		return "table"
	case TypeRecord:
		return "record"
	case TypeAny:
		return "any"
	default:
		return "unknown"
	}
}

// Type represents a PLAIN type
type Type struct {
	Kind        TypeKind
	Name        string // Full type name, e.g., "list of integer"
	ElementType *Type  // For list - element type
	KeyType     *Type  // For table - key type
	ValueType   *Type  // For table - value type
	RecordName  string // For record types - the record type name
}

// Primitive type singletons
var (
	IntegerType = &Type{Kind: TypeInteger, Name: "integer"}
	FloatType   = &Type{Kind: TypeFloat, Name: "float"}
	StringType  = &Type{Kind: TypeString, Name: "string"}
	BooleanType = &Type{Kind: TypeBoolean, Name: "boolean"}
	NullType    = &Type{Kind: TypeNull, Name: "null"}
	AnyType     = &Type{Kind: TypeAny, Name: "any"}
	UnknownType = &Type{Kind: TypeUnknown, Name: "unknown"}
)

// NewListType creates a list type with optional element type
func NewListType(elementType *Type) *Type {
	name := "list"
	if elementType != nil && elementType.Kind != TypeAny {
		name = "list of " + elementType.Name
	}
	return &Type{
		Kind:        TypeList,
		Name:        name,
		ElementType: elementType,
	}
}

// NewTableType creates a table type with optional key/value types
func NewTableType(keyType, valueType *Type) *Type {
	name := "table"
	if keyType != nil && valueType != nil && keyType.Kind != TypeAny && valueType.Kind != TypeAny {
		name = "table of " + keyType.Name + " to " + valueType.Name
	}
	return &Type{
		Kind:      TypeTable,
		Name:      name,
		KeyType:   keyType,
		ValueType: valueType,
	}
}

// NewRecordType creates a record type
func NewRecordType(recordName string) *Type {
	return &Type{
		Kind:       TypeRecord,
		Name:       recordName,
		RecordName: recordName,
	}
}

// String returns the type name
func (t *Type) String() string {
	if t == nil {
		return "unknown"
	}
	return t.Name
}

// Equals checks if two types are the same
func (t *Type) Equals(other *Type) bool {
	if t == nil || other == nil {
		return t == other
	}
	if t.Kind != other.Kind {
		return false
	}
	switch t.Kind {
	case TypeList:
		if t.ElementType == nil && other.ElementType == nil {
			return true
		}
		if t.ElementType != nil && other.ElementType != nil {
			return t.ElementType.Equals(other.ElementType)
		}
		return false
	case TypeTable:
		keyMatch := (t.KeyType == nil && other.KeyType == nil) ||
			(t.KeyType != nil && other.KeyType != nil && t.KeyType.Equals(other.KeyType))
		valueMatch := (t.ValueType == nil && other.ValueType == nil) ||
			(t.ValueType != nil && other.ValueType != nil && t.ValueType.Equals(other.ValueType))
		return keyMatch && valueMatch
	case TypeRecord:
		return t.RecordName == other.RecordName
	default:
		return true
	}
}

// InferFromPrefix infers type from PLAIN variable naming convention
// int, flt, str, bln, lst, tbl prefixes
func InferFromPrefix(name string) *Type {
	if len(name) < 3 {
		return nil
	}

	prefix := strings.ToLower(name[:3])
	switch prefix {
	case "int":
		return IntegerType
	case "flt":
		return FloatType
	case "str":
		return StringType
	case "bln":
		return BooleanType
	case "lst":
		return NewListType(nil)
	case "tbl":
		return NewTableType(nil, nil)
	}
	return nil
}

// InferFromLiteral infers type from a literal AST node
func InferFromLiteral(expr ast.Expression) *Type {
	switch e := expr.(type) {
	case *ast.IntegerLiteral:
		return IntegerType
	case *ast.FloatLiteral:
		return FloatType
	case *ast.StringLiteral:
		return StringType
	case *ast.InterpolatedString:
		return StringType
	case *ast.BooleanLiteral:
		return BooleanType
	case *ast.NullLiteral:
		return NullType
	case *ast.ListLiteral:
		// Infer element type from first element if present
		if len(e.Elements) > 0 {
			elemType := InferFromLiteral(e.Elements[0])
			return NewListType(elemType)
		}
		return NewListType(nil)
	case *ast.TableLiteral:
		// Infer key/value types from first pair if present
		for key, value := range e.Pairs {
			keyType := InferFromLiteral(key)
			valueType := InferFromLiteral(value)
			return NewTableType(keyType, valueType)
		}
		return NewTableType(nil, nil)
	case *ast.RecordLiteral:
		if e.Type != nil {
			return NewRecordType(e.Type.Value)
		}
		return UnknownType
	}
	return UnknownType
}

// TypeFromName converts a type name string to a Type
func TypeFromName(name string) *Type {
	switch strings.ToLower(name) {
	case "integer", "int":
		return IntegerType
	case "float", "flt":
		return FloatType
	case "string", "str":
		return StringType
	case "boolean", "bool", "bln":
		return BooleanType
	case "list", "lst":
		return NewListType(nil)
	case "table", "tbl":
		return NewTableType(nil, nil)
	default:
		// Could be a record type
		return NewRecordType(name)
	}
}

// CanAssign checks if a value type can be assigned to a target type
func CanAssign(target, value *Type) bool {
	if target == nil || value == nil {
		return true // Unknown types - allow for now
	}

	// Unknown value type (e.g., from function call) can be assigned to any target
	// Type checking will be deferred to runtime
	if value.Kind == TypeUnknown {
		return true
	}

	// Any type accepts anything
	if target.Kind == TypeAny || value.Kind == TypeAny {
		return true
	}

	// Null can be assigned to any reference type
	if value.Kind == TypeNull {
		return target.Kind == TypeList || target.Kind == TypeTable ||
			target.Kind == TypeRecord || target.Kind == TypeNull
	}

	// Same type
	if target.Kind == value.Kind {
		// For collections, check element types
		switch target.Kind {
		case TypeList:
			if target.ElementType == nil {
				return true // Untyped list accepts any list
			}
			if value.ElementType == nil {
				return true // Untyped value can go into typed list (runtime check)
			}
			return CanAssign(target.ElementType, value.ElementType)
		case TypeTable:
			if target.KeyType == nil || target.ValueType == nil {
				return true // Untyped table accepts any table
			}
			if value.KeyType == nil || value.ValueType == nil {
				return true // Runtime check
			}
			return CanAssign(target.KeyType, value.KeyType) &&
				CanAssign(target.ValueType, value.ValueType)
		case TypeRecord:
			return target.RecordName == value.RecordName
		}
		return true
	}

	// Integer can be assigned to float
	if target.Kind == TypeFloat && value.Kind == TypeInteger {
		return true
	}

	return false
}

// AreCompatible checks if two types are compatible for a binary operator
func AreCompatible(left, right *Type, operator string) (*Type, bool) {
	if left == nil || right == nil {
		return UnknownType, true // Unknown types - allow for now
	}

	switch operator {
	// Arithmetic operators
	case "+", "-", "*", "/", "%", "**":
		if left.Kind == TypeInteger && right.Kind == TypeInteger {
			return IntegerType, true
		}
		if (left.Kind == TypeInteger || left.Kind == TypeFloat) &&
			(right.Kind == TypeInteger || right.Kind == TypeFloat) {
			return FloatType, true
		}
		return nil, false

	// Integer division
	case "//":
		if (left.Kind == TypeInteger || left.Kind == TypeFloat) &&
			(right.Kind == TypeInteger || right.Kind == TypeFloat) {
			return IntegerType, true
		}
		return nil, false

	// String concatenation
	case "&":
		if left.Kind == TypeString && right.Kind == TypeString {
			return StringType, true
		}
		return nil, false

	// Comparison operators
	case "==", "!=":
		// Allow comparing same types
		if left.Kind == right.Kind {
			return BooleanType, true
		}
		// Allow comparing numbers
		if (left.Kind == TypeInteger || left.Kind == TypeFloat) &&
			(right.Kind == TypeInteger || right.Kind == TypeFloat) {
			return BooleanType, true
		}
		// Allow comparing with null
		if left.Kind == TypeNull || right.Kind == TypeNull {
			return BooleanType, true
		}
		return nil, false

	// Ordering operators
	case "<", ">", "<=", ">=":
		if (left.Kind == TypeInteger || left.Kind == TypeFloat) &&
			(right.Kind == TypeInteger || right.Kind == TypeFloat) {
			return BooleanType, true
		}
		if left.Kind == TypeString && right.Kind == TypeString {
			return BooleanType, true
		}
		return nil, false

	// Logical operators
	case "and", "or":
		if left.Kind == TypeBoolean && right.Kind == TypeBoolean {
			return BooleanType, true
		}
		return nil, false
	}

	return UnknownType, true
}

// UnaryResultType returns the result type of a unary operator
func UnaryResultType(operand *Type, operator string) (*Type, bool) {
	if operand == nil {
		return UnknownType, true
	}

	switch operator {
	case "-":
		if operand.Kind == TypeInteger {
			return IntegerType, true
		}
		if operand.Kind == TypeFloat {
			return FloatType, true
		}
		return nil, false
	case "not":
		if operand.Kind == TypeBoolean {
			return BooleanType, true
		}
		return nil, false
	}

	return UnknownType, true
}
