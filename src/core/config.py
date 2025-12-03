"""
Enterprise Configuration Management
Handles configuration loading, validation, encryption, and hot-reload
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict
from cryptography.fernet import Fernet
import base64


@dataclass
class Config:
    """Application configuration"""
    # Application settings
    app_name: str = "IBE-210 Enterprise"
    app_version: str = "2.3.3"
    log_level: str = "INFO"
    log_dir: str = "logs"
    
    # TSDuck settings
    tsduck_path: str = ""
    tsduck_timeout: int = 30
    
    # Stream defaults
    default_latency: int = 2000
    default_service_id: int = 1
    default_vpid: int = 256
    default_apid: int = 257
    default_scte35_pid: int = 500
    
    # API settings
    api_enabled: bool = False
    api_host: str = "127.0.0.1"
    api_port: int = 8080
    api_key: str = ""
    
    # Database settings
    database_path: str = "database/sessions.db"
    
    # UI settings
    theme: str = "dark"
    window_width: int = 1200
    window_height: int = 800
    
    # Telegram notification settings
    telegram_enabled: bool = False
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    telegram_notify_scte35: bool = True
    telegram_notify_errors: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """Create from dictionary"""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class ConfigManager:
    """Manages application configuration with encryption support"""
    
    def __init__(self, config_path: Path = None):
        self.config_path = config_path or Path("config/app_config.json")
        self.config_path.parent.mkdir(exist_ok=True)
        
        self._key: Optional[bytes] = None
        self._cipher: Optional[Fernet] = None
        self._config: Optional[Config] = None
        
        self._load_encryption_key()
        self.load()
    
    def _load_encryption_key(self):
        """Load or generate encryption key"""
        key_file = self.config_path.parent / ".encryption_key"
        
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
    
    def load(self) -> Config:
        """Load configuration from file"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Decrypt sensitive fields
                if 'api_key' in data and data['api_key']:
                    data['api_key'] = self.decrypt(data['api_key'])
                if 'telegram_bot_token' in data and data['telegram_bot_token']:
                    data['telegram_bot_token'] = self.decrypt(data['telegram_bot_token'])
                
                self._config = Config.from_dict(data)
            except Exception as e:
                print(f"[WARNING] Failed to load config: {e}. Using defaults.")
                self._config = Config()
        else:
            self._config = Config()
            self.save()
        
        return self._config
    
    def save(self, config: Config = None):
        """Save configuration to file"""
        if config:
            self._config = config
        
        if not self._config:
            return
        
        try:
            data = self._config.to_dict()
            
            # Encrypt sensitive fields
            if data.get('api_key'):
                data['api_key'] = self.encrypt(data['api_key'])
            if data.get('telegram_bot_token'):
                data['telegram_bot_token'] = self.encrypt(data['telegram_bot_token'])
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[ERROR] Failed to save config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        if not self._config:
            self.load()
        return getattr(self._config, key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        if not self._config:
            self.load()
        if hasattr(self._config, key):
            setattr(self._config, key, value)
            self.save()
    
    def get_config(self) -> Config:
        """Get full configuration object"""
        if not self._config:
            self.load()
        return self._config
    
    def update(self, updates: Dict[str, Any]):
        """Update multiple configuration values"""
        if not self._config:
            self.load()
        
        for key, value in updates.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
        
        self.save()

