#!/bin/bash
# Build Debian (.deb) package for PLAIN
# Usage: ./scripts/build-deb.sh 1.0.0

set -e

VERSION="${1:-1.0.0}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "========================================="
echo "Building PLAIN .deb package v${VERSION}"
echo "========================================="

cd "${PROJECT_ROOT}"

# Check if we have the built binaries
if [ ! -f "plain" ]; then
    echo "Error: plain interpreter not found. Run build-release.sh first."
    exit 1
fi

if [ ! -d "dist/plain-ide" ]; then
    echo "Error: IDE not built. Run build-release.sh first."
    exit 1
fi

# Create package structure
PACKAGE_NAME="plain_${VERSION}_amd64"
PACKAGE_DIR="releases/${PACKAGE_NAME}"

echo "Creating package structure..."
rm -rf "${PACKAGE_DIR}"
mkdir -p "${PACKAGE_DIR}/DEBIAN"
mkdir -p "${PACKAGE_DIR}/usr/bin"
mkdir -p "${PACKAGE_DIR}/usr/share/plain"
mkdir -p "${PACKAGE_DIR}/usr/share/applications"
mkdir -p "${PACKAGE_DIR}/usr/share/icons/hicolor/256x256/apps"
mkdir -p "${PACKAGE_DIR}/usr/share/doc/plain"

# Copy binaries
echo "Copying binaries..."
cp plain "${PACKAGE_DIR}/usr/bin/"
chmod 755 "${PACKAGE_DIR}/usr/bin/plain"

# Copy IDE
echo "Copying IDE..."
cp -r dist/plain-ide/* "${PACKAGE_DIR}/usr/share/plain/"

# Create wrapper script for IDE
cat > "${PACKAGE_DIR}/usr/bin/plain-ide" << 'EOF'
#!/bin/bash
# PLAIN IDE launcher
cd /usr/share/plain
exec ./plain-ide "$@"
EOF
chmod 755 "${PACKAGE_DIR}/usr/bin/plain-ide"

# Copy documentation
echo "Copying documentation..."
cp README.md "${PACKAGE_DIR}/usr/share/doc/plain/"
[ -f LICENSE ] && cp LICENSE "${PACKAGE_DIR}/usr/share/doc/plain/"
cp -r docs "${PACKAGE_DIR}/usr/share/plain/"
cp -r examples "${PACKAGE_DIR}/usr/share/plain/"

# Copy icon
if [ -f "images/plain_icon_256.png" ]; then
    cp images/plain_icon_256.png "${PACKAGE_DIR}/usr/share/icons/hicolor/256x256/apps/plain.png"
fi

# Create .desktop file
cat > "${PACKAGE_DIR}/usr/share/applications/plain-ide.desktop" << EOF
[Desktop Entry]
Name=PLAIN IDE
Comment=PLAIN Programming Language IDE
Exec=/usr/bin/plain-ide
Icon=plain
Terminal=false
Type=Application
Categories=Development;IDE;
Path=/usr/share/plain
EOF

# Create control file
cat > "${PACKAGE_DIR}/DEBIAN/control" << EOF
Package: plain
Version: ${VERSION}
Section: devel
Priority: optional
Architecture: amd64
Depends: python3 (>= 3.8), python3-pyqt6
Maintainer: Fragillidae Software <info@fragillidaesoftware.com>
Description: PLAIN Programming Language
 PLAIN is a beginner-friendly programming language with a clear,
 readable syntax. This package includes both the interpreter and
 the integrated development environment (IDE).
 .
 Features:
  - Simple, English-like syntax
  - Built-in functions for common tasks
  - Integrated development environment
  - Comprehensive documentation and examples
Homepage: https://github.com/CFFinch62/plain-language
EOF

# Create postinst script
cat > "${PACKAGE_DIR}/DEBIAN/postinst" << 'EOF'
#!/bin/bash
set -e

# Update desktop database
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q
fi

# Update icon cache
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true
fi

echo "PLAIN installed successfully!"
echo "Run 'plain' for the interpreter or 'plain-ide' for the IDE"

exit 0
EOF
chmod 755 "${PACKAGE_DIR}/DEBIAN/postinst"

# Create prerm script
cat > "${PACKAGE_DIR}/DEBIAN/prerm" << 'EOF'
#!/bin/bash
set -e
exit 0
EOF
chmod 755 "${PACKAGE_DIR}/DEBIAN/prerm"

# Build the package
echo "Building .deb package..."
cd releases
dpkg-deb --build "${PACKAGE_NAME}"

if [ -f "${PACKAGE_NAME}.deb" ]; then
    echo "✓ Package created: releases/${PACKAGE_NAME}.deb"
    echo ""
    echo "To install:"
    echo "  sudo dpkg -i releases/${PACKAGE_NAME}.deb"
    echo "  sudo apt-get install -f  # Install dependencies if needed"
else
    echo "Error: Failed to create .deb package"
    exit 1
fi

cd "${PROJECT_ROOT}"

