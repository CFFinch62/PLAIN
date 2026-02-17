# PLAIN Standard Library Reference

> **Every built-in function in the PLAIN language** 📚

This document is an API reference for all built-in functions available in PLAIN. Functions are organized by category. Each entry includes the signature, description, example usage, and any important notes.

For language syntax and semantics, see the [Language Reference](LANGUAGE-REFERENCE.md). For hands-on examples, see the [Tutorial](TUTORIAL.md).

---

## Table of Contents

1. [Console I/O](#1-console-io)
2. [Type Checking](#2-type-checking)
3. [Type Conversion](#3-type-conversion)
4. [String Operations](#4-string-operations)
5. [Math — Basic](#5-math--basic)
6. [Math — Trigonometric](#6-math--trigonometric)
7. [Math — Logarithmic](#7-math--logarithmic)
8. [Math — Random](#8-math--random)
9. [List Operations](#9-list-operations)
10. [Table Operations](#10-table-operations)
11. [File I/O — Simple](#11-file-io--simple)
12. [File I/O — Handle-Based](#12-file-io--handle-based)
13. [File System](#13-file-system)
14. [Path Operations](#14-path-operations)
15. [Timing and Events](#15-timing-and-events)
16. [Serial Port I/O](#16-serial-port-io)
17. [Network I/O](#17-network-io)

---

## 1. Console I/O

### `display(value1, value2, ...)`

Prints one or more values to the console, separated by spaces, followed by a newline.

```plain
display("Hello, world!")           rem: Hello, world!
display("Score:", 95)              rem: Score: 95
display("x =", 10, "y =", 20)     rem: x = 10 y = 20
```

**Arguments:** One or more values of any type. Non-string values are automatically converted to their string representation.

**Returns:** null

---
		
		### `set_float_precision(n)`
		
		Sets the number of decimal places used when displaying floating-point numbers.
		
		```plain
		display(1.0/3.0)            rem: 0.3333333333333333 (default)
		set_float_precision(2)
		display(1.0/3.0)            rem: 0.33
		set_float_precision(4)
		display(1.0/3.0)            rem: 0.3333
		set_float_precision(-1)     rem: Reset to default
		```
		
		**Arguments:**
		- `n` (integer) — Number of decimal places. Use `-1` for default formatting (standard Go `%g` behavior, which removes trailing zeros).
		
		**Returns:** null
		
		---


### `get(prompt)`

Displays a prompt and reads one line of text input from the user.

```plain
var name = get("What is your name? ")
display("Hello, " & name)
```

**Arguments:**
- `prompt` (string, optional) — Text to display before waiting for input

**Returns:** string — The line of text entered by the user

**Note:** The prompt is displayed without a trailing newline, so the cursor appears immediately after the prompt text.

---

### `clear()`

Clears the console screen and moves the cursor to the top-left corner.

```plain
display("Now you see me...")
sleep(1000)
clear()
display("Now you don't!")
```

**Arguments:** None.

**Returns:** null

**Compatibility:** Works in the PLAIN IDE internal terminal and most external terminals (Linux, macOS, Windows 10+).

---

### `text_at(x, y, text)`

Positions the cursor at the specified column and row, then prints the text.

```plain
clear()
text_at(10, 5, "Hello at position 10, 5")
text_at(10, 6, "This is one line below")
text_at(20, 8, "Indented more to the right")
```

**Arguments:**
- `x` (integer) — Column position (1-based, left edge is 1)
- `y` (integer) — Row position (1-based, top edge is 1)
- `text` (any) — Text to display (automatically converted to string)

**Returns:** null

**Note:** Coordinates are 1-based. Position (1, 1) is the top-left corner of the terminal.

---

### `text_color(foreground [, background])`

Sets the text color for subsequent output using ANSI color codes.

```plain
text_color("red")
display("This is red text")

text_color("green", "black")
display("Green text on black background")

text_color("default")
display("Back to normal")
```

**Arguments:**
- `foreground` (string) — Foreground color name
- `background` (string, optional) — Background color name

**Valid colors:** `"black"`, `"red"`, `"green"`, `"yellow"`, `"blue"`, `"magenta"`, `"cyan"`, `"white"`, `"default"`

**Returns:** null

**Note:** Use `"default"` to reset colors to terminal defaults.

---

### `draw_line(x, y, length, direction [, char])`

Draws a horizontal or vertical line at the specified position.

```plain
rem: Horizontal line
draw_line(5, 10, 40, "h")

rem: Vertical line
draw_line(5, 10, 10, "v")

rem: Custom character
draw_line(5, 15, 30, "h", "=")
draw_line(50, 10, 8, "v", "*")
```

**Arguments:**
- `x` (integer) — Starting column position
- `y` (integer) — Starting row position
- `length` (integer) — Length of the line
- `direction` (string) — Direction: `"h"`, `"horizontal"`, `"v"`, or `"vertical"`
- `char` (string, optional) — Character to use (default: `"-"` for horizontal, `"|"` for vertical)

**Returns:** null

---

### `draw_box(x, y, width, height [, title])`

Draws a bordered box using Unicode box-drawing characters.

```plain
rem: Simple box
draw_box(5, 5, 40, 10)

rem: Box with title
draw_box(5, 5, 40, 10, "Status Panel")

rem: Create a dashboard
text_color("cyan")
draw_box(1, 1, 60, 8, "Sensor Data")
text_color("default")
text_at(3, 3, "Temperature: 72.5°F")
text_at(3, 4, "Humidity: 45%")
```

**Arguments:**
- `x` (integer) — Left edge column position
- `y` (integer) — Top edge row position
- `width` (integer) — Width of the box (including borders)
- `height` (integer) — Height of the box (including borders)
- `title` (string, optional) — Title to display centered in the top border

**Returns:** null

**Note:** Uses Unicode box-drawing characters (┌─┐│└┘). Ensure your terminal supports UTF-8.

---

## 2. Type Checking

All type-checking functions take exactly one argument and return a boolean.

### `is_int(value)`

Returns `true` if the value is an integer.

```plain
display(is_int(42))        rem: true
display(is_int(3.14))      rem: false
display(is_int("42"))      rem: false
```

---

### `is_float(value)`

Returns `true` if the value is a float.

```plain
display(is_float(3.14))    rem: true
display(is_float(42))      rem: false
```

---

### `is_string(value)`

Returns `true` if the value is a string.

```plain
display(is_string("hi"))   rem: true
display(is_string(42))     rem: false
```

---

### `is_bool(value)`

Returns `true` if the value is a boolean.

```plain
display(is_bool(true))     rem: true
display(is_bool(1))        rem: false
```

---

### `is_list(value)`

Returns `true` if the value is a list.

```plain
display(is_list([1, 2]))   rem: true
display(is_list("abc"))    rem: false
```

---

### `is_table(value)`

Returns `true` if the value is a table.

```plain
display(is_table({"a": 1}))   rem: true
display(is_table([1, 2]))     rem: false
```

---

### `is_null(value)`

Returns `true` if the value is null.

```plain
display(is_null(null))     rem: true
display(is_null(0))        rem: false
display(is_null(""))       rem: false
```

---

### `type_of(value)`

Returns a string describing the type of the value.

```plain
display(type_of(42))        rem: integer
display(type_of(3.14))      rem: float
display(type_of("hello"))   rem: string
display(type_of(true))      rem: boolean
display(type_of([1, 2]))    rem: list
display(type_of({"a": 1}))  rem: table
display(type_of(null))      rem: null
```

**Returns:** string — One of: `"integer"`, `"float"`, `"string"`, `"boolean"`, `"list"`, `"table"`, `"null"`

---

## 3. Type Conversion

### `to_int(value)`

Converts a value to an integer. Recognizes `0b` (binary) and `0x` (hex) prefixed strings.

```plain
display(to_int(3.7))          rem: 3 (truncates toward zero)
display(to_int("42"))         rem: 42
display(to_int(true))         rem: 1
display(to_int(false))        rem: 0
display(to_int("0b101010"))   rem: 42 (binary prefix)
display(to_int("0xFF"))       rem: 255 (hex prefix)
```

**Accepts:** integer (returns as-is), float (truncates), string (parses decimal, `0b` binary, or `0x` hex), boolean (true=1, false=0)

**Errors:** If the string cannot be parsed as an integer.

---

### `to_float(value)`

Converts a value to a float.

```plain
display(to_float(42))       rem: 42 (as float)
display(to_float("3.14"))   rem: 3.14
```

**Accepts:** integer, float (returns as-is), string (parses)

**Errors:** If the string cannot be parsed as a float.

---

### `to_string(value)`

Converts any value to its string representation. When given a string, auto-detects binary or hex byte sequences and decodes them to text.

```plain
display(to_string(42))                        rem: "42"
display(to_string(true))                      rem: "true"
display(to_string([1, 2]))                    rem: "[1, 2]"
display(to_string("01001000 01101001"))        rem: "Hi" (binary bytes decoded)
display(to_string("48 69"))                    rem: "Hi" (hex bytes decoded)
display(to_string("hello"))                    rem: "hello" (not a byte pattern, unchanged)
```

**Accepts:** Any type.

**Auto-detection rules (string input only):**
- Binary bytes: space-separated groups of exactly 8 digits of `0`/`1`
- Hex bytes: space-separated groups of exactly 2 hex digits
- If neither pattern matches, the string is returned unchanged

---

### `to_bool(value)`

Converts a value to a boolean using truthiness rules.

```plain
display(to_bool(1))          rem: true
display(to_bool(0))          rem: false
display(to_bool("hello"))    rem: true
display(to_bool(""))         rem: false
display(to_bool(null))       rem: false
display(to_bool([1, 2]))     rem: true (non-empty list)
display(to_bool([]))         rem: false (empty list)
```

**Truthiness rules:**
- Integers/Floats: `0` is false, everything else is true
- Strings: `""` is false, non-empty is true
- Null: always false
- Lists: empty is false, non-empty is true
- Tables: empty is false, non-empty is true
- Everything else: true

### `to_bin(value)`

Converts an integer, boolean, or string to its binary representation as a string.

```plain
display(to_bin(42))          rem: "101010"
display(to_bin(0))           rem: "0"
display(to_bin(-42))         rem: "-101010"
display(to_bin(true))        rem: "1"
display(to_bin(false))       rem: "0"
display(to_bin("Hi"))        rem: "01001000 01101001"
```

**Conversion rules:**
- Integers: converted to base-2 digits (negative sign preserved)
- Booleans: `true` → `"1"`, `false` → `"0"`
- Strings: each character becomes its 8-bit binary representation, space-separated
- Floats, lists, tables, and other types produce an error

### `to_hex(value)`

Converts an integer, boolean, or string to its hexadecimal representation as a string (uppercase).

```plain
display(to_hex(255))         rem: "FF"
display(to_hex(0))           rem: "0"
display(to_hex(-42))         rem: "-2A"
display(to_hex(true))        rem: "1"
display(to_hex(false))       rem: "0"
display(to_hex("Hi"))        rem: "48 69"
```

**Conversion rules:**
- Integers: converted to base-16 uppercase digits (negative sign preserved)
- Booleans: `true` → `"1"`, `false` → `"0"`
- Strings: each character becomes its 2-digit uppercase hex representation, space-separated
- Floats, lists, tables, and other types produce an error

---

## 4. String Operations

### `len(value)`

Returns the length of a string, list, or table.

```plain
display(len("Hello"))       rem: 5
display(len([1, 2, 3]))     rem: 3
display(len({"a": 1}))      rem: 1
```

**Accepts:** string (character count), list (element count), table (key count)

**Returns:** integer

---

### `upper(str)`

Returns the string converted to uppercase.

```plain
display(upper("hello"))     rem: HELLO
display(upper("Hello!"))    rem: HELLO!
```

---

### `lower(str)`

Returns the string converted to lowercase.

```plain
display(lower("HELLO"))     rem: hello
display(lower("Hello!"))    rem: hello!
```

---

### `trim(str)`

Returns the string with leading and trailing whitespace removed.

```plain
display(trim("  hello  "))    rem: "hello"
display(trim("  hi\t"))       rem: "hi"
```

---

### `split(str, delimiter)`

Splits a string into a list of substrings at each occurrence of the delimiter.

```plain
var parts = split("a,b,c", ",")
display(parts)                    rem: [a, b, c]

var words = split("hello world", " ")
display(words)                    rem: [hello, world]
```

**Returns:** list of strings

---

### `join(list, separator)`

Joins a list of values into a single string, separated by the given separator.

```plain
var words = ["Hello", "World"]
display(join(words, " "))         rem: Hello World

var nums = [1, 2, 3]
display(join(nums, ", "))         rem: 1, 2, 3
```

**Arguments:**
- `list` — list of any values (each is converted to a string)
- `separator` — string placed between elements

**Returns:** string

---

### `substring(str, start, end)`

Returns a portion of the string from index `start` (inclusive) to index `end` (exclusive).

```plain
display(substring("Hello, World!", 0, 5))    rem: Hello
display(substring("Hello, World!", 7, 12))   rem: World
```

**Arguments:**
- `str` — the source string
- `start` — integer, starting index (0-based, inclusive)
- `end` — integer, ending index (exclusive)

**Note:** Indices are clamped to the string's bounds. If `start > end`, returns an empty string.

---

### `replace(str, old, new)`

Replaces **all** occurrences of `old` with `new` in the string.

```plain
display(replace("hello world", "world", "PLAIN"))    rem: hello PLAIN
display(replace("aaa", "a", "bb"))                   rem: bbbbbb
```

---

### `contains(str, search)`

Returns `true` if the string contains the search substring.

```plain
display(contains("Hello, World!", "World"))    rem: true
display(contains("Hello, World!", "world"))    rem: false (case-sensitive)
```

**Note:** Also works with lists — see [§9 List Operations](#9-list-operations).

---

### `starts_with(str, prefix)`

Returns `true` if the string starts with the given prefix.

```plain
display(starts_with("Hello", "He"))     rem: true
display(starts_with("Hello", "he"))     rem: false
```

---

### `ends_with(str, suffix)`

Returns `true` if the string ends with the given suffix.

```plain
display(ends_with("Hello", "lo"))       rem: true
display(ends_with("Hello", "LO"))       rem: false
```

---

### `chr(code)`

Returns the string containing the character with the given integer code point.

```plain
display(chr(65))            rem: "A"
display(chr(13))            rem: "\r" (carriage return)
```

**Arguments:**
- `code` — integer code point

**Returns:** string

---

### `ord(str)`

Returns the integer code point of the first character in the string.

```plain
display(ord("A"))           rem: 65
display(ord("\r"))          rem: 13
```

**Arguments:**
- `str` — string (non-empty)

**Returns:** integer

**Errors:** If the string is empty.

---

## 5. Math — Basic

### `abs(n)`

Returns the absolute value of a number.

```plain
display(abs(-42))       rem: 42
display(abs(42))        rem: 42
display(abs(-3.14))     rem: 3.14
```

**Accepts:** integer or float. Returns the same type.

---

### `sqrt(n)`

Returns the square root of a number.

```plain
display(sqrt(16))       rem: 4
display(sqrt(2))        rem: 1.4142135623730951
```

**Returns:** float

**Errors:** If the argument is negative.

---

### `sqr(n)`

Returns the square of a number (n * n).

```plain
display(sqr(5))         rem: 25
display(sqr(3.0))       rem: 9
```

**Returns:** Same type as input (integer or float).

---

### `pow(base, exponent)`

Returns `base` raised to the power of `exponent`.

```plain
display(pow(2, 10))     rem: 1024
display(pow(3, 0.5))    rem: 1.7320508075688772
```

**Returns:** float

**Note:** For integer exponentiation you can also use the `**` operator: `2 ** 10`.

---

### `round(n)`

Rounds a number to the nearest integer (half rounds up).

```plain
display(round(3.7))     rem: 4
display(round(3.2))     rem: 3
display(round(2.5))     rem: 3
display(round(-1.5))    rem: -2
```

**Returns:** integer

---

### `floor(n)`

Returns the largest integer less than or equal to the number (rounds down).

```plain
display(floor(3.7))     rem: 3
display(floor(3.0))     rem: 3
display(floor(-1.3))    rem: -2
```

**Returns:** integer

---

### `ceil(n)`

Returns the smallest integer greater than or equal to the number (rounds up).

```plain
display(ceil(3.2))      rem: 4
display(ceil(3.0))      rem: 3
display(ceil(-1.7))     rem: -1
```

**Returns:** integer

---

### `min(a, b)`

Returns the smaller of two numbers.

```plain
display(min(5, 3))      rem: 3
display(min(-1, 1))     rem: -1
```

**Returns:** The original value (preserves integer/float type).

---

### `max(a, b)`

Returns the larger of two numbers.

```plain
display(max(5, 3))      rem: 5
display(max(-1, 1))     rem: 1
```

**Returns:** The original value (preserves integer/float type).

---

### `mod(a, b)`

Returns the remainder of integer division.

```plain
display(mod(10, 3))     rem: 1
display(mod(15, 5))     rem: 0
```

**Arguments:** Both must be integers.

**Note:** You can also use the `%` operator: `10 % 3`.

**Errors:** If `b` is zero.

---

## 6. Math — Trigonometric

All trigonometric functions work in **radians**.

### `sin(angle)`

Returns the sine of the angle.

```plain
display(sin(0))             rem: 0
display(sin(3.14159 / 2))   rem: ~1
```

---

### `cos(angle)`

Returns the cosine of the angle.

```plain
display(cos(0))             rem: 1
display(cos(3.14159))       rem: ~-1
```

---

### `tan(angle)`

Returns the tangent of the angle.

```plain
display(tan(0))             rem: 0
display(tan(3.14159 / 4))   rem: ~1
```

---

### `asin(value)`

Returns the arcsine (inverse sine) in radians.

```plain
display(asin(1))            rem: ~1.5708 (pi/2)
```

**Argument:** Must be between -1 and 1 inclusive.

---

### `acos(value)`

Returns the arccosine (inverse cosine) in radians.

```plain
display(acos(1))            rem: 0
display(acos(0))            rem: ~1.5708 (pi/2)
```

**Argument:** Must be between -1 and 1 inclusive.

---

### `atan(value)`

Returns the arctangent (inverse tangent) in radians.

```plain
display(atan(1))            rem: ~0.7854 (pi/4)
```

---

### `atan2(y, x)`

Returns the arctangent of y/x, using the signs of both arguments to determine the quadrant. Returns a value in radians between -pi and pi.

```plain
display(atan2(1, 1))        rem: ~0.7854 (pi/4)
display(atan2(-1, -1))      rem: ~-2.3562 (-3*pi/4)
```

---

## 7. Math — Logarithmic

### `log(n)`

Returns the natural logarithm (base e) of the number.

```plain
display(log(1))             rem: 0
display(log(2.71828))       rem: ~1
```

**Errors:** If the argument is zero or negative.

---

### `log10(n)`

Returns the base-10 logarithm of the number.

```plain
display(log10(100))         rem: 2
display(log10(1000))        rem: 3
```

**Errors:** If the argument is zero or negative.

---

### `log2(n)`

Returns the base-2 logarithm of the number.

```plain
display(log2(8))            rem: 3
display(log2(1024))         rem: 10
```

**Errors:** If the argument is zero or negative.

---

### `exp(n)`

Returns e raised to the power of the number (the inverse of `log`).

```plain
display(exp(0))             rem: 1
display(exp(1))             rem: ~2.71828
display(exp(2))             rem: ~7.38906
```

---

## 8. Math — Random

### `random()`

Returns a random float between 0.0 (inclusive) and 1.0 (exclusive).

```plain
var r = random()
display(r)                  rem: e.g., 0.7234... (different each time)
```

**Arguments:** None.

---

### `random_int(min, max)`

Returns a random integer between `min` and `max` (both inclusive).

```plain
var die = random_int(1, 6)
display(die)                rem: e.g., 4 (a number from 1 to 6)
```

**Errors:** If `min > max`.

---

### `random_choice(list)`

Returns a random element from the list.

```plain
var colors = ["red", "green", "blue"]
display(random_choice(colors))    rem: e.g., "green"
```

**Errors:** If the list is empty.

---

## 9. List Operations

### `len(list)`

Returns the number of elements in the list. (Same function as string `len` — see [§4](#4-string-operations).)

```plain
display(len([10, 20, 30]))    rem: 3
display(len([]))               rem: 0
```

---

### `append(list, item)`

Adds an item to the **end** of the list. Modifies the list in place.

```plain
var fruits = ["apple", "banana"]
append(fruits, "cherry")
display(fruits)               rem: [apple, banana, cherry]
```

**Returns:** null (modifies the list in place)

---

### `insert(list, index, item)`

Inserts an item at the specified index. Existing elements shift right. Modifies the list in place.

```plain
var nums = [1, 3, 4]
insert(nums, 1, 2)
display(nums)                 rem: [1, 2, 3, 4]
```

**Arguments:**
- `list` — the list to modify
- `index` — integer, position to insert at (0-based)
- `item` — the value to insert

**Errors:** If index is out of range (negative or > list length).

---

### `remove(list, item)`

Removes the **first** occurrence of the item from the list. Modifies the list in place.

```plain
var nums = [1, 2, 3, 2]
remove(nums, 2)
display(nums)                 rem: [1, 3, 2]
```

**Errors:** If the item is not found in the list.

**Note:** Also works with tables — see [§10 Table Operations](#10-table-operations).

---

### `pop(list, index)`

Removes and returns the element at the specified index.

```plain
var nums = [10, 20, 30]
var item = pop(nums, 1)
display(item)                 rem: 20
display(nums)                 rem: [10, 30]
```

**Returns:** The removed element.

**Errors:** If index is out of range.

---

### `sort(list)`

Sorts the list in ascending order. Modifies the list in place.

```plain
var nums = [3, 1, 4, 1, 5]
sort(nums)
display(nums)                 rem: [1, 1, 3, 4, 5]

var words = ["banana", "apple", "cherry"]
sort(words)
display(words)                rem: [apple, banana, cherry]
```

**Returns:** null (modifies the list in place)

**Note:** Works with lists of integers, floats, or strings. The list should be homogeneous (all elements the same type) for predictable results.

---

### `reverse(list)`

Reverses the order of elements in the list. Modifies the list in place.

```plain
var nums = [1, 2, 3, 4]
reverse(nums)
display(nums)                 rem: [4, 3, 2, 1]
```

**Returns:** null (modifies the list in place)

---

### `contains(list, item)`

Returns `true` if the list contains the specified item.

```plain
var fruits = ["apple", "banana", "cherry"]
display(contains(fruits, "banana"))    rem: true
display(contains(fruits, "grape"))     rem: false
```

**Note:** Also works with strings — see [§4 String Operations](#4-string-operations).

---

## 10. Table Operations

### `len(table)`

Returns the number of key-value pairs in the table. (Same function as string/list `len`.)

```plain
display(len({"a": 1, "b": 2}))    rem: 2
display(len({}))                    rem: 0
```

---

### `keys(table)`

Returns a list of all keys in the table.

```plain
var scores = {"Alice": 95, "Bob": 87}
var names = keys(scores)
display(names)                rem: [Alice, Bob] (order may vary)
```

**Returns:** list of strings

**Note:** Table key order is not guaranteed. Use `sort()` if you need a specific order.

---

### `values(table)`

Returns a list of all values in the table.

```plain
var scores = {"Alice": 95, "Bob": 87}
var nums = values(scores)
display(nums)                 rem: [95, 87] (order may vary)
```

**Returns:** list

---

### `has_key(table, key)`

Returns `true` if the table contains the specified key.

```plain
var data = {"name": "Alice", "age": 30}
display(has_key(data, "name"))     rem: true
display(has_key(data, "email"))    rem: false
```

Use this before accessing a table key to avoid runtime errors.

---

### `remove(table, key)`

Removes the key-value pair with the given key from the table. Modifies the table in place.

```plain
var data = {"a": 1, "b": 2, "c": 3}
remove(data, "b")
display(data)                 rem: {a: 1, c: 3}
```

**Errors:** If the key is not found.

**Note:** Also works with lists — see [§9 List Operations](#9-list-operations).

---

## 11. File I/O — Simple

These functions read and write entire files in a single operation. They are the easiest way to work with files.

### `read_file(path)`

Reads the entire contents of a text file and returns it as a string.

```plain
var content = read_file("data.txt")
display(content)
```

**Errors:** If the file doesn't exist or can't be read.

---

### `write_file(path, content)`

Writes a string to a file, replacing any existing content. Creates the file if it doesn't exist.

```plain
write_file("output.txt", "Hello, World!")
```

---

### `append_file(path, content)`

Appends a string to the end of a file. Creates the file if it doesn't exist.

```plain
append_file("log.txt", "New log entry")
```

---

### `read_lines(path)`

Reads a text file and returns a list of strings, one per line.

```plain
var lines = read_lines("data.txt")
loop line in lines
    display(line)
```

**Returns:** list of strings (trailing newline is removed from the file; empty file returns an empty list)

---

### `write_lines(path, lines)`

Writes a list of strings to a file, one per line. Replaces any existing content.

```plain
var lines = ["Line 1", "Line 2", "Line 3"]
write_lines("output.txt", lines)
```

**Note:** Each element is converted to a string. A newline is added after each line, including the last.

---

### `read_binary(path)`

Reads the entire contents of a file as binary data.

```plain
var data = read_binary("image.png")
```

**Returns:** bytes

---

### `write_binary(path, data)`

Writes binary data to a file, replacing any existing content.

```plain
write_binary("copy.png", data)
```

---

### `append_binary(path, data)`

Appends binary data to the end of a file.

```plain
append_binary("data.bin", newData)
```

---

## 12. File I/O — Handle-Based

Handle-based I/O gives you more control by opening a file, performing multiple operations, and then closing it.

### `open(path, mode)`

Opens a file and returns a file handle.

```plain
var file = open("data.txt", "r")
```

**Modes:**

| Mode   | Description                         |
| ------ | ----------------------------------- |
| `"r"`  | Read (text) — file must exist       |
| `"w"`  | Write (text) — creates or truncates |
| `"a"`  | Append (text) — creates or appends  |
| `"rb"` | Read (binary)                       |
| `"wb"` | Write (binary)                      |
| `"ab"` | Append (binary)                     |

**Returns:** file handle

**Errors:** If the file can't be opened (e.g., read mode on a missing file).

---

### `close(handle)`

Closes a file handle. Always close files when done.

```plain
var file = open("data.txt", "r")
var content = read(file)
close(file)
```

**Tip:** Use `attempt/ensure` to guarantee files are closed:

```plain
var file = open("data.txt", "r")
attempt
    var content = read(file)
    display(content)
ensure
    close(file)
```

---

### `read(handle)`

Reads the entire remaining content from an open file handle.

```plain
var file = open("data.txt", "r")
var content = read(file)
close(file)
```

**Returns:** string (text mode) or bytes (binary mode)

---

### `read_line(handle)`

Reads the next line from an open file handle.

```plain
var file = open("data.txt", "r")
var line = read_line(file)
display(line)
close(file)
```

**Returns:** string (without trailing newline), or null if at end of file

---

### `read_bytes(handle, count)`

Reads up to `count` bytes from an open binary file handle.

```plain
var file = open("data.bin", "rb")
var chunk = read_bytes(file, 1024)
close(file)
```

**Returns:** bytes (may be fewer than `count` if near end of file)

---

### `write(handle, content)`

Writes content to an open file handle.

```plain
var file = open("output.txt", "w")
write(file, "Hello, World!")
close(file)
```

**Accepts:** string or bytes

---

### `write_line(handle, text)`

Writes a string followed by a newline to an open file handle.

```plain
var file = open("output.txt", "w")
write_line(file, "Line 1")
write_line(file, "Line 2")
close(file)
```

---

## 13. File System

### `file_exists(path)`

Returns `true` if a file (not a directory) exists at the given path.

```plain
if file_exists("config.txt")
    display("Config found")
else
    display("Config missing")
```

---

### `delete_file(path)`

Deletes a file.

```plain
delete_file("temp.txt")
```

**Errors:** If the file doesn't exist or can't be deleted.

---

### `rename_file(oldPath, newPath)`

Renames or moves a file.

```plain
rename_file("old_name.txt", "new_name.txt")
```

---

### `copy_file(source, destination)`

Copies a file to a new location.

```plain
copy_file("original.txt", "backup.txt")
```

---

### `file_size(path)`

Returns the size of a file in bytes.

```plain
var size = file_size("data.txt")
display(v"File is {size} bytes")
```

**Returns:** integer

---

### `dir_exists(path)`

Returns `true` if a directory exists at the given path.

```plain
if dir_exists("output")
    display("Directory exists")
```

---

### `create_dir(path)`

Creates a new directory.

```plain
create_dir("output")
```

**Errors:** If the directory already exists or the parent directory doesn't exist.

---

### `delete_dir(path)`

Deletes an empty directory.

```plain
delete_dir("temp_folder")
```

**Errors:** If the directory doesn't exist, isn't empty, or can't be deleted.

---

### `list_dir(path)`

Returns a list of file and directory names in the given directory.

```plain
var entries = list_dir(".")
loop name in entries
    display(name)
```

**Returns:** list of strings (names only, not full paths)

---

## 14. Path Operations

### `join_path(part1, part2, ...)`

Joins path components using the operating system's path separator.

```plain
var path = join_path("home", "user", "documents")
display(path)            rem: home/user/documents (on Linux/Mac)
```

**Arguments:** One or more strings.

---

### `split_path(path)`

Splits a path into its directory and filename components.

```plain
var parts = split_path("/home/user/file.txt")
display(parts)           rem: [/home/user, file.txt]
```

**Returns:** list of two strings: `[directory, filename]`

---

### `get_extension(path)`

Returns the file extension including the leading dot.

```plain
display(get_extension("photo.jpg"))       rem: .jpg
display(get_extension("archive.tar.gz"))  rem: .gz
display(get_extension("README"))          rem: (empty string)
```

---

### `absolute_path(path)`

Returns the absolute path for a relative path.

```plain
var abs = absolute_path("data.txt")
display(abs)             rem: /home/user/project/data.txt (full path)
```

---

### `script_dir()`

Returns the absolute path of the directory containing the currently executing script.

```plain
var dir = script_dir()
display(dir)             rem: /home/user/project/examples

rem: Use it to create files in the script's directory
var dataFile = join_path(script_dir(), "data.txt")
write_file(dataFile, "Hello!")
```

**Returns:** string (absolute path to script directory)

**Note:** This is useful for making file paths relative to the script location rather than the current working directory.

---

## 15. Timing and Events

### `sleep(milliseconds)`

Pauses execution for the specified number of milliseconds.

```plain
display("Wait...")
sleep(1000)         rem: Wait 1 second
display("Done!")
```

**Arguments:** integer

**Returns:** null

---

### `time()`

Returns the current Unix timestamp in milliseconds.

```plain
var start = time()
rem: ... do something ...
var end = time()
display("Elapsed:", end - start, "ms")
```

**Returns:** integer

---

### `date()`

Returns a table containing the current date and time components.

```plain
var now = date()
display(v"Date: {now.year}-{now.month}-{now.day}")
display(v"Time: {now.hour}:{now.minute}:{now.second}")
```

**Returns:** table with keys: `year`, `month`, `day`, `hour`, `minute`, `second` (all integers)

---

### `create_timer(interval, callback)`

Creates a repeating timer that calls a task at regular intervals. The timer does not start automatically — call `start_timer()` to begin.

```plain
task OnTick()
    display("Tick!")

task Main()
    var timer = create_timer(1000, OnTick)
    start_timer(timer)
    wait_for_events()
```

**Arguments:**
- `interval` — integer, milliseconds between calls
- `callback` — a task name (no parentheses)

**Returns:** timer object

---

### `create_timeout(delay, callback)`

Creates a one-shot timer that calls a task once after a delay. Like `create_timer`, it must be started with `start_timer()`.

```plain
task OnDone()
    display("Time's up!")

task Main()
    var timeout = create_timeout(3000, OnDone)
    start_timer(timeout)
    wait_for_events()
```

**Arguments:**
- `delay` — integer, milliseconds until the callback fires
- `callback` — a task name

**Returns:** timer object

---

### `start_timer(timer)`

Starts a timer or timeout. The timer begins running asynchronously.

```plain
var timer = create_timer(500, OnTick)
start_timer(timer)
```

---

### `stop_timer(timer)`

Stops a running timer. The timer can be restarted with `start_timer()`.

```plain
stop_timer(timer)
```

---

### `cancel_timer(timer)`

Permanently cancels a timer. It cannot be restarted.

```plain
cancel_timer(timer)
```

---

### `wait_for_events()`

Blocks execution until all timers and timeouts have completed. Use this at the end of a program that uses timers.

```plain
task Main()
    var timeout = create_timeout(2000, OnDone)
    start_timer(timeout)
    wait_for_events()       rem: waits until the timeout fires
    display("All done!")
```

**Note:** For repeating timers, you must cancel them from within a callback (using `cancel_timer` and `stop_events`) or `wait_for_events` will never return.

---

### `run_events(duration)`

Runs the event loop for the specified duration in milliseconds, then stops.

```plain
run_events(5000)            rem: process events for 5 seconds
```

**Argument:** integer (milliseconds)

---

### `stop_events()`

Stops the event loop from within a callback. Use this to end `wait_for_events()`.

```plain
task OnComplete()
    display("Done!")
    stop_events()           rem: signals wait_for_events() to return

task Main()
    var timeout = create_timeout(1000, OnComplete)
    start_timer(timeout)
    wait_for_events()
```

### Timer Callback Signatures

Timer callbacks can be defined in two ways:

**Simple callback** — no parameters:

```plain
task OnTick()
    display("Tick!")
```

**Detailed callback** — receives timer info:

```plain
task OnTick with (timer, elapsed)
    display(v"Elapsed: {elapsed}ms")
    if elapsed > 5000
        cancel_timer(timer)
        stop_events()
```

---

## 16. Serial Port I/O

PLAIN provides comprehensive serial port support for data acquisition and communication with hardware devices. This includes support for physical serial ports (RS-232, RS-485) and virtual COM ports (USB-to-serial adapters).

**Common use cases:**
- Reading NMEA 0183 GPS data
- Communicating with marine electronics and sensors
- Industrial data acquisition
- Embedded systems interfacing

---

### `serial_ports()`

Returns a list of available serial port names on the system.

```plain
var ports = serial_ports()
loop port in ports
    display(port)
rem: Linux: /dev/ttyUSB0, /dev/ttyACM0
rem: macOS: /dev/cu.usbserial-*
rem: Windows: COM1, COM3, etc.
```

**Arguments:** None

**Returns:** list of strings — Available serial port names

**Note:** Returns an empty list if no serial ports are detected. Virtual COM ports (USB-to-serial) are listed alongside physical ports.

---

### `serial_open(port, baud [, config])`

Opens a serial port connection with the specified baud rate and configuration.

```plain
var gps = serial_open("/dev/ttyUSB0", 4800)
var instrument = serial_open("COM3", 9600, "8N1")
```

**Arguments:**
- `port` (string) — Port name (e.g., "/dev/ttyUSB0", "COM3")
- `baud` (integer) — Baud rate (e.g., 4800, 9600, 19200, 38400, 57600, 115200)
- `config` (string, optional) — Configuration string, default "8N1"

**Config format:** `{data_bits}{parity}{stop_bits}`
- Data bits: 5, 6, 7, or 8
- Parity: N (none), E (even), O (odd), M (mark), S (space)
- Stop bits: 1 or 2

**Returns:** serial_port handle

**Common configurations:**
- `"8N1"` — 8 data bits, no parity, 1 stop bit (most common)
- `"7E1"` — 7 data bits, even parity, 1 stop bit
- `"8N2"` — 8 data bits, no parity, 2 stop bits

---

### `serial_close(port)`

Closes an open serial port connection.

```plain
serial_close(gps)
```

**Arguments:**
- `port` (serial_port) — Serial port handle from `serial_open()`

**Returns:** null

---

### `serial_write(port, data)`

Writes data to the serial port.

```plain
serial_write(port, "$CCMSG,1,1*hh\r\n")
var bytes_sent = serial_write(port, "Hello")
```

**Arguments:**
- `port` (serial_port) — Serial port handle
- `data` (string) — Data to send

**Returns:** integer — Number of bytes written

---

### `serial_read(port, count)`

Reads up to `count` bytes from the serial port.

```plain
var data = serial_read(port, 256)
```

**Arguments:**
- `port` (serial_port) — Serial port handle
- `count` (integer) — Maximum number of bytes to read

**Returns:** string — Data read (may be less than `count` bytes)

**Note:** This function respects the timeout set by `serial_set_timeout()`. It blocks until data is available or the timeout expires.

---

### `serial_read_line(port)`

Reads data from the serial port until a newline character (`\n`) is encountered. This is the primary function for reading line-based protocols like NMEA 0183.

```plain
var sentence = serial_read_line(gps)
rem: Returns "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,47.0,M,,*47"
```

**Arguments:**
- `port` (serial_port) — Serial port handle

**Returns:** string — Line of text with trailing `\r\n` or `\n` removed

**Note:** Blocks until a complete line is received or timeout expires. Ideal for NMEA sentences, which are CR+LF terminated.

---

### `serial_available(port)`

Checks if data is waiting to be read from the serial port.

```plain
if serial_available(port)
    var data = serial_read_line(port)
```

**Arguments:**
- `port` (serial_port) — Serial port handle

**Returns:** boolean — `true` if data is available, `false` otherwise

**Note:** This is a non-blocking check. Useful for polling-based reading.

---

### `serial_set_timeout(port, milliseconds)`

Sets the read timeout for the serial port.

```plain
serial_set_timeout(gps, 2000)    rem: 2-second timeout
serial_set_timeout(port, 0)      rem: non-blocking
serial_set_timeout(port, -1)     rem: block forever
```

**Arguments:**
- `port` (serial_port) — Serial port handle
- `milliseconds` (integer) — Timeout value
  - `0` = non-blocking (return immediately)
  - `-1` = block forever (wait until data arrives)
  - `> 0` = wait up to N milliseconds

**Returns:** null

**Best practice:** Always set a timeout in production code to prevent indefinite blocking.

---

### `serial_flush(port)`

Flushes both input and output buffers, discarding any pending data.

```plain
serial_flush(port)
```

**Arguments:**
- `port` (serial_port) — Serial port handle

**Returns:** null

**Use case:** Clear stale data before starting a new communication sequence.

---

### `serial_set_dtr(port, state)`

Controls the DTR (Data Terminal Ready) handshake line.

```plain
serial_set_dtr(port, true)     rem: assert DTR
serial_set_dtr(port, false)    rem: clear DTR
```

**Arguments:**
- `port` (serial_port) — Serial port handle
- `state` (boolean) — `true` to assert, `false` to clear

**Returns:** null

---

### `serial_set_rts(port, state)`

Controls the RTS (Request To Send) handshake line.

```plain
serial_set_rts(port, true)     rem: assert RTS
serial_set_rts(port, false)    rem: clear RTS
```

**Arguments:**
- `port` (serial_port) — Serial port handle
- `state` (boolean) — `true` to assert, `false` to clear

**Returns:** null

---

### `serial_get_signals(port)`

Reads the state of modem control lines.

```plain
var signals = serial_get_signals(port)
display("CTS:", signals["cts"])
display("DSR:", signals["dsr"])
```

**Arguments:**
- `port` (serial_port) — Serial port handle

**Returns:** table with keys:
- `"cts"` (boolean) — Clear To Send
- `"dsr"` (boolean) — Data Set Ready
- `"ri"` (boolean) — Ring Indicator
- `"dcd"` (boolean) — Data Carrier Detect

---

### Serial Port Example: NMEA GPS Reader

```plain
task Main()
    display("Available serial ports:")
    var ports = serial_ports()
    loop port in ports
        display("  " & port)

    if len(ports) = 0
        display("No serial ports found.")
        deliver null

    rem: Open GPS on first available port (typically 4800 baud for NMEA)
    var gps = serial_open(ports[0], 4800)
    serial_set_timeout(gps, 5000)

    display("Reading NMEA sentences...")
    loop i from 1 to 10
        var sentence = serial_read_line(gps)

        rem: Parse GPGGA (position) sentences
        if starts_with(sentence, "$GPGGA")
            var fields = split(sentence, ",")
            display(v"Position: {fields[2]} {fields[3]}, {fields[4]} {fields[5]}")
        otherwise
            display(sentence)

    serial_close(gps)
    display("Done.")
```

---

## 17. Network I/O

PLAIN provides TCP and UDP network connectivity for client and server applications. These functions enable communication over IP networks, including reading NMEA data over TCP/IP.

### 17.1 `net_connect(host, port [, protocol])`

Opens a network connection to a remote host.

**Parameters:**
- `host` (string): Hostname or IP address
- `port` (integer): Port number (1-65535)
- `protocol` (string, optional): "tcp" (default) or "udp"

**Returns:** Network connection handle, or error

**Example:**
```plain
conn = net_connect("192.168.1.100", 10110)
if is_error(conn)
    display("Connection failed: " + conn)
    stop
```

### 17.2 `net_close(conn)`

Closes a network connection.

**Parameters:**
- `conn` (net_conn): Connection handle from `net_connect()` or `net_accept()`

**Returns:** `null` on success, or error

**Example:**
```plain
net_close(conn)
```

### 17.3 `net_write(conn, data)`

Sends data over a network connection.

**Parameters:**
- `conn` (net_conn): Connection handle
- `data` (string or bytes): Data to send

**Returns:** Number of bytes written, or error

**Example:**
```plain
bytes_sent = net_write(conn, "Hello, server!\r\n")
display("Sent " + to_string(bytes_sent) + " bytes")
```

### 17.4 `net_read(conn, count)`

Reads up to `count` bytes from a network connection.

**Parameters:**
- `conn` (net_conn): Connection handle
- `count` (integer): Maximum number of bytes to read

**Returns:** String containing received data, or error

**Example:**
```plain
data = net_read(conn, 1024)
if is_error(data)
    display("Read error: " + data)
otherwise
    display("Received: " + data)
```

### 17.5 `net_read_line(conn)`

Reads a line of text from a network connection (up to newline character). Automatically strips CR+LF or LF line endings.

**Parameters:**
- `conn` (net_conn): Connection handle

**Returns:** String containing the line (without line ending), or error

**Example:**
```plain
line = net_read_line(conn)
if is_error(line)
    display("Error: " + line)
otherwise
    display("Received line: " + line)
```

### 17.6 `net_set_timeout(conn, milliseconds)`

Sets the read timeout for a network connection.

**Parameters:**
- `conn` (net_conn): Connection handle
- `milliseconds` (integer): Timeout in milliseconds
  - `-1` = block forever (wait indefinitely)
  - `0` = non-blocking (return immediately)
  - `> 0` = timeout after specified milliseconds

**Returns:** `null` on success, or error

**Example:**
```plain
net_set_timeout(conn, 5000)  # 5 second timeout
```

### 17.7 `net_listen(port [, protocol])`

Creates a network listener (server) on the specified port.

**Parameters:**
- `port` (integer): Port number to listen on (1-65535)
- `protocol` (string, optional): "tcp" (default) or "udp"

**Returns:** Listener handle, or error

**Example:**
```plain
listener = net_listen(8080)
if is_error(listener)
    display("Failed to start server: " + listener)
    stop
display("Server listening on port 8080")
```

### 17.8 `net_accept(listener)`

Accepts an incoming connection on a listener. This function blocks until a client connects.

**Parameters:**
- `listener` (net_conn): Listener handle from `net_listen()`

**Returns:** Client connection handle, or error

**Example:**
```plain
client = net_accept(listener)
if is_error(client)
    display("Accept failed: " + client)
otherwise
    display("Client connected!")
```

### Complete Example: NMEA GPS Reader over TCP/IP

Many GPS receivers and marine electronics support NMEA 0183 over TCP/IP (typically port 10110):

```plain
# Connect to GPS receiver on network
gps = net_connect("192.168.1.100", 10110)
if is_error(gps)
    display("Failed to connect: " + gps)
    stop

display("Connected to GPS receiver")
net_set_timeout(gps, 5000)  # 5 second timeout

# Read 10 NMEA sentences
count = 0
repeat while count < 10
    sentence = net_read_line(gps)
    if is_error(sentence)
        display("Error reading: " + sentence)
        break

    # Only display GPRMC sentences (position data)
    if starts_with(sentence, "$GPRMC")
        display(sentence)
        count = count + 1

net_close(gps)
display("Done.")
```

---

## Quick Reference Table

| Category           | Functions                                                                                                                              |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| **Console**        | `display`, `get`, `clear`, `text_at`, `text_color`, `draw_line`, `draw_box`                                                           |
| **Types**          | `is_int`, `is_float`, `is_string`, `is_bool`, `is_list`, `is_table`, `is_null`, `type_of`                                              |
| **Conversion**     | `to_int`, `to_float`, `to_string`, `to_bool`, `to_bin`, `to_hex`                                                                       |
| **Strings**        | `len`, `upper`, `lower`, `trim`, `split`, `join`, `substring`, `replace`, `contains`, `starts_with`, `ends_with`                       |
| **Math**           | `abs`, `sqrt`, `sqr`, `pow`, `round`, `floor`, `ceil`, `min`, `max`, `mod`                                                             |
| **Trigonometry**   | `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `atan2`                                                                                   |
| **Logarithms**     | `log`, `log10`, `log2`, `exp`                                                                                                          |
| **Random**         | `random`, `random_int`, `random_choice`                                                                                                |
| **Lists**          | `len`, `append`, `insert`, `remove`, `pop`, `sort`, `reverse`, `contains`                                                              |
| **Tables**         | `len`, `keys`, `values`, `has_key`, `remove`                                                                                           |
| **Files (simple)** | `read_file`, `write_file`, `append_file`, `read_lines`, `write_lines`, `read_binary`, `write_binary`, `append_binary`                  |
| **Files (handle)** | `open`, `close`, `read`, `read_line`, `read_bytes`, `write`, `write_line`                                                              |
| **File system**    | `file_exists`, `delete_file`, `rename_file`, `copy_file`, `file_size`, `dir_exists`, `create_dir`, `delete_dir`, `list_dir`            |
| **Paths**          | `join_path`, `split_path`, `get_extension`, `absolute_path`                                                                            |
| **Timing**         | `sleep`, `create_timer`, `create_timeout`, `start_timer`, `stop_timer`, `cancel_timer`, `wait_for_events`, `run_events`, `stop_events` |
| **Serial Port**    | `serial_ports`, `serial_open`, `serial_close`, `serial_write`, `serial_read`, `serial_read_line`, `serial_available`, `serial_set_timeout`, `serial_flush`, `serial_set_dtr`, `serial_set_rts`, `serial_get_signals` |
| **Network I/O**    | `net_connect`, `net_close`, `net_write`, `net_read`, `net_read_line`, `net_set_timeout`, `net_listen`, `net_accept` |

---

*This is the complete standard library reference for PLAIN version 1.0. For language syntax, see the [Language Reference](LANGUAGE-REFERENCE.md). For tutorial examples, see [TUTORIAL.md](TUTORIAL.md).*
