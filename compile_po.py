#!/usr/bin/env python3
"""
Compile all .po translation files in the locale/ directory to .mo binary files.
Uses polib (pure Python, no system gettext tools required).
Run: python compile_po.py
"""
import subprocess
import sys
import importlib

def ensure_polib():
    """Install polib if not available."""
    try:
        import polib
        return polib
    except ImportError:
        print("polib not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "polib"])
        import polib
        return polib

import os

def compile_po_files():
    polib = ensure_polib()
    locale_dir = os.path.join(os.path.dirname(__file__), 'locale')
    
    if not os.path.exists(locale_dir):
        print(f"No locale directory found at: {locale_dir}")
        return

    compiled = 0
    for root, dirs, files in os.walk(locale_dir):
        for filename in files:
            if filename.endswith('.po'):
                po_path = os.path.join(root, filename)
                mo_path = po_path.replace('.po', '.mo')
                try:
                    po = polib.pofile(po_path)
                    po.save_as_mofile(mo_path)
                    print(f"  ✔ Compiled: {po_path} → {mo_path}")
                    compiled += 1
                except Exception as e:
                    print(f"  ✘ Error compiling {po_path}: {e}")
    
    if compiled == 0:
        print("No .po files found to compile.")
    else:
        print(f"\nDone! Compiled {compiled} translation file(s).")

if __name__ == '__main__':
    compile_po_files()
