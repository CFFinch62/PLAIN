# PLAIN Language and IDE To Do List

## Current Language Issues

### All platforms

### Linux

### Mac

### Windows


## Current IDE Issues

### All platforms

### Linux

### Mac

### Windows

- When changing font or font size in the settings dialog, the font or font size is not applied to the editor until after the ide is closed and relaunched. it should be applied immediately when 'apply' or 'ok'buttons are clicked or .


## UI/UX Enhancement Roadmap

PLAIN has evolved from a teaching language into a powerful tool for data acquisition and processing. To improve the user experience of programs written in PLAIN, we're implementing a three-phase TUI (Text User Interface) enhancement plan.

### ✅ Phase 1: Enhanced Text Output (COMPLETED)

**Status:** Implemented and tested

**Goal:** Add basic positioned text and drawing functions to create better console UIs.

**Implemented Functions:**
- `text_at(x, y, text)` - Position cursor and print text at specific coordinates
- `text_color(foreground [, background])` - Set text colors using ANSI codes
- `draw_line(x, y, length, direction [, char])` - Draw horizontal/vertical lines
- `draw_box(x, y, width, height [, title])` - Draw bordered boxes with optional titles

**Examples Created:**
- `examples/basic/text_graphics_demo.plain` - Comprehensive demo of all Phase 1 features
- `examples/basic/dashboard_demo.plain` - Simulated real-time data dashboard
- `examples/basic/menu_demo.plain` - Interactive menu system
- `examples/tests/text_graphics_test.plain` - Automated test suite

**Documentation:**
- Added to `docs/user/STDLIB.md` with full API documentation
- Updated quick reference table
- Examples demonstrate use cases for data acquisition and monitoring

**Use Cases Enabled:**
- Real-time sensor data displays
- Interactive configuration menus
- Status dashboards for serial/network monitoring
- Progress indicators and data visualization
- Formatted output for data logging applications

---

### 🔄 Phase 2: Full TUI Library (IN PLANNING)

**Goal:** Implement full TUI capabilities using tcell library with event handling.

**Planned Implementation:**

**Go Wrapper:** Use `tcell` library (https://github.com/gdamore/tcell) in `internal/runtime`

**Planned Built-in Functions:**
```plain
rem: Screen management
screen = tui_init()              rem: Initialize TUI mode
tui_close(screen)                rem: Close TUI and restore terminal
tui_clear(screen)                rem: Clear screen
tui_refresh(screen)              rem: Update display
tui_size(screen)                 rem: Get terminal dimensions -> [width, height]

rem: Drawing (buffered)
tui_print(screen, x, y, text)    rem: Print at position (buffered)
tui_set_color(screen, fg, bg)    rem: Set current colors
tui_fill(screen, x, y, w, h, char) rem: Fill rectangle

rem: Event handling
event = tui_poll_event(screen)   rem: Get next event (blocking)
event = tui_poll_event(screen, timeout) rem: With timeout in ms
rem: Event table contains: {type: "key"|"mouse"|"resize", key: "a"|"Enter"|"Esc", x: 10, y: 5, ...}

rem: Keyboard
tui_has_event(screen)            rem: Check if event is available (non-blocking)

rem: Mouse support
tui_enable_mouse(screen)         rem: Enable mouse events
tui_disable_mouse(screen)        rem: Disable mouse events
```

**Example Use Case:**
```plain
task Main()
    var screen = tui_init()
    var running = true

    loop while running
        tui_clear(screen)
        tui_print(screen, 1, 1, "Press 'q' to quit")
        tui_print(screen, 1, 3, "Temperature: " & read_sensor())
        tui_refresh(screen)

        if tui_has_event(screen)
            var event = tui_poll_event(screen, 100)
            if event.type == "key" and event.key == "q"
                running = false

    tui_close(screen)
```

**Benefits:**
- Proper event-driven programming
- Mouse support for interactive UIs
- Flicker-free updates with buffering
- Terminal resize handling
- Full control over screen layout

**Technical Notes:**
- Will require CGO for tcell library
- Need to handle terminal state restoration on errors
- Should work in IDE terminal and external terminals
- Consider fallback mode for non-TUI terminals

---

### 📊 Phase 3: Data Visualization (PLANNED)

**Goal:** Add charting and table visualization functions built on Phase 2 TUI.

**Planned Built-in Functions:**
```plain
rem: Charts
plot_line_chart(screen, data, x, y, width, height, title)
plot_bar_chart(screen, data, x, y, width, height, title)
plot_histogram(screen, data, x, y, width, height, bins)
plot_sparkline(screen, data, x, y, width)

rem: Tables
draw_table(screen, headers, rows, x, y, col_widths)
draw_scrollable_table(screen, headers, rows, x, y, width, height, scroll_pos)

rem: Gauges and indicators
draw_gauge(screen, value, min, max, x, y, width, label)
draw_progress_bar(screen, value, max, x, y, width, label)
draw_meter(screen, value, min, max, x, y, width, height)

rem: Real-time graphs
create_graph(screen, x, y, width, height, max_points)
graph_add_point(graph, value)
graph_draw(graph)
```

**Example Use Case:**
```plain
task Main()
    var screen = tui_init()
    var port = serial_open("/dev/ttyUSB0", 9600, "8N1")
    var temps = []

    loop i from 1 to 100
        var line = serial_read_line(port)
        var temp = parse_temperature(line)
        append(temps, temp)

        tui_clear(screen)
        draw_box(screen, 1, 1, 78, 20, "Temperature Monitor")
        plot_line_chart(screen, temps, 2, 3, 76, 15, "Last 100 Readings")
        tui_refresh(screen)

        sleep(100)

    serial_close(port)
    tui_close(screen)
```

**Benefits:**
- Visual representation of sensor data
- Real-time monitoring dashboards
- Data analysis and exploration
- Professional-looking output for reports
- Educational tool for teaching data visualization

---

## Alternative/Future Considerations

### Minimal GUI Library (DEFERRED)

**Rationale for deferring:**
- Breaks the "plain" simplicity philosophy
- Heavy dependencies (50+ MB for Fyne)
- Harder to teach and learn
- TUI provides 80% of the value with 20% of the complexity

**If implemented later, consider:**
- Web-based approach (serve HTML, open browser)
- Very minimal wrapper around native widgets
- Optional module, not core library

### Turtle Graphics (OPTIONAL MODULE)

**Status:** Could be implemented as separate optional module

**Use case:** Educational graphics programming

**Implementation:** Could build on top of Phase 2 TUI or use separate graphics library

---

## Implementation Priority

1. ✅ **Phase 1** - COMPLETE
2. **Phase 2** - Next priority (enables event-driven programs)
3. **Phase 3** - After Phase 2 (builds on TUI foundation)
4. **GUI/Turtle** - Future consideration based on user demand

