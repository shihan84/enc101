# IBE-210 Build Instructions
## Building with Bundled TSDuck

---

## 📋 Prerequisites

1. **Python 3.9+** installed
2. **PyInstaller** installed: `pip install pyinstaller`
3. **All dependencies** installed: `pip install -r requirements.txt`

---

## 🚀 Quick Build (Without TSDuck)

If you want to build without bundled TSDuck (uses system TSDuck):

```powershell
cd IBE-210
pyinstaller IBE-210_Enterprise.spec
```

The application will use system TSDuck if available.

---

## 📦 Full Build (With Bundled TSDuck)

### Step 1: Download TSDuck Binaries

**Option A: Automatic Download (Recommended)**

```powershell
python scripts\download_tsduck.py
```

This will:
- Download TSDuck for your platform
- Extract and organize files
- Place them in `tsduck/` folder

**Option B: Manual Download**

1. Download TSDuck from: https://tsduck.io/download/tsduck/
2. Extract the ZIP file
3. Copy files:
   - `tsp.exe` → `tsduck/bin/tsp.exe`
   - All `.dll` files from `plugins/` → `tsduck/plugins/`

### Step 2: Verify TSDuck Structure

Ensure you have:

```
IBE-210/
└── tsduck/
    ├── bin/
    │   └── tsp.exe          ✅ Must exist
    └── plugins/
        ├── spliceinject.dll ✅ Must exist
        ├── splicemonitor.dll ✅ Must exist
        ├── analyze.dll      ✅ Must exist
        └── ... (other plugins)
```

### Step 3: Build Application

```powershell
pyinstaller IBE-210_Enterprise.spec
```

The spec file will automatically:
- Detect TSDuck binaries in `tsduck/` folder
- Include them in the build
- Bundle them with the application

### Step 4: Verify Build

Check the output:

```
dist/
└── IBE-210_Enterprise.exe    ✅ Main executable
    └── (TSDuck binaries included inside)
```

### Step 5: Test

Run the application:

```powershell
.\dist\IBE-210_Enterprise.exe
```

The application should:
- ✅ Start without errors
- ✅ Detect bundled TSDuck automatically
- ✅ Work without requiring separate TSDuck installation

---

## 🔍 Build Verification

### Check TSDuck Detection

1. Launch IBE-210
2. Check logs for:
   ```
   [INFO] Using bundled TSDuck: C:\...\tsduck\bin\tsp.exe
   ```
3. Or check Configuration tab → TSDuck Path should show bundled path

### Test TSDuck Functionality

1. Configure a stream
2. Start streaming
3. Verify TSDuck processes are running
4. Check stream output

---

## 📊 Build Output

### File Sizes

**Without TSDuck:**
- `IBE-210_Enterprise.exe`: ~60-100 MB

**With Bundled TSDuck:**
- `IBE-210_Enterprise.exe`: ~120-200 MB

### Build Time

- **First build**: 2-5 minutes
- **Incremental builds**: 30 seconds - 2 minutes

---

## ⚠️ Troubleshooting

### Error: TSDuck binaries not found

**Problem:** PyInstaller can't find TSDuck files

**Solution:**
1. Verify `tsduck/bin/tsp.exe` exists
2. Check file paths in spec file
3. Ensure you're running from IBE-210 directory

### Error: TSDuck plugins not loading

**Problem:** Plugins not found at runtime

**Solution:**
1. Verify all plugin DLLs are in `tsduck/plugins/`
2. Check environment variables in `tsduck_service.py`
3. Ensure plugins are included in PyInstaller build

### Error: Application can't find TSDuck

**Problem:** Runtime error - TSDuck not found

**Solution:**
1. Check logs for TSDuck path
2. Verify bundled TSDuck is included in build
3. Try using system TSDuck as fallback

### Build Fails with ModuleNotFoundError

**Problem:** PyInstaller can't find modules

**Solution:**
1. Ensure all dependencies are installed
2. Check `hiddenimports` in spec file
3. Verify `src/` directory structure

---

## 🔄 Updating TSDuck

To update bundled TSDuck:

1. **Download new TSDuck version**
2. **Replace files** in `tsduck/` folder:
   - Update `tsduck/bin/tsp.exe`
   - Update plugins in `tsduck/plugins/`
3. **Rebuild application:**
   ```powershell
   pyinstaller IBE-210_Enterprise.spec --clean
   ```

---

## 📝 Build Configuration

### Spec File Location

`IBE-210_Enterprise.spec`

### Key Settings

- **Name**: `IBE-210_Enterprise`
- **Console**: `False` (no console window)
- **Icon**: `logo.ico` (if exists)
- **TSDuck**: Automatically included if `tsduck/` folder exists

### Customization

Edit `IBE-210_Enterprise.spec` to:
- Change application name
- Add/remove files
- Modify build options
- Adjust compression settings

---

## ✅ Build Checklist

Before building:

- [ ] Python 3.9+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] PyInstaller installed
- [ ] TSDuck binaries downloaded (if bundling)
- [ ] TSDuck structure verified (`tsduck/bin/tsp.exe` exists)
- [ ] All source files present
- [ ] Logo/icon files present (optional)

After building:

- [ ] Build completed without errors
- [ ] Executable created in `dist/`
- [ ] Application launches successfully
- [ ] TSDuck detected (check logs)
- [ ] Stream functionality works
- [ ] All features tested

---

## 🎯 Next Steps

After successful build:

1. **Test the application** thoroughly
2. **Create installer** (optional, using Inno Setup, NSIS, etc.)
3. **Package for distribution**
4. **Update documentation** if needed

---

## 📚 Related Documentation

- **IBE-210 README**: `IBE-210_README.md`
- **TSDuck Setup**: `tsduck/README.md`
- **TSDuck Bundling Guide**: `TSDUCK_BUNDLING_GUIDE.md`
- **User Manual**: `USER_MANUAL.md`

---

**Ready to build?** Follow the steps above and you'll have IBE-210 with bundled TSDuck! 🚀

