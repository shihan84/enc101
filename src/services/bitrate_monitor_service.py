"""
Bitrate Monitoring Service
Real-time bitrate monitoring with historical tracking and alerts
"""

import subprocess
import re
import threading
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Callable
from dataclasses import dataclass, field
from ..core.logger import get_logger
from ..utils.exceptions import TSDuckError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .telegram_service import TelegramService


@dataclass
class BitratePoint:
    """Bitrate data point"""
    timestamp: datetime
    bitrate: float  # Mbps
    packets_per_second: int = 0
    raw_data: Dict = field(default_factory=dict)


class BitrateMonitorService:
    """Service for bitrate monitoring and reporting"""
    
    def __init__(self, tsduck_service=None, telegram_service=None):
        self.logger = get_logger("BitrateMonitor")
        self.tsduck_service = tsduck_service
        self.telegram_service: Optional['TelegramService'] = telegram_service
        self.monitoring = False
        self.monitor_process: Optional[subprocess.Popen] = None
        self.monitor_thread: Optional[threading.Thread] = None
        
        # Bitrate tracking
        self.current_bitrate: float = 0.0
        self.bitrate_history: List[BitratePoint] = []
        self.max_history = 10000  # Keep last 10000 points (about 13 hours at 5s intervals)
        
        # Thresholds and alerts
        self.min_bitrate_threshold: Optional[float] = None
        self.max_bitrate_threshold: Optional[float] = None
        self.alert_callbacks: List[Callable[[str, float], None]] = []
        self._last_alert_time: Dict[str, datetime] = {}  # Prevent spam
        
        # Statistics
        self.stats = {
            'average_bitrate': 0.0,
            'min_bitrate': 0.0,
            'max_bitrate': 0.0,
            'total_samples': 0
        }
        
        self.logger.info("Bitrate Monitor service initialized")
    
    def start_monitoring(
        self,
        input_source: str,
        interval: int = 5,
        output_callback: Optional[Callable[[str], None]] = None
    ) -> bool:
        """
        Start bitrate monitoring
        
        Args:
            input_source: Input stream URL/path
            interval: Monitoring interval in seconds
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
            # Build TSDuck command
            command = self._build_monitor_command(input_source, interval)
            
            self.logger.info(f"Starting bitrate monitoring: {input_source}")
            if output_callback:
                output_callback(f"[INFO] Starting bitrate monitoring")
                output_callback(f"[INFO] Interval: {interval}s")
            
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
            
            self.logger.info("Bitrate monitoring started")
            if output_callback:
                output_callback("[SUCCESS] Bitrate monitoring active")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {e}", exc_info=True)
            if output_callback:
                output_callback(f"[ERROR] Failed to start monitoring: {e}")
            self.monitoring = False
            return False
    
    def stop_monitoring(self):
        """Stop bitrate monitoring"""
        if not self.monitoring:
            return
        
        self.logger.info("Stopping bitrate monitoring")
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
        
        self.logger.info("Bitrate monitoring stopped")
    
    def _build_monitor_command(self, input_source: str, interval: int) -> List[str]:
        """Build TSDuck command for bitrate monitoring"""
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
            clean_url = input_source.replace("udp://", "")
            command.extend(["-I", "ip", clean_url])
        else:
            command.extend(["-I", "file", input_source])
        
        # Analyze plugin for bitrate monitoring (more reliable)
        command.extend([
            "-P", "analyze",
            "--interval", str(interval),
            "--json"  # JSON output
        ])
        
        # Drop output
        command.extend(["-O", "drop"])
        
        return command
    
    def _monitor_output(self, output_callback: Optional[Callable[[str], None]]):
        """Monitor TSDuck output for bitrate data"""
        if not self.monitor_process:
            return
        
        try:
            for line in iter(self.monitor_process.stdout.readline, ''):
                if not self.monitoring:
                    break
                
                if not line.strip():
                    continue
                
                # Parse bitrate from output
                bitrate_point = self._parse_bitrate(line)
                
                if bitrate_point:
                    self._handle_bitrate(bitrate_point, output_callback)
                elif output_callback:
                    if "error" in line.lower() or "warning" in line.lower():
                        output_callback(f"[MONITOR] {line.strip()}")
        
        except Exception as e:
            self.logger.error(f"Error in monitor output: {e}", exc_info=True)
            if output_callback:
                output_callback(f"[ERROR] Monitor error: {e}")
        finally:
            self.monitoring = False
    
    def _parse_bitrate(self, line: str) -> Optional[BitratePoint]:
        """Parse bitrate from TSDuck output"""
        try:
            # Try JSON format
            if line.strip().startswith('{'):
                import json
                data = json.loads(line.strip())
                return self._parse_json_bitrate(data)
            
            # Try text format
            return self._parse_text_bitrate(line)
            
        except json.JSONDecodeError:
            return self._parse_text_bitrate(line)
        except Exception as e:
            self.logger.debug(f"Failed to parse bitrate: {e}")
            return None
    
    def _parse_json_bitrate(self, data: Dict) -> Optional[BitratePoint]:
        """Parse JSON bitrate data"""
        try:
            bitrate = float(data.get('bitrate', 0)) / 1000000  # Convert to Mbps
            pps = int(data.get('packets_per_second', 0))
            
            return BitratePoint(
                timestamp=datetime.now(),
                bitrate=bitrate,
                packets_per_second=pps,
                raw_data=data
            )
        except Exception as e:
            self.logger.debug(f"Failed to parse JSON bitrate: {e}")
            return None
    
    def _parse_text_bitrate(self, line: str) -> Optional[BitratePoint]:
        """Parse text format bitrate"""
        try:
            # Look for bitrate pattern
            bitrate_match = re.search(r'bitrate[:\s]+([\d.]+)\s*([KMGT]?bps|Mbps)', line, re.IGNORECASE)
            if not bitrate_match:
                return None
            
            value = float(bitrate_match.group(1))
            unit = bitrate_match.group(2).upper()
            
            if 'K' in unit:
                bitrate = value / 1000
            elif 'M' in unit:
                bitrate = value
            elif 'G' in unit:
                bitrate = value * 1000
            else:
                bitrate = value / 1000000
            
            # Look for packet rate
            pps = 0
            pps_match = re.search(r'packets?[:\s]+(\d+)\s*(?:per\s*)?sec', line, re.IGNORECASE)
            if pps_match:
                pps = int(pps_match.group(1))
            
            return BitratePoint(
                timestamp=datetime.now(),
                bitrate=bitrate,
                packets_per_second=pps
            )
        except Exception as e:
            self.logger.debug(f"Failed to parse text bitrate: {e}")
            return None
    
    def _handle_bitrate(self, point: BitratePoint, output_callback: Optional[Callable[[str], None]]):
        """Handle bitrate data point"""
        # Update current bitrate
        self.current_bitrate = point.bitrate
        
        # Add to history
        self.bitrate_history.append(point)
        if len(self.bitrate_history) > self.max_history:
            self.bitrate_history = self.bitrate_history[-self.max_history:]
        
        # Update statistics
        self._update_statistics()
        
        # Check thresholds
        self._check_thresholds(point.bitrate)
        
        # Log
        if output_callback:
            output_callback(f"[BITRATE] {point.bitrate:.2f} Mbps ({point.packets_per_second} pps)")
    
    def _update_statistics(self):
        """Update bitrate statistics"""
        if not self.bitrate_history:
            return
        
        bitrates = [p.bitrate for p in self.bitrate_history if p.bitrate > 0]
        
        if bitrates:
            self.stats['average_bitrate'] = sum(bitrates) / len(bitrates)
            self.stats['min_bitrate'] = min(bitrates)
            self.stats['max_bitrate'] = max(bitrates)
            self.stats['total_samples'] = len(self.bitrate_history)
    
    def _check_thresholds(self, bitrate: float):
        """Check bitrate thresholds and trigger alerts"""
        if self.min_bitrate_threshold and bitrate < self.min_bitrate_threshold:
            alert_msg = f"Bitrate below minimum threshold: {bitrate:.2f} Mbps < {self.min_bitrate_threshold:.2f} Mbps"
            self._trigger_alert("MIN_BITRATE", alert_msg, bitrate)
        
        if self.max_bitrate_threshold and bitrate > self.max_bitrate_threshold:
            alert_msg = f"Bitrate above maximum threshold: {bitrate:.2f} Mbps > {self.max_bitrate_threshold:.2f} Mbps"
            self._trigger_alert("MAX_BITRATE", alert_msg, bitrate)
    
    def _trigger_alert(self, alert_type: str, message: str, bitrate: float):
        """Trigger bitrate alert"""
        # Prevent alert spam (max once per minute per type)
        now = datetime.now()
        last_alert = self._last_alert_time.get(alert_type)
        if last_alert and (now - last_alert).total_seconds() < 60:
            return
        
        self._last_alert_time[alert_type] = now
        self.logger.warning(message)
        
        # Send Telegram alert
        if self.telegram_service and self.telegram_service.enabled:
            try:
                alert_msg = f"📈 <b>Bitrate Alert</b>\n\n"
                alert_msg += f"<b>Type:</b> {alert_type}\n"
                alert_msg += f"<b>Message:</b> {message}\n"
                alert_msg += f"<b>Current Bitrate:</b> {bitrate:.2f} Mbps\n"
                alert_msg += f"\n<i>Time: {now.strftime('%Y-%m-%d %H:%M:%S')}</i>"
                self.telegram_service.send_message(alert_msg, disable_notification=False)
            except Exception as e:
                self.logger.error(f"Telegram alert error: {e}")
        
        # Call registered callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert_type, bitrate)
            except Exception as e:
                self.logger.error(f"Alert callback error: {e}")
    
    def set_thresholds(self, min_bitrate: Optional[float] = None, max_bitrate: Optional[float] = None):
        """Set bitrate thresholds"""
        self.min_bitrate_threshold = min_bitrate
        self.max_bitrate_threshold = max_bitrate
        self.logger.info(f"Bitrate thresholds set: min={min_bitrate}, max={max_bitrate}")
    
    def register_alert_callback(self, callback: Callable[[str, float], None]):
        """Register callback for bitrate alerts"""
        self.alert_callbacks.append(callback)
    
    def get_current_bitrate(self) -> float:
        """Get current bitrate"""
        return self.current_bitrate
    
    def get_bitrate_history(self, limit: int = 1000, time_range: Optional[timedelta] = None) -> List[BitratePoint]:
        """Get bitrate history"""
        if time_range:
            cutoff = datetime.now() - time_range
            return [p for p in self.bitrate_history if p.timestamp >= cutoff]
        return self.bitrate_history[-limit:]
    
    def get_statistics(self) -> Dict:
        """Get bitrate statistics"""
        return {
            **self.stats,
            'current_bitrate': self.current_bitrate,
            'monitoring_active': self.monitoring
        }
    
    def export_report(self, format: str = "csv") -> str:
        """Export bitrate report"""
        if format.lower() == "csv":
            lines = ["Timestamp,Bitrate (Mbps),Packets/sec"]
            for point in self.bitrate_history:
                lines.append(f"{point.timestamp.isoformat()},{point.bitrate:.2f},{point.packets_per_second}")
            return "\n".join(lines)
        elif format.lower() == "json":
            import json
            data = {
                'statistics': self.stats,
                'history': [
                    {
                        'timestamp': p.timestamp.isoformat(),
                        'bitrate': p.bitrate,
                        'packets_per_second': p.packets_per_second
                    }
                    for p in self.bitrate_history
                ]
            }
            return json.dumps(data, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def clear_history(self):
        """Clear bitrate history"""
        self.bitrate_history.clear()
        self.current_bitrate = 0.0
        self.stats = {
            'average_bitrate': 0.0,
            'min_bitrate': 0.0,
            'max_bitrate': 0.0,
            'total_samples': 0
        }
        self.logger.info("Bitrate history cleared")

