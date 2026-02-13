# PLAIN Language and IDE To Do List

## Current Language Issues

- need to be able to display floats with a specified amount of decimal places

## Current IDE Issues

- Need to add 'delete file/folder' to file browser context menu
- If terminal position is 'right side' and debug panel is selected to be shown it should show and move terminal to center bottom. this does not work. Debug panel will only show if terminal is at bottom before it is shown.
- When starting the debugger the IDE crashes

## Future Language Enhancements (Standard Library)

###Text Graphics Library (text_graphics)
Goal: Terminal-based UI (TUI) capabilities. Implementation:

Go Wrapper: Use a library like termbox-go or tcell in internal/runtime.
Built-ins:
text.clear()
text.set_cursor(x, y)
text.set_color(fg, bg)
text.print(x, y, str)
text.poll_event() (keyboard/mouse)
###Minimal GUI Library (gui)

Goal: Simple windowing and widgets (like Python's Tkinter). Implementation:

Go Wrapper: Use fyne or andlabs/ui (though Fyne is non-native look). Alternatively, valid web-view based UI (lorca).
Built-ins:
window = gui.create_window(title, width, height)
button = gui.create_button(text, callback)
gui.run()

###Turtle Graphics (turtle)
Goal: Educational drawing graphics. Implementation:

Strategy: Could be built on top of the Minimal GUI library or ebiten (2D game lib).
Built-ins:
turtle.forward(dict)
turtle.right(angle)
turtle.penup(), turtle.pendown()

###Networking Library (net)
Goal: Basic TCP/UDP/HTTP support. Implementation:

HTTP Client:
net.http.get(url) -> returns content
net.http.post(url, data)
Socket (Low-level):
socket = net.connect(host, port)
socket.send(data)
socket.receive(count)
server = net.listen(port)