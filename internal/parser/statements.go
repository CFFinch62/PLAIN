package parser

import (
	"plain/internal/ast"
	"plain/internal/token"
)

// parseIfStatement parses: if condition ... else ... or if condition then statement
func (p *Parser) parseIfStatement() ast.Statement {
	stmt := &ast.IfStatement{Token: p.curToken}

	p.nextToken()
	stmt.Condition = p.parseExpression(LOWEST)

	// Check for single-line form: if condition then statement
	if p.peekTokenIs(token.THEN) {
		p.nextToken() // consume THEN
		p.nextToken() // move to statement

		// Parse a single statement and wrap it in a block
		singleStmt := p.parseStatement()
		if singleStmt == nil {
			return nil
		}
		stmt.Consequence = &ast.BlockStatement{
			Statements: []ast.Statement{singleStmt},
		}

		// Check for single-line else: else statement
		if p.peekTokenIs(token.ELSE) {
			p.nextToken() // consume ELSE
			p.nextToken() // move to statement

			singleElse := p.parseStatement()
			if singleElse == nil {
				return nil
			}
			stmt.Alternative = &ast.BlockStatement{
				Statements: []ast.Statement{singleElse},
			}
		}

		return stmt
	}

	// Block form: if condition\n    statements
	stmt.Consequence = p.parseBlockStatement()
	if stmt.Consequence == nil {
		return nil
	}

	// After parseBlockStatement, we're at DEDENT
	// Check for else clause
	if p.peekTokenIs(token.ELSE) {
		p.nextToken() // move to ELSE

		stmt.Alternative = p.parseBlockStatement()
		if stmt.Alternative == nil {
			return nil
		}
	}

	return stmt
}

// parseChooseStatement parses: choose expr ... choice val ... default ...
func (p *Parser) parseChooseStatement() ast.Statement {
	stmt := &ast.ChooseStatement{Token: p.curToken}

	p.nextToken()
	stmt.Value = p.parseExpression(LOWEST)

	// Expect NEWLINE then INDENT
	if !p.expectPeek(token.NEWLINE) {
		return nil
	}

	if !p.expectPeek(token.INDENT) {
		return nil
	}

	p.nextToken()

	// Parse choice clauses
	for p.curTokenIs(token.CHOICE) {
		choice := &ast.ChoiceClause{Token: p.curToken}

		p.nextToken()
		choice.Value = p.parseExpression(LOWEST)

		choice.Body = p.parseBlockStatement()
		if choice.Body == nil {
			return nil
		}

		stmt.Choices = append(stmt.Choices, choice)

		// Move past DEDENT
		if p.curTokenIs(token.DEDENT) {
			p.nextToken()
		}
	}

	// Check for default clause
	if p.curTokenIs(token.DEFAULT) {
		stmt.Default = p.parseBlockStatement()
		if stmt.Default == nil {
			return nil
		}

		// Move past DEDENT
		if p.curTokenIs(token.DEDENT) {
			p.nextToken()
		}
	}

	return stmt
}

// parseLoopStatement parses all loop variants
func (p *Parser) parseLoopStatement() ast.Statement {
	stmt := &ast.LoopStatement{Token: p.curToken}

	// Check what kind of loop this is
	if p.peekTokenIs(token.NEWLINE) || p.peekTokenIs(token.INDENT) {
		// Infinite loop: loop
		stmt.Body = p.parseBlockStatement()
		return stmt
	}

	p.nextToken()

	// Check for counting loop: loop i from 1 to 10 [step 2]
	if p.peekTokenIs(token.FROM) {
		stmt.Variable = &ast.Identifier{Token: p.curToken, Value: p.curToken.Literal}
		p.nextToken() // consume FROM

		p.nextToken()
		stmt.Start = p.parseExpression(LOWEST)

		if !p.expectPeek(token.TO) {
			return nil
		}

		p.nextToken()
		stmt.End = p.parseExpression(LOWEST)

		// Check for optional step
		if p.peekTokenIs(token.STEP) {
			p.nextToken() // consume STEP
			p.nextToken()
			stmt.Step = p.parseExpression(LOWEST)
		}

		stmt.Body = p.parseBlockStatement()
		return stmt
	}

	// Check for iteration loop: loop item in collection
	if p.peekTokenIs(token.IN) {
		stmt.Variable = &ast.Identifier{Token: p.curToken, Value: p.curToken.Literal}
		p.nextToken() // consume IN

		p.nextToken()
		stmt.Iterable = p.parseExpression(LOWEST)

		stmt.Body = p.parseBlockStatement()
		return stmt
	}

	// Conditional loop: loop condition
	stmt.Condition = p.parseExpression(LOWEST)
	stmt.Body = p.parseBlockStatement()

	return stmt
}

// parseTaskStatement parses task definitions
func (p *Parser) parseTaskStatement() ast.Statement {
	stmt := &ast.TaskStatement{Token: p.curToken}

	if !p.expectPeek(token.IDENT) {
		return nil
	}

	stmt.Name = &ast.Identifier{Token: p.curToken, Value: p.curToken.Literal}

	// Check for parameters
	if p.peekTokenIs(token.WITH) {
		p.nextToken() // consume WITH
		stmt.IsFunction = false
		stmt.Parameters = p.parseTaskParameters()
	} else if p.peekTokenIs(token.USING) {
		p.nextToken() // consume USING
		stmt.IsFunction = true
		stmt.Parameters = p.parseTaskParameters()
	} else if p.peekTokenIs(token.LPAREN) {
		// No parameters: task Name()
		p.nextToken() // consume LPAREN
		if !p.expectPeek(token.RPAREN) {
			return nil
		}
	}

	stmt.Body = p.parseBlockStatement()
	if stmt.Body == nil {
		return nil
	}

	return stmt
}

func (p *Parser) parseTaskParameters() []*ast.Identifier {
	params := []*ast.Identifier{}

	if !p.expectPeek(token.LPAREN) {
		return nil
	}

	if p.peekTokenIs(token.RPAREN) {
		p.nextToken()
		return params
	}

	p.nextToken()
	param := &ast.Identifier{Token: p.curToken, Value: p.curToken.Literal}
	params = append(params, param)

	for p.peekTokenIs(token.COMMA) {
		p.nextToken()
		p.nextToken()
		param := &ast.Identifier{Token: p.curToken, Value: p.curToken.Literal}
		params = append(params, param)
	}

	if !p.expectPeek(token.RPAREN) {
		return nil
	}

	return params
}

// parseAttemptStatement parses: attempt ... handle ... ensure ...
func (p *Parser) parseAttemptStatement() ast.Statement {
	stmt := &ast.AttemptStatement{Token: p.curToken}

	stmt.Body = p.parseBlockStatement()
	if stmt.Body == nil {
		return nil
	}

	// After parseBlockStatement, we're at DEDENT
	// Don't consume it - let parseBlockStatement in the caller handle it
	// This matches the behavior of parseIfStatement

	// Parse handle clauses
	for p.peekTokenIs(token.HANDLE) {
		p.nextToken() // move to HANDLE
		handler := &ast.HandleClause{Token: p.curToken}

		// Check if there's a pattern (string literal or identifier)
		// If peekToken is not NEWLINE, there's a pattern
		if !p.peekTokenIs(token.NEWLINE) {
			p.nextToken()
			handler.Pattern = p.parseExpression(LOWEST)

			// Check for error variable name: handle err as string
			if p.peekTokenIs(token.AS) {
				p.nextToken() // consume AS
				p.nextToken() // move to type

				// Accept type keywords (string, integer, etc.) or IDENT
				if p.isTypeKeyword() || p.curTokenIs(token.IDENT) {
					// The pattern becomes the error name
					if ident, ok := handler.Pattern.(*ast.Identifier); ok {
						handler.ErrorName = ident
						handler.Pattern = nil
					}
				} else {
					p.addError("Expected type name after 'as' in handle clause")
					return nil
				}
			}
		}

		// Now curToken should be positioned before NEWLINE (either at HANDLE or at end of pattern)
		handler.Body = p.parseBlockStatement()
		if handler.Body == nil {
			return nil
		}

		stmt.Handlers = append(stmt.Handlers, handler)

		// After parseBlockStatement, we're at DEDENT
		// Don't consume it - check for more handlers or ensure by peeking
	}

	// Check for ensure clause
	if p.peekTokenIs(token.ENSURE) {
		p.nextToken() // move to ENSURE
		stmt.Ensure = p.parseBlockStatement()
		if stmt.Ensure == nil {
			return nil
		}

		// After parseBlockStatement, we're at DEDENT
		// Don't consume it - let the caller handle it
	}

	return stmt
}

// parseRecordStatement parses record definitions
func (p *Parser) parseRecordStatement() ast.Statement {
	stmt := &ast.RecordStatement{Token: p.curToken}

	if !p.expectPeek(token.IDENT) {
		return nil
	}

	stmt.Name = &ast.Identifier{Token: p.curToken, Value: p.curToken.Literal}

	if !p.expectPeek(token.COLON) {
		return nil
	}

	// Expect NEWLINE then INDENT
	if !p.expectPeek(token.NEWLINE) {
		return nil
	}

	if !p.expectPeek(token.INDENT) {
		return nil
	}

	p.nextToken()

	// Parse record body (based on, with, fields)
	for !p.curTokenIs(token.DEDENT) && !p.curTokenIs(token.EOF) {
		if p.curTokenIs(token.NEWLINE) {
			p.nextToken()
			continue
		}

		if p.curTokenIs(token.BASED) {
			// based on RecordName
			if !p.expectPeek(token.ON) {
				return nil
			}

			if !p.expectPeek(token.IDENT) {
				return nil
			}

			basedOn := &ast.Identifier{Token: p.curToken, Value: p.curToken.Literal}
			stmt.BasedOn = append(stmt.BasedOn, basedOn)
			p.nextToken()
			continue
		}

		if p.curTokenIs(token.WITH) {
			// with RecordName
			if !p.expectPeek(token.IDENT) {
				return nil
			}

			with := &ast.Identifier{Token: p.curToken, Value: p.curToken.Literal}
			stmt.With = append(stmt.With, with)
			p.nextToken()
			continue
		}

		// Parse field: name as type = defaultValue
		if p.curTokenIs(token.IDENT) {
			field := &ast.RecordField{}
			field.Name = &ast.Identifier{Token: p.curToken, Value: p.curToken.Literal}

			if !p.expectPeek(token.AS) {
				return nil
			}

			p.nextToken()
			field.TypeName = p.parseTypeName()
			if field.TypeName == nil {
				return nil
			}

			// Check for default value
			if p.peekTokenIs(token.ASSIGN) {
				p.nextToken() // consume ASSIGN
				p.nextToken()
				field.DefaultValue = p.parseExpression(LOWEST)
			}

			stmt.Fields = append(stmt.Fields, field)
			p.nextToken()
			continue
		}

		p.nextToken()
	}

	return stmt
}

// parseUseStatement parses import statements
func (p *Parser) parseUseStatement() ast.Statement {
	stmt := &ast.UseStatement{Token: p.curToken}

	// Expect NEWLINE then INDENT
	if !p.expectPeek(token.NEWLINE) {
		return nil
	}

	if !p.expectPeek(token.INDENT) {
		return nil
	}

	p.nextToken()

	// Parse use: block sections
	for !p.curTokenIs(token.DEDENT) && !p.curTokenIs(token.EOF) {
		if p.curTokenIs(token.NEWLINE) {
			p.nextToken()
			continue
		}

		if p.curTokenIs(token.ASSEMBLIES) {
			// assemblies: section
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

				if p.curTokenIs(token.IDENT) {
					// Parse assembly path (can be dotted: System.Collections)
					asm := p.parseExpression(LOWEST)
					if dotExpr, ok := asm.(*ast.DotExpression); ok {
						stmt.Assemblies = append(stmt.Assemblies, dotExpr)
					} else if ident, ok := asm.(*ast.Identifier); ok {
						// Convert simple identifier to DotExpression for consistency
						dotExpr := &ast.DotExpression{
							Token: ident.Token,
							Left:  nil,
							Right: ident,
						}
						stmt.Assemblies = append(stmt.Assemblies, dotExpr)
					}
				}

				p.nextToken()
			}

			p.nextToken() // move past DEDENT
			continue
		}

		if p.curTokenIs(token.MODULES) {
			// modules: section
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

				// Module names can be identifiers or type keywords (e.g., string.utils)
				if p.curTokenIs(token.IDENT) || p.isTypeKeyword() {
					// Parse module path (can be dotted: io.files, string.utils)
					mod := p.parseModulePath()
					if mod != nil {
						stmt.Modules = append(stmt.Modules, mod)
					}
				}

				p.nextToken()
			}

			p.nextToken() // move past DEDENT
			continue
		}

		if p.curTokenIs(token.TASKS) {
			// tasks: section
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

				if p.curTokenIs(token.IDENT) {
					// Parse task path (fully qualified: io.files.ReadBinary)
					task := p.parseExpression(LOWEST)
					if dotExpr, ok := task.(*ast.DotExpression); ok {
						stmt.Tasks = append(stmt.Tasks, dotExpr)
					}
				}

				p.nextToken()
			}

			p.nextToken() // move past DEDENT
			continue
		}

		p.nextToken()
	}

	return stmt
}

// isTypeKeyword checks if current token is a type keyword
func (p *Parser) isTypeKeyword() bool {
	return p.curTokenIs(token.INTEGER) ||
		p.curTokenIs(token.FLOAT_TYPE) ||
		p.curTokenIs(token.STRING_TYPE) ||
		p.curTokenIs(token.BOOLEAN) ||
		p.curTokenIs(token.LIST) ||
		p.curTokenIs(token.TABLE)
}

// parseModulePath parses a module path that can start with a type keyword or identifier
// and can be dotted (e.g., io.files, string.utils)
func (p *Parser) parseModulePath() *ast.DotExpression {
	// Create an identifier from the current token (even if it's a type keyword)
	firstIdent := &ast.Identifier{
		Token: p.curToken,
		Value: p.curToken.Literal,
	}

	// Check if there's a dot following
	if !p.peekTokenIs(token.DOT) {
		// Simple module name - convert to DotExpression for consistency
		return &ast.DotExpression{
			Token: firstIdent.Token,
			Left:  nil,
			Right: firstIdent,
		}
	}

	// Build dotted path
	left := ast.Expression(firstIdent)
	for p.peekTokenIs(token.DOT) {
		p.nextToken() // consume DOT
		p.nextToken() // move to next part

		right := &ast.Identifier{
			Token: p.curToken,
			Value: p.curToken.Literal,
		}

		left = &ast.DotExpression{
			Token: p.curToken,
			Left:  left,
			Right: right,
		}
	}

	return left.(*ast.DotExpression)
}
