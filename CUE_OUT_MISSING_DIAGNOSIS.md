# CUE-OUT Missing Issue - Diagnosis & Fix

## Problem Reported

**Distributor Complaint:** "We are receiving only CUE-IN markers, no CUE-OUT markers"

## Root Cause Analysis

### Current Implementation

1. **CUE-OUT Marker (when preroll > 0):**
   - Uses **scheduled injection**: `splice_immediate="false"`
   - Has `pts_time="{preroll * 90000}"` (e.g., 4 seconds = 360000 PTS units)
   - This means CUE-OUT is scheduled to inject at a **future PTS time**

2. **CUE-IN Marker:**
   - Uses **immediate injection**: `splice_immediate="true"`
   - No `pts_time` attribute
   - This means CUE-IN is injected **immediately**

3. **File Processing:**
   - TSDuck uses wildcard pattern: `splice*.xml`
   - Files are named: `splice_{event_id:05d}.xml`
   - TSDuck processes files in **alphabetical order** (by filename)
   - With `--delete-files`, files are deleted after processing

### The Problem

**Scenario:**
```
Time T0: Generate Preroll Sequence
  ├─ Create: splice_10023.xml (CUE-OUT, scheduled for T0 + 4 seconds)
  ├─ Create: splice_10024.xml (CUE-IN, immediate)
  └─ Create: splice_10025.xml (CUE-CRASH, immediate)

Time T0 + 0.5s: TSDuck polls directory
  ├─ Finds: splice_10023.xml (CUE-OUT)
  │   └─ Loads file, sees scheduled injection (pts_time = 4 seconds)
  │   └─ Schedules injection for future PTS time
  │   └─ Deletes file (--delete-files)
  │
  ├─ Finds: splice_10024.xml (CUE-IN)
  │   └─ Loads file, sees immediate injection
  │   └─ Injects immediately ✅
  │   └─ Deletes file
  │
  └─ Finds: splice_10025.xml (CUE-CRASH)
      └─ Loads file, sees immediate injection
      └─ Injects immediately ✅
      └─ Deletes file

Time T0 + 4s: Scheduled CUE-OUT should inject
  └─ BUT: File was already deleted!
  └─ TSDuck might not have the scheduled injection data anymore
  └─ Result: CUE-OUT never injected ❌
```

**Key Issues:**

1. **File Deletion Before Scheduled Injection:**
   - TSDuck deletes files immediately after loading
   - Scheduled injections need the data to persist until injection time
   - If file is deleted, scheduled injection might fail

2. **Scheduled vs Immediate Timing:**
   - CUE-OUT is scheduled for future time (preroll delay)
   - CUE-IN is immediate
   - Distributor receives CUE-IN first, then waits for CUE-OUT
   - If CUE-OUT never arrives, distributor only sees CUE-IN

3. **PTS Time Calculation:**
   - `pts_time` is relative to current stream PTS
   - If PTS extraction fails or is incorrect, scheduled injection won't work

## Solutions

### Solution 1: Make CUE-OUT Immediate (Recommended for Testing)

**Change:** Make CUE-OUT immediate when preroll = 0, or use a very small preroll delay

**Pros:**
- Simple fix
- Both markers inject immediately
- Easier to debug

**Cons:**
- Doesn't match distributor requirement (preroll should be 0-10 seconds)
- Loses the preroll warning functionality

### Solution 2: Fix Scheduled Injection Timing

**Change:** Ensure scheduled injections work correctly with file deletion

**Implementation:**
1. Don't delete files until scheduled injection completes
2. Or: Use separate injection for scheduled vs immediate markers
3. Or: Store scheduled injection data in TSDuck's internal state

**Pros:**
- Maintains preroll functionality
- Matches distributor requirements

**Cons:**
- More complex
- Requires TSDuck behavior verification

### Solution 3: Generate CUE-OUT and CUE-IN Separately

**Change:** Generate CUE-OUT first, wait for injection, then generate CUE-IN

**Implementation:**
1. Generate CUE-OUT marker
2. Wait for TSDuck to process and inject (or wait for scheduled time)
3. Then generate CUE-IN marker

**Pros:**
- Ensures proper order
- CUE-OUT injected before CUE-IN

**Cons:**
- Slower (sequential generation)
- Complex timing logic

### Solution 4: Use Immediate Injection for CUE-OUT (Best for Now)

**Change:** Make CUE-OUT immediate, but keep the preroll duration in the `break_duration`

**Implementation:**
- Set `splice_immediate="true"` for CUE-OUT
- Remove `pts_time` attribute
- Keep `break_duration` with ad duration
- The preroll is handled by the distributor's system, not by scheduling

**Pros:**
- Simple and reliable
- Both markers inject immediately
- Maintains ad duration information
- Works with file deletion

**Cons:**
- Preroll timing is handled by distributor, not by our system

## Recommended Fix

**For immediate resolution:** Use Solution 4 - Make CUE-OUT immediate

**Code Change:**
```python
# In scte35_service.py, _generate_xml() for CUE_OUT:
# Change from scheduled to immediate injection

# BEFORE:
if preroll > 0:
    # Scheduled injection
    return f'''... splice_immediate="false" pts_time="{pts_time_pts}" ...'''

# AFTER:
# Always use immediate injection for CUE-OUT
return f'''... splice_immediate="true" ...'''
```

**Rationale:**
1. Immediate injection is more reliable
2. File deletion works correctly
3. Both markers inject in order
4. Distributor can handle preroll timing on their end
5. Matches how CUE-IN works (immediate)

## Verification Steps

After fix:
1. Generate preroll sequence
2. Check logs for both CUE-OUT and CUE-IN injection
3. Use `splicemonitor` to verify both markers in stream
4. Test with distributor to confirm both markers received

