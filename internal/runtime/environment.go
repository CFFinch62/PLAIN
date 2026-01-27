package runtime

// Environment stores variable bindings
type Environment struct {
	store  map[string]Value
	parent *Environment
}

// NewEnvironment creates a new global environment
func NewEnvironment() *Environment {
	return &Environment{
		store:  make(map[string]Value),
		parent: nil,
	}
}

// NewEnclosedEnvironment creates an environment with a parent
func NewEnclosedEnvironment(parent *Environment) *Environment {
	return &Environment{
		store:  make(map[string]Value),
		parent: parent,
	}
}

// Get retrieves a value by name, searching parent scopes
func (e *Environment) Get(name string) (Value, bool) {
	val, ok := e.store[name]
	if !ok && e.parent != nil {
		return e.parent.Get(name)
	}
	return val, ok
}

// Set updates an existing variable in the appropriate scope
func (e *Environment) Set(name string, val Value) bool {
	// Check if it exists in current scope
	if _, ok := e.store[name]; ok {
		e.store[name] = val
		return true
	}
	// Check parent scopes
	if e.parent != nil {
		return e.parent.Set(name, val)
	}
	return false
}

// Define creates a new variable in the current scope
func (e *Environment) Define(name string, val Value) {
	e.store[name] = val
}
