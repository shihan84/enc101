# 📘 Preroll Marker - Complete Explanation

## What is a Preroll Marker?

A **Preroll Marker** is an SCTE-35 marker that signals an **ad break that will happen BEFORE the main program content starts**.

Think of it as a **"warning signal"** that tells the distributor's system:
> "Hey! An ad break is coming in X seconds. Get ready to switch to ads!"

---

## Why Your Distributor Needs Preroll Markers

### 1. **Advanced Warning**

The distributor needs **time to prepare** for the ad break:
- Switch to ad server
- Load ad content
- Prepare for seamless transition
- Ensure no content is cut off

**Without Preroll:**
```
Stream: [Main Content] → [Ad Break] ❌ Sudden switch, no warning!
```

**With Preroll:**
```
Stream: [Main Content] → [Preroll Warning: 4s] → [Ad Break] ✅ Smooth transition!
```

### 2. **Smooth Transitions**

Preroll markers ensure:
- ✅ No content is cut off mid-sentence
- ✅ Ad server is ready
- ✅ Seamless switch from content to ads
- ✅ Professional broadcast quality

### 3. **Industry Standard**

SCTE-35 standard requires:
- ✅ Minimum 4.0 seconds preroll (industry standard)
- ✅ Warning before ad break starts
- ✅ Proper timing for ad insertion

---

## How Preroll Markers Work

### Timeline Example:

```
Time 00:00 → Stream starts
Time 00:10 → Preroll marker sent (4 seconds warning)
             "Ad break coming in 4 seconds!"
Time 00:14 → CUE-OUT marker (Ad break starts)
Time 00:44 → CUE-IN marker (Return to content)
```

### Visual Flow:

```
┌─────────────────────────────────────────┐
│  Main Content Playing                   │
│  (e.g., TV show, movie, live stream)    │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  PREROLL MARKER (4 seconds warning)    │
│  "Ad break coming in 4 seconds!"        │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  CUE-OUT (Ad break starts)              │
│  [Ad 1] [Ad 2] [Ad 3] ...               │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  CUE-IN (Return to content)             │
│  Main Content Resumes                    │
└─────────────────────────────────────────┘
```

---

## Preroll Seconds Explained

### What is "Preroll Seconds"?

**Preroll Seconds** = The **lead time** (warning period) before the ad break starts.

**Industry Standard:**
- **Minimum**: 4.0 seconds (required by SCTE-35 standard)
- **Recommended**: 4-10 seconds
- **Maximum**: 10 seconds (usually)

### Examples:

**4 Seconds Preroll:**
```
00:00 → Preroll marker sent
00:04 → Ad break starts (4 seconds later)
```

**6 Seconds Preroll:**
```
00:00 → Preroll marker sent
00:06 → Ad break starts (6 seconds later)
```

**10 Seconds Preroll:**
```
00:00 → Preroll marker sent
00:10 → Ad break starts (10 seconds later)
```

---

## Types of Preroll Markers

### 1. **Immediate Preroll** (Most Common)

**How it works:**
- Preroll marker is sent **immediately**
- Ad break starts after the preroll delay (e.g., 4 seconds)
- Used for: Live streams, real-time ad insertion

**Example:**
```
Now: Send preroll marker (4s warning)
+4s: Ad break starts
```

### 2. **Scheduled Preroll**

**How it works:**
- Preroll marker is **scheduled** for a specific time
- Ad break starts at scheduled time + preroll delay
- Used for: Scheduled programming, pre-recorded content

**Example:**
```
Scheduled: 14:30:00 (2:30 PM)
Preroll: 4 seconds
Ad break starts: 14:30:04
```

---

## Preroll Sequence in Your Application

### What Gets Generated:

When you generate a **Preroll Sequence**, your application creates:

1. **CUE-OUT Marker** (Event ID: e.g., 10023)
   - Signals: "Ad break starting"
   - Includes: Preroll delay (4 seconds)
   - Includes: Ad duration (e.g., 600 seconds = 10 minutes)

2. **CUE-IN Marker** (Event ID: e.g., 10024)
   - Signals: "Return to content"
   - Sequential Event ID (10023 + 1)

3. **CUE-CRASH Marker** (Event ID: e.g., 10025) - Optional
   - Emergency return to content
   - Used if something goes wrong

### Event ID Sequence:

```
Preroll Sequence:
  CUE-OUT:  Event ID = 10023
  CUE-IN:   Event ID = 10024  (10023 + 1)
  CUE-CRASH: Event ID = 10025 (10024 + 1) - Optional
```

---

## How to Generate Preroll Markers

### In Your Application:

1. **Go to SCTE-35 Tab**
   - Click on "🎬 SCTE-35" tab in the application

2. **Select Preroll Type**
   - Choose "PREROLL" from the cue type dropdown

3. **Set Preroll Duration**
   - **Preroll Seconds**: 4 (minimum, industry standard)
   - Can be 4-10 seconds

4. **Set Ad Duration**
   - **Ad Duration**: How long the ad break will last
   - Example: 600 seconds = 10 minutes

5. **Generate**
   - Click "Generate Marker" or "Generate Preroll Sequence"
   - System creates CUE-OUT and CUE-IN with sequential Event IDs

---

## What Your Distributor Receives

### Preroll Marker XML:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<tsduck>
    <splice_information_table protocol_version="0" pts_adjustment="0" tier="0xFFF">
        <splice_insert splice_event_id="10023" 
                      splice_event_cancel="false" 
                      out_of_network="true" 
                      splice_immediate="false" 
                      pts_time="360000" 
                      unique_program_id="1" 
                      avail_num="1" 
                      avails_expected="1">
            <break_duration auto_return="true" duration="54000000" />
        </splice_insert>
    </splice_information_table>
</tsduck>
```

**Key Elements:**
- `splice_event_id="10023"` - Unique Event ID
- `pts_time="360000"` - When ad break starts (4 seconds = 360000 PTS units)
- `duration="54000000"` - Ad break duration (600 seconds = 10 minutes)
- `out_of_network="true"` - This is an ad break (out of main content)

---

## Preroll vs Other Marker Types

### Comparison:

| Marker Type | Purpose | When Used |
|-------------|---------|-----------|
| **PREROLL** | Ad break BEFORE content | Start of stream, before program |
| **CUE-OUT** | Start ad break | During content, mid-program |
| **CUE-IN** | End ad break | Return to content |
| **CUE-CRASH** | Emergency return | If something goes wrong |

### When to Use Preroll:

✅ **Use Preroll When:**
- Starting a new stream
- Beginning of a program
- Before main content starts
- Need advanced warning for ad insertion

❌ **Don't Use Preroll When:**
- Mid-program ad breaks (use CUE-OUT/CUE-IN)
- Emergency situations (use CUE-CRASH)
- Already in ad break

---

## Real-World Example

### Scenario: Starting a Live Stream

**Step 1: Stream Starts**
```
00:00:00 → Stream begins
00:00:00 → Main content playing
```

**Step 2: Send Preroll Marker**
```
00:00:05 → Preroll marker sent (Event ID: 10023)
           "Ad break coming in 4 seconds!"
           Preroll: 4 seconds
           Ad duration: 30 seconds
```

**Step 3: Ad Break Starts**
```
00:00:09 → CUE-OUT marker (Event ID: 10023)
           Ad break begins
           [Ad 1] [Ad 2] [Ad 3]
```

**Step 4: Return to Content**
```
00:00:39 → CUE-IN marker (Event ID: 10024)
           Return to main content
           Main program resumes
```

---

## Technical Details

### Preroll Calculation:

**PTS (Presentation Time Stamp) Units:**
- 1 second = 90,000 PTS units
- Preroll 4 seconds = 4 × 90,000 = 360,000 PTS units

**In the XML:**
```xml
pts_time="360000"  <!-- 4 seconds preroll -->
```

### Preroll Timing:

**Immediate Mode:**
- `splice_immediate="true"`
- Ad break starts immediately after preroll delay
- No `pts_time` attribute (not allowed with immediate)

**Scheduled Mode:**
- `splice_immediate="false"`
- `pts_time` specifies exact time
- Ad break starts at scheduled time + preroll delay

---

## Common Questions

### Q: Why 4 seconds minimum?

**A:** Industry standard (SCTE-35) requires minimum 4.0 seconds to:
- Give ad server time to prepare
- Ensure smooth transition
- Prevent content cutoff

### Q: Can I use more than 4 seconds?

**A:** Yes! You can use 4-10 seconds:
- 4 seconds: Minimum (standard)
- 6-8 seconds: Recommended for live streams
- 10 seconds: Maximum (usually)

### Q: What if I don't use preroll?

**A:** Without preroll:
- ❌ Sudden ad breaks (no warning)
- ❌ Content might be cut off
- ❌ Ad server might not be ready
- ❌ Poor user experience

### Q: Do I need preroll for every ad break?

**A:** No! Preroll is mainly for:
- ✅ Start of stream
- ✅ Beginning of program
- ✅ First ad break

For mid-program ad breaks, use CUE-OUT/CUE-IN pairs.

---

## Best Practices

### ✅ DO:

1. **Use 4+ Seconds Preroll**
   - Minimum 4 seconds (industry standard)
   - 6-8 seconds recommended for live streams

2. **Generate Preroll Sequence**
   - Use "Generate Preroll Sequence" button
   - Automatically creates CUE-OUT and CUE-IN with sequential IDs

3. **Set Appropriate Ad Duration**
   - Match actual ad break length
   - Common: 30 seconds, 60 seconds, 120 seconds

4. **Use Incremental Event IDs**
   - Enable "Auto Increment"
   - Ensures sequential Event IDs

### ❌ DON'T:

1. **Don't Use Less Than 4 Seconds**
   - Violates industry standard
   - May cause issues with distributor

2. **Don't Skip Preroll for First Ad**
   - Always use preroll for stream start
   - Ensures smooth beginning

3. **Don't Use Random Event IDs**
   - Use auto increment
   - Keep IDs sequential

---

## Summary

**Preroll Marker = Warning Signal Before Ad Break**

**Key Points:**
- ✅ Signals ad break **before** it starts
- ✅ **4 seconds minimum** (industry standard)
- ✅ Gives distributor **time to prepare**
- ✅ Ensures **smooth transition**
- ✅ Used at **start of stream/program**

**What Your Distributor Needs:**
- ✅ Preroll marker with **4+ seconds** warning
- ✅ **Sequential Event IDs** (incremental)
- ✅ Proper **ad duration** specified
- ✅ **CUE-OUT** and **CUE-IN** pair

**Your Application:**
- ✅ Already supports preroll markers
- ✅ Generates preroll sequences automatically
- ✅ Uses incremental Event IDs
- ✅ Follows industry standards

---

## Quick Reference

| Element | Value | Description |
|---------|-------|-------------|
| **Preroll Type** | PREROLL | Ad break before content |
| **Preroll Seconds** | 4-10 | Warning time (4 = minimum) |
| **Ad Duration** | 30-600+ | How long ad break lasts |
| **Event ID** | Incremental | Sequential (10023, 10024...) |
| **Markers** | CUE-OUT + CUE-IN | Pair with sequential IDs |

---

**Your distributor needs preroll markers to properly prepare for ad breaks!** Use the "Generate Preroll Sequence" button in your application. 🎯

