# PLAIN Language — Serial Port & Network I/O Implementation Plan

**Created:** 2026-02-13
**Status:** ✅ COMPLETE
**Goal:** Add serial port (COM/virtual COM) and TCP/UDP network I/O to PLAIN

---

## 1. Motivation

PLAIN's creator has 40+ years of data acquisition and processing experience, primarily
over serial data connections and TCP/UDP (including NMEA 0183 over IP). Adding serial
and network I/O transforms PLAIN from a teaching language into one capable of real-world
data acquisition work. Learners can grow with the language from basic programming through
to live hardware interfacing.

---

## 2. Architecture Overview

### Current State

- **Language:** Go 1.22.2+, zero external dependencies (stdlib only)
- **Builtins:** 73+ functions in `internal/runtime/builtins.go`, registered via `GetBuiltins()` map
- **Value types:** Defined in `internal/runtime/value.go`, all implement the `Value` interface
- **File I/O pattern:** `FileHandleValue` with `open()/close()/read()/write()` — the template for serial/network
- **Event system:** Timer-based event loop in `internal/runtime/events.go` (goroutine-based)
- **Platforms:** Linux, macOS (Intel + ARM), Windows

### Design Decisions

1. **Accept one external dependency:** `go.bug.st/serial` for cross-platform serial port access.
   Raw syscalls would require hundreds of lines of platform-specific ioctl/termios/DCB code.
   This library is well-maintained and widely used in the Go ecosystem.

2. **New value types:** `SerialPortValue` and (later) `NetConnValue` — following `FileHandleValue` pattern.

3. **Separate builtin namespaces:** `serial_*` prefix for serial, `net_*` prefix for network.
   This keeps the flat builtin namespace organized and avoids collision with file I/O functions.

4. **No changes to parser/lexer/evaluator:** All functionality implemented purely as builtins
   and value types. Zero language syntax changes required.

5. **Phased approach:** Serial first (Phase 1-3), then TCP/UDP (Phase 4), to validate the
   pattern before expanding.

---

## 3. Implementation Phases

### Phase 1: Foundation — Dependency & Value Type

**Files modified:**
- `go.mod` — add `go.bug.st/serial` dependency
- `internal/runtime/value.go` — add `SerialPortValue` type

**Step 1.1: Add the serial library dependency**

```bash
cd /home/chuck/Dropbox/.../PLAIN
go get go.bug.st/serial
```

This updates `go.mod` and creates `go.sum`.

**Step 1.2: Create `SerialPortValue` in `value.go`**

```go
// SerialPortValue represents an open serial port connection
type SerialPortValue struct {
    PortName string
    BaudRate int
    Config   string          // e.g., "8N1"
    Handle   interface{}     // serial.Port from go.bug.st/serial
    Reader   interface{}     // *bufio.Reader for line-based reading
    IsOpen   bool
}

func (v *SerialPortValue) Type() string   { return "serial_port" }
func (v *SerialPortValue) String() string {
    status := "closed"
    if v.IsOpen {
        status = "open"
    }
    return fmt.Sprintf("<serial %s baud=%d %s>", v.PortName, v.BaudRate, status)
}
func (v *SerialPortValue) IsTruthy() bool { return v.IsOpen }
```

**Completion criteria:** `go build cmd/plain/main.go` succeeds with new type.

---

### Phase 2: Core Serial Builtins

**Files modified:**
- `internal/runtime/builtins.go` — add serial functions

All serial builtins go in a new section in `builtins.go`, following the existing pattern.

**Step 2.1: `serial_ports()` — Port Discovery**

```
serial_ports() -> list of strings
```

Returns a list of available serial port names. Uses `serial.GetPortsList()`.

Example PLAIN usage:
```plain
var ports = serial_ports()
loop port in ports
    display(port)
```

**Step 2.2: `serial_open(port, baud)` — Open Connection**

```
serial_open(port_name, baud_rate) -> serial_port handle
serial_open(port_name, baud_rate, config) -> serial_port handle
```

Opens a serial port with the given baud rate. Optional third argument is the
config string (default "8N1"). Config format: `{data_bits}{parity}{stop_bits}`

- Data bits: 5, 6, 7, 8
- Parity: N (none), E (even), O (odd), M (mark), S (space)
- Stop bits: 1, 2

Maps to `serial.Open(portName, &serial.Mode{...})`.
Wraps the result in a `bufio.Reader` for line-based reading.

Example:
```plain
var gps = serial_open("/dev/ttyUSB0", 4800)
var instrument = serial_open("COM3", 9600, "8N1")
```

**Step 2.3: `serial_close(port)` — Close Connection**

```
serial_close(port) -> null
```

Closes the serial port. Sets `IsOpen = false`.

Example:
```plain
serial_close(gps)
```

**Step 2.4: `serial_write(port, data)` — Send Data**

```
serial_write(port, data) -> integer (bytes written)
```

Writes a string or bytes to the serial port. Returns number of bytes written.

Example:
```plain
serial_write(port, "$CCMSG,1,1*hh\r\n")
```

**Step 2.5: `serial_read(port, count)` — Read Bytes**

```
serial_read(port, count) -> string
```

Reads up to `count` bytes from the serial port. Returns a string.
Blocks until data is available (respects timeout set by `serial_set_timeout`).

Example:
```plain
var data = serial_read(port, 256)
```

**Step 2.6: `serial_read_line(port)` — Read Line (Critical for NMEA)**

```
serial_read_line(port) -> string
```

Reads until `\n` (newline) is encountered. Returns the line without the trailing
`\r\n` or `\n`. Uses the `bufio.Reader` wrapper for efficient buffered line reading.

This is the primary function for NMEA 0183 data (sentences are CR+LF terminated).

Example:
```plain
var sentence = serial_read_line(gps)
rem: Returns "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,47.0,M,,*47"
```

**Completion criteria:** Can open a port, write data, read lines, and close. Basic
serial communication works.

---

### Phase 3: Serial Utility Builtins

**Files modified:**
- `internal/runtime/builtins.go` — additional serial utility functions

**Step 3.1: `serial_available(port)` — Check Pending Data**

```
serial_available(port) -> boolean
```

Returns `true` if there is data waiting to be read. Non-blocking check.
Implementation note: `go.bug.st/serial` doesn't provide a direct "bytes available"
API, so this may use a short non-blocking read attempt or rely on platform specifics.
Alternative: return an integer count if feasible, otherwise boolean.

**Step 3.2: `serial_set_timeout(port, ms)` — Read Timeout**

```
serial_set_timeout(port, milliseconds) -> null
```

Sets the read timeout for the serial port in milliseconds.
- `0` = non-blocking (return immediately with whatever is available)
- `-1` = block forever (wait until data arrives)
- `> 0` = wait up to N milliseconds

Uses `port.SetReadTimeout(time.Duration)`.

Example:
```plain
serial_set_timeout(gps, 2000)    rem: 2-second timeout
```

**Step 3.3: `serial_flush(port)` — Flush Buffers**

```
serial_flush(port) -> null
```

Flushes both input and output buffers. Uses `port.ResetInputBuffer()` and
`port.ResetOutputBuffer()`.

**Step 3.4: `serial_set_dtr(port, state)` / `serial_set_rts(port, state)` — Control Lines**

```
serial_set_dtr(port, true/false) -> null
serial_set_rts(port, true/false) -> null
```

Control DTR (Data Terminal Ready) and RTS (Request To Send) handshake lines.
Some devices require specific DTR/RTS states.

**Step 3.5: `serial_get_signals(port)` — Read Control Lines**

```
serial_get_signals(port) -> table
```

Returns a table of control line states: `{"cts": true, "dsr": false, "ri": false, "cd": true}`.
Uses `port.GetModemStatusBits()`.

**Completion criteria:** Full serial port control including timeouts, flushing, and
hardware flow control lines.

---

### Phase 4: TCP/UDP Network I/O

**Files modified:**
- `internal/runtime/value.go` — add `NetConnValue` type
- `internal/runtime/builtins.go` — add network functions

**No additional dependencies** — uses Go's standard `net` package.

**Step 4.1: `NetConnValue` in `value.go`**

```go
// NetConnValue represents a network connection (TCP or UDP)
type NetConnValue struct {
    Address  string          // "host:port"
    Protocol string          // "tcp" or "udp"
    Handle   interface{}     // net.Conn
    Reader   interface{}     // *bufio.Reader for line-based reading
    IsOpen   bool
    IsServer bool            // true if this is a listener
}
```

**Step 4.2: Client Connection Functions**

```
net_connect(host, port, protocol) -> net_conn handle
net_close(conn) -> null
net_write(conn, data) -> integer (bytes written)
net_read(conn, count) -> string
net_read_line(conn) -> string
net_set_timeout(conn, milliseconds) -> null
```

`protocol` is `"tcp"` or `"udp"`. Default to `"tcp"` if omitted.

Example — NMEA over IP:
```plain
var sock = net_connect("192.168.1.100", 10110, "tcp")
serial_set_timeout(sock, 5000)

loop forever
    var sentence = net_read_line(sock)
    if starts_with(sentence, "$GPGGA")
        var fields = split(sentence, ",")
        display("Position:", fields[2], fields[3], fields[4], fields[5])

net_close(sock)
```

**Step 4.3: Server Listener Functions (Stretch Goal)**

```
net_listen(port, protocol) -> net_conn listener
net_accept(listener) -> net_conn client
```

Allows PLAIN to act as a TCP server — useful for data forwarding/multiplexing.

**Completion criteria:** Can connect to NMEA-over-IP sources, read sentences, and
(optionally) accept incoming connections.

---

## 4. Testing Strategy

### Unit Tests (`internal/runtime/builtins_serial_test.go`)

- `serial_ports()` returns a list (even if empty — no hardware needed)
- Argument validation for all functions (wrong types, missing args)
- Error handling for invalid port names, invalid baud rates, invalid config strings
- Config string parsing ("8N1", "7E1", "8N2", etc.)

### Integration Tests (require hardware or virtual serial ports)

- **Linux:** Use `socat` to create virtual serial port pairs:
  ```bash
  socat -d -d pty,raw,echo=0 pty,raw,echo=0
  ```
  This creates two linked pseudo-terminals (e.g., `/dev/pts/3` and `/dev/pts/4`).
  Write to one, read from the other.

- **Test program (`tests/serial_loopback.plain`):**
  ```plain
  task Main()
      rem: Requires two linked virtual serial ports
      var writer = serial_open("/dev/pts/3", 9600)
      var reader = serial_open("/dev/pts/4", 9600)
      serial_set_timeout(reader, 1000)

      serial_write(writer, "$GPGGA,test*00\r\n")
      var line = serial_read_line(reader)
      display("Got:", line)

      serial_close(writer)
      serial_close(reader)
  ```

### NMEA Simulation Test

- **Test program (`tests/nmea_reader.plain`):**
  ```plain
  task Main()
      display("Available ports:")
      var ports = serial_ports()
      loop port in ports
          display("  " & port)

      if len(ports) = 0
          display("No serial ports found.")
          deliver null

      var gps = serial_open(ports[0], 4800)
      serial_set_timeout(gps, 5000)

      display("Reading NMEA sentences...")
      loop i from 1 to 10
          var sentence = serial_read_line(gps)
          display(v"[{i}] {sentence}")

      serial_close(gps)
      display("Done.")
  ```

---

## 5. Documentation Updates

### Files to update:
1. **`docs/user/STDLIB.md`** — Add sections:
   - `16. Serial Port I/O` (after Timing and Events)
   - `17. Network I/O` (after Serial)

2. **`docs/quick_reference.md`** — Add serial/network rows to the reference table

3. **`README.md`** — Mention serial/network capability in features list

4. **`ToDo.md`** — Mark networking as implemented, add serial entry

---

## 6. File Change Summary

| File | Change Type | Phase |
|------|-------------|-------|
| `go.mod` | Modified — add `go.bug.st/serial` | 1 |
| `go.sum` | Created — dependency checksums | 1 |
| `internal/runtime/value.go` | Modified — add `SerialPortValue` | 1 |
| `internal/runtime/builtins.go` | Modified — add ~300 lines of serial builtins | 2-3 |
| `internal/runtime/value.go` | Modified — add `NetConnValue` | 4 |
| `internal/runtime/builtins.go` | Modified — add ~200 lines of network builtins | 4 |
| `internal/runtime/builtins_serial_test.go` | Created — serial unit tests | 2-3 |
| `internal/runtime/builtins_net_test.go` | Created — network unit tests | 4 |
| `docs/user/STDLIB.md` | Modified — add serial & network sections | 2-4 |
| `docs/quick_reference.md` | Modified — add reference rows | 2-4 |
| `tests/serial_loopback.plain` | Created — integration test | 3 |
| `tests/nmea_reader.plain` | Created — NMEA test | 3 |
| `examples/nmea_reader.plain` | Created — example program | 3 |

---

## 7. Complete Builtin Function Reference

### Serial Port Functions (Phases 2-3)

| Function | Signature | Description |
|----------|-----------|-------------|
| `serial_ports` | `serial_ports()` -> list | List available serial ports |
| `serial_open` | `serial_open(port, baud [, config])` -> serial_port | Open a serial port |
| `serial_close` | `serial_close(port)` -> null | Close a serial port |
| `serial_write` | `serial_write(port, data)` -> integer | Write string/bytes to port |
| `serial_read` | `serial_read(port, count)` -> string | Read up to N bytes |
| `serial_read_line` | `serial_read_line(port)` -> string | Read until newline |
| `serial_available` | `serial_available(port)` -> boolean | Check if data is waiting |
| `serial_set_timeout` | `serial_set_timeout(port, ms)` -> null | Set read timeout |
| `serial_flush` | `serial_flush(port)` -> null | Flush I/O buffers |
| `serial_set_dtr` | `serial_set_dtr(port, state)` -> null | Control DTR line |
| `serial_set_rts` | `serial_set_rts(port, state)` -> null | Control RTS line |
| `serial_get_signals` | `serial_get_signals(port)` -> table | Read CTS/DSR/RI/CD status |

### Network Functions (Phase 4)

| Function | Signature | Description |
|----------|-----------|-------------|
| `net_connect` | `net_connect(host, port [, protocol])` -> net_conn | Connect to TCP/UDP host |
| `net_close` | `net_close(conn)` -> null | Close connection |
| `net_write` | `net_write(conn, data)` -> integer | Send data |
| `net_read` | `net_read(conn, count)` -> string | Read up to N bytes |
| `net_read_line` | `net_read_line(conn)` -> string | Read until newline |
| `net_set_timeout` | `net_set_timeout(conn, ms)` -> null | Set read timeout |
| `net_listen` | `net_listen(port [, protocol])` -> net_conn | Start TCP/UDP server |
| `net_accept` | `net_accept(listener)` -> net_conn | Accept incoming connection |

---

## 8. Session Continuity Notes

This section tracks progress across development sessions.

### Session 1 — 2026-02-13
- **Completed:** Codebase exploration, architecture analysis, plan creation
- **Next:** Begin Phase 1 (dependency + value type), then Phase 2 (core builtins)
- **Key files to have open:**
  - `internal/runtime/value.go` (add SerialPortValue)
  - `internal/runtime/builtins.go` (add serial builtins)
  - `go.mod` (add dependency)

### Session 2 — 2026-02-13
- **Completed:**
  - ✅ Phase 1: Added `go.bug.st/serial` dependency and `SerialPortValue` type
  - ✅ Phase 2: Implemented all 12 serial builtins
  - ✅ Created comprehensive unit tests in `builtins_serial_test.go`
  - ✅ Phase 3: Updated documentation (STDLIB.md, quick_reference.md, README.md)
  - ✅ Created example program `examples/nmea_reader.plain`
  - ✅ Phase 4: Implemented all 8 network builtins (TCP/UDP)
  - ✅ Added `NetConnValue` type to `value.go`
  - ✅ Created comprehensive unit tests in `builtins_net_test.go` (19 tests)
  - ✅ Updated documentation for network functions
  - ✅ All builds successful, all tests passing
- **Status:** Implementation plan complete! PLAIN now has full serial port and network I/O capabilities.

### Agent Context for Future Sessions

When resuming work on this plan, the agent needs to know:

1. **Project root:** `/home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/IDES/PLAIN`
2. **This plan:** `docs/IMPL-PLAN-serial-and-network.md`
3. **Builtin pattern:** Functions are entries in the `GetBuiltins()` map in `builtins.go`.
   Each is `"name": { Name: "name", Fn: func(args ...Value) Value { ... } }`
4. **Value type pattern:** Struct implementing `Type() string`, `String() string`, `IsTruthy() bool`
5. **Error pattern:** Return `NewError("funcname() message", args...)` for errors
6. **Build command:** `go build -o plain cmd/plain/main.go`
7. **Test command:** `go test ./internal/runtime/ -v`
8. **The serial library:** `go.bug.st/serial` — see https://pkg.go.dev/go.bug.st/serial

---

## 9. Risk Notes

- **First external dependency:** This breaks the zero-dependency record. Acceptable tradeoff
  for cross-platform serial support without hundreds of lines of platform-specific code.
- **Cross-platform serial port naming:** Linux uses `/dev/ttyUSB0`, `/dev/ttyACM0`, etc.
  macOS uses `/dev/cu.usbserial-*`. Windows uses `COM1`, `COM3`, etc. The `serial_ports()`
  discovery function handles this transparently.
- **Blocking reads:** Serial reads can block. The `serial_set_timeout()` function provides
  control. Users should be advised to always set a timeout in production code.
- **Virtual COM ports:** Work identically to physical ports from the OS perspective.
  No special handling needed — `serial_ports()` will list them alongside physical ports.
