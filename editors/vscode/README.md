# PLAIN Language — VS Code extension

Syntax highlighting, editor behaviours, snippets and one-key running for
[PLAIN](https://github.com/CFFinch62/plain-language) (`.plain` files).

## Getting PLAIN

This extension highlights and runs `.plain` files — it does not bundle the
interpreter. Get the language itself from GitHub:

**<https://github.com/CFFinch62/plain-language>**

PLAIN is free and open source under the **MIT License**, as is this extension.

```sh
git clone https://github.com/CFFinch62/plain-language.git
cd plain-language
go build -o plain cmd/plain/main.go
```

Put the resulting `plain` binary on your `PATH`, or point
`plain.interpreterPath` (below) at it with an absolute path.

## What it does

| Feature | How |
|---|---|
| Syntax highlighting | TextMate grammar (`syntaxes/plain.tmLanguage.json`) |
| `note:` block comments | Grammar `while` rule scoped by indentation |
| `v"…{expr}…"` interpolation highlighted as code | Grammar |
| Auto-indent after block keywords, dedent on `else`/`handle`/… | `language-configuration.json` |
| Indentation-based folding | `language-configuration.json` (`offSide`) |
| `Ctrl+/` toggles `rem:` comments | `language-configuration.json` |
| Bracket matching, auto-close, auto-surround | `language-configuration.json` |
| 20 snippets (`task`, `loopin`, `choose`, `attempt`, …) | `snippets/plain.json` |
| ▶ Run File button, `Ctrl+F5` | `extension.js` |
| Analyze File (semantic check without running) | `extension.js` (`plain -analyze`) |
| Start REPL | `extension.js` (`plain -repl`) |
| Errors in the Problems panel | `extension.js` + the `$plain-*` matchers |
| `.plain` file icon in the explorer | `contributes.languages[].icon` |

## Installing

Plain JavaScript and JSON — no build step, no runtime dependency.

**Development (live, reloads on change):**

```sh
ln -s "$PWD" ~/.vscode/extensions/plain-language
```

Then run **Developer: Reload Window**.

**Packaged:**

```sh
npx @vscode/vsce package \
    --baseContentUrl  https://github.com/CFFinch62/plain-language/blob/main/editors/vscode/ \
    --baseImagesUrl   https://raw.githubusercontent.com/CFFinch62/plain-language/main/editors/vscode/
# -> plain-language-0.1.0.vsix
code --install-extension plain-language-0.1.0.vsix
```

The two `baseUrl` flags make this README's relative links resolve against the
repository. They are needed because the extension lives in a subfolder of the
repo, while `vsce` resolves relative links against the repository root.

To uninstall: `code --uninstall-extension fragillidae.plain-language`.

## Configuration

| Setting | Default | Meaning |
|---|---|---|
| `plain.interpreterPath` | `plain` | Path to the interpreter. Use an absolute path if it is not on your `PATH`. |
| `plain.saveBeforeRun` | `true` | Save the file before running it. |
| `plain.runInTerminal` | `true` | Run in an integrated terminal. Leave this on for programs using `read_line`, `get_key` or the TUI builtins. Turn it off for Output-channel capture plus Problems-panel squiggles. |
| `plain.projectRoot` | `""` | Passed as `--project-root`, letting a program import modules relative to a project root instead of its own directory. `${workspaceFolder}` is substituted. Empty omits the flag. |

**Analyze File** always uses the Output channel regardless of
`plain.runInTerminal`, since populating the Problems panel is the whole point of
the command.

## Diagnostics

Three things about PLAIN's error reporting shape this code, and all three differ
from the sibling Quick extension:

**Diagnostics go to stdout, not stderr.** `cmd/plain/main.go` prints them with
`fmt.Printf`, so stdout is what gets scanned.

**There are two different `ERROR:` shapes.** Parser errors put the position last,
semantic errors put it first:

```
Parser errors for: /path/to/file.plain
=====================================
ERROR: Expected next token to be RPAREN, got NEWLINE instead (line 1, column 10)

Semantic errors for: /path/to/file.plain
=====================================
ERROR: line 3, column 4: variable 'x' already declared at line 2
```

**The file appears only on the header line**, so parsing is stateful: the header
sets the current file and the `ERROR:` lines that follow attach to it. This is
also why the contributed problem matchers are multi-line, with a filler pattern
for the `=====` separator between header and first error.

PLAIN reports **1-based lines but 0-based columns** (its lexer resets `column` to
0 at each newline), so only the line number is adjusted when building a VS Code
position.

Runtime failures print `Runtime error: <msg>` with no position at all. They
appear in the Output channel but are deliberately not pinned to a guessed line.

## A note on `Main()`

The interpreter calls `Main()` itself when a program defines it. Writing an
explicit `Main()` call at the bottom of the file runs the whole program twice,
so the `main` snippet deliberately does not emit one.

## Keeping the grammar honest

The grammar's keyword list mirrors the `keywords` map in
[`internal/token/token.go`](../../internal/token/token.go) and its 151 builtin
names mirror the map literals in
[`internal/runtime/builtins*.go`](../../internal/runtime/). **These are copies —
adding a keyword or builtin to the interpreter does not update them.**

Details worth knowing before editing:

- **PLAIN keywords are case-sensitive.** `LookupIdent` is an exact Go map lookup,
  so unlike Quick nothing here needs case-insensitive matching — in either the
  grammar or the indentation rules.
- **Some keywords carry a colon**: `rem:`, `note:`, `use:`, `assemblies:`,
  `modules:`, `tasks:`. The lexer reads the identifier and then checks for a
  following `:`, so the grammar matches them with the colon included.
- **`note:` comments are scoped by indentation**, not closed by a delimiter —
  everything indented further than the `note:` line is comment. The grammar
  expresses this with a `begin`/`while` rule whose `while` pattern backreferences
  the captured indent. It cannot be expressed as a `blockComment` pair in
  `language-configuration.json`, which is why none is declared there.
- **Blocks open on a leading keyword with no trailing marker.** There is no `:`
  ending the line the way Quick and Python have, so the indentation rules key off
  the first word of the line.
- Unknown string escapes are preserved rather than rejected, so nothing is scoped
  `invalid.illegal` for them.

To inspect what the grammar produced, run **Developer: Inspect Editor Tokens and
Scopes** with the cursor in a `.plain` file.

## License and source

MIT. Both the extension and the PLAIN language are maintained at
<https://github.com/CFFinch62/plain-language>; issues and pull requests are
welcome there. More Fragillidae Software languages and tools:
<https://github.com/CFFinch62>.
