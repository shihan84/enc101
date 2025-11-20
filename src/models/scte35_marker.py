"""
SCTE-35 marker model
"""

from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from typing import Optional
from pathlib import Path


class CueType(Enum):
    """SCTE-35 cue types"""
    PREROLL = "Pre-roll (Program Transition)"
    CUE_OUT = "CUE-OUT (Ad Break Start)"
    CUE_IN = "CUE-IN (Ad Break End)"
    TIME_SIGNAL = "Time Signal"
    CUE_CRASH = "CUE-CRASH (Emergency Return)"


@dataclass
class SCTE35Marker:
    """SCTE-35 marker model"""
    event_id: int = 10023
    cue_type: CueType = CueType.PREROLL
    preroll_seconds: int = 4  # Industry standard minimum: 4.0 seconds
    ad_duration_seconds: int = 600
    schedule_time: Optional[str] = None
    immediate: bool = True
    
    # File paths
    xml_path: Optional[Path] = None
    json_path: Optional[Path] = None
    
    # Metadata
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize metadata after creation"""
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'event_id': self.event_id,
            'cue_type': self.cue_type.value,
            'preroll_seconds': self.preroll_seconds,
            'ad_duration_seconds': self.ad_duration_seconds,
            'schedule_time': self.schedule_time,
            'immediate': self.immediate,
            'xml_path': str(self.xml_path) if self.xml_path else None,
            'json_path': str(self.json_path) if self.json_path else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SCTE35Marker':
        """Create from dictionary"""
        cue_type = CueType(data.get('cue_type', CueType.PREROLL.value))
        
        created_at = None
        if data.get('created_at'):
            created_at = datetime.fromisoformat(data['created_at'])
        
        xml_path = Path(data['xml_path']) if data.get('xml_path') else None
        json_path = Path(data['json_path']) if data.get('json_path') else None
        
        return cls(
            event_id=data.get('event_id', 10023),
            cue_type=cue_type,
            preroll_seconds=data.get('preroll_seconds', 4),  # Industry standard minimum: 4.0 seconds
            ad_duration_seconds=data.get('ad_duration_seconds', 600),
            schedule_time=data.get('schedule_time'),
            immediate=data.get('immediate', True),
            xml_path=xml_path,
            json_path=json_path,
            created_at=created_at
        )

