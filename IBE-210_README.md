# IBE-210 Enterprise v2.1.0

## 🎯 What's New in IBE-210

**IBE-210** is the next generation of the IBE broadcast encoder with **bundled TSDuck support**.

### ✨ Key Features

1. **Bundled TSDuck** 🎁
   - TSDuck binaries included in the application package
   - No separate TSDuck installation required
   - Works out of the box
   - Hybrid approach: Uses bundled TSDuck first, falls back to system TSDuck

2. **All Features from IBE-100 v3.0**
   - SCTE-35 marker injection and monitoring
   - Real-time stream analysis
   - EPG/EIT generation
   - Telegram notifications
   - Profile management
   - REST API
   - And more...

## 📦 Installation

### Option 1: Pre-built Package (Recommended)

1. Download the IBE-210 installer/package
2. Run the installer
3. **That's it!** TSDuck is already included

### Option 2: Build from Source

1. **Clone or download this repository**
2. **Set up TSDuck binaries:**
   ```powershell
   python scripts\download_tsduck.py
   ```
3. **Install Python dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```
4. **Build the application:**
   ```powershell
   pyinstaller IBE-210_Enterprise.spec
   ```
5. **Run from `dist/IBE-210_Enterprise.exe`**

## 🔧 TSDuck Setup

### Automatic Setup

Run the download script:
```powershell
python scripts\download_tsduck.py
```

### Manual Setup

1. Download TSDuck from: https://tsduck.io/download/tsduck/
2. Extract to `tsduck/` folder:
   ```
   tsduck/
   ├── bin/
   │   └── tsp.exe
   └── plugins/
       └── ... (all plugin DLLs)
   ```

See `tsduck/README.md` for detailed instructions.

## 🚀 Quick Start

1. **Launch IBE-210**
2. **Configure your stream** (Input/Output settings)
3. **Start streaming** - TSDuck is ready to use!

No need to install TSDuck separately!

## 📋 System Requirements

- **Windows 10/11** (64-bit)
- **Python 3.9+** (for building from source)
- **TSDuck**: Included (bundled) or install separately

## 🔄 How Bundled TSDuck Works

IBE-210 uses a **hybrid approach**:

1. **First Priority**: Bundled TSDuck (included in package)
2. **Second Priority**: System TSDuck (if installed)
3. **Third Priority**: Custom path (user-specified)

This ensures maximum compatibility and flexibility.

## 📝 Version History

### v2.1.0 (IBE-210)
- ✨ Added bundled TSDuck support
- ✨ Hybrid TSDuck detection (bundled → system → custom)
- 🔧 Improved TSDuck environment setup
- 📦 Larger package size (~200 MB with TSDuck)

### v3.0.0 (IBE-100)
- All previous features
- Production-ready
- Comprehensive testing

## ⚖️ Licensing

**Important**: TSDuck is licensed under **GNU GPL v2**.

If you bundle TSDuck:
- Your application must be GPL (open-source), OR
- Purchase commercial license from TSDuck developers

See `TSDUCK_BUNDLING_GUIDE.md` for details.

## 🆘 Troubleshooting

### TSDuck Not Found

**If bundled TSDuck is missing:**
1. Run `python scripts\download_tsduck.py`
2. Rebuild the application
3. Or install TSDuck separately and use system version

### Build Errors

**If PyInstaller fails:**
1. Ensure TSDuck binaries are in `tsduck/` folder
2. Check that `tsp.exe` exists in `tsduck/bin/`
3. Verify plugins are in `tsduck/plugins/`

### Runtime Errors

**If application can't find TSDuck:**
1. Check logs for TSDuck path
2. Verify bundled TSDuck files are included in build
3. Try specifying custom TSDuck path in settings

## 📚 Documentation

- **User Manual**: `USER_MANUAL.md`
- **Installation Guide**: `INSTALLATION_GUIDE.md`
- **TSDuck Bundling Guide**: `TSDUCK_BUNDLING_GUIDE.md`
- **Licensing Guide**: `LICENSING_IMPLEMENTATION_GUIDE.md`

## 🤝 Support

For issues, questions, or contributions:
- Check documentation in the `docs/` folder
- Review troubleshooting guides
- Contact support (if available)

## 📄 License

See LICENSE file for details.

**Note**: If TSDuck is bundled, GPL v2 applies. See `TSDUCK_BUNDLING_GUIDE.md`.

---

**IBE-210 Enterprise** - Professional Broadcast Encoding Made Easy 🚀

