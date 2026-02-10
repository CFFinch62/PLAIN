# PLAIN v1.0.0 Beta 1

🔒 **Private Beta Release** - For invited testers only

## What's New

First private beta release of PLAIN with all core features complete:

- ✅ **Complete Language Implementation** - All 10 defects from testing fixed
- ✅ **Full-Featured IDE** - Integrated development environment with debugging
- ✅ **Comprehensive Documentation** - User guide, language reference, tutorial, and curriculum
- ✅ **Example Programs** - Sample code to get started quickly

## What's Included

Each platform package contains:

- **PLAIN Interpreter** - Cross-platform binary for running PLAIN programs
- **PLAIN IDE** - Full-featured IDE (Python source, requires Python 3.8+)
- **Documentation** - Complete user documentation and language reference
- **Examples** - Tutorial examples and sample programs
- **Installation Guide** - Step-by-step setup instructions

## Supported Platforms

| Platform | Architecture | Package |
|----------|-------------|---------|
| **Linux** | x64 | `plain-v1.0.0-beta1-linux-amd64.tar.gz` |
| **Linux** | ARM64 | `plain-v1.0.0-beta1-linux-arm64.tar.gz` |
| **macOS** | Intel (x64) | `plain-v1.0.0-beta1-darwin-amd64.tar.gz` |
| **macOS** | Apple Silicon (ARM64) | `plain-v1.0.0-beta1-darwin-arm64.tar.gz` |
| **Windows** | x64 | `plain-v1.0.0-beta1-windows-amd64.zip` |

## Installation

### Quick Start

1. Download the appropriate package for your platform (see table above)
2. Extract the archive
3. See `INSTALLATION.md` inside the package for detailed setup instructions

### Running the Interpreter

```bash
# After extraction
./plain yourfile.plain          # Linux/macOS
plain.exe yourfile.plain        # Windows
```

### Running the IDE

```bash
# After extracting and installing Python dependencies
pip3 install -r plain_ide/requirements.txt
python3 plain_ide/main.py
```

Full installation instructions are included in each package.

## System Requirements

**Interpreter:**

- Linux: glibc 2.31+ (Ubuntu 20.04+)
- macOS: 10.15 Catalina or later
- Windows: Windows 10 or later

**IDE (Optional):**

- Python 3.8 or higher
- PyQt6 and PyQt6-QScintilla (auto-installed via pip)

## Documentation

Inside each package you'll find:

- **INSTALLATION.md** - Complete installation guide
- **docs/TUTORIAL.md** - Step-by-step tutorial
- **docs/LANGUAGE-REFERENCE.md** - Complete language specification
- **docs/USER-GUIDE.md** - User guide and best practices
- **docs/STDLIB.md** - Standard library reference
- **docs/CURRICULUM.md** - Teaching curriculum
- **plain_ide/README.md** - IDE documentation and keyboard shortcuts

## Known Limitations

This is a beta release. While all major features are implemented and tested, you may encounter minor issues. Please report any bugs via GitHub Issues.

## Getting Help

- 📖 Read the documentation in the `docs/` folder
- 🐛 Report bugs via [GitHub Issues](https://github.com/CFFinch62/plain-language/issues)
- 📧 Email: [info@fragillidaesoftware.com](mailto:info@fragillidaesoftware.com)

## License

This is confidential beta software provided for evaluation purposes only. See the LICENSE file in each package for complete terms.

**By downloading this software, you agree to:**

- Keep the software confidential
- Not distribute to others without permission
- Provide feedback and bug reports
- Use for evaluation purposes only (not production)

For commercial licensing inquiries: [info@fragillidaesoftware.com](mailto:info@fragillidaesoftware.com)

---

**Thank you for participating in the PLAIN beta program!**

Your feedback is invaluable in making PLAIN better for everyone.

© 2026 Fragillidae Software. All rights reserved.