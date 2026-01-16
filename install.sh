#!/bin/bash
set -e

echo "🔧 Installing AI Grammar Keyboard..."

if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found. Install it first: brew install ollama"
    exit 1
fi

if ! pgrep -x ollama > /dev/null; then
    echo "⚠️  Starting Ollama..."
    ollama serve &
    sleep 2
fi

echo "📦 Pulling llama3.2:3b model (2GB)..."
ollama pull llama3.2:3b

echo "📁 Installing grammar-fix.sh..."
mkdir -p ~/.local/bin
cp grammar-fix.sh ~/.local/bin/
chmod +x ~/.local/bin/grammar-fix.sh

echo "📁 Installing Automator workflow..."
mkdir -p ~/Library/Services
cp -r "Fix Grammar.workflow" ~/Library/Services/

echo "🔄 Refreshing services..."
/System/Library/CoreServices/pbs -flush 2>/dev/null || true
/System/Library/CoreServices/pbs -update 2>/dev/null || true

echo ""
echo "✅ Installation complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Open System Settings → Keyboard → Keyboard Shortcuts → Services"
echo "   2. Find 'Fix Grammar' under Text"
echo "   3. Assign a shortcut (e.g., Ctrl+Option+G)"
echo ""
echo "🧪 Test: Select text anywhere → press your shortcut"
