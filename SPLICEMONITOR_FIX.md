# 🔧 splicemonitor Syntax Fix

## ❌ **Issue Found**

The `splicemonitor` plugin was incorrectly configured with `--pid` parameter:

```bash
-P splicemonitor --pid 500 --json  # ❌ WRONG - --pid is not a valid option
```

**Error Message:**
```
[TSDuck] * Error: splicemonitor: unknown option --pid
[TSDuck] * Error: splicemonitor: no parameter allowed, use options only
```

## ✅ **Fix Applied**

The `splicemonitor` plugin **doesn't need** a `--pid` parameter. It automatically monitors **all SCTE-35 splice information** in the stream.

**Correct Syntax:**
```bash
-P splicemonitor --json  # ✅ CORRECT
```

## 📋 **What Changed**

**File**: `src/services/tsduck_service.py`

**Before:**
```python
command.extend(["-P", "splicemonitor",
    "--pid", str(config.scte35_pid),  # ❌ Removed
    "--json"])
```

**After:**
```python
command.extend(["-P", "splicemonitor",
    "--json"])  # ✅ Correct - no --pid needed
```

## 🎯 **How splicemonitor Works**

According to TSDuck documentation:
- `splicemonitor` automatically detects SCTE-35 splice information in the stream
- It monitors **all** SCTE-35 splice commands (not just a specific PID)
- The `--json` flag outputs detection in JSON format for easier parsing
- No PID specification needed - it finds SCTE-35 data automatically

## ✅ **Result**

The command now works correctly:
```bash
tsp -I hls <input> \
    -P spliceinject --pid 500 --files <marker.xml> \
    -P splicemonitor --json \
    -P analyze --interval 1 \
    -O srt <output>
```

The `splicemonitor` will now correctly detect injected markers and output JSON that our parser can process!

