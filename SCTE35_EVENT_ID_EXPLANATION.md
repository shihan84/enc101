# 📘 SCTE-35 Event ID Explanation

## What is an Event ID?

**Event ID** (also called `splice_event_id`) is a unique identifier in each SCTE-35 marker that tells the receiving system (your distributor's server) which specific ad insertion event this marker represents.

Think of it like a **serial number** for each ad break marker.

## Why Must Event IDs Be Incremental?

### The Problem (What Your Distributor Reported)

When you send multiple SCTE-35 markers to your distributor:
- **CUE-OUT marker** (starts ad break) - needs Event ID
- **CUE-IN marker** (ends ad break) - needs Event ID

**Before the fix:**
- Both markers might have the **same Event ID** (e.g., both use 10023)
- Or Event IDs might be **random/non-sequential** (e.g., 10023, 10050, 10012)

**What the distributor needs:**
- Each marker must have a **unique, sequential Event ID**
- Example: CUE-OUT = 10023, CUE-IN = 10024
- Next pair: CUE-OUT = 10025, CUE-IN = 10026
- And so on...

### Why It Matters

1. **Tracking**: Distributor can track which markers belong together (pairs)
2. **Sequencing**: They know the order of ad breaks
3. **Validation**: They can detect missing or duplicate markers
4. **Compliance**: Industry standards require unique, sequential IDs

## How Our Fix Works

### Automatic Incremental System

```
Initial State: Last Event ID = 10022

User clicks "Generate CUE Pair":
  → CUE-OUT generated with Event ID = 10023 ✅
  → CUE-IN generated with Event ID = 10024 ✅
  → System saves: Last Event ID = 10024

User clicks "Generate CUE Pair" again:
  → CUE-OUT generated with Event ID = 10025 ✅
  → CUE-IN generated with Event ID = 10026 ✅
  → System saves: Last Event ID = 10026

And so on... always incrementing!
```

### State Persistence

The system remembers the last used Event ID in a file:
- **File**: `scte35_final/.scte35_state.json`
- **Content**: `{"last_event_id": 10026}`
- **Purpose**: Even if you close and reopen the app, it continues from where it left off

### Example Workflow

**Scenario: You need to send 3 ad breaks to your distributor**

1. **First Ad Break:**
   - Generate CUE Pair → CUE-OUT (ID: 10023), CUE-IN (ID: 10024)
   - Send both markers to distributor

2. **Second Ad Break:**
   - Generate CUE Pair → CUE-OUT (ID: 10025), CUE-IN (ID: 10026)
   - Send both markers to distributor

3. **Third Ad Break:**
   - Generate CUE Pair → CUE-OUT (ID: 10027), CUE-IN (ID: 10028)
   - Send both markers to distributor

**Result:** Distributor receives:
- ✅ Unique Event IDs (10023, 10024, 10025, 10026, 10027, 10028)
- ✅ Sequential order (incrementing by 1)
- ✅ Pairs are identifiable (10023-10024, 10025-10026, 10027-10028)

## What Happens When Markers Hit the Server?

### Your Distributor's Server Receives:

```xml
<!-- Marker 1: CUE-OUT -->
<splice_insert splice_event_id="10023" ...>
  <break_duration duration="600000" />
</splice_insert>

<!-- Marker 2: CUE-IN -->
<splice_insert splice_event_id="10024" ...>
  <break_duration duration="0" />
</splice_insert>

<!-- Marker 3: CUE-OUT -->
<splice_insert splice_event_id="10025" ...>
  <break_duration duration="600000" />
</splice_insert>

<!-- Marker 4: CUE-IN -->
<splice_insert splice_event_id="10026" ...>
  <break_duration duration="0" />
</splice_insert>
```

### Server Processing:

1. **Receives Marker 10023 (CUE-OUT)**
   - Server: "Ad break starting, Event ID 10023"
   - Server: "Waiting for CUE-IN with ID 10024"

2. **Receives Marker 10024 (CUE-IN)**
   - Server: "Ad break ending, Event ID 10024"
   - Server: "Pair complete: 10023-10024 ✅"

3. **Receives Marker 10025 (CUE-OUT)**
   - Server: "New ad break starting, Event ID 10025"
   - Server: "This is sequential (10024 → 10025) ✅"

4. **Receives Marker 10026 (CUE-IN)**
   - Server: "Ad break ending, Event ID 10026"
   - Server: "Pair complete: 10025-10026 ✅"

### If Event IDs Were NOT Incremental:

**Bad Example (Same IDs):**
```
Marker 1: CUE-OUT (ID: 10023)
Marker 2: CUE-IN (ID: 10023)  ❌ Same ID!
Marker 3: CUE-OUT (ID: 10023)  ❌ Same ID again!
```

**Server Confusion:**
- "Is this the same event or a new one?"
- "Which CUE-IN belongs to which CUE-OUT?"
- "Are there missing markers?"
- **Result**: Server rejects or misprocesses markers

## Technical Implementation

### In the Code:

```python
# Get next available Event ID
def get_next_event_id(self) -> int:
    next_id = self._last_event_id + 1
    if next_id > 99999:
        next_id = 10000  # Wrap around
    return next_id

# Generate CUE pair with sequential IDs
def generate_cue_pair(...):
    base_id = self.get_next_event_id()  # e.g., 10023
    cue_out = generate_marker(event_id=base_id, ...)  # 10023
    cue_in = generate_marker(event_id=base_id + 1, ...)  # 10024
    self._save_last_event_id(cue_in.event_id)  # Save 10024
```

### State File:

```json
{
  "last_event_id": 10024
}
```

This ensures:
- ✅ Next generation starts at 10025
- ✅ Persists across app restarts
- ✅ Always sequential

## Summary

**Incremental Event ID means:**
- Each SCTE-35 marker gets a **unique, sequential number**
- Numbers **increase by 1** for each new marker
- CUE-OUT and CUE-IN in a pair are **consecutive** (e.g., 10023 and 10024)
- The system **remembers** the last ID and continues from there

**When markers hit the distributor's server:**
- Server receives markers with **unique, sequential Event IDs**
- Server can **track and pair** CUE-OUT/CUE-IN correctly
- Server can **validate** that no IDs are missing or duplicated
- Server can **process** ad breaks in the correct order

**Your distributor's requirement:**
> "Event ID should be incremental" = Each marker must have a unique ID that increases sequentially (10023, 10024, 10025, 10026...)

---

**Status**: ✅ **IMPLEMENTED - Event IDs now increment automatically and sequentially**

