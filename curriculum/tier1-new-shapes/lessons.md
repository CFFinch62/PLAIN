# Tier 1 — PLAIN New Shapes

Four lessons. This tier assumes a STEPS graduate: steps, floors, risers,
`otherwise if`, the three loop forms, and tables should already be solid.
None of that is re-taught — every lesson here covers a genuinely new
PLAIN idea, or an old idea given a stricter, more precise shape. The
biggest adjustment isn't a new keyword at all: it's the *relief* of PLAIN
not forcing one function per file the way STEPS did. Name that explicitly
in Lesson 1 — it should land as a reward, not a shrug.

---

## Lesson 1 — One File, Your Choice: Tasks with `with` and `using`

**Objective**: Define and call PLAIN `task`s, using `with` for a procedure
and `using` (with `deliver`) for a function, in a single shared file.

**Vocabulary**: task, procedure, function, `deliver`.

**Teach**: Open by naming the relief directly: *"STEPS made you put every
step in its own file, in a floor, in a building, whether you wanted to or
not. PLAIN keeps the habit STEPS was training — declare clearly what a
piece of code needs and gives back — but gives you the file back."*

```plain
task Main()
    SayHello()
    var total = Add(5, 3)
    display(v"5 + 3 = {total}")

task SayHello()
    display("Hello there!")

task Add using (a, b)
    deliver a + b
```

All three tasks live in one file — that's normal in PLAIN, not a shortcut.
Point out the header does the same job STEPS' `expects`/`returns` did, in
a more compact form: `with (params)` marks a **procedure** (does
something, no return — like `SayHello`), `using (params)` marks a
**function** that must `deliver` a value (like `Add`). The keyword in the
header tells you which kind of thing you're looking at before you read a
single line of the body — same idea as STEPS, tighter syntax. Also flag:
**parameters are immutable** — `a` and `b` inside `Add` can be read but
never reassigned; copy to a local `var` first if you need to change a
value.

**Guided practice**: As a class, take a STEPS step-with-parameters example
from memory and rewrite it as a PLAIN `task ... using (...)`.

**Independent practice**: Worksheet 1.

**Wrap-up**: Exit ticket — how do you tell, just from a task's header,
whether it's a procedure or a function?

**Differentiation**: *Extension* — a function that calls another function
inside its own `deliver` expression. *Support* — one `with` task and one
`using` task, each called once, is a complete goal.

---

## Lesson 2 — `choose`/`choice`/`default`: A Third Way to Branch

**Objective**: Use `choose`/`choice`/`default` for a multi-way decision,
and explain why PLAIN drops `elseif`-style chaining again.

**Teach**: Revisit the running theme: BARE had no `elseif` at all; STEPS
answered with `otherwise if`; PLAIN answers a third way:

```plain
choose grade
    choice "A"
        display("Excellent!")
    choice "B"
        display("Good job!")
    choice "C"
        display("Satisfactory")
    default
        display("Needs improvement")
```

Put PLAIN's own reasoning to students directly: `if` is for **binary**
decisions only — there's no `elif`/`otherwise if` in PLAIN. A `choose`
block is a genuinely different construct from a chain of `if`s: it reads
as *one* decision with several possible outcomes, not several separate
decisions that happen to be related. Ask: *"You just learned STEPS'
`otherwise if` last tier. Why would a language designer take that back
out and replace it with something else, instead of just keeping it?"*
There's no single right answer — the point is the discussion. (A fair
answer: a `choose` block can't accidentally fall through to the wrong
branch the way a long `otherwise if` chain can if a condition is written
wrong; it also documents that all the branches are testing the *same*
value.)

**Guided practice**: As a class, convert a STEPS-style `otherwise if`
chain (based on comparing one variable to several fixed values, like a
grade or a day of the week) into `choose`/`choice`/`default`.

**Independent practice**: Worksheet 2.

**Wrap-up**: Exit ticket — when would `if`/`else` still be the right
choice over `choose`, even in PLAIN?

**Differentiation**: *Extension* — a `choose` with 5+ choices plus
`default`. *Support* — a 3-choice `choose` block, converted directly from
a provided `otherwise if` chain, is a complete goal.

---

## Lesson 3 — Counting Precisely: `loop from`/`to`/`step`

**Objective**: Use `loop i from X to Y step Z` to control exactly how a
counting loop increments, including counting backward.

**Teach**:

```plain
loop i from 1 to 5
    display(v"Count: {i}")

loop i from 2 to 10 step 2
    display(i)

loop i from 5 to 1 step -1
    display(i & "...")
display("Liftoff!")

loop fruit in fruits
    display("I like " & fruit & "!")
```

STEPS' `repeat N times` counts a fixed number of times but never exposes
the count itself in a controllable way, and its `repeat for each` only
goes forward, item by item. PLAIN's `loop ... from ... to ... step ...`
makes the increment a first-class, adjustable number — count by twos,
count backward for a countdown, without reaching for a `while` loop and a
manually-managed counter the way BARE always required. Also show `loop
item in collection` — the direct equivalent of STEPS' `repeat for each`,
just under the same `loop` keyword as every other loop form in PLAIN.
Mention the accumulator gotcha directly: *"When you're adding something up
inside a loop, always write `total = total + x`, never `total += x` —
PLAIN's compound-assignment operators don't reliably accumulate inside a
loop body. This isn't a style preference, it's a real, known sharp edge."*

**Guided practice**: As a class, write a loop that prints every third
number from 3 to 30 using `step 3`, then a second loop that counts down
from 10 to 1.

**Independent practice**: Worksheet 3.

**Wrap-up**: Exit ticket — what does a negative `step` value do, and why
would you want one?

**Differentiation**: *Extension* — nested `loop from/to` loops building a
multiplication table. *Support* — one forward-counting loop with `step 2`
and one countdown loop, run and read, is a complete goal.

---

## Lesson 4 — Records: Grouping Data That Belongs Together

**Objective**: Define a `record`, create instances with named fields, and
access/modify fields with dot notation.

**Vocabulary**: record, field, default value.

**Teach**:

```plain
record Student:
    name as string
    age as integer = 18
    grade as string = "A"

task Main()
    var student1 = Student(name: "Alice", age: 20, grade: "A")
    var student2 = Student(name: "Bob", age: 19)

    display(student1.name)
    display(student2.age)

    student2.grade = "B"
```

Connect this directly back to STEPS tables: `["name": "Alice", "age": 20]`
already grouped related data together, by key. A record is the same
underlying idea, made stricter and more self-documenting — the *shape* of
the data (exactly which fields exist, what type each is, whether it has a
default) is declared once, up front, instead of being whatever happens to
be in a particular table at runtime. Ask: *"If you misspell a key in a
STEPS table, what happens? If you misspell a field name on a PLAIN
record, what happens?"* (A STEPS table with a typo'd key just silently has
a different key — no error until you look up the wrong one; a record
field typo is caught because the record type itself defines what fields
exist.) Frame records as the shape of thing that becomes a full class in
Python or Java — this is its data half, with no methods attached yet.

**Guided practice**: As a class, define a `Book` record (title, author,
year, pages with a default), create two instances, and print both.

**Independent practice**: Worksheet 4.

**Wrap-up**: Exit ticket — what happens if you create a `Student` and
leave out a field that has no default value?

**Differentiation**: *Extension* — a record whose field is itself another
record (e.g., a `Course` record containing a `list of Student`).
*Support* — one record with 3 fields (one with a default), two instances
created and printed, is a complete goal.
