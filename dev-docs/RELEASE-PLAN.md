# PLAIN Release Plan v1.0

## Project Overview

PLAIN consists of two main components:
1. **PLAIN Interpreter** - Go-based language runtime (cmd/plain)
2. **PLAIN IDE** - Python/PyQt6-based integrated development environment

## Release Checklist

### Pre-Release Tasks

#### 1. Code Finalization
- [x] Fix all 10 defects identified during tutorial creation ✅
- [ ] Final code review
- [ ] Update all code comments
- [ ] Run full test suite

#### 2. Documentation Updates
- [ ] Update README.md status (currently says "Phase 2 Complete", should reflect actual state)
- [ ] Verify all user documentation is accurate:
  - [ ] docs/user/USER-GUIDE.md
  - [ ] docs/user/TUTORIAL.md
  - [ ] docs/user/LANGUAGE-REFERENCE.md
  - [ ] docs/user/STDLIB.md
  - [ ] docs/user/CURRICULUM.md
- [ ] Create CHANGELOG.md
- [ ] Write release notes
- [ ] Create installation guide

#### 3. Legal & Licensing
- [ ] Choose and add LICENSE file (MIT, Apache 2.0, GPL, etc.)
- [ ] Add copyright notices
- [ ] Review third-party dependencies and their licenses
- [ ] Update "Author" section in README

#### 4. Version Management
- [ ] Decide on version number (suggest: v1.0.0)
- [ ] Add version to interpreter (`plain --version`)
- [ ] Add version to IDE (About dialog)
- [ ] Tag repository with version

---

## Build & Package Process

### 1. PLAIN Interpreter (Go)

#### Build for Multiple Platforms

```bash
# Linux (64-bit)
GOOS=linux GOARCH=amd64 go build -o releases/plain-linux-amd64 cmd/plain/main.go

# macOS (Intel)
GOOS=darwin GOARCH=amd64 go build -o releases/plain-macos-amd64 cmd/plain/main.go

# macOS (Apple Silicon)
GOOS=darwin GOARCH=arm64 go build -o releases/plain-macos-arm64 cmd/plain/main.go

# Windows (64-bit)
GOOS=windows GOARCH=amd64 go build -o releases/plain-windows-amd64.exe cmd/plain/main.go

# Create universal macOS binary (optional)
lipo -create releases/plain-macos-amd64 releases/plain-macos-arm64 \
     -output releases/plain-macos-universal
```

#### Package Structure for Interpreter

Each platform package should include:
```
plain-v1.0.0-{platform}/
├── plain[.exe]           # Interpreter executable
├── README.md             # Quick start guide
├── LICENSE               # License file
├── examples/             # Example programs
│   ├── hello.plain
│   ├── fibonacci.plain
│   └── ...
└── docs/                 # User documentation
    ├── USER-GUIDE.md
    ├── TUTORIAL.md
    └── LANGUAGE-REFERENCE.md
```

### 2. PLAIN IDE (Python)

#### Packaging Options

**Option A: PyInstaller (Recommended for ease)**
```bash
cd plain_ide

# Install PyInstaller
pip install pyinstaller

# Create standalone executable
# Linux/macOS:
pyinstaller --name="PLAIN-IDE" \
            --windowed \
            --add-data="app:app" \
            --add-data="editor:editor" \
            --add-data="shared:shared" \
            main.py

# Windows:
pyinstaller --name="PLAIN-IDE" ^
            --windowed ^
            --add-data="app;app" ^
            --add-data="editor;editor" ^
            --add-data="shared;shared" ^
            --icon="path/to/icon.ico" ^
            main.py
```

**Option B: Python Package (for developers)**
```bash
# Create setup.py and distribute via PyPI
pip install plain-ide
plain-ide
```

**Option C: Docker Container**
```dockerfile
# For cross-platform consistency
FROM python:3.11
COPY plain_ide /app
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
```

#### Package Structure for IDE

```
plain-ide-v1.0.0-{platform}/
├── PLAIN-IDE[.exe]       # IDE executable
├── README.md             # Installation guide
├── LICENSE
└── resources/            # IDE resources (if not bundled)
    ├── themes/
    └── icons/
```

---

## Distribution Strategy

### 1. GitHub Releases (Primary Distribution)

**Steps:**
1. Create Git tag: `git tag -a v1.0.0 -m "PLAIN v1.0.0 - First Release"`
2. Push tag: `git push origin v1.0.0`
3. Create GitHub Release:
   - Go to https://github.com/yourusername/plain/releases
   - Click "Draft a new release"
   - Choose tag v1.0.0
   - Title: "PLAIN v1.0.0 - First Release"
   - Write release notes
   - Upload binaries:
     - `plain-v1.0.0-linux-amd64.tar.gz`
     - `plain-v1.0.0-macos-universal.tar.gz`
     - `plain-v1.0.0-windows-amd64.zip`
     - `plain-ide-v1.0.0-linux-amd64.tar.gz`
     - `plain-ide-v1.0.0-macos-universal.tar.gz`
     - `plain-ide-v1.0.0-windows-amd64.zip`
   - Publish release

### 2. Website (marketing-website/)

**Deploy marketing website:**
- Update website with v1.0.0 announcement
- Add download links to GitHub releases
- Include quick start guide
- Add screenshots/videos of IDE
- Deploy to:
  - GitHub Pages (free, easy)
  - Netlify (free tier available)
  - Vercel (free tier available)
  - Custom domain

### 3. Package Managers (Optional, Future)

**Homebrew (macOS/Linux):**
```bash
# Create homebrew formula
brew tap yourusername/plain
brew install plain
```

**Chocolatey (Windows):**
```powershell
choco install plain
```

**Snap (Linux):**
```bash
snap install plain
```

---

## Installation Experience

### Interpreter Installation

**Linux/macOS:**
```bash
# Download and extract
wget https://github.com/yourusername/plain/releases/download/v1.0.0/plain-v1.0.0-linux-amd64.tar.gz
tar -xzf plain-v1.0.0-linux-amd64.tar.gz

# Move to system path
sudo mv plain-v1.0.0-linux-amd64/plain /usr/local/bin/

# Verify installation
plain --version
```

**Windows:**
```powershell
# Download ZIP
# Extract to C:\Program Files\PLAIN\
# Add to PATH manually or via installer

# Verify
plain --version
```

### IDE Installation

**All Platforms:**
1. Download IDE package for your platform
2. Extract/Install
3. Run PLAIN-IDE executable
4. IDE should auto-detect interpreter in PATH

**OR use Python:**
```bash
pip install -r plain_ide/requirements.txt
cd plain_ide
python main.py
```

---

## Marketing & Announcement

### 1. Announcement Channels

- [ ] GitHub release announcement
- [ ] Personal website/blog
- [ ] Reddit (r/ProgrammingLanguages, r/programming, r/learnprogramming)
- [ ] Hacker News (Show HN: PLAIN - A programming language designed for clarity)
- [ ] Twitter/X
- [ ] LinkedIn
- [ ] Dev.to or Medium article

### 2. Press Release / Blog Post

**Sample Title:** "Introducing PLAIN: A Programming Language That Speaks Your Language"

**Key Points:**
- Why PLAIN was created
- Target audience (students, educators, marine electronics)
- Key features (natural syntax, built-in IDE, debugging)
- Educational curriculum included
- Open source and free
- Download links

### 3. Demo Materials

- [ ] Create demo video (5-10 minutes)
- [ ] Create screenshots for README
- [ ] GIF demos of IDE features
- [ ] Tutorial video series (optional)

---

## Post-Release

### 1. Community Building

- [ ] Set up GitHub Discussions
- [ ] Create Discord/Slack community (optional)
- [ ] Monitor GitHub issues
- [ ] Respond to feedback

### 2. Maintenance Plan

- [ ] Bug fix release cycle (v1.0.1, v1.0.2, etc.)
- [ ] Feature releases (v1.1.0, v1.2.0, etc.)
- [ ] Security updates
- [ ] Documentation updates

### 3. Metrics to Track

- GitHub stars
- Download counts
- Issue reports
- Community engagement
- Website traffic

---

## Automated Release Script

Create `scripts/build-release.sh`:

```bash
#!/bin/bash
set -e

VERSION="1.0.0"
PLATFORMS=("linux/amd64" "darwin/amd64" "darwin/arm64" "windows/amd64")

echo "Building PLAIN v${VERSION}..."

# Create releases directory
mkdir -p releases

# Build for each platform
for platform in "${PLATFORMS[@]}"; do
    GOOS=${platform%/*}
    GOARCH=${platform#*/}
    OUTPUT="plain-${GOOS}-${GOARCH}"

    if [ $GOOS = "windows" ]; then
        OUTPUT="${OUTPUT}.exe"
    fi

    echo "Building for ${GOOS}/${GOARCH}..."
    GOOS=$GOOS GOARCH=$GOARCH go build -o "releases/${OUTPUT}" cmd/plain/main.go
done

# Package each binary with docs
for platform in "${PLATFORMS[@]}"; do
    GOOS=${platform%/*}
    GOARCH=${platform#*/}
    PACKAGE="plain-v${VERSION}-${GOOS}-${GOARCH}"

    mkdir -p "releases/${PACKAGE}"

    # Copy binary
    if [ $GOOS = "windows" ]; then
        cp "releases/plain-${GOOS}-${GOARCH}.exe" "releases/${PACKAGE}/"
    else
        cp "releases/plain-${GOOS}-${GOARCH}" "releases/${PACKAGE}/plain"
    fi

    # Copy documentation and examples
    cp README.md LICENSE "releases/${PACKAGE}/"
    cp -r examples "releases/${PACKAGE}/"
    cp -r docs/user "releases/${PACKAGE}/docs"

    # Create archive
    cd releases
    if [ $GOOS = "windows" ]; then
        zip -r "${PACKAGE}.zip" "${PACKAGE}"
    else
        tar -czf "${PACKAGE}.tar.gz" "${PACKAGE}"
    fi
    cd ..
done

echo "Release build complete! Files in releases/"
```

---

## Recommended Release Timeline

### Week 1: Preparation
- Day 1-2: Fix remaining critical bugs
- Day 3-4: Update all documentation
- Day 5-7: Build and test on all platforms

### Week 2: Packaging
- Day 1-2: Create release packages
- Day 3-4: Write release notes and announcement
- Day 5: Set up distribution channels

### Week 3: Launch
- Day 1: Create GitHub release
- Day 2: Publish to website
- Day 3-7: Post announcements, respond to feedback

---

## Minimum Viable Release (MVP)

If you want to release quickly, the minimum requirements are:

1. ✅ Working interpreter binary (all platforms)
2. ✅ Working IDE (at least one platform)
3. ✅ README with installation instructions
4. ✅ LICENSE file
5. ✅ Basic documentation (USER-GUIDE.md)
6. ✅ Example programs
7. ✅ GitHub release with binaries

You can expand distribution channels and marketing later.

---

## Success Metrics for v1.0

- [ ] Binaries available for Windows, macOS, Linux
- [ ] IDE available for at least Windows and macOS
- [ ] 100+ GitHub stars in first month
- [ ] Active community engagement (issues, discussions)
- [ ] At least one external contributor
- [ ] Featured on programming language communities

---

## Questions to Answer Before Release

1. **License:** What license will you use? (MIT recommended for max adoption)
2. **Defects:** Release with known bugs 2-5,7 documented, or fix them first?
3. **Name/Branding:** Is "PLAIN" final? Trademark check?
4. **Support:** How will you handle support requests? GitHub issues only?
5. **Roadmap:** What's planned for v1.1, v1.2, v2.0?
