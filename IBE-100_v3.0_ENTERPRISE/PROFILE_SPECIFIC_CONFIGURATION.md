# Profile-Specific Configuration

## Overview

The application now supports **profile-specific configuration** for settings like Telegram bot credentials. This allows multiple instances of the application to run with different profiles, each having its own Telegram bot token, chat ID, and notification preferences.

## Features

### ✅ Profile-Specific Telegram Settings
- Each profile can have its own Telegram bot token and chat ID
- Settings are encrypted and stored separately per profile
- Automatically loaded when a profile is selected
- Automatically saved when Telegram settings are configured

### ✅ Secure Storage
- Telegram bot tokens are encrypted using Fernet (symmetric encryption)
- Each profile has its own encrypted configuration file: `profiles/{profile_name}_config.json`
- Encryption key is stored securely in `profiles/.encryption_key`

### ✅ Automatic Profile Switching
- When a profile is loaded, its Telegram settings are automatically applied
- SCTE-35 marker directory is also profile-specific (as implemented previously)
- All profile-specific settings are isolated per profile

## File Structure

```
profiles/
├── profiles.json                    # Profile definitions (stream configs)
├── .encryption_key                  # Shared encryption key
├── Profile1_config.json            # Profile1-specific settings (encrypted)
├── Profile2_config.json            # Profile2-specific settings (encrypted)
└── ...
```

## Usage

### Saving Telegram Settings

1. **Load a Profile**: Select or load a profile from the Configuration tab
2. **Configure Telegram**: 
   - Go to **📺 Monitoring** tab
   - Click on **🎬 SCTE-35 Monitor** sub-tab
   - Scroll to **📱 Telegram Notifications** section
   - Enter Bot Token and Chat ID
   - Click **💾 Save Configuration**
3. **Settings Saved**: Settings are automatically saved to the current profile

### Loading Telegram Settings

1. **Load a Profile**: When you load a profile from the Configuration tab
2. **Automatic Load**: Telegram settings are automatically loaded and applied
3. **UI Updated**: The Telegram configuration fields are populated with the profile's settings

## Implementation Details

### Profile Model Extension

The `Profile` model now includes Telegram settings:

```python
@dataclass
class Profile:
    name: str
    description: str = ""
    config: Optional[StreamConfig] = None
    # Profile-specific settings
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    telegram_enabled: bool = False
    telegram_notify_scte35: bool = True
    telegram_notify_errors: bool = True
```

### ProfileConfigManager

New utility class for managing profile-specific configuration:

- `load_profile_settings(profile_name)` - Load settings for a profile
- `save_profile_settings(profile_name, settings)` - Save settings for a profile
- `save_telegram_settings(...)` - Convenience method for Telegram settings
- `get_telegram_settings(profile_name)` - Get Telegram settings for a profile

### ProfileService Updates

- `save_telegram_settings(...)` - Save Telegram settings to a profile
- `get_telegram_settings(profile_name)` - Get Telegram settings from a profile
- Automatically loads profile-specific settings when profiles are loaded

## Multi-Instance Support

### Scenario: Multiple Application Instances

1. **Instance 1**: Profile "Distributor_A"
   - Telegram Bot Token: `123456789:ABC...`
   - Chat ID: `111111111`
   - SCTE-35 Directory: `scte35_final/Distributor_A/`

2. **Instance 2**: Profile "Distributor_B"
   - Telegram Bot Token: `987654321:XYZ...`
   - Chat ID: `222222222`
   - SCTE-35 Directory: `scte35_final/Distributor_B/`

Each instance operates independently with its own configuration.

## Migration Notes

### Backward Compatibility

- Existing profiles without Telegram settings will work normally
- Default values are used if profile-specific settings are not found
- Global configuration (`config/app_config.json`) is still used for application-wide settings

### Migration Path

1. **Existing Profiles**: Continue to work with global Telegram settings
2. **New Profiles**: Automatically use profile-specific settings when configured
3. **Gradual Migration**: You can migrate profiles one by one by configuring Telegram settings per profile

## Security

- **Encryption**: All sensitive data (bot tokens) are encrypted at rest
- **Key Management**: Encryption key is stored separately from configuration files
- **File Permissions**: On Unix-like systems, encryption key has restrictive permissions (600)

## API

### ProfileService Methods

```python
# Save Telegram settings for a profile
profile_service.save_telegram_settings(
    profile_name="MyProfile",
    bot_token="123456789:ABC...",
    chat_id="111111111",
    enabled=True,
    notify_scte35=True,
    notify_errors=True
)

# Get Telegram settings for a profile
settings = profile_service.get_telegram_settings("MyProfile")
# Returns: {
#     'telegram_bot_token': '...',
#     'telegram_chat_id': '...',
#     'telegram_enabled': True,
#     'telegram_notify_scte35': True,
#     'telegram_notify_errors': True
# }
```

## Troubleshooting

### Settings Not Loading

1. **Check Profile Name**: Ensure the profile name matches exactly
2. **Check File Exists**: Verify `profiles/{profile_name}_config.json` exists
3. **Check Permissions**: Ensure the application has read/write access to the profiles directory

### Settings Not Saving

1. **Check Profile Loaded**: Ensure a profile is loaded before saving
2. **Check Permissions**: Ensure the application has write access to the profiles directory
3. **Check Logs**: Review application logs for error messages

### Encryption Issues

1. **Key File**: Ensure `profiles/.encryption_key` exists and is readable
2. **Permissions**: On Unix-like systems, ensure key file has 600 permissions
3. **Regeneration**: If key is corrupted, delete it and let the application regenerate it

## Future Enhancements

Potential additions for profile-specific configuration:

- API settings per profile
- Database paths per profile
- Logging configuration per profile
- Custom notification rules per profile
- Profile-specific EPG settings

