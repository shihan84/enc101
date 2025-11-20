"""
Stream Quality Analysis Service
Real-time stream quality monitoring using TSDuck analyze plugin
"""

import subprocess
import re
import threading
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Callable
from dataclasses import dataclass, field
from ..core.logger import get_logger
from ..utils.exceptions import TSDuckError


@dataclass
class StreamMetrics:
    """Stream quality metrics"""
    timestamp: datetime
    bitrate: float = 0.0  # Mbps
    packets_per_second: int = 0
    continuity_errors: int = 0
    pcr_errors: int = 0
    pcr_jitter: float = 0.0  # microseconds
    ts_errors: int = 0
    pcr_pid: Optional[int] = None
    services_count: int = 0
    pids_count: int = 0
    raw_data: Dict = field(default_factory=dict)


@dataclass
class ComplianceReport:
    """ETSI TR 101 290 compliance report"""
    priority_1_errors: int = 0
    priority_2_errors: int = 0
    priority_3_errors: int = 0
    compliant: bool = True
    details: Dict = field(default_factory=dict)


class StreamAnalyzerService:
    """Service for real-time stream quality analysis"""
    
    def __init__(self, tsduck_service=None, telegram_service=None):
        self.logger = get_logger("StreamAnalyzer")
        self.tsduck_service = tsduck_service
        self.telegram_service: Optional['TelegramService'] = telegram_service
        self.analyzing = False
        self.analyzer_process: Optional[subprocess.Popen] = None
        self.analyzer_thread: Optional[threading.Thread] = None
        
        # Metrics tracking
        self.current_metrics: Optional[StreamMetrics] = None
        self.metrics_history: List[StreamMetrics] = []
        self.max_history = 1000  # Keep last 1000 metrics
        
        # Compliance tracking
        self.compliance_report: Optional[ComplianceReport] = None
        
        # Callbacks
        self.metrics_callbacks: List[Callable[[StreamMetrics], None]] = []
        self.compliance_callbacks: List[Callable[[ComplianceReport], None]] = []
        
        # Alert settings
        self.alert_on_compliance_failure = True
        
        self.logger.info("Stream Analyzer service initialized")
    
    def start_analysis(
        self,
        input_source: str,
        output_callback: Optional[Callable[[str], None]] = None,
        interval: int = 5
    ) -> bool:
        """
        Start stream quality analysis
        
        Args:
            input_source: Input stream URL/path
            output_callback: Callback for log messages
            interval: Analysis interval in seconds
        
        Returns:
            True if analysis started successfully
        """
        if self.analyzing:
            self.logger.warning("Analysis already active")
            return False
        
        if not self.tsduck_service:
            error_msg = "TSDuck service not available"
            self.logger.error(error_msg)
            if output_callback:
                output_callback(f"[ERROR] {error_msg}")
            return False
        
        try:
            # Build TSDuck command with analyze plugin
            command = self._build_analyze_command(input_source, interval)
            
            self.logger.info(f"Starting stream analysis: {input_source}")
            if output_callback:
                output_callback(f"[INFO] Starting stream quality analysis")
                output_callback(f"[INFO] Input: {input_source}")
            
            # Start TSDuck process
            self.analyzer_process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            self.analyzing = True
            
            # Start analysis thread
            self.analyzer_thread = threading.Thread(
                target=self._analyze_output,
                args=(output_callback,),
                daemon=True
            )
            self.analyzer_thread.start()
            
            self.logger.info("Stream analysis started")
            if output_callback:
                output_callback("[SUCCESS] Stream analysis active")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start analysis: {e}", exc_info=True)
            if output_callback:
                output_callback(f"[ERROR] Failed to start analysis: {e}")
            self.analyzing = False
            return False
    
    def stop_analysis(self):
        """Stop stream analysis"""
        if not self.analyzing:
            return
        
        self.logger.info("Stopping stream analysis")
        self.analyzing = False
        
        # Terminate process
        if self.analyzer_process:
            try:
                self.analyzer_process.terminate()
                self.analyzer_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.analyzer_process.kill()
            except Exception as e:
                self.logger.error(f"Error stopping analyzer process: {e}")
            finally:
                self.analyzer_process = None
        
        # Wait for thread
        if self.analyzer_thread and self.analyzer_thread.is_alive():
            self.analyzer_thread.join(timeout=2)
        
        self.logger.info("Stream analysis stopped")
    
    def _build_analyze_command(self, input_source: str, interval: int) -> List[str]:
        """Build TSDuck command for stream analysis"""
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
        
        # Analyze plugin - comprehensive analysis
        command.extend([
            "-P", "analyze",
            "--interval", str(interval),
            "--json"  # JSON output for easier parsing
        ])
        
        # Continuity plugin - detect continuity errors
        command.extend(["-P", "continuity"])
        
        # PCR verify plugin - PCR accuracy
        command.extend(["-P", "pcrverify"])
        
        # Drop output (we only want analysis)
        command.extend(["-O", "drop"])
        
        return command
    
    def _analyze_output(self, output_callback: Optional[Callable[[str], None]]):
        """Analyze TSDuck output for metrics"""
        if not self.analyzer_process:
            return
        
        try:
            for line in iter(self.analyzer_process.stdout.readline, ''):
                if not self.analyzing:
                    break
                
                if not line.strip():
                    continue
                
                # Parse metrics from output
                metrics = self._parse_metrics(line)
                
                if metrics:
                    self._handle_metrics(metrics, output_callback)
                elif output_callback:
                    # Log non-metric lines
                    if "error" in line.lower() or "warning" in line.lower():
                        output_callback(f"[ANALYZER] {line.strip()}")
        
        except Exception as e:
            self.logger.error(f"Error in analyzer output: {e}", exc_info=True)
            if output_callback:
                output_callback(f"[ERROR] Analyzer error: {e}")
        finally:
            self.analyzing = False
    
    def _parse_metrics(self, line: str) -> Optional[StreamMetrics]:
        """Parse metrics from TSDuck output"""
        try:
            # Try JSON format first
            if line.strip().startswith('{'):
                import json
                data = json.loads(line.strip())
                return self._parse_json_metrics(data)
            
            # Try text format parsing
            return self._parse_text_metrics(line)
            
        except json.JSONDecodeError:
            return self._parse_text_metrics(line)
        except Exception as e:
            self.logger.debug(f"Failed to parse metrics: {e}")
            return None
    
    def _parse_json_metrics(self, data: Dict) -> Optional[StreamMetrics]:
        """Parse JSON metrics from TSDuck"""
        try:
            metrics = StreamMetrics(timestamp=datetime.now(), raw_data=data)
            
            # Extract bitrate
            if 'bitrate' in data:
                metrics.bitrate = float(data['bitrate']) / 1000000  # Convert to Mbps
            
            # Extract packet rate
            if 'packets' in data:
                metrics.packets_per_second = int(data.get('packets_per_second', 0))
            
            # Extract errors
            metrics.continuity_errors = int(data.get('continuity_errors', 0))
            metrics.pcr_errors = int(data.get('pcr_errors', 0))
            metrics.ts_errors = int(data.get('ts_errors', 0))
            
            # Extract PCR jitter
            if 'pcr_jitter' in data:
                metrics.pcr_jitter = float(data['pcr_jitter'])
            
            # Extract service/PID counts
            metrics.services_count = int(data.get('services', 0))
            metrics.pids_count = int(data.get('pids', 0))
            
            # Extract PCR PID
            if 'pcr_pid' in data:
                metrics.pcr_pid = int(data['pcr_pid'])
            
            return metrics
            
        except Exception as e:
            self.logger.debug(f"Failed to parse JSON metrics: {e}")
            return None
    
    def _parse_text_metrics(self, line: str) -> Optional[StreamMetrics]:
        """Parse text format metrics from TSDuck"""
        try:
            metrics = StreamMetrics(timestamp=datetime.now())
            
            # Look for bitrate
            bitrate_match = re.search(r'bitrate[:\s]+([\d.]+)\s*([KMGT]?bps|Mbps)', line, re.IGNORECASE)
            if bitrate_match:
                value = float(bitrate_match.group(1))
                unit = bitrate_match.group(2).upper()
                if 'K' in unit:
                    metrics.bitrate = value / 1000
                elif 'M' in unit:
                    metrics.bitrate = value
                elif 'G' in unit:
                    metrics.bitrate = value * 1000
                else:
                    metrics.bitrate = value / 1000000
            
            # Look for packet rate
            pps_match = re.search(r'packets?[:\s]+(\d+)\s*(?:per\s*)?sec', line, re.IGNORECECASE)
            if pps_match:
                metrics.packets_per_second = int(pps_match.group(1))
            
            # Look for continuity errors
            cont_match = re.search(r'continuity[:\s]+(\d+)', line, re.IGNORECASE)
            if cont_match:
                metrics.continuity_errors = int(cont_match.group(1))
            
            # Look for PCR errors
            pcr_match = re.search(r'pcr[:\s]+(?:error|jitter)[:\s]+([\d.]+)', line, re.IGNORECASE)
            if pcr_match:
                metrics.pcr_jitter = float(pcr_match.group(1))
            
            return metrics
            
        except Exception as e:
            self.logger.debug(f"Failed to parse text metrics: {e}")
            return None
    
    def _handle_metrics(self, metrics: StreamMetrics, output_callback: Optional[Callable[[str], None]]):
        """Handle parsed metrics"""
        # Update current metrics
        self.current_metrics = metrics
        
        # Add to history
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > self.max_history:
            self.metrics_history = self.metrics_history[-self.max_history:]
        
        # Check compliance
        self._check_compliance(metrics)
        
        # Log metrics
        metrics_str = f"[METRICS] Bitrate: {metrics.bitrate:.2f} Mbps, "
        metrics_str += f"Packets/sec: {metrics.packets_per_second}, "
        metrics_str += f"Errors: {metrics.continuity_errors}"
        
        self.logger.debug(metrics_str)
        
        if output_callback:
            output_callback(metrics_str)
        
        # Call registered callbacks
        for callback in self.metrics_callbacks:
            try:
                callback(metrics)
            except Exception as e:
                self.logger.error(f"Metrics callback error: {e}")
    
    def _check_compliance(self, metrics: StreamMetrics):
        """Check ETSI TR 101 290 compliance"""
        report = ComplianceReport()
        
        # Priority 1: Critical errors
        if metrics.ts_errors > 0:
            report.priority_1_errors += metrics.ts_errors
        if metrics.continuity_errors > 10:  # Threshold
            report.priority_1_errors += metrics.continuity_errors
        
        # Priority 2: Important errors
        if metrics.pcr_errors > 0:
            report.priority_2_errors += metrics.pcr_errors
        if metrics.pcr_jitter > 500:  # 500 microseconds threshold
            report.priority_2_errors += 1
        
        # Priority 3: Warnings
        if metrics.bitrate == 0:
            report.priority_3_errors += 1
        if metrics.packets_per_second == 0:
            report.priority_3_errors += 1
        
        report.compliant = (report.priority_1_errors == 0 and 
                           report.priority_2_errors == 0)
        
        report.details = {
            'ts_errors': metrics.ts_errors,
            'continuity_errors': metrics.continuity_errors,
            'pcr_errors': metrics.pcr_errors,
            'pcr_jitter': metrics.pcr_jitter
        }
        
        # Check if compliance status changed
        previous_compliant = self.compliance_report.compliant if self.compliance_report else True
        self.compliance_report = report
        
        # Send Telegram alert if compliance failed
        if self.telegram_service and self.telegram_service.enabled and self.alert_on_compliance_failure:
            if not report.compliant and previous_compliant:
                try:
                    message = f"⚠️ <b>Stream Quality Alert</b>\n\n"
                    message += f"<b>Status:</b> Non-Compliant (ETSI TR 101 290)\n"
                    message += f"<b>Priority 1 Errors:</b> {report.priority_1_errors}\n"
                    message += f"<b>Priority 2 Errors:</b> {report.priority_2_errors}\n"
                    message += f"<b>Priority 3 Errors:</b> {report.priority_3_errors}\n"
                    message += f"<b>Bitrate:</b> {metrics.bitrate:.2f} Mbps\n"
                    message += f"<b>Continuity Errors:</b> {metrics.continuity_errors}\n"
                    message += f"<b>PCR Jitter:</b> {metrics.pcr_jitter:.2f} μs\n"
                    message += f"\n<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
                    self.telegram_service.send_message(message, disable_notification=False)
                except Exception as e:
                    self.logger.error(f"Telegram alert error: {e}")
        
        # Call compliance callbacks
        for callback in self.compliance_callbacks:
            try:
                callback(report)
            except Exception as e:
                self.logger.error(f"Compliance callback error: {e}")
    
    def register_metrics_callback(self, callback: Callable[[StreamMetrics], None]):
        """Register callback for metrics updates"""
        self.metrics_callbacks.append(callback)
    
    def register_compliance_callback(self, callback: Callable[[ComplianceReport], None]):
        """Register callback for compliance updates"""
        self.compliance_callbacks.append(callback)
    
    def get_current_metrics(self) -> Optional[StreamMetrics]:
        """Get current stream metrics"""
        return self.current_metrics
    
    def get_metrics_history(self, limit: int = 100) -> List[StreamMetrics]:
        """Get metrics history"""
        return self.metrics_history[-limit:]
    
    def get_compliance_report(self) -> Optional[ComplianceReport]:
        """Get compliance report"""
        return self.compliance_report
    
    def clear_history(self):
        """Clear metrics history"""
        self.metrics_history.clear()
        self.current_metrics = None
        self.compliance_report = None
        self.logger.info("Metrics history cleared")

