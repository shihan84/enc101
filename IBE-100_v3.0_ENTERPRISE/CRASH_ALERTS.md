# 🚨 Crash Detection and Alerts

## Overview

The application now includes comprehensive crash detection and Telegram alerting for application crashes, unexpected closures, and critical errors. This ensures you're immediately notified when the application encounters issues.

## Features

### ✅ Automatic Crash Detection
- **Uncaught Exceptions**: Catches all uncaught exceptions
- **Thread Exceptions**: Detects crashes in background threads
- **Startup Crashes**: Catches errors during application initialization
- **Unexpected Closures**: Detects when application closes unexpectedly

### ✅ Telegram Alerts
- **Crash Alerts**: Immediate notification with exception details
- **Traceback Information**: Full stack trace for debugging
- **Thread Information**: Identifies which thread crashed
- **Timestamp**: Exact time of crash

### ✅ Crash Logging
- **Crash Logs**: Detailed crash reports saved to `logs/crashes/`
- **Timestamped Files**: Each crash saved with timestamp
- **Full Traceback**: Complete exception information

### ✅ Graceful Shutdown Detection
- **Normal Shutdown**: Distinguishes between crashes and normal shutdown
- **Shutdown Notification**: Optional notification for graceful shutdowns
- **No False Alerts**: Only alerts on actual crashes

## How It Works

### Crash Detection

1. **Global Exception Handler**: Catches all uncaught exceptions
2. **Thread Exception Handler**: Catches exceptions in background threads
3. **Atexit Handler**: Detects unexpected application termination
4. **Signal Handlers**: Handles system signals (SIGINT, SIGTERM)

### Alert Flow

```
Application Crash
    ↓
Crash Handler Detects
    ↓
Log Crash to File
    ↓
Send Telegram Alert
    ↓
Display Error (if possible)
```

## Crash Alert Format

### Crash Alert Message

```
🚨 Application Crash

Exception: ValueError
Message: Invalid input parameter
Thread: Main
Time: 2024-01-15 14:30:45

Traceback:
[Full stack trace here]
```

### Closure Alert

```
⚠️ Application Closed

Time: 2024-01-15 14:30:45
Status: Application terminated
```

### Graceful Shutdown

```
✅ Application Shutdown

Time: 2024-01-15 14:30:45
Status: Graceful shutdown
```

## Configuration

### Enable Telegram Alerts

1. Configure Telegram in the application (see `TELEGRAM_NOTIFICATIONS.md`)
2. Crash alerts are automatically enabled when Telegram is configured
3. No additional configuration needed

### Crash Log Location

Crash logs are saved to:
```
logs/crashes/crash_YYYYMMDD_HHMMSS.log
```

Each crash creates a new log file with timestamp.

## Types of Crashes Detected

### 1. Uncaught Exceptions
- Python exceptions not caught by try/except
- Runtime errors
- Import errors
- Attribute errors

### 2. Thread Exceptions
- Exceptions in background threads
- Worker thread crashes
- Service thread errors

### 3. Startup Crashes
- Errors during initialization
- Service initialization failures
- Configuration errors

### 4. Unexpected Closures
- Application terminated without proper shutdown
- System kills
- Process termination

## What's NOT Considered a Crash

### Normal Shutdown
- User closes application normally
- Application exits with code 0
- Graceful shutdown via menu/button

### Keyboard Interrupt
- Ctrl+C pressed by user
- User-initiated termination

## Alert Reliability

### Guaranteed Delivery
- Alerts sent in separate thread to avoid blocking
- Non-blocking implementation
- Fails gracefully if Telegram unavailable

### Alert Timing
- **Immediate**: Alerts sent as soon as crash detected
- **Non-blocking**: Doesn't delay crash handling
- **Retry-safe**: Handles network failures gracefully

## Crash Log Format

Each crash log contains:

```
================================================================================
CRASH REPORT - 2024-01-15 14:30:45
================================================================================

Exception Type: ValueError
Exception Message: Invalid input parameter
Thread: Main

Traceback:
[Full Python traceback]

================================================================================
```

## Troubleshooting

### No Crash Alerts Received

1. **Check Telegram Configuration**: Verify bot token and chat ID
2. **Test Connection**: Use "Test Connection" in Telegram settings
3. **Check Logs**: Review `logs/crashes/` directory
4. **Verify Internet**: Ensure internet connection is active

### False Crash Alerts

- **Normal Shutdown**: Should not trigger crash alert
- **Keyboard Interrupt**: Should not trigger crash alert
- If false alerts occur, check crash handler logic

### Crash Logs Not Created

1. **Check Permissions**: Ensure write permissions for `logs/` directory
2. **Check Disk Space**: Ensure sufficient disk space
3. **Review Logs**: Check main application logs for errors

## Best Practices

### For Production

1. **Enable Telegram**: Configure Telegram for production monitoring
2. **Monitor Alerts**: Set up alert monitoring/notification system
3. **Review Crash Logs**: Regularly review crash logs for patterns
4. **Update Application**: Keep application updated to fix known issues

### For Development

1. **Review Crash Logs**: Use crash logs for debugging
2. **Test Crash Handling**: Verify alerts work correctly
3. **Monitor False Positives**: Ensure normal shutdowns don't trigger alerts

## Integration

### With Monitoring Systems

Crash alerts can be integrated with:
- **Telegram**: Primary alert channel
- **Log Aggregation**: Crash logs can be collected
- **Monitoring Tools**: Can parse crash logs

### With Error Tracking

- Crash logs compatible with error tracking systems
- Can be parsed for error tracking tools
- Timestamped for correlation

## Security

### Crash Information

- **Sensitive Data**: Crash logs may contain sensitive information
- **Secure Storage**: Store crash logs securely
- **Access Control**: Limit access to crash logs

### Telegram Alerts

- **Traceback**: May contain sensitive information
- **Truncation**: Long tracebacks are truncated
- **Review**: Review alerts before sharing

## Examples

### Example Crash Alert

```
🚨 Application Crash

Exception: ConnectionError
Message: Failed to connect to stream server
Thread: StreamService
Time: 2024-01-15 14:30:45

Traceback:
Traceback (most recent call last):
  File "stream_service.py", line 123, in start_stream
    connection = connect(server)
ConnectionError: Connection refused
```

### Example Startup Crash

```
🚨 Application Crash

Exception: ImportError
Message: No module named 'missing_module'
Thread: Main
Time: 2024-01-15 14:30:45

Traceback:
[Full traceback]
```

## Support

For issues with crash detection:
1. Check crash logs in `logs/crashes/`
2. Review application logs
3. Verify Telegram configuration
4. Test with known error scenarios

---

**Note**: Crash detection requires Telegram to be configured for alerts. Crash logs are always created regardless of Telegram configuration.

