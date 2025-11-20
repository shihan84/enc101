# 📖 Broadcast Encoder 110 - User Manual

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [Configuration](#configuration)
5. [Stream Processing](#stream-processing)
6. [SCTE-35 Markers](#scte-35-markers)
7. [EPG Editor](#epg-editor)
8. [Monitoring](#monitoring)
9. [Telegram Notifications](#telegram-notifications)
10. [Troubleshooting](#troubleshooting)

---

## Introduction

**Broadcast Encoder 110** is an enterprise-grade broadcast encoder application for processing and streaming video content with SCTE-35 marker injection, EPG generation, and real-time monitoring.

### Key Features
- ✅ Multi-format stream processing (HLS, SRT, UDP, TCP, HTTP/HTTPS, DVB, ASI)
- ✅ SCTE-35 marker generation and injection
- ✅ EPG/EIT generation and management
- ✅ Real-time stream quality monitoring
- ✅ Bitrate monitoring with alerts
- ✅ Telegram notifications
- ✅ Profile management
- ✅ REST API for automation

---

## Installation

### System Requirements
- **OS:** Windows 10/11 (64-bit)
- **RAM:** 4GB minimum (8GB recommended)
- **Disk Space:** 500MB for application + logs
- **TSDuck:** Version 3.30 or later (must be installed separately)

### Installing TSDuck

1. Download TSDuck from: https://tsduck.io/download/tsduck/
2. Install TSDuck to default location: `C:\Program Files\TSDuck\`
3. Verify installation:
   ```cmd
   tsp --version
   ```

### Installing Broadcast Encoder 110

1. Extract the application archive to your desired location
2. Run `IBE-100_Enterprise.exe`
3. The application will create necessary directories on first run:
   - `logs/` - Application logs
   - `config/` - Configuration files
   - `profiles/` - Stream profiles
   - `scte35_final/` - SCTE-35 markers
   - `epg/` - EPG files
   - `database/` - Session database

---

## Getting Started

### First Launch

1. **Start the Application**
   - Double-click `IBE-100_Enterprise.exe`
   - The main window will open with the Dashboard tab

2. **Configure TSDuck Path** (if needed)
   - Go to Configuration tab
   - If TSDuck is not in default location, configure the path

3. **Set Up Telegram Notifications** (optional)
   - Go to Monitoring tab → SCTE-35 Monitor
   - Click "Configure Telegram"
   - Enter Bot Token and Chat ID
   - Click "Test Connection"

### Basic Workflow

1. **Configure Stream**
   - Go to Configuration tab
   - Set Input URL (e.g., HLS, SRT, UDP)
   - Set Output type and destination
   - Configure SRT settings if using SRT output

2. **Generate SCTE-35 Marker** (optional)
   - Go to SCTE-35 tab
   - Select cue type (PREROLL, CUE-OUT, CUE-IN)
   - Configure parameters
   - Click "Generate Marker"

3. **Start Stream**
   - Click "▶️ Start Processing" button
   - Monitor progress in Monitoring tab

4. **Stop Stream**
   - Click "⏹️ Stop" button

---

## Configuration

### Stream Configuration

#### Input Types
- **HLS:** HTTP Live Streaming (e.g., `http://server.com/playlist.m3u8`)
- **SRT:** Secure Reliable Transport (e.g., `srt://server.com:8888`)
- **UDP:** UDP multicast/unicast (e.g., `udp://239.255.1.1:5000`)
- **TCP:** TCP stream (e.g., `tcp://server.com:5000`)
- **HTTP/HTTPS:** HTTP stream (e.g., `http://server.com/stream.ts`)
- **File:** Local file (e.g., `file://C:/path/to/file.ts`)

#### Output Types
- **SRT:** Secure Reliable Transport
  - Destination: `server.com:8888`
  - Stream ID: Optional (e.g., `#!::r=scte/scte,m=publish`)
  - Latency: 100-10000 ms (default: 2000)

#### Service Parameters
- **Service ID:** 1-65535 (default: 1)
- **Video PID:** 32-8190 (default: 256)
- **Audio PID:** 32-8190 (default: 257)
- **SCTE-35 PID:** 32-8190 (default: 500)

### Profile Management

**Save Profile:**
1. Configure stream settings
2. Click "💾 Save Profile"
3. Enter profile name
4. Click "Save"

**Load Profile:**
1. Select profile from dropdown
2. Click "📂 Load Profile"
3. Settings will be applied automatically

**Note:** Each profile has its own SCTE-35 marker directory and event ID sequence.

---

## Stream Processing

### Starting a Stream

1. **Configure Input/Output**
   - Set input URL
   - Set output type and destination
   - Configure service parameters

2. **Select SCTE-35 Marker** (optional)
   - Generate or select existing marker
   - Marker will be automatically used when stream starts

3. **Start Processing**
   - Click "▶️ Start Processing"
   - Confirm marker selection if marker is active
   - Stream will start processing

### Monitoring Stream Status

**Dashboard Tab:**
- Real-time statistics
- Quick actions
- System status

**Monitoring Tab:**
- **Console:** TSDuck output and logs
- **Metrics:** System metrics (CPU, Memory, Disk)
- **Status:** Stream session status
- **SCTE-35:** SCTE-35 event monitoring
- **Quality:** Stream quality analysis
- **Bitrate:** Bitrate monitoring

### Stream Status Indicators

- **Starting:** Stream is initializing
- **Running:** Stream is active and processing
- **Stopped:** Stream has stopped
- **Error:** Stream encountered an error (will auto-retry)

---

## SCTE-35 Markers

### Marker Types

1. **PREROLL** - Program transition marker
   - Generates: CUE-OUT, CUE-IN, CUE-CRASH sequence
   - Pre-roll duration: 4-10 seconds (recommended: 4.0)

2. **CUE-OUT** - Ad break start
   - Signals start of ad insertion opportunity

3. **CUE-IN** - Ad break end
   - Signals end of ad insertion

4. **CUE-CRASH** - Emergency return
   - Emergency return to program

5. **TIME_SIGNAL** - Time-based signal

### Generating Markers

1. **Basic Marker:**
   - Select cue type
   - Set event ID (or enable Auto Increment)
   - Configure ad duration
   - Click "🎯 Generate Marker"

2. **CUE Pair:**
   - Click "🎬 Generate CUE Pair"
   - Generates CUE-OUT and CUE-IN with sequential IDs

3. **Preroll Sequence:**
   - Select PREROLL cue type
   - Configure pre-roll duration (min: 4.0 seconds)
   - Click "🎯 Generate Marker"
   - Automatically generates CUE-OUT, CUE-IN, and CUE-CRASH

### Event ID Management

- **Auto Increment:** Automatically generates sequential event IDs
- **Manual:** Set specific event ID (10000-99999)
- **Profile-Specific:** Each profile maintains its own event ID sequence
- **State Persistence:** Event IDs are saved and restored on restart

### Marker Files

Markers are saved to:
- **Default Profile:** `scte35_final/`
- **Named Profiles:** `scte35_final/{profile_name}/`

Each marker includes:
- XML file (for TSDuck)
- JSON metadata file

---

## EPG Editor

### Creating EPG Events

1. **Basic Event:**
   - Enter event title
   - Set start time and duration
   - Select content type
   - Click "➕ Add"

2. **Extended Metadata:**
   - Enable "Extended Info" section
   - Add director, actors, year, rating, etc.
   - Configure season/episode information

3. **Recurring Events:**
   - Click "🔄 Recurring"
   - Configure recurrence pattern
   - Set date range
   - Click "Create"

### EPG Management

- **Search:** Filter events by title
- **Filter:** Filter by content type
- **Edit:** Select event and click "✏️ Update"
- **Copy:** Select event and click "📋 Copy"
- **Delete:** Select event(s) and click "🗑️ Delete Selected"
- **Validate:** Click "✓ Validate" to check for conflicts

### Generating EIT

1. Configure service information
2. Add EPG events
3. Click "Generate EIT"
4. EIT file will be created in `epg/` directory

---

## Monitoring

### Console Tab
- Real-time TSDuck output
- Stream processing logs
- Error messages and warnings

### System Metrics Tab
- CPU usage
- Memory usage
- Disk usage

### Stream Status Tab
- Session ID
- Start/Stop times
- Runtime
- Packets processed
- Errors count
- SCTE-35 markers injected

### SCTE-35 Monitor Tab
- Real-time SCTE-35 event detection
- Event history table
- Event details (Event ID, Cue Type, PTS Time)
- Telegram alerts (if enabled)

### Stream Quality Tab
- Bitrate monitoring
- PCR jitter
- Continuity errors
- ETSI TR 101 290 compliance
- Quality metrics history

### Bitrate Monitor Tab
- Current bitrate
- Average bitrate
- Min/Max bitrate
- Bitrate history graph
- Threshold alerts

---

## Telegram Notifications

### Setup

1. **Create Telegram Bot:**
   - Open Telegram
   - Search for @BotFather
   - Send `/newbot`
   - Follow instructions to create bot
   - Save the Bot Token

2. **Get Chat ID:**
   - Search for @userinfobot
   - Send any message
   - Copy your Chat ID

3. **Configure in Application:**
   - Go to Monitoring tab → SCTE-35 Monitor
   - Click "Configure Telegram"
   - Enter Bot Token
   - Enter Chat ID
   - Click "Test Connection"
   - Enable notifications

### Notification Types

- **Stream Start:** When stream processing begins
- **Stream Running:** When stream is actively processing
- **Stream Stop:** When stream stops (manual or unexpected)
- **SCTE-35 Events:** When SCTE-35 markers are detected
- **Quality Alerts:** When stream quality issues are detected
- **Bitrate Alerts:** When bitrate exceeds thresholds
- **Application Crashes:** When application crashes or closes unexpectedly

---

## Troubleshooting

### Stream Won't Start

**Check:**
1. Input URL is valid and accessible
2. Output destination is correct
3. TSDuck is installed and accessible
4. Firewall allows connections
5. Check Console tab for error messages

**Common Issues:**
- **SRT Connection Rejected:**
  - Check Stream ID format
  - Try without Stream ID
  - Verify server address and port
  - Ensure server is accepting connections

- **Input Stream Not Found:**
  - Verify input URL is correct
  - Check network connectivity
  - Test URL in browser/player

### SCTE-35 Markers Not Working

**Check:**
1. Marker file exists and is valid
2. SCTE-35 PID is configured correctly
3. Marker is selected before starting stream
4. Check Monitoring → SCTE-35 Monitor for detection

**Common Issues:**
- **Marker Not Detected:**
  - Verify marker file is in correct profile directory
  - Check SCTE-35 PID matches configuration
  - Ensure marker was generated for current profile

### Application Crashes

**Check:**
1. Review crash logs in `logs/crashes/`
2. Check system resources (CPU, Memory)
3. Verify TSDuck installation
4. Review application logs in `logs/app.log`

**If Crashes Persist:**
- Restart application
- Check for TSDuck process conflicts
- Verify all dependencies are installed
- Contact support with crash log

### Performance Issues

**Optimize:**
1. Close unnecessary applications
2. Reduce number of monitoring tabs open
3. Increase system resources if possible
4. Check disk space availability

### API Not Working

**Check:**
1. API is enabled in configuration
2. API port is not blocked by firewall
3. Rate limit not exceeded (check headers)
4. Verify API endpoint URLs

---

## Advanced Features

### REST API

**Enable API:**
1. Edit `config/app_config.json`
2. Set `"api_enabled": true`
3. Configure `api_host` and `api_port`
4. Restart application

**Endpoints:**
- `GET /health` - Simple health check
- `GET /api/health` - Comprehensive health check
- `GET /api/stream/status` - Stream status
- `GET /api/metrics` - System metrics
- `GET /api/profiles` - List profiles

**Rate Limiting:**
- Default: 100 requests per 60 seconds per IP
- Health check endpoints are exempt
- Rate limit headers in response:
  - `X-RateLimit-Limit`
  - `X-RateLimit-Remaining`
  - `X-RateLimit-Window`

### Multiple Instances

**Profile-Specific Directories:**
- Each profile has its own SCTE-35 marker directory
- Each profile maintains its own event ID sequence
- Allows running multiple instances with different profiles

**Best Practices:**
- Use unique profile names for each instance
- Monitor system resources when running multiple instances
- Configure different API ports for each instance

---

## Support

### Logs Location
- Application logs: `logs/app.log`
- Error logs: `logs/errors.log`
- Crash logs: `logs/crashes/`
- Structured logs: `logs/structured.json`
- Audit logs: `logs/audit.log`

### Getting Help
1. Check logs for error messages
2. Review this manual
3. Check troubleshooting section
4. Contact support with:
   - Application version
   - Error messages
   - Relevant log files

---

**Version:** 3.0.0 Enterprise  
**Last Updated:** 2024-01-XX

