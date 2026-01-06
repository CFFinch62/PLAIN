package parser

import (
	"fmt"
	"plain/internal/ast"
	"plain/internal/lexer"
	"plain/internal/token"
	"strconv"
)

// Operator precedence levels (from lowest to highest)
const (
	_ int = iota
	LOWEST
	OR          // or
	AND         // and
	NOT         // not
	EQUALS      // == !=
	LESSGREATER // > < >= <=
	CONCAT      // &
	SUM         // + -
	PRODUCT     // * / // %
	POWER       // **
	PREFIX      // -x or not x
	CALL        // myFunction(x)
	INDEX       // array[index]
)

// precedences maps token types to their precedence levels
var precedences = map[token.TokenType]int{
	token.OR:        OR,
	token.AND:       AND,
	token.NOT:       NOT,
	token.EQ:        EQUALS,
	token.NEQ:       EQUALS,
	token.LT:        LESSGREATER,
	token.GT:        LESSGREATER,
	token.LTE:       LESSGREATER,
	token.GTE:       LESSGREATER,
	token.AMPERSAND: CONCAT,
	token.PLUS:      SUM,
	token.MINUS:     SUM,
	token.SLASH:     PRODUCT,
	token.ASTERISK:  PRODUCT,
	token.INTDIV:    PRODUCT,
	token.PERCENT:   PRODUCT,
	token.POWER:     POWER,
	token.LPAREN:    CALL,
	token.LBRACKET:  INDEX,
	token.DOT:       INDEX,
}

// Parser represents the parser
type Parser struct {
	l      *lexer.Lexer
	errors []string

	curToken  token.Token
	peekToken token.Token

	prefixParseFns map[token.TokenType]prefixParseFn
	infixParseFns  map[token.TokenType]infixParseFn
}

type (
	prefixParseFn func() ast.Expression
	infixParseFn  func(ast.Expression) ast.Expression
)

// New creates a new Parser
func New(l *lexer.Lexer) *Parser {
	p := &Parser{
		l:      l,
		errors: []string{},
	}

	// Register prefix parse functions
	p.prefixParseFns = make(map[token.TokenType]prefixParseFn)
	p.registerPrefix(token.IDENT, p.parseIdentifier)
	p.registerPrefix(token.INT, p.parseIntegerLiteral)
	p.registerPrefix(token.FLOAT, p.parseFloatLiteral)
	p.registerPrefix(token.STRING, p.parseStringLiteral)
	p.registerPrefix(token.VSTRING, p.parseInterpolatedString)
	p.registerPrefix(token.TRUE, p.parseBooleanLiteral)
	p.registerPrefix(token.FALSE, p.parseBooleanLiteral)
	p.registerPrefix(token.NULL, p.parseNullLiteral)
	p.registerPrefix(token.MINUS, p.parsePrefixExpression)
	p.registerPrefix(token.NOT, p.parsePrefixExpression)
	p.registerPrefix(token.LPAREN, p.parseGroupedExpression)
	p.registerPrefix(token.LBRACKET, p.parseListLiteral)
	p.registerPrefix(token.LBRACE, p.parseTableLiteral)

	// Register infix parse functions
	p.infixParseFns = make(map[token.TokenType]infixParseFn)
	p.registerInfix(token.PLUS, p.parseInfixExpression)
	p.registerInfix(token.MINUS, p.parseInfixExpression)
	p.registerInfix(token.SLASH, p.parseInfixExpression)
	p.registerInfix(token.ASTERISK, p.parseInfixExpression)
	p.registerInfix(token.INTDIV, p.parseInfixExpression)
	p.registerInfix(token.PERCENT, p.parseInfixExpression)
	p.registerInfix(token.POWER, p.parseInfixExpression)
	p.registerInfix(token.AMPERSAND, p.parseInfixExpression)
	p.registerInfix(token.EQ, p.parseInfixExpression)
	p.registerInfix(token.NEQ, p.parseInfixExpression)
	p.registerInfix(token.LT, p.parseInfixExpression)
	p.registerInfix(token.GT, p.parseInfixExpression)
	p.registerInfix(token.LTE, p.parseInfixExpression)
	p.registerInfix(token.GTE, p.parseInfixExpression)
	p.registerInfix(token.AND, p.parseInfixExpression)
	p.registerInfix(token.OR, p.parseInfixExpression)
	p.registerInfix(token.LPAREN, p.parseCallExpression)
	p.registerInfix(token.LBRACKET, p.parseIndexExpression)
	p.registerInfix(token.DOT, p.parseDotExpression)

	// Read two tokens to initialize curToken and peekToken
	p.nextToken()
	p.nextToken()

	return p
}

// Errors returns the parser errors
func (p *Parser) Errors() []string {
	return p.errors
}

func (p *Parser) peekError(t token.TokenType) {
	msg := fmt.Sprintf("Expected next token to be %s, got %s instead (line %d, column %d)",
		t, p.peekToken.Type, p.peekToken.Line, p.peekToken.Column)
	p.errors = append(p.errors, msg)
}

func (p *Parser) addError(msg string) {
	fullMsg := fmt.Sprintf("%s (line %d, column %d)",
		msg, p.curToken.Line, p.curToken.Column)
	p.errors = append(p.errors, fullMsg)
}

func (p *Parser) nextToken() {
	p.curToken = p.peekToken
	p.peekToken = p.l.NextToken()

	// Skip NEWLINE tokens in most contexts (they're handled specially in statement parsing)
	// This makes expression parsing cleaner
}

func (p *Parser) curTokenIs(t token.TokenType) bool {
	return p.curToken.Type == t
}

func (p *Parser) peekTokenIs(t token.TokenType) bool {
	return p.peekToken.Type == t
}

func (p *Parser) expectPeek(t token.TokenType) bool {
	if p.peekTokenIs(t) {
		p.nextToken()
		return true
	}
	p.peekError(t)
	return false
}

func (p *Parser) peekPrecedence() int {
	if p, ok := precedences[p.peekToken.Type]; ok {
		return p
	}
	return LOWEST
}

func (p *Parser) curPrecedence() int {
	if p, ok := precedences[p.curToken.Type]; ok {
		return p
	}
	return LOWEST
}

func (p *Parser) registerPrefix(tokenType token.TokenType, fn prefixParseFn) {
	p.prefixParseFns[tokenType] = fn
}

func (p *Parser) registerInfix(tokenType token.TokenType, fn infixParseFn) {
	p.infixParseFns[tokenType] = fn
}

// skipNewlines skips over NEWLINE tokens
func (p *Parser) skipNewlines() {
	for p.curTokenIs(token.NEWLINE) {
		p.nextToken()
	}
}

// ParseProgram parses the entire program
func (p *Parser) ParseProgram() *ast.Program {
	program := &ast.Program{}
	program.Statements = []ast.Statement{}

	for !p.curTokenIs(token.EOF) {
		// Skip newlines at the top level
		if p.curTokenIs(token.NEWLINE) {
			p.nextToken()
			continue
		}

		stmt := p.parseStatement()
		if stmt != nil {
			program.Statements = append(program.Statements, stmt)
		}
		p.nextToken()
	}

	return program
}

// parseStatement parses a statement
func (p *Parser) parseStatement() ast.Statement {
	switch p.curToken.Type {
	case token.VAR:
		return p.parseVarStatement()
	case token.FXD:
		return p.parseFxdStatement()
	case token.TASK:
		return p.parseTaskStatement()
	case token.IF:
		return p.parseIfStatement()
	case token.CHOOSE:
		return p.parseChooseStatement()
	case token.LOOP:
		return p.parseLoopStatement()
	case token.DELIVER:
		return p.parseDeliverStatement()
	case token.ABORT:
		return p.parseAbortStatement()
	case token.EXIT:
		return p.parseExitStatement()
	case token.CONTINUE:
		return p.parseContinueStatement()
	case token.ATTEMPT:
		return p.parseAttemptStatement()
	case token.RECORD:
		return p.parseRecordStatement()
	case token.USE:
		return p.parseUseStatement()
	default:
		return p.parseExpressionStatement()
	}
}

// ============================================================================
// EXPRESSION PARSING
// ============================================================================

func (p *Parser) parseExpression(precedence int) ast.Expression {
	prefix := p.prefixParseFns[p.curToken.Type]
	if prefix == nil {
		p.noPrefixParseFnError(p.curToken.Type)
		return nil
	}
	leftExp := prefix()

	for !p.peekTokenIs(token.NEWLINE) && !p.peekTokenIs(token.EOF) && precedence < p.peekPrecedence() {
		infix := p.infixParseFns[p.peekToken.Type]
		if infix == nil {
			return leftExp
		}

		p.nextToken()
		leftExp = infix(leftExp)
	}

	return leftExp
}

func (p *Parser) noPrefixParseFnError(t token.TokenType) {
	msg := fmt.Sprintf("No prefix parse function for %s found", t)
	p.addError(msg)
}

func (p *Parser) parseIdentifier() ast.Expression {
	return &ast.Identifier{Token: p.curToken, Value: p.curToken.Literal}
}

func (p *Parser) parseIntegerLiteral() ast.Expression {
	lit := &ast.IntegerLiteral{Token: p.curToken}

	value, err := strconv.ParseInt(p.curToken.Literal, 0, 64)
	if err != nil {
		msg := fmt.Sprintf("Could not parse %q as integer", p.curToken.Literal)
		p.addError(msg)
		return nil
	}

	lit.Value = value
	return lit
}

func (p *Parser) parseFloatLiteral() ast.Expression {
	lit := &ast.FloatLiteral{Token: p.curToken}

	value, err := strconv.ParseFloat(p.curToken.Literal, 64)
	if err != nil {
		msg := fmt.Sprintf("Could not parse %q as float", p.curToken.Literal)
		p.addError(msg)
		return nil
	}

	lit.Value = value
	return lit
}

func (p *Parser) parseStringLiteral() ast.Expression {
	return &ast.StringLiteral{Token: p.curToken, Value: p.curToken.Literal}
}

func (p *Parser) parseInterpolatedString() ast.Expression {
	return &ast.InterpolatedString{Token: p.curToken, Value: p.curToken.Literal}
}

func (p *Parser) parseBooleanLiteral() ast.Expression {
	return &ast.BooleanLiteral{Token: p.curToken, Value: p.curTokenIs(token.TRUE)}
}

func (p *Parser) parseNullLiteral() ast.Expression {
	return &ast.NullLiteral{Token: p.curToken}
}

func (p *Parser) parsePrefixExpression() ast.Expression {
	expression := &ast.PrefixExpression{
		Token:    p.curToken,
		Operator: p.curToken.Literal,
	}

	p.nextToken()
	expression.Right = p.parseExpression(PREFIX)

	return expression
}

func (p *Parser) parseInfixExpression(left ast.Expression) ast.Expression {
	expression := &ast.InfixExpression{
		Token:    p.curToken,
		Operator: p.curToken.Literal,
		Left:     left,
	}

	precedence := p.curPrecedence()

	// Power operator is right-associative
	if p.curTokenIs(token.POWER) {
		precedence = precedence - 1
	}

	p.nextToken()
	expression.Right = p.parseExpression(precedence)

	return expression
}

func (p *Parser) parseGroupedExpression() ast.Expression {
	p.nextToken()

	exp := p.parseExpression(LOWEST)

	if !p.expectPeek(token.RPAREN) {
		return nil
	}

	return exp
}

func (p *Parser) parseListLiteral() ast.Expression {
	list := &ast.ListLiteral{Token: p.curToken}
	list.Elements = p.parseExpressionList(token.RBRACKET)
	return list
}

func (p *Parser) parseExpressionList(end token.TokenType) []ast.Expression {
	list := []ast.Expression{}

	if p.peekTokenIs(end) {
		p.nextToken()
		return list
	}

	p.nextToken()
	list = append(list, p.parseExpression(LOWEST))

	for p.peekTokenIs(token.COMMA) {
		p.nextToken()
		p.nextToken()
		list = append(list, p.parseExpression(LOWEST))
	}

	if !p.expectPeek(end) {
		return nil
	}

	return list
}

func (p *Parser) parseTableLiteral() ast.Expression {
	table := &ast.TableLiteral{Token: p.curToken}
	table.Pairs = make(map[ast.Expression]ast.Expression)

	for !p.peekTokenIs(token.RBRACE) {
		p.nextToken()
		key := p.parseExpression(LOWEST)

		if !p.expectPeek(token.COLON) {
			return nil
		}

		p.nextToken()
		value := p.parseExpression(LOWEST)

		table.Pairs[key] = value

		if !p.peekTokenIs(token.RBRACE) && !p.expectPeek(token.COMMA) {
			return nil
		}
	}

	if !p.expectPeek(token.RBRACE) {
		return nil
	}

	return table
}

func (p *Parser) parseCallExpression(function ast.Expression) ast.Expression {
	// Check if this might be a record literal by peeking ahead
	// Record literals have the form: TypeName(field: value, ...)
	// We need to check if the first argument has a colon

	// Save current position to potentially parse as record literal
	if p.peekTokenIs(token.IDENT) {
		// Look ahead to see if there's a colon after the identifier
		// This is a simple heuristic: if we see IDENT followed by COLON, it's likely a record literal
		return p.parseCallOrRecordLiteral(function)
	}

	exp := &ast.CallExpression{Token: p.curToken, Function: function}
	exp.Arguments = p.parseExpressionList(token.RPAREN)
	return exp
}

func (p *Parser) parseCallOrRecordLiteral(function ast.Expression) ast.Expression {
	// Try to determine if this is a record literal or a function call
	// by checking if the first argument has the pattern: identifier COLON

	p.nextToken() // move to first argument

	if p.curTokenIs(token.RPAREN) {
		// Empty argument list - it's a call
		return &ast.CallExpression{
			Token:     p.curToken,
			Function:  function,
			Arguments: []ast.Expression{},
		}
	}

	// Check if current token is IDENT and peek is COLON
	if p.curTokenIs(token.IDENT) && p.peekTokenIs(token.COLON) {
		// This is a record literal
		return p.parseRecordLiteralFields(function)
	}

	// Otherwise, it's a regular call - parse first expression and continue
	firstArg := p.parseExpression(LOWEST)
	args := []ast.Expression{firstArg}

	for p.peekTokenIs(token.COMMA) {
		p.nextToken() // consume comma
		p.nextToken() // move to next expression
		args = append(args, p.parseExpression(LOWEST))
	}

	if !p.expectPeek(token.RPAREN) {
		return nil
	}

	return &ast.CallExpression{
		Token:     p.curToken,
		Function:  function,
		Arguments: args,
	}
}

func (p *Parser) parseRecordLiteralFields(typeExpr ast.Expression) ast.Expression {
	// typeExpr should be an Identifier representing the record type
	typeName, ok := typeExpr.(*ast.Identifier)
	if !ok {
		p.addError("Record literal type must be an identifier")
		return nil
	}

	lit := &ast.RecordLiteral{
		Token:  p.curToken,
		Type:   typeName,
		Fields: make(map[string]ast.Expression),
	}

	// Parse field: value pairs
	for !p.curTokenIs(token.RPAREN) && !p.curTokenIs(token.EOF) {
		if !p.curTokenIs(token.IDENT) {
			p.addError("Expected field name in record literal")
			return nil
		}

		fieldName := p.curToken.Literal

		if !p.expectPeek(token.COLON) {
			return nil
		}

		p.nextToken() // move to value expression
		value := p.parseExpression(LOWEST)

		lit.Fields[fieldName] = value

		if p.peekTokenIs(token.COMMA) {
			p.nextToken() // consume comma
			p.nextToken() // move to next field name
		} else if p.peekTokenIs(token.RPAREN) {
			break
		} else {
			p.addError("Expected comma or closing paren in record literal")
			return nil
		}
	}

	if !p.expectPeek(token.RPAREN) {
		return nil
	}

	return lit
}

func (p *Parser) parseIndexExpression(left ast.Expression) ast.Expression {
	exp := &ast.IndexExpression{Token: p.curToken, Left: left}

	p.nextToken()
	exp.Index = p.parseExpression(LOWEST)

	if !p.expectPeek(token.RBRACKET) {
		return nil
	}

	return exp
}

func (p *Parser) parseDotExpression(left ast.Expression) ast.Expression {
	exp := &ast.DotExpression{Token: p.curToken, Left: left}

	if !p.expectPeek(token.IDENT) {
		return nil
	}

	exp.Right = &ast.Identifier{Token: p.curToken, Value: p.curToken.Literal}

	return exp
}

// ============================================================================
// STATEMENT PARSING
// ============================================================================

func (p *Parser) parseExpressionStatement() ast.Statement {
	stmt := &ast.ExpressionStatement{Token: p.curToken}

	stmt.Expression = p.parseExpression(LOWEST)

	// Check if this is actually an assignment
	if p.peekTokenIs(token.ASSIGN) || p.peekTokenIs(token.PLUS_EQ) ||
		p.peekTokenIs(token.MINUS_EQ) || p.peekTokenIs(token.TIMES_EQ) ||
		p.peekTokenIs(token.DIV_EQ) || p.peekTokenIs(token.MOD_EQ) ||
		p.peekTokenIs(token.CONCAT_EQ) {
		return p.parseAssignStatement(stmt.Expression)
	}

	return stmt
}

func (p *Parser) parseAssignStatement(left ast.Expression) ast.Statement {
	stmt := &ast.AssignStatement{Name: left}

	p.nextToken()
	stmt.Token = p.curToken

	p.nextToken()
	stmt.Value = p.parseExpression(LOWEST)

	return stmt
}

func (p *Parser) parseVarStatement() ast.Statement {
	stmt := &ast.VarStatement{Token: p.curToken}

	if !p.expectPeek(token.IDENT) {
		return nil
	}

	stmt.Name = &ast.Identifier{Token: p.curToken, Value: p.curToken.Literal}

	// Check for explicit type: var name as type = value
	if p.peekTokenIs(token.AS) {
		p.nextToken() // consume 'as'
		p.nextToken()
		stmt.TypeName = p.parseTypeName()
		if stmt.TypeName == nil {
			return nil
		}
	}

	if !p.expectPeek(token.ASSIGN) {
		return nil
	}

	p.nextToken()
	stmt.Value = p.parseExpression(LOWEST)

	return stmt
}

// parseTypeName parses a type name (can be keyword like int, float, or identifier)
func (p *Parser) parseTypeName() *ast.Identifier {
	// Type names can be keywords (int, float, string, etc.) or identifiers (custom types)
	switch p.curToken.Type {
	case token.INTEGER, token.FLOAT_TYPE, token.STRING_TYPE, token.BOOLEAN,
		token.LIST, token.TABLE, token.IDENT:
		return &ast.Identifier{Token: p.curToken, Value: p.curToken.Literal}
	default:
		p.addError("Expected type name")
		return nil
	}
}

func (p *Parser) parseFxdStatement() ast.Statement {
	stmt := &ast.FxdStatement{Token: p.curToken}

	if !p.expectPeek(token.IDENT) {
		return nil
	}

	stmt.Name = &ast.Identifier{Token: p.curToken, Value: p.curToken.Literal}

	// Constants require explicit type
	if !p.expectPeek(token.AS) {
		p.addError("Constants must have explicit type (fxd name as type = value)")
		return nil
	}

	p.nextToken()
	stmt.TypeName = p.parseTypeName()
	if stmt.TypeName == nil {
		return nil
	}

	if !p.expectPeek(token.ASSIGN) {
		return nil
	}

	p.nextToken()
	stmt.Value = p.parseExpression(LOWEST)

	return stmt
}

func (p *Parser) parseDeliverStatement() ast.Statement {
	stmt := &ast.DeliverStatement{Token: p.curToken}

	p.nextToken()
	stmt.ReturnValue = p.parseExpression(LOWEST)

	return stmt
}

func (p *Parser) parseAbortStatement() ast.Statement {
	stmt := &ast.AbortStatement{Token: p.curToken}

	p.nextToken()
	stmt.Message = p.parseExpression(LOWEST)

	return stmt
}

func (p *Parser) parseExitStatement() ast.Statement {
	return &ast.ExitStatement{Token: p.curToken}
}

func (p *Parser) parseContinueStatement() ast.Statement {
	return &ast.ContinueStatement{Token: p.curToken}
}

// parseBlockStatement parses an indented block of statements
func (p *Parser) parseBlockStatement() *ast.BlockStatement {
	block := &ast.BlockStatement{Token: p.curToken}
	block.Statements = []ast.Statement{}

	// Expect NEWLINE then INDENT
	if !p.expectPeek(token.NEWLINE) {
		return nil
	}

	if !p.expectPeek(token.INDENT) {
		return nil
	}

	p.nextToken()

	for !p.curTokenIs(token.DEDENT) && !p.curTokenIs(token.EOF) {
		if p.curTokenIs(token.NEWLINE) {
			p.nextToken()
			continue
		}

		stmt := p.parseStatement()
		if stmt != nil {
			block.Statements = append(block.Statements, stmt)
		}
		p.nextToken()
	}

	return block
}
