# TSDuck Bundling Guide
## Inbuilding TSDuck into Your Application

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Current Approach vs Bundled Approach](#current-approach-vs-bundled-approach)
3. [What "Inbuilding" TSDuck Means](#what-inbuilding-tsduck-means)
4. [Technical Implementation](#technical-implementation)
5. [Pros and Cons](#pros-and-cons)
6. [Licensing Considerations](#licensing-considerations)
7. [File Size Impact](#file-size-impact)
8. [Platform-Specific Considerations](#platform-specific-considerations)
9. [Implementation Steps](#implementation-steps)
10. [Alternative Approaches](#alternative-approaches)

---

## 🎯 Overview

**"Inbuilding TSDuck"** means bundling the TSDuck binaries (executables, DLLs, plugins) directly into your application package, so users don't need to install TSDuck separately.

### Current Situation

**Your Application Currently:**
- ✅ Requires users to install TSDuck separately
- ✅ Looks for TSDuck in common locations (`C:\Program Files\TSDuck\bin\tsp.exe`)
- ✅ Falls back to PATH if TSDuck is installed
- ✅ Shows error if TSDuck is not found

**With Bundled TSDuck:**
- ✅ TSDuck binaries included in your application package
- ✅ No separate installation required
- ✅ Works out of the box
- ✅ Version-controlled (you control which TSDuck version)

---

## 🔄 Current Approach vs Bundled Approach

### **Current Approach: External Dependency**

```
┌─────────────────────┐
│  Your Application  │
│  (IBE-100.exe)     │
└──────────┬──────────┘
           │
           │ Calls: tsp.exe
           ▼
┌─────────────────────┐
│  TSDuck Installation│
│  (External)         │
│  C:\Program Files\  │
│  TSDuck\bin\tsp.exe │
└─────────────────────┘
```

**User Experience:**
1. Download your application
2. **Must separately install TSDuck** from tsduck.io
3. Configure TSDuck path (if not in default location)
4. Then use your application

**Issues:**
- ❌ Extra installation step for users
- ❌ Version mismatch (user might have old TSDuck)
- ❌ Installation errors (user might install wrong version)
- ❌ Path configuration required
- ❌ Support issues ("TSDuck not found")

---

### **Bundled Approach: Included TSDuck**

```
┌─────────────────────────────────┐
│  Your Application Package       │
│  ┌───────────────────────────┐ │
│  │  IBE-100.exe              │ │
│  └──────────┬────────────────┘ │
│             │                   │
│  ┌──────────▼────────────────┐ │
│  │  TSDuck Binaries          │ │
│  │  ├── tsp.exe              │ │
│  │  ├── tsp.dll              │ │
│  │  ├── plugins/             │ │
│  │  │   ├── spliceinject.dll │ │
│  │  │   ├── splicemonitor.dll│ │
│  │  │   ├── analyze.dll      │ │
│  │  │   └── ...              │ │
│  │  └── libs/                │ │
│  └───────────────────────────┘ │
└─────────────────────────────────┘
```

**User Experience:**
1. Download your application
2. **Run immediately** - TSDuck is included
3. No configuration needed

**Benefits:**
- ✅ Single installation
- ✅ Guaranteed TSDuck version
- ✅ No path configuration
- ✅ Better user experience
- ✅ Fewer support issues

---

## 🔧 What "Inbuilding" TSDuck Means

### **1. Include TSDuck Binaries**

**What to Bundle:**
- `tsp.exe` - Main TSDuck executable
- `tsp.dll` - TSDuck library (if exists)
- `plugins/` - All TSDuck plugins (DLLs)
  - `spliceinject.dll`
  - `splicemonitor.dll`
  - `analyze.dll`
  - `sdt.dll`
  - `pmt.dll`
  - `remap.dll`
  - `hls.dll`
  - `srt.dll`
  - `ip.dll`
  - `tcp.dll`
  - `http.dll`
  - ... (all plugins you use)
- `libs/` - TSDuck dependencies (if any)
  - C++ runtime libraries
  - Other DLLs

### **2. Modify Application to Use Bundled TSDuck**

**Current Code:**
```python
# src/services/tsduck_service.py
def __init__(self, tsduck_path: str = None):
    self.tsduck_path = tsduck_path or find_tsduck()  # Looks in system
```

**Bundled Code:**
```python
# src/services/tsduck_service.py
def __init__(self, tsduck_path: str = None):
    if tsduck_path:
        self.tsduck_path = tsduck_path
    else:
        # First try bundled TSDuck
        bundled_path = self._get_bundled_tsduck_path()
        if bundled_path and os.path.exists(bundled_path):
            self.tsduck_path = bundled_path
        else:
            # Fallback to system TSDuck
            self.tsduck_path = find_tsduck()
    
def _get_bundled_tsduck_path(self) -> str:
    """Get path to bundled TSDuck executable"""
    if getattr(sys, 'frozen', False):
        # PyInstaller bundled mode
        base_path = Path(sys._MEIPASS)
    else:
        # Development mode
        base_path = Path(__file__).parent.parent.parent
    
    tsp_exe = base_path / "tsduck" / "bin" / "tsp.exe"
    if tsp_exe.exists():
        return str(tsp_exe)
    return None
```

### **3. Package Structure**

**With Bundled TSDuck:**
```
IBE-100_Enterprise/
├── dist/
│   └── IBE-100_Enterprise.exe
├── tsduck/                    # Bundled TSDuck
│   ├── bin/
│   │   └── tsp.exe
│   ├── plugins/
│   │   ├── spliceinject.dll
│   │   ├── splicemonitor.dll
│   │   ├── analyze.dll
│   │   └── ... (all plugins)
│   └── libs/                 # Dependencies (if needed)
│       └── ...
├── src/
└── ...
```

---

## ✅ Pros and Cons

### **✅ Advantages of Bundling**

1. **Better User Experience**
   - ✅ Single download and installation
   - ✅ No separate TSDuck installation required
   - ✅ Works immediately after installation
   - ✅ No path configuration needed

2. **Version Control**
   - ✅ You control which TSDuck version is used
   - ✅ Tested compatibility with your application
   - ✅ No version mismatch issues
   - ✅ Users can't break it by updating TSDuck

3. **Reduced Support Burden**
   - ✅ Fewer "TSDuck not found" errors
   - ✅ No path configuration issues
   - ✅ Guaranteed compatibility

4. **Easier Distribution**
   - ✅ Single installer/package
   - ✅ No external dependencies
   - ✅ Works on systems without TSDuck installed

5. **Professional Appearance**
   - ✅ More polished product
   - ✅ Self-contained application
   - ✅ Better for commercial distribution

---

### **❌ Disadvantages of Bundling**

1. **Increased File Size**
   - ⚠️ TSDuck binaries are large (~50-100 MB)
   - ⚠️ Your application package becomes bigger
   - ⚠️ Longer download times

2. **Licensing Complexity**
   - ⚠️ TSDuck is **GPL-licensed** (see Licensing section)
   - ⚠️ May require open-sourcing your application
   - ⚠️ Or purchasing commercial license from TSDuck

3. **Update Complexity**
   - ⚠️ To update TSDuck, you must rebuild your application
   - ⚠️ Can't leverage TSDuck updates independently
   - ⚠️ Must test new TSDuck versions before bundling

4. **Platform-Specific Binaries**
   - ⚠️ Need separate bundles for Windows, Linux, macOS
   - ⚠️ More complex build process
   - ⚠️ Larger repository size

5. **Disk Space**
   - ⚠️ Users get TSDuck even if they already have it
   - ⚠️ Duplicate installation on system

---

## ⚖️ Licensing Considerations

### **TSDuck License: GPL v2**

**Important:** TSDuck is licensed under **GNU GPL v2**, which has implications:

#### **GPL Requirements:**

1. **If you bundle GPL software, your application must also be GPL**
   - ✅ You must open-source your application code
   - ✅ Users must be able to access source code
   - ✅ You must provide GPL license text

2. **Commercial Use:**
   - ⚠️ You can still charge for your application
   - ⚠️ But users can redistribute it freely
   - ⚠️ Users can modify and redistribute

3. **Options:**

   **Option A: Open-Source Your Application**
   - ✅ Bundle TSDuck freely
   - ✅ Release your code under GPL
   - ✅ Users can modify and redistribute
   - ❌ Less control over distribution

   **Option B: Commercial License from TSDuck**
   - ✅ Purchase commercial license from TSDuck developers
   - ✅ Keep your application proprietary
   - ✅ Bundle TSDuck without GPL restrictions
   - ❌ Additional cost

   **Option C: Keep External Dependency**
   - ✅ No licensing issues
   - ✅ Keep your application proprietary
   - ❌ Users must install TSDuck separately

   **Option D: Dynamic Linking (Complex)**
   - ✅ Load TSDuck at runtime (not bundled)
   - ✅ May avoid GPL requirements (legal gray area)
   - ⚠️ Consult lawyer for compliance

---

### **Recommendation:**

**For Commercial Application:**
- **Best:** Keep TSDuck as external dependency (current approach)
- **Alternative:** Purchase commercial license from TSDuck if bundling is required

**For Open-Source Application:**
- **Best:** Bundle TSDuck and release under GPL

---

## 📦 File Size Impact

### **TSDuck Binary Sizes:**

**Windows:**
- `tsp.exe`: ~5-10 MB
- Plugins (all): ~20-30 MB
- Dependencies: ~10-20 MB
- **Total: ~50-100 MB**

**Linux:**
- `tsp`: ~5-10 MB
- Plugins: ~20-30 MB
- Dependencies: ~5-10 MB
- **Total: ~40-80 MB**

**macOS:**
- `tsp`: ~5-10 MB
- Plugins: ~20-30 MB
- Dependencies: ~10-20 MB
- **Total: ~50-100 MB**

### **Your Application Size:**

**Current (without TSDuck):**
- Python runtime: ~30-50 MB
- Your code: ~5-10 MB
- Dependencies: ~20-30 MB
- **Total: ~60-100 MB**

**With Bundled TSDuck:**
- Python runtime: ~30-50 MB
- Your code: ~5-10 MB
- Dependencies: ~20-30 MB
- **TSDuck: ~50-100 MB**
- **Total: ~120-200 MB**

**Impact:** ~2x larger download size

---

## 🖥️ Platform-Specific Considerations

### **Windows**

**Bundling:**
- ✅ Include `tsp.exe` and all `.dll` files
- ✅ Include Visual C++ runtime (if required)
- ✅ Test on Windows 10/11

**PyInstaller:**
```python
# IBE-100_Enterprise.spec
datas = [
    ('tsduck/bin/tsp.exe', 'tsduck/bin'),
    ('tsduck/plugins', 'tsduck/plugins'),
    ('tsduck/libs', 'tsduck/libs'),
]
```

---

### **Linux**

**Bundling:**
- ✅ Include `tsp` binary and `.so` files
- ✅ Include required system libraries
- ✅ May need AppImage or Snap for distribution

**Considerations:**
- Different distributions may need different binaries
- Consider static linking or AppImage format

---

### **macOS**

**Bundling:**
- ✅ Include `tsp` binary and `.dylib` files
- ✅ Create `.app` bundle
- ✅ Code signing required for distribution

**Considerations:**
- macOS Gatekeeper may block unsigned binaries
- Need Apple Developer certificate for distribution

---

## 🛠️ Implementation Steps

### **Step 1: Download TSDuck Binaries**

1. Download TSDuck for your target platform
2. Extract to a `tsduck/` folder in your project:
   ```
   IBE-100_v3.0_ENTERPRISE/
   └── tsduck/
       ├── bin/
       │   └── tsp.exe
       └── plugins/
           └── ... (all plugins)
   ```

---

### **Step 2: Modify TSDuckService**

**File:** `src/services/tsduck_service.py`

```python
import sys
from pathlib import Path

class TSDuckService:
    def __init__(self, tsduck_path: str = None):
        self.logger = get_logger("TSDuckService")
        
        if tsduck_path:
            self.tsduck_path = tsduck_path
        else:
            # Try bundled TSDuck first
            bundled_path = self._get_bundled_tsduck_path()
            if bundled_path and Path(bundled_path).exists():
                self.tsduck_path = bundled_path
                self.logger.info(f"Using bundled TSDuck: {self.tsduck_path}")
            else:
                # Fallback to system TSDuck
                self.tsduck_path = find_tsduck()
                self.logger.info(f"Using system TSDuck: {self.tsduck_path}")
    
    def _get_bundled_tsduck_path(self) -> Optional[str]:
        """Get path to bundled TSDuck executable"""
        if getattr(sys, 'frozen', False):
            # PyInstaller bundled mode
            base_path = Path(sys._MEIPASS)
        else:
            # Development mode
            base_path = Path(__file__).parent.parent.parent
        
        # Try different possible locations
        possible_paths = [
            base_path / "tsduck" / "bin" / "tsp.exe",  # Windows
            base_path / "tsduck" / "bin" / "tsp",      # Linux/macOS
            base_path.parent / "tsduck" / "bin" / "tsp.exe",
            base_path.parent / "tsduck" / "bin" / "tsp",
        ]
        
        for path in possible_paths:
            if path.exists():
                return str(path)
        
        return None
```

---

### **Step 3: Update PyInstaller Spec**

**File:** `IBE-100_Enterprise.spec`

```python
# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

# Add TSDuck binaries to datas
tsduck_bin = Path('tsduck/bin')
tsduck_plugins = Path('tsduck/plugins')
tsduck_libs = Path('tsduck/libs') if Path('tsduck/libs').exists() else None

datas = [
    ('tsduck/bin', 'tsduck/bin'),
    ('tsduck/plugins', 'tsduck/plugins'),
]

# Add libs if they exist
if tsduck_libs and tsduck_libs.exists():
    datas.append(('tsduck/libs', 'tsduck/libs'))

a = Analysis(
    ['main_enterprise.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='IBE-100_Enterprise',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```

---

### **Step 4: Set Environment Variables (if needed)**

Some TSDuck plugins may need environment variables:

```python
# In tsduck_service.py
import os

def _setup_tsduck_environment(self):
    """Set up environment variables for bundled TSDuck"""
    if getattr(sys, 'frozen', False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent.parent.parent
    
    tsduck_base = base_path / "tsduck"
    
    # Set TSDuck plugin path
    plugin_path = tsduck_base / "plugins"
    if plugin_path.exists():
        current_path = os.environ.get('PATH', '')
        os.environ['PATH'] = f"{plugin_path}{os.pathsep}{current_path}"
        
        # TSDuck-specific environment variable (if exists)
        os.environ['TSDUCK_PLUGIN_PATH'] = str(plugin_path)
```

---

### **Step 5: Update .gitignore**

```
# TSDuck binaries (too large for Git)
tsduck/bin/
tsduck/plugins/
tsduck/libs/
```

**Note:** Use Git LFS or download script instead of committing binaries.

---

### **Step 6: Create Download Script**

**File:** `scripts/download_tsduck.py`

```python
"""Download TSDuck binaries for bundling"""
import urllib.request
import zipfile
from pathlib import Path

def download_tsduck():
    """Download TSDuck for Windows"""
    url = "https://github.com/tsduck/tsduck/releases/download/v3.30/TSDuck-Win64-3.30-xxxx.zip"
    output_path = Path("tsduck.zip")
    
    print("Downloading TSDuck...")
    urllib.request.urlretrieve(url, output_path)
    
    print("Extracting...")
    with zipfile.ZipFile(output_path, 'r') as zip_ref:
        zip_ref.extractall("tsduck")
    
    print("Done!")
```

---

## 🔄 Alternative Approaches

### **Approach 1: Hybrid (Recommended)**

**Best of Both Worlds:**
- Try bundled TSDuck first
- Fallback to system TSDuck if bundled not found
- User can override with custom path

**Benefits:**
- ✅ Works out of the box (bundled)
- ✅ Users can use system TSDuck if preferred
- ✅ Flexible configuration

---

### **Approach 2: Optional Bundling**

**User Choice:**
- Provide two download options:
  - **Lite:** Without TSDuck (smaller, requires TSDuck installation)
  - **Full:** With TSDuck bundled (larger, self-contained)

**Benefits:**
- ✅ Users choose based on their needs
- ✅ Smaller download for users who have TSDuck
- ✅ Full package for new users

---

### **Approach 3: Installer with TSDuck**

**Separate Installer:**
- Create installer that includes TSDuck
- Installer extracts TSDuck to application folder
- Application uses local TSDuck

**Benefits:**
- ✅ Single installer
- ✅ TSDuck not in Git repository
- ✅ Can update TSDuck without rebuilding app

---

## 📊 Comparison Table

| Aspect | External TSDuck | Bundled TSDuck |
|--------|----------------|----------------|
| **File Size** | ~60-100 MB | ~120-200 MB |
| **Installation** | 2 steps | 1 step |
| **User Experience** | ⚠️ Requires TSDuck install | ✅ Works immediately |
| **Version Control** | ⚠️ User controls | ✅ You control |
| **Licensing** | ✅ No issues | ⚠️ GPL implications |
| **Updates** | ✅ Independent | ⚠️ Requires rebuild |
| **Support Issues** | ⚠️ More common | ✅ Fewer issues |
| **Distribution** | ⚠️ Two packages | ✅ Single package |

---

## 🎯 Recommendation

### **For Your Application:**

**Recommended: Hybrid Approach**

1. **Bundle TSDuck** in your application
2. **Fallback to system TSDuck** if bundled not found
3. **Allow user override** with custom path
4. **Handle licensing** appropriately (GPL or commercial license)

**Implementation Priority:**
1. ✅ Modify `TSDuckService` to check bundled path first
2. ✅ Update PyInstaller spec to include TSDuck binaries
3. ✅ Test on clean system (no TSDuck installed)
4. ✅ Test fallback to system TSDuck
5. ⚠️ Address licensing (GPL compliance or commercial license)

---

## ❓ FAQ

**Q: Can I bundle TSDuck without open-sourcing my app?**  
A: Only if you purchase a commercial license from TSDuck developers, or use dynamic linking (consult lawyer).

**Q: How do I update bundled TSDuck?**  
A: Download new TSDuck binaries, replace in `tsduck/` folder, rebuild application.

**Q: Will bundled TSDuck work on all Windows versions?**  
A: Usually yes, but test on Windows 10/11. May need different binaries for older Windows.

**Q: Can I bundle only specific plugins?**  
A: Yes, but TSDuck may require all plugins. Test thoroughly.

**Q: What if user already has TSDuck installed?**  
A: With hybrid approach, user can choose to use system TSDuck or bundled version.

---

## 🚀 Next Steps

1. **Decide on licensing approach** (GPL or commercial)
2. **Download TSDuck binaries** for your platform
3. **Modify TSDuckService** to support bundled TSDuck
4. **Update PyInstaller spec** to include binaries
5. **Test thoroughly** on clean system
6. **Update documentation** for users

**Ready to implement?** Let me know and I'll help you set it up! 🎯

