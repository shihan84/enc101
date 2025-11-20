# IBE-100 v2.0.0 - Installation & Usage Guide

## 🎉 Welcome to IBE-100 v2.0

**ITAssist Broadcast Encoder - 100 (IBE-100)** is a professional TSDuck-based streaming encoder with integrated SCTE-35 support for ad insertion and program cues.

## 📦 Installation

### Requirements
- Windows 10/11 (64-bit)
- TSDuck installed in standard location (C:\Program Files\TSDuck\bin\)
- 4GB RAM minimum (8GB recommended)
- Network connection for streaming

### Quick Prerequisite Check
**Before deploying to a new system, run:**
```cmd
check_prerequisites.bat
```

This will verify:
- ✅ TSDuck installation
- ✅ Required plugins
- ✅ Network connectivity
- ✅ File permissions
- ✅ System resources

### Installation Steps
1. **Check prerequisites** (recommended): Run `check_prerequisites.bat`
2. **Extract** this folder to your desired location
3. **Launch** using: `launch_ibe100_v2.0.1.bat` or double-click `IBE-100.exe`
4. **Configure** your stream settings
5. **Start** processing

## 🚀 Quick Start

### 1. Stream Configuration Tab
- **Input Type**: Select your input format (HLS, SRT, etc.)
- **Stream URL**: Enter your input stream URL
- **Output Type**: Choose output format (SRT, HLS, DASH)
- **Destination**: Set output destination
- **Service Config**: Configure service name, provider, IDs
- **PIDs**: Set Video, Audio, and SCTE-35 PIDs

### 2. SCTE-35 Tab
- **Manual Cue**: Select cue type (Pre-roll, CUE-OUT, etc.)
- **Schedule**: Set time or enable "Immediate Cue"
- **Generate**: Click to create marker
- **Templates**: Use pre-configured templates

### 3. Start Processing
- **Preview**: Check TSDuck command
- **Start**: Begin stream processing
- **Stop**: Terminate stream

### 4. Monitoring Tab
- **Console**: Real-time TSDuck output
- **SCTE-35 Status**: Marker monitoring
- **System Metrics**: CPU, Memory, Disk usage
- **Web Server**: For HLS/DASH testing

## 🌐 Web Server for HLS/DASH

### Using Built-in Web Server

1. **Generate** HLS/DASH content:
   - Set Output Type to "HLS" or "DASH"
   - Set output directory
   - Enable CORS Headers
   - Start processing

2. **Start Web Server**:
   - Navigate to Monitoring → Web Server tab
   - Set Port (default: 8000)
   - Set Serving Directory (match output directory)
   - Click **Start Web Server**

3. **Test** in browser:
   - Open `test_player.html`
   - Enter URL: `http://localhost:8000/stream.m3u8`
   - Click "Load Stream" and "Play"

### Using Standalone Server

Alternatively, use the included `serve_hls.py`:

```bash
python serve_hls.py 8000 output/hls
```

Then access at `http://localhost:8000`

## 📋 Features

### ✨ Core Features
- ✅ Multiple input formats (HLS, SRT, UDP, TCP, HTTP, DVB, ASI)
- ✅ Multiple output formats (SRT, HLS, DASH, UDP, TCP, HTTP, File)
- ✅ SCTE-35 marker generation
- ✅ Real-time monitoring
- ✅ Integrated web server
- ✅ Configuration save/load

### 🎯 Advanced Features
- Manual cue generation with scheduling
- Dynamic marker detection
- System metrics display
- CORS support for web testing
- Automatic TSDuck detection

## 📚 Documentation

- **RELEASE_NOTES_v2.0.0.md** - Complete release notes
- **PRE_REQUISITE_CHECKLIST.md** - Pre-deployment requirements
- **DEPLOYMENT_TROUBLESHOOTING_v2.0.1.md** - Troubleshooting guide
- **test_player.html** - Browser test player
- **serve_hls.py** - Standalone web server

### Diagnostic Tools
- **check_prerequisites.bat** - Pre-deployment verification
- **diagnose_system.bat** - System diagnostics
- **launch_ibe100_v2.0.1.bat** - Launch with pre-flight checks

## 🔧 Configuration

### Save Configuration
1. Configure all settings
2. Click **Save Config**
3. Enter filename
4. Configuration saved as JSON

### Load Configuration
1. Click **Load Config**
2. Select JSON file
3. All settings restored

## 🆘 Troubleshooting

### Pre-Deployment Checks
**Run these diagnostic tools:**
1. `check_prerequisites.bat` - Verify all prerequisites
2. `diagnose_system.bat` - Detailed system diagnostics

### TSDuck Not Found
- Install TSDuck: https://tsduck.io/download/
- Add to PATH: `set PATH=%PATH%;C:\Program Files\TSDuck\bin`
- Verify: `tsp --version` works

### Error Code 1 (Most Common)
**Cause:** TSDuck not installed or not in PATH  
**Solution:**
1. Install TSDuck from official website
2. Verify: `tsp --version`
3. Add to PATH if needed
4. See `DEPLOYMENT_TROUBLESHOOTING_v2.0.1.md` for details

### CORS Errors
- Enable "Enable CORS Headers" in configuration
- Or use built-in web server

### Port Already in Use
- Change port in Web Server settings
- Or stop conflicting application

### Stream Not Starting
- Check input URL
- Verify network connection
- Check console for errors
- Run diagnostic tools for detailed analysis

## 📞 Support

- **Documentation**: See RELEASE_NOTES_v2.0.0.md
- **Email**: support@itassist.one
- **Website**: https://www.itassist.one

## 📄 License

© 2024 ITAssist Broadcast Solutions  
All Rights Reserved

---

**Version**: 2.0.0  
**Build Date**: January 2025  
**Status**: Production Ready ✅

