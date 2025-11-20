# 📦 Broadcast Encoder 110 - Installation Guide

## Quick Start

1. **Install TSDuck** (required)
2. **Extract Application**
3. **Run Application**
4. **Configure Settings**

---

## Detailed Installation

### Step 1: Install TSDuck

TSDuck is required for stream processing. Download and install from:

**Official Website:** https://tsduck.io/download/tsduck/

#### Windows Installation

1. Download TSDuck installer for Windows
2. Run installer
3. Install to default location: `C:\Program Files\TSDuck\`
4. Verify installation:
   ```cmd
   tsp --version
   ```
   Should display TSDuck version (e.g., "TSDuck 3.30-xxxx")

#### Alternative Installation

If TSDuck is installed in a custom location:
1. Note the installation path
2. Configure in application: Configuration tab → TSDuck Path

---

### Step 2: Extract Application

1. **Download** the application archive
2. **Extract** to desired location (e.g., `C:\Program Files\Broadcast Encoder 110\`)
3. **Verify** files:
   - `IBE-100_Enterprise.exe` (main executable)
   - `logo.ico` (application icon)
   - Other supporting files

---

### Step 3: First Run

1. **Run** `IBE-100_Enterprise.exe`
2. **Wait** for application to initialize
3. **Check** that directories are created:
   - `logs/`
   - `config/`
   - `profiles/`
   - `scte35_final/`
   - `epg/`
   - `database/`

---

### Step 4: Initial Configuration

#### Configure TSDuck Path (if needed)

1. Go to **Configuration** tab
2. If TSDuck is not in default location, set custom path
3. Application will verify TSDuck accessibility

#### Configure Telegram (optional)

1. Go to **Monitoring** tab → **SCTE-35 Monitor**
2. Click **"Configure Telegram"**
3. Enter:
   - **Bot Token:** From @BotFather
   - **Chat ID:** From @userinfobot
4. Click **"Test Connection"**
5. Enable notifications

---

## System Requirements

### Minimum Requirements
- **OS:** Windows 10 (64-bit) or later
- **RAM:** 4GB
- **Disk Space:** 500MB
- **Network:** Internet connection (for Telegram, HLS, HTTP streams)

### Recommended Requirements
- **OS:** Windows 11 (64-bit)
- **RAM:** 8GB or more
- **Disk Space:** 2GB (for logs and temporary files)
- **CPU:** Multi-core processor
- **Network:** Stable internet connection

### Dependencies
- **TSDuck:** Version 3.30 or later (required)
- **Python Runtime:** Included in executable (no separate installation needed)

---

## Post-Installation

### Verify Installation

1. **Check TSDuck:**
   ```cmd
   tsp --version
   ```

2. **Check Application:**
   - Run application
   - Verify all tabs load correctly
   - Check logs for errors

3. **Test Stream:**
   - Configure a test stream
   - Start processing
   - Verify monitoring works

### Directory Structure

After first run, the following directories will be created:

```
Broadcast Encoder 110/
├── IBE-100_Enterprise.exe
├── logo.ico
├── config/
│   ├── app_config.json
│   └── .encryption_key
├── logs/
│   ├── app.log
│   ├── errors.log
│   ├── structured.json
│   ├── audit.log
│   └── crashes/
├── profiles/
├── scte35_final/
│   └── {profile_name}/
├── epg/
└── database/
    └── sessions.db
```

---

## Uninstallation

### Standard Uninstallation

1. **Stop** application if running
2. **Delete** application directory
3. **Optional:** Delete configuration and data:
   - `config/`
   - `logs/`
   - `profiles/`
   - `scte35_final/`
   - `epg/`
   - `database/`

**Note:** TSDuck is not uninstalled (it's a separate application).

---

## Troubleshooting Installation

### TSDuck Not Found

**Problem:** Application cannot find TSDuck

**Solutions:**
1. Verify TSDuck is installed:
   ```cmd
   tsp --version
   ```
2. Check TSDuck path in Configuration tab
3. Add TSDuck to system PATH:
   - Add `C:\Program Files\TSDuck\bin` to PATH
   - Restart application

### Application Won't Start

**Problem:** Application crashes on startup

**Solutions:**
1. Check Windows Event Viewer for errors
2. Review crash logs in `logs/crashes/`
3. Verify system requirements are met
4. Run as Administrator (if permission issues)
5. Check antivirus isn't blocking application

### Missing Dependencies

**Problem:** Error messages about missing files

**Solutions:**
1. Re-extract application archive
2. Verify all files are present
3. Check file permissions
4. Run as Administrator

### Permission Errors

**Problem:** Cannot create directories or write files

**Solutions:**
1. Run application as Administrator
2. Check folder permissions
3. Ensure disk space is available
4. Check antivirus isn't blocking file operations

---

## Updating

### Update Process

1. **Backup** configuration and profiles:
   - Copy `config/` directory
   - Copy `profiles/` directory
   - Copy `scte35_final/` directory (if needed)

2. **Stop** application

3. **Replace** executable:
   - Delete old `IBE-100_Enterprise.exe`
   - Extract new executable

4. **Restore** backups (if needed)

5. **Start** application

6. **Verify** settings and profiles

---

## Network Configuration

### Firewall Rules

**Inbound Rules (if using API):**
- Port 8080 (default API port) - TCP

**Outbound Rules:**
- Allow application to connect to:
  - Input stream sources
  - Output stream destinations
  - Telegram API (if using notifications)

### Port Configuration

**Default Ports:**
- API: 8080 (configurable)
- SRT: User-configured (typically 8888)

**Change API Port:**
1. Edit `config/app_config.json`
2. Change `api_port` value
3. Restart application

---

## Security Considerations

### Configuration Encryption

- Configuration files are encrypted by default
- Encryption key stored in `config/.encryption_key`
- **Important:** Backup encryption key for recovery

### API Security

- API is disabled by default
- When enabled, use firewall rules to restrict access
- Consider using API key authentication for production

### File Permissions

- Application creates files with appropriate permissions
- Logs may contain sensitive information
- Secure log directory in production environments

---

## Support

### Installation Issues

If you encounter installation problems:

1. **Check Logs:**
   - `logs/app.log` - Application logs
   - `logs/errors.log` - Error logs
   - `logs/crashes/` - Crash logs

2. **Verify Requirements:**
   - TSDuck installed and accessible
   - System meets minimum requirements
   - Sufficient disk space

3. **Contact Support:**
   - Provide error messages
   - Include relevant log files
   - Describe installation steps taken

---

**Version:** 3.0.0 Enterprise  
**Last Updated:** 2024-01-XX

