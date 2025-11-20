# 🎬 SCTE-35 Monitoring Guide

## 📺 **When Does SCTE-35 Monitoring Show Data?**

The SCTE-35 Status tab in the Monitoring section shows three possible states:

### **1. ❌ Error State (Red)**
**When:** No `scte35_final` directory exists

**Message:**
```
[ERROR] No markers directory found
```

**Solution:** This is normal on first launch. The directory will be created when you generate your first marker.

---

### **2. ⚠️ Warning State (Orange)**
**When:** Directory exists but no marker files yet

**Message:**
```
[WARNING] No SCTE-35 markers found. Generate markers from the SCTE-35 tab.
```

**Solution:** Generate markers first (see steps below)

---

### **3. ✅ Active State (Green)**
**When:** Markers have been generated

**Shows:**
```
═══════════════════════════════════════════════════
          SCTE-35 MARKER STATUS (Real-time)
═══════════════════════════════════════════════════

Total Markers:      5
Latest Marker:      preroll_10023_1761557199.xml
Last Modified:      2025-10-27 15:30:45
Marker Directory:   E:\...\scte35_final

═══════════════════════════════════════════════════

[INFO] SCTE-35 monitoring active...
[INFO] Ready to inject markers into stream

═══════════════════════════════════════════════════
```

**Updates:** Every 2 seconds automatically

---

## 🚀 **How to Generate Markers**

### **Step 1: Go to SCTE-35 Tab**
- Open IBE-100 v2.0.1
- Click on "🎬 SCTE-35" tab

### **Step 2: Select Cue Type**
Choose from:
- **Pre-roll** - Program transition marker
- **CUE-OUT** - Ad break start marker
- **CUE-IN** - Ad break end marker
- **Time Signal** - Time-based signal marker

### **Step 3: Configure Settings**
- **Pre-roll Duration:** How long the pre-roll (in frames or seconds)
- **Ad Duration:** How long the ad break lasts (in frames or seconds)
- **Event ID:** Unique identifier for the event

### **Step 4: Generate Marker**
- Click **"Generate"** button
- Marker files created in `scte35_final` folder
  - XML file (for TSDuck)
  - JSON file (metadata)

### **Step 5: View in Monitoring**
- Go to **Monitoring** tab
- Click **"🎬 SCTE-35 Status"** sub-tab
- See marker count, latest marker, and status

---

## 📊 **What Gets Displayed**

### **Information Shown:**
1. **Total Markers** - Count of all XML marker files
2. **Latest Marker** - Most recently created marker filename
3. **Last Modified** - Timestamp of latest marker
4. **Marker Directory** - Full path to markers folder
5. **Status** - Active or waiting

### **Update Frequency:**
- Updates every **2 seconds** automatically
- Shows real-time marker creation
- Updates when you generate new markers

---

## 🔍 **Troubleshooting**

### **Problem: Monitoring shows nothing**
**Cause:** No markers generated yet

**Solution:**
1. Go to SCTE-35 tab
2. Configure and generate at least one marker
3. Return to Monitoring tab

### **Problem: Always shows "No markers found"**
**Cause:** Generated markers not saved properly

**Solution:**
1. Check `scte35_final` folder exists
2. Look for XML files in that folder
3. Verify folder permissions
4. Try generating a new marker

### **Problem: Monitoring not updating**
**Cause:** Timer not running or crash

**Solution:**
1. Check console for errors
2. Restart application
3. Go to Monitoring tab to refresh

---

## 💡 **Best Practices**

### **1. Generate Markers Before Streaming**
- Generate markers in SCTE-35 tab first
- Wait for monitoring to show them
- Then start stream processing

### **2. Check Monitoring Regularly**
- Monitor shows marker count
- Verify latest marker matches your needs
- Check last modified timestamp

### **3. Multiple Markers**
- Generate multiple markers as needed
- Monitoring shows total count
- Latest marker is always selected for injection

---

## 🎯 **Quick Reference**

| Status | Color | Meaning |
|--------|-------|---------|
| Error | Red ❌ | No directory exists |
| Warning | Orange ⚠️ | No markers yet |
| Active | Green ✅ | Markers ready |

---

## 📝 **Example Workflow**

### **First Launch:**
1. Launch IBE-100 v2.0.1
2. Go to Monitoring → SCTE-35 Status
3. See: `[WARNING] No markers found`

### **After Generating First Marker:**
1. Go to SCTE-35 tab
2. Configure and click "Generate"
3. Go to Monitoring → SCTE-35 Status
4. See: `Total Markers: 1` with details

### **After Generating More Markers:**
1. Generate additional markers
2. Monitoring auto-updates every 2 seconds
3. See increasing marker count
4. Latest marker shows newest file

---

## ✅ **Success Indicators**

When SCTE-35 monitoring is working correctly:
- ✅ Green status message
- ✅ Marker count shows number
- ✅ Latest marker filename displayed
- ✅ Last modified timestamp current
- ✅ Updates every 2 seconds

---

## 📞 **Support**

If monitoring never shows data:
1. Check `scte35_final` folder exists
2. Look for XML files in that folder
3. Check console for errors
4. Try generating a new marker
5. Restart application if needed

**Email:** support@itassist.one  
**Website:** https://itassist.one

---

**Version:** 2.0.1  
**Last Updated:** October 2025  
**Status:** ✅ Documentation Complete

