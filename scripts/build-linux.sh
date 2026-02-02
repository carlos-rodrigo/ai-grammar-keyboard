#!/bin/bash
# Build Linux binary and AppImage
set -e

cd "$(dirname "$0")/.."

echo "🔧 Building Grammar Fix for Linux..."

# Check we're on Linux
if [[ "$(uname)" != "Linux" ]]; then
    echo "❌ This script must be run on Linux"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -e ".[linux,dev]" --quiet

# Clean previous builds
rm -rf build dist

# Create binary with PyInstaller
echo "🏗️  Building binary..."
pyinstaller \
    --name "grammar-fix" \
    --onefile \
    --add-data "src/grammar_fix:grammar_fix" \
    src/grammar_fix/__main__.py

# Make it executable
chmod +x dist/grammar-fix

echo ""
echo "✅ Build complete!"
echo ""
echo "📁 Output:"
echo "   dist/grammar-fix"
echo ""
echo "🧪 To test: ./dist/grammar-fix"
echo ""
echo "📋 To install:"
echo "   sudo cp dist/grammar-fix /usr/local/bin/"
echo ""
echo "🚀 To auto-start, add to your DE's startup applications"
