# 🔧 IBE-100 v2.0.1 Deployment Troubleshooting

## ❌ **Common Issue: Error Code 1 on Target Systems**

### **Problem Description**
When running IBE-100 v2.0.1 on another system, you may encounter:
```
[ERROR] Processing failed with exit code 1
Stream stops after a few seconds
```

### **Root Cause - Most Common Issues**

#### 1. TSDuck Not Installed or Not in PATH ⚠️
**Most Common Cause**

Even though IBE-100 v2.0.1 has TSDuck detection, the TSDuck executable must be installed on the target system.

**Symptoms:**
- Error code 1 immediately after clicking "Start Stream"
- Console shows: "tsp: command not found" or similar
- Stream never starts

**Solution:**
```cmd
# Step 1: Install TSDuck
# Download from: https://tsduck.io/download/tsduck/
# Run the Windows installer

# Step 2: Verify installation
tsp --version

# Step 3: If not found, add to PATH
set PATH=%PATH%;C:\Program Files\TSDuck\bin

# Or permanently add to environment variables:
# Control Panel → System → Environment Variables → PATH
# Add: C:\Program Files\TSDuck\bin
```

#### 2. Input Source Not Accessible
**Symptoms:**
- Error code 1 after a few seconds
- Network errors in console
- "Connection refused" or "No such host"

**Solution:**
```cmd
# Test if your HLS source is accessible:
curl -I https://your-hls-url/index.m3u8

# Or test with TSDuck:
tsp -I hls https://your-url/index.m3u8 -O drop

# Check network connectivity
ping your-server.com
```

#### 3. SRT Server Rejecting Connection
**Symptoms:**
- Error code 1 when using SRT output
- Console shows: "Connection rejected"
- Stream connects but immediately stops

**Solution:**
```cmd
# Verify SRT server is running
# Check SRT server logs
# Verify streamid format if required

# Test SRT connection manually:
tsp -I file input.ts -O srt srt://server:port

# If server requires streamid:
tsp -I file input.ts -O srt srt://server:port?streamid=your-streamid
```

#### 4. Missing Permissions
**Symptoms:**
- Error code 1 with "Permission denied"
- Cannot write to output location
- Cannot create files

**Solution:**
```cmd
# Run as administrator
# Or fix folder permissions
# Check write permissions in current directory
```

---

## 🛠️ **Quick Diagnostic Steps**

### Step 1: Run System Diagnostic
```cmd
cd dist_final
diagnose_system.bat
```

This will check:
- ✅ IBE-100.exe presence
- ✅ TSDuck installation
- ✅ Required plugins
- ✅ Network connectivity
- ✅ SCTE-35 configuration

### Step 2: Verify TSDuck
```cmd
# Check TSDuck version
tsp --version

# Check plugins
tsp --list-plugins

# Should show: hls, srt, spliceinject, pmt, services, ip
```

### Step 3: Test Basic TSDuck
```cmd
# Test with a simple command
tsp --help

# Should work without errors
```

### Step 4: Check Configuration
```cmd
# Verify config file exists (if saved)
dir *.json

# Verify SCTE-35 folder (created automatically)
dir scte35_final
```

---

## ✅ **Pre-Deployment Checklist**

Before deploying to target systems:

- [ ] Install TSDuck on target system
- [ ] Verify `tsp --version` works
- [ ] Test TSDuck with a simple command
- [ ] Check network connectivity to input source
- [ ] Test output destination (SRT/UDP server)
- [ ] Run `diagnose_system.bat`
- [ ] Check firewall settings
- [ ] Ensure required ports are open
- [ ] Verify IBE-100.exe can be executed
- [ ] Test basic stream functionality

---

## 📋 **v2.0.1 Specific Features**

### Integrated Web Server
- Start web server from Monitoring tab
- Configure port (8000-9999)
- Select directory for HLS/DASH output
- Test with built-in test_player.html

### Enhanced SCTE-35 Support
- Manual cue generation
- Scheduling support
- Template system
- TSDuck-compatible XML format

### Real-time Monitoring
- Console output
- SCTE-35 status
- System metrics (CPU, Memory, Disk)
- Web server control

---

## 🎯 **Common Solutions**

### If TSDuck is Installed but Not Found:

**Windows:**
```cmd
# Method 1: Add to PATH temporarily
set PATH=%PATH%;C:\Program Files\TSDuck\bin

# Method 2: Add permanently
# Control Panel → System → Environment Variables
# Add to System PATH: C:\Program Files\TSDuck\bin
```

### If Input Source Not Working:

1. **Check URL is correct**
   - Test in browser: `https://your-url/index.m3u8`
   - Should download M3U8 file

2. **Check network settings**
   - Ping the server
   - Check firewall rules
   - Verify DNS resolution

3. **Test manually**
   ```cmd
   tsp -I hls https://your-url/index.m3u8 -O drop
   ```

### If SRT Connection Fails:

1. **Check SRT server is running**
   - Verify server logs
   - Check server configuration

2. **Verify connection parameters**
   - Host: correct IP or domain
   - Port: correct port number
   - StreamID: correct format if required

3. **Test manually**
   ```cmd
   tsp -I file input.ts -O srt srt://server:port
   ```

---

## 🆘 **Getting Help**

### Collect Diagnostic Information:

1. **Run diagnostic:**
   ```cmd
   diagnose_system.bat > diagnostic_report.txt
   ```

2. **Check TSDuck:**
   ```cmd
   tsp --version >> diagnostic_report.txt
   tsp --list-plugins >> diagnostic_report.txt
   ```

3. **Test basic functionality:**
   ```cmd
   tsp -I file test.ts -O drop >> diagnostic_report.txt
   ```

### Contact Support:

- **Email:** support@itassist.one
- **Website:** https://itassist.one
- **Include:** diagnostic_report.txt, error messages, system info

---

## 💡 **Quick Tips**

1. **Always check console output** - it shows specific error messages
2. **Use "Preview Command"** - tests TSDuck command before running
3. **Start with local test** - test with UDP output before SRT
4. **Check firewall** - Windows Defender may block connections
5. **Run as administrator** - if permission issues persist
6. **Enable web server** - for HLS/DASH testing within LAN

---

## ✅ **Success Indicators**

When everything is working correctly:
- ✅ TSDuck found and accessible
- ✅ Stream starts successfully
- ✅ Console shows TSDuck output
- ✅ Exit code 0 on completion
- ✅ SCTE-35 markers detected (if configured)
- ✅ Web server serves HLS/DASH (if enabled)

---

## 📞 **Additional Resources**

- **TSDuck Documentation:** https://tsduck.io/doc/
- **TSDuck Download:** https://tsduck.io/download/
- **Release Notes:** RELEASE_NOTES_v2.0.0.md
- **Test Player:** test_player.html (open in browser)

---

**Remember:** Most error code 1 issues are caused by missing TSDuck installation. Always verify `tsp --version` works before starting streams!

