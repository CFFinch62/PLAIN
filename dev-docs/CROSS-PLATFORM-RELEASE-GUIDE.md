# Cross-Platform Release & Installer Guide

Complete guide for building and distributing PLAIN across Windows, macOS, and Linux with professional installers.

---

## Table of Contents

1. [Current Build System](#current-build-system)
2. [Platform-Specific Builds](#platform-specific-builds)
3. [Installer Creation](#installer-creation)
4. [Code Signing](#code-signing)
5. [Distribution Strategy](#distribution-strategy)
6. [Automated Release Workflow](#automated-release-workflow)

---

## Current Build System

### What We Have

✅ **Build Scripts:**
- `scripts/build-release.sh` - Linux/macOS build script
- `scripts/build-release.bat` - Windows build script
- `plain_ide.spec` - PyInstaller configuration for IDE

✅ **Components:**
- Go-based interpreter (cross-compiles easily)
- Python-based IDE (PyInstaller for standalone executables)

### Current Limitations

❌ No cross-compilation setup (must build on each platform)
❌ No installer packages (just ZIP/TAR archives)
❌ No code signing
❌ Manual build process

---

## Platform-Specific Builds

### 1. Linux

**Target Distributions:**
- Ubuntu/Debian (`.deb` package)
- Fedora/RHEL (`.rpm` package)
- Generic (`.tar.gz` archive) ✅ Already working

**Build Requirements:**
- Go 1.21+
- Python 3.8+
- PyInstaller
- `dpkg-deb` (for .deb)
- `rpmbuild` (for .rpm)

**Build Command:**
```bash
./scripts/build-release.sh 1.0.0
```

**Output:**
- `releases/plain-v1.0.0-linux-amd64.tar.gz` ✅
- `releases/plain-v1.0.0-linux-amd64.deb` (to be created)
- `releases/plain-v1.0.0-linux-amd64.rpm` (to be created)

### 2. macOS

**Target Architectures:**
- Intel (x86_64/amd64)
- Apple Silicon (arm64)

**Build Requirements:**
- Go 1.21+
- Python 3.8+
- PyInstaller
- Xcode Command Line Tools
- `create-dmg` (for DMG installer)
- Apple Developer Account (for code signing)

**Build Command:**
```bash
# Intel
GOARCH=amd64 ./scripts/build-release.sh 1.0.0

# Apple Silicon
GOARCH=arm64 ./scripts/build-release.sh 1.0.0
```

**Output:**
- `releases/plain-v1.0.0-darwin-amd64.tar.gz`
- `releases/plain-v1.0.0-darwin-arm64.tar.gz`
- `releases/PLAIN-v1.0.0-Intel.dmg` (to be created)
- `releases/PLAIN-v1.0.0-AppleSilicon.dmg` (to be created)

### 3. Windows

**Target Architectures:**
- x64 (amd64)

**Build Requirements:**
- Go 1.21+
- Python 3.8+
- PyInstaller
- Inno Setup (for installer)
- Optional: Code signing certificate

**Build Command:**
```cmd
scripts\build-release.bat 1.0.0
```

**Output:**
- `releases/plain-v1.0.0-windows-amd64.zip` ✅
- `releases/PLAIN-Setup-v1.0.0.exe` (to be created)

---

## Installer Creation

### Linux: DEB Package

**Tool:** `dpkg-deb`

**Structure:**
```
plain_1.0.0_amd64/
├── DEBIAN/
│   ├── control
│   ├── postinst
│   └── prerm
├── usr/
│   ├── bin/
│   │   ├── plain
│   │   └── plain-ide
│   ├── share/
│   │   ├── applications/
│   │   │   └── plain-ide.desktop
│   │   ├── icons/
│   │   │   └── hicolor/256x256/apps/plain.png
│   │   └── plain/
│   │       ├── docs/
│   │       └── examples/
```

**Create Script:** `scripts/build-deb.sh` (to be created)

### Linux: RPM Package

**Tool:** `rpmbuild`

**Spec File:** `scripts/plain.spec` (to be created)

**Create Script:** `scripts/build-rpm.sh` (to be created)

### macOS: DMG Installer

**Tool:** `create-dmg` or manual `hdiutil`

**Contents:**
- PLAIN IDE.app (application bundle)
- plain (command-line tool installer script)
- README.txt
- Applications folder symlink (for drag-and-drop install)

**Create Script:** `scripts/build-dmg.sh` (to be created)

**Application Bundle Structure:**
```
PLAIN IDE.app/
├── Contents/
│   ├── Info.plist
│   ├── MacOS/
│   │   ├── plain-ide (executable)
│   │   └── plain (interpreter)
│   ├── Resources/
│   │   ├── icon.icns
│   │   ├── docs/
│   │   └── examples/
```

### Windows: Inno Setup Installer

**Tool:** Inno Setup

**Script:** `scripts/plain-installer.iss` (to be created)

**Features:**
- Install to Program Files
- Add to PATH option
- Create Start Menu shortcuts
- Create Desktop shortcut option
- Associate .plain files with IDE
- Uninstaller

**Create Command:**
```cmd
iscc scripts\plain-installer.iss
```

---

## Code Signing

### Why Code Sign?

- **Windows:** Prevents SmartScreen warnings
- **macOS:** Required for Gatekeeper (macOS 10.15+)
- **Linux:** Not required but adds trust

### Windows Code Signing

**Requirements:**
- Code signing certificate (from DigiCert, Sectigo, etc.)
- `signtool.exe` (Windows SDK)

**Cost:** ~$200-400/year

**Process:**
```cmd
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com plain.exe
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com plain-ide.exe
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com PLAIN-Setup.exe
```

### macOS Code Signing

**Requirements:**
- Apple Developer Account ($99/year)
- Developer ID Application certificate
- `codesign` tool (included with Xcode)

**Process:**
```bash
# Sign the interpreter
codesign --force --sign "Developer ID Application: Your Name" plain

# Sign the app bundle
codesign --force --deep --sign "Developer ID Application: Your Name" "PLAIN IDE.app"

# Notarize (required for macOS 10.15+)
xcrun notarytool submit PLAIN-v1.0.0.dmg --apple-id your@email.com --password app-specific-password --team-id TEAMID
```

### Linux Code Signing

**Optional:** Use GPG to sign packages

```bash
gpg --detach-sign --armor plain-v1.0.0-linux-amd64.tar.gz
```

---

## Distribution Strategy

### Option 1: GitHub Releases (Recommended for Beta)

**Pros:**
- Free
- Version control integration
- Download statistics
- Release notes

**Process:**
1. Create Git tag: `git tag v1.0.0`
2. Push tag: `git push origin v1.0.0`
3. Create GitHub Release
4. Upload all platform binaries
5. Add release notes

### Option 2: Self-Hosted Download Server

**Pros:**
- Full control
- Custom download page
- Analytics

**Cons:**
- Hosting costs
- Bandwidth costs
- Maintenance

### Option 3: Package Managers

**Linux:**
- APT repository (for .deb)
- YUM/DNF repository (for .rpm)
- Snap Store
- Flatpak

**macOS:**
- Homebrew tap

**Windows:**
- Chocolatey
- Winget

---

## Automated Release Workflow

### GitHub Actions Workflow

Create `.github/workflows/release.yml`:

```yaml
name: Build Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-go@v4
        with:
          go-version: '1.21'
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install pyinstaller
      - name: Build
        run: ./scripts/build-release.sh ${GITHUB_REF#refs/tags/v}
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: linux-release
          path: releases/*.tar.gz

  build-macos:
    runs-on: macos-latest
    strategy:
      matrix:
        arch: [amd64, arm64]
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-go@v4
      - uses: actions/setup-python@v4
      - name: Build
        run: GOARCH=${{ matrix.arch }} ./scripts/build-release.sh ${GITHUB_REF#refs/tags/v}
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: macos-${{ matrix.arch }}-release
          path: releases/*.tar.gz

  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-go@v4
      - uses: actions/setup-python@v4
      - name: Build
        run: scripts\build-release.bat ${env:GITHUB_REF -replace 'refs/tags/v',''}
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: windows-release
          path: releases/*.zip

  create-release:
    needs: [build-linux, build-macos, build-windows]
    runs-on: ubuntu-latest
    steps:
      - name: Download all artifacts
        uses: actions/download-artifact@v3
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            linux-release/*
            macos-*-release/*
            windows-release/*
          draft: false
          prerelease: false
```

---

## Next Steps - Priority Order

### Phase 1: Immediate (Current Archives Work)
1. ✅ Test current build scripts on all platforms
2. ✅ Verify PyInstaller bundles work
3. ✅ Update INSTALLATION.md with clear instructions
4. ✅ Create GitHub Release manually

### Phase 2: Professional Installers (1-2 weeks)
1. Create DEB package script
2. Create RPM package script
3. Create Windows Inno Setup installer
4. Create macOS DMG with app bundle
5. Test installers on clean VMs

### Phase 3: Code Signing (Optional, 2-4 weeks)
1. Obtain Windows code signing certificate
2. Enroll in Apple Developer Program
3. Implement signing in build scripts
4. Notarize macOS builds

### Phase 4: Automation (1 week)
1. Set up GitHub Actions workflow
2. Test automated builds
3. Configure release automation

### Phase 5: Package Managers (Ongoing)
1. Create Homebrew tap
2. Submit to Chocolatey
3. Create Snap package
4. Create Flatpak package

---

## Immediate Action Items

**For your next beta release, you can:**

1. **Use existing build scripts** - They work!
   ```bash
   # On Linux
   ./scripts/build-release.sh 1.0.0-beta1

   # On macOS (need access to Mac)
   ./scripts/build-release.sh 1.0.0-beta1

   # On Windows (need access to Windows)
   scripts\build-release.bat 1.0.0-beta1
   ```

2. **Create GitHub Release**
   - Tag: `v1.0.0-beta1`
   - Upload the 3-4 archives (Linux, macOS Intel, macOS ARM, Windows)
   - Include INSTALLATION.md in release notes

3. **Share with testers**
   - Send GitHub release link
   - They download appropriate archive
   - Follow INSTALLATION.md

**This gets you 80% of the way there with minimal effort!**

---

## Resources

- **Inno Setup:** https://jrsoftware.org/isinfo.php
- **create-dmg:** https://github.com/create-dmg/create-dmg
- **PyInstaller:** https://pyinstaller.org/
- **GitHub Actions:** https://docs.github.com/en/actions
- **Code Signing Guide:** https://www.ssl.com/guide/ev-code-signing-certificate/

---

Copyright © 2026 Fragillidae Software



