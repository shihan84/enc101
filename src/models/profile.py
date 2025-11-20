"""
Profile model
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from .stream_config import StreamConfig


@dataclass
class Profile:
    """Configuration profile model"""
    name: str
    description: str = ""
    config: Optional[StreamConfig] = None
    created: Optional[datetime] = None
    modified: Optional[datetime] = None
    # Profile-specific settings (for multi-instance support)
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    telegram_enabled: bool = False
    telegram_notify_scte35: bool = True
    telegram_notify_errors: bool = True
    
    def __post_init__(self):
        """Initialize timestamps"""
        if self.created is None:
            self.created = datetime.now()
        if self.modified is None:
            self.modified = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'description': self.description,
            'config': self.config.to_dict() if self.config else None,
            'created': self.created.isoformat() if self.created else None,
            'modified': self.modified.isoformat() if self.modified else None,
            # Profile-specific settings
            'telegram_bot_token': self.telegram_bot_token,
            'telegram_chat_id': self.telegram_chat_id,
            'telegram_enabled': self.telegram_enabled,
            'telegram_notify_scte35': self.telegram_notify_scte35,
            'telegram_notify_errors': self.telegram_notify_errors
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Profile':
        """Create from dictionary"""
        config = None
        if data.get('config'):
            from .stream_config import StreamConfig
            config = StreamConfig.from_dict(data['config'])
        
        created = None
        if data.get('created'):
            created = datetime.fromisoformat(data['created'])
        
        modified = None
        if data.get('modified'):
            modified = datetime.fromisoformat(data['modified'])
        
        return cls(
            name=data['name'],
            description=data.get('description', ''),
            config=config,
            created=created,
            modified=modified,
            # Profile-specific settings (with defaults for backward compatibility)
            telegram_bot_token=data.get('telegram_bot_token', ''),
            telegram_chat_id=data.get('telegram_chat_id', ''),
            telegram_enabled=data.get('telegram_enabled', False),
            telegram_notify_scte35=data.get('telegram_notify_scte35', True),
            telegram_notify_errors=data.get('telegram_notify_errors', True)
        )
    
    def update_config(self, config: StreamConfig):
        """Update profile configuration"""
        self.config = config
        self.modified = datetime.now()

