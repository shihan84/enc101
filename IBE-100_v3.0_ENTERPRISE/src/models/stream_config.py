"""
Stream configuration model
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class InputType(Enum):
    """Input stream types"""
    HLS = "HLS (HTTP Live Streaming)"
    SRT = "SRT (Secure Reliable Transport)"
    UDP = "UDP (User Datagram Protocol)"
    TCP = "TCP (Transmission Control Protocol)"
    HTTP = "HTTP/HTTPS"
    DVB = "DVB"
    ASI = "ASI"


class OutputType(Enum):
    """Output stream types"""
    SRT = "SRT"
    HLS = "HLS"
    DASH = "DASH"
    UDP = "UDP"
    TCP = "TCP"
    HTTP = "HTTP/HTTPS"
    FILE = "File"


@dataclass
class StreamConfig:
    """Stream configuration model"""
    # Input configuration
    input_type: InputType = InputType.HLS
    input_url: str = ""
    
    # Output configuration
    output_type: OutputType = OutputType.SRT
    output_srt: str = ""
    output_hls: str = "output/hls"
    output_dash: str = "output/dash"
    
    # Service configuration
    service_name: str = "SCTE-35 Stream"
    provider_name: str = "ITAssist"
    service_id: int = 1
    
    # PID configuration
    vpid: int = 256
    apid: int = 257
    scte35_pid: int = 500
    
    # SRT configuration
    stream_id: str = "#!::r=scte/scte,m=publish"
    latency: int = 2000
    
    # HLS/DASH configuration
    enable_cors: bool = True
    segment_duration: int = 6
    playlist_window: int = 5
    
    # SCTE-35 injection settings
    start_delay: int = 2000
    inject_count: int = 1
    inject_interval: int = 1000
    
    # Metadata
    profile_name: Optional[str] = None
    description: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'input_type': self.input_type.value,
            'input_url': self.input_url,
            'output_type': self.output_type.value,
            'output_srt': self.output_srt,
            'output_hls': self.output_hls,
            'output_dash': self.output_dash,
            'service_name': self.service_name,
            'provider_name': self.provider_name,
            'service_id': self.service_id,
            'vpid': self.vpid,
            'apid': self.apid,
            'scte35_pid': self.scte35_pid,
            'stream_id': self.stream_id,
            'latency': self.latency,
            'enable_cors': self.enable_cors,
            'segment_duration': self.segment_duration,
            'playlist_window': self.playlist_window,
            'start_delay': self.start_delay,
            'inject_count': self.inject_count,
            'inject_interval': self.inject_interval,
            'profile_name': self.profile_name,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'StreamConfig':
        """Create from dictionary"""
        # Convert enum strings back to enums
        input_type = InputType(data.get('input_type', InputType.HLS.value))
        output_type = OutputType(data.get('output_type', OutputType.SRT.value))
        
        return cls(
            input_type=input_type,
            input_url=data.get('input_url', ''),
            output_type=output_type,
            output_srt=data.get('output_srt', ''),
            output_hls=data.get('output_hls', 'output/hls'),
            output_dash=data.get('output_dash', 'output/dash'),
            service_name=data.get('service_name', 'SCTE-35 Stream'),
            provider_name=data.get('provider_name', 'ITAssist'),
            service_id=data.get('service_id', 1),
            vpid=data.get('vpid', 256),
            apid=data.get('apid', 257),
            scte35_pid=data.get('scte35_pid', 500),
            stream_id=data.get('stream_id', '#!::r=scte/scte,m=publish'),
            latency=data.get('latency', 2000),
            enable_cors=data.get('enable_cors', True),
            segment_duration=data.get('segment_duration', 6),
            playlist_window=data.get('playlist_window', 5),
            start_delay=data.get('start_delay', 2000),
            inject_count=data.get('inject_count', 1),
            inject_interval=data.get('inject_interval', 1000),
            profile_name=data.get('profile_name'),
            description=data.get('description')
        )

