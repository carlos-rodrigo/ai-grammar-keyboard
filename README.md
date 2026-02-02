# Grammar Fix ✨

Fix grammar with a keyboard shortcut using a local LLM. Works offline, private, and fast.

![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- 🔒 **Private**: Uses Ollama locally - no data sent to the cloud
- ⚡ **Fast**: ~2 second response time
- 🌍 **Works everywhere**: System tray app with global hotkey
- 💻 **Cross-platform**: macOS and Linux

## Quick Install

### Prerequisites

1. Install [Ollama](https://ollama.ai):
   ```bash
   # macOS
   brew install ollama
   
   # Linux
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. Start Ollama and pull the model:
   ```bash
   ollama serve &
   ollama pull llama3.2:1b
   ```

### macOS

**Option A: Download DMG** (Recommended)

1. Download `GrammarFix-1.0.0-macos.dmg` from [Releases](https://github.com/carlos-rodrigo/ai-grammar-keyboard/releases)
2. Open the DMG
3. Drag "Grammar Fix" to Applications
4. Open "Grammar Fix" from Applications
5. Grant Accessibility permission when prompted

**Option B: From source**

```bash
git clone https://github.com/carlos-rodrigo/ai-grammar-keyboard.git
cd ai-grammar-keyboard
pip3 install -e ".[macos]"
grammar-fix
```

### Linux

**Option A: One-line install**

```bash
curl -fsSL https://raw.githubusercontent.com/carlos-rodrigo/ai-grammar-keyboard/main/scripts/install-linux.sh | bash
```

**Option B: From source**

```bash
# Install system dependencies (Debian/Ubuntu)
sudo apt install xclip python3-gi

git clone https://github.com/carlos-rodrigo/ai-grammar-keyboard.git
cd ai-grammar-keyboard
pip3 install -e ".[linux]"
grammar-fix
```

## Usage

1. **Start the app** - Look for "G" in your menu bar / system tray
2. **Select text** in any application
3. **Press the hotkey**:
   - macOS: `Ctrl+Option+G`
   - Linux: `Ctrl+Alt+G`
4. **Wait ~2 seconds** - text is replaced with corrected version

## Building from Source

### macOS

```bash
./scripts/build-macos.sh
# Output: dist/Grammar Fix.app, dist/GrammarFix-1.0.0-macos.dmg
```

### Linux

```bash
./scripts/build-linux.sh
# Output: dist/grammar-fix
```

## Troubleshooting

### "Ollama not running"

```bash
ollama serve
```

### macOS: "Accessibility permission required"

System Settings → Privacy & Security → Accessibility → Enable "Grammar Fix"

### Linux: Hotkey not working

Make sure `xclip` is installed:
```bash
sudo apt install xclip  # Debian/Ubuntu
sudo pacman -S xclip    # Arch
```

### Test Ollama directly

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2:1b",
  "prompt": "Fix: She no go store",
  "stream": false
}'
```

## Configuration

The app uses sensible defaults. To customize, edit:

- Model: Change `DEFAULT_MODEL` in `src/grammar_fix/core.py`
- Prompt: Modify `PROMPT_TEMPLATE` in `src/grammar_fix/core.py`
- Hotkey: 
  - macOS: Change `HOTKEY_KEYCODE` in `app_macos.py`
  - Linux: Modify the hotkey string in `app_linux.py`

## How It Works

```
Select text → Hotkey → Copy to clipboard → Ollama API → Paste corrected text
```

The app simulates Cmd/Ctrl+C, sends the text to your local Ollama instance, and simulates Cmd/Ctrl+V to paste the result.

## License

MIT © Carlos Rodrigo
