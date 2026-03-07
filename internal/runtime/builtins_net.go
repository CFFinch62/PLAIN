//go:build !js

package runtime

import (
	"bufio"
	"fmt"
	"net"
	"strings"
	"time"
)

func getNetBuiltins() map[string]*BuiltinValue {
	return map[string]*BuiltinValue{
		// ============================================================
		// Network I/O (TCP/UDP)
		// ============================================================
		"net_connect": {
			Name: "net_connect",
			Fn: func(args ...Value) Value {
				if len(args) < 2 || len(args) > 3 {
					return NewError("net_connect() takes 2 or 3 arguments (host, port [, protocol])")
				}
				host, ok := args[0].(*StringValue)
				if !ok {
					return NewError("net_connect() first argument must be a string (host)")
				}
				portArg, ok := args[1].(*IntegerValue)
				if !ok {
					return NewError("net_connect() second argument must be an integer (port)")
				}
				protocol := "tcp"
				if len(args) == 3 {
					protoVal, ok := args[2].(*StringValue)
					if !ok {
						return NewError("net_connect() third argument must be a string (protocol: \"tcp\" or \"udp\")")
					}
					protocol = strings.ToLower(protoVal.Val)
					if protocol != "tcp" && protocol != "udp" {
						return NewError("net_connect() protocol must be \"tcp\" or \"udp\"")
					}
				}
				address := fmt.Sprintf("%s:%d", host.Val, portArg.Val)
				conn, err := net.Dial(protocol, address)
				if err != nil {
					return NewError("net_connect() failed: %s", err.Error())
				}
				reader := bufio.NewReader(conn)
				return &NetConnValue{
					Address:  address,
					Protocol: protocol,
					Handle:   conn,
					Reader:   reader,
					IsOpen:   true,
					IsServer: false,
				}
			},
		},
		"net_close": {
			Name: "net_close",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("net_close() takes exactly 1 argument")
				}
				nc, ok := args[0].(*NetConnValue)
				if !ok {
					return NewError("net_close() argument must be a network connection handle")
				}
				if !nc.IsOpen {
					return NewError("net_close() connection already closed")
				}
				conn := nc.Handle.(net.Conn)
				nc.IsOpen = false
				nc.Handle = nil
				nc.Reader = nil
				err := conn.Close()
				if err != nil {
					return NewError("net_close() failed: %s", err.Error())
				}
				return NULL
			},
		},
		"net_write": {
			Name: "net_write",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("net_write() takes exactly 2 arguments (conn, data)")
				}
				nc, ok := args[0].(*NetConnValue)
				if !ok {
					return NewError("net_write() first argument must be a network connection handle")
				}
				if !nc.IsOpen {
					return NewError("net_write() connection is closed")
				}
				conn := nc.Handle.(net.Conn)
				var data []byte
				switch v := args[1].(type) {
				case *StringValue:
					data = []byte(v.Val)
				case *BytesValue:
					data = v.Data
				default:
					return NewError("net_write() second argument must be a string or bytes")
				}
				n, err := conn.Write(data)
				if err != nil {
					return NewError("net_write() failed: %s", err.Error())
				}
				return NewInteger(int64(n))
			},
		},
		"net_read": {
			Name: "net_read",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("net_read() takes exactly 2 arguments (conn, count)")
				}
				nc, ok := args[0].(*NetConnValue)
				if !ok {
					return NewError("net_read() first argument must be a network connection handle")
				}
				if !nc.IsOpen {
					return NewError("net_read() connection is closed")
				}
				count, ok := args[1].(*IntegerValue)
				if !ok {
					return NewError("net_read() second argument must be an integer (byte count)")
				}
				if count.Val <= 0 {
					return NewError("net_read() count must be positive")
				}
				conn := nc.Handle.(net.Conn)
				buf := make([]byte, count.Val)
				n, err := conn.Read(buf)
				if err != nil {
					return NewError("net_read() failed: %s", err.Error())
				}
				return NewString(string(buf[:n]))
			},
		},
		"net_read_line": {
			Name: "net_read_line",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("net_read_line() takes exactly 1 argument")
				}
				nc, ok := args[0].(*NetConnValue)
				if !ok {
					return NewError("net_read_line() argument must be a network connection handle")
				}
				if !nc.IsOpen {
					return NewError("net_read_line() connection is closed")
				}
				reader := nc.Reader.(*bufio.Reader)
				line, err := reader.ReadString('\n')
				if err != nil {
					return NewError("net_read_line() failed: %s", err.Error())
				}
				// Trim trailing \r\n or \n
				line = strings.TrimRight(line, "\r\n")
				return NewString(line)
			},
		},
		"net_set_timeout": {
			Name: "net_set_timeout",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("net_set_timeout() takes exactly 2 arguments (conn, milliseconds)")
				}
				nc, ok := args[0].(*NetConnValue)
				if !ok {
					return NewError("net_set_timeout() first argument must be a network connection handle")
				}
				if !nc.IsOpen {
					return NewError("net_set_timeout() connection is closed")
				}
				ms, ok := args[1].(*IntegerValue)
				if !ok {
					return NewError("net_set_timeout() second argument must be an integer (milliseconds)")
				}
				conn := nc.Handle.(net.Conn)
				var timeout time.Duration
				if ms.Val < 0 {
					// -1 means block forever (no timeout)
					timeout = 0
				} else if ms.Val == 0 {
					// 0 means non-blocking (immediate timeout)
					timeout = 1 * time.Nanosecond
				} else {
					timeout = time.Duration(ms.Val) * time.Millisecond
				}
				err := conn.SetReadDeadline(time.Now().Add(timeout))
				if err != nil {
					return NewError("net_set_timeout() failed: %s", err.Error())
				}
				return NULL
			},
		},
		"net_listen": {
			Name: "net_listen",
			Fn: func(args ...Value) Value {
				if len(args) < 1 || len(args) > 2 {
					return NewError("net_listen() takes 1 or 2 arguments (port [, protocol])")
				}
				portArg, ok := args[0].(*IntegerValue)
				if !ok {
					return NewError("net_listen() first argument must be an integer (port)")
				}
				protocol := "tcp"
				if len(args) == 2 {
					protoVal, ok := args[1].(*StringValue)
					if !ok {
						return NewError("net_listen() second argument must be a string (protocol: \"tcp\" or \"udp\")")
					}
					protocol = strings.ToLower(protoVal.Val)
					if protocol != "tcp" && protocol != "udp" {
						return NewError("net_listen() protocol must be \"tcp\" or \"udp\"")
					}
				}
				address := fmt.Sprintf(":%d", portArg.Val)
				listener, err := net.Listen(protocol, address)
				if err != nil {
					return NewError("net_listen() failed: %s", err.Error())
				}
				return &NetConnValue{
					Address:  address,
					Protocol: protocol,
					Handle:   listener,
					Reader:   nil,
					IsOpen:   true,
					IsServer: true,
				}
			},
		},
		"net_accept": {
			Name: "net_accept",
			Fn: func(args ...Value) Value {
				if len(args) != 1 {
					return NewError("net_accept() takes exactly 1 argument")
				}
				nc, ok := args[0].(*NetConnValue)
				if !ok {
					return NewError("net_accept() argument must be a network connection handle")
				}
				if !nc.IsServer {
					return NewError("net_accept() can only be called on a listener")
				}
				if !nc.IsOpen {
					return NewError("net_accept() listener is closed")
				}
				listener := nc.Handle.(net.Listener)
				conn, err := listener.Accept()
				if err != nil {
					return NewError("net_accept() failed: %s", err.Error())
				}
				reader := bufio.NewReader(conn)
				return &NetConnValue{
					Address:  conn.RemoteAddr().String(),
					Protocol: nc.Protocol,
					Handle:   conn,
					Reader:   reader,
					IsOpen:   true,
					IsServer: false,
				}
			},
		},
	}
}
