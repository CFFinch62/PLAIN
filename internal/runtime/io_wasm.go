//go:build js && wasm

package runtime

import (
	"strings"
	"sync"
)

var (
	outputMu  sync.Mutex
	outputBuf strings.Builder
	inputLines []string
	inputIdx   int
)

// SetInputLines loads the pre-supplied input queue before running a program.
// Lines are consumed one-by-one each time get() is called.
func SetInputLines(lines []string) {
	inputLines = lines
	inputIdx = 0
}

// GetOutput returns all captured program output and resets the buffer.
// Call this after RunProgram() to retrieve what the program printed.
func GetOutput() string {
	outputMu.Lock()
	defer outputMu.Unlock()
	s := outputBuf.String()
	outputBuf.Reset()
	return s
}

func init() {
	// Route all PLAIN output into the in-memory buffer.
	PrintFunc = func(s string) {
		outputMu.Lock()
		outputBuf.WriteString(s)
		outputMu.Unlock()
	}

	// Serve get() prompts from the pre-supplied input queue.
	// The prompt and the echoed answer are both written to the output buffer
	// so the user can see a natural-looking conversation in the output panel.
	InputFunc = func(prompt string) string {
		if prompt != "" {
			PrintFunc(prompt)
		}
		if inputIdx < len(inputLines) {
			line := inputLines[inputIdx]
			inputIdx++
			PrintFunc(line + "\n") // echo the supplied answer
			return line
		}
		// Input queue exhausted — return empty string and note it.
		PrintFunc("[no more input]\n")
		return ""
	}
}

