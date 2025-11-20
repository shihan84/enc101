# 🚀 IBE-100 v2.0.1 Quick Start Guide

## ⚡ **5-Minute Setup**

### **Step 1: Verify Prerequisites** (2 minutes)
```cmd
check_prerequisites.bat
```

**Expected Output:**
```
[OK] TSDuck installed
[OK] TSDuck found in PATH
[OK] Required plugins available
[PASSED] All prerequisites met!
```

### **Step 2: Launch Application** (1 minute)
```cmd
launch_ibe100_v2.0.1.bat
```

Or double-click:
- `IBE-100.exe`

### **Step 3: Configure Stream** (1 minute)

**Stream Configuration Tab:**
- Input Type: Select your input (HLS, SRT, etc.)
- Stream URL: Enter your input stream
- Output Type: Select output (SRT, HLS, DASH)
- Destination: Enter output destination

**Service Configuration:**
- Service Name: Your service name
- Service Provider: Your provider name
- Service ID: Your service ID (default: 1)
- Video PID: Default 256
- Audio PID: Default 257
- SCTE-35 PID: Default 500

### **Step 4: Start Streaming** (1 minute)
1. Click **"Preview Command"** to verify TSDuck command
2. Click **"Start Stream"**
3. Check console output for success
4. Monitor in Monitoring tab

---

## ✅ **Success Indicators**

### **Console Shows:**
```
[INFO] Starting processing...
[INFO] Using marker: scte35_final/latest.xml
[TSDuck] Running command: tsp -I ...
[TSDuck] Processing...
```

### **Monitoring Tab Shows:**
- ✅ TSDuck output streaming
- ✅ CPU usage normal
- ✅ Memory usage stable
- ✅ No error messages

---

## ❌ **If You Get Error Code 1**

### **Quick Fix:**
1. **Install TSDuck:**
   - Download: https://tsduck.io/download/tsduck/
   - Install to default location
   - Add to PATH: `set PATH=%PATH%;C:\Program Files\TSDuck\bin`

2. **Verify Installation:**
   ```cmd
   tsp --version
   ```

3. **Run Diagnostic:**
   ```cmd
   diagnose_system.bat
   ```

4. **Try Again:**
   ```cmd
   launch_ibe100_v2.0.1.bat
   ```

---

## 📋 **Common Commands**

### **Check Prerequisites**
```cmd
check_prerequisites.bat
```

### **Run Diagnostics**
```cmd
diagnose_system.bat
```

### **Launch Application**
```cmd
launch_ibe100_v2.0.1.bat
```

### **Test TSDuck Manually**
```cmd
tsp --version
tsp -I hls https://your-url/index.m3u8 -O drop
```

---

## 🎯 **Quick Reference**

| Task | Command | Location |
|------|---------|----------|
| Check Prerequisites | `check_prerequisites.bat` | dist_final/ |
| Run Diagnostics | `diagnose_system.bat` | dist_final/ |
| Launch App | `launch_ibe100_v2.0.1.bat` | dist_final/ |
| Test TSDuck | `tsp --version` | Anywhere (if in PATH) |

---

## 📞 **Need Help?**

1. **Run diagnostics:**
   ```cmd
   diagnose_system.bat
   ```

2. **Check documentation:**
   - `PRE_REQUISITE_CHECKLIST.md`
   - `DEPLOYMENT_TROUBLESHOOTING_v2.0.1.md`

3. **Contact support:**
   - Email: support@itassist.one
   - Website: https://itassist.one

---

## 🎉 **That's It!**

You're now ready to stream with IBE-100 v2.0.1!

**Remember:**
- ✅ Always run `check_prerequisites.bat` before deployment
- ✅ Verify TSDuck is installed and in PATH
- ✅ Test input source accessibility
- ✅ Check console output for errors
- ✅ Monitor system resources

---

**Version:** 2.0.1  
**Status:** ✅ Production Ready

