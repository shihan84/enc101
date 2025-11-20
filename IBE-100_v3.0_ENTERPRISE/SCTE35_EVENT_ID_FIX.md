# ✅ SCTE-35 Event ID Incremental Fix

## Problem
Distributor reported that CUE-IN and CUE-OUT markers were being received with non-unique event IDs. Event IDs should be incremental and unique for each marker.

## Solution Implemented

### 1. Automatic Event ID Management
- ✅ **State Persistence**: Event IDs are now tracked in `.scte35_state.json` file
- ✅ **Auto-Increment**: Each marker automatically gets the next sequential event ID
- ✅ **Range Management**: IDs wrap around from 99999 to 10000 if needed

### 2. CUE Pair Generation
- ✅ **Sequential IDs**: CUE-OUT and CUE-IN pairs now get sequential event IDs
  - CUE-OUT: Uses base event ID (e.g., 10023)
  - CUE-IN: Uses base event ID + 1 (e.g., 10024)
- ✅ **Automatic Tracking**: Last used event ID is saved after each generation

### 3. UI Enhancements
- ✅ **Auto-Increment Checkbox**: Option to enable/disable automatic event ID increment
- ✅ **Generate CUE Pair Button**: New button to generate CUE-OUT/CUE-IN pairs with sequential IDs
- ✅ **Event ID Display**: Shows the next available event ID when auto-increment is enabled

## Usage

### Option 1: Auto-Increment (Recommended)
1. Check "Auto Increment" checkbox
2. Click "🎬 Generate CUE Pair"
3. System automatically assigns:
   - CUE-OUT: Event ID 10023
   - CUE-IN: Event ID 10024
4. Next pair will use 10025 and 10026, etc.

### Option 2: Manual Event ID
1. Uncheck "Auto Increment"
2. Set desired Event ID manually
3. Click "🎬 Generate CUE Pair"
4. CUE-OUT uses your ID, CUE-IN uses ID + 1

### Option 3: Single Marker
1. Select marker type (CUE-OUT, CUE-IN, etc.)
2. Enable/disable auto-increment as needed
3. Click "🎯 Generate Marker"
4. Event ID increments automatically if enabled

## Technical Details

### State File
- Location: `scte35_final/.scte35_state.json`
- Format:
```json
{
  "last_event_id": 10024
}
```

### Service Methods
- `get_next_event_id()`: Returns next available event ID
- `generate_cue_pair()`: Generates CUE-OUT/CUE-IN with sequential IDs
- `generate_marker()`: Enhanced with auto-increment support

## Benefits
- ✅ **Unique Event IDs**: Every marker gets a unique, incremental ID
- ✅ **No Manual Tracking**: System automatically manages event IDs
- ✅ **Persistent State**: Event IDs persist across application restarts
- ✅ **Distributor Compliant**: Meets requirement for incremental event IDs

---

**Status**: ✅ **FIXED - Event IDs are now incremental and unique**

