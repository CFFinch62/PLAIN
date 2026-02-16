# Using `--project-root` for Module Resolution

## The Problem

By default, when you run a PLAIN file, the interpreter sets the module resolution base directory to the **directory containing the file being run**. This means:

```
project/
├── lib/
│   └── utils.plain
└── solutions/
    └── solution1.plain
```

If you run `solutions/solution1.plain` directly, it can only import modules from:
- `solutions/` (same directory)
- `solutions/subfolder/` (subdirectories)

It **cannot** import from `../lib/` (parent directory).

## The Solution: `--project-root`

The `--project-root` flag tells PLAIN where your project root is, allowing all files to import from a common base directory.

### Syntax

```bash
plain --project-root=<directory> <file.plain>
# or
plain --project-root <directory> <file.plain>
```

### Example

**Project Structure:**
```
project_euler/
├── pelib/              # Shared library modules
│   ├── gcd_lcm.plain
│   ├── is_prime.plain
│   └── ...
└── solutions/          # Solution files
    ├── solution1.plain
    ├── solution5.plain
    └── ...
```

**In `solutions/solution5.plain`:**
```plain
use:
    tasks:
        pelib.gcd_lcm.LCM    # Import from ../pelib/gcd_lcm.plain
```

**Running from command line:**
```bash
cd /path/to/project_euler
plain --project-root=. solutions/solution5.plain
```

**Or with absolute path:**
```bash
plain --project-root=/path/to/project_euler /path/to/project_euler/solutions/solution5.plain
```

## IDE Integration

### Using the PLAIN IDE

The PLAIN IDE has built-in support for the `--project-root` flag. You can configure it through the settings:

**Steps:**
1. Open **Settings → Preferences** (`Ctrl+,`)
2. Go to the **Runtime** tab
3. In "Project Root (Module Resolution)", click **Browse...**
4. Select your project root directory (e.g., `/path/to/project_euler`)
5. Click **OK**

Now when you press `F5` to run any file, the IDE automatically passes `--project-root` to the interpreter.

**Verification:** When you run a file, you'll see this in the terminal:
```
[>] Running: /path/to/project/solutions/solution1.plain
[>] Interpreter: /path/to/plain
[>] Project Root: /path/to/project
--------------------------------------------------
```

**See:** [IDE_Project_Root_Setup.md](IDE_Project_Root_Setup.md) for detailed instructions.

### Using External IDEs (VS Code, Sublime, etc.)

When configuring an external IDE to run PLAIN files, add the `--project-root` flag to the command:

**Example for VS Code (tasks.json):**
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Run PLAIN",
      "type": "shell",
      "command": "/path/to/plain",
      "args": [
        "--project-root=${workspaceFolder}",
        "${file}"
      ],
      "group": {
        "kind": "build",
        "isDefault": true
      },
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    }
  ]
}
```

**Example for Sublime Text (build system):**
```json
{
  "cmd": ["/path/to/plain", "--project-root=${folder}", "$file"],
  "file_regex": "^(..[^:]*):([0-9]+):?([0-9]+)?:? (.*)$",
  "working_dir": "${folder}",
  "selector": "source.plain"
}
```

**Generic IDE Configuration:**
```
Command: /path/to/plain
Arguments: --project-root=/path/to/project ${file}
```

This allows you to:
1. Keep ONE copy of shared libraries in a central location
2. Run files from anywhere in your project
3. Import from the project root instead of just the file's directory

## Benefits

✅ **No file duplication** - One copy of each library module  
✅ **Easier maintenance** - Update libraries in one place  
✅ **Standard project structure** - Like Python, Node.js, Go, etc.  
✅ **IDE-friendly** - Works when running files from the IDE  

## Without `--project-root`

If you don't use `--project-root`, you have two options:

1. **Run from project root:**
   ```bash
   cd /path/to/project_euler
   plain solutions/solution5.plain
   ```
   This works from command line but may not work in IDEs.

2. **Restructure your project** to avoid parent directory imports (not recommended).

## Cascading Imports

The `--project-root` flag works perfectly with cascading imports:

```plain
# main.plain
use:
    tasks:
        lib.lcm.LCM

# lib/lcm.plain
use:
    tasks:
        lib.gcd.GCD    # This works!

task LCM using (a, b)
    deliver a * b / GCD(a, b)
```

When you run with `--project-root`, all modules resolve from the same base, so cascading imports work correctly.

