# 📊 Stream Session Metrics Display

## ⏰ **When Metrics Are Shown**

### **Automatic Display**

Stream session metrics are displayed **automatically** when:

1. ✅ **Stream Starts** - Metrics appear immediately when stream session is created
2. ✅ **Every 3 Seconds** - Status updates automatically via timer
3. ✅ **Real-time Updates** - Metrics update as stream processes packets

### **Display Location**

- **Tab**: Monitoring → **📡 Status** tab
- **Update Frequency**: Every **3 seconds**
- **Real-time**: Yes, metrics update continuously while stream is running

## 📋 **What Metrics Are Shown**

### **Session Information**

- **Session ID**: Unique identifier for the stream session
- **Status**: Current status (STARTING, RUNNING, STOPPED)
- **Start Time**: When the stream started
- **Stop Time**: When the stream stopped (or "Running..." if active)
- **Runtime**: How long the stream has been running

### **Real-Time Statistics**

- **Packets**: Total packets processed (with comma formatting)
- **Packets/sec**: Real-time packets per second calculation
- **Errors**: Number of errors encountered
- **SCTE-35**: Number of SCTE-35 markers injected

## 🔄 **Update Timeline**

### **Immediate (0 seconds)**
```
✅ Stream session created
✅ Status: "STARTING"
✅ Metrics: 0 packets, 0 errors
✅ Display: Shows session info immediately
```

### **After 3 seconds (First Update)**
```
✅ Timer triggers first update
✅ Status: "RUNNING" (if process started)
✅ Metrics: Updated with current values
✅ Runtime: Calculated and displayed
```

### **Every 3 seconds (Continuous)**
```
✅ Automatic updates every 3 seconds
✅ Packets: Increments as packets are processed
✅ Packets/sec: Calculated from runtime
✅ Errors: Updated if errors occur
✅ Runtime: Continuously updated
```

## 📊 **Example Display**

```
═══════════════════════════════════════════════════
          STREAM SESSION STATUS
═══════════════════════════════════════════════════

Session ID:     167b1bef...
Status:         RUNNING

Start Time:     2025-11-18 16:40:18
Stop Time:      Running...
Runtime:        2m 15s

═══════════════════════════════════════════════════
              REAL-TIME METRICS
═══════════════════════════════════════════════════

Statistics:
  Packets:      1,234,567
  Packets/sec: 9,123.4
  Errors:       0
  SCTE-35:      1 markers injected

═══════════════════════════════════════════════════
```

## 🎯 **Key Features**

### **✅ Automatic Updates**
- No manual refresh needed
- Updates every 3 seconds automatically
- Real-time calculation of packets per second

### **✅ Performance Optimized**
- Caching prevents unnecessary UI updates
- Only updates when values change
- Efficient timer-based updates

### **✅ Comprehensive Information**
- Session details
- Runtime tracking
- Real-time statistics
- Error tracking
- SCTE-35 injection count

## 🔍 **How to View Metrics**

1. **Start Stream**: Click "▶️ Start Processing"
2. **Open Monitoring Tab**: Go to "📺 Monitoring" tab
3. **View Status**: Click on "📡 Status" sub-tab
4. **Watch Updates**: Metrics update automatically every 3 seconds

## ⚙️ **Technical Details**

### **Update Mechanism**

- **Timer**: `QTimer` updates every 3000ms (3 seconds)
- **Method**: `_update_stream_status()` called automatically
- **Caching**: Only updates UI when values change (performance optimization)

### **Metrics Calculation**

- **Packets/sec**: `packets_processed / runtime_seconds`
- **Runtime**: Calculated from `start_time` to current time (or `stop_time`)
- **Status**: Retrieved from `session.status` ("starting", "running", "stopped")

### **Data Source**

- **Session**: Retrieved from `stream_service.get_current_session()`
- **Statistics**: From `StreamSession` model:
  - `packets_processed`
  - `errors_count`
  - `scte35_injected`
  - `start_time` / `stop_time`

## ✅ **Summary**

- ✅ **Metrics show immediately** when stream starts
- ✅ **Updates every 3 seconds** automatically
- ✅ **Real-time calculations** for packets/sec and runtime
- ✅ **Comprehensive display** with all session information
- ✅ **Performance optimized** with caching

The metrics are always visible and update automatically - no action required from the user!

