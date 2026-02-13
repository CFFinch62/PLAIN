package runtime

import (
	"testing"
)

// ============================================================
// Network I/O — Argument Validation Tests
// ============================================================
// These tests validate argument checking and error handling
// without requiring actual network connections.

func TestNetConnectWrongArgCount(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["net_connect"].Fn

	// Too few args
	result := fn(NewString("localhost"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("net_connect() with 1 arg should return an error")
	}

	// Too many args
	result = fn(NewString("localhost"), NewInteger(8080), NewString("tcp"), NewString("extra"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("net_connect() with 4 args should return an error")
	}
}

func TestNetConnectWrongArgTypes(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["net_connect"].Fn

	// First arg must be string
	result := fn(NewInteger(42), NewInteger(8080))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("net_connect(42, 8080) should return an error (first arg must be string)")
	}

	// Second arg must be integer
	result = fn(NewString("localhost"), NewString("8080"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("net_connect('localhost', '8080') should return an error (second arg must be integer)")
	}

	// Third arg must be string
	result = fn(NewString("localhost"), NewInteger(8080), NewInteger(1))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("net_connect('localhost', 8080, 1) should return an error (third arg must be string)")
	}
}

func TestNetConnectInvalidProtocol(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["net_connect"].Fn

	result := fn(NewString("localhost"), NewInteger(8080), NewString("http"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("net_connect() with invalid protocol should return an error")
	}
}

func TestNetCloseWrongArgCount(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["net_close"].Fn

	result := fn()
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("net_close() with no args should return an error")
	}

	result = fn(NewString("conn"), NewString("extra"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("net_close() with 2 args should return an error")
	}
}

func TestNetCloseWrongArgType(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["net_close"].Fn

	result := fn(NewString("not a connection"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("net_close('string') should return an error")
	}
}

func TestNetWriteWrongArgCount(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["net_write"].Fn

	result := fn(NewString("conn"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("net_write() with 1 arg should return an error")
	}
}

func TestNetWriteWrongArgTypes(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["net_write"].Fn

	result := fn(NewString("not a conn"), NewString("data"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("net_write('string', 'data') should return an error (first arg must be net_conn)")
	}
}

func TestNetReadWrongArgCount(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["net_read"].Fn

	result := fn(NewString("conn"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("net_read() with 1 arg should return an error")
	}
}

func TestNetReadWrongArgTypes(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["net_read"].Fn

	result := fn(NewString("not a conn"), NewInteger(100))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("net_read('string', 100) should return an error (first arg must be net_conn)")
	}

	// Create a mock NetConnValue for testing count validation
	mockConn := &NetConnValue{IsOpen: true}
	result = fn(mockConn, NewString("100"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("net_read(conn, '100') should return an error (second arg must be integer)")
	}

	result = fn(mockConn, NewInteger(0))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("net_read(conn, 0) should return an error (count must be positive)")
	}

	result = fn(mockConn, NewInteger(-5))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("net_read(conn, -5) should return an error (count must be positive)")
	}
}

func TestNetReadLineWrongArgCount(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["net_read_line"].Fn

	result := fn()
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("net_read_line() with no args should return an error")
	}

	result = fn(NewString("conn"), NewString("extra"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("net_read_line() with 2 args should return an error")
	}
}

func TestNetReadLineWrongArgType(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["net_read_line"].Fn

	result := fn(NewString("not a conn"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("net_read_line('string') should return an error")
	}
}

func TestNetSetTimeoutWrongArgCount(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["net_set_timeout"].Fn

	result := fn(NewString("conn"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("net_set_timeout() with 1 arg should return an error")
	}
}

func TestNetSetTimeoutWrongArgTypes(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["net_set_timeout"].Fn

	result := fn(NewString("not a conn"), NewInteger(1000))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("net_set_timeout('string', 1000) should return an error (first arg must be net_conn)")
	}

	mockConn := &NetConnValue{IsOpen: true}
	result = fn(mockConn, NewString("1000"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("net_set_timeout(conn, '1000') should return an error (second arg must be integer)")
	}
}

func TestNetListenWrongArgCount(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["net_listen"].Fn

	result := fn()
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("net_listen() with no args should return an error")
	}

	result = fn(NewInteger(8080), NewString("tcp"), NewString("extra"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("net_listen() with 3 args should return an error")
	}
}

func TestNetListenWrongArgTypes(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["net_listen"].Fn

	result := fn(NewString("8080"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("net_listen('8080') should return an error (first arg must be integer)")
	}

	result = fn(NewInteger(8080), NewInteger(1))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("net_listen(8080, 1) should return an error (second arg must be string)")
	}
}

func TestNetListenInvalidProtocol(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["net_listen"].Fn

	result := fn(NewInteger(8080), NewString("http"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("net_listen() with invalid protocol should return an error")
	}
}

func TestNetAcceptWrongArgCount(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["net_accept"].Fn

	result := fn()
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("net_accept() with no args should return an error")
	}

	result = fn(NewString("listener"), NewString("extra"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("net_accept() with 2 args should return an error")
	}
}

func TestNetAcceptWrongArgType(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["net_accept"].Fn

	result := fn(NewString("not a listener"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("net_accept('string') should return an error")
	}
}

func TestNetAcceptNotListener(t *testing.T) {
	builtins := GetBuiltins()
	fn := builtins["net_accept"].Fn

	// Create a client connection (not a listener)
	mockConn := &NetConnValue{IsOpen: true, IsServer: false}
	result := fn(mockConn)
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("net_accept() on a client connection should return an error")
	}
}
