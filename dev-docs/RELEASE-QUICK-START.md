# Release Quick Start Guide

Fast track to creating releases for testers and reviewers.

---

## Option 1: Simple Archives (Fastest - Use This First!)

This is what you should do **right now** for your initial beta testers.

### On Linux (Your Current Machine)

```bash
# Build everything
./scripts/build-release.sh 1.0.0-beta1

# Result: releases/plain-v1.0.0-beta1-linux-amd64.tar.gz
```

### On macOS (Need Access to Mac)

```bash
# Intel Mac
./scripts/build-release.sh 1.0.0-beta1

# Apple Silicon Mac  
GOARCH=arm64 ./scripts/build-release.sh 1.0.0-beta1

# Results:
# releases/plain-v1.0.0-beta1-darwin-amd64.tar.gz
# releases/plain-v1.0.0-beta1-darwin-arm64.tar.gz
```

### On Windows (Need Access to Windows)

```cmd
scripts\build-release.bat 1.0.0-beta1

REM Result: releases\plain-v1.0.0-beta1-windows-amd64.zip
```

### Create GitHub Release

1. Create and push tag:
   ```bash
   git tag v1.0.0-beta1
   git push origin v1.0.0-beta1
   ```

2. Go to GitHub → Releases → "Draft a new release"

3. Upload all archives:
   - `plain-v1.0.0-beta1-linux-amd64.tar.gz`
   - `plain-v1.0.0-beta1-darwin-amd64.tar.gz`
   - `plain-v1.0.0-beta1-darwin-arm64.tar.gz`
   - `plain-v1.0.0-beta1-windows-amd64.zip`

4. Add release notes (see template below)

5. Check "This is a pre-release" for beta

6. Publish!

**Done! Testers can now download and follow INSTALLATION.md**

---

## Option 2: Professional Installers (Later)

Once you have access to all platforms and want polished installers:

### Linux DEB Package

```bash
# First build the release
./scripts/build-release.sh 1.0.0

# Then create DEB
./scripts/build-deb.sh 1.0.0

# Result: releases/plain_1.0.0_amd64.deb
```

**Install:**
```bash
sudo dpkg -i plain_1.0.0_amd64.deb
sudo apt-get install -f  # Fix dependencies
```

### macOS DMG

```bash
# First build the release
./scripts/build-release.sh 1.0.0

# Then create DMG
./scripts/build-dmg.sh 1.0.0 amd64  # Intel
./scripts/build-dmg.sh 1.0.0 arm64  # Apple Silicon

# Results:
# releases/PLAIN-v1.0.0-Intel.dmg
# releases/PLAIN-v1.0.0-AppleSilicon.dmg
```

**Install:** Double-click DMG, drag to Applications

### Windows Installer

```cmd
REM First build the release
scripts\build-release.bat 1.0.0

REM Then create installer (requires Inno Setup installed)
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" scripts\plain-installer.iss

REM Result: releases\PLAIN-Setup-v1.0.0.exe
```

**Install:** Double-click the installer

---

## Release Notes Template

```markdown
# PLAIN v1.0.0-beta1

First beta release of PLAIN programming language!

## What's Included

- **PLAIN Interpreter** - Run PLAIN programs from command line
- **PLAIN IDE** - Full-featured development environment
- **Documentation** - Complete language reference and tutorial
- **Examples** - 20+ example programs to learn from

## Installation

Download the appropriate file for your platform:

- **Linux:** `plain-v1.0.0-beta1-linux-amd64.tar.gz`
- **macOS (Intel):** `plain-v1.0.0-beta1-darwin-amd64.tar.gz`
- **macOS (Apple Silicon):** `plain-v1.0.0-beta1-darwin-arm64.tar.gz`
- **Windows:** `plain-v1.0.0-beta1-windows-amd64.zip`

See [INSTALLATION.md](INSTALLATION.md) for detailed setup instructions.

## Quick Start

```bash
# Extract the archive
tar -xzf plain-v1.0.0-beta1-*.tar.gz  # Linux/macOS
# or unzip on Windows

# Run the interpreter
./plain examples/tutorial/lesson_01_hello.plain

# Launch the IDE
python3 plain_ide/main.py
```

## Known Issues

- [ ] List any known bugs or limitations
- [ ] Mention platform-specific quirks

## Feedback

Please report bugs and suggestions:
- GitHub Issues: https://github.com/CFFinch62/plain-language/issues
- Email: info@fragillidaesoftware.com

## License

Proprietary - See LICENSE file

---

**Thank you for testing PLAIN!** 🎉
```

---

## Cross-Platform Build Strategy

### If You Only Have Linux

**Option A: Use GitHub Actions (Automated)**
- Set up the workflow in `.github/workflows/release.yml`
- Push a tag, GitHub builds all platforms automatically
- See `CROSS-PLATFORM-RELEASE-GUIDE.md` for details

**Option B: Use Virtual Machines**
- VirtualBox/VMware for Windows
- Cloud Mac rental (MacStadium, AWS EC2 Mac)
- Build manually on each VM

**Option C: Ask Testers to Build**
- Share source code
- Provide build instructions
- They build on their own platform

### Recommended Approach for Beta

1. **Week 1:** Release Linux build only (you can do this now!)
2. **Week 2:** Get access to Mac/Windows, build those
3. **Week 3:** Set up GitHub Actions for automation
4. **Week 4:** Create professional installers

**Don't let perfect be the enemy of good!** Start with simple archives.

---

## Checklist Before Release

- [ ] All tests pass: `go test ./...`
- [ ] IDE launches and runs programs
- [ ] Documentation is up to date
- [ ] Examples all work
- [ ] LICENSE file is included
- [ ] README.md has correct version number
- [ ] INSTALLATION.md is clear and tested
- [ ] Git tag created
- [ ] Release notes written

---

## After Release

1. **Announce** to your testers
2. **Monitor** GitHub issues for bug reports
3. **Respond** to feedback quickly
4. **Plan** next release based on feedback

---

## Quick Commands Reference

```bash
# Build current platform
./scripts/build-release.sh 1.0.0-beta1

# Create DEB (Linux only)
./scripts/build-deb.sh 1.0.0-beta1

# Create DMG (macOS only)
./scripts/build-dmg.sh 1.0.0-beta1 amd64

# Tag and push
git tag v1.0.0-beta1
git push origin v1.0.0-beta1

# Test the build
cd releases/plain-v1.0.0-beta1-*/
./plain examples/tutorial/lesson_01_hello.plain
python3 plain_ide/main.py
```

---

**You're ready to release! Start with Option 1 (simple archives) today.**

