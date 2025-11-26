# 📘 Event ID Incremental - Complete Explanation

## What Does "Event ID Should Be Incremental" Mean?

**Incremental Event ID** means that each SCTE-35 marker must have a **unique, sequential number** that **increases by 1** for each new marker.

### Simple Example:

```
✅ CORRECT (Incremental):
Marker 1: Event ID = 10023
Marker 2: Event ID = 10024  (10023 + 1)
Marker 3: Event ID = 10025  (10024 + 1)
Marker 4: Event ID = 10026  (10025 + 1)
```

```
❌ WRONG (Not Incremental):
Marker 1: Event ID = 10023
Marker 2: Event ID = 10023  (Same ID - ERROR!)
Marker 3: Event ID = 10050  (Jumped - ERROR!)
Marker 4: Event ID = 10012  (Went backwards - ERROR!)
```

---

## Why Your Distributor Needs This

### 1. **Tracking Ad Break Pairs**

When you send a CUE-OUT (start ad break) and CUE-IN (end ad break), the distributor needs to know they belong together:

**✅ CORRECT (Incremental):**
```
CUE-OUT: Event ID = 10023  (Starts ad break)
CUE-IN:  Event ID = 10024  (Ends ad break)
         ↑ Sequential - distributor knows they're a pair!
```

**❌ WRONG (Same ID):**
```
CUE-OUT: Event ID = 10023  (Starts ad break)
CUE-IN:  Event ID = 10023  (Ends ad break)
         ↑ Same ID - distributor can't tell which is which!
```

### 2. **Sequencing Ad Breaks**

The distributor needs to know the **order** of ad breaks:

**✅ CORRECT:**
```
Ad Break 1: CUE-OUT (10023) → CUE-IN (10024)
Ad Break 2: CUE-OUT (10025) → CUE-IN (10026)
Ad Break 3: CUE-OUT (10027) → CUE-IN (10028)
         ↑ Sequential order is clear!
```

**❌ WRONG:**
```
Ad Break 1: CUE-OUT (10023) → CUE-IN (10024)
Ad Break 2: CUE-OUT (10050) → CUE-IN (10012)
         ↑ Random IDs - distributor doesn't know the order!
```

### 3. **Detecting Missing Markers**

If IDs are incremental, the distributor can detect if a marker is missing:

**✅ CORRECT:**
```
Received: 10023, 10024, 10025, 10027
          ↑ Missing 10026 - distributor knows something's wrong!
```

**❌ WRONG:**
```
Received: 10023, 10024, 10050, 10012
          ↑ Random IDs - can't detect missing markers!
```

### 4. **Industry Standard Compliance**

SCTE-35 standard requires:
- ✅ Each marker must have a **unique** Event ID
- ✅ Event IDs should be **sequential** (incremental)
- ✅ CUE-OUT and CUE-IN pairs should be **consecutive**

---

## How It Works in Your Application

### Current Implementation (Already Fixed!)

Your application **already supports incremental Event IDs**:

1. **State Persistence**
   - Last Event ID is saved in: `scte35_final/.scte35_state.json`
   - Example: `{"last_event_id": 10024}`
   - Even if you close the app, it remembers where it left off

2. **Automatic Increment**
   - When you generate a marker, it automatically uses the next ID
   - CUE-OUT gets ID 10023
   - CUE-IN gets ID 10024 (10023 + 1)
   - Next pair gets 10025 and 10026

3. **Profile-Specific**
   - Each profile has its own Event ID counter
   - Profile A: 10023, 10024, 10025...
   - Profile B: 10023, 10024, 10025... (separate counter)

---

## Example: What Happens When You Generate Markers

### Scenario: Generate 3 CUE Pairs

**Step 1: Generate First Pair**
```
Last Event ID: 10022 (from state file)

Generate CUE Pair:
  → CUE-OUT: Event ID = 10023 ✅
  → CUE-IN:  Event ID = 10024 ✅
  → Save: last_event_id = 10024
```

**Step 2: Generate Second Pair**
```
Last Event ID: 10024 (from state file)

Generate CUE Pair:
  → CUE-OUT: Event ID = 10025 ✅
  → CUE-IN:  Event ID = 10026 ✅
  → Save: last_event_id = 10026
```

**Step 3: Generate Third Pair**
```
Last Event ID: 10026 (from state file)

Generate CUE Pair:
  → CUE-OUT: Event ID = 10027 ✅
  → CUE-IN:  Event ID = 10028 ✅
  → Save: last_event_id = 10028
```

**Result:**
```
✅ All Event IDs are incremental:
   10023, 10024, 10025, 10026, 10027, 10028
   ↑ Sequential, no duplicates, no gaps!
```

---

## What Your Distributor Sees

### ✅ CORRECT (Incremental IDs):

**Stream Timeline:**
```
Time 00:00 → CUE-OUT (Event ID: 10023) - Ad break starts
Time 00:30 → CUE-IN  (Event ID: 10024) - Ad break ends
Time 05:00 → CUE-OUT (Event ID: 10025) - Ad break starts
Time 05:30 → CUE-IN  (Event ID: 10026) - Ad break ends
```

**Distributor's System:**
- ✅ "Received 10023 and 10024 - they're a pair!"
- ✅ "Received 10025 and 10026 - they're a pair!"
- ✅ "All IDs are sequential - everything is correct!"
- ✅ "Can track order: 10023 → 10024 → 10025 → 10026"

### ❌ WRONG (Non-Incremental IDs):

**Stream Timeline:**
```
Time 00:00 → CUE-OUT (Event ID: 10023) - Ad break starts
Time 00:30 → CUE-IN  (Event ID: 10023) - Ad break ends ❌ Same ID!
Time 05:00 → CUE-OUT (Event ID: 10050) - Ad break starts ❌ Jumped!
Time 05:30 → CUE-IN  (Event ID: 10012) - Ad break ends ❌ Went backwards!
```

**Distributor's System:**
- ❌ "Received 10023 twice - which one is CUE-OUT and which is CUE-IN?"
- ❌ "Received 10050 then 10012 - what's the order?"
- ❌ "Can't pair markers - IDs don't match!"
- ❌ "System rejects or misprocesses markers"

---

## Technical Details

### Event ID Range

- **Minimum**: 10000
- **Maximum**: 99999
- **Wrap Around**: If ID reaches 99999, it wraps back to 10000

### Code Implementation

```python
def get_next_event_id(self) -> int:
    """Get the next available event ID (incremental)"""
    next_id = self._last_event_id + 1
    # Ensure ID is within valid range (10000-99999)
    if next_id > 99999:
        next_id = 10000  # Wrap around
    return next_id
```

### State File

**Location**: `scte35_final/.scte35_state.json`

**Content**:
```json
{
  "last_event_id": 10024
}
```

**Purpose**: 
- Remembers the last used Event ID
- Ensures continuity across app restarts
- Prevents duplicate IDs

---

## Common Issues and Solutions

### Issue 1: Same Event ID for CUE-OUT and CUE-IN

**Problem:**
```
CUE-OUT: Event ID = 10023
CUE-IN:  Event ID = 10023  ❌ Same ID!
```

**Solution:**
- ✅ Use "Generate CUE Pair" button (automatically uses sequential IDs)
- ✅ Enable "Auto Increment" checkbox
- ✅ Don't manually set the same Event ID for both markers

### Issue 2: Event IDs Jump Around

**Problem:**
```
Marker 1: Event ID = 10023
Marker 2: Event ID = 10050  ❌ Jumped!
Marker 3: Event ID = 10012  ❌ Went backwards!
```

**Solution:**
- ✅ Always use "Auto Increment" mode
- ✅ Don't manually set random Event IDs
- ✅ Let the system manage Event IDs automatically

### Issue 3: Event IDs Reset

**Problem:**
```
Yesterday: Last Event ID = 10050
Today:     Last Event ID = 10023  ❌ Reset!
```

**Solution:**
- ✅ Don't delete the state file: `scte35_final/.scte35_state.json`
- ✅ The system automatically continues from last ID
- ✅ If you need to reset, manually edit the state file

---

## Best Practices

### ✅ DO:

1. **Use Auto Increment**
   - Enable "Auto Increment" checkbox
   - Let the system manage Event IDs

2. **Use Generate CUE Pair**
   - Click "Generate CUE Pair" button
   - Automatically creates sequential IDs

3. **Keep State File**
   - Don't delete `.scte35_state.json`
   - It ensures continuity

4. **One Profile = One Counter**
   - Each profile has its own Event ID counter
   - Use separate profiles for different streams

### ❌ DON'T:

1. **Don't Reuse Event IDs**
   - Never use the same Event ID twice
   - Each marker must be unique

2. **Don't Set Random IDs**
   - Don't manually set random Event IDs
   - Use auto increment instead

3. **Don't Skip Numbers**
   - Don't manually jump Event IDs (e.g., 10023 → 10050)
   - Keep them sequential

4. **Don't Delete State File**
   - Don't delete `.scte35_state.json` unless you want to reset
   - It tracks the last used ID

---

## Summary

**"Event ID should be incremental" means:**

1. ✅ Each marker gets a **unique** Event ID
2. ✅ Event IDs **increase by 1** for each new marker
3. ✅ CUE-OUT and CUE-IN pairs are **consecutive** (e.g., 10023 and 10024)
4. ✅ The system **remembers** the last ID and continues from there
5. ✅ No **duplicates**, no **gaps**, no **random jumps**

**Why it matters:**

- ✅ Distributor can **track** which markers belong together
- ✅ Distributor can **sequence** ad breaks correctly
- ✅ Distributor can **detect** missing markers
- ✅ **Compliance** with SCTE-35 industry standards

**Your application already does this correctly!** Just make sure:
- ✅ "Auto Increment" is enabled
- ✅ Use "Generate CUE Pair" button
- ✅ Don't manually set duplicate or random Event IDs

---

## Quick Reference

| What | Incremental? | Example |
|------|--------------|---------|
| ✅ Correct | Yes | 10023, 10024, 10025, 10026 |
| ❌ Wrong | No | 10023, 10023, 10050, 10012 |
| ✅ CUE Pair | Yes | OUT=10023, IN=10024 |
| ❌ CUE Pair | No | OUT=10023, IN=10023 |

---

**Your distributor's requirement is already implemented!** Just use the "Auto Increment" feature and "Generate CUE Pair" button. 🎯

