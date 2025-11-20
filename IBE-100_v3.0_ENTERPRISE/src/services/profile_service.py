"""
Profile Management Service
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from ..core.logger import get_logger
from ..models.profile import Profile
from ..models.stream_config import StreamConfig, InputType, OutputType
from ..utils.profile_config_manager import ProfileConfigManager


class ProfileService:
    """Service for managing configuration profiles"""
    
    def __init__(self, profiles_dir: Path = None):
        self.logger = get_logger("ProfileService")
        self.profiles_dir = profiles_dir or Path("profiles")
        self.profiles_dir.mkdir(exist_ok=True)
        self.profiles_file = self.profiles_dir / "profiles.json"
        self._profiles: dict[str, Profile] = {}
        # Profile-specific config manager for Telegram and other settings
        self.config_manager = ProfileConfigManager(self.profiles_dir)
        self.load_profiles()
        self.logger.info(f"Profile service initialized with {len(self._profiles)} profiles")
    
    def load_profiles(self):
        """Load profiles from disk"""
        if self.profiles_file.exists():
            try:
                with open(self.profiles_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self._profiles = {}
                for name, profile_data in data.items():
                    try:
                        profile = Profile.from_dict(profile_data)
                        # Load profile-specific settings (Telegram, etc.)
                        profile_settings = self.config_manager.load_profile_settings(name)
                        if profile_settings:
                            # Update profile with profile-specific settings
                            if 'telegram_bot_token' in profile_settings:
                                profile.telegram_bot_token = profile_settings['telegram_bot_token']
                            if 'telegram_chat_id' in profile_settings:
                                profile.telegram_chat_id = profile_settings['telegram_chat_id']
                            if 'telegram_enabled' in profile_settings:
                                profile.telegram_enabled = profile_settings['telegram_enabled']
                            if 'telegram_notify_scte35' in profile_settings:
                                profile.telegram_notify_scte35 = profile_settings['telegram_notify_scte35']
                            if 'telegram_notify_errors' in profile_settings:
                                profile.telegram_notify_errors = profile_settings['telegram_notify_errors']
                        self._profiles[name] = profile
                    except Exception as e:
                        self.logger.error(f"Failed to load profile {name}: {e}")
                
                self.logger.info(f"Loaded {len(self._profiles)} profiles")
            except Exception as e:
                self.logger.error(f"Failed to load profiles: {e}")
                self._profiles = {}
        else:
            self._create_default_profiles()
    
    def _create_default_profiles(self):
        """Create default profile templates"""
        defaults = {
            "Distributor_SRT": Profile(
                name="Distributor SRT",
                description="Standard distributor SRT output",
                config=StreamConfig(
                    input_type=InputType.HLS,
                    input_url="https://cdn.example.com/stream/index.m3u8",
                    output_type=OutputType.SRT,
                    output_srt="server.com:9045",
                    stream_id="#!::r=scte/scte,m=publish",
                    latency=2000
                )
            ),
            "HLS_Output": Profile(
                name="HLS Output",
                description="HLS streaming with CORS",
                config=StreamConfig(
                    input_type=InputType.SRT,
                    input_url="srt://source:8088",
                    output_type=OutputType.HLS,
                    output_hls="output/hls",
                    enable_cors=True
                )
            )
        }
        
        self._profiles.update(defaults)
        self.save_profiles()
    
    def save_profiles(self):
        """Save profiles to disk"""
        try:
            data = {name: profile.to_dict() for name, profile in self._profiles.items()}
            with open(self.profiles_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Saved {len(self._profiles)} profiles")
        except Exception as e:
            self.logger.error(f"Failed to save profiles: {e}")
    
    def get_profile_names(self) -> List[str]:
        """Get list of profile names"""
        return list(self._profiles.keys())
    
    def get_profile(self, name: str) -> Optional[Profile]:
        """Get profile by name"""
        return self._profiles.get(name)
    
    def save_profile(self, profile: Profile) -> bool:
        """Save or update a profile"""
        try:
            self._profiles[profile.name] = profile
            profile.modified = datetime.now()
            self.save_profiles()
            
            # Save profile-specific settings (Telegram, etc.) separately
            profile_settings = {
                'telegram_bot_token': profile.telegram_bot_token,
                'telegram_chat_id': profile.telegram_chat_id,
                'telegram_enabled': profile.telegram_enabled,
                'telegram_notify_scte35': profile.telegram_notify_scte35,
                'telegram_notify_errors': profile.telegram_notify_errors
            }
            self.config_manager.save_profile_settings(profile.name, profile_settings)
            
            self.logger.info(f"Saved profile: {profile.name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save profile: {e}")
            return False
    
    def save_telegram_settings(
        self,
        profile_name: str,
        bot_token: str,
        chat_id: str,
        enabled: bool = True,
        notify_scte35: bool = True,
        notify_errors: bool = True
    ) -> bool:
        """
        Save Telegram settings for a profile
        
        Args:
            profile_name: Name of the profile
            bot_token: Telegram bot token
            chat_id: Telegram chat ID
            enabled: Whether Telegram is enabled
            notify_scte35: Notify on SCTE-35 events
            notify_errors: Notify on errors
        
        Returns:
            True if saved successfully
        """
        try:
            # Update profile if it exists
            profile = self.get_profile(profile_name)
            if profile:
                profile.telegram_bot_token = bot_token
                profile.telegram_chat_id = chat_id
                profile.telegram_enabled = enabled
                profile.telegram_notify_scte35 = notify_scte35
                profile.telegram_notify_errors = notify_errors
                profile.modified = datetime.now()
                self.save_profiles()
            
            # Save to profile-specific config file
            self.config_manager.save_telegram_settings(
                profile_name, bot_token, chat_id, enabled, notify_scte35, notify_errors
            )
            
            self.logger.info(f"Saved Telegram settings for profile: {profile_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save Telegram settings: {e}")
            return False
    
    def get_telegram_settings(self, profile_name: str) -> dict:
        """
        Get Telegram settings for a profile
        
        Args:
            profile_name: Name of the profile
        
        Returns:
            Dictionary with Telegram settings
        """
        return self.config_manager.get_telegram_settings(profile_name)
    
    def delete_profile(self, name: str) -> bool:
        """Delete a profile"""
        if name in self._profiles:
            del self._profiles[name]
            self.save_profiles()
            self.logger.info(f"Deleted profile: {name}")
            return True
        return False

