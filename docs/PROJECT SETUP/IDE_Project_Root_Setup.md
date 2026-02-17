# Setting Up Project Root in PLAIN IDE

## Overview

The PLAIN IDE now supports setting a **Project Root** directory for module resolution. This allows you to organize your projects with shared libraries and import them from anywhere in your project structure.

## The Problem This Solves

**Without Project Root:**
```
project/
├── lib/
│   └── utils.plain
└── solutions/
    └── solution1.plain
```

When you run `solutions/solution1.plain` from the IDE, it can only import modules from `solutions/` and its subdirectories. It **cannot** import from `../lib/`.

**With Project Root:**
Set the project root to `/path/to/project`, and now `solutions/solution1.plain` can import from `lib/utils.plain` using:
```plain
use:
    tasks:
        lib.utils.SomeTask
```

## How to Configure

### Step 1: Open Settings

1. Go to **Settings → Preferences** (or press `Ctrl+,`)
2. Click on the **Runtime** tab

### Step 2: Set Project Root

1. In the "Project Root (Module Resolution)" section, click **Browse...**
2. Select your project's root directory
3. Click **OK** or **Apply**

**Example:**
- If your project is at `/home/user/my_project/`
- Set Project Root to: `/home/user/my_project`

### Step 3: Run Your Files

Now when you press **F5** to run any PLAIN file in your project, the IDE will automatically pass the `--project-root` flag to the interpreter.

## Example: Project Euler Setup

For your Project Euler project:

**Project Structure:**
```
/home/chuck/Dropbox/Programming/Languages_and_Code/PLAIN-DB/projects/project_euler/
├── pelib/              # Shared library modules
│   ├── gcd_lcm.plain
│   ├── is_prime.plain
│   └── ...
└── solutions/          # Solution files
    ├── solution1.plain
    ├── solution5.plain
    └── ...
```

**Configuration:**
1. Open Settings → Preferences → Runtime
2. Set Project Root to: `/home/chuck/Dropbox/Programming/Languages_and_Code/PLAIN-DB/projects/project_euler`
3. Click OK

**In your solution files:**
```plain
use:
    tasks:
        pelib.gcd_lcm.GCD
        pelib.gcd_lcm.LCM
        pelib.is_prime.IsPrime

task Main()
    var result = LCM(12, 18)
    display(v"LCM is: {result}")
```

**Running:**
- Open any file in `solutions/`
- Press **F5** to run
- The IDE will automatically use the project root for module resolution
- All imports from `pelib/` will work correctly!

## Benefits

✅ **No file duplication** - Keep one copy of each library  
✅ **Easy maintenance** - Update libraries in one place  
✅ **Standard structure** - Like Python, Node.js, Go, etc.  
✅ **IDE-friendly** - Works when running files directly from the IDE  
✅ **Cascading imports** - Modules can import other modules  

## Verification

When you run a file with Project Root configured, you'll see this in the terminal output:

```
[>] Running: /path/to/project/solutions/solution1.plain
[>] Interpreter: /path/to/plain
[>] Project Root: /path/to/project
--------------------------------------------------
```

The `[>] Project Root:` line confirms that the flag is being used.

## Troubleshooting

### "Module not found" errors

1. Verify the Project Root path is correct
2. Check that your import paths are relative to the project root
3. Make sure the module files exist in the expected locations

### Project Root not showing in output

1. Check that you saved the settings (click OK or Apply)
2. Restart the IDE if needed
3. Verify the path is not empty in Settings → Runtime

## Leave Empty for Default Behavior

If you don't set a Project Root, the IDE will use the **file's directory** as the base for module resolution (the default PLAIN behavior).

