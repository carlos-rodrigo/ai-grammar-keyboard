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
    python3 << 'PYTHON_SCRIPT'
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw

assets = Path("assets")
iconset = assets / "icon.iconset"
iconset.mkdir(exist_ok=True)

# Create a nice gradient icon programmatically
def create_icon(size):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Rounded rectangle background (purple gradient approximation)
    margin = size // 8
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=size // 5,
        fill=(99, 102, 241, 255)  # Indigo
    )
    
    # "G" letter in white
    font_size = size // 2
    try:
        from PIL import ImageFont
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except:
        font = ImageFont.load_default()
    
    text = "G"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - bbox[1]
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
    
    return img

# Sizes needed for macOS iconset
sizes = [16, 32, 64, 128, 256, 512]

for size in sizes:
    # Normal resolution
    img = create_icon(size)
    img.save(iconset / f"icon_{size}x{size}.png")
    
    # Retina (@2x)
    img_2x = create_icon(size * 2)
    img_2x.save(iconset / f"icon_{size}x{size}@2x.png")

# Convert iconset to icns
subprocess.run(["iconutil", "-c", "icns", str(iconset)], check=True)
print("✅ Icon generated successfully")

# Cleanup iconset folder
import shutil
shutil.rmtree(iconset)
PYTHON_SCRIPT
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
