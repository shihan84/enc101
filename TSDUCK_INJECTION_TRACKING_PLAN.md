# 📋 TSDuck SCTE-35 Injection Tracking - Research & Plan

## 🔍 **Research: TSDuck spliceinject Plugin Output**

### **Current Understanding**

1. **TSDuck spliceinject Plugin**:
   - Handles SCTE-35 marker injection internally
   - Accepts XML/JSON/binary marker files
   - Injects markers based on `--inject-count` and `--inject-interval`
   - No explicit "injection confirmed" messages in standard output

2. **What We Know**:
   - Plugin processes files from `--files` directory
   - Markers are injected according to configuration
   - TSDuck doesn't provide explicit injection confirmation in output
   - We need to find alternative ways to track injections

### **Possible Tracking Methods**

#### **Method 1: File-Based Tracking** ✅ (Recommended)
- **Concept**: Track when marker files are loaded/processed
- **Implementation**: 
  - Monitor when files are read from `--files` directory
  - Count files processed (if `--delete-files` is used)
  - Track file timestamps

#### **Method 2: TSDuck Output Parsing** ⚠️ (Limited)
- **Concept**: Parse TSDuck console output for injection hints
- **Challenges**:
  - TSDuck may not output explicit injection confirmations
  - Output format may vary by version
  - Need to test actual output

#### **Method 3: Stream Monitoring** ✅ (Most Accurate)
- **Concept**: Use `splicemonitor` plugin to detect injected markers
- **Implementation**:
  - Run `splicemonitor` in parallel or on output stream
  - Detect when markers appear in stream
  - Count detected markers

#### **Method 4: Configuration-Based Counting** ✅ (Simple)
- **Concept**: Count based on `--inject-count` parameter
- **Implementation**:
  - If `--inject-count=1` and marker file exists → count = 1
  - If `--inject-count=2` → count = 2
  - Simple but assumes successful injection

## 📊 **Recommended Approach: Hybrid Method**

### **Phase 1: Configuration-Based (Immediate)**
- Count markers based on:
  - Marker file provided: +1
  - `--inject-count` parameter: multiply by count
  - Preroll sequence: count all markers in sequence (CUE-OUT, CUE-IN, CUE-CRASH)

### **Phase 2: Stream Monitoring (Accurate)**
- Use `splicemonitor` to detect actual markers in stream
- More accurate but requires additional processing

### **Phase 3: File Tracking (Enhanced)**
- Monitor marker file access
- Track when files are loaded by TSDuck

## 🎯 **Implementation Plan**

### **Option A: Simple Configuration-Based (Quick Fix)**
```python
# When stream starts with marker
if marker:
    # Count based on marker type
    if marker.cue_type == CueType.PREROLL:
        # Preroll generates 3 markers (CUE-OUT, CUE-IN, CUE-CRASH)
        session.scte35_injected = 3
    else:
        # Single marker
        session.scte35_injected = config.inject_count or 1
```

**Pros**: Simple, immediate, works now  
**Cons**: Assumes successful injection, not actual detection

### **Option B: Stream Monitoring (Accurate)**
```python
# Use splicemonitor to detect actual markers
# Run in parallel or on output stream
# Count detected markers
```

**Pros**: Accurate, real detection  
**Cons**: More complex, additional processing

### **Option C: Hybrid (Best of Both)**
```python
# Start with configuration-based count
# Enhance with stream monitoring if available
# Fallback to configuration if monitoring fails
```

**Pros**: Best accuracy, fallback available  
**Cons**: More code, but robust

## 🤔 **Questions to Answer**

1. **Does TSDuck output injection confirmations?**
   - Need to test with verbose/debug flags
   - Check actual console output

2. **Can we use splicemonitor for tracking?**
   - Monitor output stream for injected markers
   - Count detected markers

3. **Is file-based tracking reliable?**
   - Track when files are loaded
   - Monitor file access

## 📝 **Next Steps**

1. ✅ Research TSDuck documentation (in progress)
2. ⏳ Test TSDuck output with verbose flags
3. ⏳ Check if splicemonitor can detect injected markers
4. ⏳ Decide on implementation approach
5. ⏳ Implement chosen method

## 💡 **Recommendation**

**Start with Option A (Configuration-Based)** because:
- ✅ Simple and immediate
- ✅ Works with current setup
- ✅ No additional processing needed
- ✅ Can enhance later with monitoring

**Then enhance with Option C (Hybrid)** for:
- ✅ More accurate tracking
- ✅ Real detection capability
- ✅ Better user confidence

