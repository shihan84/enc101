# 📱 Telegram Notifications Guide

## Overview

The Telegram notification feature allows you to receive real-time alerts and notifications about SCTE-35 events, monitoring status, and errors directly in your Telegram chat. This is perfect for production monitoring and remote alerting.

## Features

### ✅ Real-Time SCTE-35 Alerts
- **Event Detection**: Instant notifications when SCTE-35 events are detected
- **Rich Formatting**: HTML-formatted messages with event details
- **Event Types**: Alerts for CUE-OUT, CUE-IN, PREROLL, and TIME_SIGNAL events

### ✅ Monitoring Status Updates
- **Start/Stop Notifications**: Alerts when monitoring starts or stops
- **Status Updates**: Periodic status information
- **Error Alerts**: Critical error notifications

### ✅ Secure Configuration
- **Encrypted Storage**: Bot token is encrypted in configuration
- **Easy Setup**: Simple UI for configuration
- **Connection Testing**: Built-in connection test

## Setup Instructions

### Step 1: Create a Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Follow the instructions to name your bot
4. Copy the **Bot Token** (e.g., `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Get Your Chat ID

**Option A: Using @userinfobot**
1. Search for **@userinfobot** in Telegram
2. Start a conversation
3. The bot will reply with your Chat ID (e.g., `123456789`)

**Option B: Using @getidsbot**
1. Search for **@getidsbot** in Telegram
2. Start a conversation
3. The bot will reply with your Chat ID

**Option C: For Group Chats**
1. Add **@getidsbot** to your group
2. The bot will display the group Chat ID (usually negative number)

### Step 3: Configure in IBE-100

1. Open IBE-100 v3.0 Enterprise
2. Navigate to **📺 Monitoring** tab
3. Click on **🎬 SCTE-35 Monitor** sub-tab
4. Scroll to **📱 Telegram Notifications** section
5. Enter your **Bot Token**
6. Enter your **Chat ID**
7. Click **🔍 Test Connection** to verify
8. Click **💾 Save Config** to save

### Step 4: Enable Notifications

1. Click **🔔 Enable Notifications** button (should be green/enabled by default)
2. Start monitoring to receive alerts

## Notification Types

### SCTE-35 Event Alerts

When an SCTE-35 event is detected, you'll receive a formatted message:

```
🎬 SCTE-35 Event Detected

Type: CUE-OUT
Event ID: 10023
PTS: 9000000 (100.00s)
Duration: 5400000.0s
Status: 🔴 Out of Network

Source: https://example.com/stream.m3u8

Time: 2024-01-15 14:30:45
```

### Monitoring Status

**Start Notification:**
```
🔍 SCTE-35 Monitoring Started

Source: https://example.com/stream.m3u8
SCTE-35 PID: 500

Time: 2024-01-15 14:30:00
```

**Stop Notification:**
```
⏹️ SCTE-35 Monitoring Stopped

Time: 2024-01-15 15:30:00
```

### Error Alerts

```
⚠️ Error Alert

Type: Connection Error
Message: Failed to connect to stream
Source: https://example.com/stream.m3u8

Time: 2024-01-15 14:30:45
```

## Configuration Options

### In Application Config

You can also configure Telegram in the application configuration file:

```json
{
  "telegram_enabled": true,
  "telegram_bot_token": "encrypted_token",
  "telegram_chat_id": "123456789",
  "telegram_notify_scte35": true,
  "telegram_notify_errors": true
}
```

**Note**: The bot token is automatically encrypted when saved.

## Usage

### Enable/Disable Notifications

- **Enable**: Click **🔔 Enable Notifications** (button turns green)
- **Disable**: Click **🔕 Disable Notifications** (button turns gray)

When disabled, no Telegram messages will be sent, but monitoring continues.

### Test Connection

1. Enter bot token and chat ID
2. Click **🔍 Test Connection**
3. If successful:
   - Status shows "✅ Connected"
   - A test message is sent to your Telegram
   - You'll receive: "✅ IBE-100 Enterprise - Telegram notifications are now active!"

### Save Configuration

1. Enter bot token and chat ID
2. Click **💾 Save Config**
3. Configuration is saved and encrypted
4. Status shows "💾 Configuration saved"

## Message Formatting

Telegram messages use HTML formatting:

- **Bold**: `<b>text</b>`
- **Italic**: `<i>text</i>`
- **Emojis**: Automatically included for visual clarity

## Security

### Token Encryption

- Bot tokens are encrypted using Fernet (symmetric encryption)
- Encryption key is stored separately in `.encryption_key` file
- Tokens are never displayed in plain text in the UI (password field)

### Best Practices

1. **Never share your bot token** publicly
2. **Use separate bots** for different environments (dev/prod)
3. **Regularly rotate tokens** if compromised
4. **Use group chats** for team notifications
5. **Set up bot permissions** appropriately

## Troubleshooting

### No Notifications Received

1. **Check Connection**: Click "Test Connection" to verify
2. **Verify Chat ID**: Ensure correct chat ID (user or group)
3. **Check Bot Status**: Ensure bot is active and not blocked
4. **Enable Notifications**: Ensure notifications are enabled in UI
5. **Check Logs**: Review application logs for errors

### Connection Test Fails

1. **Verify Bot Token**: Check token is correct (no extra spaces)
2. **Check Internet**: Ensure internet connection is active
3. **Firewall**: Check if firewall is blocking Telegram API
4. **Bot Status**: Verify bot is not deleted or disabled

### Notifications Stop Working

1. **Re-test Connection**: Use "Test Connection" button
2. **Check Monitoring**: Ensure monitoring is still active
3. **Review Logs**: Check for error messages
4. **Restart Application**: Sometimes helps with connection issues

## API Integration

The Telegram service can also be used programmatically:

```python
from src.services.telegram_service import TelegramService

# Initialize
telegram = TelegramService(bot_token="your_token", chat_id="your_chat_id")

# Send message
telegram.send_message("Hello from IBE-100!")

# Send SCTE-35 alert
telegram.send_scte35_alert(
    event_id=10023,
    cue_type="CUE-OUT",
    pts_time=9000000,
    break_duration=5400000,
    out_of_network=True
)
```

## Rate Limits

Telegram Bot API has rate limits:
- **20 messages per minute** per chat
- **30 messages per second** globally

The service handles rate limits gracefully and logs warnings if limits are exceeded.

## Advanced Features

### Custom Message Templates

You can customize message formats by modifying `telegram_service.py`:

```python
def send_scte35_alert(self, ...):
    # Customize message format here
    message = f"Custom format: {event_id}..."
```

### Multiple Chat IDs

To send to multiple chats, create multiple TelegramService instances:

```python
telegram1 = TelegramService(token, chat_id1)
telegram2 = TelegramService(token, chat_id2)
```

### Group Notifications

Use group chat ID (negative number) for team notifications:

```python
telegram.configure(bot_token, "-123456789")  # Group chat ID
```

## Support

For issues:
1. Check Telegram Bot API status: https://core.telegram.org/bots/api
2. Review application logs
3. Test with @BotFather to verify bot is active
4. Verify chat ID is correct

---

**Note**: Telegram notifications require an active internet connection and valid bot token/chat ID.

