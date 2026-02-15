#!/bin/bash
# Build macOS DMG installer for PLAIN
# Usage: ./scripts/build-dmg.sh 1.0.0 [amd64|arm64]

set -e

VERSION="${1:-1.0.0}"
ARCH="${2:-amd64}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ "$ARCH" = "amd64" ]; then
    ARCH_NAME="Intel"
elif [ "$ARCH" = "arm64" ]; then
    ARCH_NAME="AppleSilicon"
else
    echo "Error: Invalid architecture. Use 'amd64' or 'arm64'"
    exit 1
fi

echo "========================================="
echo "Building PLAIN DMG v${VERSION} for ${ARCH_NAME}"
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

# Create app bundle structure
APP_NAME="PLAIN IDE.app"
APP_DIR="releases/${APP_NAME}"

echo "Creating application bundle..."
rm -rf "${APP_DIR}"
mkdir -p "${APP_DIR}/Contents/MacOS"
mkdir -p "${APP_DIR}/Contents/Resources"
mkdir -p "${APP_DIR}/Contents/Frameworks"

# Copy IDE executable and resources
echo "Copying IDE..."
cp -r dist/plain-ide/* "${APP_DIR}/Contents/MacOS/"

# Copy interpreter
echo "Copying interpreter..."
cp plain "${APP_DIR}/Contents/MacOS/"
chmod +x "${APP_DIR}/Contents/MacOS/plain"

# Copy documentation and examples
cp -r docs "${APP_DIR}/Contents/Resources/"
cp -r examples "${APP_DIR}/Contents/Resources/"
cp README.md "${APP_DIR}/Contents/Resources/"
[ -f LICENSE ] && cp LICENSE "${APP_DIR}/Contents/Resources/"

# Copy icon (convert PNG to ICNS if needed)
if [ -f "images/plain_icon_256.png" ]; then
    # For now, just copy the PNG. To create proper ICNS:
    # mkdir plain.iconset
    # sips -z 16 16 plain_icon_256.png --out plain.iconset/icon_16x16.png
    # ... (repeat for all sizes)
    # iconutil -c icns plain.iconset
    cp images/plain_icon_256.png "${APP_DIR}/Contents/Resources/icon.png"
fi

# Create Info.plist
cat > "${APP_DIR}/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleExecutable</key>
    <string>plain-ide</string>
    <key>CFBundleIconFile</key>
    <string>icon</string>
    <key>CFBundleIdentifier</key>
    <string>com.fragillidaesoftware.plain</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>PLAIN IDE</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>${VERSION}</string>
    <key>CFBundleVersion</key>
    <string>${VERSION}</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>CFBundleDocumentTypes</key>
    <array>
        <dict>
            <key>CFBundleTypeName</key>
            <string>PLAIN Program</string>
            <key>CFBundleTypeRole</key>
            <string>Editor</string>
            <key>LSItemContentTypes</key>
            <array>
                <string>public.plain-text</string>
            </array>
            <key>LSHandlerRank</key>
            <string>Owner</string>
            <key>CFBundleTypeExtensions</key>
            <array>
                <string>plain</string>
            </array>
        </dict>
    </array>
</dict>
</plist>
EOF

# Make the main executable actually executable
chmod +x "${APP_DIR}/Contents/MacOS/plain-ide"

# Create DMG staging directory
DMG_STAGING="releases/dmg-staging"
rm -rf "${DMG_STAGING}"
mkdir -p "${DMG_STAGING}"

# Copy app bundle to staging
cp -r "${APP_DIR}" "${DMG_STAGING}/"

# Create symlink to Applications folder
ln -s /Applications "${DMG_STAGING}/Applications"

# Create README
cat > "${DMG_STAGING}/README.txt" << EOF
PLAIN Programming Language v${VERSION}

Installation:
1. Drag "PLAIN IDE.app" to the Applications folder
2. Open Terminal and run: sudo ln -s "/Applications/PLAIN IDE.app/Contents/MacOS/plain" /usr/local/bin/plain
3. Launch PLAIN IDE from Applications

For more information, see the documentation in:
PLAIN IDE.app/Contents/Resources/docs/

Copyright © 2026 Fragillidae Software
EOF

# Create DMG
DMG_NAME="PLAIN-v${VERSION}-${ARCH_NAME}.dmg"
DMG_PATH="releases/${DMG_NAME}"

echo "Creating DMG..."
rm -f "${DMG_PATH}"

# Use hdiutil to create DMG
hdiutil create -volname "PLAIN ${VERSION}" \
    -srcfolder "${DMG_STAGING}" \
    -ov -format UDZO \
    "${DMG_PATH}"

if [ -f "${DMG_PATH}" ]; then
    echo "✓ DMG created: ${DMG_PATH}"
    echo ""
    echo "To install:"
    echo "  1. Open the DMG"
    echo "  2. Drag PLAIN IDE to Applications"
    echo "  3. Run: sudo ln -s '/Applications/PLAIN IDE.app/Contents/MacOS/plain' /usr/local/bin/plain"
else
    echo "Error: Failed to create DMG"
    exit 1
fi

# Cleanup
rm -rf "${DMG_STAGING}"

cd "${PROJECT_ROOT}"

