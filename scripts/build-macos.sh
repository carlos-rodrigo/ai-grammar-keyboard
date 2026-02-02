#!/bin/bash
# Build macOS .app and .dmg
set -e

cd "$(dirname "$0")/.."

echo "🔧 Building Grammar Fix for macOS..."

# Check we're on macOS
if [[ "$(uname)" != "Darwin" ]]; then
    echo "❌ This script must be run on macOS"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -e ".[macos,dev]" --quiet

# Clean previous builds
rm -rf build dist

# Create app bundle with PyInstaller
echo "🏗️  Building .app bundle..."
pyinstaller \
    --name "Grammar Fix" \
    --windowed \
    --onefile \
    --icon assets/icon.icns \
    --osx-bundle-identifier "me.carlosrodrigo.grammarfix" \
    --add-data "src/grammar_fix:grammar_fix" \
    src/grammar_fix/__main__.py

# Create DMG
echo "📀 Creating DMG..."
mkdir -p dist/dmg
cp -r "dist/Grammar Fix.app" dist/dmg/

# Create Applications symlink
ln -sf /Applications dist/dmg/Applications

# Create DMG with hdiutil
hdiutil create -volname "Grammar Fix" \
    -srcfolder dist/dmg \
    -ov -format UDZO \
    "dist/GrammarFix-1.0.0-macos.dmg"

# Cleanup
rm -rf dist/dmg

echo ""
echo "✅ Build complete!"
echo ""
echo "📁 Output:"
echo "   dist/Grammar Fix.app"
echo "   dist/GrammarFix-1.0.0-macos.dmg"
echo ""
echo "🧪 To test: open 'dist/Grammar Fix.app'"
