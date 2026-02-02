#!/bin/bash
# One-line installer for Linux
set -e

echo "🔧 Installing Grammar Fix for Linux..."

# Check for Ollama
if ! command -v ollama &> /dev/null; then
    echo ""
    echo "⚠️  Ollama not found!"
    echo ""
    echo "Install Ollama first:"
    echo "  curl -fsSL https://ollama.ai/install.sh | sh"
    echo ""
    read -p "Continue anyway? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for required system packages
echo "📋 Checking dependencies..."
MISSING_DEPS=()

if ! command -v xclip &> /dev/null; then
    MISSING_DEPS+=("xclip")
fi

if ! python3 -c "import gi" 2>/dev/null; then
    MISSING_DEPS+=("python3-gi")
fi

if [ ${#MISSING_DEPS[@]} -ne 0 ]; then
    echo ""
    echo "⚠️  Missing system packages: ${MISSING_DEPS[*]}"
    echo ""
    echo "Install them with:"
    echo "  sudo apt install ${MISSING_DEPS[*]}  # Debian/Ubuntu"
    echo "  sudo dnf install ${MISSING_DEPS[*]}  # Fedora"
    echo "  sudo pacman -S ${MISSING_DEPS[*]}    # Arch"
    echo ""
fi

# Install Python package
echo "📦 Installing Grammar Fix..."
pip3 install --user "grammar-fix[linux]" 2>/dev/null || {
    # If not on PyPI, install from source
    pip3 install --user -e ".[linux]"
}

# Pull Ollama model
echo "🤖 Pulling LLM model..."
if command -v ollama &> /dev/null; then
    ollama pull llama3.2:1b || echo "⚠️  Could not pull model. Make sure Ollama is running."
fi

# Create desktop entry
echo "🖥️  Creating desktop entry..."
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/grammar-fix.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=Grammar Fix
Comment=Fix grammar with AI using local LLM
Exec=grammar-fix
Icon=accessories-text-editor
Categories=Utility;TextTools;
Keywords=grammar;spelling;text;ai;
StartupNotify=false
Terminal=false
EOF

# Create autostart entry
echo "🚀 Setting up autostart..."
mkdir -p ~/.config/autostart
cp ~/.local/share/applications/grammar-fix.desktop ~/.config/autostart/

echo ""
echo "✅ Installation complete!"
echo ""
echo "📋 Usage:"
echo "   1. Start: grammar-fix (or find in app menu)"
echo "   2. Select any text"
echo "   3. Press Ctrl+Alt+G"
echo "   4. Text is corrected!"
echo ""
echo "💡 The app will auto-start on login."
echo "   To disable: remove ~/.config/autostart/grammar-fix.desktop"
