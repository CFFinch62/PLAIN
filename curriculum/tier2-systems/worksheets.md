# Tier 2 Student Worksheets

---

## Worksheet 1 — Shadowing and Immutability

1. **Predict, then run**: what error do you get from this, and on which
   line?
   ```plain
   task Main()
       var count = 0
       loop i from 1 to 3
           var count = i * 2
           display(count)
   ```
   Fix it so it works (hint: you don't need a second `count`).
2. **Predict, then run**: what error do you get from this?
   ```plain
   task Double with (n)
       n = n * 2
       display(n)
   ```
   Fix it by copying `n` to a new local variable before doubling it.
3. In your own words, what bug does each of these two rules prevent?

---

## Worksheet 2 — Error Handling

1. Type and run:
   ```plain
   attempt
       var result = 10 / 0
       display("This won't print")
   handle
       display("Caught a division error!")
   ensure
       display("Cleanup complete (always runs).")
   ```
2. Write a `SafeDivide` function (`using`) that takes two numbers and
   `deliver`s the result, or `0` if the divisor is zero — using
   `attempt`/`handle` internally.
3. Write a task `ValidateAge` that `abort`s with a message if the age
   passed in is negative.
4. Explain in one sentence why a `handle` block that does nothing (just
   catches the error silently) is worse than not catching it at all.

---

## Worksheet 3 — Modules

1. Create a two-file project: `main.plain` and `math_helpers.plain`.
   Put a function `Square using (n)` in `math_helpers.plain`, and import
   just that one task into `main.plain` using the `tasks:` import level.
   Call it from `Main()`.
2. Now import the whole module instead of just the one task (use
   `modules: math_helpers` instead), and update the call site to match.
3. In your own words, what's the trade-off between importing a single
   task versus importing a whole module?

---

## Worksheet 4 — Capstone Plan

Write a short plan (turned in, not typed into the IDE):
1. Which project are you building (Gradebook, Quiz Game, or your own
   idea)?
2. List each file/module you'll create and what each one exports.
3. Define the record(s) you'll need — name each field and its type.
4. Where will you use `attempt`/`handle`, and what specifically does your
   `handle` block do to resolve the problem (not just catch it)?
