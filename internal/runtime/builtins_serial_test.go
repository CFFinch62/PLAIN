package runtime

import (
	"testing"
)

// ============================================================
// Serial Port — Argument Validation Tests
// ============================================================
// These tests validate argument checking and error handling
// without requiring physical serial hardware.

func TestSerialPortsNoArgs(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["serial_ports"].Fn

	// serial_ports() with no args should return a list (even if empty)
	result := fn()
	if _, ok := result.(*ListValue); !ok {
		if _, isErr := result.(*ErrorValue); isErr {
			// Some systems may error if no serial subsystem — acceptable
			t.Logf("serial_ports() returned error (may be OK on this system): %s", result.String())
		} else {
			t.Fatalf("serial_ports() expected list or error, got %T: %s", result, result.String())
		}
	}
}

func TestSerialPortsWrongArgs(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["serial_ports"].Fn

	// serial_ports() should reject arguments
	result := fn(NewString("extra"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_ports('extra') should return an error")
	}
}

func TestSerialOpenWrongArgCount(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["serial_open"].Fn

	// Too few args
	result := fn(NewString("/dev/ttyUSB0"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_open() with 1 arg should return an error")
	}

	// Too many args
	result = fn(NewString("/dev/ttyUSB0"), NewInteger(9600), NewString("8N1"), NewString("extra"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_open() with 4 args should return an error")
	}
}

func TestSerialOpenWrongArgTypes(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["serial_open"].Fn

	// First arg must be string
	result := fn(NewInteger(42), NewInteger(9600))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_open(42, 9600) should return an error (first arg must be string)")
	}

	// Second arg must be integer
	result = fn(NewString("/dev/ttyUSB0"), NewString("9600"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_open('/dev/ttyUSB0', '9600') should return an error (second arg must be integer)")
	}

	// Third arg must be string
	result = fn(NewString("/dev/ttyUSB0"), NewInteger(9600), NewInteger(8))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_open() with integer config should return an error")
	}
}

func TestSerialOpenInvalidConfig(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["serial_open"].Fn

	// Invalid config string length
	result := fn(NewString("/dev/ttyUSB0"), NewInteger(9600), NewString("8N"))
	errVal, ok := result.(*ErrorValue)
	if !ok {
		t.Fatal("serial_open() with 2-char config should return an error")
	}
	if errVal.Message == "" {
		t.Error("error message should not be empty")
	}

	// Invalid data bits
	result = fn(NewString("/dev/ttyUSB0"), NewInteger(9600), NewString("9N1"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_open() with data bits '9' should return an error")
	}

	// Invalid parity
	result = fn(NewString("/dev/ttyUSB0"), NewInteger(9600), NewString("8X1"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_open() with parity 'X' should return an error")
	}

	// Invalid stop bits
	result = fn(NewString("/dev/ttyUSB0"), NewInteger(9600), NewString("8N3"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_open() with stop bits '3' should return an error")
	}
}

func TestSerialOpenInvalidPort(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["serial_open"].Fn

	// Opening a non-existent port should return an error, not panic
	result := fn(NewString("/dev/nonexistent_port_xyz"), NewInteger(9600))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_open() on non-existent port should return an error")
	}
}

func TestSerialCloseWrongArgs(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["serial_close"].Fn

	// Wrong arg count
	result := fn()
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_close() with no args should return an error")
	}

	// Wrong arg type
	result = fn(NewString("not a port"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_close() with string arg should return an error")
	}

	// Closed port
	closedPort := &SerialPortValue{PortName: "test", IsOpen: false}
	result = fn(closedPort)
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_close() on closed port should return an error")
	}
}

func TestSerialWriteWrongArgs(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["serial_write"].Fn

	// Wrong arg count
	result := fn(NewString("only one"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_write() with 1 arg should return an error")
	}

	// Wrong first arg type
	result = fn(NewString("not a port"), NewString("data"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_write() with string first arg should return an error")
	}

	// Closed port
	closedPort := &SerialPortValue{PortName: "test", IsOpen: false}
	result = fn(closedPort, NewString("data"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_write() on closed port should return an error")
	}
}

func TestSerialReadWrongArgs(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["serial_read"].Fn

	// Wrong arg count
	result := fn(NewString("only one"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_read() with 1 arg should return an error")
	}

	// Wrong first arg type
	result = fn(NewString("not a port"), NewInteger(10))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_read() with string first arg should return an error")
	}

	// Wrong second arg type
	closedPort := &SerialPortValue{PortName: "test", IsOpen: true}
	result = fn(closedPort, NewString("ten"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_read() with string count should return an error")
	}

	// Negative count
	result = fn(closedPort, NewInteger(-1))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_read() with negative count should return an error")
	}

	// Closed port
	closedPort2 := &SerialPortValue{PortName: "test", IsOpen: false}
	result = fn(closedPort2, NewInteger(10))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_read() on closed port should return an error")
	}
}

func TestSerialReadLineWrongArgs(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["serial_read_line"].Fn

	// Wrong arg count
	result := fn()
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_read_line() with no args should return an error")
	}

	// Wrong arg type
	result = fn(NewString("not a port"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_read_line() with string arg should return an error")
	}

	// Closed port
	closedPort := &SerialPortValue{PortName: "test", IsOpen: false}
	result = fn(closedPort)
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_read_line() on closed port should return an error")
	}
}

func TestSerialSetTimeoutWrongArgs(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["serial_set_timeout"].Fn

	// Wrong arg count
	result := fn(NewString("only one"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_set_timeout() with 1 arg should return an error")
	}

	// Wrong first arg type
	result = fn(NewString("not a port"), NewInteger(1000))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_set_timeout() with string first arg should return an error")
	}

	// Closed port
	closedPort := &SerialPortValue{PortName: "test", IsOpen: false}
	result = fn(closedPort, NewInteger(1000))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_set_timeout() on closed port should return an error")
	}
}

func TestSerialFlushWrongArgs(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["serial_flush"].Fn

	// Wrong arg count
	result := fn()
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_flush() with no args should return an error")
	}

	// Wrong arg type
	result = fn(NewString("not a port"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_flush() with string arg should return an error")
	}
}

func TestSerialSetDtrWrongArgs(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["serial_set_dtr"].Fn

	// Wrong arg count
	result := fn(NewString("only one"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_set_dtr() with 1 arg should return an error")
	}

	// Wrong first arg type
	result = fn(NewString("not a port"), NewBoolean(true))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_set_dtr() with string first arg should return an error")
	}

	// Wrong second arg type
	closedPort := &SerialPortValue{PortName: "test", IsOpen: true}
	result = fn(closedPort, NewString("true"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_set_dtr() with string state should return an error")
	}
}

func TestSerialSetRtsWrongArgs(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["serial_set_rts"].Fn

	// Wrong arg count
	result := fn(NewString("only one"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_set_rts() with 1 arg should return an error")
	}

	// Wrong first arg type
	result = fn(NewString("not a port"), NewBoolean(true))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_set_rts() with string first arg should return an error")
	}
}

func TestSerialGetSignalsWrongArgs(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["serial_get_signals"].Fn

	// Wrong arg count
	result := fn()
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_get_signals() with no args should return an error")
	}

	// Wrong arg type
	result = fn(NewString("not a port"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_get_signals() with string arg should return an error")
	}
}

func TestSerialAvailableWrongArgs(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["serial_available"].Fn

	// Wrong arg count
	result := fn()
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_available() with no args should return an error")
	}

	// Wrong arg type
	result = fn(NewString("not a port"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_available() with string arg should return an error")
	}

	// Closed port
	closedPort := &SerialPortValue{PortName: "test", IsOpen: false}
	result = fn(closedPort)
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("serial_available() on closed port should return an error")
	}
}

// ============================================================
// SerialPortValue Type Tests
// ============================================================

func TestSerialPortValueType(t *testing.T) {
	sp := &SerialPortValue{
		PortName: "/dev/ttyUSB0",
		BaudRate: 9600,
		Config:   "8N1",
		IsOpen:   true,
	}

	if sp.Type() != "serial_port" {
		t.Errorf("Type() = %q, want \"serial_port\"", sp.Type())
	}

	if !sp.IsTruthy() {
		t.Error("open serial port should be truthy")
	}

	expected := "<serial /dev/ttyUSB0 baud=9600 open>"
	if sp.String() != expected {
		t.Errorf("String() = %q, want %q", sp.String(), expected)
	}

	// Closed port
	sp.IsOpen = false
	if sp.IsTruthy() {
		t.Error("closed serial port should be falsy")
	}

	expected = "<serial /dev/ttyUSB0 baud=9600 closed>"
	if sp.String() != expected {
		t.Errorf("String() = %q, want %q", sp.String(), expected)
	}
}

// ============================================================
// Config Parsing Validation Tests
// ============================================================

func TestSerialOpenValidConfigs(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["serial_open"].Fn

	// These will all fail to actually open (no real port), but they should
	// fail with a port-not-found error, NOT a config parsing error.
	validConfigs := []string{"8N1", "7E1", "8O2", "5N1", "6S1", "8M1", "8n1", "7e2"}

	for _, cfg := range validConfigs {
		result := fn(NewString("/dev/nonexistent_test_port"), NewInteger(9600), NewString(cfg))
		errVal, ok := result.(*ErrorValue)
		if !ok {
			// If it somehow succeeded (unlikely), that's fine too
			continue
		}
		// The error should be about opening the port, not about config parsing
		if errContains(errVal.Message, "invalid data bits") ||
			errContains(errVal.Message, "invalid parity") ||
			errContains(errVal.Message, "invalid stop bits") ||
			errContains(errVal.Message, "config must be") {
			t.Errorf("serial_open() with valid config %q returned config error: %s", cfg, errVal.Message)
		}
	}
}

// errContains is a helper to check if a string contains a substring
func errContains(s, substr string) bool {
	return len(s) >= len(substr) && containsStr(s, substr)
}

func containsStr(s, substr string) bool {
	for i := 0; i <= len(s)-len(substr); i++ {
		if s[i:i+len(substr)] == substr {
			return true
		}
	}
	return false
}

// ============================================================
// All Serial Builtins Registration Test
// ============================================================

func TestSerialBuiltinsRegistered(t *testing.T) {
	builtins := GetBuiltins()

	expectedBuiltins := []string{
		"serial_ports",
		"serial_open",
		"serial_close",
		"serial_write",
		"serial_read",
		"serial_read_line",
		"serial_available",
		"serial_set_timeout",
		"serial_flush",
		"serial_set_dtr",
		"serial_set_rts",
		"serial_get_signals",
	}

	for _, name := range expectedBuiltins {
		if _, ok := builtins[name]; !ok {
			t.Errorf("builtin %q is not registered", name)
		}
	}
}
