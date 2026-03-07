//go:build !js

package runtime

import (
	"bufio"
	"os"
)

func init() {
	scanner := bufio.NewScanner(os.Stdin)
	InputFunc = func(prompt string) string {
		if prompt != "" {
			PrintFunc(prompt)
		}
		if scanner.Scan() {
			return scanner.Text()
		}
		return ""
	}
}

