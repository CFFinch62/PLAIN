package runtime

import "fmt"

// PrintFunc is the package-level output function.
// All PLAIN output (display, get prompts, clear, TUI) routes through here.
// Default writes to stdout; replaced by io_wasm.go for browser builds.
var PrintFunc func(string) = func(s string) { fmt.Print(s) }

// InputFunc is the package-level input function.
// Called by the get() builtin. The argument is the prompt string.
// Returns the line the user entered (without trailing newline).
// Set by io_native.go (stdin scanner) or io_wasm.go (input queue).
var InputFunc func(string) string

// PlaygroundMode disables browser-incompatible features when true.
// When enabled: file I/O, serial, network, and use: imports all return
// a friendly "not available in playground" error message.
// Set to true by the WASM entry point (cmd/plain-wasm/main.go).
var PlaygroundMode bool

// playgroundUnavailable returns a consistent error for features that
// are not supported in the web playground.
func playgroundUnavailable(name string) Value {
	return NewError(
		"%s() is not available in the web playground.\n"+
			"Download the desktop app for the full PLAIN experience.",
		name,
	)
}
