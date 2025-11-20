# ✅ SCTE-35 Standard Compliance Analysis

## 📋 **Standard Parameters Used**

Our preroll marker implementation uses **standard SCTE-35 parameters** that are globally recognized:

### ✅ **Standard Parameters Implemented**

1. **`splice_event_id`** ✓
   - Unique identifier for each splice event
   - Used globally for event tracking
   - **Our Implementation**: ✅ Correctly implemented

2. **`unique_program_id`** ✓
   - Provides unique identification for viewing event within service
   - **Our Implementation**: ✅ Set to "1" (standard default)

3. **`out_of_network`** ✓
   - Indicates if splice event is for out-of-network (ad) insertion
   - **Our Implementation**: ✅ Set to "true" for preroll markers

4. **`splice_immediate`** ✓
   - Specifies if splice should occur immediately
   - **Our Implementation**: ✅ Correctly implemented (configurable)

5. **`break_duration`** ✓
   - Duration of break in 90kHz clock ticks
   - **Our Implementation**: ✅ Correctly uses `ad_duration * 90000` (standard format)

6. **`auto_return`** ✓
   - Flag indicating if splicer should return to network at end of break
   - **Our Implementation**: ✅ Set to "true" for preroll markers

7. **`avail_num` and `avails_expected`** ✓
   - Standard availability tracking parameters
   - **Our Implementation**: ✅ Both set to "1" (standard)

8. **`pts_time`** ✓
   - Presentation Time Stamp for scheduled events
   - **Our Implementation**: ✅ Correctly uses 90kHz ticks (`preroll * 90000`)

## ⚠️ **Industry Standard Recommendation**

### **Preroll Duration**

- **Industry Standard Minimum**: **4.0 seconds** (recommended by SCTE-35 standard)
- **Previous Default**: 2 seconds
- **Updated Default**: **4 seconds** ✅

**Rationale**: The 4.0-second minimum preroll allows downstream systems adequate time to:
- Prepare for the splice event
- Buffer content
- Switch to ad content smoothly
- Avoid playback interruptions

## 📊 **Compliance Summary**

| Parameter | Standard | Our Implementation | Status |
|-----------|----------|-------------------|--------|
| `splice_event_id` | Required | ✅ Implemented | ✅ Compliant |
| `unique_program_id` | Required | ✅ Set to "1" | ✅ Compliant |
| `out_of_network` | Required | ✅ Set to "true" | ✅ Compliant |
| `splice_immediate` | Required | ✅ Configurable | ✅ Compliant |
| `break_duration` | Required | ✅ 90kHz ticks | ✅ Compliant |
| `auto_return` | Recommended | ✅ Set to "true" | ✅ Compliant |
| `avail_num` | Required | ✅ Set to "1" | ✅ Compliant |
| `avails_expected` | Required | ✅ Set to "1" | ✅ Compliant |
| `pts_time` | For scheduled | ✅ 90kHz ticks | ✅ Compliant |
| **Preroll Duration** | **Min 4.0s** | **✅ Updated to 4s** | **✅ Compliant** |

## 🎯 **Conclusion**

✅ **Our implementation is fully compliant with SCTE-35 standards**

All standard parameters are correctly implemented and follow global industry practices. The only update needed was adjusting the default preroll duration from 2 seconds to 4 seconds to match the industry-recommended minimum.

## 📚 **References**

- SCTE-35 Digital Program Insertion Cueing Message Standard
- Industry recommendation: Minimum 4.0 seconds preroll for reliable ad insertion
- TSDuck documentation for SCTE-35 XML format compliance

