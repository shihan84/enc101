# 🔧 Monitoring Issues Fix - Profile Directory & Interval

## 📋 **Issues Identified from Monitoring Logs**

### **Issue 1: Wrong Directory Path** ❌

**Problem:**
```
TSDuck Command shows: C:\ENC210\scte35_final\dynamic_markers\splice*.xml
Should be: C:\ENC210\scte35_final\lokmanch\dynamic_markers\splice*.xml
```

**Root Cause:**
- Profile "lokmanch" is not in the directory path
- Dynamic marker service is using default directory instead of profile-specific directory
- Profile may not be synced before stream starts

**Impact:**
- Markers are generated in wrong directory
- TSDuck can't find markers (0 b/s bitrate)
- SCTE-35 markers not injected into stream

---

### **Issue 2: Interval Too Frequent** ⚠️

**Problem:**
```
[INFO] Interval: 1.0 seconds
Should be: 60 seconds (60000 ms)
```

**Root Cause:**
- `inject_interval` in configuration is set to 1000 ms (1 second)
- Should be 60000 ms (60 seconds) for standard streaming

**Impact:**
- Markers generated too frequently (every 1 second)
- Unnecessary overhead
- Not following industry standard (30-300 seconds)

---

### **Issue 3: SCTE-35 Bitrate is 0** ❌

**Problem:**
```
0x01F4 SCTE 35 Splice Info .......................... C 0 b/s
```

**Root Cause:**
- Markers are being generated but not injected
- TSDuck can't find marker files (wrong directory path)
- No markers in stream = 0 bitrate

**Impact:**
- Distributor can't see markers
- No ad insertion possible
- Stream has no SCTE-35 data

---

## ✅ **Fixes Applied**

### **Fix 1: Profile Directory Sync**

**Changes Made:**
1. Added profile sync before starting dynamic marker generation
2. Ensures dynamic marker service uses same profile as SCTE35Service
3. Validates directory path includes profile name
4. Adds warning if profile path is incorrect

**Code Location:**
- `src/services/stream_service.py` - `start_stream()` method

**What It Does:**
```python
# Sync profile with SCTE35Service before starting generation
if hasattr(self.dynamic_marker_service, 'scte35_service'):
    scte35_service = self.dynamic_marker_service.scte35_service
    if hasattr(scte35_service, 'profile_name'):
        current_profile = scte35_service.profile_name
        if current_profile != self.dynamic_marker_service.profile_name:
            self.dynamic_marker_service.set_profile(current_profile)
```

---

### **Fix 2: Interval Warning**

**Changes Made:**
1. Added warning when interval is too short (< 30 seconds)
2. Logs recommended interval (60 seconds)
3. Shows current vs recommended values

**Code Location:**
- `src/services/dynamic_marker_service.py` - `start_generation()` method

**What It Does:**
```python
# Warn if interval is too short
if interval_seconds < 30:
    self.logger.warning(f"Inject interval is very short ({interval_seconds} seconds)!")
    self.logger.warning(f"Recommended: 60 seconds (60000 ms) for standard streaming")
```

---

## 🔧 **How to Fix Your Configuration**

### **Step 1: Fix Inject Interval**

**In Your Profile Configuration:**
1. Open your profile settings
2. Find "Inject Interval" field
3. Change from `1000` to `60000` (60 seconds)
4. Save profile

**Or in UI:**
1. Go to Configuration tab
2. Find "Inject Interval" spin box
3. Set to `60000` (60 seconds)
4. Save configuration

---

### **Step 2: Verify Profile Directory**

**Check Logs After Starting Stream:**
Look for these log messages:
```
[INFO] Profile: lokmanch
[INFO] Profile directory: C:\ENC210\scte35_final\lokmanch
[INFO] Dynamic markers directory: C:\ENC210\scte35_final\lokmanch\dynamic_markers
[INFO] TSDuck will use: C:\ENC210\scte35_final\lokmanch\dynamic_markers\splice*.xml
```

**If you see warnings:**
```
[WARNING] Profile directory path may be incorrect!
[WARNING] Expected profile 'lokmanch' in path
```
→ This means profile wasn't set correctly. Make sure to load the profile before starting stream.

---

### **Step 3: Verify SCTE-35 Bitrate**

**After Starting Stream:**
Look for this in TSDuck analysis:
```
0x01F4 SCTE 35 Splice Info .......................... C [SHOULD BE > 0] b/s
```

**If bitrate is > 0:**
✅ Markers are being injected correctly!

**If bitrate is still 0:**
❌ Check:
1. Profile directory path is correct
2. Markers are being generated (check logs for `[SCTE-35] Generated marker`)
3. TSDuck command uses correct path

---

## 📊 **Expected Behavior After Fix**

### **Correct Logs:**
```
[INFO] Profile: lokmanch
[INFO] Profile directory: C:\ENC210\scte35_final\lokmanch
[INFO] Dynamic markers directory: C:\ENC210\scte35_final\lokmanch\dynamic_markers
[INFO] TSDuck will use: C:\ENC210\scte35_final\lokmanch\dynamic_markers\splice*.xml
[INFO] Starting dynamic marker generation
[INFO] Interval: 60.0 seconds (60000 ms)
[INFO] Starting Event ID: 10025
[SCTE-35] Generated marker: Event ID=10025 (Total: 1)
[SCTE-35] Generated marker: Event ID=10026 (Total: 2)
...
```

### **TSDuck Analysis:**
```
0x01F4 SCTE 35 Splice Info .......................... C [> 0] b/s  ← Should be > 0!
```

### **TSDuck Command:**
```
--files C:\ENC210\scte35_final\lokmanch\dynamic_markers\splice*.xml  ← Correct path!
```

---

## 🎯 **Summary**

### **Issues Fixed:**
1. ✅ Profile directory sync before stream start
2. ✅ Directory path validation
3. ✅ Warning for short intervals
4. ✅ Better logging for debugging

### **Action Required:**
1. ⚠️ **Change `inject_interval` from 1000 to 60000** in your configuration
2. ✅ **Load profile before starting stream** (to ensure profile is set)
3. ✅ **Check logs** to verify correct directory path

### **Expected Result:**
- ✅ Correct profile directory: `scte35_final\lokmanch\dynamic_markers\`
- ✅ Correct interval: 60 seconds
- ✅ SCTE-35 bitrate > 0
- ✅ Markers injected into stream
- ✅ Distributor can see markers

---

## 🚀 **Next Steps**

1. **Update Configuration:**
   - Set `inject_interval` to 60000 (60 seconds)

2. **Restart Stream:**
   - Load profile "lokmanch"
   - Start stream with marker
   - Check logs for correct directory path

3. **Verify:**
   - Check SCTE-35 bitrate > 0
   - Check markers are being generated
   - Check distributor can see markers

---

**After applying these fixes, your stream should work correctly with profile-specific directories and proper marker injection intervals!** ✅

