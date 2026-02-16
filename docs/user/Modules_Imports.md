# PLAIN Module & Import System - Complete Analysis

> **A comprehensive reference for how modules, assemblies, and imports work in PLAIN**

---

## Table of Contents

1. [Three-Tier Hierarchy](#three-tier-hierarchy)
2. [Project Structure Example](#project-structure-example)
3. [The `use:` Block](#the-use-block)
4. [Three Import Levels Explained](#three-import-levels-explained)
5. [Common Pitfall: Module Qualified Names](#common-pitfall-module-qualified-names)
6. [Naming Conventions](#naming-conventions)
7. [How Module Resolution Works](#how-module-resolution-works)
8. [How Qualified Name Calls Work](#how-qualified-name-calls-work)
9. [Key Behaviors Verified by Testing](#key-behaviors-verified-by-testing)
10. [Progress Bar Module Import Patterns](#progress-bar-module-import-patterns)
11. [Test Files](#test-files)

---

## Three-Tier Hierarchy

PLAIN organizes code into three levels:

| Level | What It Is | File System Mapping | Example |
|-------|-----------|---------------------|---------|
| **Assembly** | A subdirectory grouping related modules | A folder | `mathlib/`, `io/` |
| **Module** | A single `.plain` file | A file | `helpers.plain`, `mathlib/arithmetic.plain` |
| **Task** | A function or procedure inside a module | A `task` definition | `Add`, `CircleArea` |

---

## Project Structure Example

```
MyProject/
  main.plain              (entry point module - root level)
  helpers.plain            (root-level module - no assembly)
  mathlib/                 (assembly directory)
    arithmetic.plain       (module in mathlib assembly)
    geometry.plain         (module in mathlib assembly)
  textlib/                 (assembly directory)
    formatting.plain       (module in textlib assembly)
```

---

## The `use:` Block

The `use:` block goes at the **top of the file** before any tasks/variables. It has three optional subsections:

```plain
use:
    assemblies:
        mathlib              rem: register assembly for qualified access
    modules:
        helpers              rem: root module - access as helpers.TaskName
        mathlib.geometry     rem: assembly module - access as mathlib.geometry.TaskName
    tasks:
        mathlib.arithmetic.Add    rem: specific task - call as Add() directly
```

---

## Three Import Levels Explained

### 1. `tasks:` - Most Specific (Direct Call, No Prefix)

```plain
use:
    tasks:
        mathlib.arithmetic.Add
        helpers.Greet
```

- **Calling convention:** `Add(10, 5)` - no prefix needed
- **What happens:** The runtime loads `mathlib/arithmetic.plain`, finds the `Add` task, and binds it directly into the current scope
- **Side effect:** The parent module (`mathlib.arithmetic`) also becomes accessible for qualified calls like `mathlib.arithmetic.Multiply()`
- **Naming:** Format is `assembly.module.TaskName` (for assembly modules) or `module.TaskName` (for root modules)

---

### 2. `modules:` - Import Entire Module (Qualified Access)

```plain
use:
    modules:
        helpers               rem: root module
        mathlib.geometry      rem: assembly module
```

- **Calling convention:** `helpers.AddNumbers(3, 4)` or `mathlib.geometry.CircleArea(5)`
- **What happens:** The runtime loads the `.plain` file, evaluates it in an isolated environment, and exports all tasks as a namespace table
- **Root modules:** Just the filename without `.plain` &rarr; `helpers`
- **Assembly modules:** `assembly.module` notation &rarr; `mathlib.geometry`

---

### 3. `assemblies:` - Declarative Marker (No Code Loading)

```plain
use:
    assemblies:
        mathlib
```

- **What happens:** Registers the assembly name as a marker string in the environment. Does **NOT** load any files, evaluate any code, or make any tasks callable.
- **Access:** Modules within must still be imported via `modules:` or `tasks:` for actual use.
- **Purpose:** Declares dependency on the assembly for documentation and future tooling.

#### What `assemblies:` actually does at runtime

The entire runtime implementation of `assemblies:` is this:

```go
for _, asmExpr := range stmt.Assemblies {
    asmPath := e.dotExpressionToPath(asmExpr)
    asmKey := e.pathToModuleKey(asmPath)
    if _, ok := env.Get(asmKey); !ok {
        env.Define(asmKey, NewString("assembly:"+asmKey))
    }
}
```

It registers a string value `"assembly:mathlib"` into the environment under the key `mathlib`. That is **all** it does. No files are read. No modules are parsed. No tasks become available.

Compare this to `modules:`, which calls `loadModule()` - a function that reads files from disk, parses them, creates isolated environments, evaluates all the code, and exports task namespaces. Or `tasks:`, which does all of that plus extracts specific tasks for direct binding.

#### What `assemblies:` provides

1. **Self-documenting code** - Reading the `use:` block shows at a glance which major subsystems the file depends on, separate from specific modules or tasks
2. **Prevents "undefined" errors on the name** - If any code checks whether `mathlib` exists in the environment, it finds the marker string instead of an error
3. **Future-proofing** - The spec reserves this for IDE features like assembly-level dependency graphs, dead code detection, and project structure validation

#### What `assemblies:` does NOT do

It does **not** make any tasks callable. This will fail:

```plain
use:
    assemblies:
        pblib

task Main()
    pblib.pb.ProgBar()    rem: RUNTIME ERROR
    rem: pblib is just the string "assembly:pblib", not a module namespace
    rem: Dot access on a string causes: "property access not supported for STRING"
```

#### Processing order

The `use:` block sections are processed in this order:

1. **`tasks:`** first - loads modules, extracts and binds specific tasks
2. **`modules:`** second - loads modules as namespace tables
3. **`assemblies:`** last - registers marker strings

Because `assemblies:` runs last and has a guard (`if _, ok := env.Get(asmKey); !ok`), if a `modules:` or `tasks:` import already registered the same name (which happens automatically via intermediate path registration), the `assemblies:` line becomes a **complete no-op**.

#### When to use `assemblies:`

In practice, `assemblies:` is useful as a **documentation convention** in your `use:` block. It communicates intent to readers:

```plain
use:
    assemblies:
        io                   rem: tells the reader: "we use the io subsystem broadly"

    modules:
        io.files             rem: this is what actually loads the code

    tasks:
        io.network.Download  rem: this is what actually loads the code
```

For getting actual work done, always use `modules:` or `tasks:`.

---

## Common Pitfall: Module Qualified Names

A frequent source of confusion is how the **call prefix** relates to the **import path**. The rule is simple but easy to miss:

> **The call prefix always matches the exact import path. There is no shorthand and no aliasing.**

### Example: Importing from a subfolder

Given this structure:

```
myproject/
  main.plain
  pblib/
    pb.plain          (contains task ProgBar)
```

Here is what works and what does **not** work:

#### This does NOT work

```plain
use:
    modules:
        pblib.pb

task Main()
    pb.ProgBar()          rem: WRONG - "pb" is not defined
```

When you import `pblib.pb`, the module is registered under its **full qualified name** `pblib.pb`, not just `pb`. PLAIN has no import aliasing.

#### These DO work

**Option 1: Module import with full qualified call**

```plain
use:
    modules:
        pblib.pb

task Main()
    pblib.pb.ProgBar()    rem: CORRECT - full path matches the import
```

**Option 2: Task import for direct call (recommended)**

```plain
use:
    tasks:
        pblib.pb.ProgBar

task Main()
    ProgBar()             rem: CORRECT - task imports have no prefix
```

**Option 3: Move the file to the root for a shorter prefix**

```
myproject/
  main.plain
  pb.plain                (moved out of pblib/)
```

```plain
use:
    modules:
        pb

task Main()
    pb.ProgBar()          rem: CORRECT - root module, short prefix
```

---

## Naming Conventions

| Element | Convention | Examples |
|---------|-----------|---------|
| **Assembly names** | lowercase, short | `mathlib`, `io`, `data`, `textlib` |
| **Module filenames** | lowercase, descriptive | `arithmetic.plain`, `geometry.plain`, `formatting.plain` |
| **Task names** | PascalCase | `Add`, `CircleArea`, `FormatDate` |
| **Variable prefixes** | Type prefix + camelCase | `intCount`, `strName`, `fltPrice` |
| **Constants** | UPPER_SNAKE_CASE | `PI`, `MAX_SIZE` |

---

## How Module Resolution Works

### Base Directory

By default, the `baseDir` is set to the directory containing the main `.plain` file being run:

```go
baseDir := filepath.Dir(filename)  // directory of the .plain file being run
```

However, you can override this with the `--project-root` flag to use a different base directory for module resolution.

### Path Resolution Rules

1. `baseDir` is set to:
   - The directory specified by `--project-root` flag (if provided), OR
   - The directory containing the main `.plain` file (default)
2. Module path `["mathlib", "geometry"]` resolves to `<baseDir>/mathlib/geometry.plain`
3. Root module `["helpers"]` resolves to `<baseDir>/helpers.plain`
4. File must exist or you get: `"module not found: mathlib.geometry"`

### Using `--project-root` for Parent Directory Imports

**The Problem:** By default, PLAIN can only import modules from the file's directory and subdirectories. It cannot import from parent directories.

**The Solution:** Use the `--project-root` flag to set a common base directory for all imports.

**Example:**

```
my_project/
├── lib/
│   ├── utils.plain
│   └── helpers.plain
└── solutions/
    ├── solution1.plain
    └── solution2.plain
```

**Without `--project-root`:**
```bash
cd my_project/solutions
plain solution1.plain
# Can only import from solutions/ and subdirectories
# Cannot import from ../lib/
```

**With `--project-root`:**
```bash
cd my_project
plain --project-root=. solutions/solution1.plain
# Can import from lib/, solutions/, and any subdirectory
```

**In solution1.plain:**
```plain
use:
    tasks:
        lib.utils.SomeTask    # Works with --project-root!
```

**IDE Configuration:** The PLAIN IDE can be configured to automatically use `--project-root`. See [IDE_Project_Root_Setup.md](IDE_Project_Root_Setup.md) for instructions.

**See also:** [Project_Root_Flag.md](Project_Root_Flag.md) for complete documentation.

### Runtime Behavior

- **Caching:** A `loadedModules` map prevents loading the same module twice
- **Isolation:** Each module gets its own environment - module variables are **NOT** shared
- **Export:** All symbols from the module's store become a namespace table
- **Intermediate paths:** Loading `mathlib.geometry` also registers `mathlib` as an empty table for path traversal

---

## How Qualified Name Calls Work

When you write `mathlib.geometry.CircleArea(5)`:

1. The parser creates nested `DotExpression` nodes: `(mathlib.geometry).CircleArea`
2. `evalDotExpression` first converts to qualified string `"mathlib.geometry.CircleArea"`
3. Looks up `"mathlib.geometry.CircleArea"` in environment - not found
4. Evaluates left side `mathlib.geometry` as a qualified lookup - finds the module namespace table
5. Accesses `"CircleArea"` as a table key - finds the function
6. Function is called with the argument

---

## Key Behaviors Verified by Testing

All 32 tests pass, confirming:

| Behavior | Documentation Says | Implementation Does | Status |
|----------|-------------------|--------------------|----|
| Task import &rarr; direct call | "callable directly without prefix" | `Add(10,5)` works | **MATCH** |
| Module import &rarr; qualified call | "accessible via module.TaskName" | `helpers.AddNumbers(3,4)` works | **MATCH** |
| Assembly.module qualified | "assembly.module notation" | `mathlib.geometry.CircleArea(1)` works | **MATCH** |
| Task import enables parent module | "makes parent module available" | `mathlib.arithmetic.Multiply()` works after importing only `Add` | **MATCH** |
| Module isolation | "NOT global" | Module vars not directly accessible from other modules | **MATCH** |
| Error propagation across modules | "abort propagates up call stack" | `attempt/handle` catches `abort` from imported module | **MATCH** |
| Return types preserved | Implicit | `is_int()`, `is_float()`, `is_string()` all correct | **MATCH** |
| Multiple tasks from same module | Implicit | All three (`Add`, `Subtract`, `Square`) work | **MATCH** |
| Cross-assembly calls | Implicit | Nesting calls from different assemblies works | **MATCH** |
| Module constants accessible | Implicit | `GetPi()` returns the module-level `fxd PI` value | **MATCH** |

---

## Progress Bar Module Import Patterns

### If `progbar.plain` is in the project root

**Task-level import (direct call):**

```plain
use:
    tasks:
        progbar.ProgBar

task Main()
    ProgBar(100)
```

**Module-level import (qualified call):**

```plain
use:
    modules:
        progbar

task Main()
    progbar.ProgBar(100)
```

### If `progbar.plain` is inside a `utils/` assembly

```plain
use:
    tasks:
        utils.progbar.ProgBar

task Main()
    ProgBar(100)
```

---

## Test Files

The comprehensive test project is at `examples/tests/module_test/` with this structure:

```
module_test/
  main.plain              (32-test runner)
  helpers.plain            (root-level module)
  mathlib/
    arithmetic.plain       (Add, Subtract, Multiply, Divide, Square)
    geometry.plain         (CircleArea, RectangleArea, TriangleArea, GetPi)
  textlib/
    formatting.plain       (Banner, Repeat, PadRight, Capitalize)
```

**Run it with:**

```bash
./plain examples/tests/module_test/main.plain
```

---

*This analysis was generated by examining all documentation in `dev-docs/` and `docs/`, the interpreter source code in `internal/`, and verified by running 32 automated tests against the live interpreter.*
