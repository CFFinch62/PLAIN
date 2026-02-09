package lexer

import (
	"plain/internal/token"
)

// Lexer represents the lexical analyzer
type Lexer struct {
	input        string
	position     int  // current position in input (points to current char)
	readPosition int  // current reading position in input (after current char)
	ch           byte // current char under examination
	line         int  // current line number
	column       int  // current column number

	// Indentation tracking
	indentStack   []int         // stack of indentation levels
	pendingTokens []token.Token // tokens to emit before reading next
}

// New creates a new Lexer instance
func New(input string) *Lexer {
	l := &Lexer{
		input:         input,
		line:          1,
		column:        0,
		indentStack:   []int{0}, // start with base indentation level
		pendingTokens: []token.Token{},
	}
	l.readChar() // initialize first character

	// Handle indentation at start of file
	l.handleIndentation()

	return l
}

// readChar advances the position and reads the next character
func (l *Lexer) readChar() {
	if l.readPosition >= len(l.input) {
		l.ch = 0 // ASCII code for "NUL" - signifies EOF
	} else {
		l.ch = l.input[l.readPosition]
	}
	l.position = l.readPosition
	l.readPosition++
	l.column++
}

// peekChar returns the next character without advancing position
func (l *Lexer) peekChar() byte {
	if l.readPosition >= len(l.input) {
		return 0
	}
	return l.input[l.readPosition]
}

// peekCharAt returns the character at offset positions ahead
func (l *Lexer) peekCharAt(offset int) byte {
	pos := l.readPosition + offset - 1
	if pos >= len(l.input) {
		return 0
	}
	return l.input[pos]
}

// skipWhitespace skips spaces and tabs (but not newlines)
func (l *Lexer) skipWhitespace() {
	for l.ch == ' ' || l.ch == '\t' || l.ch == '\r' {
		l.readChar()
	}
}

// readIdentifier reads an identifier or keyword
func (l *Lexer) readIdentifier() string {
	position := l.position

	// First character must be letter or underscore
	if isLetter(l.ch) {
		l.readChar()
	}

	// Subsequent characters can be letters, digits, or underscores
	for isLetter(l.ch) || isDigit(l.ch) {
		l.readChar()
	}

	return l.input[position:l.position]
}

// readNumber reads a number (integer or float)
func (l *Lexer) readNumber() (string, token.TokenType) {
	position := l.position
	tokenType := token.INT

	// Read integer part
	for isDigit(l.ch) {
		l.readChar()
	}

	// Check for decimal point
	if l.ch == '.' && isDigit(l.peekChar()) {
		tokenType = token.FLOAT
		l.readChar() // consume '.'

		// Read fractional part
		for isDigit(l.ch) {
			l.readChar()
		}
	}

	// Check for scientific notation (e or E)
	if l.ch == 'e' || l.ch == 'E' {
		tokenType = token.FLOAT
		l.readChar() // consume 'e' or 'E'

		// Optional sign
		if l.ch == '+' || l.ch == '-' {
			l.readChar()
		}

		// Read exponent
		for isDigit(l.ch) {
			l.readChar()
		}
	}

	return l.input[position:l.position], tokenType
}

// isLetter checks if a character is a letter or underscore
func isLetter(ch byte) bool {
	return 'a' <= ch && ch <= 'z' || 'A' <= ch && ch <= 'Z' || ch == '_'
}

// isDigit checks if a character is a digit
func isDigit(ch byte) bool {
	return '0' <= ch && ch <= '9'
}

// newToken creates a new token
func (l *Lexer) newToken(tokenType token.TokenType, literal string) token.Token {
	return token.Token{
		Type:    tokenType,
		Literal: literal,
		Line:    l.line,
		Column:  l.column - len(literal),
	}
}

// makeToken creates a token from the current character
func (l *Lexer) makeToken(tokenType token.TokenType) token.Token {
	return l.newToken(tokenType, string(l.ch))
}

// readString reads a string literal
func (l *Lexer) readString() (string, bool) {
	var result []byte
	l.readChar() // skip opening quote

	for {
		if l.ch == 0 {
			// Unterminated string
			return "", false
		}

		if l.ch == '"' {
			break
		}

		// Handle escape sequences
		if l.ch == '\\' {
			l.readChar() // move to escaped character

			switch l.ch {
			case 'n':
				result = append(result, '\n')
			case 't':
				result = append(result, '\t')
			case 'r':
				result = append(result, '\r')
			case '\\':
				result = append(result, '\\')
			case '"':
				result = append(result, '"')
			case '\'':
				result = append(result, '\'')
			default:
				// Unknown escape sequence - keep the backslash and character
				result = append(result, '\\')
				result = append(result, l.ch)
			}
			l.readChar()
			continue
		}

		// Track newlines in strings (for multi-line strings)
		if l.ch == '\n' {
			l.line++
			l.column = 0
		}

		result = append(result, l.ch)
		l.readChar()
	}

	return string(result), true
}

// readInterpolatedString reads a v"..." interpolated string
func (l *Lexer) readInterpolatedString() (string, bool) {
	// For now, we'll read it as a string and let the parser handle interpolation
	// The lexer just needs to recognize it as a VSTRING token
	return l.readString()
}

// skipLineComment skips a rem: comment (single line)
func (l *Lexer) skipLineComment() {
	// Skip until end of line or EOF
	for l.ch != '\n' && l.ch != 0 {
		l.readChar()
	}

	// Also consume the newline if present
	if l.ch == '\n' {
		l.readChar()
		l.line++
		l.column = 0
		// Handle indentation on the next line
		l.handleIndentation()
	}
}

// skipBlockComment skips a note: comment (multi-line, indentation-based)
func (l *Lexer) skipBlockComment() {
	// note: comments continue until we reach a line with same or less indentation
	// For now, we'll implement a simple version that skips until dedent
	// A more sophisticated version would track indentation properly

	startColumn := l.column

	// Skip to end of current line
	for l.ch != '\n' && l.ch != 0 {
		l.readChar()
	}

	if l.ch == '\n' {
		l.readChar()
		l.line++
		l.column = 0
	}

	// Skip lines that are more indented than the note: line
	for l.ch != 0 {
		// Count indentation of current line
		indent := 0
		for l.ch == ' ' || l.ch == '\t' {
			if l.ch == ' ' {
				indent++
			} else {
				indent += 4 // tab = 4 spaces
			}
			l.readChar()
		}

		// If we hit a blank line, skip it
		if l.ch == '\n' {
			l.readChar()
			l.line++
			l.column = 0
			continue
		}

		// If indentation is less than or equal to start, we're done
		if indent <= startColumn {
			break
		}

		// Skip rest of this line
		for l.ch != '\n' && l.ch != 0 {
			l.readChar()
		}

		if l.ch == '\n' {
			l.readChar()
			l.line++
			l.column = 0
		}
	}
}

// handleIndentation processes indentation at the start of a line
// Returns INDENT, DEDENT, or continues to next token
func (l *Lexer) handleIndentation() {
	// Count spaces at the beginning of the line
	indent := 0
	for l.ch == ' ' || l.ch == '\t' {
		if l.ch == ' ' {
			indent++
		} else {
			indent += 4 // tab = 4 spaces
		}
		l.readChar()
	}

	// Skip blank lines and lines with only comments
	if l.ch == '\n' || l.ch == 0 {
		return
	}

	currentIndent := l.indentStack[len(l.indentStack)-1]

	if indent > currentIndent {
		// Increased indentation - emit INDENT
		l.indentStack = append(l.indentStack, indent)
		l.pendingTokens = append(l.pendingTokens, l.newToken(token.INDENT, ""))
	} else if indent < currentIndent {
		// Decreased indentation - emit DEDENT(s)
		for len(l.indentStack) > 0 && l.indentStack[len(l.indentStack)-1] > indent {
			l.indentStack = l.indentStack[:len(l.indentStack)-1]
			l.pendingTokens = append(l.pendingTokens, l.newToken(token.DEDENT, ""))
		}

		// Check for indentation error
		if len(l.indentStack) == 0 || l.indentStack[len(l.indentStack)-1] != indent {
			// Indentation doesn't match any previous level
			l.pendingTokens = append(l.pendingTokens, l.newToken(token.ILLEGAL, "invalid indentation"))
		}
	}
	// If indent == currentIndent, no change needed
}

// NextToken returns the next token from the input
func (l *Lexer) NextToken() token.Token {
	// Return pending tokens first (for DEDENT handling)
	if len(l.pendingTokens) > 0 {
		tok := l.pendingTokens[0]
		l.pendingTokens = l.pendingTokens[1:]
		return tok
	}

	var tok token.Token

	l.skipWhitespace()

	switch l.ch {
	case '\n':
		tok = l.makeToken(token.NEWLINE)
		l.readChar()
		l.line++
		l.column = 0

		// Handle indentation on the next line
		l.handleIndentation()

		// If we have pending tokens (INDENT/DEDENT), return the NEWLINE
		// and the pending tokens will be returned on subsequent calls
		if len(l.pendingTokens) > 0 {
			return tok
		}

	case '+':
		if l.peekChar() == '=' {
			ch := l.ch
			l.readChar()
			tok = l.newToken(token.PLUS_EQ, string(ch)+string(l.ch))
			l.readChar()
		} else {
			tok = l.makeToken(token.PLUS)
			l.readChar()
		}

	case '-':
		if l.peekChar() == '=' {
			ch := l.ch
			l.readChar()
			tok = l.newToken(token.MINUS_EQ, string(ch)+string(l.ch))
			l.readChar()
		} else {
			tok = l.makeToken(token.MINUS)
			l.readChar()
		}

	case '*':
		if l.peekChar() == '*' {
			ch := l.ch
			l.readChar()
			tok = l.newToken(token.POWER, string(ch)+string(l.ch))
			l.readChar()
		} else if l.peekChar() == '=' {
			ch := l.ch
			l.readChar()
			tok = l.newToken(token.TIMES_EQ, string(ch)+string(l.ch))
			l.readChar()
		} else {
			tok = l.makeToken(token.ASTERISK)
			l.readChar()
		}

	case '/':
		if l.peekChar() == '/' {
			ch := l.ch
			l.readChar()
			tok = l.newToken(token.INTDIV, string(ch)+string(l.ch))
			l.readChar()
		} else if l.peekChar() == '=' {
			ch := l.ch
			l.readChar()
			tok = l.newToken(token.DIV_EQ, string(ch)+string(l.ch))
			l.readChar()
		} else {
			tok = l.makeToken(token.SLASH)
			l.readChar()
		}

	case '%':
		if l.peekChar() == '=' {
			ch := l.ch
			l.readChar()
			tok = l.newToken(token.MOD_EQ, string(ch)+string(l.ch))
			l.readChar()
		} else {
			tok = l.makeToken(token.PERCENT)
			l.readChar()
		}

	case '&':
		if l.peekChar() == '=' {
			ch := l.ch
			l.readChar()
			tok = l.newToken(token.CONCAT_EQ, string(ch)+string(l.ch))
			l.readChar()
		} else {
			tok = l.makeToken(token.AMPERSAND)
			l.readChar()
		}

	case '=':
		if l.peekChar() == '=' {
			ch := l.ch
			l.readChar()
			tok = l.newToken(token.EQ, string(ch)+string(l.ch))
			l.readChar()
		} else {
			tok = l.makeToken(token.ASSIGN)
			l.readChar()
		}

	case '!':
		if l.peekChar() == '=' {
			ch := l.ch
			l.readChar()
			tok = l.newToken(token.NEQ, string(ch)+string(l.ch))
			l.readChar()
		} else {
			tok = l.makeToken(token.ILLEGAL)
			l.readChar()
		}

	case '<':
		if l.peekChar() == '=' {
			ch := l.ch
			l.readChar()
			tok = l.newToken(token.LTE, string(ch)+string(l.ch))
			l.readChar()
		} else {
			tok = l.makeToken(token.LT)
			l.readChar()
		}

	case '>':
		if l.peekChar() == '=' {
			ch := l.ch
			l.readChar()
			tok = l.newToken(token.GTE, string(ch)+string(l.ch))
			l.readChar()
		} else {
			tok = l.makeToken(token.GT)
			l.readChar()
		}

	case '(':
		tok = l.makeToken(token.LPAREN)
		l.readChar()

	case ')':
		tok = l.makeToken(token.RPAREN)
		l.readChar()

	case '[':
		tok = l.makeToken(token.LBRACKET)
		l.readChar()

	case ']':
		tok = l.makeToken(token.RBRACKET)
		l.readChar()

	case '{':
		tok = l.makeToken(token.LBRACE)
		l.readChar()

	case '}':
		tok = l.makeToken(token.RBRACE)
		l.readChar()

	case ',':
		tok = l.makeToken(token.COMMA)
		l.readChar()

	case ':':
		tok = l.makeToken(token.COLON)
		l.readChar()

	case '.':
		tok = l.makeToken(token.DOT)
		l.readChar()

	case '"':
		str, ok := l.readString()
		if !ok {
			tok = l.newToken(token.ILLEGAL, "unterminated string")
		} else {
			tok = l.newToken(token.STRING, str)
		}
		l.readChar()

	case 0:
		// Emit any remaining DEDENT tokens before EOF
		if len(l.indentStack) > 1 {
			l.indentStack = l.indentStack[:len(l.indentStack)-1]
			tok = l.newToken(token.DEDENT, "")
			// Add EOF to pending tokens so it gets returned after all DEDENTs
			if len(l.indentStack) == 1 {
				l.pendingTokens = append(l.pendingTokens, l.newToken(token.EOF, ""))
			}
		} else {
			tok = l.newToken(token.EOF, "")
		}

	default:
		if isLetter(l.ch) {
			literal := l.readIdentifier()

			// Check for v"..." interpolated string
			if literal == "v" && l.ch == '"' {
				str, ok := l.readInterpolatedString()
				if !ok {
					tok = l.newToken(token.ILLEGAL, "unterminated interpolated string")
				} else {
					tok = l.newToken(token.VSTRING, str)
				}
				l.readChar()
				return tok
			}

			// Check for keywords with colons (rem:, note:, use:, etc.)
			if l.ch == ':' {
				literalWithColon := literal + ":"
				tokType := token.LookupIdent(literalWithColon)
				if tokType != token.IDENT {
					l.readChar() // consume the colon

					// Handle comments - skip them and get next token
					if tokType == token.REM {
						l.skipLineComment()
						return l.NextToken()
					} else if tokType == token.NOTE {
						l.skipBlockComment()
						return l.NextToken()
					}

					tok = l.newToken(tokType, literalWithColon)
					return tok
				}
			}

			tokType := token.LookupIdent(literal)
			tok = l.newToken(tokType, literal)
			return tok

		} else if isDigit(l.ch) {
			literal, tokType := l.readNumber()
			tok = l.newToken(tokType, literal)
			return tok

		} else {
			tok = l.makeToken(token.ILLEGAL)
			l.readChar()
		}
	}

	return tok
}
