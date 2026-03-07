//go:build js && wasm

package runtime

// getSerialBuiltins returns nil in WASM builds — serial port I/O is not
// available in the browser. GetBuiltins() handles this gracefully.
func getSerialBuiltins() map[string]*BuiltinValue {
	return nil
}

// getNetBuiltins returns nil in WASM builds — raw TCP/UDP networking is not
// available in the browser. GetBuiltins() handles this gracefully.
func getNetBuiltins() map[string]*BuiltinValue {
	return nil
}

