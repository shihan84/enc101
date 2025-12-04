# IBE-210 Enterprise v2.3.5.0 - Release Notes

**Release Date:** December 2024  
**Version:** 2.3.5.0

## Overview

This release fixes a critical issue where dynamic marker generation was only creating CUE-IN markers, missing CUE-OUT markers. The fix ensures proper preroll sequences (CUE-OUT, CUE-IN, CUE-CRASH) are generated for continuous streaming.

## Critical Fix

### Dynamic Marker Generation Fix

**Issue:** All markers detected as CUE-IN only, no CUE-OUT markers in stream

**Root Cause:**
- Dynamic marker generation was using the initial marker's `cue_type` (which could be CUE-IN)
- This caused only CUE-IN markers to be generated instead of full preroll sequences
- Distributors were receiving only CUE-IN markers, missing CUE-OUT markers

**Fix Applied:**
- **Always use `CueType.PREROLL` for dynamic generation** - ensures full sequences are generated
- **Start from next available event ID** - prevents ID conflicts with initial markers
- Dynamic generation now creates proper sequences: CUE-OUT → CUE-IN → CUE-CRASH

**Files Changed:**
- `src/services/stream_service.py` - Fixed dynamic generation initialization

## Verification

**Before Fix:**
```
[TSDuck] {"event-id": 10025, "event-type": "in", ...}
[TSDuck] {"event-id": 10026, "event-type": "in", ...}
[TSDuck] {"event-id": 10027, "event-type": "in", ...}
```
All markers were CUE-IN only.

**After Fix:**
```
[TSDuck] {"event-id": 10026, "event-type": "out", ...}  // CUE-OUT ✅
[TSDuck] {"event-id": 10027, "event-type": "in", ...}   // CUE-IN ✅
[TSDuck] {"event-id": 10028, "event-type": "in", ...}   // CUE-CRASH ✅
[TSDuck] {"event-id": 10029, "event-type": "out", ...}  // Next CUE-OUT ✅
```
Both CUE-OUT and CUE-IN markers are now present.

## Technical Details

### Dynamic Generation Behavior

**Preroll Sequence Pattern:**
- **CUE-OUT** (Event ID: N)
  - `out_of_network="true"`
  - `splice_immediate="true"`
  - Signals start of ad break
  
- **CUE-IN** (Event ID: N+1)
  - `out_of_network="false"`
  - `splice_immediate="true"`
  - Signals end of ad break
  
- **CUE-CRASH** (Event ID: N+2)
  - `out_of_network="false"`
  - `splice_immediate="true"`
  - Emergency return to program

**Event ID Management:**
- Sequential, incremental IDs (10000-99999 range)
- Each preroll sequence increments by 3 (OUT, IN, CRASH)
- No ID conflicts or duplicates

## Improvements

- **Reliable Marker Generation**: Dynamic generation now consistently creates full preroll sequences
- **Distributor Compliance**: Both CUE-OUT and CUE-IN markers are now present in stream
- **Better Event ID Management**: Proper sequencing prevents conflicts

## Testing

✅ Verified CUE-OUT markers are generated and detected  
✅ Verified CUE-IN markers are generated and detected  
✅ Verified Event IDs are sequential and incremental  
✅ Verified TSDuck correctly identifies marker types  
✅ Verified SCTE-35 stream is active and healthy  

## Installation

1. Download `IBE-210_Enterprise.exe` from the releases page
2. Close any running instances of IBE-210 Enterprise
3. Replace the existing executable with the new version
4. Launch the application

## Upgrade Notes

- No configuration changes required
- Existing marker files and settings are compatible
- No database migration needed
- **Important**: This fix ensures distributors receive both CUE-OUT and CUE-IN markers

## Known Issues

None at this time.

## Support

For issues, questions, or feature requests, please contact support or open an issue on the repository.

---

**Previous Version:** [v2.3.4.0 Release Notes](RELEASE_NOTES_v2.3.4.md)  
**Related Documentation:** [Dynamic Marker Fix Details](DYNAMIC_MARKER_FIX_v2.3.4.md)

