"""
Profile-specific configuration manager
Handles encryption and storage of profile-specific settings (Telegram, etc.)
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from cryptography.fernet import Fernet
from ..core.logger import get_logger


class ProfileConfigManager:
    """Manages profile-specific configuration with encryption"""
    
    def __init__(self, profiles_dir: Path = None):
        """
        Initialize profile config manager
        
        Args:
            profiles_dir: Directory where profiles are stored
        """
        self.logger = get_logger("ProfileConfigManager")
        self.profiles_dir = profiles_dir or Path("profiles")
        self.profiles_dir.mkdir(exist_ok=True)
        
        # Load or generate encryption key (shared across profiles)
        self._key: Optional[bytes] = None
        self._cipher: Optional[Fernet] = None
        self._load_encryption_key()
    
    def _load_encryption_key(self):
        """Load or generate encryption key"""
        key_file = self.profiles_dir / ".encryption_key"
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                self._key = f.read()
        else:
            # Generate new key
            self._key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(self._key)
            # Set restrictive permissions (Unix-like)
            if hasattr(os, 'chmod'):
                os.chmod(key_file, 0o600)
        
        self._cipher = Fernet(self._key)
    
    def encrypt(self, value: str) -> str:
        """Encrypt a string value"""
        if not value:
            return ""
        return self._cipher.encrypt(value.encode()).decode()
    
    def decrypt(self, encrypted: str) -> str:
        """Decrypt a string value"""
        if not encrypted:
            return ""
        try:
            return self._cipher.decrypt(encrypted.encode()).decode()
        except Exception:
            return ""
    
    def get_profile_config_path(self, profile_name: str) -> Path:
        """Get configuration file path for a profile"""
        # Sanitize profile name for filesystem
        safe_name = "".join(c for c in profile_name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_name = safe_name.replace(' ', '_')
        return self.profiles_dir / f"{safe_name}_config.json"
    
    def load_profile_settings(self, profile_name: str) -> Dict[str, Any]:
        """
        Load profile-specific settings
        
        Args:
            profile_name: Name of the profile
        
        Returns:
            Dictionary of profile settings
        """
        config_path = self.get_profile_config_path(profile_name)
        
        if not config_path.exists():
            return {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Decrypt sensitive fields
            if 'telegram_bot_token' in data and data['telegram_bot_token']:
                data['telegram_bot_token'] = self.decrypt(data['telegram_bot_token'])
            
            return data
        except Exception as e:
            self.logger.error(f"Failed to load profile config for {profile_name}: {e}")
            return {}
    
    def save_profile_settings(self, profile_name: str, settings: Dict[str, Any]):
        """
        Save profile-specific settings
        
        Args:
            profile_name: Name of the profile
            settings: Dictionary of settings to save
        """
        config_path = self.get_profile_config_path(profile_name)
        
        try:
            # Encrypt sensitive fields
            data = settings.copy()
            if 'telegram_bot_token' in data and data['telegram_bot_token']:
                data['telegram_bot_token'] = self.encrypt(data['telegram_bot_token'])
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved profile-specific settings for: {profile_name}")
        except Exception as e:
            self.logger.error(f"Failed to save profile config for {profile_name}: {e}")
    
    def save_telegram_settings(
        self,
        profile_name: str,
        bot_token: str,
        chat_id: str,
        enabled: bool = True,
        notify_scte35: bool = True,
        notify_errors: bool = True
    ):
        """
        Save Telegram settings for a profile
        
        Args:
            profile_name: Name of the profile
            bot_token: Telegram bot token
            chat_id: Telegram chat ID
            enabled: Whether Telegram is enabled
            notify_scte35: Notify on SCTE-35 events
            notify_errors: Notify on errors
        """
        settings = {
            'telegram_bot_token': bot_token,
            'telegram_chat_id': chat_id,
            'telegram_enabled': enabled,
            'telegram_notify_scte35': notify_scte35,
            'telegram_notify_errors': notify_errors
        }
        self.save_profile_settings(profile_name, settings)
    
    def get_telegram_settings(self, profile_name: str) -> Dict[str, Any]:
        """
        Get Telegram settings for a profile
        
        Args:
            profile_name: Name of the profile
        
        Returns:
            Dictionary with Telegram settings
        """
        settings = self.load_profile_settings(profile_name)
        return {
            'telegram_bot_token': settings.get('telegram_bot_token', ''),
            'telegram_chat_id': settings.get('telegram_chat_id', ''),
            'telegram_enabled': settings.get('telegram_enabled', False),
            'telegram_notify_scte35': settings.get('telegram_notify_scte35', True),
            'telegram_notify_errors': settings.get('telegram_notify_errors', True)
        }
    
    def delete_profile_config(self, profile_name: str):
        """Delete profile-specific configuration"""
        config_path = self.get_profile_config_path(profile_name)
        if config_path.exists():
            try:
                config_path.unlink()
                self.logger.info(f"Deleted profile config for: {profile_name}")
            except Exception as e:
                self.logger.error(f"Failed to delete profile config for {profile_name}: {e}")

