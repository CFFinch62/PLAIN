package runtime

// Environment stores variable bindings.
//
// Backed by a linear-scan slice rather than a Go map, and left
// unallocated (nil) until the first Define -- see the interpreter-level
// performance investigation referenced from dev-docs/session_log.md.
// Profiling real Project Euler solutions (and a synthetic loop+if
// isolation case) found Environment.Get/Set/Define's underlying map
// operations (hashing plus the map machinery itself) dominating CPU
// time -- ~30% of total runtime spent in Get alone on one real
// solution -- for two compounding reasons:
//
//  1. NewEnclosedEnvironment allocated a fresh map eagerly on every
//     block entry (every loop iteration's `if`, every loop body), even
//     though most blocks never declare a single local of their own --
//     an `if` body that only assigns to an *outer* variable never calls
//     Define, so that map was allocated, hashed into zero times, and
//     discarded. A nil slice costs nothing until first appended to.
//  2. Go's real map has meaningful per-access overhead (hash
//     computation, bucket lookup) that isn't worth paying for the
//     handful of variables a typical task/block scope actually holds --
//     a linear scan with a plain string comparison is faster below
//     roughly a few dozen entries, comfortably covering real programs.
//
// Public API (Get/Set/Define) is unchanged, so no caller outside this
// file needed to change -- except internal/runtime/debugger.go's direct
// use of the old exported-within-package `store` map field for the
// IDE's live variables panel, which now goes through snapshot() instead
// (see that file).
type Environment struct {
	names  []string
	values []Value
	parent *Environment
}

// NewEnvironment creates a new global environment.
func NewEnvironment() *Environment {
	return &Environment{parent: nil}
}

// NewEnclosedEnvironment creates an environment with a parent.
func NewEnclosedEnvironment(parent *Environment) *Environment {
	return &Environment{parent: parent}
}

// Get retrieves a value by name, searching parent scopes.
func (e *Environment) Get(name string) (Value, bool) {
	for i, n := range e.names {
		if n == name {
			return e.values[i], true
		}
	}
	if e.parent != nil {
		return e.parent.Get(name)
	}
	return nil, false
}

// Set updates an existing variable in the appropriate scope.
func (e *Environment) Set(name string, val Value) bool {
	for i, n := range e.names {
		if n == name {
			e.values[i] = val
			return true
		}
	}
	if e.parent != nil {
		return e.parent.Set(name, val)
	}
	return false
}

// Define creates (or, matching the prior map-based behavior, overwrites)
// a variable in the current scope.
func (e *Environment) Define(name string, val Value) {
	for i, n := range e.names {
		if n == name {
			e.values[i] = val
			return
		}
	}
	e.names = append(e.names, name)
	e.values = append(e.values, val)
}

// snapshot returns a name->value map of just this scope's own entries
// (not parent scopes) -- used only by debugger.go's cold-path variable
// introspection, which was written directly against the old `store`
// map field. Not used by anything performance-sensitive.
func (e *Environment) snapshot() map[string]Value {
	m := make(map[string]Value, len(e.names))
	for i, n := range e.names {
		m[n] = e.values[i]
	}
	return m
}
