# PLAIN Programming Language - Interactive Tutorial

> **Learn PLAIN step-by-step with hands-on examples!** 🎓

This tutorial will guide you through the PLAIN programming language with practical examples you can run and modify. Each lesson builds on the previous one, introducing new concepts gradually. By the end, you'll be writing complete programs with confidence!

---

## Table of Contents

1. [Hello, PLAIN!](#lesson-1-hello-plain)
2. [Variables and Types](#lesson-2-variables-and-types)
3. [User Input](#lesson-3-user-input)
4. [Making Decisions](#lesson-4-making-decisions)
5. [Loops and Repetition](#lesson-5-loops-and-repetition)
6. [Working with Lists](#lesson-6-working-with-lists)
7. [Working with Tables](#lesson-7-working-with-tables)
8. [Creating Tasks](#lesson-8-creating-tasks)
9. [Tasks with Parameters](#lesson-9-tasks-with-parameters)
10. [Functions and Return Values](#lesson-10-functions-and-return-values)
11. [Project: Gradebook](#lesson-11-project-gradebook) ⭐
12. [String Operations](#lesson-12-string-operations)
13. [Error Handling](#lesson-13-error-handling)
14. [Records and Custom Types](#lesson-14-records-and-custom-types)
15. [Working with Files](#lesson-15-working-with-files)
16. [Randomness and Games](#lesson-16-randomness-and-games)
17. [Modules and Organization](#lesson-17-modules-and-organization)
18. [Events and Timers](#lesson-18-events-and-timers)

---

## How to Use This Tutorial

Each lesson has:
- **Concept**: What you'll learn
- **Example Program**: A working PLAIN program in `examples/tutorial/`
- **What's Happening?**: A walkthrough of the key ideas
- **Try It**: Exercises to practice on your own
- **Key Takeaways**: Summary of important points

### Running the Examples

```bash
# From the PLAIN directory, run any lesson:
go run ./cmd/plain/ examples/tutorial/lesson_01_hello.plain

# Or use the IDE:
go run ./cmd/plain-ide/
# Then open a lesson file and press F5 to run
```

### Tips for Learning

- **Type the code yourself** rather than just reading it — you'll learn faster!
- **Experiment freely** — change values, add lines, break things, fix them
- **Read the error messages** — PLAIN tries to tell you exactly what went wrong
- **Have fun** — programming is creative and rewarding 🎉

---

## Lesson 1: Hello, PLAIN!

### Concept: Your First Program

Every PLAIN program starts with `task Main()` — that's where your code begins. Let's write the simplest program possible and see it run!

### Example: `lesson_01_hello.plain`

```plain
rem: Lesson 1 - Hello, PLAIN!
rem: Your very first PLAIN program

task Main()
    display("Hello, PLAIN!")
    display("Welcome to programming!")
    display("Let's learn together!")
```

### What's Happening?

- `rem:` — A **comment**. It's a note for humans; PLAIN ignores it completely
- `task Main()` — Declares the **main task**, the entry point of your program
- **Indentation matters** — everything inside Main is indented with spaces
- `display("...")` — Shows text on the screen. The text goes inside quotes

### Try It

1. Run the program and see the output
2. Change the messages to greet yourself by name
3. Add two more `display()` lines with your own messages

### Key Takeaways

✓ Every program needs `task Main()`
✓ Use `rem:` for comments
✓ Use `display()` to show output
✓ Indentation defines what's inside a task

---

## Lesson 2: Variables and Types

### Concept: Storing and Using Data

Variables are named containers that hold data. PLAIN has four basic types: **integer**, **float**, **string**, and **boolean**. You can let PLAIN figure out the type automatically, or declare it explicitly.

### Example: `lesson_02_variables.plain`

```plain
rem: Lesson 2 - Variables and Types
rem: Learn about storing data in variables

task Main()
    rem: Variables with type prefix inference
    var intAge = 25
    var fltPrice = 9.99
    var strName = "Alice"
    var blnActive = true

    display("Name: " & strName)
    display("Age: " & intAge)
    display("Price: $" & fltPrice)
    display("Active: " & blnActive)

    rem: Constants cannot be changed
    fxd PI as float = 3.14159
    fxd APP_NAME as string = "My First App"

    display("Pi is " & PI)
    display("App: " & APP_NAME)

    rem: Explicit type with 'as' keyword
    var score as integer = 95
    var temperature as float = 72.5

    display("Score: " & score)
    display("Temperature: " & temperature)

    rem: Changing variable values
    var intCount = 0
    display("Count starts at: " & intCount)
    intCount = intCount + 1
    display("Count is now: " & intCount)
    intCount += 5
    display("Count after adding 5: " & intCount)
```

### What's Happening?

- `var` creates a **variable** (can be changed later)
- `fxd` creates a **constant** (fixed — cannot be changed)
- **Type prefixes** let PLAIN infer the type: `int` = integer, `flt` = float, `str` = string, `bln` = boolean
- You can also declare types explicitly with `as`: `var score as integer = 95`
- `&` **concatenates** (joins) strings together for display
- Constants require an explicit type: `fxd PI as float = 3.14159`

### PLAIN Data Types

| Type | Prefix | Example | Description |
|------|--------|---------|-------------|
| `integer` | `int` | `42` | Whole numbers |
| `float` | `flt` | `3.14` | Decimal numbers |
| `string` | `str` | `"hello"` | Text |
| `boolean` | `bln` | `true` | True or false |

### Try It

1. Create variables for your name, age, and a favorite number
2. Display them all using `&` to build a sentence
3. Create a constant for your birth year and display it

### Key Takeaways

✓ `var` creates variables, `fxd` creates constants
✓ Type prefixes (`int`, `flt`, `str`, `bln`) enable automatic type inference
✓ Use `as` for explicit types: `var x as integer = 10`
✓ `&` joins values together into strings

---

## Lesson 3: User Input

### Concept: Making Programs Interactive

Programs become interesting when they can talk to the user! The `get()` function pauses and waits for the user to type something, then gives you back what they typed as a string.

### Example: `lesson_03_input.plain`

```plain
rem: Lesson 3 - User Input
rem: Getting input from the user and building responses

task Main()
    rem: Getting input with get()
    var strName = get("What is your name? ")
    var strColor = get("What is your favorite color? ")

    rem: String concatenation with &
    display("Hello, " & strName & "!")
    display("Nice to meet you!")

    rem: String interpolation with v""
    display(v"So {strName}, your favorite color is {strColor}!")

    rem: Converting input to numbers
    var strAge = get("How old are you? ")
    var intAge = to_int(strAge)

    var intNextYear = intAge + 1
    display(v"Next year you will be {intNextYear}!")

    rem: Building a greeting message
    var strGreeting = "Welcome, " & strName & "! "
    strGreeting &= "You are " & intAge & " years old "
    strGreeting &= "and you love " & strColor & "."
    display(strGreeting)
```

### What's Happening?

- `get("prompt")` — Displays a prompt and waits for the user to type a response
- `get()` always returns a **string**, even if the user types a number
- `to_int()` converts a string to an integer so you can do math with it
- `v"..."` is **string interpolation** — variables inside `{braces}` get replaced with their values
- `&=` appends to a string (shorthand for `strGreeting = strGreeting & "..."`)

### Try It

1. Ask the user for their name and favorite food, then display a sentence about them
2. Ask for two numbers, convert them with `to_int()`, and display their sum
3. Use `v"..."` interpolation to build a fun "Mad Libs" style story

### Key Takeaways

✓ `get("prompt")` reads user input as a string
✓ Use `to_int()` or `to_float()` to convert strings to numbers
✓ `v"Hello {name}!"` is string interpolation — cleaner than concatenation
✓ `&=` appends to an existing string

---

## Lesson 4: Making Decisions

### Concept: Controlling Program Flow

Programs need to make choices! The `if/else` statement runs different code depending on whether a condition is true or false. For multiple options, `choose` is even cleaner.

### Example: `lesson_04_decisions.plain`

```plain
rem: Lesson 4 - Making Decisions
rem: Using if/else and choose to control program flow

task Main()
    rem: Simple if/else
    var intTemperature = 75

    if intTemperature > 80
        display("It's hot outside!")
    else
        display("The weather is pleasant.")

    rem: Nested if/else for multiple conditions
    var intScore = 85

    if intScore >= 90
        display("Grade: A - Excellent!")
    else
        if intScore >= 80
            display("Grade: B - Good job!")
        else
            if intScore >= 70
                display("Grade: C - Keep trying!")
            else
                display("Grade: F - Study harder!")

    rem: Logical operators: and, or, not
    var intAge = 16
    var blnHasPermission = true

    if intAge >= 16 and blnHasPermission
        display("You can drive!")

    rem: Choose statement for multiple options
    var strDay = "Monday"

    choose strDay
        choice "Monday"
            display("Start of the work week!")
        choice "Friday"
            display("Almost the weekend!")
        choice "Saturday"
            display("Weekend fun!")
        default
            display("Just a regular day.")
```

### What's Happening?

- `if condition` — Runs the indented code only when the condition is true
- `else` — Runs when the condition is false
- **Comparison operators**: `==`, `!=`, `<`, `>`, `<=`, `>=`
- **Logical operators**: `and`, `or`, `not` — combine conditions naturally
- `choose/choice/default` — Like a switch statement, matches a value against options

### Try It

1. Write a program that checks if a number is positive, negative, or zero
2. Use `and`/`or` to check if a person qualifies for a student discount (age < 25 and has a student ID)
3. Use `choose` to display a message for each season ("Spring", "Summer", "Fall", "Winter")

### Key Takeaways

✓ `if/else` controls which code runs based on conditions
✓ Nest `if/else` for multiple branches
✓ `and`, `or`, `not` combine conditions naturally in English
✓ `choose/choice/default` cleanly handles multiple specific values

---

## Lesson 5: Loops and Repetition

### Concept: Doing Things Over and Over

Loops let you repeat code without writing it over and over. PLAIN has **counting loops** (do something N times) and **collection loops** (do something for each item in a list).

### Example: `lesson_05_loops.plain`

```plain
rem: Lesson 5 - Loops and Repetition

task Main()
    rem: Counting loop (from...to)
    display("=== Counting from 1 to 5 ===")
    loop i from 1 to 5
        display(v"Count: {i}")

    rem: Counting with step
    display("")
    display("=== Even numbers from 2 to 10 ===")
    loop i from 2 to 10 step 2
        display(i)

    rem: Countdown with negative step
    display("")
    display("=== Countdown! ===")
    loop i from 5 to 1 step -1
        display(i & "...")
    display("Liftoff!")

    rem: Collection loop (for-each)
    display("")
    display("=== Favorite fruits ===")
    var fruits = ["apple", "banana", "cherry", "mango"]
    loop fruit in fruits
        display("I like " & fruit & "!")

    rem: Nested loops - Multiplication table
    display("")
    display("=== Multiplication Table (1-4) ===")
    loop row from 1 to 4
        var line = ""
        loop col from 1 to 4
            line = line & (row * col) & "  "
        display(line)

    rem: Summing with a loop
    display("")
    display("=== Sum of 1 to 10 ===")
    var total = 0
    loop i from 1 to 10
        total = total + i
    display(v"Sum = {total}")
```

### What's Happening?

- `loop i from 1 to 5` — Counts from 1 to 5, setting `i` each time
- `step 2` — Counts by twos (or any number); use negative steps for countdowns
- `loop fruit in fruits` — Iterates over each item in a list
- **Nested loops** — A loop inside a loop, great for grids and tables
- **Accumulating**: Use `total = total + i` to build up a sum inside a loop

> 💡 **Tip**: Inside loops, always write `total = total + x` instead of `total += x` for reliable accumulation.

### Try It

1. Print the numbers 1 to 20 using a counting loop
2. Print every third number from 3 to 30 using `step 3`
3. Create a list of your friends' names and loop through it to greet each one

### Key Takeaways

✓ `loop i from start to end` counts through a range
✓ `step N` controls the increment (including negative for countdowns)
✓ `loop item in list` iterates over each element
✓ Loops can be nested for grids and complex patterns

---

## Lesson 6: Working with Lists

### Concept: Ordered Collections of Items

Lists hold multiple values in order. You can add, remove, search, sort, and loop through them — they're one of the most useful data structures in programming!

### Example: `lesson_06_lists.plain`

See `examples/tutorial/lesson_06_lists.plain` for the complete program.

### What's Happening?

- `var colors = ["red", "green", "blue"]` — Creates a list with square brackets
- `colors[0]` — Access items by index (starting from 0!)
- `append(list, item)` — Adds an item to the end
- `insert(list, index, item)` — Inserts at a specific position
- `remove(list, item)` — Removes by value
- `pop(list, index)` — Removes by index and returns the removed item
- `sort(list)` and `reverse(list)` — Reorder the list in place
- `contains(list, item)` — Checks if an item is in the list
- `len(list)` — Returns how many items are in the list

### Try It

1. Create a list of 5 animals, then add 2 more with `append()`
2. Sort the animal list alphabetically, then reverse it
3. Write a numbered list using a loop counter: `1. cat`, `2. dog`, etc.

### Key Takeaways

✓ Lists use square brackets: `["a", "b", "c"]`
✓ Indexing starts at 0 (first item is `list[0]`)
✓ `append()`, `insert()`, `remove()`, `pop()` modify the list
✓ `sort()`, `reverse()`, `contains()`, `len()` are essential list tools

---

## Lesson 7: Working with Tables

### Concept: Key-Value Data Storage

Tables (also called dictionaries or maps in other languages) store data as **key-value pairs**. Instead of accessing items by position, you access them by name — perfect for structured data like a person's profile.

### Example: `lesson_07_tables.plain`

See `examples/tutorial/lesson_07_tables.plain` for the complete program.

### What's Happening?

- `var person = {"name": "Alice", "age": 30}` — Creates a table with curly braces
- `person["name"]` — Access a value by its key
- `person["email"] = "alice@example.com"` — Add or update a key
- `has_key(table, key)` — Check if a key exists before accessing it
- `keys(table)` and `values(table)` — Get all keys or values as lists
- `remove(table, key)` — Remove a key-value pair
- `loop key in keys(table)` — Iterate over all entries

### Try It

1. Create a table for a book with keys: "title", "author", "year", "pages"
2. Check if the book has a "genre" key, and add one if it doesn't
3. Loop through the book table and display each key-value pair

### Key Takeaways

✓ Tables use curly braces: `{"key": value}`
✓ Access values with `table["key"]`
✓ `has_key()` prevents errors when a key might not exist
✓ `keys()` and `values()` make tables iterable

---

## Lesson 8: Creating Tasks

### Concept: Organizing Code into Reusable Blocks

As programs grow, you need to organize them. **Tasks** are named blocks of code that you can call whenever you need them. Think of them as mini-programs within your program.

### Example: `lesson_08_tasks.plain`

```plain
rem: Lesson 8 - Creating Tasks

task Main()
    SayHello()
    DrawLine()
    SayGoodbye()
    DrawLine()
    ShowMenu()
    DrawLine()

rem: A simple task with no parameters
task SayHello()
    display("Hello there!")
    display("Welcome to the program!")

task SayGoodbye()
    display("Thanks for using the program!")
    display("Goodbye!")

task DrawLine()
    display("========================")

task ShowMenu()
    display("1. Start Game")
    display("2. View Scores")
    display("3. Settings")
    display("4. Quit")
```

### What's Happening?

- `task Name()` — Defines a new task (like a procedure or function)
- `Name()` — Calls the task, running its code
- Tasks can be defined **after** they're called — PLAIN finds them automatically
- Each task is an **independent block** — organize related code together
- Tasks can call other tasks, building up complex behavior from simple pieces

### Try It

1. Write a `DisplayHeader()` task that shows your program's name in a decorative box
2. Create separate tasks for different sections of a menu program
3. Write a task that calls three other tasks in sequence

### Key Takeaways

✓ `task Name()` defines a reusable block of code
✓ Call a task by writing `Name()`
✓ Tasks make code organized, readable, and reusable
✓ Tasks can be defined anywhere in the file

---

## Lesson 9: Tasks with Parameters

### Concept: Passing Data into Tasks

Tasks become much more powerful when they can accept **parameters** — data you pass in when calling them. Use the `with` keyword to define parameters.

### Example: `lesson_09_parameters.plain`

See `examples/tutorial/lesson_09_parameters.plain` for the complete program.

Key snippet:

```plain
rem: Task with one parameter
task Greet with (strName)
    display(v"Hello, {strName}! Nice to meet you!")

rem: Task with two parameters
task DisplayScore with (strName, intScore)
    var strGrade = "F"
    if intScore >= 90
        strGrade = "A"
    else
        if intScore >= 80
            strGrade = "B"
    display(v"  {strName}: {intScore}/100 (Grade: {strGrade})")
```

### What's Happening?

- `task Greet with (strName)` — Defines a task that takes one parameter
- `Greet("Alice")` — Calls it, passing `"Alice"` as `strName`
- `with` means this is a **procedure** — it does something but doesn't return a value
- Parameters are **immutable** inside the task — you can read them but not change them
- Multiple parameters are separated by commas: `with (name, score)`

### Try It

1. Write a `PrintBox` task that takes a message and displays it inside a border
2. Create a `CompareNumbers` task that takes two numbers and prints which is larger
3. Write a `RepeatMessage` task that takes a message and a count, then displays the message that many times

### Key Takeaways

✓ `with (params)` defines task parameters
✓ Pass values in parentheses when calling: `Greet("Alice")`
✓ Parameters are read-only inside the task
✓ Tasks with `with` are **procedures** — they perform actions

---

## Lesson 10: Functions and Return Values

### Concept: Tasks That Compute and Return Results

Sometimes you need a task that **computes a value and gives it back**. In PLAIN, the `using` keyword marks a task as a **function**, and `deliver` sends the result back to the caller.

### Example: `lesson_10_functions.plain`

See `examples/tutorial/lesson_10_functions.plain` for the complete program.

Key snippet:

```plain
rem: Function with 'using' - must deliver a value
task Add using (a, b)
    deliver a + b

task IsEven using (n)
    deliver n % 2 == 0

task FahrenheitToCelsius using (f)
    deliver round((f - 32) * 5 / 9)
```

Calling functions:

```plain
var result = Add(5, 3)
display(v"5 + 3 = {result}")

if IsEven(42)
    display("42 is even")
```

### What's Happening?

- `using` signals this is a **function** — it must return a value
- `deliver value` — Returns the value to whoever called the function
- Function results can be stored in variables: `var result = Add(5, 3)`
- Function results can be used directly: `display(Add(5, 3))`
- Function results can be used in conditions: `if IsEven(42)`

### `with` vs `using` — What's the Difference?

| | `with` (Procedure) | `using` (Function) |
|---|---|---|
| **Purpose** | Does something | Computes something |
| **Returns a value?** | No | Yes, with `deliver` |
| **Example** | `task Greet with (name)` | `task Add using (a, b)` |
| **Call style** | `Greet("Alice")` | `var x = Add(5, 3)` |

### Try It

1. Write an `Area` function that takes width and height and delivers the area
2. Write a `Max` function that takes two numbers and delivers the larger one
3. Write a `CelsiusToFahrenheit` function (the reverse of the example)

### Key Takeaways

✓ `using` makes a function — it must `deliver` a value
✓ `with` makes a procedure — it performs actions without returning
✓ Function results can be stored, displayed, or used in conditions
✓ Functions can call other functions

---

## Lesson 11: Project: Gradebook ⭐

### Concept: Putting It All Together!

This is your first **complete project** — a student gradebook that combines everything from Lessons 1–10: variables, lists, loops, decisions, tasks, and functions. Take a deep breath — you've learned enough to build something real!

### Example: `lesson_11_project_gradebook.plain`

See `examples/tutorial/lesson_11_project_gradebook.plain` for the complete program (~84 lines).

Here's the core structure:

```plain
task Main()
    rem: Student data (parallel lists)
    var names = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
    var scores1 = [95, 87, 92, 88]
    var scores2 = [78, 82, 74, 80]
    rem: ... more scores ...
    var allScores = [scores1, scores2, scores3, scores4, scores5]

    rem: Display all student reports
    loop i from 0 to len(names) - 1
        DisplayStudentReport(names[i], allScores[i])

    DisplayClassSummary(names, allScores)

rem: Calculate average of a list of scores
task CalculateAverage using (scores)
    var total = 0.0
    loop score in scores
        total = total + score
    deliver total / len(scores)

rem: Determine letter grade
task GetGrade using (average)
    if average >= 90
        deliver "A"
    else
        if average >= 80
            deliver "B"
        rem: ... more grades ...
```

### Sample Output

```
=================================
     Student Gradebook v1.0
=================================

Student: Alice
  Scores: [95, 87, 92, 88]
  Average: 90.5
  Grade: A

Student: Bob
  Scores: [78, 82, 74, 80]
  Average: 78.5
  Grade: C
...
=================================
       Class Summary
=================================
  Class Average: 83.85
  Top Student: Charlie (93)
  Total Students: 5
=================================
```

### What's Happening?

- **Lists of lists** — `allScores` contains each student's score list
- **Functions** (`CalculateAverage`, `GetGrade`) compute values with `using`/`deliver`
- **Procedures** (`DisplayStudentReport`, `DisplayClassSummary`) format and display output with `with`
- **Loops** iterate through students and scores
- **Decisions** determine letter grades

### Try It

1. Add a sixth student with their own scores
2. Add a "Highest Score" and "Lowest Score" to each student report
3. Add a `CountGrade` function that counts how many students got each letter grade

### Key Takeaways

✓ Real programs combine many concepts working together
✓ Break complex problems into small, focused tasks
✓ Functions (`using`) compute values; procedures (`with`) perform actions
✓ Lists of lists can represent structured data like a spreadsheet

---

## Lesson 12: String Operations

### Concept: Powerful Text Processing

PLAIN has a rich set of built-in string functions for searching, transforming, and breaking apart text. Mastering strings is essential for real-world programming.

### Example: `lesson_12_strings.plain`

See `examples/tutorial/lesson_12_strings.plain` for the complete program.

Key operations demonstrated:

```plain
rem: Case conversion
var name = "alice smith"
display("Upper: " & upper(name))        rem: ALICE SMITH
display("Lower: " & lower("HELLO"))     rem: hello

rem: Searching
var sentence = "The quick brown fox"
display(contains(sentence, "fox"))       rem: true
display(starts_with(sentence, "The"))    rem: true

rem: Splitting and joining
var words = split(sentence, " ")         rem: ["The", "quick", "brown", "fox"]
var joined = join(words, ", ")           rem: "The, quick, brown, fox"

rem: Replacing
var updated = replace(sentence, "quick", "slow")
```

### String Function Reference

| Function | Description | Example |
|----------|-------------|---------|
| `upper(s)` | Uppercase | `upper("hi")` → `"HI"` |
| `lower(s)` | Lowercase | `lower("HI")` → `"hi"` |
| `trim(s)` | Remove whitespace | `trim("  hi  ")` → `"hi"` |
| `len(s)` | String length | `len("hello")` → `5` |
| `contains(s, sub)` | Check substring | `contains("hello", "ell")` → `true` |
| `starts_with(s, pre)` | Check prefix | `starts_with("hello", "he")` → `true` |
| `ends_with(s, suf)` | Check suffix | `ends_with("hello", "lo")` → `true` |
| `substring(s, start, end)` | Extract portion | `substring("hello", 0, 3)` → `"hel"` |
| `replace(s, old, new)` | Replace text | `replace("hi all", "hi", "hey")` → `"hey all"` |
| `split(s, delim)` | Split to list | `split("a,b,c", ",")` → `["a","b","c"]` |
| `join(list, delim)` | Join to string | `join(["a","b"], "-")` → `"a-b"` |

### Try It

1. Write a program that asks for a sentence and displays it in uppercase, lowercase, and reversed
2. Split a comma-separated string like `"apple,banana,cherry"` and display each fruit on its own line
3. Build a simple "title case" converter (capitalize the first letter of each word)

### Key Takeaways

✓ `split()` and `join()` convert between strings and lists
✓ `contains()`, `starts_with()`, `ends_with()` search without modifying
✓ `replace()` creates a new string — it doesn't modify the original
✓ `substring(s, start, end)` extracts a portion of text

---

## Lesson 13: Error Handling

### Concept: Gracefully Handling Problems

Sometimes things go wrong — division by zero, invalid input, missing files. PLAIN uses `attempt/handle/ensure` to catch errors and keep your program running smoothly. The `abort` keyword lets you signal your own errors.

### Example: `lesson_13_error_handling.plain`

See `examples/tutorial/lesson_13_error_handling.plain` for the complete program.

Key patterns:

```plain
rem: Catching errors with attempt/handle
attempt
    var result = 10 / 0
    display("This won't print")
handle
    display("Caught a division error!")

rem: Using abort to signal errors
task ValidateAge using (age)
    if age < 0
        abort "Age cannot be negative"
    deliver age

rem: Ensure block always runs (cleanup)
attempt
    display("Working...")
    abort "Something went wrong"
handle
    display("Error was caught!")
ensure
    display("Cleanup complete (always runs).")
```

### What's Happening?

- `attempt` — Try running this code; if an error occurs, jump to `handle`
- `handle` — Code that runs when an error is caught
- `ensure` — Code that **always** runs, whether an error occurred or not (great for cleanup)
- `abort "message"` — Signal an error with a custom message

### Try It

1. Write a "safe calculator" that catches division by zero errors
2. Write a validation function that aborts if a string is empty
3. Use `ensure` to always display "Program complete!" at the end of a risky operation

### Key Takeaways

✓ `attempt/handle` catches errors so your program doesn't crash
✓ `ensure` runs cleanup code regardless of whether an error occurred
✓ `abort "message"` signals a custom error
✓ Error handling makes programs robust and user-friendly

---

## Lesson 14: Records and Custom Types

### Concept: Defining Your Own Data Structures

When you need to group related data together — like a student's name, age, and grade — **records** let you define your own custom types with named fields.

### Example: `lesson_14_records.plain`

See `examples/tutorial/lesson_14_records.plain` for the complete program.

Key concepts:

```plain
rem: Define a record type
record Student:
    name as string
    age as integer = 18
    grade as string = "A"

task Main()
    rem: Create instances with named fields
    var student1 = Student(name: "Alice", age: 20, grade: "A")
    var student2 = Student(name: "Bob", age: 19)
    var student3 = Student(name: "Charlie")

    rem: Access fields with dot notation
    display(student1.name)      rem: Alice
    display(student2.age)       rem: 19
    display(student3.grade)     rem: A (default)

    rem: Modify fields
    student2.grade = "B"
```

### What's Happening?

- `record Student:` — Defines a new data type with named fields
- Fields can have types and **default values**: `age as integer = 18`
- `Student(name: "Alice", age: 20)` — Creates an instance with named arguments
- Omitted fields use their default values
- `student.name` — Access fields with **dot notation**
- Fields can be modified: `student.grade = "B"`
- Records work in lists: `var students = [student1, student2, student3]`

### Try It

1. Define a `Book` record with title, author, year, and pages (with defaults)
2. Create a list of 3 books and loop through them to display each one
3. Define a `Rectangle` record with width and height, and write an `Area` function for it

### Key Takeaways

✓ `record Name:` defines a custom data type
✓ Fields have types and optional default values
✓ Create instances with named arguments: `Name(field: value)`
✓ Access fields with dot notation: `instance.field`

---

## Lesson 15: Working with Files

### Concept: Reading and Writing Data on Disk

Programs often need to save data and load it later. PLAIN provides simple functions for reading and writing text files, plus tools for checking files and managing directories.

### Example: `lesson_15_files.plain`

See `examples/tutorial/lesson_15_files.plain` for the complete program.

Key operations:

```plain
rem: Write lines to a file
var lines = ["Hello from PLAIN!", "This is line 2.", "This is line 3."]
write_lines("/tmp/plain_demo.txt", lines)

rem: Read the whole file as a string
var content = read_file("/tmp/plain_demo.txt")

rem: Read as a list of lines
var readLines = read_lines("/tmp/plain_demo.txt")
loop i from 0 to len(readLines) - 1
    var line = readLines[i]
    display("  Line " & (i + 1) & ": " & line)

rem: Append to an existing file
append_file("/tmp/plain_demo.txt", "New line!")

rem: Check if file exists, get size
var exists = file_exists("/tmp/plain_demo.txt")
var size = file_size("/tmp/plain_demo.txt")
```

### File Function Reference

| Function | Description |
|----------|-------------|
| `write_file(path, text)` | Write text to a file (creates/overwrites) |
| `read_file(path)` | Read entire file as a string |
| `write_lines(path, list)` | Write a list of strings as lines |
| `read_lines(path)` | Read file into a list of lines |
| `append_file(path, text)` | Append text to an existing file |
| `file_exists(path)` | Check if a file exists (true/false) |
| `file_size(path)` | Get file size in bytes |
| `delete_file(path)` | Delete a file |
| `create_dir(path)` | Create a directory |
| `dir_exists(path)` | Check if a directory exists |
| `join_path(a, b)` | Join path components |
| `get_extension(path)` | Get file extension (e.g., ".txt") |

### Try It

1. Write a program that saves your name and age to a file, then reads and displays them
2. Create a simple "note-taking" program that appends notes to a file
3. Write a program that lists all files in a directory

### Key Takeaways

✓ `write_file()` / `read_file()` work with whole file contents
✓ `write_lines()` / `read_lines()` work with lists of lines
✓ Always check `file_exists()` before reading to avoid errors
✓ `append_file()` adds to a file without erasing it

---

## Lesson 16: Randomness and Games

### Concept: Adding Unpredictability

Random numbers make programs fun — from dice games to password generators. PLAIN has three random functions that cover most use cases.

### Example: `lesson_16_random_games.plain`

See `examples/tutorial/lesson_16_random_games.plain` for the complete program.

Key patterns:

```plain
rem: Random float between 0.0 and 1.0
display("Random: " & random())

rem: Random integer in a range (inclusive)
var diceRoll = random_int(1, 6)

rem: Random choice from a list
var colors = ["red", "blue", "green", "yellow"]
display("Color: " & random_choice(colors))

rem: Dice rolling with accumulation
var total = 0
loop i from 1 to 5
    var roll = random_int(1, 6)
    total = total + roll

rem: Random password generator
var chars = ["a","b","c","d","2","3","4","5"]
var password = ""
loop i from 1 to 8
    password = password & random_choice(chars)
```

### Random Function Reference

| Function | Description | Example |
|----------|-------------|---------|
| `random()` | Float from 0.0 to 1.0 | `0.7382...` |
| `random_int(min, max)` | Integer in range (inclusive) | `random_int(1, 6)` → `4` |
| `random_choice(list)` | Pick a random item from a list | `random_choice(colors)` → `"blue"` |

### Try It

1. Build a "Magic 8-Ball" — create a list of responses and pick one randomly
2. Simulate rolling two dice 100 times and count how many times you get doubles
3. Write a program that generates a random quiz question from a list

### Key Takeaways

✓ `random()` gives a float, `random_int()` gives an integer in a range
✓ `random_choice()` picks from a list — great for games
✓ Combine randomness with loops for simulations
✓ Results change every time the program runs!

---

## Lesson 17: Modules and Organization

### Concept: Organizing Large Programs

As your programs grow, you'll want to split code across multiple files. PLAIN uses a three-tier system: **packages** (your project), **assemblies** (directories), and **modules** (individual `.plain` files).

### Example: `lesson_17_modules.plain`

See `examples/tutorial/lesson_17_modules.plain` for the complete program.

### Project Structure

```
my_project/
  main.plain              (entry point)
  utils.plain             (utility module)
  math/
    geometry.plain         (math.geometry module)
    statistics.plain       (math.statistics module)
  io/
    files.plain            (io.files module)
    network.plain          (io.network module)
```

### Import Syntax

```plain
use:
    assemblies:
        io                           rem: Import entire assembly
    modules:
        math.geometry                rem: Import specific module
    tasks:
        math.statistics.Average      rem: Import specific task
```

### Three Import Levels

| Level | Syntax | Access Pattern |
|-------|--------|----------------|
| **Assembly** | `assemblies: io` | `io.files.ReadText()` |
| **Module** | `modules: math.geometry` | `geometry.CircleArea()` |
| **Task** | `tasks: math.geometry.CircleArea` | `CircleArea()` |

### Try It

1. Think about a program you'd like to build — how would you organize it into modules?
2. Create a `math_helpers.plain` file with utility functions, and a `main.plain` that uses them
3. Draw a diagram of your project's module structure

### Key Takeaways

✓ Large programs should be split across multiple files
✓ `use:` imports assemblies, modules, or individual tasks
✓ More specific imports = shorter names when calling
✓ Group related tasks into modules and modules into assemblies

---

## Lesson 18: Events and Timers

### Concept: Working with Time

Sometimes your program needs to wait, pause, or schedule things for later. PLAIN provides `sleep()` for pausing, and timers for scheduling callbacks.

### Example: `lesson_18_timers.plain`

See `examples/tutorial/lesson_18_timers.plain` for the complete program.

Key patterns:

```plain
rem: Pause execution for 500 milliseconds
sleep(500)

rem: Create a one-shot timeout
task OnTimeout()
    display("Timeout fired!")

var timeout = create_timeout(1000, OnTimeout)
start_timer(timeout)
wait_for_events()
```

### What's Happening?

- `sleep(ms)` — Pauses the program for the given number of milliseconds
- `create_timeout(ms, task)` — Creates a one-shot timer that calls a task after a delay
- `start_timer(timer)` — Starts a timer that was created
- `wait_for_events()` — Waits for all pending timeouts to complete

### Timer Function Reference

| Function | Description |
|----------|-------------|
| `sleep(ms)` | Pause execution for N milliseconds |
| `create_timer(ms, task)` | Create a repeating timer |
| `create_timeout(ms, task)` | Create a one-shot timer |
| `start_timer(timer)` | Start a timer |
| `stop_timer(timer)` | Stop a running timer |
| `wait_for_events()` | Wait for all events to complete |
| `run_events(ms)` | Run the event loop for N milliseconds |

### Try It

1. Write a countdown timer that displays "3... 2... 1... Go!" with pauses between
2. Create a "stopwatch" that displays a message every second for 5 seconds
3. Use `create_timeout` to schedule a "reminder" message after 3 seconds

### Key Takeaways

✓ `sleep()` is the simplest way to add delays
✓ `create_timeout()` schedules a one-shot event
✓ `create_timer()` schedules repeating events
✓ `wait_for_events()` keeps the program alive until events finish

---

## What's Next? 🚀

Congratulations — you've completed the PLAIN tutorial! You now know how to:

- Write programs with variables, input, and output
- Make decisions with `if/else` and `choose`
- Repeat actions with loops
- Organize code with tasks, parameters, and functions
- Work with lists, tables, strings, records, and files
- Handle errors gracefully
- Use randomness, modules, and timers

### Keep Learning

- **[USER-GUIDE.md](USER-GUIDE.md)** — Detailed reference for all PLAIN features
- **[LANGUAGE-REFERENCE.md](LANGUAGE-REFERENCE.md)** — Complete language specification
- **[STDLIB.md](STDLIB.md)** — Every built-in function documented

### Ideas for Projects

Here are some projects to practice your skills:

1. **To-Do List Manager** — Add, remove, and display tasks (use lists and files)
2. **Number Guessing Game** — The computer picks a number, the player guesses (use random and loops)
3. **Contact Book** — Store contacts in a table, save/load from a file
4. **Quiz Game** — Multiple choice questions with scoring (use lists, records, and random)
5. **Text Adventure** — A simple story game with choices (use tasks and choose)
6. **Grade Calculator** — Extend the gradebook with weighted grades and more features

Happy coding! 🎉
