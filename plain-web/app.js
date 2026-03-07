// plain-lang.js is loaded as a plain <script> before this file and exposes
// window.registerPlainLanguage — no ES module import needed.

// ── Example programs ───────────────────────────────────────────────────────
const EXAMPLES = [
  {
    id: "fibonacci",
    label: "Fibonacci Sequence",
    code: `rem: Print the first 15 Fibonacci numbers
var a = 0
var b = 1
var count = 0

loop
    if count == 15 then exit
    display(to_string(a))
    var temp = a + b
    a = b
    b = temp
    count += 1
`,
    inputs: "",
  },
  {
    id: "fizzbuzz",
    label: "FizzBuzz",
    code: `rem: Classic FizzBuzz 1-30
loop n from 1 to 30
    choose true
        choice n % 15 == 0
            display("FizzBuzz")
        choice n % 3 == 0
            display("Fizz")
        choice n % 5 == 0
            display("Buzz")
        default
            display(to_string(n))
`,
    inputs: "",
  },
  {
    id: "calculator",
    label: "Simple Calculator (uses input)",
    code: `rem: Simple calculator — enter two numbers and an operator
rem: Pre-fill the inputs box below before clicking Run

var a = to_float(get("First number: "))
var b = to_float(get("Second number: "))
var op = get("Operator (+ - * /): ")

var result = 0.0
choose op
    choice "+"
        result = a + b
    choice "-"
        result = a - b
    choice "*"
        result = a * b
    choice "/"
        if b == 0.0
            display("Error: division by zero")
            exit
        result = a / b
    default
        display("Unknown operator: " & op)
        exit

display(to_string(a) & " " & op & " " & to_string(b) & " = " & to_string(result))
`,
    inputs: "10\n3\n+",
  },
  {
    id: "grade",
    label: "Grade Calculator (uses input)",
    code: `rem: Enter up to 5 scores (type 'done' to finish)
rem: Pre-fill inputs below — one score per line, last line: done

var scores = []
var total = 0
var count = 0

loop
    var input = get("Enter score (or 'done'): ")
    if input == "done" then exit
    var score = to_int(input)
    append(scores, score)
    total += score
    count += 1

if count == 0
    display("No scores entered.")
else
    var avg = total / count
    display("Scores entered: " & to_string(count))
    display("Average: " & to_string(avg))
    choose true
        choice avg >= 90
            display("Grade: A")
        choice avg >= 80
            display("Grade: B")
        choice avg >= 70
            display("Grade: C")
        choice avg >= 60
            display("Grade: D")
        default
            display("Grade: F")
`,
    inputs: "85\n92\n78\ndone",
  },
];

// ── Tutorial lessons ───────────────────────────────────────────────────────
const TUTORIALS = [
  {
    id: "hello_world",
    order: 1,
    label: "Hello World",
    level: "easy",
    summary: [
      "How to run a PLAIN program.",
      "How display() sends text to the output panel.",
    ],
    explanation: [
      "PLAIN programs run from top to bottom.",
      "display() writes one line to the output area, so it is the quickest way to see what your code is doing.",
    ],
    task: [
      "Click Run once and compare the output to the expected result below.",
      "Then change the text inside display() and run it again.",
    ],
    expectedOutput: ["Hello, World!"],
    hint: ["Text must be inside double quotes."],
    starterCode: `display("Hello, World!")`,
    inputs: "",
  },
  {
    id: "variables",
    order: 2,
    label: "Variables, Types, and Display",
    level: "easy",
    summary: [
      "How var declares a variable and gives it a name.",
      "How variables hold typed values such as strings, integers, and floats.",
      "How display() and & can show text together with variable values.",
    ],
    explanation: [
      "A declaration such as var name = \"Ada\" both creates the variable and stores its first value.",
      "PLAIN keeps track of the value's type. A quoted value is a string, a whole number is an integer, and a decimal number is a float.",
      "You can let PLAIN infer the type, or you can write it explicitly with as string, as integer, and so on.",
      "In the desktop lessons you may also see naming conventions such as strName, intCount, or fltPrice. Those prefixes can make a variable's purpose easier to read.",
    ],
    task: [
      "Fill in the empty string so the variable name stores Ada.",
      "Then run the lesson. Optional: change the greeting or name to make it your own.",
    ],
    expectedOutput: ["Hello, Ada!"],
    hint: ["name is explicitly typed as a string, while message lets PLAIN infer the type from the quoted text. Later you may also see names like strName or intCount in the desktop tutorials."],
    starterCode: `var name as string = ""
var message = "Hello"

display(message & ", " & name & "!")`,
    inputs: "",
  },
  {
    id: "math",
    order: 3,
    label: "Numbers: Integers and Floats",
    level: "easy",
    summary: [
      "How integers store whole numbers such as 3 or 42.",
      "How floats store numbers with a decimal point such as 3.5.",
      "How numeric values can be displayed just like text.",
    ],
    explanation: [
      "An integer has no decimal point. A float does.",
      "Use integer for whole counts, and float when fractional values matter, such as prices, measurements, or averages.",
      "Both are numbers, but choosing the right one makes your program easier to read.",
    ],
    task: [
      "Change the float value from 0.0 to 3.5.",
      "Then add a second display() line that shows the decimal number.",
    ],
    expectedOutput: ["Whole number: 3", "Decimal number: 3.5"],
    hint: ["3 is an integer. 3.5 is a float because it has a decimal point."],
    starterCode: `var whole as integer = 3
var price as float = 0.0

display("Whole number: " & whole)
rem: Add one display() line here for the decimal number.`,
    inputs: "",
  },
  {
    id: "arithmetic",
    order: 4,
    label: "Arithmetic Operators",
    level: "easy",
    summary: [
      "How + adds, - subtracts, and * multiplies.",
      "How / divides and % gives the remainder.",
      "How arithmetic expressions can be displayed so you can check your work.",
    ],
    explanation: [
      "Each arithmetic operator does a different job, so this lesson is really about learning which symbol matches which idea.",
      "% tells you the remainder after division. For example, 9 % 4 is 1.",
      "When you want a decimal result from division, use float values such as 9.0 and 4.0 instead of 9 and 4.",
    ],
    task: [
      "Keep a and b as they are.",
      "Add one display() line for subtraction, one for multiplication, and one for remainder.",
    ],
    expectedOutput: ["Add: 13", "Divide: 2.25", "Subtract: 5", "Multiply: 36", "Remainder: 1"],
    hint: ["Use (a - b), (a * b), and (a % b) inside the missing display() lines."],
    starterCode: `var a = 9
var b = 4

display("Add: " & (a + b))
display("Divide: " & (9.0 / 4.0))
rem: Add one display() line here for subtract.
rem: Add one display() line here for multiply.
rem: Add one display() line here for remainder.`,
    inputs: "",
  },
  {
    id: "if_else",
    order: 5,
    label: "If / Else",
    level: "easy",
    summary: [
      "How if / else chooses between two paths.",
      "How comparison operators create true or false conditions.",
    ],
    explanation: [
      "A comparison such as temperature > 80 evaluates to true or false.",
      "If the condition is true, the if block runs. Otherwise, the else block runs.",
    ],
    task: [
      "Set temperature to 72.",
      "Then add an else branch so the expected output appears.",
    ],
    expectedOutput: ["It's mild today."],
    hint: ["Only one branch runs: the if block when the condition is true, or the else block when it is false."],
    starterCode: `var temperature = 72

if temperature > 80
    display("It's hot today.")
rem: Add an else branch here for mild weather.`,
    inputs: "",
  },
  {
    id: "choose_value",
    order: 6,
    label: "Choose / Choice with Values",
    level: "practice",
    summary: [
      "How choose compares one value against several choices.",
      "How default handles anything not matched above.",
    ],
    explanation: [
      "Use this when you already have one value, such as a day name, and want to compare it to several exact options.",
      "The desktop decisions lesson uses choose for day names because it reads more clearly than a long chain of nested if statements.",
    ],
    task: [
      "Set day to Friday.",
      "Add a Friday choice so the expected output appears.",
      "Optional: add a Saturday choice that prints Weekend!.",
    ],
    expectedOutput: ["Almost weekend!"],
    hint: ["Each choice should match the same kind of value as choose day, so the choices here should be strings such as \"Friday\"."],
    starterCode: `var day = ""

choose day
    choice "Monday"
        display("Start of the week")
    rem: Add a Friday choice here.
    default
        display("Just a regular day.")`,
    inputs: "",
  },
  {
    id: "choose_true",
    order: 7,
    label: "Choose True for Conditions",
    level: "practice",
    summary: [
      "How choose true lets each choice be a condition.",
      "Why the first true choice wins.",
    ],
    explanation: [
      "Use this pattern when each branch is a comparison such as score >= 80 rather than a fixed value match.",
      "It plays a similar role to an if / else-if ladder, but often stays easier to scan.",
      "The desktop decisions lesson also introduces logical operators such as and, or, and not. Those combine naturally with choose true conditions later on.",
    ],
    task: [
      "Keep score at 87.",
      "Add the missing choice so the program prints Grade: B.",
    ],
    expectedOutput: ["Grade: B"],
    hint: ["Use choose true when each choice is a test such as score >= 80 rather than a fixed value such as \"Friday\"."],
    starterCode: `var score = 87

choose true
    choice score >= 90
        display("Grade: A")
    rem: Add a choice here for scores 80 and above.
    choice score >= 70
        display("Grade: C")
    default
        display("Keep practicing")`,
    inputs: "",
  },
  {
    id: "loops",
    order: 8,
    label: "Counting Loops",
    level: "practice",
    summary: [
      "How loop ... from ... to repeats a block of code.",
      "How the loop variable changes each time.",
    ],
    explanation: [
      "The desktop loop lesson shows that counting loops can also use step, such as step 2 for even numbers or step -1 for a countdown.",
      "PLAIN also has collection loops written as loop item in list, which you will use later when you reach lists.",
    ],
    task: [
      "Change the ending number so the loop counts from 1 to 5.",
      "Then add the display() line inside the loop.",
    ],
    expectedOutput: ["1", "2", "3", "4", "5"],
    hint: ["Inside the loop, n already holds the current number. You can display it directly or convert it with to_string(n)."],
    starterCode: `loop n from 1 to 0
    rem: Add a display() line here to print n.`,
    inputs: "",
  },
  {
    id: "constants",
    order: 9,
    label: "Fixed Values with fxd",
    level: "practice",
    summary: [
      "How fxd creates a constant that should not change.",
      "How constants must include an explicit type.",
    ],
    explanation: [
      "The desktop variables lesson pairs ordinary variables with constants so learners can see the difference between changeable data and fixed values such as PI or an app name.",
      "Use a constant when the value is meant to stay the same for the whole program.",
    ],
    task: [
      "Fill in the empty string so the constant says Welcome to PLAIN!.",
      "Then run the lesson without trying to reassign the constant.",
    ],
    expectedOutput: ["Welcome to PLAIN!"],
    hint: ["A constant looks like fxd NAME as string = \"text\"."],
    starterCode: `fxd GREETING as string = ""

display(GREETING)`,
    inputs: "",
  },
  {
    id: "input",
    order: 10,
    label: "Getting Input and Building Responses",
    level: "practice",
    summary: [
      "How get() reads one line from the input box.",
      "How the prompt and your supplied answer appear in the output panel.",
      "How input starts as text, even when it looks like a number.",
    ],
    explanation: [
      "The desktop input lesson first builds replies with & and later shows interpolation with v\"Hello, {name}!\".",
      "It also converts numeric input with to_int() before doing arithmetic. That is the right next step when you want to add, compare, or count using user input.",
    ],
    task: [
      "Leave the input box as it is.",
      "Add a display() line that greets the name returned by get().",
      "Optional: change the supplied name and run it again, or rewrite the greeting with interpolation.",
    ],
    expectedOutput: ["What is your name? Sam", "Hello, Sam!"],
    hint: ["The first output line includes both the prompt and the supplied answer. get() returns text, so numeric input usually needs to_int() later if you want to do arithmetic with it."],
    starterCode: `var name = get("What is your name? ")

rem: Add a display() line here that says Hello, Sam! when the input is Sam.`,
    inputs: "Sam",
  },
  {
    id: "strings_basic",
    order: 11,
    label: "Strings: Case and Length",
    level: "practice",
    summary: [
      "How strings store text values.",
      "How upper(), lower(), and len() help you inspect or transform text.",
    ],
    explanation: [
      "The desktop strings lesson goes on to cover trim(), contains(), substring(), replace(), split(), and join().",
      "For a beginner lesson, the most useful first step is learning that text can be changed to upper- or lower-case and measured with len().",
      "Because len() returns a number, you often wrap it with to_string(...) when you want to place it inside a longer message.",
    ],
    task: [
      "Keep the word as hello.",
      "Add one display() line that prints the word in uppercase.",
      "Add one display() line that prints Length: 5.",
      "Optional: change the word and run it again.",
    ],
    expectedOutput: ["Upper: HELLO", "Length: 5"],
    hint: ["Use upper(word) for uppercase text, and to_string(len(word)) when you want to show the length inside a sentence."],
    starterCode: `var word = "hello"

rem: Add a display() line here for the uppercase version.
rem: Add a display() line here for the length.`,
    inputs: "",
  },
  {
    id: "task_basic",
    order: 12,
    label: "Your First Task",
    level: "practice",
    summary: [
      "How to define a simple task with no parameters.",
      "How to call a task by name with parentheses.",
    ],
    explanation: [
      "The desktop tasks lesson uses several tiny tasks such as SayHello(), DrawLine(), and ShowMenu() to show that tasks help organize code into named pieces.",
      "A task is useful when you want to reuse a behavior or give a block of code a clear purpose.",
    ],
    task: [
      "Add one display() line inside the task.",
      "Then call PracticeMessage() once below the task.",
      "Optional: call it a second time to see how reusable tasks behave.",
    ],
    expectedOutput: ["You are learning PLAIN."],
    hint: ["Write the code inside the task first, then call it with PracticeMessage()."],
    starterCode: `task PracticeMessage()
    rem: Add one display() line here.

rem: Call PracticeMessage() here.`,
    inputs: "",
  },
  {
    id: "task_with_parameter",
    order: 13,
    label: "Tasks with Parameters",
    level: "practice",
    summary: [
      "How a task can accept information using with (...).",
      "How the value you pass in becomes available inside the task.",
    ],
    explanation: [
      "The desktop parameter lesson shows that tasks can take one parameter or several, such as a name and a score.",
      "Parameters let one task work with many different inputs instead of hard-coding a single value.",
    ],
    task: [
      "Write the display() line inside the task so it greets the name parameter.",
      "Then call Greet(\"Mia\") below.",
      "Optional: call it again with a different name.",
    ],
    expectedOutput: ["Hello, Mia!"],
    hint: ["Use task Greet with (name) when the task needs an input value. Later, the same pattern can take multiple parameters, such as a name and a score."],
    starterCode: `task Greet with (name)
    rem: Add a display() line that uses the name parameter.

rem: Call Greet("Mia") here.`,
    inputs: "",
  },
  {
    id: "deliver_value",
    order: 14,
    label: "Functions with deliver",
    level: "practice",
    summary: [
      "How using (...) creates a task that returns a value.",
      "How deliver sends the result back to the caller.",
    ],
    explanation: [
      "The desktop functions lesson shows returned values being stored in variables, used directly inside display(), and even used inside conditions such as if IsEven(42).",
      "That is the key difference between a task with and a task using: a using task computes a value and gives it back.",
    ],
    task: [
      "Finish the task so it returns n * 2.",
      "Then complete the display() line so the expected output appears.",
    ],
    expectedOutput: ["Double: 14"],
    hint: ["A using task should finish with deliver some_value. After that, you can store the result in a variable or use it directly in another expression."],
    starterCode: `task Double using (n)
    rem: Add a deliver line here.

var answer = Double(7)
rem: Add a display() line here for the answer.`,
    inputs: "",
  },
  {
    id: "lists",
    order: 15,
    label: "Lists and Indexes",
    level: "practice",
    summary: [
      "How to store several values in a list.",
      "How list indexes start at 0 and how append() adds one more item.",
    ],
    explanation: [
      "The desktop lists lesson treats a list as an ordered collection, which is why positions matter and indexes start at 0.",
      "It also shows follow-on tools such as insert(), remove(), pop(), contains(), sort(), and reverse(). For this lesson, append() and index reading are the two core ideas to practice first.",
      "Lists also connect to string work: split() can turn text into a list, and join() can turn a list back into text.",
    ],
    task: [
      "Add one append() call so the list has four items.",
      "Then add a display() line that prints the first color.",
    ],
    expectedOutput: ["First color: red", "List size: 4"],
    hint: ["The first list item is colors[0], not colors[1]. A line such as append(colors, \"yellow\") adds one more item to the end."],
    starterCode: `var colors = ["red", "blue", "green"]
rem: Add one append() call here.

rem: Add a display() line here for the first color.
display("List size: " & to_string(len(colors)))`,
    inputs: "",
  },
  {
    id: "strings_tools",
    order: 16,
    label: "Strings: Search, Replace, and Split",
    level: "practice",
    summary: [
      "How contains(), substring(), and replace() help you inspect and edit text.",
      "How split() turns text into a list and join() turns list items back into one string.",
    ],
    explanation: [
      "The desktop strings lesson shows that text work is not just printing words. You can search inside text, slice out part of it, replace part of it, or break it into pieces.",
      "split(sentence, \" \") returns a list of words, which is why this lesson fits well after the list lesson.",
      "join(words, \"-\") does the reverse by combining many pieces into one string again.",
    ],
    task: [
      "Keep the sentence as it is.",
      "Add a display() line that checks whether the sentence contains coding.",
      "Add a display() line that prints the first 5 letters with substring().",
      "Add a display() line that replaces clear with fun.",
      "Add a display() line that joins the words with dashes.",
    ],
    expectedOutput: [
      "Contains coding: true",
      "Start: plain",
      "Updated: plain makes coding fun",
      "Joined: plain-makes-coding-clear",
    ],
    hint: ["Use split(sentence, \" \") to create the words list, substring(sentence, 0, 5) for the first five characters, and join(words, \"-\") to connect the words again."],
    starterCode: `var sentence = "plain makes coding clear"
var words = split(sentence, " ")

rem: Add a display() line for contains(sentence, "coding").
rem: Add a display() line for the first 5 letters.
rem: Add a display() line with clear replaced by fun.
rem: Add a display() line that joins words with "-".`,
    inputs: "",
  },
  {
    id: "list_loop",
    order: 17,
    label: "Looping Through a List",
    level: "practice",
    summary: [
      "How loop item in list visits each list value in order.",
      "How the loop variable changes on each pass.",
    ],
    explanation: [
      "The desktop lists lesson uses this pattern for things like shopping lists, where each pass through the loop gives you the next item in order.",
      "You can also keep extra information alongside the loop, such as a counter for numbering items or another list that you build with append() inside the loop.",
    ],
    task: [
      "Add one more fruit to the list.",
      "Then complete the loop body so each fruit prints on its own line.",
      "Optional: add a counter variable before the loop and number the items.",
    ],
    expectedOutput: ["apple", "banana", "cherry", "orange"],
    hint: ["Use loop fruit in fruits to step through each item. Inside the loop, fruit already holds the current item."],
    starterCode: `var fruits = ["apple", "banana", "cherry"]

rem: Add one more fruit to the list above.

loop fruit in fruits
    rem: Add a display() line here.`,
    inputs: "",
  },
  {
    id: "tables",
    order: 18,
    label: "Tables with Keys and Values",
    level: "practice",
    summary: [
      "How a table stores values under string keys.",
      "How to read and add values with square brackets.",
    ],
    explanation: [
      "The desktop tables lesson treats a table as a key-value lookup tool, similar to a dictionary. Instead of numeric positions, you use names such as \"name\" or \"age\".",
      "Later on, tables become even more useful with helpers such as has_key(), keys(), and values(), and by looping through keys(table) to inspect everything stored inside.",
      "Tables are good for lookups, grouped data, and counting patterns where the key is a word or label.",
    ],
    task: [
      "Add an age value to the table.",
      "Then add a display() line that prints the pet name.",
    ],
    expectedOutput: ["Pet: Nori", "Age: 3"],
    hint: ["Use pet[\"name\"] to read the value stored under the key name. The same square-bracket pattern also works when you add pet[\"age\"] = 3."],
    starterCode: `var pet = {"name": "Nori", "type": "cat"}
rem: Add pet["age"] = 3 here.

rem: Add a display() line here for the pet name.
display("Age: " & to_string(pet["age"]))`,
    inputs: "",
  },
  {
    id: "challenge_greeter",
    order: 19,
    label: "Mini Challenge: Friendly Greeter",
    level: "stretch",
    summary: [
      "Combine get() with a task that accepts a parameter.",
      "Pass the name you read from input into the task call.",
    ],
    explanation: [
      "This challenge brings together two earlier ideas: reading text with get() and passing that text into a task with a parameter.",
      "A good way to solve it is in two steps: first store the input in name, then pass name into Greet(name).",
    ],
    task: [
      "Use the input box as it is.",
      "Finish the task so it greets the person by name.",
      "Then call Greet(name).",
    ],
    expectedOutput: ["What is your name? Riley", "Welcome, Riley!"],
    hint: ["Read the name first, then pass that variable into Greet(name). Inside the task, use the parameter rather than the original input variable."],
    starterCode: `var name = get("What is your name? ")

task Greet with (person)
    rem: Add one display() line here.

rem: Call Greet(name) here.`,
    inputs: "Riley",
  },
  {
    id: "challenge_fizzbuzz",
    order: 20,
    label: "Mini Challenge: FizzBuzz",
    level: "stretch",
    summary: [
      "Combine a counting loop with choose true.",
      "Use the % operator to test multiples of 3, 5, and 15.",
    ],
    explanation: [
      "This challenge combines the loop lesson, the choose true lesson, and the remainder operator from arithmetic.",
      "The order of the choices matters: test 15 first so numbers such as 15 do not stop at the 3 or 5 branch too early.",
    ],
    task: [
      "Finish each display() line in the choose block.",
      "Keep the loop from 1 to 15 until the expected output matches.",
    ],
    expectedOutput: [
      "1",
      "2",
      "Fizz",
      "4",
      "Buzz",
      "Fizz",
      "7",
      "8",
      "Fizz",
      "Buzz",
      "11",
      "Fizz",
      "13",
      "14",
      "FizzBuzz",
    ],
    hint: ["Check the 15 case first so it wins before the 3 and 5 cases. In the default branch, display the current number n."],
    starterCode: `loop n from 1 to 15
    choose true
        choice n % 15 == 0
            rem: Display FizzBuzz here.
        choice n % 3 == 0
            rem: Display Fizz here.
        choice n % 5 == 0
            rem: Display Buzz here.
        default
            rem: Display the number n here.`,
    inputs: "",
  },
  {
    id: "challenge_pet_roll_call",
    order: 21,
    label: "Mini Challenge: Pet Roll Call",
    level: "stretch",
    summary: [
      "Combine a list loop with table lookups.",
      "Read a table value using the current loop variable as the key.",
    ],
    explanation: [
      "This combines the main ideas from the desktop lists and tables lessons: lists keep an ordered set of names, and tables let you look up details about each name.",
      "It uses the same general pattern as more advanced counter examples: loop through items, then use the current item to read or update a value in a table.",
    ],
    task: [
      "Add a third pet named Pip to the list.",
      "Add Pip's age to the ages table.",
      "Then complete the loop body so each line prints like Name: age.",
    ],
    expectedOutput: ["Nori: 3", "Luna: 5", "Pip: 2"],
    hint: ["Inside the loop, pet is the current name, so ages[pet] gives that pet's age. If you need it, to_string(ages[pet]) turns the age into text."],
    starterCode: `var pets = ["Nori", "Luna"]
var ages = {"Nori": 3, "Luna": 5}

rem: Add "Pip" to pets.
rem: Add ages["Pip"] = 2 here.

loop pet in pets
    rem: Add a display() line using pet and ages[pet].`,
    inputs: "",
  },
];

const MODES = {
  EXAMPLES: "examples",
  TUTORIALS: "tutorials",
};

function toLines(value) {
  if (!value) return [];
  return Array.isArray(value) ? value : String(value).split("\n");
}

function noteBodyLines(lines, bulletPrefix = "- ") {
  return toLines(lines).map((line) => (line ? "    " + bulletPrefix + line : ""));
}

function noteSection(title, lines, bulletPrefix = "- ") {
  return ["    " + title, ...noteBodyLines(lines, bulletPrefix)];
}

function renderTutorialContent(lesson) {
  const codeLines = toLines(lesson.starterCode.trimEnd());
  const parts = [
    "note:",
    "    LESSON " + String(lesson.order).padStart(2, "0") + " - " + lesson.label,
    ...(lesson.level ? ["    LEVEL " + lesson.level] : []),
    "",
    ...noteSection("WHAT YOU WILL LEARN", lesson.summary),
  ];

  if (lesson.explanation && lesson.explanation.length > 0) {
    parts.push("", ...noteSection("KEY IDEAS", lesson.explanation, ""));
  }

  parts.push(
    "",
    ...noteSection("YOUR TASK", lesson.task),
    "",
    ...noteSection("EXPECTED OUTPUT", lesson.expectedOutput)
  );

  if (lesson.hint && lesson.hint.length > 0) {
    parts.push("", ...noteSection("HINT", lesson.hint));
  }

  parts.push(
    "",
    "    STARTER CODE",
    "",
    ...codeLines
  );

  return parts.join("\n") + "\n";
}

// ── Strip ANSI escape codes ────────────────────────────────────────────────
function stripAnsi(str) {
  // eslint-disable-next-line no-control-regex
  return str.replace(/\x1b\[[0-9;]*[mGKHF]/g, "");
}

// ── DOM refs & editor instance ─────────────────────────────────────────────
var editor;   // set by initApp() once Monaco is ready
var examplesModeBtn = document.getElementById("examplesModeBtn");
var tutorialsModeBtn = document.getElementById("tutorialsModeBtn");
var runBtn     = document.getElementById("runBtn");
var resetLessonBtn = document.getElementById("resetLessonBtn");
var clearEditorBtn = document.getElementById("clearEditorBtn");
var clearBtn   = document.getElementById("clearBtn");
var outputEl   = document.getElementById("output");
var inputEl    = document.getElementById("inputArea");
var statusEl   = document.getElementById("statusBar");
var contentSelect = document.getElementById("contentSelect");
var currentMode = MODES.EXAMPLES;
var lastSelectedIds = {
  [MODES.EXAMPLES]: EXAMPLES[0].id,
  [MODES.TUTORIALS]: TUTORIALS[0].id,
};

function setStatus(msg, kind) {   // kind: "ok" | "error" | ""
  statusEl.textContent = msg;
  statusEl.className = kind || "";
}

function showOutput(text, isError) {
  outputEl.textContent = stripAnsi(text) || (isError ? "" : "(no output)");
  outputEl.className = isError ? "has-error" : "";
}

function clearWorkspaceFeedback() {
  showOutput("", false);
  setStatus("", "");
}

function updateModeUI() {
  var exampleModeActive = currentMode === MODES.EXAMPLES;
  examplesModeBtn.classList.toggle("active", exampleModeActive);
  tutorialsModeBtn.classList.toggle("active", !exampleModeActive);
  examplesModeBtn.setAttribute("aria-pressed", exampleModeActive ? "true" : "false");
  tutorialsModeBtn.setAttribute("aria-pressed", exampleModeActive ? "false" : "true");
  resetLessonBtn.hidden = exampleModeActive;
  contentSelect.title = exampleModeActive ? "Load an example program" : "Load a tutorial lesson";

  if (editor) {
    editor.updateOptions({
      wordWrap: exampleModeActive ? "off" : "on",
      wrappingIndent: exampleModeActive ? "none" : "same",
    });
  }
}

function currentItems() {
  return currentMode === MODES.EXAMPLES ? EXAMPLES : TUTORIALS;
}

function itemForMode(mode, id) {
  const items = mode === MODES.EXAMPLES ? EXAMPLES : TUTORIALS;
  return items.find((item) => item.id === id) || items[0] || null;
}

function loadExample(id) {
  const ex = itemForMode(MODES.EXAMPLES, id);
  if (!ex || !editor) return;
  lastSelectedIds[MODES.EXAMPLES] = ex.id;
  editor.setValue(ex.code);
  inputEl.value = ex.inputs;
  clearWorkspaceFeedback();
}

function loadTutorial(id) {
  const lesson = itemForMode(MODES.TUTORIALS, id);
  if (!lesson || !editor) return;
  lastSelectedIds[MODES.TUTORIALS] = lesson.id;
  editor.setValue(renderTutorialContent(lesson));
  inputEl.value = lesson.inputs || "";
  clearWorkspaceFeedback();
}

function loadSelectedContent(id) {
  if (currentMode === MODES.EXAMPLES) {
    loadExample(id);
  } else {
    loadTutorial(id);
  }
  contentSelect.value = id;
}

function populateContentSelect() {
  const items = currentItems();
  contentSelect.innerHTML = "";

  items.forEach((item) => {
    const opt = document.createElement("option");
    opt.value = item.id;
    opt.textContent = currentMode === MODES.TUTORIALS
      ? String(item.order).padStart(2, "0") + ". " + item.label + (item.level ? " · " + item.level : "")
      : item.label;
    contentSelect.appendChild(opt);
  });

  if (items.length === 0) return;

  const selected = itemForMode(currentMode, lastSelectedIds[currentMode]) || items[0];
  loadSelectedContent(selected.id);
}

function switchMode(mode) {
  if (!MODES[mode.toUpperCase()] || mode === currentMode) return;
  currentMode = mode;
  updateModeUI();
  populateContentSelect();
}

examplesModeBtn.addEventListener("click", () => switchMode(MODES.EXAMPLES));
tutorialsModeBtn.addEventListener("click", () => switchMode(MODES.TUTORIALS));
contentSelect.addEventListener("change", () => loadSelectedContent(contentSelect.value));

resetLessonBtn.addEventListener("click", () => {
  if (currentMode !== MODES.TUTORIALS || !editor) return;
  loadTutorial(lastSelectedIds[MODES.TUTORIALS]);
  editor.focus();
  setStatus("Lesson reset.", "ok");
});

clearEditorBtn.addEventListener("click", () => {
  if (!editor) return;
  if (editor.getValue().length > 0) {
    var confirmed = window.confirm("Clear all code from the editor?");
    if (!confirmed) {
      editor.focus();
      return;
    }
  }
  editor.setValue("");
  editor.focus();
  setStatus("Editor cleared.", "ok");
});

clearBtn.addEventListener("click", () => {
  clearWorkspaceFeedback();
});

// ── initApp: called from the inline <script> in index.html once Monaco is ready
window.initApp = async function (monaco) {
  // Register PLAIN language + theme (defined in plain-lang.js)
  window.registerPlainLanguage(monaco);

  editor = monaco.editor.create(document.getElementById("editorContainer"), {
    value: EXAMPLES[0].code,
    language: "plain",
    theme: "plain-dark",
    autoIndent: "full",
    fontSize: 14,
    fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    automaticLayout: true,
    lineNumbers: "on",
    tabSize: 4,
    insertSpaces: true,
    wordWrap: "off",
    wrappingIndent: "none",
    renderLineHighlight: "line",
  });

  updateModeUI();
  populateContentSelect();

  // ── Load WASM ─────────────────────────────────────────────────────────────
  setStatus("Loading PLAIN runtime…", "");
  try {
    var go = new Go();
    var wasmResult = await WebAssembly.instantiateStreaming(fetch("plain.wasm"), go.importObject);
    go.run(wasmResult.instance);
    runBtn.disabled = false;
    runBtn.textContent = "▶ Run";
    setStatus("Ready.", "ok");
    setTimeout(function () { setStatus("", ""); }, 2000);
  } catch (err) {
    setStatus("Failed to load WASM: " + err.message, "error");
    return;
  }

  // ── Run button ────────────────────────────────────────────────────────────
  runBtn.addEventListener("click", function () {
    var code   = editor.getValue();
    var inputs = inputEl.value;

    runBtn.disabled = true;
    setStatus("Running…", "");

    // setTimeout lets the browser repaint the disabled button before the
    // synchronous WASM call blocks the thread.
    setTimeout(function () {
      try {
        var result = runPlain(code, inputs);
        var hasError = result.error && result.error.length > 0;
        var text = result.output + (hasError ? "\n\nERROR: " + result.error : "");
        showOutput(text, hasError);
        setStatus(hasError ? "Finished with errors." : "Done.", hasError ? "error" : "ok");
      } catch (e) {
        showOutput("Internal error: " + e.message, true);
        setStatus("Internal error.", "error");
      } finally {
        runBtn.disabled = false;
      }
    }, 10);
  });

  // Ctrl/Cmd+Enter runs the program
  editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, function () { runBtn.click(); });
};

