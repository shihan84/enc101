# 📊 Why SCTE-35 Marker Count Shows 0

## ❓ **Question: Why do I see "SCTE-35: 0 markers injected" in metrics?**

## 🔍 **Explanation**

### **Current Implementation**

The `scte35_injected` counter in the stream session metrics shows **0** because:

1. **Counter Initialization**: The counter starts at `0` when a stream session is created
   ```python
   scte35_injected: int = 0  # Default value in StreamSession
   ```

2. **No Tracking Logic**: The counter is **never incremented** anywhere in the code
   - TSDuck handles marker injection internally
   - We pass the marker file to TSDuck, but don't track when injection happens
   - The counter remains at 0 throughout the stream session

3. **Display Only**: The counter is displayed in the UI but never updated
   ```python
   SCTE-35: {session.scte35_injected} markers injected  # Always shows 0
   ```

### **Why It's Not Tracked**

- **TSDuck Internal Process**: TSDuck's `spliceinject` plugin handles injection internally
- **No Output Parsing**: We don't parse TSDuck output to detect successful injections
- **Asynchronous**: Injection happens asynchronously, making it hard to track

## ✅ **Solution: Implement Marker Injection Tracking**

To fix this, we need to:

1. **Parse TSDuck Output**: Look for injection confirmation messages
2. **Detect Injection Events**: Identify when markers are successfully injected
3. **Update Counter**: Increment `scte35_injected` when injection is confirmed

### **How TSDuck Reports Injections**

TSDuck's `spliceinject` plugin may output messages like:
- `"spliceinject: injecting marker from file..."`
- `"spliceinject: marker injected successfully"`
- Or similar confirmation messages

We need to parse these messages and increment the counter.

## 🎯 **Would You Like Me To Implement This?**

I can add:
1. ✅ TSDuck output parsing for injection confirmations
2. ✅ Real-time counter updates
3. ✅ Accurate marker injection tracking

This will show the actual number of markers injected into the stream!

