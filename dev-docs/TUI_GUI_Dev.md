PLAIN Language: TUI/GUI Assessment
Current State
The language already has a foundation for TUI work:

text_at(x, y, text), text_color(), draw_line(), draw_box() — raw ANSI escape codes
An event loop with timer callbacks (events.go)
A clean I/O hook abstraction (io_hooks.go) with injectable PrintFunc/InputFunc
Platform separation via build tags (native vs. WASM)
The main gaps are: input is blocking and line-only (get() waits for Enter), there's no non-blocking key/mouse event handling, and the ANSI approach is fragile (terminal size unknown, no screen buffering).

Options, Ranked by Effort vs. Payoff
Tier 1 — Extend existing ANSI TUI (Low effort, immediate value)
No new dependencies. Just add more built-ins:

New built-in	Purpose
screen_size()	Returns [cols, rows] via ANSI query or os.Stdin terminal size
cursor_show() / cursor_hide()	\033[?25h / \033[?25l
get_key()	Read a single raw keypress (including arrow keys as strings like "UP")
mouse_enable() / mouse_read()	ANSI mouse tracking codes
set_raw_mode() / set_cooked_mode()	Switch terminal between raw/normal mode
This is entirely within the ANSI approach you already use. get_key() in raw mode is the single biggest unlock — it lets PLAIN programs react to arrow keys, Escape, Enter, etc. without waiting for a newline. This alone enables menu navigation, games, and interactive UI loops.

What was added
New file internal/runtime/builtins_tui.go — native-only (!js build tag), 22 new built-ins across 6 categories. WASM stub added to internal/runtime/builtins_wasm.go. Merged via internal/runtime/builtins.go using the same pattern as serial/net.

Screen control
Function	Purpose
screen_size()	Returns [cols, rows] — uses golang.org/x/term
screen_alt()	Switch to alternate screen buffer (saves current screen)
screen_main()	Restore main screen buffer
Cursor control
| cursor_show() / cursor_hide() | Show/hide the cursor (prevents flicker during drawing) |
| cursor_pos(x, y) | Move cursor without printing |

Raw mode + input (the big unlock)
| set_raw_mode() | Immediate keypresses, no echo, special keys readable |
| set_cooked_mode() | Restore normal terminal mode |
| get_key() | Blocking — returns "UP", "ENTER", "CTRL_C", "a", etc. |
| get_event() | Blocking — returns a table {type, key} or {type, action, button, x, y} |

Mouse
| mouse_enable() / mouse_disable() | Toggle SGR mouse event reporting |

Text attributes (all ANSI, no extra dep)
text_reset(), text_bold(), text_dim(), text_italic(), text_underline(), text_blink(), text_reverse(), text_strike()

Extended color
| text_color_256(fg [, bg]) | 256-color palette (0–255) |
| text_color_rgb(r, g, b [, br, bg, bb]) | 24-bit true color |

Note: The test suite failure at evaluator.go:869 is pre-existing and unrelated to these changes — the binary builds and runs fine.

Tier 2 — tcell integration (Medium effort, full TUI capability)
tcell is the premier Go terminal library — well-maintained, cross-platform, supports mouse, Unicode, proper screen buffering, and all special keys. It's what tview and many major TUI apps are built on.

The approach: add a tui_init() / tui_quit() built-in pair that takes over the screen via tcell. Between those calls, expose:


tui_init()              -- enter alternate screen, raw mode
tui_size()              -- [cols, rows]
tui_clear()             -- clear screen buffer
tui_draw(x, y, text)    -- draw text at position
tui_set_color(fg, bg)   -- named colors (not just ANSI 8)
tui_flush()             -- push buffer to screen
tui_event()             -- returns next event {type, key, mouse_x, mouse_y}
tui_quit()              -- restore terminal
The event model fits naturally into PLAIN's existing event loop. A program structure would be:


tui_init()
loop while true:
    var e = tui_event()
    if e.type == "key" and e.key == "q":
        exit
    -- draw frame
    tui_flush()
tui_quit()
Effort: ~1 week. Risk: Medium — tcell replaces the ANSI approach entirely, so existing text_at() calls would need to be bridged or deprecated. However the I/O hook architecture makes this clean.

Tier 3 — tview widgets on top of tcell (Medium-high effort, rich TUI)
tview is built on tcell and provides proper widget primitives: text views, input fields, lists, drop-downs, modal dialogs, flex layouts, tables. These could be exposed as PLAIN objects:


var list = tui_list(["Option A", "Option B", "Option C"])
var input = tui_input("Enter name: ")
var layout = tui_flex([list, input], "horizontal")
tui_run(layout)
This is much more expressive but requires exposing widget objects as a new PLAIN value type. The RecordValue / TableValue types in value.go could carry widget handles, similar to how FileHandleValue and SerialPortValue work today.

Effort: 2-3 weeks. Risk: Medium — architecture is sound, but it's a lot of surface area.

Tier 4 — Fyne GUI (High effort, true windowed GUI)
Fyne is a pure-Go cross-platform GUI toolkit — no cgo, no system dependencies beyond a graphics driver. It's the most practical true-GUI option for Go without pulling in cgo or Electron-style infrastructure.


var win = gui_window("My App", 800, 600)
var btn = gui_button("Click me", task() display("clicked") end)
var label = gui_label("Hello!")
gui_show(win, [label, btn])
gui_run()
Effort: 3-4 weeks minimum. Risk: Higher — Fyne has opinions about layout and app lifecycle that would need to map cleanly onto PLAIN's execution model. Also breaks WASM compatibility (Fyne doesn't target WASM).

Tier 5 — webview / HTML UI backend (High effort, web-tech UI)
Using webview (or Wails), PLAIN could drive an HTML/CSS/JS window with Go as the backend. The PLAIN program calls web_window("ui.html") and exposes callback tasks that JavaScript can invoke. Powerful, but requires cgo and complicates cross-platform builds.

Effort: 3-5 weeks. Risk: High — cgo dependency, more complex build, harder to keep WASM version compatible.

My Recommendation
Start with Tier 1 immediately — get_key() in raw mode is a 1-day change that unlocks interactive programs and gives users something concrete.

Then target tcell (Tier 2) as the primary TUI path. It's the right foundation — tcell is battle-tested, the screen-buffer model is much more reliable than raw ANSI, and the mouse+keyboard event system fits naturally into your existing event loop design in events.go.

Hold off on Tier 4/5 until the TUI path is solid. Most use cases that seem to "need" a GUI can actually be served well by a proper TUI, and keeping WASM compatibility is a real asset worth preserving.

One concrete note: whatever you add, the PlaygroundMode guard pattern you use for file/network I/O should apply to TUI features too, since ANSI codes and raw mode don't make sense in the web textarea output.