"""
Runtime hook for PyInstaller to ensure src package is importable
"""
import sys
import os
from pathlib import Path

# In PyInstaller bundled mode, ensure src package is in path
if getattr(sys, 'frozen', False):
    # Get the base path where PyInstaller extracted files
    base_path = Path(sys._MEIPASS)
    
    # Add base path to sys.path (this is where all modules are)
    if str(base_path) not in sys.path:
        sys.path.insert(0, str(base_path))
    
    # Try to find src package
    src_path = base_path / "src"
    if src_path.exists() and str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    # Also check if src is a package in the base path
    src_init = base_path / "src" / "__init__.py"
    if src_init.exists():
        # src package exists, ensure it's importable
        if str(base_path) not in sys.path:
            sys.path.insert(0, str(base_path))

