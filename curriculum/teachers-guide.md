# PLAIN Curriculum — Teacher's Guide

This assumes your students have finished the STEPS curriculum and covers
the bridge into PLAIN's own existing course
([docs/LEARNING/CURRICULUM.md](../docs/LEARNING/CURRICULUM.md)). It does
not replace that course — it tells you how to open it with a class that
already knows how to program, just not in PLAIN's syntax.

## 1. Why PLAIN, and why now

PLAIN's own design philosophy, stated directly in its spec: "readability
first, natural language orientation, minimal mental noise, clear intent,
explicit over implicit." Everything new in PLAIN serves one of those five
ideas, and almost every one of them is a *direct answer* to a question a
STEPS program forces on students. Use this framing with your class:

- STEPS made every function declare `expects`/`returns` and live in its
  own file. PLAIN keeps the declared-inputs-and-outputs habit but names it
  more precisely: `task Name with (...)` for a procedure (no return value)
  versus `task Name using (...)` for a function that must `deliver` a
  result. The header itself now tells you which kind of thing you're
  looking at — you don't have to read the body to find out.
- STEPS's `attempt` / `if unsuccessful` / `then continue` becomes
  `attempt` / `handle` / `ensure` — the same three-part shape, sturdier
  names, and one added rule: a PLAIN `handle` block is **not allowed to
  silently re-throw**. It has to actually resolve the problem. That's a
  deliberate anti-pattern block, not a missing feature.
- STEPS's mandatory one-step-per-file rule is gone. Multiple `task`s can
  live in one file, and imports are your choice, not the language's
  requirement. This is the biggest **relief** students will feel moving
  from STEPS to PLAIN — name it explicitly so it registers as a reward,
  not as "the rules got looser so who cares now."

## 2. What's genuinely new (not just STEPS renamed)

- **Records** — `record Person: name as string / age as integer = 0` —
  structured, named, typed data with default values and composition
  (`based on` keeps required fields, `with` makes them optional). This is
  PLAIN's answer to "I want to group related data together" without
  reaching for full object-oriented classes — there are no methods, no
  inheritance, just data. It's worth explicitly telling students: *"this
  is the shape of thing that becomes a class in Python or Java — you're
  seeing the data half of that idea first, on its own."*
- **`choose` / `choice` / `default`** for 3+ way branching. Note the
  irony worth naming out loud: BARE had no `elseif`, STEPS added
  `otherwise if`, and PLAIN removes multi-way `if`-chaining *again* in
  favor of a dedicated construct. Walk students through why: PLAIN's own
  spec says "`if` is for binary decisions only" — a `choose` block reads
  as one decision with many outcomes, rather than a chain of separate
  binary decisions that happen to be related. This is worth a full
  discussion, the same way BARE's missing `elseif` was — three languages,
  three different answers to the same underlying question.
- **No variable shadowing, ever** — redeclaring a name already in scope,
  even in a nested block, is a hard error with a specific message
  (`Variable 'counter' already declared in outer scope...`). This is
  stricter than most students' next language will be, exactly the same
  posture BARE took with its scope rule — call that continuity out.
- **Parameter immutability** — a task's parameters can't be reassigned;
  students must copy to a local variable first if they want to change a
  value. This is a real, if small, preview of value-vs-reference thinking.
- **A real module system** — Package → Assembly → Module, with explicit
  `use:` / `assemblies:` / `modules:` / `tasks:` declarations and no
  wildcard imports. This is genuinely new territory (STEPS's floors are a
  folder convention; this is an import system with real scoping rules) and
  deserves full time — it's Week 17 in the existing tutorial's numbering.
- **A large standard library** (150+ functions: strings, math, lists,
  tables, files, timers/events, serial and network I/O, a text-UI toolkit)
  — big enough that "what can I build with this" stops being a limiting
  question. The `plain_instruments` example (a live marine-electronics
  dashboard) is worth showing on day one as a "here's the ceiling" moment.

## 3. Pacing the existing 12-week course for a STEPS-experienced class

[tier1-new-shapes/](tier1-new-shapes/) and [tier2-systems/](tier2-systems/)
are this bridge's own lesson plans, worksheets, and checkpoint
assessments — use them as the primary teaching sequence. The table below
maps that same content onto weeks of the language's own existing
[docs/LEARNING/CURRICULUM.md](../docs/LEARNING/CURRICULUM.md), in case you
want to pull additional worked examples or homework from it alongside the
tier lessons. That existing course was written assuming no prior
programming background; your students have it, so compress accordingly:

| Weeks | Existing content | For a STEPS-experienced class |
|---|---|---|
| 1-4 | Variables, types, input, decisions, loops, lists/tables | Move fast — this is STEPS content in new syntax. Spend the saved time on the `choose`/`if` discussion in §2. |
| 5-6 | Tasks, parameters, return values | Slow down here — `with` vs `using` and parameter immutability are genuinely new rules, not renames. |
| 7-9 | Strings, error handling, records | Full time — records and `attempt`/`handle`/`ensure`'s no-rethrow rule are new. |
| 10-12 | Files, randomness, modules, events/timers, serial/network I/O, TUI | Full time, and don't rush the module system — it's the closest thing to "real project structure" students will have seen. |

## 4. Misconceptions and gotchas specific to a STEPS→PLAIN move

| What trips students up | What's actually happening |
|---|---|
| Writing `otherwise if` | PLAIN doesn't have it — reach for `choose`/`choice`/`default` instead. |
| Reassigning a parameter directly | Parameters are immutable in PLAIN; copy to a local `var` first. |
| Redeclaring a loop variable that shadows an outer one | Hard error, not a warning — PLAIN never allows shadowing, anywhere. |
| Writing a `handle` block that just re-raises the problem | Not allowed — PLAIN forces you to actually resolve it (log it, fall back to a default, or `abort` with a new, clearer message). |
| Expecting one step per file, like STEPS | PLAIN has no such rule — multiple `task`s per file is normal and expected. |

## 5. Bridge forward

When this course wraps, tell students plainly what's coming: FORGE asks
them to write down the *type* of every value, every time, and takes away
the safety net of the interpreter always being able to run their code —
FORGE programs can also be **compiled** to a native binary, and students
will get to watch that actually happen. Everything else they already
know — procedures with declared inputs/outputs, records-as-structured-data,
modules — carries forward directly.
