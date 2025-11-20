#!/usr/bin/env python3
"""
Copy TSDuck binaries from existing installation for bundling with IBE-210
"""

import shutil
from pathlib import Path
import sys
import platform

def find_tsduck_installation():
    """Find TSDuck installation on the system"""
    possible_paths = []
    
    if platform.system() == "Windows":
        possible_paths = [
            Path("C:/Program Files/TSDuck"),
            Path("C:/Program Files (x86)/TSDuck"),
            Path("C:/tsduck"),
        ]
    else:
        possible_paths = [
            Path("/usr/local/tsduck"),
            Path("/opt/tsduck"),
            Path("/usr/tsduck"),
        ]
    
    for path in possible_paths:
        if path.exists():
            bin_path = path / "bin" / ("tsp.exe" if platform.system() == "Windows" else "tsp")
            if bin_path.exists():
                return path
    
    return None

def copy_tsduck_files(source_path: Path, target_path: Path):
    """Copy TSDuck files from installation to bundling directory"""
    print(f"Copying TSDuck from: {source_path}")
    print(f"To: {target_path}")
    print()
    
    # Create target directories
    target_bin = target_path / "bin"
    target_plugins = target_path / "plugins"
    target_bin.mkdir(parents=True, exist_ok=True)
    target_plugins.mkdir(parents=True, exist_ok=True)
    
    # Copy tsp executable
    source_bin = source_path / "bin"
    tsp_exe = source_bin / ("tsp.exe" if platform.system() == "Windows" else "tsp")
    
    if not tsp_exe.exists():
        print(f"ERROR: tsp executable not found at {tsp_exe}")
        return False
    
    shutil.copy2(tsp_exe, target_bin / tsp_exe.name)
    print(f"[OK] Copied {tsp_exe.name} to {target_bin}")
    
    # Copy all DLLs from bin (dependencies)
    for dll_file in source_bin.glob("*.dll"):
        if dll_file.name.lower() != tsp_exe.name.lower():
            shutil.copy2(dll_file, target_bin / dll_file.name)
            print(f"  Copied dependency: {dll_file.name}")
    
    # Copy plugins
    source_plugins = source_path / "plugins"
    if source_plugins.exists():
        plugin_count = 0
        for plugin_file in source_plugins.glob("*.dll"):
            shutil.copy2(plugin_file, target_plugins / plugin_file.name)
            plugin_count += 1
        
        for plugin_file in source_plugins.glob("*.so"):
            shutil.copy2(plugin_file, target_plugins / plugin_file.name)
            plugin_count += 1
        
        print(f"[OK] Copied {plugin_count} plugins to {target_plugins}")
    else:
        print("[WARNING] Plugins directory not found")
    
    # Copy any libs if they exist
    source_libs = source_path / "lib"
    target_libs = target_path / "libs"
    if source_libs.exists():
        target_libs.mkdir(parents=True, exist_ok=True)
        lib_count = 0
        for lib_file in source_libs.rglob("*"):
            if lib_file.is_file():
                rel_path = lib_file.relative_to(source_libs)
                target_file = target_libs / rel_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(lib_file, target_file)
                lib_count += 1
        if lib_count > 0:
            print(f"[OK] Copied {lib_count} library files to {target_libs}")
    
    return True

def main():
    """Main function"""
    print("=" * 60)
    print("IBE-210 TSDuck Copier")
    print("=" * 60)
    print()
    
    # Find TSDuck installation
    tsduck_path = find_tsduck_installation()
    
    if not tsduck_path:
        print("ERROR: TSDuck installation not found!")
        print()
        print("Please install TSDuck from: https://tsduck.io/download/tsduck/")
        print("Or manually copy TSDuck files to tsduck/ folder")
        return 1
    
    print(f"Found TSDuck installation at: {tsduck_path}")
    print()
    
    # Get target directory
    project_root = Path(__file__).parent.parent
    target_path = project_root / "tsduck"
    
    # Copy files
    if not copy_tsduck_files(tsduck_path, target_path):
        return 1
    
    print()
    print("=" * 60)
    print("SUCCESS: TSDuck setup complete!")
    print("=" * 60)
    print(f"TSDuck binaries are now in: {target_path}")
    print(f"  - Executable: {target_path / 'bin' / ('tsp.exe' if platform.system() == 'Windows' else 'tsp')}")
    print(f"  - Plugins: {target_path / 'plugins'}")
    print()
    print("You can now build IBE-210 with bundled TSDuck:")
    print("  pyinstaller IBE-210_Enterprise.spec")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

