# Tier 2 — PLAIN Systems

Four lessons. Tier 1 covered PLAIN's new *shapes* for familiar ideas
(tasks, branching, loops, structured data). Tier 2 covers the ideas that
have no real STEPS equivalent at all: rules stricter than any language so
far in the suite, error handling that refuses to let you cheat, and a real
module system for programs that span multiple files **by choice** rather
than by force.

---

## Lesson 1 — No Shadowing, Immutable Parameters: Stricter Rules, Clearer Code

**Objective**: Explain and avoid PLAIN's two strictest rules — no variable
shadowing, ever, and read-only task parameters.

**Teach**: Recall BARE's strictest rule (a `sub` can't see outside
variables, no exceptions) and STEPS' parallel (a riser is invisible
outside its step). PLAIN adds two rules in that same spirit, and they're
stricter than most languages a student will meet after this suite:

```plain
task Main()
    var count = 0
    loop i from 1 to 3
        var count = i * 2    rem: ERROR: 'count' already declared in outer scope
        display(count)
```

Run it and read the error together:
`Variable 'count' already declared in outer scope at line X`. PLAIN
**never** allows a name to be redeclared in a nested scope, even
temporarily, even if you meant to. Ask: *"Why would a language designer
consider this worth banning outright, instead of just letting the inner
one 'win' the way most languages do?"* — the answer is exactly the kind
of bug it prevents: two variables with the same name at different levels
is a classic source of "which one did I just change?" confusion, and
PLAIN simply removes the possibility.

The second rule:

```plain
task Double with (n)
    n = n * 2        rem: ERROR: parameters are immutable
    display(n)
```

A parameter can be read but never reassigned — copy it to a local `var`
first if you need to change it. Connect this to value semantics: the
caller's original value is never at risk of being silently changed by a
task it calls.

**Guided practice**: As a class, take a broken example of each kind (a
shadowed variable, a reassigned parameter) and fix both properly.

**Independent practice**: Worksheet 1.

**Wrap-up**: Exit ticket — name one bug each of these two rules makes
impossible.

**Differentiation**: *Extension* — find and fix a shadowing bug hidden
three loops deep in a provided broken program. *Support* — the two
canonical broken examples above, read, run, and fixed by hand, is a
complete goal.

---

## Lesson 2 — Handling Errors for Real: `attempt`/`handle`/`ensure`

**Objective**: Use `attempt`/`handle`/`ensure` to catch and *resolve* an
error, and explain why PLAIN won't let a `handle` block just pass the
problem along.

**Teach**: Connect directly to STEPS' `attempt`/`if unsuccessful`/`then
continue` — same three-part shape, sturdier names:

```plain
attempt
    var result = 10 / 0
    display("This won't print")
handle
    display("Caught a division error!")
ensure
    display("Cleanup complete (always runs).")
```

`attempt` wraps risky code; `handle` runs if it failed; `ensure` always
runs, error or not — for cleanup. New in PLAIN: `abort "message"` lets a
task raise its own error on purpose —

```plain
task ValidateAge using (age)
    if age < 0
        abort "Age cannot be negative"
    deliver age
```

— and PLAIN adds one hard rule STEPS didn't have: **a `handle` block is
not allowed to simply pass the error along unresolved.** It has to
actually do something — log it, fall back to a safe default, or `abort`
with a clearer message of its own. Ask students to imagine a `handle`
block that does nothing (or worse, silently ignores the problem) and
discuss why that's worse than not catching the error at all. This is the
same instinct behind FORGE's later rule that a failing result *must* be
checked before use — PLAIN gets there first, softer.

**Guided practice**: As a class, write a "safe divide" task that catches a
division-by-zero and `deliver`s a sensible fallback instead of crashing.

**Independent practice**: Worksheet 2.

**Wrap-up**: Exit ticket — what's wrong with a `handle` block that just
displays "an error happened" and does nothing else?

**Differentiation**: *Extension* — a task using `ensure` to guarantee a
"connection closed" message prints whether or not the risky code inside
`attempt` succeeded. *Support* — the safe-divide task above, triggered
with a 0 on purpose, is a complete goal.

---

## Lesson 3 — Modules: Package → Assembly → Module

**Objective**: Split a program across multiple files using PLAIN's
three-tier import system, and choose the right import level for a task.

**Vocabulary**: package, assembly, module, `use:`.

**Teach**: Show a real project layout:

```
my_project/
    main.plain
    utils.plain
    math/
        geometry.plain
        statistics.plain
```

And the import syntax:

```plain
use:
    assemblies:
        io                           rem: everything in the io assembly
    modules:
        math.geometry                rem: one file's worth of tasks
    tasks:
        math.statistics.Average      rem: one specific task
```

| Level | Syntax | Access pattern |
|---|---|---|
| Assembly | `assemblies: io` | `io.files.ReadText()` |
| Module | `modules: math.geometry` | `geometry.CircleArea()` |
| Task | `tasks: math.geometry.CircleArea` | `CircleArea()` |

Connect back to STEPS' floors directly: a floor was a folder-and-naming
*convention* enforced structurally but with no real import mechanism — a
step just had to exist in the right place. PLAIN's assemblies/modules are
an actual import system: you choose exactly what's visible in a given
file and under what name, and nothing is visible that isn't explicitly
imported. More specific imports (a single task) mean shorter names at the
call site but more import lines to maintain; a whole assembly import
means less typing up front but longer names everywhere it's used. That
trade-off — precision versus convenience — is worth a real discussion.

**Guided practice**: As a class, sketch a 3-file project (main + two
helper modules) and write the `use:` block main.plain would need.

**Independent practice**: Worksheet 3.

**Wrap-up**: Exit ticket — what's the difference between importing a
whole assembly and importing one task from a module?

**Differentiation**: *Extension* — a 4-file project with one module
importing from another (chained imports). *Support* — a single-import,
2-file project (main.plain importing one task from one helper module) is
a complete goal.

---

## Lesson 4 — Capstone: A Multi-Module PLAIN Project

**Objective**: Design and build a multi-file PLAIN program using tasks
(`with` and `using`), at least one record, `attempt`/`handle`/`ensure`,
and a real module import.

**Teach**: Present capstone options:
- **Gradebook** — a `students.plain` module defining a `Student` record
  and tasks to add/display students, a `main.plain` that imports it and
  handles bad score input with `attempt`/`handle`.
- **Quiz Game** — a `questions.plain` module (a `Question` record, a list
  of them, a scoring function), a `main.plain` that runs the game loop and
  catches invalid answers.
- **A project of the student's own design**, approved by the teacher,
  using at least two files, one record, and one `attempt`/`handle` block.

Require a written plan: what modules, what each module exports, what
record(s) are needed, and where `attempt`/`handle` protects the program
from bad input — before any code.

**Guided practice**: Peer-review plans in pairs — a partner should be able
to say, from the plan alone, which file defines the `Student` (or
equivalent) record and which file uses it.

**Independent practice**: Build the capstone.

**Wrap-up**: Showcase — each student runs their program and explains what
their record represents, what their `handle` block actually resolves
(not just catches), and why they split the code into the files they did.

**Differentiation**: *Extension* — a third module, or a record field that
is itself a list of another record (e.g., a `Course` holding a `list of
Student`). *Support* — the Gradebook option with a provided 2-file
skeleton (module and record already declared, tasks left to fill in) is
the lowest-friction path.
