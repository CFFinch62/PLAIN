//go:build !js

package runtime

import (
	"fmt"
	"os"

	"golang.org/x/term"
)

// rawModeState holds the saved terminal state for restoration after set_raw_mode().
var rawModeState *term.State

// getTUIBuiltins returns the native TUI built-in functions.
// These are only available in native builds; the WASM build returns nil.
func getTUIBuiltins() map[string]*BuiltinValue {
	return map[string]*BuiltinValue{

		// ============================================================
		// Screen Control
		// ============================================================

		// screen_size() -> [cols, rows]
		// Returns the current terminal dimensions. Returns [80, 24] if
		// detection fails (e.g., stdout is redirected).
		"screen_size": {
			Name: "screen_size",
			Fn: func(args ...Value) Value {
				if PlaygroundMode {
					return playgroundUnavailable("screen_size")
				}
				cols, rows, err := term.GetSize(int(os.Stdout.Fd()))
				if err != nil {
					return NewList([]Value{NewInteger(80), NewInteger(24)})
				}
				return NewList([]Value{NewInteger(int64(cols)), NewInteger(int64(rows))})
			},
		},

		// screen_alt() - switch to the terminal alternate screen buffer.
		// Saves the current screen contents so they are restored on screen_main().
		// Use this at the start of a full-screen TUI application.
		"screen_alt": {
			Name: "screen_alt",
			Fn: func(args ...Value) Value {
				if PlaygroundMode {
					return playgroundUnavailable("screen_alt")
				}
				PrintFunc("\033[?1049h")
				return NULL
			},
		},

		// screen_main() - restore the main screen buffer.
		// Undoes screen_alt(), restoring the terminal to its prior state.
		"screen_main": {
			Name: "screen_main",
			Fn: func(args ...Value) Value {
				if PlaygroundMode {
					return playgroundUnavailable("screen_main")
				}
				PrintFunc("\033[?1049l")
				return NULL
			},
		},

		// ============================================================
		// Cursor Control
		// ============================================================

		// cursor_show() - make the terminal cursor visible.
		"cursor_show": {
			Name: "cursor_show",
			Fn: func(args ...Value) Value {
				PrintFunc("\033[?25h")
				return NULL
			},
		},

		// cursor_hide() - make the terminal cursor invisible.
		// Useful for TUI rendering loops to prevent cursor flicker.
		"cursor_hide": {
			Name: "cursor_hide",
			Fn: func(args ...Value) Value {
				PrintFunc("\033[?25l")
				return NULL
			},
		},

		// cursor_pos(x, y) - move the cursor to (x, y) without printing text.
		// Coordinates are 1-based (top-left is 1, 1).
		"cursor_pos": {
			Name: "cursor_pos",
			Fn: func(args ...Value) Value {
				if len(args) != 2 {
					return NewError("cursor_pos() takes 2 arguments: x, y")
				}
				xVal, ok := args[0].(*IntegerValue)
				if !ok {
					return NewError("cursor_pos() x must be an integer")
				}
				yVal, ok := args[1].(*IntegerValue)
				if !ok {
					return NewError("cursor_pos() y must be an integer")
				}
				PrintFunc(fmt.Sprintf("\033[%d;%dH", yVal.Val, xVal.Val))
				return NULL
			},
		},

		// ============================================================
		// Raw Mode
		// ============================================================

		// set_raw_mode() - put the terminal into raw input mode.
		// In raw mode: keypresses are delivered immediately (no line buffering),
		// echo is disabled, and special keys (arrows, F-keys, etc.) are readable
		// via get_key() or get_event(). Always call set_cooked_mode() before exit.
		"set_raw_mode": {
			Name: "set_raw_mode",
			Fn: func(args ...Value) Value {
				if PlaygroundMode {
					return playgroundUnavailable("set_raw_mode")
				}
				state, err := term.MakeRaw(int(os.Stdin.Fd()))
				if err != nil {
					return NewError("set_raw_mode() failed: %s", err.Error())
				}
				rawModeState = state
				return NULL
			},
		},

		// set_cooked_mode() - restore normal terminal input mode.
		// Must be called before program exit if set_raw_mode() was used,
		// otherwise the terminal is left in an unusable state.
		"set_cooked_mode": {
			Name: "set_cooked_mode",
			Fn: func(args ...Value) Value {
				if PlaygroundMode {
					return playgroundUnavailable("set_cooked_mode")
				}
				if rawModeState == nil {
					return NULL
				}
				if err := term.Restore(int(os.Stdin.Fd()), rawModeState); err != nil {
					return NewError("set_cooked_mode() failed: %s", err.Error())
				}
				rawModeState = nil
				return NULL
			},
		},

		// ============================================================
		// Keyboard Input
		// ============================================================

		// get_key() -> string
		// Blocks until the user presses a key and returns its name.
		// Requires set_raw_mode() to be active. Mouse events are discarded.
		//
		// Printable keys:  "a", "A", "1", "!", etc.
		// Special keys:    "ENTER", "TAB", "BACKSPACE", "SPACE", "ESCAPE"
		// Arrow keys:      "UP", "DOWN", "LEFT", "RIGHT"
		// Navigation:      "HOME", "END", "PGUP", "PGDN", "INS", "DEL"
		// Function keys:   "F1" through "F12"
		// Shifted:         "SHIFT_TAB"
		// Control keys:    "CTRL_A" through "CTRL_Z"
		"get_key": {
			Name: "get_key",
			Fn: func(args ...Value) Value {
				if PlaygroundMode {
					return playgroundUnavailable("get_key")
				}
				for {
					key, isMouse, _, err := readInputEvent()
					if err != nil {
						return NewError("get_key() failed: %s", err.Error())
					}
					if !isMouse {
						return NewString(key)
					}
				}
			},
		},

		// get_event() -> table
		// Blocks until the next keyboard or mouse event and returns a table.
		// Requires set_raw_mode(). For mouse events, mouse_enable() must also
		// have been called.
		//
		// Key event:   {type: "key", key: "UP"}
		// Mouse event: {type: "mouse", action: "press"|"release"|"move",
		//               button: "left"|"middle"|"right"|"none", x: col, y: row}
		"get_event": {
			Name: "get_event",
			Fn: func(args ...Value) Value {
				if PlaygroundMode {
					return playgroundUnavailable("get_event")
				}
				key, isMouse, mouseData, err := readInputEvent()
				if err != nil {
					return NewError("get_event() failed: %s", err.Error())
				}
				if isMouse {
					return mouseData
				}
				return NewTable(map[string]Value{
					"type": NewString("key"),
					"key":  NewString(key),
				})
			},
		},

		// ============================================================
		// Mouse
		// ============================================================

		// mouse_enable() - enable terminal mouse event reporting.
		// After calling this, mouse clicks and releases are delivered as
		// escape sequences readable via get_event(). Use with set_raw_mode().
		"mouse_enable": {
			Name: "mouse_enable",
			Fn: func(args ...Value) Value {
				if PlaygroundMode {
					return playgroundUnavailable("mouse_enable")
				}
				// Enable button events with SGR extended coordinates (1006)
				PrintFunc("\033[?1000h\033[?1006h")
				return NULL
			},
		},

		// mouse_disable() - disable terminal mouse event reporting.
		"mouse_disable": {
			Name: "mouse_disable",
			Fn: func(args ...Value) Value {
				if PlaygroundMode {
					return playgroundUnavailable("mouse_disable")
				}
				PrintFunc("\033[?1006l\033[?1000l")
				return NULL
			},
		},

		// ============================================================
		// Text Attributes
		// ============================================================

		// text_reset() - clear all text attributes (color, bold, underline, etc.)
		"text_reset": {
			Name: "text_reset",
			Fn: func(args ...Value) Value {
				PrintFunc("\033[0m")
				return NULL
			},
		},

		// text_bold() - enable bold / bright text
		"text_bold": {
			Name: "text_bold",
			Fn: func(args ...Value) Value {
				PrintFunc("\033[1m")
				return NULL
			},
		},

		// text_dim() - enable dim / faint text
		"text_dim": {
			Name: "text_dim",
			Fn: func(args ...Value) Value {
				PrintFunc("\033[2m")
				return NULL
			},
		},

		// text_italic() - enable italic text
		"text_italic": {
			Name: "text_italic",
			Fn: func(args ...Value) Value {
				PrintFunc("\033[3m")
				return NULL
			},
		},

		// text_underline() - enable underlined text
		"text_underline": {
			Name: "text_underline",
			Fn: func(args ...Value) Value {
				PrintFunc("\033[4m")
				return NULL
			},
		},

		// text_blink() - enable blinking text
		"text_blink": {
			Name: "text_blink",
			Fn: func(args ...Value) Value {
				PrintFunc("\033[5m")
				return NULL
			},
		},

		// text_reverse() - swap foreground and background colors
		"text_reverse": {
			Name: "text_reverse",
			Fn: func(args ...Value) Value {
				PrintFunc("\033[7m")
				return NULL
			},
		},

		// text_strike() - enable strikethrough text
		"text_strike": {
			Name: "text_strike",
			Fn: func(args ...Value) Value {
				PrintFunc("\033[9m")
				return NULL
			},
		},

		// ============================================================
		// Extended Color
		// ============================================================

		// text_color_256(fg [, bg]) - set 256-color palette colors.
		// fg and bg are palette indices 0-255.
		// Colors 0-7: standard, 8-15: bright, 16-231: 6x6x6 RGB cube,
		// 232-255: grayscale ramp.
		"text_color_256": {
			Name: "text_color_256",
			Fn: func(args ...Value) Value {
				if len(args) < 1 || len(args) > 2 {
					return NewError("text_color_256() takes 1 or 2 arguments: fg [, bg]")
				}
				fgVal, ok := args[0].(*IntegerValue)
				if !ok || fgVal.Val < 0 || fgVal.Val > 255 {
					return NewError("text_color_256() fg must be an integer 0-255")
				}
				PrintFunc(fmt.Sprintf("\033[38;5;%dm", fgVal.Val))
				if len(args) == 2 {
					bgVal, ok := args[1].(*IntegerValue)
					if !ok || bgVal.Val < 0 || bgVal.Val > 255 {
						return NewError("text_color_256() bg must be an integer 0-255")
					}
					PrintFunc(fmt.Sprintf("\033[48;5;%dm", bgVal.Val))
				}
				return NULL
			},
		},

		// text_color_rgb(r, g, b [, br, bg, bb]) - set 24-bit true color.
		// r, g, b are foreground RGB values (0-255).
		// Optional br, bg, bb are background RGB values (0-255).
		"text_color_rgb": {
			Name: "text_color_rgb",
			Fn: func(args ...Value) Value {
				if len(args) != 3 && len(args) != 6 {
					return NewError("text_color_rgb() takes 3 or 6 arguments: r, g, b [, br, bg, bb]")
				}
				r, g, b, err := extractRGB(args[0], args[1], args[2])
				if err != nil {
					return NewError("text_color_rgb() foreground: %s", err.Error())
				}
				PrintFunc(fmt.Sprintf("\033[38;2;%d;%d;%dm", r, g, b))
				if len(args) == 6 {
					br, bg, bb, err := extractRGB(args[3], args[4], args[5])
					if err != nil {
						return NewError("text_color_rgb() background: %s", err.Error())
					}
					PrintFunc(fmt.Sprintf("\033[48;2;%d;%d;%dm", br, bg, bb))
				}
				return NULL
			},
		},
	}
}

// extractRGB validates and extracts three 0-255 integer values for an RGB color.
func extractRGB(rv, gv, bv Value) (int64, int64, int64, error) {
	r, ok := rv.(*IntegerValue)
	if !ok || r.Val < 0 || r.Val > 255 {
		return 0, 0, 0, fmt.Errorf("r must be an integer 0-255")
	}
	g, ok := gv.(*IntegerValue)
	if !ok || g.Val < 0 || g.Val > 255 {
		return 0, 0, 0, fmt.Errorf("g must be an integer 0-255")
	}
	b, ok := bv.(*IntegerValue)
	if !ok || b.Val < 0 || b.Val > 255 {
		return 0, 0, 0, fmt.Errorf("b must be an integer 0-255")
	}
	return r.Val, g.Val, b.Val, nil
}

// readInputEvent reads one keyboard or mouse event from stdin.
// Returns the key name string, whether it is a mouse event, the mouse table
// value (when isMouse is true), and any read error.
//
// In raw mode, terminal emulators deliver escape sequences atomically, so a
// single Read call typically returns the full multi-byte sequence for special
// keys, arrow keys, and mouse events.
func readInputEvent() (key string, isMouse bool, mouseData Value, err error) {
	buf := make([]byte, 32)
	n, readErr := os.Stdin.Read(buf)
	if readErr != nil {
		return "", false, NULL, readErr
	}
	return decodeInputBytes(buf[:n])
}

// decodeInputBytes converts raw stdin bytes into a key name or mouse event.
func decodeInputBytes(b []byte) (string, bool, Value, error) {
	if len(b) == 0 {
		return "", false, NULL, nil
	}

	// SGR mouse: ESC [ < params M/m
	if len(b) >= 6 && b[0] == 0x1B && b[1] == '[' && b[2] == '<' {
		return decodeSGRMouse(b)
	}

	// Legacy X10 mouse: ESC [ M + 3 bytes
	if len(b) >= 6 && b[0] == 0x1B && b[1] == '[' && b[2] == 'M' {
		return decodeLegacyMouse(b[3:])
	}

	// Single byte
	if len(b) == 1 {
		return decodeSingleByte(b[0]), false, NULL, nil
	}

	// Escape sequence
	if b[0] == 0x1B {
		if len(b) >= 2 && b[1] == '[' {
			return decodeCSI(b[2:]), false, NULL, nil
		}
		if len(b) >= 2 && b[1] == 'O' {
			return decodeApplicationKey(b[2:]), false, NULL, nil
		}
		return "ESCAPE", false, NULL, nil
	}

	// Multi-byte UTF-8 character or other sequence
	return string(b), false, NULL, nil
}

func decodeSingleByte(b byte) string {
	switch b {
	case 0x0D, 0x0A:
		return "ENTER"
	case 0x09:
		return "TAB"
	case 0x7F, 0x08:
		return "BACKSPACE"
	case 0x20:
		return "SPACE"
	case 0x1B:
		return "ESCAPE"
	default:
		if b < 0x20 {
			return fmt.Sprintf("CTRL_%c", b+64)
		}
		return string([]byte{b})
	}
}

// decodeCSI decodes the payload after ESC [ into a key name.
func decodeCSI(seq []byte) string {
	if len(seq) == 0 {
		return "ESCAPE"
	}
	switch seq[0] {
	case 'A':
		return "UP"
	case 'B':
		return "DOWN"
	case 'C':
		return "RIGHT"
	case 'D':
		return "LEFT"
	case 'H':
		return "HOME"
	case 'F':
		return "END"
	case 'Z':
		return "SHIFT_TAB"
	case 'P':
		return "F1"
	case 'Q':
		return "F2"
	case 'R':
		return "F3"
	case 'S':
		return "F4"
	}
	// Tilde-terminated sequences: number ~
	if len(seq) >= 2 && seq[len(seq)-1] == '~' {
		switch string(seq[:len(seq)-1]) {
		case "2":
			return "INS"
		case "3":
			return "DEL"
		case "5":
			return "PGUP"
		case "6":
			return "PGDN"
		case "15":
			return "F5"
		case "17":
			return "F6"
		case "18":
			return "F7"
		case "19":
			return "F8"
		case "20":
			return "F9"
		case "21":
			return "F10"
		case "23":
			return "F11"
		case "24":
			return "F12"
		}
	}
	return fmt.Sprintf("ESC[%s", string(seq))
}

// decodeApplicationKey decodes the payload after ESC O into a key name.
func decodeApplicationKey(seq []byte) string {
	if len(seq) == 0 {
		return "ESCAPE"
	}
	switch seq[0] {
	case 'P':
		return "F1"
	case 'Q':
		return "F2"
	case 'R':
		return "F3"
	case 'S':
		return "F4"
	case 'H':
		return "HOME"
	case 'F':
		return "END"
	}
	return fmt.Sprintf("ESCO%s", string(seq))
}

// decodeSGRMouse parses an SGR extended mouse event: ESC [ < params M/m
func decodeSGRMouse(b []byte) (string, bool, Value, error) {
	s := string(b[3:])
	if len(s) == 0 {
		return "", false, NULL, fmt.Errorf("invalid SGR mouse sequence")
	}
	last := s[len(s)-1]
	released := last == 'm'
	params := s[:len(s)-1]

	var btnCode, x, y int
	fmt.Sscanf(params, "%d;%d;%d", &btnCode, &x, &y)

	action := "press"
	if released {
		action = "release"
	} else if btnCode&32 != 0 {
		action = "move"
	}

	button := decodeSGRButton(btnCode & 3)
	return "", true, NewTable(map[string]Value{
		"type":   NewString("mouse"),
		"action": NewString(action),
		"button": NewString(button),
		"x":      NewInteger(int64(x)),
		"y":      NewInteger(int64(y)),
	}), nil
}

// decodeLegacyMouse parses a legacy X10 mouse event (3 bytes after ESC [ M).
func decodeLegacyMouse(b []byte) (string, bool, Value, error) {
	if len(b) < 3 {
		return "", false, NULL, fmt.Errorf("incomplete legacy mouse sequence")
	}
	btnCode := int(b[0]) - 32
	x := int(b[1]) - 32
	y := int(b[2]) - 32

	action := "press"
	buttonName := decodeSGRButton(btnCode & 3)
	if btnCode&3 == 3 {
		action = "release"
		buttonName = "none"
	}

	return "", true, NewTable(map[string]Value{
		"type":   NewString("mouse"),
		"action": NewString(action),
		"button": NewString(buttonName),
		"x":      NewInteger(int64(x)),
		"y":      NewInteger(int64(y)),
	}), nil
}

func decodeSGRButton(code int) string {
	switch code {
	case 0:
		return "left"
	case 1:
		return "middle"
	case 2:
		return "right"
	default:
		return "none"
	}
}
