# Learn to Program with PLAIN — Bridging from STEPS

PLAIN already has a full, excellent course of its own:
[docs/LEARNING/CURRICULUM.md](../docs/LEARNING/CURRICULUM.md) (a 12-week
plan with assignments and rubrics) and
[docs/LEARNING/TUTORIAL.md](../docs/LEARNING/TUTORIAL.md) (22 hands-on
lessons with runnable code). Neither was written with STEPS or BARE in
mind — they were written for PLAIN as a standalone entry point. This
folder doesn't replace them; it's the short **bridge** a student who
already knows STEPS needs before dropping into that existing material:
what's actually new, what's a relief, what's a trap, and where to start.

**Start here if you're a teacher**: read
[teachers-guide.md](teachers-guide.md) for the "why" and the pacing notes,
then use the two tier folders below for actual lesson plans. Both tiers
assume PLAIN's existing tutorial/reference docs are available alongside
them for hands-on practice and depth — see "How this relates to the rest
of the PLAIN project" below.

## Why PLAIN comes after STEPS

STEPS forced discipline a student didn't get to choose: every function is
its own file, forced into a floor, forced into a building. PLAIN keeps
everything that discipline was *for* — clear names, declared inputs and
outputs, organized multi-file projects — but hands the choice back. A
`task` can live wherever makes sense; a whole small program can be one
file. That's not a step backward; it's the payoff for having done it the
hard way first. Read PLAIN's own mission statement, which the language
takes seriously: *"clear thinking over clever syntax, natural readability
over terse notation, and honest capability over complex features."*

PLAIN also brings real capability increases that matter for what students
can *build*: records (structured data, a first taste of what other
languages call objects, without the inheritance machinery), a genuine
module/import system for multi-file projects, and a standard library large
enough to write something real — network I/O, serial ports, timers, a text
UI toolkit. PLAIN ships with a real product built in it (a marine
electronics dashboard reading live NMEA-0183 data), which is worth showing
students directly: this is not a toy language pretending to be a real one.

## The two tiers

| Tier | Comes after | Folder | New big idea |
|---|---|---|---|
| **1 — PLAIN New Shapes** | STEPS Tier 2 | [tier1-new-shapes/](tier1-new-shapes/) | `with`/`using` tasks, `choose`/`choice`, precise counting loops, records — familiar ideas from STEPS given a stricter, more compact shape, plus one file replacing STEPS' one-function-per-file rule |
| **2 — PLAIN Systems** | Tier 1 | [tier2-systems/](tier2-systems/) | No shadowing, immutable parameters, `attempt`/`handle`/`ensure`, and a real Package/Assembly/Module import system |

Each tier folder has `lessons.md`, `worksheets.md`, and `assessment.md`,
matching BARE's format — kept intentionally short, since PLAIN's own
existing [docs/LEARNING/TUTORIAL.md](../docs/LEARNING/TUTORIAL.md) (22
lessons) and [docs/LEARNING/CURRICULUM.md](../docs/LEARNING/CURRICULUM.md)
(12-week course) already provide deep, hands-on practice for every
concept — use them alongside these tiers for extra worked examples and
homework, the same way BARE's curriculum leans on its own `docs/` and
`examples/`.

## How this relates to the rest of the PLAIN project

- [docs/LEARNING/TUTORIAL.md](../docs/LEARNING/TUTORIAL.md)'s 22 lessons
  are the hands-on material matching the 12-week plan — use them directly.
- [docs/REFERENCE/LANGUAGE-REFERENCE.md](../docs/REFERENCE/LANGUAGE-REFERENCE.md)
  and [docs/REFERENCE/STDLIB.md](../docs/REFERENCE/STDLIB.md) are the
  spec and standard library reference.
- [examples/plain_instruments/](../examples/plain_instruments/) (the
  marine dashboard) and [examples/plain_euler/](../examples/plain_euler/)
  (Project Euler solutions with a shared library) are strong capstone and
  extension material.
- The PLAIN IDE has **nested scope-block coloring** (View menu or
  Preferences → Editor), a visual debugger, and a built-in
  **Python ↔ PLAIN converter** (`Tools → Convert File`) — worth
  demonstrating once students later meet Python, as a concrete "same
  logic, different clothes" comparison.
