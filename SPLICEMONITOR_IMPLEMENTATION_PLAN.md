# 🎯 splicemonitor Implementation Plan - Monitor from Your Side

## ✅ **Answer: YES, You Can Monitor from Your Side!**

### **How TSDuck Pipeline Works**

TSDuck processes plugins **in sequence** (left to right):

```
Input → Plugin1 → Plugin2 → Plugin3 → Output
```

### **Your Current Pipeline**

```
Input → SDT → PMT → spliceinject → analyze → Output (SRT)
```

### **With splicemonitor Added**

```
Input → SDT → PMT → spliceinject → splicemonitor → analyze → Output (SRT)
                                    ↑
                            Detects markers HERE
                            (after injection, before output)
```

## 🎯 **Why This Works**

1. **spliceinject** injects markers into the stream
2. **splicemonitor** (placed after spliceinject) sees the stream **with markers already injected**
3. **splicemonitor** detects and reports the markers
4. Stream continues to **analyze** and then **Output**

**Result**: You can verify markers are in the stream **before** sending to distributor!

## 📊 **Implementation Strategy**

### **Option 1: Add splicemonitor to Main Stream** ⭐⭐⭐ (Recommended)

**Pros:**
- ✅ Real-time detection of injected markers
- ✅ Verifies injection worked
- ✅ Accurate counting
- ✅ No separate process needed

**Cons:**
- ⚠️ Slight performance overhead (minimal)
- ⚠️ Need to parse output

**Implementation:**
```python
# In tsduck_service.py, add after spliceinject:
if marker_path and marker_path.exists():
    command.extend(["-P", "spliceinject", ...])
    
    # Add splicemonitor to detect injected markers
    command.extend(["-P", "splicemonitor",
        "--pid", str(config.scte35_pid),
        "--json"])  # JSON output for easier parsing
```

### **Option 2: Separate Monitoring Process** ⚠️ (Not Recommended)

**Pros:**
- ✅ Doesn't affect main stream

**Cons:**
- ❌ Would need to monitor output stream (SRT) which is more complex
- ❌ Requires separate connection
- ❌ More overhead

## 🔧 **Implementation Details**

### **1. Add splicemonitor to TSDuck Command**

**Location**: `src/services/tsduck_service.py`

**Code:**
```python
# After spliceinject plugin
if marker_path and marker_path.exists():
    command.extend(["-P", "spliceinject", ...])
    
    # Add splicemonitor to verify injection
    command.extend(["-P", "splicemonitor",
        "--pid", str(config.scte35_pid),
        "--json"])  # JSON format for easier parsing
```

### **2. Parse splicemonitor Output**

**Location**: `src/services/stream_service.py`

**Code:**
```python
def _parse_splicemonitor_output(self, line: str, session: StreamSession):
    """Parse splicemonitor JSON output for SCTE-35 detections"""
    try:
        # splicemonitor outputs JSON when --json flag is used
        if '{' in line and 'splice' in line.lower():
            import json
            try:
                data = json.loads(line)
                # Check for splice_insert detection
                if 'splice_insert' in data or 'event_id' in data:
                    session.scte35_injected += 1
                    self.logger.info(f"SCTE-35 marker detected: {data}")
            except json.JSONDecodeError:
                pass
    except Exception as e:
        self.logger.debug(f"Splicemonitor parsing error: {e}")
```

### **3. Update Stream Service**

**Location**: `src/services/stream_service.py` in `_run_stream` method

**Code:**
```python
# In the output reading loop:
for line in self._process.stdout:
    line_text = line.strip()
    self._notify_output(f"[TSDuck] {line_text}")
    
    # Parse splicemonitor output for marker detection
    self._parse_splicemonitor_output(line_text, session)
    
    # Parse real metrics from TSDuck analyze plugin
    self._parse_metrics_from_output(line_text, session)
```

## 📋 **Expected splicemonitor Output**

### **JSON Format (with --json flag)**
```json
{
  "splice_insert": {
    "event_id": 10023,
    "out_of_network": true,
    "splice_immediate": true,
    "unique_program_id": 1
  }
}
```

### **Text Format (without --json)**
```
splicemonitor: splice_insert detected, event_id=10023, out_of_network=true
```

## 🎯 **Benefits of This Approach**

1. ✅ **Real Detection**: Counts actual markers in stream
2. ✅ **Verification**: Confirms injection worked
3. ✅ **Accurate**: No assumptions, real detection
4. ✅ **On Your Side**: No need for distributor to monitor
5. ✅ **Production-Ready**: Uses TSDuck's built-in monitoring

## ⚠️ **Considerations**

1. **Performance**: Minimal overhead (splicemonitor is lightweight)
2. **Output Parsing**: Need to parse JSON or text output
3. **Multiple Injections**: If `--inject-count=2`, splicemonitor will detect 2 markers
4. **Preroll Sequence**: Will detect all 3 markers (CUE-OUT, CUE-IN, CUE-CRASH)

## 📝 **Implementation Steps**

1. ✅ Add `splicemonitor` plugin to TSDuck command (after `spliceinject`)
2. ✅ Add `--json` flag for easier parsing
3. ✅ Create `_parse_splicemonitor_output` method in `StreamService`
4. ✅ Call parser in output reading loop
5. ✅ Update `session.scte35_injected` counter
6. ✅ Test with actual stream

## 🧪 **Testing Plan**

1. **Test 1: Single Marker**
   - Generate single CUE-OUT marker
   - Start stream
   - Verify count = 1

2. **Test 2: Preroll Sequence**
   - Generate preroll (3 markers)
   - Start stream
   - Verify count = 3

3. **Test 3: Multiple Injections**
   - Set `--inject-count=2`
   - Start stream
   - Verify count = 2 (or 6 for preroll)

## 💡 **Recommendation**

**Implement splicemonitor detection** because:
- ✅ Most accurate method
- ✅ Verifies injection worked
- ✅ Works from your side
- ✅ Production-grade solution
- ✅ Uses TSDuck's built-in capabilities

This is better than configuration-based counting because it's **real detection**, not assumption!

