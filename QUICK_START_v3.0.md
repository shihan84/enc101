# IBE-100 v3.0 Enterprise - Quick Start Guide

## 🚀 Getting Started

### Current Status
- ✅ Virtual environment configured
- ✅ Dependencies installed (PyQt6, psutil, PyInstaller)
- ✅ Application ready for development

### Running the Application

#### Option 1: Direct Python Execution
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run the application
python main.py
```

#### Option 2: Build Executable
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Build executable
pyinstaller IBE-100.spec

# Run from dist folder
.\dist\IBE-100\IBE-100.exe
```

## 📁 Project Structure

```
IBE-100_v3.0_ENTERPRISE/
├── main.py                 # Main application entry point
├── profile_manager.py      # Profile management system
├── requirements.txt        # Python dependencies
├── IBE-100.spec           # PyInstaller build spec
├── src/                    # Modular source structure (for future expansion)
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── services/
│   ├── ui/
│   └── utils/
├── profiles/               # Saved configuration profiles
├── scte35_final/          # Generated SCTE-35 markers
├── output/                # Stream output directory
│   ├── hls/              # HLS segments
│   └── dash/              # DASH segments
├── dist/                  # Build output
├── dist_final/            # Final distribution package
└── logs/                  # Application logs
```

## 🎯 Key Features

### 1. Stream Configuration
- Multiple input formats (HLS, SRT, UDP, TCP, HTTP/HTTPS, DVB, ASI)
- Multiple output formats (SRT, HLS, DASH, UDP, TCP, HTTP/HTTPS, File)
- Service configuration (Name, Provider, Service ID)
- PID configuration (Video, Audio, SCTE-35)

### 2. SCTE-35 Marker Generation
- Manual cue types (Pre-roll, CUE-OUT, CUE-IN, Time Signal)
- Scheduling support (Immediate or time-based)
- Dynamic marker file generation

### 3. Profile Management
- Save/load stream configurations
- Multiple profile support
- Profile templates included

### 4. Monitoring Dashboard
- Real-time console output
- SCTE-35 status monitoring
- System metrics (CPU, Memory, Disk)
- Integrated web server for HLS/DASH testing

### 5. Web Server Integration
- Built-in CORS-enabled HTTP server
- One-click start/stop
- Configurable port and directory

## 🔧 Development Workflow

### 1. Activate Environment
```powershell
cd "E:\NEW DOWNLOADS\Enc-100\Encoder-100\IBE-100_v3.0_ENTERPRISE"
.\venv\Scripts\Activate.ps1
```

### 2. Install/Update Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Run Application
```powershell
python main.py
```

### 4. Make Changes
- Edit `main.py` for main application logic
- Edit `profile_manager.py` for profile management
- Add modules to `src/` for modular expansion

### 5. Build Executable
```powershell
pyinstaller IBE-100.spec
```

## 📋 Prerequisites

### Required
- ✅ Python 3.13.5 (installed)
- ✅ TSDuck (must be installed separately)
  - Download from: https://tsduck.io/download/
  - Install to: `C:\Program Files\TSDuck\bin\`
  - Verify: `tsp --version`

### Optional
- FFmpeg (for advanced stream processing)
- Network access (for streaming)

## 🎨 Application Tabs

### 1. Configuration Tab
- Input/Output stream settings
- Service configuration
- PID settings
- SRT parameters
- HLS/DASH settings
- SCTE-35 injection settings
- Profile management

### 2. SCTE-35 Tab
- Marker generation
- Cue type selection
- Scheduling options
- Event ID configuration

### 3. Monitoring Tab
- **Console**: Real-time TSDuck output
- **SCTE-35 Status**: Marker monitoring
- **System Metrics**: CPU, Memory, Disk usage
- **Web Server**: Local server control

## 🚦 Quick Test

1. **Start Application**
   ```powershell
   python main.py
   ```

2. **Configure Stream**
   - Set Input Type: HLS
   - Set Input URL: `https://cdn.itassist.one/BREAKING/NEWS/index.m3u8`
   - Set Output Type: SRT
   - Set Output SRT: `cdn.itassist.one:8888`

3. **Generate SCTE-35 Marker**
   - Go to SCTE-35 tab
   - Click "Generate SCTE-35 Marker"

4. **Start Processing**
   - Click "Preview Command" to verify
   - Click "Start Processing"

5. **Monitor**
   - Check Monitoring tab for real-time output

## 📝 Configuration Files

### Profiles
- Location: `profiles/profiles.json`
- Format: JSON
- Contains: Stream configurations, service settings, PIDs

### SCTE-35 Markers
- Location: `scte35_final/`
- Format: XML (for TSDuck) + JSON (metadata)
- Naming: `{cue_type}_{event_id}_{timestamp}.xml`

### Logs
- Location: `logs/`
- Files: `IBE100.log`, `IBE100_errors.log`, `IBE100_structured.json`

## 🔍 Troubleshooting

### TSDuck Not Found
- Install TSDuck from official website
- Verify installation: `tsp --version`
- Check PATH environment variable

### Import Errors
- Activate virtual environment: `.\venv\Scripts\Activate.ps1`
- Install dependencies: `pip install -r requirements.txt`

### Port Already in Use
- Change web server port in Monitoring tab
- Or stop conflicting application

## 📚 Documentation

- `FEATURE_CHECKLIST.md` - Feature implementation status
- `FINAL_FEATURE_SUMMARY.md` - Complete feature list
- `FINAL_SUMMARY.md` - Build summary
- `HLS_DASH_GUIDE.md` - HLS/DASH usage guide
- `WEB_SERVER_FEATURE.md` - Web server documentation
- `dist_final/README.md` - User documentation

## 🎯 Next Steps

1. **Test Application**: Run `python main.py` and verify all features
2. **Configure Streams**: Set up your input/output configurations
3. **Generate Markers**: Create SCTE-35 markers for testing
4. **Build Executable**: Create distributable package
5. **Deploy**: Use `dist_final/` for production deployment

## 📞 Support

- **Documentation**: See included .md files
- **Version**: v3.0 Enterprise (based on v2.0.4 codebase)
- **Status**: Ready for development and testing

---

**Last Updated**: January 2025  
**Environment**: Windows 10/11  
**Python**: 3.13.5  
**Status**: ✅ Ready for Development

