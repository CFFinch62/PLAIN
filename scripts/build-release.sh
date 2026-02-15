#!/bin/bash
# PLAIN Release Build Script
# Builds the Interpreter and IDE for the CURRENT platform only.

set -e

VERSION="${1:-1.0.0}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "========================================="
echo "Building PLAIN v${VERSION} for Current Platform"
echo "========================================="

cd "${PROJECT_ROOT}"

# 1. Detect OS and Arch
GOOS=$(go env GOOS)
GOARCH=$(go env GOARCH)
PLATFORM="${GOOS}/${GOARCH}"

echo "Detected Platform: ${PLATFORM}"

INTERPRETER_NAME="plain"
if [ "$GOOS" = "windows" ]; then
    INTERPRETER_NAME="plain.exe"
fi

# 2. Build Interpreter
echo ""
echo "Building Interpreter..."
echo "  → ${INTERPRETER_NAME}..."
go build -ldflags="-s -w" -o "${INTERPRETER_NAME}" cmd/plain/main.go

if [ ! -f "${INTERPRETER_NAME}" ]; then
    echo "Error: Failed to build interpreter."
    exit 1
fi
echo "  ✓ Interpreter built successfully."

# 3. Build IDE
echo ""
echo "Building IDE..."

# Check for PyInstaller
if ! python3 -c "import PyInstaller" &> /dev/null; then
    echo "Error: PyInstaller not found in python3."
    echo "Please install it: pip install pyinstaller" 
    exit 1
fi

echo "  → Running PyInstaller..."
# Use python3 -m PyInstaller to ensure we use the correct environment
python3 -m PyInstaller plain_ide.spec --noconfirm --clean

if [ ! -d "dist/plain-ide" ]; then
    echo "Error: PyInstaller failed to create dist/plain-ide directory."
    exit 1
fi
echo "  ✓ IDE built successfully."

# 4. Package Release
echo ""
echo "Packaging Release..."

RELEASE_DIR="${PROJECT_ROOT}/releases"
mkdir -p "${RELEASE_DIR}"

PACKAGE_NAME="plain-v${VERSION}-${GOOS}-${GOARCH}"
PACKAGE_PATH="${RELEASE_DIR}/${PACKAGE_NAME}"

# Create a clean directory for packaging
rm -rf "${PACKAGE_PATH}"
mkdir -p "${PACKAGE_PATH}"

# Copy the build output (which contains the IDE and the bundled interpreter)
cp -r dist/plain-ide/* "${PACKAGE_PATH}/"

# Copy standalone interpreter to root directory (in addition to _internal)
echo "  → Copying standalone interpreter to release root..."
cp "${INTERPRETER_NAME}" "${PACKAGE_PATH}/"

# Copy Documentation
cp README.md "${PACKAGE_PATH}/"
[ -f LICENSE ] && cp LICENSE "${PACKAGE_PATH}/"
[ -f INSTALLATION.md ] && cp INSTALLATION.md "${PACKAGE_PATH}/"

# Copy Documentation Folder
if [ -d "docs" ]; then
    cp -r docs "${PACKAGE_PATH}/"
fi

# Copy Examples (preserve directory structure)
if [ -d "examples" ]; then
    echo "  → Copying examples directory with full structure..."
    cp -r examples "${PACKAGE_PATH}/"
fi

# Create Archive
cd "${RELEASE_DIR}"
if [ "$GOOS" = "windows" ]; then
    ARCHIVE_NAME="${PACKAGE_NAME}.zip"
    rm -f "${ARCHIVE_NAME}"
    # Use python to zip if zip command might be missing (e.g. on clean Windows), 
    # but for now assume standard tools or git bash.
    if command -v zip &> /dev/null; then
        zip -q -r "${ARCHIVE_NAME}" "${PACKAGE_NAME}"
    else
        echo "Warning: 'zip' command not found. Skipping archive creation."
    fi
else
    ARCHIVE_NAME="${PACKAGE_NAME}.tar.gz"
    rm -f "${ARCHIVE_NAME}"
    tar -czf "${ARCHIVE_NAME}" "${PACKAGE_NAME}"
fi

echo "  ✓ Package content prepared in: releases/${PACKAGE_NAME}"
if [ -f "${ARCHIVE_NAME}" ]; then
    echo "  ✓ Archive created: releases/${ARCHIVE_NAME}"
fi

cd "${PROJECT_ROOT}"

# Cleanup (Optional)
# rm "${INTERPRETER_NAME}" 

echo ""
echo "========================================="
echo "Build Complete!"
echo "========================================="
