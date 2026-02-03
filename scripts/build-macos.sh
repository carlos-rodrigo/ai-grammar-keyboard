#!/bin/bash
# Build macOS .app and .dmg
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VERSION="1.0.0"

cd "$PROJECT_DIR"

echo "🔧 Building Grammar Fix for macOS..."
echo ""

# Check we're on macOS
if [[ "$(uname)" != "Darwin" ]]; then
    echo "❌ This script must be run on macOS"
    exit 1
fi

# Check dependencies
echo "📋 Checking dependencies..."
command -v python3 >/dev/null || { echo "❌ Python 3 required"; exit 1; }
command -v pip3 >/dev/null || { echo "❌ pip3 required"; exit 1; }

# Install build dependencies
echo "📦 Installing build dependencies..."
pip3 install pyinstaller pillow --quiet

# Install project dependencies
pip3 install -e ".[macos]" --quiet

# Generate icon if needed
echo "🎨 Generating app icon..."
if [[ ! -f assets/icon.icns ]]; then
    if [[ -f assets/icon.svg ]]; then
        # Convert SVG to PNG then to ICNS
        python3 << 'PYTHON_SCRIPT'
import subprocess
import os
from pathlib import Path

assets = Path("assets")
svg_file = assets / "icon.svg"
iconset = assets / "icon.iconset"
iconset.mkdir(exist_ok=True)

# Sizes needed for macOS iconset
sizes = [16, 32, 64, 128, 256, 512]

try:
    from PIL import Image
    import cairosvg
    
    for size in sizes:
        # Normal resolution
        png_path = iconset / f"icon_{size}x{size}.png"
        cairosvg.svg2png(url=str(svg_file), write_to=str(png_path), 
                        output_width=size, output_height=size)
        
        # Retina (@2x)
        png_path_2x = iconset / f"icon_{size}x{size}@2x.png"
        cairosvg.svg2png(url=str(svg_file), write_to=str(png_path_2x),
                        output_width=size*2, output_height=size*2)
    
    # Convert iconset to icns
    subprocess.run(["iconutil", "-c", "icns", str(iconset)], check=True)
    print("✅ Icon generated successfully")
    
except ImportError:
    print("⚠️  cairosvg not available, using placeholder icon")
    # Create a simple placeholder PNG
    img = Image.new('RGBA', (512, 512), (99, 102, 241, 255))
    for size in sizes:
        resized = img.resize((size, size), Image.LANCZOS)
        resized.save(iconset / f"icon_{size}x{size}.png")
        resized_2x = img.resize((size*2, size*2), Image.LANCZOS)
        resized_2x.save(iconset / f"icon_{size}x{size}@2x.png")
    subprocess.run(["iconutil", "-c", "icns", str(iconset)], check=True)

# Cleanup iconset folder
import shutil
shutil.rmtree(iconset)
PYTHON_SCRIPT
    else
        echo "⚠️  No icon source found, build will use default icon"
    fi
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
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
    --hidden-import rumps \
    --hidden-import Quartz \
    --hidden-import AppKit \
    src/grammar_fix/__main__.py

# Verify .app was created
if [[ ! -d "dist/Grammar Fix.app" ]]; then
    echo "❌ Build failed - .app not created"
    exit 1
fi

# Create DMG
echo "📀 Creating DMG..."
DMG_DIR="dist/dmg"
DMG_NAME="GrammarFix-${VERSION}-macos.dmg"

mkdir -p "$DMG_DIR"
cp -r "dist/Grammar Fix.app" "$DMG_DIR/"

# Create Applications symlink for drag-to-install
ln -sf /Applications "$DMG_DIR/Applications"

# Create DMG with hdiutil
hdiutil create \
    -volname "Grammar Fix" \
    -srcfolder "$DMG_DIR" \
    -ov \
    -format UDZO \
    "dist/$DMG_NAME"

# Cleanup
rm -rf "$DMG_DIR"

# Get file sizes
APP_SIZE=$(du -sh "dist/Grammar Fix.app" | cut -f1)
DMG_SIZE=$(du -sh "dist/$DMG_NAME" | cut -f1)

echo ""
echo "✅ Build complete!"
echo ""
echo "📁 Output:"
echo "   dist/Grammar Fix.app  ($APP_SIZE)"
echo "   dist/$DMG_NAME  ($DMG_SIZE)"
echo ""
echo "🧪 To test locally:"
echo "   open 'dist/Grammar Fix.app'"
echo ""
echo "📤 To distribute:"
echo "   Upload dist/$DMG_NAME to GitHub Releases"
