# AI Grammar Keyboard

Fix grammar with a keyboard shortcut using a local LLM. Works offline, private, and fast.

## Features

- **Local LLM**: Uses Ollama with llama3.2:3b (no data sent to cloud)
- **System-wide**: Works in any macOS app via Services menu
- **Fast**: ~2 second response time
- **Simple**: Select text → press shortcut → grammar fixed

## Requirements

- macOS 13+
- [Ollama](https://ollama.ai) installed
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

## Setup Keyboard Shortcut

1. Open **System Settings** → **Keyboard** → **Keyboard Shortcuts**
2. Click **Services** → **Text**
3. Find **Fix Grammar**
4. Double-click and press your shortcut (e.g., `Ctrl+Option+G`)

> **Note**: Avoid `Cmd+G` as it conflicts with "Find Next" in most apps.

## Usage

1. Select text in any app
2. Press your shortcut
3. Wait ~2 seconds
4. Text is replaced with corrected version

## Limitations

- **Chromium browsers** (Arc, Chrome, Brave): Services don't work well. Use right-click → Services → Fix Grammar instead.
- **Some apps** may not support macOS Services.

## How It Works

```
Select text → Shortcut → Automator Service → Shell script → Ollama API → Replace text
```

## Troubleshooting

**Service not appearing?**
```bash
/System/Library/CoreServices/pbs -flush
/System/Library/CoreServices/pbs -update
```

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
