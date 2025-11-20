# 🎬 SCTE-35 Monitoring Guide

## Overview

The SCTE-35 Monitoring feature provides real-time detection and tracking of SCTE-35 events in transport streams using TSDuck's `splicemonitor` plugin. This allows you to monitor ad insertion markers, program transitions, and other SCTE-35 events as they occur in your stream.

## Features

### ✅ Real-Time Event Detection
- **Automatic Detection**: Monitors stream for SCTE-35 splice information
- **Multiple Formats**: Supports JSON and text output from TSDuck
- **Event Parsing**: Extracts event ID, cue type, PTS, duration, and network status

### ✅ Event Tracking
- **Event History**: Maintains history of detected events (up to 1000 events)
- **Statistics**: Real-time statistics including:
  - Total events detected
  - Events per minute
  - Events by type (CUE-OUT, CUE-IN, PREROLL, TIME_SIGNAL)
  - Last event timestamp

### ✅ User Interface
- **Control Panel**: Start/stop monitoring with configurable input source and PID
- **Events Table**: Real-time table showing detected events with:
  - Timestamp
  - Event ID
  - Cue Type
  - PTS (Presentation Time Stamp)
  - Break Duration
  - Network Status (In/Out of Network)
- **Statistics Display**: Live statistics panel
- **Monitor Log**: Real-time log of monitoring activity

## How to Use

### Step 1: Access SCTE-35 Monitor

1. Open IBE-100 v3.0 Enterprise
2. Navigate to the **📺 Monitoring** tab
3. Click on the **🎬 SCTE-35 Monitor** sub-tab

### Step 2: Configure Monitoring

1. **Input Source**: Enter your stream URL or path
   - **HLS**: `https://example.com/stream.m3u8`
   - **SRT**: `srt://server:port?streamid=stream_id`
   - **UDP**: `udp://@239.1.1.1:5000`
   - **File**: `/path/to/stream.ts`

2. **SCTE-35 PID**: Set the PID where SCTE-35 data is located
   - Default: `500`
   - Range: 0-8191

### Step 3: Start Monitoring

1. Click **▶️ Start Monitoring**
2. The monitor will:
   - Start TSDuck with `splicemonitor` plugin
   - Begin analyzing the stream
   - Display detected events in real-time

### Step 4: View Events

- **Events Table**: Shows all detected events with details
- **Statistics**: Updates every 2 seconds with current metrics
- **Log Console**: Displays monitoring activity and event notifications

### Step 5: Stop Monitoring

- Click **⏹️ Stop** to stop monitoring
- Events history is preserved until cleared

### Clear Events

- Click **🗑️ Clear Events** to clear the event history and statistics

## TSDuck Integration

The monitoring uses TSDuck's `splicemonitor` plugin with the following command structure:

```bash
tsp -I <input_plugin> <input_source> \
    -P splicemonitor --pid <scte35_pid> --json \
    -O drop
```

### Supported Input Types

- **HLS**: `-I hls <url>`
- **SRT**: `-I srt <host:port> --transtype live`
- **UDP**: `-I ip <address:port>`
- **HTTP**: `-I http <url>`
- **File**: `-I file <path>`

## Event Types

### CUE-OUT (Ad Break Start)
- Indicates start of ad break
- `out_of_network = true`
- Contains break duration

### CUE-IN (Ad Break End)
- Indicates end of ad break
- `out_of_network = false`
- Returns to main program

### PREROLL (Program Transition)
- Program transition marker
- Used for program boundaries

### TIME_SIGNAL
- Time-based signaling
- Used for scheduled events

## Event Data Structure

Each detected event contains:

```python
SCTE35Event(
    timestamp: datetime,          # Detection time
    event_id: int,                  # SCTE-35 event ID
    cue_type: str,                  # Event type
    splice_command_type: int,       # Command type code
    pts_time: int,                  # Presentation Time Stamp
    break_duration: int,            # Break duration (90kHz units)
    out_of_network: bool,           # Network status
    splice_immediate: bool,         # Immediate splice flag
    raw_data: dict                  # Raw TSDuck output
)
```

## Statistics

The monitor tracks:

- **Total Events**: Total number of events detected since start
- **Events per Minute**: Rate of event detection
- **Events by Type**: Breakdown by cue type
- **Last Event Time**: Timestamp of most recent event

## Troubleshooting

### No Events Detected

1. **Check Input Source**: Verify the stream URL/path is correct
2. **Verify PID**: Ensure SCTE-35 PID matches your stream configuration
3. **Check Stream**: Confirm the stream contains SCTE-35 data
4. **Review Log**: Check the monitor log for errors

### Monitoring Won't Start

1. **TSDuck Installation**: Verify TSDuck is installed and accessible
2. **Input Format**: Ensure input source format is supported
3. **Network Access**: For remote streams, verify network connectivity
4. **Permissions**: Check file permissions for file inputs

### Events Not Parsing Correctly

1. **Stream Format**: Some streams may use non-standard SCTE-35 encoding
2. **PID Mismatch**: Verify the SCTE-35 PID is correct
3. **Check Log**: Review raw output in the log console

## Performance

- **Memory Usage**: Events are limited to 1000 entries (auto-pruned)
- **CPU Usage**: Minimal overhead, monitoring runs in background thread
- **Update Rate**: Statistics update every 2 seconds
- **Event Processing**: Real-time as events are detected

## Integration with Stream Processing

The SCTE-35 monitor can run independently or alongside stream processing:

- **Standalone**: Monitor any stream without processing
- **Concurrent**: Monitor input stream while processing output
- **Post-Processing**: Monitor processed output stream

## API Integration

The monitoring service can be accessed via the REST API:

- **Start Monitoring**: `POST /api/scte35/monitor/start`
- **Stop Monitoring**: `POST /api/scte35/monitor/stop`
- **Get Events**: `GET /api/scte35/monitor/events`
- **Get Statistics**: `GET /api/scte35/monitor/stats`

## Best Practices

1. **Monitor Input Streams**: Monitor source streams to verify SCTE-35 presence
2. **Monitor Output Streams**: Verify injected markers are present
3. **Set Appropriate PID**: Use correct SCTE-35 PID for your stream
4. **Review Statistics**: Regularly check event rates and types
5. **Clear History**: Periodically clear old events to maintain performance

## References

- **TSDuck Documentation**: [tsduck.io](https://tsduck.io)
- **SCTE-35 Standard**: SCTE 35 2021
- **Splicemonitor Plugin**: TSDuck User's Guide Section 5.2.15

## Support

For issues or questions:
1. Check the monitor log for error messages
2. Verify TSDuck installation: `tsp --version`
3. Test with known SCTE-35 streams
4. Review TSDuck documentation for `splicemonitor` plugin

---

**Note**: SCTE-35 monitoring requires TSDuck to be installed and accessible in your system PATH or configured path.

