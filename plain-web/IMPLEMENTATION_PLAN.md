# PLAIN Web Playground — Implementation Plan

## 1. Overview

A zero-server, WebAssembly-based online playground for the PLAIN programming language.
The PLAIN interpreter (Go) is compiled to WASM and runs entirely in the browser.
No backend, no execution costs — hosted as a fully static site (e.g. GitHub Pages).

---

## 2. Goals

- Let users write and run PLAIN code in the browser with no install required
- Provide syntax-highlighted editing via Monaco Editor
- Support pre-supplied user input (for programs that call `get()`)
- Display clear instructions about playground limitations
- Link users to the GitHub repo / desktop app for the full language

## 3. Non-Goals (Explicitly Excluded)

| Feature | Reason Excluded |
|---|---|
| Serial port builtins (`serial_*`) | Hardware I/O — not possible in browser |
| Network builtins (`net_connect`, `net_listen`, etc.) | Browser security model |
| File I/O builtins (`read_file`, `write_file`, etc.) | No filesystem in browser |
| `use:` / module imports | Requires multi-file support — desktop only |
| TUI positioning (`text_at`, `draw_box`, etc.) | ANSI codes don't render in textarea |
| Interactive `get()` mid-run | Blocking stdin not possible in WASM |

All excluded features return a friendly error with a link to the desktop app.

---

## 4. Architecture

```
Browser (Static Site)
┌─────────────────────────────────────────────────────┐
│  Monaco Editor  │  Input Box  │  Output Panel        │
│  (PLAIN syntax  │  (pre-type  │  (captured stdout)   │
│   highlighting) │   answers)  │                      │
│                 │             │                      │
│         app.js — calls runPlain(code, inputs)        │
│                      │                               │
│              plain.wasm  ◄── Go WASM binary          │
│              wasm_exec.js (Go runtime shim)          │
└─────────────────────────────────────────────────────┘

PLAIN repo changes (Go side)
├── internal/runtime/
│   ├── io_hooks.go              NEW — PrintFunc / InputFunc package vars
│   ├── io_native.go             NEW — native stdin (build: !js)
│   ├── io_wasm.go               NEW — JS output buffer + input queue (build: js,wasm)
│   ├── builtins.go              MODIFIED — use PrintFunc/InputFunc, remove serial/net
│   ├── builtins_serial.go       NEW — serial builtins (build: !js)
│   ├── builtins_net.go          NEW — network builtins (build: !js)
│   └── builtins_wasm.go         NEW — stub getSerialBuiltins/getNetBuiltins (build: js,wasm)
│   └── evaluator.go             MODIFIED — PlaygroundMode flag, disable use: imports
├── cmd/plain-wasm/
│   └── main.go                  NEW — WASM entry point, exports runPlain() to JS
└── plain-web/                   NEW — static web app (this folder)
    ├── IMPLEMENTATION_PLAN.md   This file
    ├── index.html
    ├── style.css
    ├── app.js
    ├── plain-lang.js            Monaco syntax grammar for PLAIN
    ├── build.sh                 Compiles plain.wasm
    └── wasm_exec.js             Copied from Go installation
```

---

## 5. Playground Limitations UI

A collapsible "ℹ About this Playground" panel explains:

> This playground covers the core PLAIN language: variables, types, tasks,
> loops, conditionals, and string operations. The following are desktop-only:
> file I/O, serial/network, multi-file imports, and TUI drawing.
> **[Download the desktop app →]** (links to GitHub)

For `get()` input: a labelled input box appears with the note:
> "Type your answers here (one per line) before pressing Run."

---

## 6. Implementation Phases

### Phase 1 — Go Runtime Refactoring ✅ COMPLETE
*Modify the existing interpreter to support injectable I/O and platform build tags.*

- [x] **1.1** Create `internal/runtime/io_hooks.go`
  - Package-level `PrintFunc func(string)` (default: `fmt.Print`)
  - Package-level `InputFunc func(string) string` (default: nil, set by platform)
  - Package-level `PlaygroundMode bool` (default: false)

- [x] **1.2** Create `internal/runtime/io_native.go` *(build tag: `!js`)*
  - `init()` sets `InputFunc` to use `bufio.NewScanner(os.Stdin)`

- [x] **1.3** Create `internal/runtime/io_wasm.go` *(build tag: `js && wasm`)*
  - `init()` sets `PrintFunc` to write to a `strings.Builder` output buffer
  - `SetInputLines(lines []string)` — loads pre-supplied input queue
  - `GetOutput() string` — returns and resets the output buffer
  - `InputFunc` reads from input queue, echoes prompt+answer to output

- [x] **1.4** Modify `internal/runtime/builtins.go`
  - Removed imports: `net`, `go.bug.st/serial` (kept `bufio` for `read_line`)
  - Removed global `var inputScanner`
  - `display` builtin: replaced `fmt.Print` calls with `PrintFunc`
  - `get` builtin: replaced scanner logic with `InputFunc(prompt)`
  - `clear` builtin: replaced `fmt.Print(ansi)` with `PrintFunc(ansi)`
  - TUI builtins (`text_at`, `text_color`, `draw_line`, `draw_box`): replaced
    all `fmt.Printf/Print` with `PrintFunc(fmt.Sprintf(...))`
  - File I/O builtins (19 functions): added `PlaygroundMode` guard at top of each
  - Removed serial+net sections → moved to split files
  - `GetBuiltins()`: merges in `getSerialBuiltins()` and `getNetBuiltins()`

- [x] **1.5** Create `internal/runtime/builtins_serial.go` *(build tag: `!js`)*
  - Serial builtins in `func getSerialBuiltins() map[string]*BuiltinValue { ... }`
  - Retains `go.bug.st/serial` import (native only)

- [x] **1.6** Create `internal/runtime/builtins_net.go` *(build tag: `!js`)*
  - Network builtins in `func getNetBuiltins() map[string]*BuiltinValue { ... }`
  - Retains `net` import (native only)

- [x] **1.7** Create `internal/runtime/builtins_wasm.go` *(build tag: `js && wasm`)*
  - Stub `func getSerialBuiltins() map[string]*BuiltinValue { return nil }`
  - Stub `func getNetBuiltins() map[string]*BuiltinValue { return nil }`

- [x] **1.8** Modify `internal/runtime/evaluator.go`
  - `evalUseStatement`: if `PlaygroundMode`, returns descriptive error
  - Note: `PlaygroundMode` is a package-level var (not Evaluator field) — simpler

- [x] **1.9** Verify existing tests still pass
  - `go build ./...` ✅  `go test ./...` ✅ — all 7 packages pass

---

### Phase 2 — WASM Entry Point ✅ COMPLETE
*Build the Go→WASM bridge.*

- [x] **2.1** Create `cmd/plain-wasm/main.go`
  - Build tags: `//go:build js && wasm`
  - Exports `runPlain(code, inputs)` to `js.Global()` via `js.FuncOf`
  - Calls `runtime.SetInputLines(...)` and sets `runtime.PlaygroundMode = true`
  - Lexes → parses → analyzes → evaluates the code
  - Returns JS object: `{ output: string, error: string }`
  - Keeps program alive with `select {}`

- [x] **2.2** Create `plain-web/build.sh`
  - `GOOS=js GOARCH=wasm go build -o plain-web/plain.wasm ./cmd/plain-wasm/`
  - Copies `wasm_exec.js` — handles both old (`misc/wasm/`) and new (`lib/wasm/`) locations
  - Optionally runs `wasm-opt` (Binaryen) for size reduction if installed
  - Output: `plain.wasm` ≈ 4 MB

- [x] **2.3** First WASM smoke test
  - Created minimal `plain-web/index.html` with inline textarea editor
  - Served with `python3 -m http.server 8080` — all assets served 200 OK
  - WASM loads and `runPlain()` is callable from JS
  - Native `go build ./...` and `go test ./...` still all pass

---

### Phase 3 — Web Playground UI
*Build the static web application.*

- [x] **3.1** Create `plain-web/index.html`
  - Monaco Editor (loaded from CDN) for code input
  - Pre-supplied input textarea with instructions
  - Output panel (monospace, read-only)
  - Run button + Clear button
  - "About this Playground" collapsible info panel
  - Link to GitHub / desktop download

- [x] **3.2** Create `plain-web/style.css`
  - Clean two-panel layout (editor left, I/O right)
  - Dark theme (Catppuccin-inspired) matching PLAIN's desktop IDE aesthetic
  - Responsive design (usable on tablet)

- [x] **3.3** Create `plain-web/plain-lang.js`
  - Monaco language definition for `plain`
  - Keywords: `task`, `var`, `fxd`, `if`, `else`, `loop`, `choose`, `choice`,
    `default`, `deliver`, `rem`, `use`, `get`, `display`, `swap`, `from`, `to`,
    `step`, `loop`, `choose`, `choice`
  - Type prefixes: `str`, `int`, `flt`, `bln`, `lst`, `tbl`
  - String literals: `"..."` and `v"..."` (interpolated)
  - Comments: lines starting with `rem:` or `note:`
  - Operators and brackets
  - Custom `plain-dark` theme with Catppuccin colours

- [x] **3.4** Create `plain-web/app.js`
  - Loads and instantiates `plain.wasm`
  - Wires Run button → `runPlain(editorContent, inputContent)`
  - Displays output in output panel
  - Displays errors in styled error panel (red text)
  - Strips ANSI escape codes from output before display
  - Loads example programs into editor from dropdown
  - Ctrl/Cmd+Enter keyboard shortcut to run

- [x] **3.5** Populate example programs (embedded in `app.js`)
  - Hello World
  - Fibonacci sequence
  - Simple calculator (uses `get()` — demonstrates input)
  - FizzBuzz
  - Grade calculator

---

### Phase 4 — Polish & Deployment
*Final checks and publishing.*

- [ ] **4.1** Cross-browser testing (Chrome, Firefox, Safari)
- [ ] **4.2** Mobile / tablet layout check
- [ ] **4.3** Write `plain-web/README.md` — build & deploy instructions
- [ ] **4.4** Configure GitHub Pages (or Netlify) deployment
- [ ] **4.5** Final review of all user-facing error messages for excluded features

---

## 7. Progress Log

| Date | Phase | Notes |
|------|-------|-------|
| 2026-03-05 | Phase 1 | **COMPLETE.** Created io_hooks.go, io_native.go, io_wasm.go. Extracted serial/net builtins into build-tagged files. Updated display/get/clear/TUI builtins to use PrintFunc/InputFunc. Added PlaygroundMode guards to all 19 file I/O builtins. Disabled use: imports under PlaygroundMode in evaluator.go. Native `go build ./...` and `go test ./...` all pass. |
| 2026-03-05 | Phase 2 | **COMPLETE.** Created cmd/plain-wasm/main.go (WASM entry point exporting runPlain to JS). Created plain-web/build.sh (handles Go 1.21+ wasm_exec.js location). Built plain.wasm (≈4 MB). Created smoke-test index.html. Verified all assets served 200 OK via python3 -m http.server 8080. runPlain() callable from browser JS. Native build and tests still all pass. |
| 2026-03-05 | Phase 3 | **COMPLETE.** Created style.css (Catppuccin dark theme, two-panel grid layout). Created plain-lang.js (Monarch tokeniser + plain-dark Monaco theme). Created app.js (WASM loading, Run wiring, ANSI stripping, Ctrl+Enter shortcut, 5 example programs). Replaced smoke-test index.html with full Monaco-based UI including collapsible info panel. Verified all files served and Monaco editor loads in browser. |

