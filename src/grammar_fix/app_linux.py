#!/usr/bin/env python3
"""Linux system tray app for Grammar Fix."""

import sys
import time
import threading
from typing import Optional, Callable

import pystray
from PIL import Image, ImageDraw, ImageFont
from pynput import keyboard
import pyperclip
import subprocess

from . import __version__, __app_name__
from .core import fix_grammar, check_ollama


def create_icon_image(letter: str = "G", size: int = 64, bg_color: str = "#4A90D9", fg_color: str = "white") -> Image.Image:
    """Create a simple icon with a letter."""
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw circle background
    padding = 4
    draw.ellipse([padding, padding, size - padding, size - padding], fill=bg_color)
    
    # Draw letter
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size // 2)
    except:
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), letter, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - 2
    draw.text((x, y), letter, fill=fg_color, font=font)
    
    return image


class GrammarFixApp:
    """Linux system tray application for grammar fixing."""
    
    def __init__(self):
        self.status = "Starting..."
        self.icon: Optional[pystray.Icon] = None
        self.hotkey_listener: Optional[keyboard.GlobalHotKeys] = None
        self._running = True
        
        # Check Ollama
        self._check_ollama_status()
    
    def _check_ollama_status(self):
        """Check if Ollama is ready."""
        ok, message = check_ollama()
        self.status = "Ready ✓" if ok else message
    
    def _update_icon(self, letter: str = "G"):
        """Update the tray icon."""
        if self.icon:
            self.icon.icon = create_icon_image(letter)
    
    def _notify(self, title: str, message: str):
        """Send desktop notification."""
        try:
            subprocess.run([
                "notify-send",
                title,
                message,
                "--app-name", __app_name__,
                "-t", "3000"
            ], check=False, capture_output=True)
        except FileNotFoundError:
            # notify-send not available
            print(f"[{title}] {message}")
    
    def _get_selected_text(self) -> str:
        """Get currently selected text using xclip/xsel."""
        try:
            # Try to get primary selection (highlighted text)
            result = subprocess.run(
                ["xclip", "-selection", "primary", "-o"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        try:
            # Fallback: simulate Ctrl+C and get clipboard
            ctrl = keyboard.Controller()
            with ctrl.pressed(keyboard.Key.ctrl):
                ctrl.press('c')
                ctrl.release('c')
            time.sleep(0.15)
            return pyperclip.paste()
        except Exception:
            pass
        
        return ""
    
    def _paste_text(self, text: str):
        """Paste text using clipboard."""
        pyperclip.copy(text)
        time.sleep(0.05)
        
        try:
            ctrl = keyboard.Controller()
            with ctrl.pressed(keyboard.Key.ctrl):
                ctrl.press('v')
                ctrl.release('v')
        except Exception as e:
            print(f"Paste error: {e}")
    
    def _do_fix_grammar(self):
        """Perform the grammar fix operation."""
        try:
            self._update_icon("⏳")
            self.status = "Copying..."
            
            # Get selected text
            original = self._get_selected_text()
            if not original or not original.strip():
                self._update_icon("G")
                self.status = "No text selected"
                self._notify(__app_name__, "No text selected")
                return
            
            # Fix grammar
            self.status = "Fixing grammar..."
            corrected = fix_grammar(original)
            
            # Paste result
            if corrected and corrected != original:
                self.status = "Pasting..."
                self._paste_text(corrected)
                self.status = "Done! ✓"
            else:
                self.status = "No changes needed"
            
            self._update_icon("G")
            
        except ConnectionError as e:
            self._update_icon("G")
            self.status = "Ollama not running"
            self._notify(__app_name__, str(e))
        except Exception as e:
            self._update_icon("G")
            self.status = f"Error: {e}"
            self._notify(__app_name__, f"Error: {e}")
    
    def _on_hotkey(self):
        """Handle hotkey press."""
        threading.Thread(target=self._do_fix_grammar, daemon=True).start()
    
    def _create_menu(self) -> pystray.Menu:
        """Create the tray menu."""
        return pystray.Menu(
            pystray.MenuItem(
                "Fix Grammar (Ctrl+Alt+G)",
                lambda: self._on_hotkey()
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                lambda text: f"Status: {self.status}",
                None,
                enabled=False
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                f"About {__app_name__} v{__version__}",
                lambda: self._notify(__app_name__, f"Version {__version__}\nFix grammar with AI using local LLM.\nHotkey: Ctrl+Alt+G")
            ),
            pystray.MenuItem("Quit", self._quit),
        )
    
    def _quit(self):
        """Quit the application."""
        self._running = False
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        if self.icon:
            self.icon.stop()
    
    def _setup_hotkey(self):
        """Set up global hotkey listener."""
        self.hotkey_listener = keyboard.GlobalHotKeys({
            '<ctrl>+<alt>+g': self._on_hotkey
        })
        self.hotkey_listener.start()
    
    def run(self):
        """Run the application."""
        # Set up hotkey
        self._setup_hotkey()
        
        # Create and run tray icon
        self.icon = pystray.Icon(
            __app_name__,
            create_icon_image("G"),
            __app_name__,
            menu=self._create_menu()
        )
        
        print(f"{__app_name__} running. Hotkey: Ctrl+Alt+G")
        self.icon.run()


def main():
    """Run the Linux app."""
    app = GrammarFixApp()
    app.run()


if __name__ == "__main__":
    main()
