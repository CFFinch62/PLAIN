# Tier 2 Assessment

Two checkpoints plus the capstone rubric.

---

## Checkpoint 1 — Strict Rules and Error Handling (after Lesson 2)

1. What error, if any, does this produce?
   ```plain
   task Main()
       var x = 5
       loop i from 1 to 2
           var x = i
   ```
2. Why doesn't PLAIN let the inner `x` just "win," the way many languages
   do?
3. What error, if any, does this produce?
   ```plain
   task AddOne with (n)
       n = n + 1
       display(n)
   ```
4. What does `ensure` guarantee that `handle` does not?
5. Why is a `handle` block required to actually resolve a problem instead
   of just catching and ignoring it?

**Answer key**: 1. `Variable 'x' already declared in outer scope...` —
PLAIN never allows shadowing, even in a loop  2. Because a shadowed
variable is a classic source of "which one did I just change" bugs;
PLAIN removes the possibility entirely rather than trusting the
programmer to keep track  3. An error — task parameters are immutable in
PLAIN; `n` cannot be reassigned  4. `ensure` always runs, whether or not
an error occurred, unlike `handle`, which only runs on failure  5.
Because silently swallowing an error without resolving it (a safe
fallback, a clearer `abort`, or logging) hides real problems instead of
handling them — PLAIN treats that as an anti-pattern worth blocking
outright.

---

## Checkpoint 2 — Modules (after Lesson 3)

1. Given this import:
   ```plain
   use:
       modules:
           math.geometry
   ```
   how would you call a task named `CircleArea` defined in that module?
2. Given this import instead:
   ```plain
   use:
       tasks:
           math.geometry.CircleArea
   ```
   how would you call it now?
3. What's the difference between importing an assembly and importing a
   module?
4. Compare PLAIN's module system to STEPS' floors: what does PLAIN's
   system enforce that STEPS' floors only suggested by convention?

**Answer key**: 1. `geometry.CircleArea()` — the module name prefixes the
call  2. `CircleArea()` — importing the specific task drops the need for
any prefix  3. An assembly is a whole directory of modules (`io` might
contain `io.files`, `io.network`, etc.); a module is a single file's
worth of tasks  4. PLAIN's `use:` block enforces exactly what's visible
in a given file — nothing is accessible unless explicitly imported;
STEPS' floors organize files into folders but don't control visibility
the same way — any step can be called from anywhere once it's known to
the building.

---

## Capstone Rubric

Score each category 0-3.

| Category | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| **Correctness** | Doesn't run, or a core feature is missing | Runs but a core feature is broken in common cases | Works correctly for the project's core requirements | Also handles at least one edge case cleanly via `attempt`/`handle` |
| **Structure & records** | Everything in one file, no records used | Split across files, but the split is arbitrary; or a record exists but is used superficially | A sensible module split with a clear reason for each file; at least one record used meaningfully | Also uses a record containing another record or a list of records where it genuinely fits |
| **Error handling** | No `attempt`/`handle` used anywhere risky | At least one `attempt`/`handle` block exists, in a plausible place | Used where user input or a calculation could realistically fail, and the `handle` block actually resolves the problem | Also uses `ensure` correctly for guaranteed cleanup |
| **Explanation** | Can't describe what their own code does | Can describe what it does but not why it's organized that way | Can explain each module's purpose and what their `handle` block resolves, not just what it catches | Can also justify the specific import level (assembly/module/task) chosen for each import |

A student scoring 2+ across all four categories has met the tier's goal
and is ready to move to FORGE.
