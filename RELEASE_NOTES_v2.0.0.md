# IBE-100 v2.0.0 Release Notes

## Release Date
January 2025

## Overview
IBE-100 v2.0 is a complete rebuild of the ITAssist Broadcast Encoder with a clean, professional implementation focusing on essential features and modern UI/UX.

## What's New

### ✨ Major Features
1. **Clean Architecture**: Complete rebuild from scratch with minimal, focused codebase
2. **Integrated Web Server**: Built-in web server for HLS/DASH local testing with CORS support
3. **Real-Time Monitoring**: System metrics, SCTE-35 status, and console output
4. **Manual Cue Generation**: Advanced SCTE-35 marker generation with scheduling
5. **Multi-Format Output**: Support for SRT, HLS, DASH, UDP, TCP, HTTP, and File output
6. **Configuration Management**: Save/load configurations as JSON files

### 🎨 UI/UX Improvements
- Modern dark theme with professional styling
- Scrollable content areas for better visibility
- White input fields with black text for readability
- Integrated logo and branding
- Tab-based interface for organized workflow
- Real-time status indicators

### 🔧 Technical Improvements
- Automatic TSDuck path detection
- Dynamic SCTE-35 marker detection (no hardcoded values)
- Process management with proper cleanup
- Error handling and validation
- CORS support for web-based testing

### 🌐 Web Server Integration
- **Built-in Server**: No external Python scripts needed
- **One-Click Start/Stop**: Simple button controls
- **Configurable Port**: 8000-9999 range
- **Directory Selection**: Serve any output directory
- **CORS Headers**: Automatic cross-origin support
- **Status Display**: Real-time server status

### 📊 Monitoring Features
- **Console Tab**: Real-time TSDuck output
- **SCTE-35 Status**: Marker monitoring and detection
- **System Metrics**: CPU, Memory, Disk usage
- **Web Server**: Control and monitor local server

### 🎬 SCTE-35 Features
- **Manual Cue Types**: Pre-roll, CUE-OUT, CUE-IN, Time Signal
- **Scheduling**: Scheduled or immediate cue injection
- **Template System**: Organized marker templates
- **Dynamic Detection**: Latest marker auto-detection

### 📡 Stream Configuration
- **Input Formats**: HLS, SRT, UDP, TCP, HTTP/HTTPS, DVB, ASI
- **Output Formats**: SRT, HLS, DASH, UDP, TCP, HTTP/HTTPS, File
- **Service Configuration**: Service Name, Provider, Service ID
- **PID Configuration**: Video, Audio, SCTE-35 PIDs
- **SRT Parameters**: Stream ID and Latency
- **HLS/DASH Settings**: Segment duration, Playlist window, CORS

## Files Included
- `IBE-100.exe` - Main executable
- `logo.png` - Application icon
- `scte35_final/` - SCTE-35 marker directory
- `test_player.html` - Web test player
- `serve_hls.py` - Standalone web server (optional)

## Usage

### Quick Start
1. Launch `IBE-100.exe`
2. Configure input stream in "Stream Configuration" tab
3. Set output type and destination
4. Generate SCTE-35 markers in "SCTE-35" tab
5. Start processing from main controls
6. Monitor in "Monitoring" tab

### HLS/DASH Testing
1. Set Output Type to "HLS" or "DASH"
2. Set Output Directory (e.g., `output/hls`)
3. Enable CORS Headers
4. Start processing
5. Go to Monitoring → Web Server tab
6. Click "Start Web Server"
7. Open `test_player.html` in browser
8. Enter stream URL and click Load

### Web Server
- Navigate to **Monitoring → Web Server** tab
- Set Port (default: 8000)
- Set Serving Directory
- Click **Start Web Server**
- Access at `http://localhost:8000`

## Technical Details

### System Requirements
- Windows 10/11
- Python 3.8+ (for development)
- TSDuck installed in standard location
- 4GB RAM minimum
- Network connection for streaming

### Dependencies
- PyQt6 (GUI framework)
- psutil (system metrics)
- Pillow (icon generation)
- PyInstaller (packaging)

### Build Information
- Version: 2.0.0
- Architecture: x86_64
- Build Tool: PyInstaller (onefile)
- Icon: Embedded (logo.ico)

## Configuration File Format

```json
{
  "input_type": "HLS (HTTP Live Streaming)",
  "input_url": "https://cdn.example.com/stream.m3u8",
  "output_type": "SRT",
  "output_srt": "cdn.example.com:8888",
  "service_name": "SCTE-35 Stream",
  "service_id": 1,
  "vpid": 256,
  "apid": 257,
  "scte35_pid": 500,
  "stream_id": "#!::r=scte/scte,m=publish",
  "latency": 2000,
  "start_delay": 2000,
  "inject_count": 1,
  "inject_interval": 1000
}
```

## Breaking Changes
- Previous v1.x configuration files are NOT compatible
- New JSON format for configuration files
- Redesigned UI layout
- Changed file structure

## Migration Guide
1. **Backup** your current configuration
2. **Export** any custom SCTE-35 markers
3. **Install** IBE-100 v2.0
4. **Configure** stream settings from scratch
5. **Import** custom SCTE-35 markers to `scte35_final/` directory

## Known Issues
- None reported

## Future Roadmap
- Multiple output streams simultaneously
- Preview player within application
- Advanced error recovery
- Cloud streaming integration
- Mobile companion app

## Support
- Documentation: Included in release
- Email: support@itassist.one
- Website: https://www.itassist.one

## Changelog

### v2.0.0 (January 2025)
- ✨ Complete rebuild from scratch
- ✨ Integrated web server
- ✨ Real-time monitoring dashboard
- ✨ Manual SCTE-35 cue generation
- ✨ Multi-format output support
- ✨ Configuration save/load
- 🎨 Modern dark theme UI
- 🔧 Improved TSDuck integration
- 📊 System metrics display
- 🌐 CORS support for web testing
- 🛠️ Automatic TSDuck detection

---

**© 2024 ITAssist Broadcast Solutions**  
**All Rights Reserved**

