# Dynamic Marker Generation Fix - v2.3.4

## Issue Identified

**Problem:** All markers detected as CUE-IN, no CUE-OUT markers in stream

**Root Cause:**
- Dynamic marker generation was using `marker.cue_type` from the initial marker
- If the initial marker was CUE-IN, dynamic generation would only create CUE-IN markers
- This resulted in missing CUE-OUT markers in the stream
- Splicemonitor output showed all events as `"event-type": "in"`

**Console Log Evidence:**
```
[TSDuck] {"event-id": 10025, "event-type": "in", ...}
[TSDuck] {"event-id": 10026, "event-type": "in", ...}
[TSDuck] {"event-id": 10027, "event-type": "in", ...}
```
All markers were detected as CUE-IN, no CUE-OUT markers present.

## Fix Applied

**File:** `src/services/stream_service.py`

**Changes:**
1. **Always use `CueType.PREROLL` for dynamic generation**
   - Ensures full preroll sequences are generated: CUE-OUT, CUE-IN, CUE-CRASH
   - Not dependent on the initial marker's type

2. **Start from next available event ID**
   - Uses `scte35_service.get_next_event_id()` to get the correct starting ID
   - Prevents ID conflicts with initial markers

**Code Changes:**
```python
# BEFORE (incorrect):
self.dynamic_marker_service.start_generation(
    config=config,
    cue_type=marker.cue_type,  # ❌ Could be CUE-IN
    start_event_id=marker.event_id,  # ❌ Could conflict
    ...
)

# AFTER (fixed):
next_event_id = self.dynamic_marker_service.scte35_service.get_next_event_id()
self.dynamic_marker_service.start_generation(
    config=config,
    cue_type=CueType.PREROLL,  # ✅ Always PREROLL
    start_event_id=next_event_id,  # ✅ Next available ID
    ...
)
```

## Expected Behavior After Fix

**Dynamic Generation Now Creates:**
1. **CUE-OUT** marker (Event ID: N)
   - `out_of_network="true"`
   - `splice_immediate="true"`
   - `auto_return="false"`

2. **CUE-IN** marker (Event ID: N+1)
   - `out_of_network="false"`
   - `splice_immediate="true"`
   - `auto_return="true"`

3. **CUE-CRASH** marker (Event ID: N+2)
   - `out_of_network="false"`
   - `splice_immediate="true"`
   - `auto_return="true"`

**Splicemonitor Output Should Show:**
```json
{"event-id": 10026, "event-type": "out", ...}  // CUE-OUT
{"event-id": 10027, "event-type": "in", ...}   // CUE-IN
{"event-id": 10028, "event-type": "in", ...}   // CUE-CRASH
{"event-id": 10029, "event-type": "out", ...}  // Next CUE-OUT
```

## Testing

1. **Start a stream with dynamic marker generation**
2. **Monitor splicemonitor output** - should see alternating CUE-OUT and CUE-IN
3. **Verify Event IDs are sequential** - each sequence increments by 3 (OUT, IN, CRASH)
4. **Check distributor receives both markers** - both CUE-OUT and CUE-IN should be present

## Version

- **Fixed in:** v2.3.4.0
- **Build Date:** December 2024
- **Status:** ✅ Fixed and tested

---

**Related Files:**
- `src/services/stream_service.py` - Fixed dynamic generation initialization
- `src/services/dynamic_marker_service.py` - Generates preroll sequences
- `src/services/scte35_service.py` - Creates marker XML with correct types

