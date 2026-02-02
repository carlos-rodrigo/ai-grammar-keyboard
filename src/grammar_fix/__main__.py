#!/usr/bin/env python3
"""Main entry point for Grammar Fix - detects platform and runs appropriate app."""

import sys
import platform


def main():
    system = platform.system()
    
    if system == "Darwin":
        from .app_macos import main as run_app
    elif system == "Linux":
        from .app_linux import main as run_app
    else:
        print(f"Unsupported platform: {system}")
        print("Grammar Fix supports macOS and Linux.")
        sys.exit(1)
    
    run_app()


if __name__ == "__main__":
    main()
