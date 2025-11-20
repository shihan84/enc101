# ✅ SCTE-35 Marker Management - New vs Old Markers

## 🎯 **How Marker Selection Works**

### **Automatic Marker Replacement**

When you generate a **new marker**, the system automatically:

1. ✅ **Replaces the old marker** - The previous marker is no longer active
2. ✅ **Sets new marker as active** - Only the newest marker will be used
3. ✅ **Shows clear notification** - You'll see which marker was replaced
4. ✅ **Prevents old marker usage** - Old markers are NOT included in the stream

### **Visual Indicators**

- **📌 Active Marker**: Shown in the control bar at the bottom
- **Monitoring Console**: Shows when markers are replaced
- **Confirmation Dialog**: Shows which marker will be used before stream starts

## 🔄 **Marker Lifecycle**

### **Step 1: Generate New Marker**
```
1. Go to "🎬 SCTE-35" tab
2. Configure marker settings
3. Click "🎯 Generate Marker"
4. New marker is created and automatically becomes active
```

### **Step 2: Old Marker Replacement**
```
✅ Old marker is automatically replaced
✅ Old marker will NOT be used in stream
✅ Only the newest marker is active
```

### **Step 3: Start Stream**
```
1. Click "▶️ Start Processing"
2. Confirmation dialog shows which marker will be used
3. Only the active marker is included in TSDuck command
4. Old markers are completely ignored
```

## ⚠️ **Important Rules**

### **✅ What Happens**

1. **New Marker Generated** → Automatically becomes active
2. **Old Marker** → Automatically replaced, NOT used
3. **Stream Start** → Only uses the currently active marker
4. **Multiple Markers** → Only the latest one is used

### **❌ What Does NOT Happen**

1. ❌ Old markers are NOT automatically included
2. ❌ Multiple markers are NOT combined
3. ❌ Old markers are NOT used even if they exist in the folder
4. ❌ No confusion about which marker is active

## 📋 **Example Workflow**

### **Scenario: Generating Multiple Markers**

```
1. Generate Marker #1: "cue_out_10023_1234567890.xml"
   → Active: cue_out_10023_1234567890.xml
   → Old: None

2. Generate Marker #2: "cue_out_10024_1234567891.xml"
   → Active: cue_out_10024_1234567891.xml
   → Old: cue_out_10023_1234567890.xml (replaced, NOT used)

3. Start Stream
   → Uses ONLY: cue_out_10024_1234567891.xml
   → Ignores: cue_out_10023_1234567890.xml
```

## 🔍 **How to Verify**

### **Check Active Marker**

1. **Look at Control Bar**: Shows "📌 Active: [marker_name]"
2. **Check Monitoring Console**: Shows marker replacement messages
3. **Confirmation Dialog**: Shows which marker will be used

### **Verify Old Markers Are Not Used**

1. **Check TSDuck Command**: Only one marker file is specified
2. **Check Monitoring Console**: Shows "Old marker will NOT be used"
3. **File System**: Old marker files remain but are not used

## 🎯 **Best Practices**

### **✅ Recommended Workflow**

1. **Generate marker when needed** - Don't generate multiple markers in advance
2. **Check active marker** - Verify which marker is active before starting stream
3. **Use confirmation dialog** - Review the marker selection before starting
4. **One marker per stream** - Only one marker is used per stream session

### **⚠️ Important Notes**

- **Old markers are NOT deleted** - They remain in the folder for reference
- **Only active marker is used** - Even if multiple markers exist
- **New marker replaces old** - Automatically, no manual action needed
- **Confirmation required** - You'll see which marker will be used

## 🔧 **Technical Details**

### **Marker Storage**

- **Active Marker**: Stored in `self.current_marker`
- **Old Markers**: Remain in `scte35_final/` folder but are not used
- **Replacement**: Automatic when new marker is generated

### **TSDuck Command**

```bash
# Only the active marker is included
-P spliceinject --files "scte35_final/cue_out_10024_1234567891.xml"
```

**Note**: Only ONE marker file is specified, not multiple files.

## ✅ **Summary**

- ✅ **New markers automatically replace old ones**
- ✅ **Only the newest marker is used in stream**
- ✅ **Old markers are NOT included automatically**
- ✅ **Clear visual indicators show active marker**
- ✅ **Confirmation dialog prevents mistakes**

This ensures that **only the marker you just generated** is used, and old markers are never accidentally included in the stream.

