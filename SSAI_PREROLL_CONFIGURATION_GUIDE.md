# 🎯 Preroll Markers for SSAI Distributors - Complete Guide

## 📋 **Understanding SSAI (Server-Side Ad Insertion)**

### **What is SSAI?**

SSAI (Server-Side Ad Insertion) is a technology that allows distributors to:
- ✅ Insert ads **per-viewer** (different ads for different viewers)
- ✅ Insert ads **dynamically** when viewers connect
- ✅ Personalize ad content based on viewer demographics
- ✅ Insert ads **server-side** (before content reaches the viewer)

### **How SSAI Works with SCTE-35 Markers**

There are **two main approaches** SSAI systems use:

---

## 🔄 **Approach 1: SSAI with Stream Markers (Most Common)**

### **How It Works:**

```
Your Stream (with markers) → SSAI System → Per-Viewer Streams (with personalized ads)
```

**Process:**
1. You inject SCTE-35 markers into your stream
2. SSAI system detects markers in the stream
3. When a viewer connects, SSAI system:
   - Reads the marker from your stream
   - Inserts personalized ads for that viewer
   - Creates a unique stream for that viewer

### **What You Need to Do:**

✅ **Still inject markers continuously** (like normal distributors)
✅ **Use standard preroll markers** (SCTE-35 format)
✅ **Inject markers periodically** (every 30-300 seconds)

### **Configuration:**

```python
# Standard configuration for SSAI distributors
inject_interval: 60000  # Every 60 seconds (standard)
start_delay: 2000      # 2-second delay
# Dynamic generation: Enabled (continuous)
```

### **Why Continuous Injection is Still Needed:**

- SSAI systems need **recent markers** in the stream
- When a viewer connects, SSAI looks for markers in the **recent stream**
- If no recent markers exist, SSAI can't insert preroll ads
- Continuous injection ensures markers are always available

### **Example Timeline:**

```
00:00:00 → Stream starts
00:00:02 → Marker 1 injected (Event ID: 10025)
00:01:02 → Marker 2 injected (Event ID: 10026)
00:02:02 → Marker 3 injected (Event ID: 10027)
...
Viewer A connects at 00:01:30
  → SSAI detects Marker 2 (recent)
  → SSAI inserts personalized ads for Viewer A
  → Viewer A sees: [Personalized Ads] → [Content]

Viewer B connects at 00:02:45
  → SSAI detects Marker 3 (recent)
  → SSAI inserts different ads for Viewer B
  → Viewer B sees: [Different Ads] → [Content]
```

---

## 🔄 **Approach 2: SSAI with Dynamic Per-Viewer Insertion (Less Common)**

### **How It Works:**

```
Your Stream (no markers needed) → SSAI System → Per-Viewer Streams (with preroll)
```

**Process:**
1. You send stream **without markers**
2. SSAI system detects when viewer connects
3. SSAI system **dynamically inserts** preroll marker for that viewer
4. Viewer sees preroll ads immediately

### **What You Need to Do:**

❌ **No markers needed** in your stream
✅ **Just send clean stream** (no SCTE-35 injection)
✅ **SSAI handles everything** automatically

### **Configuration:**

```python
# No marker injection needed
marker: None  # Don't inject any markers
```

### **When This Approach is Used:**

- Advanced SSAI systems (like Nimble Advertizer)
- Systems with full SSAI framework
- Distributors with custom SSAI implementation

---

## 🎯 **Which Approach Does Your Distributor Use?**

### **How to Find Out:**

**Ask your distributor these questions:**

1. **"Do you need SCTE-35 markers in the source stream?"**
   - ✅ **Yes** → Use Approach 1 (continuous injection)
   - ❌ **No** → Use Approach 2 (no markers needed)

2. **"How do you handle preroll ads?"**
   - **"We read markers from your stream"** → Approach 1
   - **"We insert preroll automatically"** → Approach 2

3. **"What marker interval do you expect?"**
   - **"Every 30-300 seconds"** → Approach 1 (continuous injection)
   - **"We don't need markers"** → Approach 2

---

## ✅ **Recommended Configuration for SSAI Distributors**

### **Most Common Setup (Approach 1):**

```python
# Configuration for SSAI distributors (most common)
inject_interval: 60000   # Every 60 seconds (standard)
start_delay: 2000        # 2-second delay
preroll_seconds: 4       # Standard 4-second preroll
ad_duration_seconds: 600  # 10 minutes (adjust as needed)

# Dynamic generation: Enabled (automatic)
# Event IDs: Auto-incrementing (10025, 10026, 10027...)
```

### **Why This Configuration:**

1. **60-second interval**: Standard for most SSAI systems
   - Ensures recent markers are always available
   - Not too frequent (reduces overhead)
   - Not too sparse (ensures availability)

2. **4-second preroll**: Industry standard
   - Gives SSAI system time to prepare
   - Allows for smooth ad insertion
   - Compliant with SCTE-35 standard

3. **Continuous injection**: Essential for SSAI
   - Viewers can connect at any time
   - SSAI needs recent markers
   - Ensures 24/7 coverage

---

## 📊 **How SSAI Uses Your Markers**

### **Scenario: Viewer Connects**

```
Timeline:
00:00:00 → Stream starts
00:00:02 → Marker 1 (Event ID: 10025) injected
00:01:02 → Marker 2 (Event ID: 10026) injected
00:02:02 → Marker 3 (Event ID: 10027) injected

Viewer connects at 00:01:30:
  ↓
SSAI System:
  1. Detects viewer connection
  2. Looks for recent markers in stream
  3. Finds Marker 2 (Event ID: 10026) at 00:01:02
  4. Reads marker information:
     - Preroll: 4 seconds
     - Ad duration: 600 seconds
     - Event ID: 10026
  5. Contacts ad server with viewer info:
     - Viewer demographics
     - Viewer location
     - Viewer preferences
  6. Ad server returns personalized ads
  7. SSAI inserts ads into viewer's stream:
     - [Personalized Preroll Ads] → [Main Content]
  8. Viewer sees personalized ads
```

### **Key Points:**

- ✅ **SSAI reads markers from your stream**
- ✅ **SSAI uses markers to trigger ad insertion**
- ✅ **SSAI personalizes ads per viewer**
- ✅ **Each viewer gets different ads** (based on demographics)
- ✅ **Markers are still needed** (to trigger insertion)

---

## 🔧 **Configuration Options**

### **Option 1: Standard Configuration (Recommended)**

```python
# For most SSAI distributors
inject_interval: 60000   # Every 60 seconds
start_delay: 2000        # 2 seconds
preroll_seconds: 4       # 4 seconds
ad_duration_seconds: 600 # 10 minutes
```

**Use this if:**
- Distributor says "we need markers in your stream"
- Distributor says "inject markers every 60 seconds"
- Distributor says "we use SSAI with stream markers"

### **Option 2: More Frequent (High Traffic)**

```python
# For high-traffic SSAI systems
inject_interval: 30000   # Every 30 seconds
start_delay: 2000       # 2 seconds
preroll_seconds: 4      # 4 seconds
ad_duration_seconds: 600 # 10 minutes
```

**Use this if:**
- Distributor has high viewer traffic
- Distributor wants more frequent markers
- Distributor says "inject markers every 30 seconds"

### **Option 3: Less Frequent (Scheduled Programming)**

```python
# For scheduled programming
inject_interval: 300000  # Every 5 minutes
start_delay: 2000       # 2 seconds
preroll_seconds: 4     # 4 seconds
ad_duration_seconds: 600 # 10 minutes
```

**Use this if:**
- Distributor has scheduled ad breaks
- Distributor wants markers at specific intervals
- Distributor says "inject markers every 5 minutes"

### **Option 4: No Markers (Advanced SSAI)**

```python
# For advanced SSAI systems
marker: None  # No markers needed
```

**Use this if:**
- Distributor says "we don't need markers"
- Distributor says "we handle preroll automatically"
- Distributor has full SSAI framework (like Nimble Advertizer)

---

## 🧪 **Testing with SSAI Distributors**

### **Step 1: Verify Marker Reception**

Ask your distributor to check:
- ✅ Can they see SCTE-35 markers in your stream?
- ✅ Are markers being received correctly?
- ✅ Are event IDs incrementing?

### **Step 2: Test Per-Viewer Ads**

Have multiple viewers connect:
- ✅ Viewer A: Should see personalized ads
- ✅ Viewer B: Should see different ads
- ✅ Both should see preroll ads

### **Step 3: Verify Timing**

Check with distributor:
- ✅ Are preroll ads appearing at correct time?
- ✅ Is the 4-second preroll working?
- ✅ Are ads transitioning smoothly?

---

## 📝 **Summary**

### **For SSAI Distributors (Most Common):**

✅ **Still inject markers continuously** (every 60 seconds)
✅ **Use standard preroll markers** (4-second preroll)
✅ **Ensure recent markers are always available**
✅ **Let SSAI system personalize ads per viewer**

### **Configuration:**

```python
inject_interval: 60000   # Every 60 seconds (standard)
start_delay: 2000        # 2-second delay
preroll_seconds: 4       # 4-second preroll
ad_duration_seconds: 600 # 10 minutes
```

### **How It Works:**

1. You inject markers continuously into stream
2. SSAI system reads markers from your stream
3. When viewer connects, SSAI:
   - Detects recent marker
   - Contacts ad server with viewer info
   - Inserts personalized ads for that viewer
4. Viewer sees personalized preroll ads

### **Key Insight:**

**SSAI personalizes ads, but still needs markers in your stream to trigger insertion!**

---

## 🎯 **Next Steps**

1. **Ask your distributor:**
   - "Do you need SCTE-35 markers in my stream?"
   - "What marker interval do you expect?"
   - "How do you handle preroll ads?"

2. **Configure based on their answer:**
   - If they need markers → Use continuous injection (60-second interval)
   - If they don't need markers → Disable marker injection

3. **Test and verify:**
   - Check marker reception
   - Test per-viewer ads
   - Verify timing

---

**Your current implementation (continuous injection with dynamic generation) is perfect for SSAI distributors!** ✅

