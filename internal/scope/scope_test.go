package scope

import "testing"

func TestNewScope(t *testing.T) {
	// Test module scope creation
	module := NewModuleScope()
	if module.Level() != ModuleScope {
		t.Errorf("expected ModuleScope, got %s", module.Level())
	}
	if module.Parent() != nil {
		t.Error("module scope should have nil parent")
	}

	// Test child scope creation
	task := New(module, TaskScope)
	if task.Level() != TaskScope {
		t.Errorf("expected TaskScope, got %s", task.Level())
	}
	if task.Parent() != module {
		t.Error("task scope should have module as parent")
	}
}

func TestDefineAndResolve(t *testing.T) {
	scope := NewModuleScope()

	sym := &Symbol{
		Name:    "counter",
		Type:    "integer",
		Mutable: true,
		Line:    1,
		Column:  5,
	}

	err := scope.Define(sym)
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}

	// Resolve should find the symbol
	found, ok := scope.Resolve("counter")
	if !ok {
		t.Error("expected to find 'counter'")
	}
	if found.Name != "counter" {
		t.Errorf("expected name 'counter', got '%s'", found.Name)
	}
	if found.Mutable != true {
		t.Error("expected mutable to be true")
	}

	// Resolve nonexistent should return false
	_, ok = scope.Resolve("nonexistent")
	if ok {
		t.Error("expected not to find 'nonexistent'")
	}
}

func TestNoShadowingSameScope(t *testing.T) {
	scope := NewModuleScope()

	sym1 := &Symbol{Name: "x", Line: 1}
	sym2 := &Symbol{Name: "x", Line: 5}

	err := scope.Define(sym1)
	if err != nil {
		t.Errorf("unexpected error defining first: %v", err)
	}

	err = scope.Define(sym2)
	if err == nil {
		t.Error("expected error when redefining 'x' in same scope")
	}
}

func TestNoShadowingParentScope(t *testing.T) {
	module := NewModuleScope()
	task := New(module, TaskScope)

	moduleSym := &Symbol{Name: "counter", Line: 1}
	taskSym := &Symbol{Name: "counter", Line: 10}

	err := module.Define(moduleSym)
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}

	// Attempting to define same name in child scope should fail (no shadowing)
	err = task.Define(taskSym)
	if err == nil {
		t.Error("expected shadowing error when defining 'counter' in task scope")
	}
}

func TestResolveParentScope(t *testing.T) {
	module := NewModuleScope()
	task := New(module, TaskScope)
	block := New(task, BlockScope)

	moduleSym := &Symbol{Name: "moduleVar", Line: 1}
	taskSym := &Symbol{Name: "taskVar", Line: 5}
	blockSym := &Symbol{Name: "blockVar", Line: 10}

	module.Define(moduleSym)
	task.Define(taskSym)
	block.Define(blockSym)

	// Block scope should be able to resolve all three
	if _, ok := block.Resolve("blockVar"); !ok {
		t.Error("block scope should resolve blockVar")
	}
	if _, ok := block.Resolve("taskVar"); !ok {
		t.Error("block scope should resolve taskVar from parent")
	}
	if _, ok := block.Resolve("moduleVar"); !ok {
		t.Error("block scope should resolve moduleVar from grandparent")
	}

	// Module scope should only resolve its own
	if _, ok := module.Resolve("moduleVar"); !ok {
		t.Error("module scope should resolve moduleVar")
	}
	if _, ok := module.Resolve("taskVar"); ok {
		t.Error("module scope should NOT resolve taskVar")
	}
}

func TestResolveLocal(t *testing.T) {
	module := NewModuleScope()
	task := New(module, TaskScope)

	module.Define(&Symbol{Name: "moduleVar", Line: 1})
	task.Define(&Symbol{Name: "taskVar", Line: 5})

	// ResolveLocal should only find symbols in current scope
	if _, ok := task.ResolveLocal("taskVar"); !ok {
		t.Error("should find taskVar locally")
	}
	if _, ok := task.ResolveLocal("moduleVar"); ok {
		t.Error("should NOT find moduleVar locally")
	}

	// But Resolve should find both
	if _, ok := task.Resolve("moduleVar"); !ok {
		t.Error("should find moduleVar via Resolve")
	}
}

func TestSymbols(t *testing.T) {
	scope := NewModuleScope()

	scope.Define(&Symbol{Name: "a", Line: 1})
	scope.Define(&Symbol{Name: "b", Line: 2})
	scope.Define(&Symbol{Name: "c", Line: 3})

	symbols := scope.Symbols()
	if len(symbols) != 3 {
		t.Errorf("expected 3 symbols, got %d", len(symbols))
	}

	if _, ok := symbols["a"]; !ok {
		t.Error("missing symbol 'a'")
	}
	if _, ok := symbols["b"]; !ok {
		t.Error("missing symbol 'b'")
	}
	if _, ok := symbols["c"]; !ok {
		t.Error("missing symbol 'c'")
	}
}

func TestScopeLevelString(t *testing.T) {
	tests := []struct {
		level    ScopeLevel
		expected string
	}{
		{ModuleScope, "module"},
		{TaskScope, "task"},
		{BlockScope, "block"},
		{ParameterScope, "parameter"},
		{ScopeLevel(99), "unknown"},
	}

	for _, tt := range tests {
		if got := tt.level.String(); got != tt.expected {
			t.Errorf("ScopeLevel(%d).String() = %s, want %s", tt.level, got, tt.expected)
		}
	}
}

func TestDeepNesting(t *testing.T) {
	// Test deep scope nesting like nested loops
	module := NewModuleScope()
	module.Define(&Symbol{Name: "depth0", Line: 1})

	current := module
	for i := 1; i <= 5; i++ {
		child := New(current, BlockScope)
		child.Define(&Symbol{Name: "depth" + string(rune('0'+i)), Line: i + 1})
		current = child
	}

	// Deepest scope should be able to resolve all symbols
	for i := 0; i <= 5; i++ {
		name := "depth" + string(rune('0'+i))
		if _, ok := current.Resolve(name); !ok {
			t.Errorf("deepest scope should resolve %s", name)
		}
	}
}
