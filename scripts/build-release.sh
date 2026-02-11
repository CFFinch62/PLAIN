#!/bin/bash
# PLAIN Release Build Script
# Builds interpreter binaries for multiple platforms and packages them with documentation

set -e

VERSION="${1:-1.0.0}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "========================================="
echo "Building PLAIN v${VERSION}"
echo "========================================="

# Create releases directory
mkdir -p "${PROJECT_ROOT}/releases"
cd "${PROJECT_ROOT}"

# Define platforms
declare -a PLATFORMS=(
    "linux/amd64"
    "linux/arm64"
    "darwin/amd64"
    "darwin/arm64"
    "windows/amd64"
)

# Build for each platform
echo ""
echo "Building interpreter binaries..."
for platform in "${PLATFORMS[@]}"; do
    GOOS=${platform%/*}
    GOARCH=${platform#*/}
    OUTPUT="plain-${GOOS}-${GOARCH}"

    if [ $GOOS = "windows" ]; then
        OUTPUT="${OUTPUT}.exe"
    fi

    echo "  → ${GOOS}/${GOARCH}..."
    GOOS=$GOOS GOARCH=$GOARCH go build -ldflags="-s -w" -o "releases/${OUTPUT}" cmd/plain/main.go
done

# Create universal macOS binary if both arm64 and amd64 exist (macOS only)
if [ -f "releases/plain-darwin-amd64" ] && [ -f "releases/plain-darwin-arm64" ]; then
    if command -v lipo &> /dev/null; then
        echo "  → Creating universal macOS binary..."
        lipo -create releases/plain-darwin-amd64 releases/plain-darwin-arm64 \
             -output releases/plain-darwin-universal
    else
        echo "  → Skipping universal macOS binary (lipo not available on this platform)"
    fi
fi

echo ""
echo "Building IDE executable (Linux only)..."
# DISABLED: Compiling IDE with PyInstaller
# The IDE will be distributed as source code instead, which ensures
# all themes and resources are properly included in the release
echo "  → Skipping IDE compilation (distributing as source code)"
# if [ "$(uname)" = "Linux" ] && python3 -m PyInstaller --version &> /dev/null; then
#     echo "  → Compiling PLAIN IDE with PyInstaller..."
#     python3 -m PyInstaller --clean --noconfirm plain_ide.spec
#     
#     if [ -f "dist/plain-ide" ]; then
#         echo "  → IDE compilation successful"
#         # Move to releases for packaging
#         mkdir -p releases/ide-build
#         mv dist/plain-ide releases/ide-build/
#     else
#         echo "  → Warning: IDE compilation failed, will include source instead"
#     fi
# else
#     if [ "$(uname)" != "Linux" ]; then
#         echo "  → Skipping IDE compilation (not on Linux)"
#     else
#         echo "  → Skipping IDE compilation (PyInstaller not found)"
#         echo "     Install with: sudo apt install python3-pyinstaller"
#     fi
# fi


echo ""
echo "Packaging releases..."

# Package each binary with docs and examples
for platform in "${PLATFORMS[@]}"; do
    GOOS=${platform%/*}
    GOARCH=${platform#*/}
    PACKAGE="plain-v${VERSION}-${GOOS}-${GOARCH}"

    echo "  → ${PACKAGE}..."

    # Create package directory
    mkdir -p "releases/${PACKAGE}"

    # Copy binary
    if [ $GOOS = "windows" ]; then
        cp "releases/plain-${GOOS}-${GOARCH}.exe" "releases/${PACKAGE}/plain.exe"
    else
        cp "releases/plain-${GOOS}-${GOARCH}" "releases/${PACKAGE}/plain"
        chmod +x "releases/${PACKAGE}/plain"
    fi

    # Copy documentation
    cp README.md "releases/${PACKAGE}/"
    [ -f LICENSE ] && cp LICENSE "releases/${PACKAGE}/"
    [ -f INSTALLATION.md ] && cp INSTALLATION.md "releases/${PACKAGE}/"
    [ -f CHANGELOG.md ] && cp CHANGELOG.md "releases/${PACKAGE}/"

    # Copy user documentation
    mkdir -p "releases/${PACKAGE}/docs"
    if [ -d "docs/user" ]; then
        cp -r docs/user/* "releases/${PACKAGE}/docs/"
    fi

    # Copy examples
    if [ -d "examples" ]; then
        mkdir -p "releases/${PACKAGE}/examples"
        # Copy .plain files only
        find examples -name "*.plain" -exec cp {} "releases/${PACKAGE}/examples/" \;
    fi

    # Copy IDE as source code
    if [ -d "plain_ide" ]; then
        echo "     Including IDE source code..."
        cp -r plain_ide "releases/${PACKAGE}/"
        
        # Verify themes were copied
        THEME_COUNT=$(find "releases/${PACKAGE}/plain_ide/themes/syntax" -name "*.conf" 2>/dev/null | wc -l)
        if [ "$THEME_COUNT" -gt 0 ]; then
            echo "     ✓ Included ${THEME_COUNT} syntax themes"
        else
            echo "     ⚠ Warning: No syntax themes found in package!"
        fi
        
        # Remove pycache and other unnecessary files
        find "releases/${PACKAGE}/plain_ide" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        find "releases/${PACKAGE}/plain_ide" -name "*.pyc" -delete 2>/dev/null || true
    fi


    # Create archive
    cd releases
    if [ $GOOS = "windows" ]; then
        zip -q -r "${PACKAGE}.zip" "${PACKAGE}"
        echo "     Created: ${PACKAGE}.zip"
    else
        tar -czf "${PACKAGE}.tar.gz" "${PACKAGE}"
        echo "     Created: ${PACKAGE}.tar.gz"
    fi
    cd ..

    # Clean up directory
    rm -rf "releases/${PACKAGE}"
done

# Create universal macOS package if binary exists
if [ -f "releases/plain-darwin-universal" ]; then
    PACKAGE="plain-v${VERSION}-macos-universal"
    echo "  → ${PACKAGE}..."

    mkdir -p "releases/${PACKAGE}"
    cp "releases/plain-darwin-universal" "releases/${PACKAGE}/plain"
    chmod +x "releases/${PACKAGE}/plain"

    cp README.md "releases/${PACKAGE}/"
    [ -f LICENSE ] && cp LICENSE "releases/${PACKAGE}/"
    [ -f INSTALLATION.md ] && cp INSTALLATION.md "releases/${PACKAGE}/"
    [ -f CHANGELOG.md ] && cp CHANGELOG.md "releases/${PACKAGE}/"

    mkdir -p "releases/${PACKAGE}/docs"
    if [ -d "docs/user" ]; then
        cp -r docs/user/* "releases/${PACKAGE}/docs/"
    fi

    if [ -d "examples" ]; then
        mkdir -p "releases/${PACKAGE}/examples"
        find examples -name "*.plain" -exec cp {} "releases/${PACKAGE}/examples/" \;
    fi

    # Copy IDE
    if [ -d "plain_ide" ]; then
        echo "     Including IDE source code..."
        cp -r plain_ide "releases/${PACKAGE}/"
        
        # Verify themes were copied
        THEME_COUNT=$(find "releases/${PACKAGE}/plain_ide/themes/syntax" -name "*.conf" 2>/dev/null | wc -l)
        if [ "$THEME_COUNT" -gt 0 ]; then
            echo "     ✓ Included ${THEME_COUNT} syntax themes"
        else
            echo "     ⚠ Warning: No syntax themes found in package!"
        fi
        
        find "releases/${PACKAGE}/plain_ide" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        find "releases/${PACKAGE}/plain_ide" -name "*.pyc" -delete 2>/dev/null || true
    fi

    cd releases
    tar -czf "${PACKAGE}.tar.gz" "${PACKAGE}"
    echo "     Created: ${PACKAGE}.tar.gz"
    cd ..

    rm -rf "releases/${PACKAGE}"
fi

# Create checksums
echo ""
echo "Creating checksums..."
cd releases
sha256sum *.tar.gz *.zip 2>/dev/null > "plain-v${VERSION}-checksums.txt" || \
    shasum -a 256 *.tar.gz *.zip > "plain-v${VERSION}-checksums.txt"
cd ..

# Show summary
echo ""
echo "========================================="
echo "Build Complete!"
echo "========================================="
echo ""
echo "Release artifacts in: ${PROJECT_ROOT}/releases/"
echo ""
ls -lh releases/*.{tar.gz,zip} 2>/dev/null || ls -lh releases/
echo ""
echo "To create a GitHub release:"
echo "  1. git tag -a v${VERSION} -m 'Release v${VERSION}'"
echo "  2. git push origin v${VERSION}"
echo "  3. Upload files from releases/ to GitHub release"
echo ""
