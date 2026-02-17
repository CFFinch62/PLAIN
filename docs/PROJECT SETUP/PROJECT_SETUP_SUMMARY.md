# PLAIN Project Setup Summary

> **Quick reference for setting up PLAIN projects with module imports**

---

## Overview

PLAIN supports two ways to organize projects with shared libraries:

1. **Default behavior** - Modules resolve from the file's directory
2. **Project root mode** - Modules resolve from a configured base directory

---

## When to Use Project Root

Use `--project-root` when your project has this structure:

```
my_project/
├── lib/              # Shared libraries
│   ├── utils.plain
│   └── helpers.plain
└── solutions/        # Your code
    ├── solution1.plain
    └── solution2.plain
```

**Without project root:** Files in `solutions/` cannot import from `../lib/`

**With project root:** Files anywhere can import from `lib/`

---

## Setup Options

### Option 1: Using PLAIN IDE (Recommended)

**One-time setup:**
1. Open PLAIN IDE
2. Go to **Settings → Preferences** (`Ctrl+,`)
3. Click **Runtime** tab
4. In "Project Root", click **Browse...** and select `/path/to/my_project`
5. Click **OK**

**Usage:**
- Open any file in your project
- Press `F5` to run
- Imports work automatically!

**Documentation:** [IDE_Project_Root_Setup.md](IDE_Project_Root_Setup.md)

---

### Option 2: Command Line

**Every time you run:**
```bash
cd /path/to/my_project
plain --project-root=. solutions/solution1.plain
```

**Documentation:** [Project_Root_Flag.md](Project_Root_Flag.md)

---

### Option 3: External IDE (VS Code, Sublime, etc.)

**One-time setup in VS Code:**

Create `.vscode/tasks.json`:
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Run PLAIN",
      "type": "shell",
      "command": "/path/to/plain",
      "args": ["--project-root=${workspaceFolder}", "${file}"],
      "group": {"kind": "build", "isDefault": true}
    }
  ]
}
```

**Usage:**
- Press `Ctrl+Shift+B` to run current file

**Documentation:** [Project_Root_Flag.md](Project_Root_Flag.md#using-external-ides-vs-code-sublime-etc)

---

## Writing Import Statements

Once project root is configured, use imports relative to the project root:

```plain
use:
    tasks:
        lib.utils.FormatDate
        lib.helpers.ValidateInput
    modules:
        lib.math

task Main()
    var date = FormatDate("2024-01-15")
    display(date)
    
    var result = lib.math.Add(10, 20)
    display(v"Result: {result}")
```

---

## Verification

### PLAIN IDE
When you run a file, check the terminal output:
```
[>] Running: /path/to/project/solutions/solution1.plain
[>] Interpreter: /path/to/plain
[>] Project Root: /path/to/project    ← Should show your project root
--------------------------------------------------
```

### Command Line
If imports work without errors, it's configured correctly!

---

## Troubleshooting

### "Module not found" errors

**Check:**
1. Project root path is correct
2. Module files exist in expected locations
3. Import paths are relative to project root (not file's directory)

**Example:**
```
Project root: /home/user/my_project
File location: /home/user/my_project/solutions/solution1.plain
Module location: /home/user/my_project/lib/utils.plain

✅ Correct import: lib.utils
❌ Wrong import: ../lib/utils
```

### IDE not using project root

1. Verify setting is saved (check Settings → Runtime)
2. Restart the IDE
3. Check terminal output for `[>] Project Root:` line

---

## Complete Documentation

- **[USER-GUIDE.md](USER-GUIDE.md)** - Complete PLAIN user guide
- **[Modules_Imports.md](Modules_Imports.md)** - How the module system works
- **[Project_Root_Flag.md](Project_Root_Flag.md)** - Command-line flag documentation
- **[IDE_Project_Root_Setup.md](IDE_Project_Root_Setup.md)** - IDE setup guide

---

## Quick Start Example

**1. Create project structure:**
```bash
mkdir -p my_project/lib my_project/solutions
```

**2. Create a library (`my_project/lib/greet.plain`):**
```plain
task SayHello with (name)
    display(v"Hello, {name}!")
```

**3. Create main file (`my_project/solutions/main.plain`):**
```plain
use:
    tasks:
        lib.greet.SayHello

task Main()
    SayHello("World")
```

**4. Configure and run:**

**PLAIN IDE:**
- Settings → Runtime → Project Root → Browse → Select `my_project` → OK
- Open `solutions/main.plain`
- Press F5

**Command line:**
```bash
cd my_project
plain --project-root=. solutions/main.plain
```

**Output:**
```
Hello, World!
```

Success! 🎉

