#!/usr/bin/env python3
"""
Download TSDuck binaries for bundling with IBE-210
This script downloads TSDuck for Windows and extracts it to the tsduck/ folder
"""

import urllib.request
import zipfile
import shutil
from pathlib import Path
import sys

# TSDuck download URLs (update with latest version)
TSDUCK_VERSION = "3.30"
TSDUCK_URLS = {
    "Windows": f"https://github.com/tsduck/tsduck/releases/download/v{TSDUCK_VERSION}/TSDuck-Win64-{TSDUCK_VERSION}-xxxx.zip",
    # Add other platforms as needed
}

def download_file(url: str, output_path: Path, description: str = "file"):
    """Download a file from URL"""
    print(f"Downloading {description}...")
    print(f"URL: {url}")
    print(f"Destination: {output_path}")
    
    try:
        urllib.request.urlretrieve(url, output_path)
        print(f"✅ Successfully downloaded {description}")
        return True
    except Exception as e:
        print(f"❌ Failed to download {description}: {e}")
        return False

def extract_zip(zip_path: Path, extract_to: Path):
    """Extract ZIP file to directory"""
    print(f"Extracting {zip_path.name} to {extract_to}...")
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print(f"✅ Successfully extracted to {extract_to}")
        return True
    except Exception as e:
        print(f"❌ Failed to extract: {e}")
        return False

def organize_tsduck_files(extracted_path: Path, target_path: Path):
    """Organize TSDuck files into tsduck/bin and tsduck/plugins structure"""
    print("Organizing TSDuck files...")
    
    # Find tsp.exe and plugins
    tsp_exe = None
    plugins_dir = None
    
    # Search for tsp.exe
    for exe_file in extracted_path.rglob("tsp.exe"):
        tsp_exe = exe_file
        break
    
    if not tsp_exe:
        for exe_file in extracted_path.rglob("tsp"):
            tsp_exe = exe_file
            break
    
    # Search for plugins directory
    for dir_path in extracted_path.rglob("plugins"):
        if dir_path.is_dir():
            plugins_dir = dir_path
            break
    
    if not tsp_exe:
        print("❌ tsp executable not found in extracted files")
        return False
    
    # Create target structure
    target_bin = target_path / "bin"
    target_plugins = target_path / "plugins"
    target_bin.mkdir(parents=True, exist_ok=True)
    target_plugins.mkdir(parents=True, exist_ok=True)
    
    # Copy tsp executable
    shutil.copy2(tsp_exe, target_bin / tsp_exe.name)
    print(f"✅ Copied {tsp_exe.name} to {target_bin}")
    
    # Copy plugins
    if plugins_dir and plugins_dir.exists():
        for plugin_file in plugins_dir.glob("*.dll"):
            shutil.copy2(plugin_file, target_plugins / plugin_file.name)
            print(f"  Copied plugin: {plugin_file.name}")
        for plugin_file in plugins_dir.glob("*.so"):
            shutil.copy2(plugin_file, target_plugins / plugin_file.name)
            print(f"  Copied plugin: {plugin_file.name}")
        print(f"✅ Copied plugins to {target_plugins}")
    else:
        print("⚠️  Plugins directory not found, skipping...")
    
    # Copy any DLL dependencies from bin directory
    bin_dir = tsp_exe.parent
    if bin_dir.exists():
        for dll_file in bin_dir.glob("*.dll"):
            if dll_file.name != tsp_exe.name:
                shutil.copy2(dll_file, target_bin / dll_file.name)
                print(f"  Copied dependency: {dll_file.name}")
    
    return True

def main():
    """Main download and setup function"""
    print("=" * 60)
    print("IBE-210 TSDuck Downloader")
    print("=" * 60)
    print()
    
    # Determine platform
    import platform
    system = platform.system()
    
    if system not in TSDUCK_URLS:
        print(f"❌ Unsupported platform: {system}")
        print(f"Supported platforms: {list(TSDUCK_URLS.keys())}")
        return 1
    
    url = TSDUCK_URLS[system]
    project_root = Path(__file__).parent.parent
    tsduck_dir = project_root / "tsduck"
    download_dir = project_root / "downloads"
    zip_path = download_dir / "tsduck.zip"
    extract_path = download_dir / "tsduck_extracted"
    
    # Create directories
    download_dir.mkdir(exist_ok=True)
    extract_path.mkdir(exist_ok=True)
    
    # Download TSDuck
    if not download_file(url, zip_path, "TSDuck"):
        print("\n⚠️  Download failed. You can manually download TSDuck from:")
        print("   https://tsduck.io/download/tsduck/")
        print(f"   And extract it to: {tsduck_dir}")
        return 1
    
    # Extract ZIP
    if not extract_zip(zip_path, extract_path):
        return 1
    
    # Organize files
    if not organize_tsduck_files(extract_path, tsduck_dir):
        return 1
    
    # Cleanup
    print("\nCleaning up temporary files...")
    if zip_path.exists():
        zip_path.unlink()
    if extract_path.exists():
        shutil.rmtree(extract_path)
    
    print()
    print("=" * 60)
    print("✅ TSDuck setup complete!")
    print("=" * 60)
    print(f"TSDuck binaries are now in: {tsduck_dir}")
    print(f"  - Executable: {tsduck_dir / 'bin' / 'tsp.exe'}")
    print(f"  - Plugins: {tsduck_dir / 'plugins'}")
    print()
    print("You can now build IBE-210 with bundled TSDuck:")
    print("  pyinstaller IBE-210_Enterprise.spec")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

