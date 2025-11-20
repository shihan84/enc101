# ✅ IBE-100 v2.0.1 Pre-Deployment Prerequisite Checklist

## 🎯 **Purpose**
This checklist ensures all prerequisites are met before deploying IBE-100 v2.0.1 to a new system, preventing Error Code 1 and other deployment issues.

---

## 📋 **System Requirements Checklist**

### **Operating System**
- [ ] Windows 10 (64-bit) or later
- [ ] Windows 11 (64-bit)
- [ ] At least 4GB RAM (8GB recommended)
- [ ] At least 2GB free disk space
- [ ] Administrator privileges available

### **Network**
- [ ] Internet connectivity available
- [ ] Firewall can be configured
- [ ] Ports available for streaming (UDP/TCP)
- [ ] SRT server accessible (if using SRT output)

---

## 📦 **Software Prerequisites**

### **1. TSDuck Installation** ⚠️ **CRITICAL**

#### Installation
- [ ] TSDuck downloaded from: https://tsduck.io/download/tsduck/
- [ ] TSDuck installer executed
- [ ] TSDuck installed to: `C:\Program Files\TSDuck\bin\`
- [ ] Installation completed successfully

#### Verification
- [ ] Command: `tsp --version` works
- [ ] Output shows version 3.30 or later
- [ ] Command: `tsp --list-plugins` works
- [ ] Required plugins available: `hls`, `srt`, `spliceinject`, `pmt`, `services`, `ip`

#### PATH Configuration
- [ ] TSDuck added to system PATH
- [ ] Verification: Can run `tsp` from any directory
- [ ] Command: `where tsp` shows correct path

**Common Issues:**
- ❌ TSDuck not installed → Install from official website
- ❌ TSDuck not in PATH → Add `C:\Program Files\TSDuck\bin` to PATH
- ❌ Plugins missing → Reinstall TSDuck or rebuild

---

### **2. Python (Optional for web server)**
- [ ] Python 3.8+ installed (if using serve_hls.py)
- [ ] Command: `python --version` works
- [ ] pip available

---

## 🧪 **Verification Tests**

### **Test 1: TSDuck Basic Test**
```cmd
tsp --version
```
**Expected:** Shows TSDuck version (e.g., "tsp: TSDuck - version 3.42-4421")

### **Test 2: TSDuck Plugins Test**
```cmd
tsp --list-plugins | findstr /i "hls srt spliceinject"
```
**Expected:** Shows all three plugins listed

### **Test 3: Network Connectivity Test**
```cmd
ping 8.8.8.8
```
**Expected:** 4 packets sent, 4 received

### **Test 4: Input Source Test (Optional)**
```cmd
curl -I https://your-hls-source/index.m3u8
```
**Expected:** HTTP 200 OK (or appropriate response)

---

## 📁 **IBE-100 Deployment**

### **Files Required**
- [ ] `IBE-100.exe` present in deployment folder
- [ ] `launch_ibe100_v2.0.1.bat` present
- [ ] `diagnose_system.bat` present
- [ ] `README.md` present
- [ ] `DEPLOYMENT_TROUBLESHOOTING_v2.0.1.md` present
- [ ] `test_player.html` present (for HLS/DASH testing)

### **Directory Structure**
- [ ] `scte35_final` folder will be created automatically
- [ ] Write permissions in current directory
- [ ] Network permissions if streaming to remote server

---

## 🚀 **Pre-Launch Verification**

### **Before First Launch**
- [ ] Run: `diagnose_system.bat`
- [ ] Verify all checks pass
- [ ] Review any warnings
- [ ] Fix any critical issues

### **Launch Test**
- [ ] Run: `launch_ibe100_v2.0.1.bat`
- [ ] Application starts without errors
- [ ] GUI loads successfully
- [ ] All tabs accessible

---

## ⚙️ **Configuration Prerequisites**

### **Input Configuration**
- [ ] Input source URL/address available
- [ ] Input source type selected (HLS, SRT, UDP, etc.)
- [ ] Input source is accessible from target system
- [ ] Network path to input verified

### **Output Configuration**
- [ ] Output destination configured
- [ ] SRT server running and accessible (if using SRT)
- [ ] UDP/TCP ports available (if using UDP/TCP)
- [ ] File output path exists and writable (if using file)

### **Service Configuration**
- [ ] Service name configured
- [ ] Service provider configured
- [ ] Service ID configured
- [ ] Video PID configured
- [ ] Audio PID configured
- [ ] SCTE-35 PID configured

---

## 🔒 **Security & Permissions**

### **File Permissions**
- [ ] Read access to input directory (if using file input)
- [ ] Write access to output directory
- [ ] Write access to current directory (for logs)
- [ ] Read/write access to scte35_final folder

### **Network Permissions**
- [ ] Firewall allows TSDuck connections
- [ ] Firewall allows IBE-100.exe
- [ ] Antivirus not blocking TSDuck
- [ ] Antivirus not blocking IBE-100.exe

### **Administrator Privileges**
- [ ] Run as administrator if permission errors occur
- [ ] UAC settings allow application to run
- [ ] No Windows Defender blocking

---

## 📝 **Quick Pre-Deployment Script**

Run this batch file to check all prerequisites:

```cmd
@echo off
echo ========================================
echo  IBE-100 v2.0.1 Pre-Deployment Check
echo ========================================
echo.

echo [1] Checking TSDuck...
tsp --version
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] TSDuck not found!
    echo Please install TSDuck first.
    exit /b 1
)
echo [OK] TSDuck found
echo.

echo [2] Checking plugins...
tsp --list-plugins | findstr /i "hls srt spliceinject" >nul
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Some plugins missing
) else (
    echo [OK] Required plugins available
)
echo.

echo [3] Checking network...
ping -n 1 8.8.8.8 >nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Network connectivity OK
) else (
    echo [WARNING] Network issues detected
)
echo.

echo [4] Checking IBE-100.exe...
if exist "IBE-100.exe" (
    echo [OK] IBE-100.exe found
) else (
    echo [ERROR] IBE-100.exe not found
    exit /b 1
)
echo.

echo ========================================
echo  Pre-deployment check complete!
echo ========================================
pause
```

Save as `check_prerequisites.bat` and run before deployment.

---

## ✅ **Final Checklist**

### **Before First Stream**
- [ ] All prerequisites verified
- [ ] TSDuck installed and working
- [ ] Network connectivity confirmed
- [ ] Configuration saved (optional)
- [ ] Input source tested manually
- [ ] Output destination accessible
- [ ] Firewall configured
- [ ] System diagnostic passed

### **First Successful Run**
- [ ] Application launched successfully
- [ ] Stream started without error
- [ ] TSDuck output visible in console
- [ ] Exit code 0 (success)
- [ ] SCTE-35 markers working (if configured)
- [ ] Monitor running without errors

---

## 🆘 **If Prerequisites Not Met**

### **TSDuck Not Installed**
1. Download from: https://tsduck.io/download/tsduck/
2. Run installer
3. Verify installation
4. Add to PATH if needed

### **Network Issues**
1. Check firewall rules
2. Verify network connectivity
3. Test with: `ping 8.8.8.8`
4. Check DNS resolution

### **Permission Issues**
1. Run as administrator
2. Check file permissions
3. Configure UAC settings
4. Add antivirus exceptions

---

## 📞 **Support & Resources**

- **TSDuck Download:** https://tsduck.io/download/
- **TSDuck Docs:** https://tsduck.io/doc/
- **Email Support:** support@itassist.one
- **Website:** https://itassist.one

---

## 🎯 **Summary**

**Critical Prerequisites:**
1. ✅ TSDuck installed and in PATH
2. ✅ Required plugins available
3. ✅ Network connectivity working
4. ✅ File permissions correct
5. ✅ Firewall configured

**Recommended:**
- Run `diagnose_system.bat` before first launch
- Test manually with TSDuck commands
- Configure and save settings
- Verify input/output accessibility

**Success Criteria:**
- ✅ All checklist items completed
- ✅ diagnostic_system.bat passes all checks
- ✅ First stream runs successfully
- ✅ Exit code 0

---

**Version:** 2.0.1  
**Last Updated:** October 2025  
**Status:** ✅ Production Ready

