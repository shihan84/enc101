# TSDuck Binaries for IBE-210

This directory contains bundled TSDuck binaries for IBE-210 Enterprise.

## Structure

```
tsduck/
├── bin/
│   └── tsp.exe          # TSDuck main executable
├── plugins/
│   ├── spliceinject.dll
│   ├── splicemonitor.dll
│   ├── analyze.dll
│   └── ... (other plugins)
└── libs/                # Dependencies (if needed)
```

## Setup

### Automatic Setup (Recommended)

Run the download script:

```powershell
python scripts\download_tsduck.py
```

This will:
1. Download TSDuck for your platform
2. Extract and organize files
3. Place them in the correct structure

### Manual Setup

1. Download TSDuck from: https://tsduck.io/download/tsduck/
2. Extract the ZIP file
3. Copy `tsp.exe` (or `tsp` on Linux/macOS) to `tsduck/bin/`
4. Copy all plugin DLLs (`.dll` on Windows, `.so` on Linux) to `tsduck/plugins/`
5. Copy any required dependencies to `tsduck/libs/` (if needed)

## Building with Bundled TSDuck

After setting up TSDuck binaries, build the application:

```powershell
pyinstaller IBE-210_Enterprise.spec
```

The PyInstaller spec file will automatically include TSDuck binaries if they exist in this directory.

## How It Works

IBE-210 uses a **hybrid approach**:

1. **First**: Tries to use bundled TSDuck (from this directory)
2. **Fallback**: Uses system TSDuck if bundled not found
3. **Override**: User can specify custom TSDuck path in settings

This ensures:
- ✅ Works out of the box (bundled TSDuck)
- ✅ Flexible (can use system TSDuck)
- ✅ User control (custom path option)

## Licensing

**Important**: TSDuck is licensed under **GNU GPL v2**.

If you bundle TSDuck with your application:
- Your application must also be GPL (open-source), OR
- Purchase a commercial license from TSDuck developers

See `TSDUCK_BUNDLING_GUIDE.md` for more information.

## Notes

- TSDuck binaries are **not** committed to Git (too large)
- Use Git LFS or download script for distribution
- Update TSDuck by replacing files in this directory and rebuilding

