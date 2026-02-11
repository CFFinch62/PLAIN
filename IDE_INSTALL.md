# PLAIN Installation

## Linux Installation (Recommended)

If you downloaded a Linux release package:

### Quick Install

```bash
cd plain-v1.0.0-linux-amd64/
./install.sh
```

This will install:
- **PLAIN interpreter** to `~/.local/share/plain-v1.0.0/plain`
- **PLAIN IDE** (compiled) to `~/.local/share/plain-v1.0.0/bin/plain-ide`
- **Desktop menu entry** for the IDE
- **Symlinks** in `~/.local/bin/` for both `plain` and `plain-ide` commands
- **Documentation** and **examples**

After installation:
- Run PLAIN programs: `plain myprogram.plain`
- Launch IDE from application menu (search for "PLAIN IDE")
- Launch IDE from terminal: `plain-ide`

### Manual Installation

1. Extract the release archive
2. Copy the `plain` binary to your preferred location
3. Optionally copy `bin/plain-ide` for the IDE
4. Add to PATH or create symlinks

### Uninstall

```bash
rm -rf ~/.local/share/plain-v1.0.0
rm ~/.local/bin/plain
rm ~/.local/bin/plain-ide
rm ~/.local/share/applications/plain-ide.desktop
```

## Running from Source

If you prefer to run from source or are on a non-Linux platform:

### PLAIN Interpreter

```bash
go run cmd/plain/main.go myprogram.plain
```

### PLAIN IDE

**Requirements:**
- Python 3.8+
- PyQt6

**Install Dependencies:**

```bash
cd plain_ide/
pip3 install -r requirements.txt
```

**Run:**

```bash
python3 plain_ide/main.py
```

## IDE Features

- Syntax highlighting for PLAIN language
- 50+ bundled color themes (Geany-compatible)
- Integrated terminal
- Debugger support
- File browser
- Find/Replace

## Configuration

Settings and themes are stored in `~/.config/plain_ide/`
