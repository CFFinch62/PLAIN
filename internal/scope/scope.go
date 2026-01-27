package scope

import "fmt"

// ScopeLevel indicates the type of scope
type ScopeLevel int

const (
	ModuleScope    ScopeLevel = iota // File-level declarations
	TaskScope                        // Task-level declarations
	BlockScope                       // Control structure blocks (if, loop, etc.)
	ParameterScope                   // Task parameters (immutable)
)

// String returns a human-readable name for the scope level
func (sl ScopeLevel) String() string {
	switch sl {
	case ModuleScope:
		return "module"
	case TaskScope:
		return "task"
	case BlockScope:
		return "block"
	case ParameterScope:
		return "parameter"
	default:
		return "unknown"
	}
}

// Symbol represents a declared identifier in the program
type Symbol struct {
	Name    string // Variable/constant/parameter name
	Type    string // Type name (for Phase 4 type checking)
	Mutable bool   // true for var, false for fxd and parameters
	Line    int    // Declaration line number
	Column  int    // Declaration column number
}

// Scope represents a lexical scope containing symbols
type Scope struct {
	parent  *Scope
	symbols map[string]*Symbol
	level   ScopeLevel
}

// New creates a new scope with the given parent and level
func New(parent *Scope, level ScopeLevel) *Scope {
	return &Scope{
		parent:  parent,
		symbols: make(map[string]*Symbol),
		level:   level,
	}
}

// NewModuleScope creates a new top-level module scope
func NewModuleScope() *Scope {
	return New(nil, ModuleScope)
}

// Parent returns the parent scope (nil for module scope)
func (s *Scope) Parent() *Scope {
	return s.parent
}

// Level returns the scope level
func (s *Scope) Level() ScopeLevel {
	return s.level
}

// Define adds a symbol to the current scope
// Returns an error if the name is already declared in this or any outer scope (no shadowing)
func (s *Scope) Define(sym *Symbol) error {
	// Check for shadowing in current scope
	if existing, ok := s.symbols[sym.Name]; ok {
		return fmt.Errorf("variable '%s' already declared at line %d", sym.Name, existing.Line)
	}

	// Check for shadowing in parent scopes (PLAIN does not allow shadowing)
	if s.parent != nil {
		if existing, found := s.parent.Resolve(sym.Name); found {
			return fmt.Errorf("variable '%s' already declared in outer scope at line %d", sym.Name, existing.Line)
		}
	}

	s.symbols[sym.Name] = sym
	return nil
}

// Resolve looks up a symbol by name in this scope and all parent scopes
// Returns the symbol and true if found, nil and false otherwise
func (s *Scope) Resolve(name string) (*Symbol, bool) {
	// Check current scope first
	if sym, ok := s.symbols[name]; ok {
		return sym, true
	}

	// Check parent scopes
	if s.parent != nil {
		return s.parent.Resolve(name)
	}

	return nil, false
}

// ResolveLocal looks up a symbol only in the current scope (not parent scopes)
// Returns the symbol and true if found, nil and false otherwise
func (s *Scope) ResolveLocal(name string) (*Symbol, bool) {
	sym, ok := s.symbols[name]
	return sym, ok
}

// Symbols returns all symbols defined in this scope (not including parent scopes)
func (s *Scope) Symbols() map[string]*Symbol {
	result := make(map[string]*Symbol)
	for k, v := range s.symbols {
		result[k] = v
	}
	return result
}
