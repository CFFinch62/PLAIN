package token

// TokenType represents the type of a token
type TokenType int

const (
	// Special tokens
	ILLEGAL TokenType = iota
	EOF
	NEWLINE

	// Indentation
	INDENT
	DEDENT

	// Identifiers and literals
	IDENT   // variable names, task names
	INT     // 123
	FLOAT   // 123.45
	STRING  // "hello"
	VSTRING // v"hello {name}" - interpolated string

	// Keywords - Task related
	TASK
	WITH
	USING
	DELIVER
	ABORT
	SWAP

	// Keywords - Variables
	VAR
	FXD
	AS

	// Keywords - Control flow
	IF
	THEN
	ELSE
	CHOOSE
	CHOICE
	DEFAULT
	LOOP
	FROM
	TO
	STEP
	IN
	EXIT
	CONTINUE

	// Keywords - Error handling
	ATTEMPT
	HANDLE
	ENSURE

	// Keywords - Modules
	USE
	ASSEMBLIES
	MODULES
	TASKS

	// Keywords - Records
	RECORD
	BASED
	ON

	// Keywords - Types
	INTEGER
	FLOAT_TYPE
	STRING_TYPE
	BOOLEAN
	LIST
	TABLE
	OF

	// Keywords - Literals
	TRUE
	FALSE
	NULL

	// Keywords - Logical operators
	AND
	OR
	NOT

	// Operators - Arithmetic
	PLUS     // +
	MINUS    // -
	ASTERISK // *
	SLASH    // /
	INTDIV   // //
	PERCENT  // %
	POWER    // **

	// Operators - Comparison
	EQ  // ==
	NEQ // !=
	LT  // <
	GT  // >
	LTE // <=
	GTE // >=

	// Operators - Assignment
	ASSIGN    // =
	PLUS_EQ   // +=
	MINUS_EQ  // -=
	TIMES_EQ  // *=
	DIV_EQ    // /=
	MOD_EQ    // %=
	CONCAT_EQ // &=

	// Operators - String
	AMPERSAND // & (string concatenation)

	// Delimiters
	LPAREN   // (
	RPAREN   // )
	LBRACKET // [
	RBRACKET // ]
	LBRACE   // {
	RBRACE   // }
	COMMA    // ,
	COLON    // :
	DOT      // .

	// Comments
	REM  // rem:
	NOTE // note:
)

// Token represents a lexical token
type Token struct {
	Type    TokenType
	Literal string
	Line    int
	Column  int
}

// Position represents a position in the source code
type Position struct {
	Line   int
	Column int
	Offset int
}

// keywords maps keyword strings to their token types
var keywords = map[string]TokenType{
	// Task related
	"task":    TASK,
	"with":    WITH,
	"using":   USING,
	"deliver": DELIVER,
	"abort":   ABORT,
	"swap":    SWAP,

	// Variables
	"var": VAR,
	"fxd": FXD,
	"as":  AS,

	// Control flow
	"if":       IF,
	"then":     THEN,
	"else":     ELSE,
	"choose":   CHOOSE,
	"choice":   CHOICE,
	"default":  DEFAULT,
	"loop":     LOOP,
	"from":     FROM,
	"to":       TO,
	"step":     STEP,
	"in":       IN,
	"exit":     EXIT,
	"continue": CONTINUE,

	// Error handling
	"attempt": ATTEMPT,
	"handle":  HANDLE,
	"ensure":  ENSURE,

	// Modules
	"use:":        USE,
	"assemblies:": ASSEMBLIES,
	"modules:":    MODULES,
	"tasks:":      TASKS,

	// Records
	"record": RECORD,
	"based":  BASED,
	"on":     ON,

	// Types
	"integer": INTEGER,
	"float":   FLOAT_TYPE,
	"string":  STRING_TYPE,
	"boolean": BOOLEAN,
	"list":    LIST,
	"table":   TABLE,
	"of":      OF,

	// Type prefixes (also keywords)
	"int": INTEGER,
	"flt": FLOAT_TYPE,
	"str": STRING_TYPE,
	"bln": BOOLEAN,
	"lst": LIST,
	"tbl": TABLE,

	// Literals
	"true":  TRUE,
	"false": FALSE,
	"null":  NULL,

	// Logical operators
	"and": AND,
	"or":  OR,
	"not": NOT,

	// Comments
	"rem:":  REM,
	"note:": NOTE,
}

// LookupIdent checks if an identifier is a keyword
func LookupIdent(ident string) TokenType {
	if tok, ok := keywords[ident]; ok {
		return tok
	}
	return IDENT
}

// String returns a string representation of the token type
func (tt TokenType) String() string {
	switch tt {
	case ILLEGAL:
		return "ILLEGAL"
	case EOF:
		return "EOF"
	case NEWLINE:
		return "NEWLINE"
	case INDENT:
		return "INDENT"
	case DEDENT:
		return "DEDENT"
	case IDENT:
		return "IDENT"
	case INT:
		return "INT"
	case FLOAT:
		return "FLOAT"
	case STRING:
		return "STRING"
	case VSTRING:
		return "VSTRING"
	case TASK:
		return "TASK"
	case WITH:
		return "WITH"
	case USING:
		return "USING"
	case DELIVER:
		return "DELIVER"
	case ABORT:
		return "ABORT"
	case SWAP:
		return "SWAP"
	case VAR:
		return "VAR"
	case FXD:
		return "FXD"
	case AS:
		return "AS"
	case IF:
		return "IF"
	case THEN:
		return "THEN"
	case ELSE:
		return "ELSE"
	case CHOOSE:
		return "CHOOSE"
	case CHOICE:
		return "CHOICE"
	case DEFAULT:
		return "DEFAULT"
	case LOOP:
		return "LOOP"
	case FROM:
		return "FROM"
	case TO:
		return "TO"
	case STEP:
		return "STEP"
	case IN:
		return "IN"
	case EXIT:
		return "EXIT"
	case CONTINUE:
		return "CONTINUE"
	case ATTEMPT:
		return "ATTEMPT"
	case HANDLE:
		return "HANDLE"
	case ENSURE:
		return "ENSURE"
	case USE:
		return "USE"
	case ASSEMBLIES:
		return "ASSEMBLIES"
	case MODULES:
		return "MODULES"
	case TASKS:
		return "TASKS"
	case RECORD:
		return "RECORD"
	case BASED:
		return "BASED"
	case ON:
		return "ON"
	case INTEGER:
		return "INTEGER"
	case FLOAT_TYPE:
		return "FLOAT_TYPE"
	case STRING_TYPE:
		return "STRING_TYPE"
	case BOOLEAN:
		return "BOOLEAN"
	case LIST:
		return "LIST"
	case TABLE:
		return "TABLE"
	case OF:
		return "OF"
	case TRUE:
		return "TRUE"
	case FALSE:
		return "FALSE"
	case NULL:
		return "NULL"
	case AND:
		return "AND"
	case OR:
		return "OR"
	case NOT:
		return "NOT"
	case PLUS:
		return "PLUS"
	case MINUS:
		return "MINUS"
	case ASTERISK:
		return "ASTERISK"
	case SLASH:
		return "SLASH"
	case INTDIV:
		return "INTDIV"
	case PERCENT:
		return "PERCENT"
	case POWER:
		return "POWER"
	case EQ:
		return "EQ"
	case NEQ:
		return "NEQ"
	case LT:
		return "LT"
	case GT:
		return "GT"
	case LTE:
		return "LTE"
	case GTE:
		return "GTE"
	case ASSIGN:
		return "ASSIGN"
	case PLUS_EQ:
		return "PLUS_EQ"
	case MINUS_EQ:
		return "MINUS_EQ"
	case TIMES_EQ:
		return "TIMES_EQ"
	case DIV_EQ:
		return "DIV_EQ"
	case MOD_EQ:
		return "MOD_EQ"
	case CONCAT_EQ:
		return "CONCAT_EQ"
	case AMPERSAND:
		return "AMPERSAND"
	case LPAREN:
		return "LPAREN"
	case RPAREN:
		return "RPAREN"
	case LBRACKET:
		return "LBRACKET"
	case RBRACKET:
		return "RBRACKET"
	case LBRACE:
		return "LBRACE"
	case RBRACE:
		return "RBRACE"
	case COMMA:
		return "COMMA"
	case COLON:
		return "COLON"
	case DOT:
		return "DOT"
	case REM:
		return "REM"
	case NOTE:
		return "NOTE"
	default:
		return "UNKNOWN"
	}
}
