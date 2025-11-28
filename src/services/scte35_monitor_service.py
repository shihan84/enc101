"""
SCTE-35 Monitoring Service
Real-time SCTE-35 event detection and tracking using TSDuck splicemonitor
"""

import subprocess
import json
import re
import threading
import queue
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Callable
from dataclasses import dataclass, field
from ..core.logger import get_logger
from ..utils.exceptions import SCTE35Error
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .telegram_service import TelegramService


@dataclass
class SCTE35Event:
    """Detected SCTE-35 event"""
    timestamp: datetime
    event_id: Optional[int] = None
    cue_type: Optional[str] = None
    splice_command_type: Optional[int] = None
    pts_time: Optional[int] = None
    break_duration: Optional[int] = None
    out_of_network: Optional[bool] = None
    splice_immediate: Optional[bool] = None
    raw_data: Dict = field(default_factory=dict)
    source: Optional[str] = None


class SCTE35MonitorService:
    """Service for real-time SCTE-35 event monitoring"""
    
    def __init__(self, tsduck_service=None, telegram_service=None):
        self.logger = get_logger("SCTE35Monitor")
        self.tsduck_service = tsduck_service
        self.telegram_service: Optional['TelegramService'] = telegram_service
        self.monitoring = False
        self.monitor_process: Optional[subprocess.Popen] = None
        self.monitor_thread: Optional[threading.Thread] = None
        
        # Event tracking
        self.detected_events: List[SCTE35Event] = []
        self.max_events = 1000  # Keep last 1000 events
        self.event_callbacks: List[Callable[[SCTE35Event], None]] = []
        
        # Telegram notification settings
        self.telegram_notify_enabled = True
        
        # Statistics
        self.stats = {
            'total_events': 0,
            'events_by_type': {},
            'last_event_time': None,
            'events_per_minute': 0
        }
        
        self.logger.info("SCTE-35 Monitor service initialized")
    
    def set_telegram_service(self, telegram_service: 'TelegramService'):
        """Set Telegram service for notifications"""
        self.telegram_service = telegram_service
    
    def enable_telegram_notifications(self, enabled: bool = True):
        """Enable/disable Telegram notifications"""
        self.telegram_notify_enabled = enabled
    
    def start_monitoring(
        self,
        input_source: str,
        scte35_pid: int = 500,
        output_callback: Optional[Callable[[str], None]] = None
    ) -> bool:
        """
        Start monitoring SCTE-35 events in a stream
        
        Args:
            input_source: Input stream URL/path
            scte35_pid: PID for SCTE-35 data (default: 500)
            output_callback: Callback for log messages
        
        Returns:
            True if monitoring started successfully
        """
        if self.monitoring:
            self.logger.warning("Monitoring already active")
            return False
        
        if not self.tsduck_service:
            error_msg = "TSDuck service not available"
            self.logger.error(error_msg)
            if output_callback:
                output_callback(f"[ERROR] {error_msg}")
            return False
        
        try:
            # Build TSDuck command with splicemonitor plugin
            command = self._build_monitor_command(input_source, scte35_pid)
            
            self.logger.info(f"Starting SCTE-35 monitoring: {input_source}")
            if output_callback:
                output_callback(f"[INFO] Starting SCTE-35 monitoring on PID {scte35_pid}")
                output_callback(f"[INFO] Input: {input_source}")
            
            # Start TSDuck process
            self.monitor_process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            self.monitoring = True
            
            # Start monitoring thread
            self.monitor_thread = threading.Thread(
                target=self._monitor_output,
                args=(output_callback,),
                daemon=True
            )
            self.monitor_thread.start()
            
            self.logger.info("SCTE-35 monitoring started")
            if output_callback:
                output_callback("[SUCCESS] SCTE-35 monitoring active")
            
            # Send Telegram notification
            if self.telegram_service and self.telegram_notify_enabled:
                self.telegram_service.send_monitoring_started(input_source, scte35_pid)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {e}", exc_info=True)
            if output_callback:
                output_callback(f"[ERROR] Failed to start monitoring: {e}")
            self.monitoring = False
            return False
    
    def stop_monitoring(self):
        """Stop SCTE-35 monitoring"""
        if not self.monitoring:
            return
        
        self.logger.info("Stopping SCTE-35 monitoring")
        self.monitoring = False
        
        # Terminate process
        if self.monitor_process:
            try:
                self.monitor_process.terminate()
                self.monitor_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.monitor_process.kill()
            except Exception as e:
                self.logger.error(f"Error stopping monitor process: {e}")
            finally:
                self.monitor_process = None
        
        # Wait for thread
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2)
        
        # Send Telegram notification
        if self.telegram_service and self.telegram_notify_enabled:
            self.telegram_service.send_monitoring_stopped()
        
        self.logger.info("SCTE-35 monitoring stopped")
    
    def _build_monitor_command(self, input_source: str, scte35_pid: int) -> List[str]:
        """Build TSDuck command for SCTE-35 monitoring"""
        tsduck_path = self.tsduck_service.tsduck_path
        
        command = [tsduck_path]
        
        # Input plugin - detect type
        if input_source.startswith("http://") or input_source.startswith("https://"):
            if input_source.endswith(".m3u8") or "/playlist" in input_source.lower():
                command.extend(["-I", "hls", input_source])
            else:
                command.extend(["-I", "http", input_source])
        elif input_source.startswith("srt://") or input_source.startswith("srt:"):
            clean_url = input_source.replace("srt://", "").replace("srt:", "")
            command.extend(["-I", "srt", clean_url, "--transtype", "live"])
        elif input_source.startswith("udp://") or ":" in input_source and not input_source.startswith("http"):
            # Assume UDP
            clean_url = input_source.replace("udp://", "")
            command.extend(["-I", "ip", clean_url])
        else:
            # File input
            command.extend(["-I", "file", input_source])
        
        # Splicemonitor plugin - monitors SCTE-35 events
        # Note: splicemonitor automatically monitors all SCTE-35 splice information
        # No --pid option needed (it monitors all SCTE-35 PIDs automatically)
        command.extend([
            "-P", "splicemonitor",
            "--json"  # Output in JSON format for easier parsing
        ])
        
        # Drop output (we only want monitoring)
        command.extend(["-O", "drop"])
        
        return command
    
    def _monitor_output(self, output_callback: Optional[Callable[[str], None]]):
        """Monitor TSDuck output for SCTE-35 events"""
        if not self.monitor_process:
            return
        
        try:
            for line in iter(self.monitor_process.stdout.readline, ''):
                if not self.monitoring:
                    break
                
                if not line.strip():
                    continue
                
                # Try to parse as JSON (TSDuck JSON output)
                event = self._parse_line(line)
                
                if event:
                    self._handle_event(event, output_callback)
                elif output_callback:
                    # Log non-event lines
                    if "error" in line.lower() or "warning" in line.lower():
                        output_callback(f"[MONITOR] {line.strip()}")
        
        except Exception as e:
            self.logger.error(f"Error in monitor output: {e}", exc_info=True)
            if output_callback:
                output_callback(f"[ERROR] Monitor error: {e}")
        finally:
            self.monitoring = False
    
    def _parse_line(self, line: str) -> Optional[SCTE35Event]:
        """Parse TSDuck output line for SCTE-35 events"""
        try:
            # Try JSON format first
            if line.strip().startswith('{'):
                data = json.loads(line.strip())
                return self._parse_json_event(data)
            
            # Try text format parsing
            return self._parse_text_event(line)
            
        except json.JSONDecodeError:
            # Not JSON, try text parsing
            return self._parse_text_event(line)
        except Exception as e:
            self.logger.debug(f"Failed to parse line: {e}")
            return None
    
    def _parse_json_event(self, data: Dict) -> Optional[SCTE35Event]:
        """Parse JSON event data from TSDuck"""
        try:
            # TSDuck splicemonitor JSON format varies, try common fields
            event = SCTE35Event(
                timestamp=datetime.now(),
                raw_data=data
            )
            
            # Extract common fields
            if 'splice_event_id' in data:
                event.event_id = int(data['splice_event_id'])
            
            if 'splice_command_type' in data:
                event.splice_command_type = int(data['splice_command_type'])
            
            if 'pts_time' in data:
                event.pts_time = int(data['pts_time'])
            
            if 'break_duration' in data:
                event.break_duration = int(data['break_duration'])
            
            if 'out_of_network' in data:
                event.out_of_network = bool(data['out_of_network'])
            
            if 'splice_immediate' in data:
                event.splice_immediate = bool(data['splice_immediate'])
            
            # Determine cue type from command type
            if event.splice_command_type:
                cue_type_map = {
                    0x05: "Splice Insert",
                    0x06: "Time Signal",
                    0x07: "Bandwidth Reservation"
                }
                event.cue_type = cue_type_map.get(event.splice_command_type, "Unknown")
            
            return event
            
        except Exception as e:
            self.logger.debug(f"Failed to parse JSON event: {e}")
            return None
    
    def _parse_text_event(self, line: str) -> Optional[SCTE35Event]:
        """Parse text format event from TSDuck"""
        try:
            # Look for SCTE-35 keywords
            if not any(keyword in line.lower() for keyword in ['splice', 'scte', 'cue', 'break']):
                return None
            
            event = SCTE35Event(
                timestamp=datetime.now(),
                raw_data={'text': line.strip()}
            )
            
            # Try to extract event ID
            event_id_match = re.search(r'event[_\s]*id[:\s]*(\d+)', line, re.IGNORECASE)
            if event_id_match:
                event.event_id = int(event_id_match.group(1))
            
            # Try to extract PTS
            pts_match = re.search(r'pts[:\s]*(\d+)', line, re.IGNORECASE)
            if pts_match:
                event.pts_time = int(pts_match.group(1))
            
            # Determine cue type from keywords
            line_lower = line.lower()
            if 'cue-out' in line_lower or 'out_of_network' in line_lower:
                event.cue_type = "CUE-OUT"
            elif 'cue-in' in line_lower or 'in_network' in line_lower:
                event.cue_type = "CUE-IN"
            elif 'preroll' in line_lower:
                event.cue_type = "PREROLL"
            elif 'time_signal' in line_lower or 'time signal' in line_lower:
                event.cue_type = "TIME_SIGNAL"
            
            return event
            
        except Exception as e:
            self.logger.debug(f"Failed to parse text event: {e}")
            return None
    
    def _handle_event(self, event: SCTE35Event, output_callback: Optional[Callable[[str], None]]):
        """Handle detected SCTE-35 event"""
        # Add to events list
        self.detected_events.append(event)
        
        # Limit events list size
        if len(self.detected_events) > self.max_events:
            self.detected_events = self.detected_events[-self.max_events:]
        
        # Update statistics
        self.stats['total_events'] += 1
        self.stats['last_event_time'] = event.timestamp
        
        if event.cue_type:
            self.stats['events_by_type'][event.cue_type] = \
                self.stats['events_by_type'].get(event.cue_type, 0) + 1
        
        # Calculate events per minute (last minute)
        one_minute_ago = datetime.now().timestamp() - 60
        recent_events = [e for e in self.detected_events 
                        if e.timestamp.timestamp() > one_minute_ago]
        self.stats['events_per_minute'] = len(recent_events)
        
        # Log event
        event_str = f"[SCTE-35] Event detected: {event.cue_type or 'Unknown'}"
        if event.event_id:
            event_str += f" (ID: {event.event_id})"
        if event.pts_time:
            event_str += f" PTS: {event.pts_time}"
        
        self.logger.info(event_str)
        
        if output_callback:
            output_callback(event_str)
        
        # Send Telegram notification
        if self.telegram_service and self.telegram_notify_enabled:
            try:
                self.telegram_service.send_scte35_alert(
                    event_id=event.event_id,
                    cue_type=event.cue_type,
                    pts_time=event.pts_time,
                    break_duration=event.break_duration,
                    out_of_network=event.out_of_network,
                    source=event.source
                )
            except Exception as e:
                self.logger.error(f"Telegram notification error: {e}")
        
        # Call registered callbacks
        for callback in self.event_callbacks:
            try:
                callback(event)
            except Exception as e:
                self.logger.error(f"Event callback error: {e}")
    
    def register_event_callback(self, callback: Callable[[SCTE35Event], None]):
        """Register callback for SCTE-35 events"""
        self.event_callbacks.append(callback)
    
    def get_recent_events(self, limit: int = 50) -> List[SCTE35Event]:
        """Get recent SCTE-35 events"""
        return self.detected_events[-limit:]
    
    def get_statistics(self) -> Dict:
        """Get monitoring statistics"""
        return {
            **self.stats,
            'monitoring_active': self.monitoring,
            'total_detected': len(self.detected_events)
        }
    
    def clear_events(self):
        """Clear event history"""
        self.detected_events.clear()
        self.stats = {
            'total_events': 0,
            'events_by_type': {},
            'last_event_time': None,
            'events_per_minute': 0
        }
        self.logger.info("Event history cleared")

