# 🔍 TSDuck SCTE-35 Injection Tracking - Research Findings

## 📚 **TSDuck Documentation Research**

### **Available Options for Tracking**

#### **1. Verbose/Debug Output**
TSDuck provides these flags:
- `--verbose` or `-v`: Produce verbose output
- `--debug[=level]`: Produce debug traces (level 1-9, higher = more messages)
- `--timed-log` or `-t`: Add timestamps to log messages
- `--synchronous-log` or `-s`: Guarantee all messages are displayed (for files, not live streams)

**Question**: Does `spliceinject` plugin output injection confirmations in verbose/debug mode?

#### **2. TSDuck spliceinject Plugin Behavior**
From help output:
- Plugin processes files from `--files` directory
- Files are loaded and injected based on `--inject-count` and `--inject-interval`
- `--delete-files` option: Delete files after loading
- Files are reloaded if modified

**Key Insight**: Plugin processes files, but may not output explicit "injection successful" messages.

#### **3. Alternative: splicemonitor Plugin**
- TSDuck has `splicemonitor` plugin for **detecting** SCTE-35 markers
- Can monitor input or output stream
- Detects markers that are actually in the stream

**Best Approach**: Use `splicemonitor` to detect injected markers in the output stream!

## 🎯 **Recommended Solutions**

### **Solution 1: Configuration-Based Counting** ⭐ (Quick & Simple)

**How it works:**
- Count markers based on what we **know** is being injected
- If marker file provided → count it
- If preroll sequence → count all 3 markers (CUE-OUT, CUE-IN, CUE-CRASH)
- Multiply by `--inject-count` parameter

**Pros:**
- ✅ Simple to implement
- ✅ Works immediately
- ✅ No additional processing

**Cons:**
- ⚠️ Assumes successful injection (doesn't verify)
- ⚠️ Not actual detection

**Code:**
```python
# When stream starts
if marker:
    if marker.cue_type == CueType.PREROLL:
        # Preroll = 3 markers (CUE-OUT, CUE-IN, CUE-CRASH)
        session.scte35_injected = 3 * (config.inject_count or 1)
    else:
        # Single marker
        session.scte35_injected = config.inject_count or 1
```

### **Solution 2: splicemonitor Detection** ⭐⭐⭐ (Most Accurate)

**How it works:**
- Add `splicemonitor` plugin to output stream
- Monitor for SCTE-35 markers in the stream
- Count detected markers
- This is **actual detection**, not assumption

**Pros:**
- ✅ **Real detection** - counts actual markers in stream
- ✅ **Accurate** - verifies injection worked
- ✅ Uses TSDuck's built-in monitoring

**Cons:**
- ⚠️ Requires additional plugin in command
- ⚠️ Slight performance overhead
- ⚠️ More complex parsing

**Implementation:**
```python
# Add to TSDuck command (before output)
command.extend(["-P", "splicemonitor", "--pid", str(config.scte35_pid)])

# Parse output for detected markers
# Look for: "splicemonitor: splice_insert detected" or similar
```

### **Solution 3: Verbose Output Parsing** ⚠️ (Uncertain)

**How it works:**
- Enable `--verbose` or `--debug` flags
- Parse TSDuck output for injection messages
- Look for patterns like "spliceinject: injecting..." or "marker loaded"

**Pros:**
- ✅ Uses existing output stream
- ✅ No additional plugins

**Cons:**
- ⚠️ **Unknown if TSDuck outputs these messages**
- ⚠️ Output format may vary
- ⚠️ Need to test first

**Status**: **Needs Testing** - We don't know if TSDuck outputs injection confirmations

### **Solution 4: File Monitoring** ✅ (Reliable)

**How it works:**
- Monitor when marker files are accessed/loaded
- Track file timestamps
- Count files processed (if `--delete-files` is used)

**Pros:**
- ✅ Reliable indicator
- ✅ Works with file-based injection

**Cons:**
- ⚠️ Platform-specific (file system monitoring)
- ⚠️ Doesn't verify actual injection

## 📊 **Comparison Table**

| Solution | Accuracy | Complexity | Performance | Reliability |
|----------|----------|------------|-------------|-------------|
| **Config-Based** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **splicemonitor** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Verbose Parsing** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **File Monitoring** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

## 🎯 **Recommended Approach: Hybrid Solution**

### **Phase 1: Quick Fix (Now)**
Implement **Configuration-Based Counting**:
- Simple and immediate
- Works with current setup
- Shows reasonable count

### **Phase 2: Enhanced (Later)**
Add **splicemonitor Detection**:
- Real marker detection
- Accurate counting
- Verifies injection worked

### **Implementation Strategy**

```python
# Phase 1: Configuration-based (immediate)
if marker:
    if marker.cue_type == CueType.PREROLL:
        session.scte35_injected = 3  # CUE-OUT, CUE-IN, CUE-CRASH
    else:
        session.scte35_injected = 1

# Phase 2: Enhanced with splicemonitor (future)
# Add splicemonitor to command
# Parse output for actual detections
# Update counter with real detections
```

## 🤔 **Questions to Answer Before Implementation**

1. **Does TSDuck output injection confirmations?**
   - Need to test with `--verbose` or `--debug` flags
   - Check actual console output during injection

2. **Can we use splicemonitor for tracking?**
   - Test if splicemonitor can detect injected markers
   - Check output format

3. **What's the best balance?**
   - Simple config-based for now?
   - Or implement splicemonitor detection?

## 📝 **Next Steps**

1. ✅ Research TSDuck documentation (done)
2. ⏳ **Test TSDuck with --verbose flag** to see actual output
3. ⏳ **Test splicemonitor** to see if it detects injected markers
4. ⏳ **Decide on implementation approach** based on test results
5. ⏳ **Implement chosen solution**

## 💡 **My Recommendation**

**Start with Solution 1 (Configuration-Based)** because:
- ✅ Quick to implement
- ✅ Works immediately
- ✅ Reasonable accuracy for most cases
- ✅ Can enhance later with Solution 2

**Then enhance with Solution 2 (splicemonitor)** for:
- ✅ Real detection capability
- ✅ Production-grade accuracy
- ✅ Verification that injection worked

## 🔬 **Testing Plan**

Before implementing, we should test:

1. **Test 1: Verbose Output**
   ```bash
   tsp -I hls <input> -P spliceinject --files <marker.xml> --verbose -O null
   ```
   - Check if output shows injection confirmations

2. **Test 2: splicemonitor Detection**
   ```bash
   tsp -I hls <input> -P spliceinject --files <marker.xml> -P splicemonitor -O null
   ```
   - Check if splicemonitor detects injected markers

3. **Test 3: Debug Output**
   ```bash
   tsp -I hls <input> -P spliceinject --files <marker.xml> --debug=2 -O null
   ```
   - Check debug output for injection details

## 📋 **Decision Points**

1. **Do we need 100% accurate detection?**
   - If yes → Use splicemonitor
   - If no → Config-based is sufficient

2. **Is performance critical?**
   - If yes → Config-based (lighter)
   - If no → splicemonitor (more accurate)

3. **Do we want to verify injection worked?**
   - If yes → splicemonitor (real detection)
   - If no → Config-based (assumes success)

