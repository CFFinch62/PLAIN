//go:build !js

package runtime

import (
	"bufio"
	"strings"
	"time"

	"go.bug.st/serial"
)

func getSerialBuiltins() map[string]*BuiltinValue {
	return map[string]*BuiltinValue{
		// ============================================================
		// Serial Port I/O
		// ============================================================
		"serial_ports": {
			Name: "serial_ports",
			Fn: func(args ...Value) Value {
				if len(args) != 0 {
					return NewError("serial_ports() takes no arguments")
				}
				ports, err := serial.GetPortsList()
				if err != nil {
					return NewError("serial_ports() failed: %s", err.Error())
				}
				elements := make([]Value, len(ports))
				for i, p := range ports {
					elements[i] = NewString(p)
				}
				return NewList(elements)
			},
		},
		"serial_open": {
			Name: "serial_open",
			Fn: func(args ...Value) Value {
				if len(args) < 2 || len(args) > 3 {
					return NewError("serial_open() takes 2 or 3 arguments (port, baud [, config])")
				}
				portName, ok := args[0].(*StringValue)
				if !ok {
					return NewError("serial_open() first argument must be a string (port name)")
				}
				baudArg, ok := args[1].(*IntegerValue)
				if !ok {
					return NewError("serial_open() second argument must be an integer (baud rate)")
				}
				configStr := "8N1"
				if len(args) == 3 {
					cfgVal, ok := args[2].(*StringValue)
					if !ok {
						return NewError("serial_open() third argument must be a string (config, e.g. \"8N1\")")
					}
					configStr = cfgVal.Val
				}
				// Parse config string (e.g. "8N1")
				if len(configStr) != 3 {
					return NewError("serial_open() config must be 3 characters: data_bits + parity + stop_bits (e.g. \"8N1\")")
				}
				var dataBits int
				switch configStr[0] {
				case '5':
					dataBits = 5
				case '6':
					dataBits = 6
				case '7':
					dataBits = 7
				case '8':
					dataBits = 8
				default:
					return NewError("serial_open() invalid data bits '%c' (use 5, 6, 7, or 8)", configStr[0])
				}
				var parity serial.Parity
				switch configStr[1] {
				case 'N', 'n':
					parity = serial.NoParity
				case 'E', 'e':
					parity = serial.EvenParity
				case 'O', 'o':
					parity = serial.OddParity
				case 'M', 'm':
					parity = serial.MarkParity
				case 'S', 's':
					parity = serial.SpaceParity
				default:
					return NewError("serial_open() invalid parity '%c' (use N, E, O, M, or S)", configStr[1])
				}
				var stopBits serial.StopBits
				switch configStr[2] {
				case '1':
					stopBits = serial.OneStopBit
				case '2':
					stopBits = serial.TwoStopBits
				default:
					return NewError("serial_open() invalid stop bits '%c' (use 1 or 2)", configStr[2])
				}
				mode := &serial.Mode{
					BaudRate: int(baudArg.Val),
					DataBits: dataBits,
					Parity:   parity,
					StopBits: stopBits,
				}
				port, err := serial.Open(portName.Val, mode)
				if err != nil {
					return NewError("serial_open() failed: %s", err.Error())
				}
				reader := bufio.NewReader(port)
				return &SerialPortValue{
					PortName: portName.Val,
					BaudRate: int(baudArg.Val),
					Config:   configStr,
					Handle:   port,
					Reader:   reader,
					IsOpen:   true,
				}
			},
		},
		"serial_close": {
			Name: "serial_close",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("serial_close() takes exactly 1 argument")
				}
				sp, ok := args[0].(*SerialPortValue)
				if !ok {
					return NewError("serial_close() argument must be a serial port handle")
				}
				if !sp.IsOpen {
					return NewError("serial_close() port already closed")
				}
				port := sp.Handle.(serial.Port)
				err := port.Close()
				sp.IsOpen = false
				sp.Handle = nil
				sp.Reader = nil
				if err != nil {
					return NewError("serial_close() failed: %s", err.Error())
				}
				return NULL
			},
		},
		"serial_write": {
			Name: "serial_write",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("serial_write() takes exactly 2 arguments (port, data)")
				}
				sp, ok := args[0].(*SerialPortValue)
				if !ok {
					return NewError("serial_write() first argument must be a serial port handle")
				}
				if !sp.IsOpen {
					return NewError("serial_write() port is closed")
				}
				port := sp.Handle.(serial.Port)
				var data []byte
				switch v := args[1].(type) {
				case *StringValue:
					data = []byte(v.Val)
				case *BytesValue:
					data = v.Data
				default:
					return NewError("serial_write() second argument must be a string or bytes")
				}
				n, err := port.Write(data)
				if err != nil {
					return NewError("serial_write() failed: %s", err.Error())
				}
				return NewInteger(int64(n))
			},
		},
		"serial_read": {
			Name: "serial_read",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("serial_read() takes exactly 2 arguments (port, count)")
				}
				sp, ok := args[0].(*SerialPortValue)
				if !ok {
					return NewError("serial_read() first argument must be a serial port handle")
				}
				if !sp.IsOpen {
					return NewError("serial_read() port is closed")
				}
				count, ok := args[1].(*IntegerValue)
				if !ok {
					return NewError("serial_read() second argument must be an integer (byte count)")
				}
				if count.Val <= 0 {
					return NewError("serial_read() count must be positive")
				}
				port := sp.Handle.(serial.Port)
				buf := make([]byte, count.Val)
				n, err := port.Read(buf)
				if err != nil {
					return NewError("serial_read() failed: %s", err.Error())
				}
				return NewString(string(buf[:n]))
			},
		},
		"serial_read_line": {
			Name: "serial_read_line",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("serial_read_line() takes exactly 1 argument")
				}
				sp, ok := args[0].(*SerialPortValue)
				if !ok {
					return NewError("serial_read_line() argument must be a serial port handle")
				}
				if !sp.IsOpen {
					return NewError("serial_read_line() port is closed")
				}
				reader := sp.Reader.(*bufio.Reader)
				line, err := reader.ReadString('\n')
				if err != nil {
					return NewError("serial_read_line() failed: %s", err.Error())
				}
				// Trim trailing \r\n or \n
				line = strings.TrimRight(line, "\r\n")
				return NewString(line)
			},
		},
		"serial_available": {
			Name: "serial_available",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("serial_available() takes exactly 1 argument")
				}
				sp, ok := args[0].(*SerialPortValue)
				if !ok {
					return NewError("serial_available() argument must be a serial port handle")
				}
				if !sp.IsOpen {
					return NewError("serial_available() port is closed")
				}
				reader := sp.Reader.(*bufio.Reader)
				return NewBoolean(reader.Buffered() > 0)
			},
		},
		"serial_set_timeout": {
			Name: "serial_set_timeout",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("serial_set_timeout() takes exactly 2 arguments (port, milliseconds)")
				}
				sp, ok := args[0].(*SerialPortValue)
				if !ok {
					return NewError("serial_set_timeout() first argument must be a serial port handle")
				}
				if !sp.IsOpen {
					return NewError("serial_set_timeout() port is closed")
				}
				ms, ok := args[1].(*IntegerValue)
				if !ok {
					return NewError("serial_set_timeout() second argument must be an integer (milliseconds)")
				}
				port := sp.Handle.(serial.Port)
				var timeout time.Duration
				if ms.Val < 0 {
					// Negative = block forever (effectively very long timeout)
					timeout = time.Duration(0)
				} else if ms.Val == 0 {
					// Zero = non-blocking: use 1ms minimum
					timeout = time.Millisecond
				} else {
					timeout = time.Duration(ms.Val) * time.Millisecond
				}
				err := port.SetReadTimeout(timeout)
				if err != nil {
					return NewError("serial_set_timeout() failed: %s", err.Error())
				}
				return NULL
			},
		},
		"serial_flush": {
			Name: "serial_flush",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("serial_flush() takes exactly 1 argument")
				}
				sp, ok := args[0].(*SerialPortValue)
				if !ok {
					return NewError("serial_flush() argument must be a serial port handle")
				}
				if !sp.IsOpen {
					return NewError("serial_flush() port is closed")
				}
				port := sp.Handle.(serial.Port)
				err := port.ResetInputBuffer()
				if err != nil {
					return NewError("serial_flush() failed to flush input: %s", err.Error())
				}
				err = port.ResetOutputBuffer()
				if err != nil {
					return NewError("serial_flush() failed to flush output: %s", err.Error())
				}
				// Also reset the buffered reader since we flushed the input
				sp.Reader = bufio.NewReader(port)
				return NULL
			},
		},
		"serial_set_dtr": {
			Name: "serial_set_dtr",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("serial_set_dtr() takes exactly 2 arguments (port, state)")
				}
				sp, ok := args[0].(*SerialPortValue)
				if !ok {
					return NewError("serial_set_dtr() first argument must be a serial port handle")
				}
				if !sp.IsOpen {
					return NewError("serial_set_dtr() port is closed")
				}
				state, ok := args[1].(*BooleanValue)
				if !ok {
					return NewError("serial_set_dtr() second argument must be a boolean")
				}
				port := sp.Handle.(serial.Port)
				err := port.SetDTR(state.Val)
				if err != nil {
					return NewError("serial_set_dtr() failed: %s", err.Error())
				}
				return NULL
			},
		},
		"serial_set_rts": {
			Name: "serial_set_rts",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("serial_set_rts() takes exactly 2 arguments (port, state)")
				}
				sp, ok := args[0].(*SerialPortValue)
				if !ok {
					return NewError("serial_set_rts() first argument must be a serial port handle")
				}
				if !sp.IsOpen {
					return NewError("serial_set_rts() port is closed")
				}
				state, ok := args[1].(*BooleanValue)
				if !ok {
					return NewError("serial_set_rts() second argument must be a boolean")
				}
				port := sp.Handle.(serial.Port)
				err := port.SetRTS(state.Val)
				if err != nil {
					return NewError("serial_set_rts() failed: %s", err.Error())
				}
				return NULL
			},
		},
		"serial_get_signals": {
			Name: "serial_get_signals",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("serial_get_signals() takes exactly 1 argument")
				}
				sp, ok := args[0].(*SerialPortValue)
				if !ok {
					return NewError("serial_get_signals() argument must be a serial port handle")
				}
				if !sp.IsOpen {
					return NewError("serial_get_signals() port is closed")
				}
				port := sp.Handle.(serial.Port)
				status, err := port.GetModemStatusBits()
				if err != nil {
					return NewError("serial_get_signals() failed: %s", err.Error())
				}
				pairs := map[string]Value{
					"cts": NewBoolean(status.CTS),
					"dsr": NewBoolean(status.DSR),
					"ri":  NewBoolean(status.RI),
					"dcd": NewBoolean(status.DCD),
				}
				return NewTable(pairs)
			},
		},

	}
}
