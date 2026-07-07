# Tier 1 Student Worksheets

---

## Worksheet 1 — `with` and `using`

1. Type and run:
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
2. Write a `with` task called `Greet` that takes a name and displays a
   greeting (no return value).
3. Write a `using` task called `IsEven` that takes a number and delivers
   `true` or `false`.
4. **Predict, then run**: what happens if you try to reassign a parameter
   inside a task, like this?
   ```plain
   task Double with (n)
       n = n * 2
       display(n)
   ```

---

## Worksheet 2 — `choose`/`choice`/`default`

1. Type and run:
   ```plain
   choose grade
       choice "A"
           display("Excellent!")
       choice "B"
           display("Good job!")
       default
           display("Needs improvement")
   ```
   Try it with `grade` set to `"A"`, `"B"`, and `"F"`.
2. Convert this STEPS-style chain into a PLAIN `choose` block:
   ```
   if day is equal to "Sat"
       display "Weekend!"
   otherwise if day is equal to "Sun"
       display "Weekend!"
   otherwise
       display "Weekday"
   ```
3. Write a `choose` block for a traffic light color (`"red"`, `"yellow"`,
   `"green"`) that displays what to do at each.

---

## Worksheet 3 — Counting Precisely

1. Type and run:
   ```plain
   loop i from 1 to 10 step 2
       display(i)

   loop i from 10 to 1 step -1
       display(i)
   display("Liftoff!")
   ```
2. Write a loop that prints every third number from 3 to 30.
3. Write a nested loop that prints a multiplication table for 1 through 5
   (a loop inside a loop, both using `from`/`to`).
4. **Predict, then run**: what's wrong with this accumulator, and how
   would you fix it?
   ```plain
   var total = 0
   loop i from 1 to 10
       total += i
   display(total)
   ```

---

## Worksheet 4 — Records

1. Type and run:
   ```plain
   record Book:
       title as string
       author as string
       year as integer = 2020

   task Main()
       var b1 = Book(title: "Dune", author: "Herbert", year: 1965)
       var b2 = Book(title: "Foundation", author: "Asimov")

       display(b1.title)
       display(b2.year)
   ```
2. Define your own `Pet` record (name, species, age with a default of 1).
   Create two instances and display all their fields.
3. **Predict, then run**: what happens if you try to create a `Book`
   without providing a `title`?
