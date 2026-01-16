# AI Grammar Keyboard

Fix grammar with a keyboard shortcut using a local LLM. Works offline, private, and fast.

## Features

- **Local LLM**: Uses Ollama with llama3.2:3b (no data sent to cloud)
- **Works everywhere**: Menu bar app with global hotkey (Ctrl+Option+G)
- **Fast**: ~2 second response time
- **Simple**: Select text → press shortcut → grammar fixed

## Requirements

- macOS 13+
- [Ollama](https://ollama.ai) installed
- Python 3.9+
- ~2GB disk space for the model

## Installation

```bash
# Install Ollama first
brew install ollama

# Clone and install
git clone https://github.com/carlos-rodrigo/ai-grammar-keyboard.git
cd ai-grammar-keyboard
./install.sh
```

## Option 1: Menu Bar App (Recommended)

Works **everywhere** including Terminal, Arc, Chrome, VS Code.

```bash
# Install Python dependencies
pip3 install -r requirements.txt

# Run the app
python3 grammar_app.py
```

Look for **"G"** in your menu bar. Press **Ctrl+Option+G** to fix selected text.

**Note:** macOS will ask for Accessibility permissions on first use.

## Option 2: Automator Service

Works in native macOS apps (TextEdit, Notes, Mail).

```bash
./install.sh
```

Then set up keyboard shortcut in **System Settings → Keyboard → Keyboard Shortcuts → Services → Text → Fix Grammar**

## Usage

1. Select text in any app
2. Press **Ctrl+Option+G**
3. Wait ~2 seconds
4. Text is replaced with corrected version

## How It Works

```
Select text → Ctrl+Option+G → Copy to clipboard → Ollama API → Paste corrected text
```

## Troubleshooting

**Menu bar app needs permissions?**
- System Settings → Privacy & Security → Accessibility
- Add Terminal or Python

**Ollama not running?**
```bash
ollama serve
```

**Test the script directly:**
```bash
echo "She no go store" | ~/.local/bin/grammar-fix.sh
```

## License

MIT
