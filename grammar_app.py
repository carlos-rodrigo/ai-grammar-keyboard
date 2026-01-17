#!/usr/bin/env python3
import rumps
import requests
import subprocess
import time
import threading
from AppKit import NSPasteboard, NSStringPboardType
from Quartz import (
    CGEventCreateKeyboardEvent,
    CGEventPost,
    kCGHIDEventTap,
    CGEventSetFlags,
    kCGEventFlagMaskCommand,
)

import re

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:1b"
PROMPT_TEMPLATE = """Fix grammar/spelling. Output ONLY the corrected sentence, nothing else.

Input: {text}
Output:"""

def extract_corrected_text(response, original):
    text = response.strip()
    if not text:
        return original
    lines = text.split('\n')
    result = lines[0].strip()
    for prefix in ['Output:', 'Corrected:', 'Corrected text:', 'Result:']:
        if result.lower().startswith(prefix.lower()):
            result = result[len(prefix):].strip()
    result = result.strip('"\'')
    if len(result) < 2 or len(result) > len(original) * 3:
        return original
    return result

class GrammarApp(rumps.App):
    def __init__(self):
        super().__init__("G", quit_button=None)
        self.menu = [
            rumps.MenuItem("Fix Grammar (Ctrl+Option+G)", callback=self.fix_grammar_click),
            None,
            rumps.MenuItem("Status: Ready", callback=None),
            None,
            rumps.MenuItem("Quit", callback=self.quit_app),
        ]
        self.status_item = self.menu["Status: Ready"]
        self.hotkey_thread = threading.Thread(target=self.listen_hotkey, daemon=True)
        self.hotkey_thread.start()

    def set_status(self, text):
        self.status_item.title = f"Status: {text}"

    def listen_hotkey(self):
        from Quartz import (
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

        def callback(proxy, event_type, event, refcon):
            keycode = CGEventGetIntegerValueField(event, kCGKeyboardEventKeycode)
            flags = CGEventGetFlags(event)
            ctrl = flags & kCGEventFlagMaskControl
            opt = flags & kCGEventFlagMaskAlternate
            if keycode == 5 and ctrl and opt:
                threading.Thread(target=self.fix_grammar, daemon=True).start()
                return None
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

    def simulate_key(self, keycode, cmd=False):
        event_down = CGEventCreateKeyboardEvent(None, keycode, True)
        event_up = CGEventCreateKeyboardEvent(None, keycode, False)
        if cmd:
            CGEventSetFlags(event_down, kCGEventFlagMaskCommand)
            CGEventSetFlags(event_up, kCGEventFlagMaskCommand)
        CGEventPost(kCGHIDEventTap, event_down)
        CGEventPost(kCGHIDEventTap, event_up)

    def copy_selection(self):
        pb = NSPasteboard.generalPasteboard()
        old_content = pb.stringForType_(NSStringPboardType)
        pb.clearContents()
        self.simulate_key(8, cmd=True)
        time.sleep(0.1)
        new_content = pb.stringForType_(NSStringPboardType)
        if new_content and new_content != old_content:
            return new_content
        return new_content or ""

    def paste_text(self, text):
        pb = NSPasteboard.generalPasteboard()
        pb.clearContents()
        pb.setString_forType_(text, NSStringPboardType)
        time.sleep(0.05)
        self.simulate_key(9, cmd=True)

    def call_ollama(self, text):
        prompt = PROMPT_TEMPLATE.format(text=text)
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "prompt": prompt, "stream": False},
            timeout=30,
        )
        raw = response.json().get("response", "")
        return extract_corrected_text(raw, text)

    def fix_grammar(self):
        try:
            self.title = "⏳"
            self.set_status("Copying...")
            original = self.copy_selection()
            if not original:
                self.title = "G"
                self.set_status("No text selected")
                rumps.notification("Grammar Fix", "", "No text selected")
                return

            self.set_status("Fixing grammar...")
            corrected = self.call_ollama(original)

            if corrected and corrected != original:
                self.set_status("Pasting...")
                self.paste_text(corrected)
                self.set_status("Done!")
            else:
                self.set_status("No changes needed")

            self.title = "G"
        except Exception as e:
            self.title = "G"
            self.set_status(f"Error: {e}")
            rumps.notification("Grammar Fix", "Error", str(e))

    @rumps.clicked("Fix Grammar (Ctrl+Option+G)")
    def fix_grammar_click(self, _):
        threading.Thread(target=self.fix_grammar, daemon=True).start()

    def quit_app(self, _):
        rumps.quit_application()

if __name__ == "__main__":
    GrammarApp().run()
