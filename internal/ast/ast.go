package ast

import (
	"plain/internal/token"
	"strings"
)

// Node is the base interface for all AST nodes
type Node interface {
	TokenLiteral() string
	String() string
}

// Statement represents a statement node
type Statement interface {
	Node
	statementNode()
}

// Expression represents an expression node
type Expression interface {
	Node
	expressionNode()
}

// Program is the root node of the AST
type Program struct {
	Statements []Statement
}

func (p *Program) TokenLiteral() string {
	if len(p.Statements) > 0 {
		return p.Statements[0].TokenLiteral()
	}
	return ""
}

func (p *Program) String() string {
	var out strings.Builder
	for _, s := range p.Statements {
		out.WriteString(s.String())
	}
	return out.String()
}

// ============================================================================
// STATEMENTS
// ============================================================================

// VarStatement represents a variable declaration: var name = value
type VarStatement struct {
	Token    token.Token // the VAR token
	Name     *Identifier
	TypeName *Identifier // optional explicit type (as integer)
	Value    Expression
}

func (vs *VarStatement) statementNode()       {}
func (vs *VarStatement) TokenLiteral() string { return vs.Token.Literal }
func (vs *VarStatement) String() string {
	var out strings.Builder
	out.WriteString("var ")
	out.WriteString(vs.Name.String())
	if vs.TypeName != nil {
		out.WriteString(" as ")
		out.WriteString(vs.TypeName.String())
	}
	out.WriteString(" = ")
	if vs.Value != nil {
		out.WriteString(vs.Value.String())
	}
	return out.String()
}

// FxdStatement represents a constant declaration: fxd name as type = value
type FxdStatement struct {
	Token    token.Token // the FXD token
	Name     *Identifier
	TypeName *Identifier // required for constants
	Value    Expression
}

func (fs *FxdStatement) statementNode()       {}
func (fs *FxdStatement) TokenLiteral() string { return fs.Token.Literal }
func (fs *FxdStatement) String() string {
	var out strings.Builder
	out.WriteString("fxd ")
	out.WriteString(fs.Name.String())
	out.WriteString(" as ")
	out.WriteString(fs.TypeName.String())
	out.WriteString(" = ")
	if fs.Value != nil {
		out.WriteString(fs.Value.String())
	}
	return out.String()
}

// AssignStatement represents an assignment: name = value
type AssignStatement struct {
	Token token.Token // the ASSIGN token
	Name  Expression  // can be identifier or index expression
	Value Expression
}

func (as *AssignStatement) statementNode()       {}
func (as *AssignStatement) TokenLiteral() string { return as.Token.Literal }
func (as *AssignStatement) String() string {
	var out strings.Builder
	out.WriteString(as.Name.String())
	out.WriteString(" = ")
	if as.Value != nil {
		out.WriteString(as.Value.String())
	}
	return out.String()
}

// ExpressionStatement represents an expression used as a statement
type ExpressionStatement struct {
	Token      token.Token // the first token of the expression
	Expression Expression
}

func (es *ExpressionStatement) statementNode()       {}
func (es *ExpressionStatement) TokenLiteral() string { return es.Token.Literal }
func (es *ExpressionStatement) String() string {
	if es.Expression != nil {
		return es.Expression.String()
	}
	return ""
}

// DeliverStatement represents: deliver expression
type DeliverStatement struct {
	Token       token.Token // the DELIVER token
	ReturnValue Expression
}

func (ds *DeliverStatement) statementNode()       {}
func (ds *DeliverStatement) TokenLiteral() string { return ds.Token.Literal }
func (ds *DeliverStatement) String() string {
	var out strings.Builder
	out.WriteString("deliver ")
	if ds.ReturnValue != nil {
		out.WriteString(ds.ReturnValue.String())
	}
	return out.String()
}

// AbortStatement represents: abort "message"
type AbortStatement struct {
	Token   token.Token // the ABORT token
	Message Expression  // should be a string expression
}

func (as *AbortStatement) statementNode()       {}
func (as *AbortStatement) TokenLiteral() string { return as.Token.Literal }
func (as *AbortStatement) String() string {
	var out strings.Builder
	out.WriteString("abort ")
	if as.Message != nil {
		out.WriteString(as.Message.String())
	}
	return out.String()
}

// BlockStatement represents a block of statements (indented)
type BlockStatement struct {
	Token      token.Token // the token that starts the block
	Statements []Statement
}

func (bs *BlockStatement) statementNode()       {}
func (bs *BlockStatement) TokenLiteral() string { return bs.Token.Literal }
func (bs *BlockStatement) String() string {
	var out strings.Builder
	for _, s := range bs.Statements {
		out.WriteString(s.String())
		out.WriteString("\n")
	}
	return out.String()
}

// ============================================================================
// EXPRESSIONS
// ============================================================================

// Identifier represents a variable or task name
type Identifier struct {
	Token token.Token // the IDENT token
	Value string
}

func (i *Identifier) expressionNode()      {}
func (i *Identifier) TokenLiteral() string { return i.Token.Literal }
func (i *Identifier) String() string       { return i.Value }

// IntegerLiteral represents an integer value
type IntegerLiteral struct {
	Token token.Token
	Value int64
}

func (il *IntegerLiteral) expressionNode()      {}
func (il *IntegerLiteral) TokenLiteral() string { return il.Token.Literal }
func (il *IntegerLiteral) String() string       { return il.Token.Literal }

// FloatLiteral represents a floating-point value
type FloatLiteral struct {
	Token token.Token
	Value float64
}

func (fl *FloatLiteral) expressionNode()      {}
func (fl *FloatLiteral) TokenLiteral() string { return fl.Token.Literal }
func (fl *FloatLiteral) String() string       { return fl.Token.Literal }

// StringLiteral represents a string value
type StringLiteral struct {
	Token token.Token
	Value string
}

func (sl *StringLiteral) expressionNode()      {}
func (sl *StringLiteral) TokenLiteral() string { return sl.Token.Literal }
func (sl *StringLiteral) String() string       { return "\"" + sl.Value + "\"" }

// InterpolatedString represents a v"..." string with interpolation
type InterpolatedString struct {
	Token token.Token // the VSTRING token
	Value string      // the raw string with {expressions}
}

func (is *InterpolatedString) expressionNode()      {}
func (is *InterpolatedString) TokenLiteral() string { return is.Token.Literal }
func (is *InterpolatedString) String() string       { return "v\"" + is.Value + "\"" }

// BooleanLiteral represents true or false
type BooleanLiteral struct {
	Token token.Token
	Value bool
}

func (bl *BooleanLiteral) expressionNode()      {}
func (bl *BooleanLiteral) TokenLiteral() string { return bl.Token.Literal }
func (bl *BooleanLiteral) String() string       { return bl.Token.Literal }

// NullLiteral represents null
type NullLiteral struct {
	Token token.Token
}

func (nl *NullLiteral) expressionNode()      {}
func (nl *NullLiteral) TokenLiteral() string { return nl.Token.Literal }
func (nl *NullLiteral) String() string       { return "null" }

// PrefixExpression represents a prefix operator expression: -x, not x
type PrefixExpression struct {
	Token    token.Token // the operator token
	Operator string
	Right    Expression
}

func (pe *PrefixExpression) expressionNode()      {}
func (pe *PrefixExpression) TokenLiteral() string { return pe.Token.Literal }
func (pe *PrefixExpression) String() string {
	var out strings.Builder
	out.WriteString("(")
	out.WriteString(pe.Operator)
	out.WriteString(pe.Right.String())
	out.WriteString(")")
	return out.String()
}

// InfixExpression represents a binary operator expression: x + y
type InfixExpression struct {
	Token    token.Token // the operator token
	Left     Expression
	Operator string
	Right    Expression
}

func (ie *InfixExpression) expressionNode()      {}
func (ie *InfixExpression) TokenLiteral() string { return ie.Token.Literal }
func (ie *InfixExpression) String() string {
	var out strings.Builder
	out.WriteString("(")
	out.WriteString(ie.Left.String())
	out.WriteString(" " + ie.Operator + " ")
	out.WriteString(ie.Right.String())
	out.WriteString(")")
	return out.String()
}

// CallExpression represents a task call: TaskName(arg1, arg2)
type CallExpression struct {
	Token     token.Token // the '(' token
	Function  Expression  // Identifier or selector expression
	Arguments []Expression
}

func (ce *CallExpression) expressionNode()      {}
func (ce *CallExpression) TokenLiteral() string { return ce.Token.Literal }
func (ce *CallExpression) String() string {
	var out strings.Builder
	out.WriteString(ce.Function.String())
	out.WriteString("(")
	args := []string{}
	for _, a := range ce.Arguments {
		args = append(args, a.String())
	}
	out.WriteString(strings.Join(args, ", "))
	out.WriteString(")")
	return out.String()
}

// ListLiteral represents a list: [1, 2, 3]
type ListLiteral struct {
	Token    token.Token // the '[' token
	Elements []Expression
}

func (ll *ListLiteral) expressionNode()      {}
func (ll *ListLiteral) TokenLiteral() string { return ll.Token.Literal }
func (ll *ListLiteral) String() string {
	var out strings.Builder
	out.WriteString("[")
	elements := []string{}
	for _, el := range ll.Elements {
		elements = append(elements, el.String())
	}
	out.WriteString(strings.Join(elements, ", "))
	out.WriteString("]")
	return out.String()
}

// TableLiteral represents a table: {"key": value}
type TableLiteral struct {
	Token token.Token // the '{' token
	Pairs map[Expression]Expression
}

func (tl *TableLiteral) expressionNode()      {}
func (tl *TableLiteral) TokenLiteral() string { return tl.Token.Literal }
func (tl *TableLiteral) String() string {
	var out strings.Builder
	out.WriteString("{")
	pairs := []string{}
	for key, value := range tl.Pairs {
		pairs = append(pairs, key.String()+": "+value.String())
	}
	out.WriteString(strings.Join(pairs, ", "))
	out.WriteString("}")
	return out.String()
}

// IndexExpression represents indexing: array[index] or table[key]
type IndexExpression struct {
	Token token.Token // the '[' token
	Left  Expression  // the array or table
	Index Expression  // the index or key
}

func (ie *IndexExpression) expressionNode()      {}
func (ie *IndexExpression) TokenLiteral() string { return ie.Token.Literal }
func (ie *IndexExpression) String() string {
	var out strings.Builder
	out.WriteString("(")
	out.WriteString(ie.Left.String())
	out.WriteString("[")
	out.WriteString(ie.Index.String())
	out.WriteString("])")
	return out.String()
}

// DotExpression represents member access: object.field
type DotExpression struct {
	Token token.Token // the '.' token
	Left  Expression  // the object
	Right *Identifier // the field name
}

func (de *DotExpression) expressionNode()      {}
func (de *DotExpression) TokenLiteral() string { return de.Token.Literal }
func (de *DotExpression) String() string {
	var out strings.Builder
	// Handle case where Left is nil (simple identifier converted to DotExpression)
	if de.Left != nil {
		out.WriteString(de.Left.String())
		out.WriteString(".")
	}
	out.WriteString(de.Right.String())
	return out.String()
}

// ============================================================================
// CONTROL FLOW STATEMENTS
// ============================================================================

// IfStatement represents: if condition ... else ...
type IfStatement struct {
	Token       token.Token // the IF token
	Condition   Expression
	Consequence *BlockStatement
	Alternative *BlockStatement // can be nil
}

func (is *IfStatement) statementNode()       {}
func (is *IfStatement) TokenLiteral() string { return is.Token.Literal }
func (is *IfStatement) String() string {
	var out strings.Builder
	out.WriteString("if ")
	out.WriteString(is.Condition.String())
	out.WriteString(" ")
	out.WriteString(is.Consequence.String())
	if is.Alternative != nil {
		out.WriteString("else ")
		out.WriteString(is.Alternative.String())
	}
	return out.String()
}

// ChooseStatement represents: choose expr ... choice val ... default ...
type ChooseStatement struct {
	Token   token.Token // the CHOOSE token
	Value   Expression
	Choices []*ChoiceClause
	Default *BlockStatement // can be nil
}

type ChoiceClause struct {
	Token token.Token // the CHOICE token
	Value Expression
	Body  *BlockStatement
}

func (cs *ChooseStatement) statementNode()       {}
func (cs *ChooseStatement) TokenLiteral() string { return cs.Token.Literal }
func (cs *ChooseStatement) String() string {
	var out strings.Builder
	out.WriteString("choose ")
	out.WriteString(cs.Value.String())
	out.WriteString("\n")
	for _, choice := range cs.Choices {
		out.WriteString("  choice ")
		out.WriteString(choice.Value.String())
		out.WriteString("\n")
		out.WriteString(choice.Body.String())
	}
	if cs.Default != nil {
		out.WriteString("  default\n")
		out.WriteString(cs.Default.String())
	}
	return out.String()
}

// LoopStatement represents all loop variants
type LoopStatement struct {
	Token     token.Token // the LOOP token
	Condition Expression  // for conditional loop (while-style)
	Variable  *Identifier // for counting and iteration loops
	Start     Expression  // for counting loop (from)
	End       Expression  // for counting loop (to)
	Step      Expression  // for counting loop (step) - optional
	Iterable  Expression  // for iteration loop (in)
	Body      *BlockStatement
}

func (ls *LoopStatement) statementNode()       {}
func (ls *LoopStatement) TokenLiteral() string { return ls.Token.Literal }
func (ls *LoopStatement) String() string {
	var out strings.Builder
	out.WriteString("loop")
	if ls.Condition != nil {
		out.WriteString(" ")
		out.WriteString(ls.Condition.String())
	} else if ls.Variable != nil && ls.Start != nil && ls.End != nil {
		out.WriteString(" ")
		out.WriteString(ls.Variable.String())
		out.WriteString(" from ")
		out.WriteString(ls.Start.String())
		out.WriteString(" to ")
		out.WriteString(ls.End.String())
		if ls.Step != nil {
			out.WriteString(" step ")
			out.WriteString(ls.Step.String())
		}
	} else if ls.Variable != nil && ls.Iterable != nil {
		out.WriteString(" ")
		out.WriteString(ls.Variable.String())
		out.WriteString(" in ")
		out.WriteString(ls.Iterable.String())
	}
	out.WriteString("\n")
	out.WriteString(ls.Body.String())
	return out.String()
}

// ExitStatement represents: exit
type ExitStatement struct {
	Token token.Token // the EXIT token
}

func (es *ExitStatement) statementNode()       {}
func (es *ExitStatement) TokenLiteral() string { return es.Token.Literal }
func (es *ExitStatement) String() string       { return "exit" }

// ContinueStatement represents: continue
type ContinueStatement struct {
	Token token.Token // the CONTINUE token
}

func (cs *ContinueStatement) statementNode()       {}
func (cs *ContinueStatement) TokenLiteral() string { return cs.Token.Literal }
func (cs *ContinueStatement) String() string       { return "continue" }

// ============================================================================
// TASK DEFINITIONS
// ============================================================================

// TaskStatement represents a task definition
type TaskStatement struct {
	Token      token.Token // the TASK token
	Name       *Identifier
	Parameters []*Identifier // task parameters
	IsFunction bool          // true if using 'using', false if 'with' or no params
	Body       *BlockStatement
}

func (ts *TaskStatement) statementNode()       {}
func (ts *TaskStatement) TokenLiteral() string { return ts.Token.Literal }
func (ts *TaskStatement) String() string {
	var out strings.Builder
	out.WriteString("task ")
	out.WriteString(ts.Name.String())
	if len(ts.Parameters) > 0 {
		if ts.IsFunction {
			out.WriteString(" using (")
		} else {
			out.WriteString(" with (")
		}
		params := []string{}
		for _, p := range ts.Parameters {
			params = append(params, p.String())
		}
		out.WriteString(strings.Join(params, ", "))
		out.WriteString(")")
	} else {
		out.WriteString("()")
	}
	out.WriteString("\n")
	out.WriteString(ts.Body.String())
	return out.String()
}

// ============================================================================
// ERROR HANDLING
// ============================================================================

// AttemptStatement represents: attempt ... handle ... ensure ...
type AttemptStatement struct {
	Token    token.Token // the ATTEMPT token
	Body     *BlockStatement
	Handlers []*HandleClause
	Ensure   *BlockStatement // can be nil
}

type HandleClause struct {
	Token     token.Token // the HANDLE token
	Pattern   Expression  // can be string literal or identifier
	ErrorName *Identifier // optional error variable name
	Body      *BlockStatement
}

func (as *AttemptStatement) statementNode()       {}
func (as *AttemptStatement) TokenLiteral() string { return as.Token.Literal }
func (as *AttemptStatement) String() string {
	var out strings.Builder
	out.WriteString("attempt\n")
	out.WriteString(as.Body.String())
	for _, handler := range as.Handlers {
		out.WriteString("handle ")
		if handler.Pattern != nil {
			out.WriteString(handler.Pattern.String())
		}
		if handler.ErrorName != nil {
			out.WriteString(" ")
			out.WriteString(handler.ErrorName.String())
		}
		out.WriteString("\n")
		out.WriteString(handler.Body.String())
	}
	if as.Ensure != nil {
		out.WriteString("ensure\n")
		out.WriteString(as.Ensure.String())
	}
	return out.String()
}

// ============================================================================
// RECORDS
// ============================================================================

// RecordStatement represents a record definition
type RecordStatement struct {
	Token   token.Token // the RECORD token
	Name    *Identifier
	Fields  []*RecordField
	BasedOn []*Identifier // records to inherit from with 'based on'
	With    []*Identifier // records to include with 'with'
}

type RecordField struct {
	Name         *Identifier
	TypeName     *Identifier
	DefaultValue Expression // can be nil for required fields
}

func (rs *RecordStatement) statementNode()       {}
func (rs *RecordStatement) TokenLiteral() string { return rs.Token.Literal }
func (rs *RecordStatement) String() string {
	var out strings.Builder
	out.WriteString("record ")
	out.WriteString(rs.Name.String())
	out.WriteString(":\n")

	for _, based := range rs.BasedOn {
		out.WriteString("  based on ")
		out.WriteString(based.String())
		out.WriteString("\n")
	}

	for _, with := range rs.With {
		out.WriteString("  with ")
		out.WriteString(with.String())
		out.WriteString("\n")
	}

	for _, field := range rs.Fields {
		out.WriteString("  ")
		out.WriteString(field.Name.String())
		out.WriteString(" as ")
		out.WriteString(field.TypeName.String())
		if field.DefaultValue != nil {
			out.WriteString(" = ")
			out.WriteString(field.DefaultValue.String())
		}
		out.WriteString("\n")
	}
	return out.String()
}

// RecordLiteral represents creating a record instance: Person(name: "Chuck", age: 63)
type RecordLiteral struct {
	Token  token.Token           // the '(' token
	Type   *Identifier           // the record type name
	Fields map[string]Expression // field name -> value
}

func (rl *RecordLiteral) expressionNode()      {}
func (rl *RecordLiteral) TokenLiteral() string { return rl.Token.Literal }
func (rl *RecordLiteral) String() string {
	var out strings.Builder
	out.WriteString(rl.Type.String())
	out.WriteString("(")
	fields := []string{}
	for name, value := range rl.Fields {
		fields = append(fields, name+": "+value.String())
	}
	out.WriteString(strings.Join(fields, ", "))
	out.WriteString(")")
	return out.String()
}

// ============================================================================
// IMPORTS
// ============================================================================

// UseStatement represents the use: block for imports
type UseStatement struct {
	Token      token.Token      // the USE token
	Assemblies []*DotExpression // can be simple or dotted (System.Collections)
	Modules    []*DotExpression // can be simple or dotted (io.files)
	Tasks      []*DotExpression // fully qualified task names
}

func (us *UseStatement) statementNode()       {}
func (us *UseStatement) TokenLiteral() string { return us.Token.Literal }
func (us *UseStatement) String() string {
	var out strings.Builder
	out.WriteString("use:\n")

	if len(us.Assemblies) > 0 {
		out.WriteString("  assemblies:\n")
		for _, asm := range us.Assemblies {
			out.WriteString("    ")
			out.WriteString(asm.String())
			out.WriteString("\n")
		}
	}

	if len(us.Modules) > 0 {
		out.WriteString("  modules:\n")
		for _, mod := range us.Modules {
			out.WriteString("    ")
			out.WriteString(mod.String())
			out.WriteString("\n")
		}
	}

	if len(us.Tasks) > 0 {
		out.WriteString("  tasks:\n")
		for _, task := range us.Tasks {
			out.WriteString("    ")
			out.WriteString(task.String())
			out.WriteString("\n")
		}
	}

	return out.String()
}
