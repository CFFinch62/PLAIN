# PLAIN Teaching Curriculum

> **An educator's guide to teaching programming with PLAIN** 🎓

This document provides a complete 12-week course plan for teaching introductory programming using the PLAIN language. It includes weekly schedules, learning objectives, assignments, project rubrics, assessment ideas, and teaching tips.

---

## Table of Contents

1. [Course Overview](#1-course-overview)
2. [12-Week Course Plan](#2-12-week-course-plan)
3. [Learning Objectives by Unit](#3-learning-objectives-by-unit)
4. [Assignment Descriptions](#4-assignment-descriptions)
5. [Project Rubrics](#5-project-rubrics)
6. [Assessment Ideas](#6-assessment-ideas)
7. [Teaching Tips](#7-teaching-tips)
8. [Differentiation](#8-differentiation)
9. [Resources](#9-resources)

---

## 1. Course Overview

### Goals

By the end of this course, students will be able to:

- Write complete programs that solve real problems
- Understand fundamental programming concepts (variables, control flow, functions, data structures)
- Read and debug unfamiliar code
- Design and implement a multi-component project from scratch
- Develop computational thinking skills applicable to any programming language

### Target Audience

This curriculum is designed to be flexible across educational contexts:

| Audience | Typical Setting | Pace Notes |
|----------|----------------|------------|
| **High school** (grades 9–12) | Semester course, daily classes | May need extra time on weeks 1–4; simplify final project |
| **College intro** (CS 101) | Semester course, 2–3 classes/week | Follow as written; extend with bonus challenges |
| **Self-learners** | Self-paced | Skip assessments; focus on projects and exercises |
| **Workshop / bootcamp** | 1–2 week intensive | Compress weeks 1–7 into days; focus on the project |

### Prerequisites

**None.** This course assumes no prior programming experience. Students should be comfortable:
- Typing on a keyboard
- Using a text editor (PLAIN's IDE handles this)
- Thinking logically about step-by-step processes

### Required Software

- **Go** (for building PLAIN from source)
- **PLAIN interpreter** (built from source: `go build -o plain ./cmd/plain/`)
- **PLAIN IDE** (optional but recommended: `python3 plain_ide/main.py`)
- A terminal / command prompt

---

## 2. 12-Week Course Plan

### Week 1 — Getting Started

**Theme:** What is programming? Your first PLAIN programs.

| Component | Details |
|-----------|---------|
| **Topics** | What is programming, how computers execute instructions, installing PLAIN, writing and running programs, using the REPL |
| **Tutorial Lessons** | Lesson 1 (Hello, PLAIN!) |
| **Concepts** | `display()`, `rem:`, program structure, `task Main()` |
| **Classroom Activity** | Live demo: write a program together, run it, modify it, break it on purpose |
| **Assignment** | **Install & Explore** — Install PLAIN, run 3 provided programs, modify each one to produce different output |

**Suggested Lecture Flow:**
1. What is programming? (Analogy: recipe, directions, instructions)
2. Demo: write `display("Hello!")` in the REPL
3. Create a `.plain` file, run it from the command line
4. Explain `task Main()` — every program needs a starting point
5. Introduce `rem:` comments — annotating your code
6. Students write their own "About Me" program with multiple `display()` calls

---

### Week 2 — Data and Variables

**Theme:** Storing and working with information.

| Component | Details |
|-----------|---------|
| **Topics** | Variables (`var`), constants (`fxd`), data types (integer, float, string, boolean), type prefixes, `as` keyword, expressions, operators |
| **Tutorial Lessons** | Lesson 2 (Variables & Types), Lesson 3 (User Input) |
| **Concepts** | `var`, `fxd`, `get()`, `&` concatenation, `v"..."` interpolation, arithmetic operators |
| **Classroom Activity** | "Prediction game" — show code, students predict the output before running |
| **Assignment** | **Calculator** — Build a program that asks the user for two numbers and an operation (+, -, *, /), then displays the result |

---

### Week 3 — Making Decisions

**Theme:** Programs that choose what to do.

| Component | Details |
|-----------|---------|
| **Topics** | `if`/`else`, comparison operators (`==`, `!=`, `<`, `>`, `<=`, `>=`), logical operators (`and`, `or`, `not`), `choose`/`choice`/`default` |
| **Tutorial Lessons** | Lesson 4 (Making Decisions) |
| **Concepts** | Boolean expressions, branching, multi-way selection |
| **Classroom Activity** | "Flow chart to code" — give students a decision flowchart, translate to PLAIN |
| **Assignment** | **Grade Classifier** — Input a numeric score, output the letter grade (A/B/C/D/F) with appropriate messages using `choose` |

---

### Week 4 — Loops and Repetition

**Theme:** Making programs repeat.

| Component | Details |
|-----------|---------|
| **Topics** | Counting loops (`from`/`to`/`step`), collection loops (`in`), `exit`, `continue`, nested loops |
| **Tutorial Lessons** | Lesson 5 (Loops & Repetition) |
| **Concepts** | Four loop variants, loop variable scope, `exit`, `continue` |
| **Classroom Activity** | "Loop tracing" — students trace through loops by hand, tracking variable values each iteration |
| **Assignment** | **Multiplication Table** — Generate a formatted multiplication table (1–10) using nested loops |

---

### Week 5 — Collections

**Theme:** Working with groups of data.

| Component | Details |
|-----------|---------|
| **Topics** | Lists (creation, access, modification), tables (key-value pairs), iterating over collections, list/table operations |
| **Tutorial Lessons** | Lesson 6 (Lists), Lesson 7 (Tables) |
| **Concepts** | `append`, `remove`, `sort`, `min`, `max`, `sum`, `keys`, `values`, `has_key`, `len` |
| **Classroom Activity** | "Data organizer" — students enter data interactively and see it organized in different ways |
| **Assignment** | **Contact List Manager** — Store names and phone numbers in a table, with options to add, look up, remove, and list all contacts |

---

### Week 6 — Tasks (Procedures)

**Theme:** Organizing code into reusable pieces.

| Component | Details |
|-----------|---------|
| **Topics** | Defining tasks, calling tasks, `with` parameters, parameter immutability, code organization |
| **Tutorial Lessons** | Lesson 8 (Creating Tasks), Lesson 9 (Parameters) |
| **Concepts** | `task`, `with`, parameter passing (by value), code reuse, naming conventions |
| **Classroom Activity** | "Refactoring exercise" — give students a long program, have them break it into tasks |
| **Assignment** | **Menu-Driven Program** — Create a program with a main menu that calls different tasks for each option (at least 4 options) |

---

### Week 7 — Functions and Strings

**Theme:** Tasks that compute and return values.

| Component | Details |
|-----------|---------|
| **Topics** | `using` vs `with`, `deliver`, return values, string operations (`upper`, `lower`, `trim`, `split`, `join`, `substring`, `replace`, `contains`) |
| **Tutorial Lessons** | Lesson 10 (Functions), Lesson 12 (String Operations) |
| **Concepts** | Functions vs procedures, using return values, string manipulation |
| **Classroom Activity** | "Function workshop" — each student writes a function, then others call it (pair programming) |
| **Assignment** | **Text Analyzer** — Read a string from the user and report: word count, character count, uppercase/lowercase count, most common word, reversed text |

---

### Week 8 — Midterm Project

**Theme:** Putting it all together.

| Component | Details |
|-----------|---------|
| **Topics** | Integration of all concepts from weeks 1–7, project planning, design before coding |
| **Tutorial Lessons** | Lesson 11 (Project: Gradebook) |
| **Concepts** | Program design, combining concepts, testing your work |
| **Classroom Activity** | Day 1: Plan the project on paper. Day 2–3: Implement. Day 4: Present to a partner |
| **Assignment** | **Gradebook Application** — See [§4 Assignment Descriptions](#week-8-midterm-gradebook-application) |

---

### Week 9 — Error Handling and Records

**Theme:** Building robust programs with custom data types.

| Component | Details |
|-----------|---------|
| **Topics** | `attempt`/`handle`/`ensure`, `abort`, error recovery, `record` definitions, fields, defaults, `based on`/`with` composition |
| **Tutorial Lessons** | Lesson 13 (Error Handling), Lesson 14 (Records) |
| **Concepts** | Defensive programming, custom types, structured data |
| **Classroom Activity** | "Break-proof program" — students deliberately try to crash each other's programs; the program with the fewest unhandled errors wins |
| **Assignment** | **Student Records System** — Define records for students and courses, create instances, handle invalid data gracefully with `attempt`/`handle` |

---

### Week 10 — Files and I/O

**Theme:** Making programs work with persistent data.

| Component | Details |
|-----------|---------|
| **Topics** | Reading/writing text files, `read_lines`/`write_lines`, file system operations (`file_exists`, `create_dir`, `list_dir`), path operations |
| **Tutorial Lessons** | Lesson 15 (Working with Files) |
| **Concepts** | Persistence, file modes, safe file handling with `attempt`/`ensure` |
| **Classroom Activity** | "File detective" — provide files with hidden messages encoded in various ways; students write programs to decode them |
| **Assignment** | **File-Based Address Book** — A contact manager that saves/loads contacts from a file so data persists between program runs |

---

### Week 11 — Advanced Topics

**Theme:** Modules, randomness, and time-based programs.

| Component | Details |
|-----------|---------|
| **Topics** | `use:` imports, module organization, random numbers, timers, event-driven programming |
| **Tutorial Lessons** | Lesson 16 (Random & Games), Lesson 17 (Modules), Lesson 18 (Timers) |
| **Concepts** | Code organization, randomness, asynchronous events |
| **Classroom Activity** | "Game jam" — 90-minute session where students build a simple text-based game |
| **Assignment** | **Game or Simulation** — Choose one: (a) Number guessing game with scoring, (b) Dice game (Yahtzee-lite), or (c) Simple text adventure. Must use randomness and file I/O for high scores |

---

### Week 12 — Final Project

**Theme:** Design, build, and present an original program.

| Component | Details |
|-----------|---------|
| **Topics** | Project planning, requirements gathering, implementation, testing, presentation |
| **Tutorial Lessons** | All (as reference) |
| **Concepts** | Software development lifecycle, independent problem-solving |
| **Activity** | Day 1: Proposal and design document. Days 2–4: Implementation. Day 5: Presentations |
| **Assignment** | **Final Project** — See [§4 Assignment Descriptions](#week-12-final-project) |

---

## 3. Learning Objectives by Unit

### Week 1 — Getting Started
- Students can install and run the PLAIN interpreter
- Students can write a program with `display()` statements
- Students can explain what `task Main()` does
- Students can use `rem:` to comment their code

### Week 2 — Data and Variables
- Students can declare variables with `var` and constants with `fxd`
- Students can identify PLAIN's data types (integer, float, string, boolean)
- Students can use type prefixes to name variables (`intCount`, `strName`)
- Students can read user input with `get()` and use it in expressions
- Students can concatenate strings with `&` and use `v"..."` for interpolation

### Week 3 — Making Decisions
- Students can write `if`/`else` blocks to branch based on conditions
- Students can use comparison and logical operators
- Students can use `choose`/`choice` for multi-way decisions
- Students can trace through conditional logic to predict program output

### Week 4 — Loops and Repetition
- Students can write counting loops with `from`/`to` and optional `step`
- Students can write collection loops with `in`
- Students can use `exit` to break out of a loop early
- Students can use `continue` to skip iterations
- Students can trace through nested loops

### Week 5 — Collections
- Students can create and manipulate lists (add, remove, access by index)
- Students can create and manipulate tables (add, look up, check for keys)
- Students can iterate over lists and tables
- Students can choose the appropriate collection type for a problem

### Week 6 — Tasks (Procedures)
- Students can define and call tasks with no parameters
- Students can define tasks with `with` parameters
- Students can explain why parameters are immutable
- Students can decompose a problem into reusable tasks

### Week 7 — Functions and Strings
- Students can define functions with `using` and `deliver`
- Students can explain the difference between procedures (`with`) and functions (`using`)
- Students can use string operations to process text
- Students can use function return values in expressions

### Week 8 — Midterm Project
- Students can design a multi-task program before coding
- Students can integrate variables, loops, collections, tasks, and functions
- Students can test their program with different inputs

### Week 9 — Error Handling and Records
- Students can use `attempt`/`handle` to catch errors
- Students can raise errors with `abort`
- Students can define records with typed fields and defaults
- Students can create record instances and access fields
- Students can explain record composition with `based on` and `with`

### Week 10 — Files and I/O
- Students can read and write text files using `read_file`/`write_file`
- Students can process files line-by-line with `read_lines`/`write_lines`
- Students can check for file existence before reading
- Students can use `attempt`/`ensure` for safe file handling

### Week 11 — Advanced Topics
- Students can organize code into modules with `use:`
- Students can generate random numbers and use them in programs
- Students can create timers and handle timed events

### Week 12 — Final Project
- Students can plan, design, and implement an original program
- Students can present their work and explain their design choices
- Students can identify concepts they've mastered and areas for growth

---

## 4. Assignment Descriptions

### Week 1: Install and Explore

**Objective:** Get comfortable with the PLAIN development environment.

**Requirements:**
1. Install PLAIN successfully (verify with `plain -help`)
2. Run three provided example programs
3. For each program, make at least two modifications and observe the results
4. Write a short paragraph (3–5 sentences) describing what you changed and what happened

**Deliverable:** Modified `.plain` files and a text document with observations.

---

### Week 2: Calculator

**Objective:** Practice variables, user input, and arithmetic expressions.

**Requirements:**
1. Ask the user for two numbers
2. Ask for an operation (+, -, *, /)
3. Perform the calculation and display the result
4. Handle division by zero with an appropriate message

**Sample interaction:**
```
Enter first number: 15
Enter second number: 4
Enter operation (+, -, *, /): *
15 * 4 = 60
```

**Deliverable:** `calculator.plain`

---

### Week 3: Grade Classifier

**Objective:** Practice conditional logic and multi-way branching.

**Requirements:**
1. Ask the user for a numeric score (0–100)
2. Display the letter grade using this scale: A (90–100), B (80–89), C (70–79), D (60–69), F (below 60)
3. Display an encouraging or appropriate message for each grade
4. Handle invalid input (scores below 0 or above 100)

**Deliverable:** `grade_classifier.plain`

---

### Week 4: Multiplication Table

**Objective:** Practice loops and formatted output.

**Requirements:**
1. Generate a multiplication table from 1×1 to 10×10
2. Format the output in a grid with aligned columns
3. Include row and column headers

**Deliverable:** `multiplication_table.plain`

---

### Week 5: Contact List Manager

**Objective:** Practice collections (lists and tables) with user interaction.

**Requirements:**
1. Store contacts (name → phone number) in a table
2. Provide a menu with options: Add, Look Up, Remove, List All, Quit
3. Handle the case where a contact isn't found
4. Display all contacts sorted by name

**Deliverable:** `contact_list.plain`

---

### Week 6: Menu-Driven Program

**Objective:** Practice organizing code into tasks.

**Requirements:**
1. Create a program with at least 4 menu options plus Quit
2. Each option calls a separate task
3. The program loops back to the menu after each action
4. Use at least one task with parameters

**Topic suggestions:** Unit converter, quiz game, to-do list, mini-encyclopedia

**Deliverable:** `menu_program.plain`

---

### Week 7: Text Analyzer

**Objective:** Practice functions and string operations.

**Requirements:**
1. Ask the user for a line of text
2. Report: total characters, total words, uppercase letters, lowercase letters
3. Display the text reversed
4. Display the text in all uppercase and all lowercase
5. Each analysis should be its own function (using `using`/`deliver`)

**Deliverable:** `text_analyzer.plain`

---

### Week 8 (Midterm): Gradebook Application

**Objective:** Integrate all concepts from weeks 1–7 into a complete application.

**Requirements:**
1. Store data for at least 3 students, each with at least 4 grades
2. Calculate each student's average
3. Calculate the class average
4. Determine the highest and lowest averages (hint: try `min()` and `max()` on a list)
5. Display a formatted report
6. Use tasks for organization (at least 3 separate tasks)
7. Use functions for calculations (at least 2 `using` tasks)

**Grading:** See [§5 Project Rubrics](#midterm-project-rubric).

**Deliverable:** `gradebook.plain`

---

### Week 9: Student Records System

**Objective:** Practice records and error handling.

**Requirements:**
1. Define a `Student` record with: name (string), id (integer), grade (string), gpa (float with default)
2. Create at least 3 student instances
3. Write a function that validates student data (GPA between 0.0–4.0, name not empty)
4. Use `attempt`/`handle` to catch validation errors
5. Display all student information in a formatted table

**Deliverable:** `student_records.plain`

---

### Week 10: File-Based Address Book

**Objective:** Practice file I/O with persistent data.

**Requirements:**
1. Load contacts from a file at program start (if the file exists)
2. Provide menu options: Add Contact, Search, Delete, List All, Save, Quit
3. Save contacts to file before quitting
4. Use `attempt`/`ensure` for safe file operations
5. Handle the case where the data file doesn't exist (first run)

**Deliverable:** `address_book.plain`

---

### Week 11: Game or Simulation

**Objective:** Practice randomness and advanced features.

**Choose one:**

**(a) Number Guessing Game**
- Computer picks a random number (1–100)
- Player guesses with "too high" / "too low" feedback
- Track number of guesses
- Save high scores to a file

**(b) Dice Game**
- Simulate dice rolls with scoring rules
- Multiple rounds with running scores
- Save results to a file

**(c) Text Adventure**
- At least 5 rooms/locations
- Player navigates with text commands
- Track inventory items
- Use `choose`/`choice` for player decisions

**Deliverable:** Game `.plain` file + high scores file (if applicable)

---

### Week 12: Final Project

**Objective:** Design and build an original program using concepts from the entire course.

**Phase 1 — Proposal (Day 1):**
- One paragraph describing what the program will do
- List of features
- List of PLAIN concepts used (must use at least 5 different concepts from the course)

**Phase 2 — Implementation (Days 2–4):**
- Working program with clean, commented code
- At least 100 lines of code (excluding comments)
- Organized into multiple tasks

**Phase 3 — Presentation (Day 5):**
- 5-minute demo to the class
- Explain one thing you're proud of
- Explain one challenge you overcame

**Grading:** See [§5 Project Rubrics](#final-project-rubric).

**Project Ideas:**
- Personal finance tracker (budgets, expenses, savings goals)
- Quiz/flashcard application (load questions from file, track scores)
- Recipe manager (store, search, display recipes)
- Mini database (records, file storage, search/filter)
- Text-based RPG (rooms, inventory, combat with random elements)
- Inventory management system (items, quantities, alerts)
- Student schedule planner (courses, times, conflict detection)

---

## 5. Project Rubrics

### Midterm Project Rubric

| Criterion | Excellent (A) | Good (B) | Adequate (C) | Needs Work (D/F) |
|-----------|--------------|----------|--------------|-------------------|
| **Correctness** (30%) | All calculations are correct; no runtime errors | Minor calculation errors; handles most cases | Some incorrect results; crashes on edge cases | Major errors; doesn't run |
| **Code Organization** (25%) | 3+ well-named tasks, clear structure, logical flow | 2–3 tasks, mostly organized | Minimal use of tasks; some structure | All code in Main; no organization |
| **Concepts Used** (20%) | Uses variables, loops, lists, tasks, functions appropriately | Uses most concepts but some are awkward | Uses basic concepts only | Missing several required concepts |
| **Output Quality** (15%) | Clean, formatted, easy to read | Mostly formatted; minor issues | Output is functional but unformatted | Difficult to read or understand |
| **Comments & Style** (10%) | Clear comments, consistent naming, good indentation | Some comments, mostly consistent | Few comments, inconsistent style | No comments, hard to follow |

---

### Final Project Rubric

| Criterion | Excellent (A) | Good (B) | Adequate (C) | Needs Work (D/F) |
|-----------|--------------|----------|--------------|-------------------|
| **Functionality** (25%) | All features work; handles edge cases | Most features work; minor bugs | Core features work; some broken | Major features missing or broken |
| **Complexity** (20%) | Uses 7+ concepts; non-trivial logic | Uses 5–6 concepts; moderate complexity | Uses 4–5 concepts; simple logic | Below minimum concept requirement |
| **Code Quality** (20%) | Well-organized tasks, clean code, good names | Mostly organized; some long functions | Functional but messy | Disorganized; hard to follow |
| **Error Handling** (10%) | Gracefully handles invalid input and edge cases | Handles most common errors | Minimal error handling | No error handling; crashes easily |
| **Documentation** (10%) | Clear comments explaining why, not just what | Comments on most sections | Some comments | No comments |
| **Presentation** (15%) | Clear demo, articulate explanation, shows pride | Good demo, adequate explanation | Basic demo, minimal explanation | Unprepared or unclear |

---

## 6. Assessment Ideas

### Weekly Quizzes (10–15 minutes)

**Week 2 — Variables Quiz:**
1. What is the difference between `var` and `fxd`?
2. What type prefix would you use for a variable holding someone's name?
3. What does `v"Hello {name}"` do?
4. What is the result of `7 / 2`? What about `7 // 2`?

**Week 4 — Loops Quiz:**
1. How many times does `loop i from 1 to 5` execute its body?
2. What does `exit` do inside a loop?
3. Write a loop that displays the numbers 10, 8, 6, 4, 2.
4. What is the difference between `loop i from 1 to 5` and `loop item in myList`?

**Week 7 — Functions Quiz:**
1. What is the difference between `with` and `using`?
2. What keyword returns a value from a function?
3. Why can't you reassign a parameter inside a task?
4. Write a function `Double` that takes a number and returns it multiplied by 2.

### Code Reading Exercises

Give students code and ask them to:
1. **Predict the output** without running it
2. **Find the bug** in an intentionally broken program
3. **Trace through** a loop, writing the value of each variable at each step
4. **Explain in plain English** what a program does

Example (find the bug):
```plain
task Main()
    var total = 0
    loop i from 1 to 5
        var total = total + i     rem: Bug! declares new variable instead of updating
    display(total)
```

### Debugging Challenges

Provide programs with 2–3 bugs and ask students to:
1. Run the program and observe the incorrect behavior
2. Identify each bug
3. Fix each bug
4. Explain why the bug caused the observed behavior

### Pair Programming Exercises

Students work in pairs:
- **Driver:** Types the code
- **Navigator:** Reviews each line, suggests improvements
- Switch roles every 15 minutes
- At the end, both students should be able to explain every line

---

## 7. Teaching Tips

### Why PLAIN Helps Beginners

PLAIN was designed with teaching in mind. Here's how its features prevent common beginner mistakes:

| PLAIN Feature | What It Prevents | Common Mistake in Other Languages |
|---------------|-----------------|----------------------------------|
| **No variable shadowing** | Inner variable accidentally hiding outer one | `for (int i...) { int i = 5; }` — which `i`? |
| **`with` vs `using`** | Forgetting to return a value, or returning from a procedure | `def add(a, b):` — should it return? Who knows |
| **Parameter immutability** | Accidentally modifying function inputs | Changing a parameter and expecting the caller to see the change |
| **`rem:` / `note:` comments** | Confusing comment syntax with operators | Python: Is `# comment` a comment or a length operation? |
| **`deliver` instead of `return`** | Clearer mental model for beginners | `return` is overloaded across languages with different meanings |
| **Indentation-based blocks** | Missing braces, dangling else | C/Java: `if (x) stmt1; stmt2;` — is `stmt2` in the `if`? |

### Common Student Misconceptions

1. **"Variables are containers"** — Students often think `var x = 5` puts 5 "inside" x. Encourage thinking of it as "x now refers to the value 5."

2. **"`=` means 'equals'"** — Students confuse assignment (`=`) with comparison (`==`). Emphasize: "single equals *sets*, double equals *tests*."

3. **"The computer reads the whole file first"** — Students may think all tasks run simultaneously. Emphasize sequential execution starting from `Main()`.

4. **"Loops run instantly"** — Students may not realize each iteration takes time. Use `sleep()` or tracing to slow things down.

5. **"Variables remember everything"** — Students may think reassigning a variable keeps the old value somewhere. Demonstrate that `x = 10` then `x = 20` means the 10 is gone.

### Classroom Activities That Work

- **Live coding with mistakes:** Deliberately make errors while coding in front of the class. Let students spot and fix them.
- **Prediction exercises:** Show 5 lines of code. Students write what they think the output will be. Then run it. Discuss surprises.
- **Code telephone:** One student writes a program, passes it to the next student who must explain what it does, passes the explanation to a third student who must recreate the program from the description.
- **Bug bounty:** Students write programs, then swap with a partner who tries to crash it with unusual inputs.

### Pacing Suggestions

- **If students are struggling** with a concept, slow down. It's better to deeply understand weeks 1–8 than to rush through all 12.
- **If students are ahead**, use the bonus challenges in [§8 Differentiation](#8-differentiation).
- **Labs matter more than lectures.** Students learn programming by *doing*. Aim for at least 60% hands-on time.
- **The midterm project (week 8) is a checkpoint.** If students can complete it, they've mastered the fundamentals. Everything after is enrichment.

---

## 8. Differentiation

### For Struggling Students

**Scaffolding strategies:**

1. **Starter code** — Provide partially-complete programs with `rem: YOUR CODE HERE` markers
2. **Guided exercises** — Step-by-step instructions: "First, declare a variable called `total`..."
3. **Pair with a stronger student** — The stronger student explains; the struggling student types
4. **Reduce scope** — Instead of a full contact manager, start with just "add and display"
5. **Visual tracing worksheets** — Tables where students fill in variable values at each step

**Modified assignments:**
- Week 4: Generate a 5×5 table instead of 10×10
- Week 8: Gradebook with 2 students and 2 grades (instead of 3 and 4)
- Week 12: Simpler project with 3 concepts instead of 5

### For Advanced Students

**Extension challenges by week:**

- **Week 2:** Support more operations (exponent, square root, modulo)
- **Week 3:** Implement a BMI calculator with health category recommendations
- **Week 4:** Generate a triangle pattern, diamond pattern, or Pascal's triangle
- **Week 5:** Implement a basic stack or queue using a list
- **Week 6:** Create a unit conversion program with 10+ conversions organized into categories
- **Week 7:** Implement a Caesar cipher encoder/decoder
- **Week 8:** Add: sort students by average, grade distribution histogram (text-based), GPA calculation
- **Week 9:** Implement record composition — create an inheritance hierarchy 3 levels deep
- **Week 10:** Implement a simple CSV parser that reads and writes tabular data
- **Week 11:** Create a multi-room text adventure game with save/load functionality
- **Week 12:** Present to the class AND write a 1-page design document explaining architectural decisions

**Independent projects for fast finishers:**
- Build a simple database system using files and records
- Create a text-based drawing program (ASCII art)
- Implement a basic encryption/decryption program
- Write a program that generates other PLAIN programs (meta-programming)

---

## 9. Resources

### Documentation

| Document | Description | When to Reference |
|----------|-------------|-------------------|
| [User Guide](USER-GUIDE.md) | Getting started, tools, concepts overview | Weeks 1–2, and as a general reference |
| [Tutorial](TUTORIAL.md) | 18 progressive hands-on lessons | Each week — maps to the tutorial lessons |
| [Language Reference](LANGUAGE-REFERENCE.md) | Complete formal specification | When students ask "but exactly what happens if..." |
| [Standard Library](STDLIB.md) | Every built-in function documented | Whenever students need a function — look it up here |

### Tutorial Lesson Mapping

| Week | Tutorial Lessons | Example Files |
|------|-----------------|---------------|
| 1 | 1 | `lesson_01_hello.plain` |
| 2 | 2, 3 | `lesson_02_variables.plain`, `lesson_03_input.plain` |
| 3 | 4 | `lesson_04_decisions.plain` |
| 4 | 5 | `lesson_05_loops.plain` |
| 5 | 6, 7 | `lesson_06_lists.plain`, `lesson_07_tables.plain` |
| 6 | 8, 9 | `lesson_08_tasks.plain`, `lesson_09_parameters.plain` |
| 7 | 10, 12 | `lesson_10_functions.plain`, `lesson_12_strings.plain` |
| 8 | 11 | `lesson_11_project_gradebook.plain` |
| 9 | 13, 14 | `lesson_13_error_handling.plain`, `lesson_14_records.plain` |
| 10 | 15 | `lesson_15_files.plain` |
| 11 | 16, 17, 18 | `lesson_16_random_games.plain`, `lesson_17_modules.plain`, `lesson_18_timers.plain` |
| 12 | All | All (as reference) |

### Example Programs

All tutorial example programs are in the `examples/tutorial/` directory. Each is a complete, runnable program that demonstrates the lesson concepts. Students can:
- Run them to see expected output
- Modify them for exercises
- Use them as templates for assignments

---

*This curriculum guide is for PLAIN version 1.0. For language documentation, see the [User Guide](USER-GUIDE.md), [Language Reference](LANGUAGE-REFERENCE.md), and [Standard Library](STDLIB.md).*
