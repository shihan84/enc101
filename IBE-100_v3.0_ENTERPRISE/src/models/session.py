"""
Stream session model
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from .stream_config import StreamConfig
from .scte35_marker import SCTE35Marker


@dataclass
class StreamSession:
    """Stream processing session model"""
    session_id: str
    config: StreamConfig
    marker: Optional[SCTE35Marker] = None
    
    # Status
    status: str = "stopped"  # stopped, starting, running, error, stopped
    start_time: Optional[datetime] = None
    stop_time: Optional[datetime] = None
    
    # Statistics
    bytes_processed: int = 0
    packets_processed: int = 0
    errors_count: int = 0
    scte35_injected: int = 0
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'session_id': self.session_id,
            'config': self.config.to_dict(),
            'marker': self.marker.to_dict() if self.marker else None,
            'status': self.status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'stop_time': self.stop_time.isoformat() if self.stop_time else None,
            'bytes_processed': self.bytes_processed,
            'packets_processed': self.packets_processed,
            'errors_count': self.errors_count,
            'scte35_injected': self.scte35_injected,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'StreamSession':
        """Create from dictionary"""
        from .stream_config import StreamConfig
        from .scte35_marker import SCTE35Marker
        
        config = StreamConfig.from_dict(data['config'])
        marker = None
        if data.get('marker'):
            marker = SCTE35Marker.from_dict(data['marker'])
        
        start_time = None
        if data.get('start_time'):
            start_time = datetime.fromisoformat(data['start_time'])
        
        stop_time = None
        if data.get('stop_time'):
            stop_time = datetime.fromisoformat(data['stop_time'])
        
        created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now()
        
        return cls(
            session_id=data['session_id'],
            config=config,
            marker=marker,
            status=data.get('status', 'stopped'),
            start_time=start_time,
            stop_time=stop_time,
            bytes_processed=data.get('bytes_processed', 0),
            packets_processed=data.get('packets_processed', 0),
            errors_count=data.get('errors_count', 0),
            scte35_injected=data.get('scte35_injected', 0),
            created_at=created_at
        )

