#!/usr/bin/env python3
"""macOS menu bar app for Grammar Fix."""

import sys
import time
import threading
from typing import Optional

import rumps
from AppKit import NSPasteboard, NSStringPboardType
from Quartz import (
    CGEventCreateKeyboardEvent,
    CGEventPost,
    kCGHIDEventTap,
    CGEventSetFlags,
    kCGEventFlagMaskCommand,
    CGEventTapCreate,
    CGEventTapEnable,
    kCGSessionEventTap,
    kCGHeadInsertEventTap,
    kCGEventTapOptionDefault,
    CGEventMaskBit,
    kCGEventKeyDown,
    CFMachPortCreateRunLoopSource,
    CFRunLoopGetCurrent,
    CFRunLoopAddSource,
    kCFRunLoopCommonModes,
    CFRunLoopRun,
    CGEventGetIntegerValueField,
    kCGKeyboardEventKeycode,
    CGEventGetFlags,
    kCGEventFlagMaskControl,
    kCGEventFlagMaskAlternate,
)

from . import __version__, __app_name__
from .core import fix_grammar, check_ollama

# Hotkey: Ctrl+Option+G (keycode 5 = G)
HOTKEY_KEYCODE = 5


class GrammarFixApp(rumps.App):
    """macOS menu bar application for grammar fixing."""
    
    def __init__(self):
        super().__init__("G", quit_button=None)
        
        # Build menu
        self.menu = [
            rumps.MenuItem("Fix Grammar (⌃⌥G)", callback=self.fix_grammar_click),
            None,  # Separator
            rumps.MenuItem("Status: Checking...", callback=None),
            None,  # Separator
            rumps.MenuItem(f"About {__app_name__} v{__version__}", callback=self.show_about),
            rumps.MenuItem("Quit", callback=self.quit_app),
        ]
        
        self.status_item = self.menu["Status: Checking..."]
        
        # Check Ollama on startup
        self._check_ollama_status()
        
        # Start hotkey listener
        self.hotkey_thread = threading.Thread(target=self._listen_hotkey, daemon=True)
        self.hotkey_thread.start()
    
    def _set_status(self, text: str):
        """Update status in menu."""
        self.status_item.title = f"Status: {text}"
    
    def _check_ollama_status(self):
        """Check if Ollama is ready."""
        ok, message = check_ollama()
        self._set_status("Ready ✓" if ok else message)
    
    def _listen_hotkey(self):
        """Listen for global hotkey (Ctrl+Option+G)."""
        
        def callback(proxy, event_type, event, refcon):
            keycode = CGEventGetIntegerValueField(event, kCGKeyboardEventKeycode)
            flags = CGEventGetFlags(event)
            
            ctrl = flags & kCGEventFlagMaskControl
            opt = flags & kCGEventFlagMaskAlternate
            
            # Check for Ctrl+Option+G
            if keycode == HOTKEY_KEYCODE and ctrl and opt:
                threading.Thread(target=self._do_fix_grammar, daemon=True).start()
                return None  # Consume the event
            
            return event
        
        mask = CGEventMaskBit(kCGEventKeyDown)
        tap = CGEventTapCreate(
            kCGSessionEventTap,
            kCGHeadInsertEventTap,
            kCGEventTapOptionDefault,
            mask,
            callback,
            None,
        )
        
        if tap:
            source = CFMachPortCreateRunLoopSource(None, tap, 0)
            CFRunLoopAddSource(CFRunLoopGetCurrent(), source, kCFRunLoopCommonModes)
            CGEventTapEnable(tap, True)
            CFRunLoopRun()
        else:
            self._set_status("⚠️ Need Accessibility permission")
            rumps.notification(
                __app_name__,
                "Permission Required",
                "Enable in System Settings → Privacy → Accessibility"
            )
    
    def _simulate_key(self, keycode: int, cmd: bool = False):
        """Simulate a key press."""
        event_down = CGEventCreateKeyboardEvent(None, keycode, True)
        event_up = CGEventCreateKeyboardEvent(None, keycode, False)
        
        if cmd:
            CGEventSetFlags(event_down, kCGEventFlagMaskCommand)
            CGEventSetFlags(event_up, kCGEventFlagMaskCommand)
        
        CGEventPost(kCGHIDEventTap, event_down)
        CGEventPost(kCGHIDEventTap, event_up)
    
    def _copy_selection(self) -> str:
        """Copy currently selected text to clipboard and return it."""
        pb = NSPasteboard.generalPasteboard()
        old_content = pb.stringForType_(NSStringPboardType)
        
        pb.clearContents()
        self._simulate_key(8, cmd=True)  # Cmd+C (keycode 8 = C)
        time.sleep(0.15)
        
        new_content = pb.stringForType_(NSStringPboardType)
        
        if new_content and new_content != old_content:
            return new_content
        return new_content or ""
    
    def _paste_text(self, text: str):
        """Paste text from clipboard."""
        pb = NSPasteboard.generalPasteboard()
        pb.clearContents()
        pb.setString_forType_(text, NSStringPboardType)
        time.sleep(0.05)
        self._simulate_key(9, cmd=True)  # Cmd+V (keycode 9 = V)
    
    def _do_fix_grammar(self):
        """Perform the grammar fix operation."""
        try:
            # Show working indicator
            self.title = "⏳"
            self._set_status("Copying...")
            
            # Get selected text
            original = self._copy_selection()
            if not original or not original.strip():
                self.title = "G"
                self._set_status("No text selected")
                rumps.notification(__app_name__, "", "No text selected")
                return
            
            # Fix grammar
            self._set_status("Fixing grammar...")
            corrected = fix_grammar(original)
            
            # Paste result
            if corrected and corrected != original:
                self._set_status("Pasting...")
                self._paste_text(corrected)
                self._set_status("Done! ✓")
            else:
                self._set_status("No changes needed")
            
            self.title = "G"
            
        except ConnectionError as e:
            self.title = "G"
            self._set_status("Ollama not running")
            rumps.notification(__app_name__, "Error", str(e))
        except Exception as e:
            self.title = "G"
            self._set_status(f"Error")
            rumps.notification(__app_name__, "Error", str(e))
    
    @rumps.clicked("Fix Grammar (⌃⌥G)")
    def fix_grammar_click(self, _):
        """Handle menu click."""
        threading.Thread(target=self._do_fix_grammar, daemon=True).start()
    
    def show_about(self, _):
        """Show about dialog."""
        rumps.notification(
            __app_name__,
            f"Version {__version__}",
            "Fix grammar with AI using local LLM.\nHotkey: Ctrl+Option+G"
        )
    
    def quit_app(self, _):
        """Quit the application."""
        rumps.quit_application()


def main():
    """Run the macOS app."""
    app = GrammarFixApp()
    app.run()


if __name__ == "__main__":
    main()
