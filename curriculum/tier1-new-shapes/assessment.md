# Tier 1 Assessment

Two checkpoints — no capstone here; that lands in Tier 2 alongside modules.

---

## Checkpoint 1 — Tasks and Branching (after Lesson 2)

1. What's the difference between a task defined with `with` and one
   defined with `using`?
2. What will this print?
   ```plain
   task Square using (n)
       deliver n * n

   task Main()
       display(Square(4))
   ```
3. What happens if you try to reassign a parameter inside a task?
4. Rewrite this as a `choose` block:
   ```
   if size is equal to "S"
       display "Small"
   otherwise if size is equal to "M"
       display "Medium"
   otherwise
       display "Large"
   ```

**Answer key**: 1. `with` defines a procedure (performs an action, no
return value); `using` defines a function that must `deliver` a value
back to the caller  2. `16`  3. It's an error — task parameters are
immutable in PLAIN; you must copy the value to a local `var` first if you
need to change it  4.
```plain
choose size
    choice "S"
        display("Small")
    choice "M"
        display("Medium")
    default
        display("Large")
```

---

## Checkpoint 2 — Loops and Records (after Lesson 4)

1. What will this print?
   ```plain
   loop i from 10 to 2 step -2
       display(i)
   ```
2. Why should you write `total = total + x` instead of `total += x` inside
   a loop in PLAIN?
3. Given
   ```plain
   record Car:
       make as string
       year as integer = 2020
   ```
   what will `Car(make: "Toyota").year` be?
4. What's the key difference between a STEPS table and a PLAIN record?
5. What happens if you try to create a `Car` without providing `make`?

**Answer key**: 1. `10`, `8`, `6`, `4`, `2` (one per line)  2. PLAIN's
compound-assignment operators (`+=` etc.) don't reliably accumulate a
running total inside a loop body — a known sharp edge, not a style
preference  3. `2020` (the default value)  4. A record's shape — which
fields exist and their types — is declared once, up front, and checked;
a table's keys are just whatever you happen to put in it, with no
declared shape to catch a typo  5. An error — `make` has no default
value, so it's a required field.
