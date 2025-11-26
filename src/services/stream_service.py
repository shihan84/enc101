"""
Stream Processing Service
Manages stream processing sessions with error handling and recovery
"""

import threading
import time
import subprocess
from datetime import datetime
from typing import Optional, Callable
from pathlib import Path
from ..core.logger import get_logger
from ..models.stream_config import StreamConfig
from ..models.session import StreamSession
from ..models.scte35_marker import SCTE35Marker
from .tsduck_service import TSDuckService
from .dynamic_marker_service import DynamicMarkerService
from ..utils.exceptions import StreamError
import uuid

# Optional Telegram service import
try:
    from .telegram_service import TelegramService
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    TelegramService = None


class StreamService:
    """Service for managing stream processing"""
    
    def __init__(self, tsduck_service: TSDuckService, telegram_service=None, dynamic_marker_service: Optional[DynamicMarkerService] = None):
        self.logger = get_logger("StreamService")
        self.tsduck_service = tsduck_service
        self.telegram_service = telegram_service  # Optional Telegram service
        self.dynamic_marker_service = dynamic_marker_service  # Optional dynamic marker service
        self._current_session: Optional[StreamSession] = None
        self._process: Optional[subprocess.Popen] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._output_callbacks = []
        self.logger.info("Stream service initialized")
    
    def start_stream(
        self,
        config: StreamConfig,
        marker: Optional[SCTE35Marker] = None,
        output_callback: Optional[Callable[[str], None]] = None
    ) -> StreamSession:
        """
        Start stream processing
        
        Args:
            config: Stream configuration
            marker: Optional SCTE-35 marker
            output_callback: Callback for output lines
        
        Returns:
            StreamSession object
        """
        if self._running:
            raise StreamError("Stream is already running")
        
        # Input validation
        from ..utils.validators import validate_url, validate_port, validate_stream_id
        
        # Validate input URL
        if not config.input_url or not config.input_url.strip():
            raise StreamError("Input URL cannot be empty")
        
        is_valid, error_msg = validate_url(config.input_url)
        if not is_valid:
            raise StreamError(f"Invalid input URL: {error_msg}")
        
        # Validate output configuration
        if config.output_type.value == "SRT":
            if not config.output_srt or not config.output_srt.strip():
                raise StreamError("SRT destination cannot be empty")
            
            # Parse SRT destination (format: host:port)
            if ':' in config.output_srt:
                host, port = config.output_srt.rsplit(':', 1)
                is_valid, error_msg = validate_port(port)
                if not is_valid:
                    raise StreamError(f"Invalid SRT port: {error_msg}")
            
            # Validate stream ID if provided
            if config.stream_id:
                is_valid, error_msg = validate_stream_id(config.stream_id)
                if not is_valid:
                    raise StreamError(f"Invalid stream ID: {error_msg}")
        
        # Validate marker file if provided
        if marker and marker.xml_path:
            from ..utils.validators import validate_file_path
            is_valid, error_msg = validate_file_path(str(marker.xml_path), must_exist=True)
            if not is_valid:
                raise StreamError(f"Invalid marker file: {error_msg}")
        
        try:
            # Create session
            session = StreamSession(
                session_id=str(uuid.uuid4()),
                config=config,
                marker=marker
            )
            session.status = "starting"
            session.start_time = datetime.now()
            
            self._current_session = session
            self._running = True
            
            if output_callback:
                self._output_callbacks.append(output_callback)
            
            # Determine marker path: use dynamic directory if dynamic generation is enabled
            # Dynamic generation is enabled if:
            #   1. Dynamic marker service is available
            #   2. Marker is provided
            #   3. Either inject_count > 1 OR we want continuous injection (24/7 streaming)
            # For 24/7 streaming, we always use dynamic generation to ensure incrementing event IDs
            use_dynamic_generation = (
                self.dynamic_marker_service is not None and 
                marker is not None
            )
            
            if use_dynamic_generation:
                # Start dynamic marker generation
                self.logger.info("Starting dynamic marker generation for continuous injection")
                self.dynamic_marker_service.start_generation(
                    config=config,
                    cue_type=marker.cue_type,
                    preroll_seconds=marker.preroll_seconds,
                    ad_duration_seconds=marker.ad_duration_seconds,
                    immediate=marker.immediate,
                    start_event_id=marker.event_id,  # Start with the marker's event ID
                    output_callback=output_callback
                )
                # Use dynamic markers directory instead of single file
                marker_path = self.dynamic_marker_service.get_dynamic_markers_dir()
                self.logger.info(f"Using dynamic marker directory: {marker_path}")
            else:
                # Use single marker file (traditional mode - only if dynamic service not available)
                marker_path = marker.xml_path if marker else None
                self.logger.info(f"Using single marker file: {marker_path}")
            
            # Build command
            command = self.tsduck_service.build_command(config, marker_path)
            
            self.logger.info(f"Starting stream session: {session.session_id}")
            cmd_str = ' '.join(command)
            self.logger.info(f"TSDuck command: {cmd_str}")
            self._notify_output(f"[INFO] TSDuck Command: {cmd_str}")
            
            # Start processing in background thread
            self._thread = threading.Thread(
                target=self._run_stream,
                args=(command, session),
                daemon=True
            )
            self._thread.start()
            
            # Send Telegram notification for stream start
            if self.telegram_service and self.telegram_service.enabled:
                try:
                    input_info = f"{config.input_type.value}: {config.input_url}"
                    output_info = f"{config.output_type.value}"
                    if config.output_type.value == "SRT":
                        output_info += f": {config.output_srt}"
                    marker_info = f"Marker: {marker.xml_path.name}" if marker else "No marker"
                    
                    message = f"▶️ <b>Stream Started</b>\n\n"
                    message += f"<b>Input:</b> {input_info}\n"
                    message += f"<b>Output:</b> {output_info}\n"
                    message += f"<b>{marker_info}</b>\n"
                    message += f"<b>Session ID:</b> {session.session_id[:8]}...\n"
                    message += f"\n<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
                    
                    self.telegram_service.send_message(message, disable_notification=False)
                except Exception as e:
                    self.logger.error(f"Failed to send stream start notification: {e}")
            
            return session
            
        except Exception as e:
            self.logger.error(f"Failed to start stream: {e}", exc_info=True)
            raise StreamError(f"Failed to start stream: {e}")
    
    def _run_stream(self, command: list, session: StreamSession):
        """Run stream processing in background thread"""
        max_retries = 999
        retry_count = 0
        
        while self._running and retry_count < max_retries:
            try:
                # Kill any existing processes
                self.tsduck_service.kill_all_processes()
                
                # Start process
                self._process = self.tsduck_service.execute_command(command)
                if not self._process:
                    self.logger.error("Failed to start TSDuck process")
                    session.errors_count += 1
                    retry_count += 1
                    wait_time = min(5 * min(retry_count, 6), 30)
                    for i in range(wait_time):
                        if not self._running:
                            break
                        time.sleep(1)
                    continue
                
                session.status = "running"
                
                # Send Telegram notification when stream is running
                if retry_count == 0 and self.telegram_service and self.telegram_service.enabled:
                    try:
                        message = f"🟢 <b>Stream Running</b>\n\n"
                        message += f"<b>Status:</b> Active and processing\n"
                        message += f"<b>Session ID:</b> {session.session_id[:8]}...\n"
                        if session.config:
                            message += f"<b>Input:</b> {session.config.input_url}\n"
                        message += f"\n<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
                        self.telegram_service.send_message(message, disable_notification=True)
                    except Exception as e:
                        self.logger.error(f"Failed to send stream running notification: {e}")
                
                if retry_count > 0:
                    self._notify_output(f"[INFO] Reconnected - Retry attempt {retry_count}")
                    retry_count = 0
                
                # Read output
                srt_error_detected = False
                srt_error_details = []
                
                if not self._process or not self._process.stdout:
                    self.logger.error("Process or stdout is None, cannot read output")
                    session.errors_count += 1
                    retry_count += 1
                    wait_time = min(5 * min(retry_count, 6), 30)
                    for i in range(wait_time):
                        if not self._running:
                            break
                        time.sleep(1)
                    continue
                
                try:
                    for line in self._process.stdout:
                        if not self._running:
                            break
                        
                        line_text = line.strip()
                        self._notify_output(f"[TSDuck] {line_text}")
                        
                        # Detect SRT connection errors
                        line_lower = line_text.lower()
                        if "srt" in line_lower and ("error" in line_lower or "reject" in line_lower):
                            srt_error_detected = True
                            srt_error_details.append(line_text)
                        
                        # Check for specific SRT rejection errors
                        if "connection rejected" in line_lower or "peer rejected" in line_lower:
                            srt_error_detected = True
                            self._notify_output("[SRT ERROR] Connection rejected by server")
                            self._notify_output("[SRT TIP] Check Stream ID format or try without Stream ID")
                            self._notify_output("[SRT TIP] Verify server address and port are correct")
                            self._notify_output("[SRT TIP] Ensure server is accepting connections")
                        
                        # Parse splicemonitor output for SCTE-35 marker detection
                        self._parse_splicemonitor_output(line_text, session)
                        
                        # Sync injection count from dynamic marker service (if using dynamic generation)
                        if self.dynamic_marker_service and self.dynamic_marker_service.is_running():
                            markers_generated = self.dynamic_marker_service.get_markers_generated()
                            if markers_generated > session.scte35_injected:
                                session.scte35_injected = markers_generated
                        
                        # Parse real metrics from TSDuck analyze plugin
                        self._parse_metrics_from_output(line_text, session)
                except (ValueError, AttributeError, OSError) as e:
                    self.logger.error(f"Error reading process output: {e}")
                    session.errors_count += 1
                
                # Log SRT errors if detected
                if srt_error_detected:
                    self.logger.warning(f"SRT connection error detected: {srt_error_details}")
                    session.errors_count += 1
                
                # Process finished - safely get exit code
                exit_code = -1
                if self._process:
                    try:
                        self._process.wait(timeout=1)
                        exit_code = self._process.returncode if self._process.returncode is not None else -1
                    except Exception as e:
                        self.logger.error(f"Error waiting for process: {e}")
                        exit_code = -1
                    finally:
                        self._process = None
                
                if not self._running:
                    session.status = "stopped"
                    session.stop_time = datetime.now()
                    self._notify_output("[INFO] Stream stopped by user")
                    
                    # Send Telegram notification for stream stop
                    if self.telegram_service and self.telegram_service.enabled:
                        try:
                            runtime = session.stop_time - session.start_time if session.start_time and session.stop_time else None
                            runtime_str = "N/A"
                            if runtime:
                                hours, remainder = divmod(int(runtime.total_seconds()), 3600)
                                minutes, seconds = divmod(remainder, 60)
                                if hours > 0:
                                    runtime_str = f"{hours}h {minutes}m {seconds}s"
                                elif minutes > 0:
                                    runtime_str = f"{minutes}m {seconds}s"
                                else:
                                    runtime_str = f"{seconds}s"
                            
                            message = f"⏹️ <b>Stream Stopped</b>\n\n"
                            message += f"<b>Status:</b> Stopped by user\n"
                            message += f"<b>Session ID:</b> {session.session_id[:8]}...\n"
                            message += f"<b>Runtime:</b> {runtime_str}\n"
                            message += f"<b>Packets Processed:</b> {session.packets_processed:,}\n"
                            message += f"<b>SCTE-35 Markers:</b> {session.scte35_injected}\n"
                            message += f"\n<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
                            self.telegram_service.send_message(message, disable_notification=False)
                        except Exception as e:
                            self.logger.error(f"Failed to send stream stop notification: {e}")
                    
                    break
                
                # Stream stopped unexpectedly - reconnect
                retry_count += 1
                
                # Provide specific error messages based on exit code
                if exit_code == 0:
                    self._notify_output(f"[WARNING] Stream disconnected (exit code: {exit_code}). Reconnecting in 5 seconds...")
                elif exit_code == 3221225477 or exit_code == -1073741819:
                    # SRT connection error codes
                    self._notify_output(f"[SRT ERROR] Connection rejected by server (exit code: {exit_code})")
                    self._notify_output("[SRT TROUBLESHOOTING]")
                    self._notify_output("  1. Check Stream ID format - try without '#!::' prefix")
                    self._notify_output("  2. Try leaving Stream ID empty")
                    self._notify_output("  3. Verify server address and port")
                    self._notify_output("  4. Ensure server is accepting connections")
                    self._notify_output(f"[INFO] Reconnecting in 5 seconds... (Attempt {retry_count})")
                    session.errors_count += 1
                else:
                    self._notify_output(f"[WARNING] Stream error (exit code: {exit_code}). Reconnecting in 5 seconds...")
                    session.errors_count += 1
                
                # Wait before reconnecting
                wait_time = min(5 * min(retry_count, 6), 30)
                for i in range(wait_time):
                    if not self._running:
                        break
                    time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Stream error: {e}", exc_info=True)
                session.errors_count += 1
                if not self._running:
                    break
                
                retry_count += 1
                wait_time = min(5 * min(retry_count, 6), 30)
                self._notify_output(f"[INFO] Retrying in {wait_time} seconds...")
                for i in range(wait_time):
                    if not self._running:
                        break
                    time.sleep(1)
        
        # After while loop ends, finalize session
        session.status = "stopped"
        session.stop_time = datetime.now()
        self.logger.info(f"Stream session ended: {session.session_id}")
        
        # Send Telegram notification for stream end (if not already sent)
        if self.telegram_service and self.telegram_service.enabled and session.stop_time:
            try:
                runtime = session.stop_time - session.start_time if session.start_time else None
                runtime_str = "N/A"
                if runtime:
                    hours, remainder = divmod(int(runtime.total_seconds()), 3600)
                    minutes, seconds = divmod(remainder, 60)
                    if hours > 0:
                        runtime_str = f"{hours}h {minutes}m {seconds}s"
                    elif minutes > 0:
                        runtime_str = f"{minutes}m {seconds}s"
                    else:
                        runtime_str = f"{seconds}s"
                
                message = f"⏹️ <b>Stream Ended</b>\n\n"
                message += f"<b>Status:</b> Session completed\n"
                message += f"<b>Session ID:</b> {session.session_id[:8]}...\n"
                message += f"<b>Runtime:</b> {runtime_str}\n"
                message += f"<b>Packets Processed:</b> {session.packets_processed:,}\n"
                message += f"<b>Errors:</b> {session.errors_count}\n"
                message += f"<b>SCTE-35 Markers:</b> {session.scte35_injected}\n"
                message += f"\n<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
                self.telegram_service.send_message(message, disable_notification=True)
            except Exception as e:
                self.logger.error(f"Failed to send stream end notification: {e}")
    
    def test_srt_connection(self, server: str, stream_id: str = None, timeout: int = 5) -> tuple[bool, str]:
        """
        Test SRT connection without starting full stream
        
        Args:
            server: SRT server address (e.g., "server.com:8888")
            stream_id: Optional stream ID
            timeout: Connection timeout in seconds
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Build a minimal test command
            test_command = ["tsp", "-I", "null", "-O", "srt", "--caller", server, "--latency", "2000"]
            if stream_id and stream_id.strip():
                test_command.extend(["--streamid", stream_id.strip()])
            
            self.logger.info(f"Testing SRT connection to {server}")
            
            # Run test with timeout
            process = subprocess.Popen(
                test_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                exit_code = process.returncode
                
                if exit_code == 0 or "connected" in stdout.lower() or "connected" in stderr.lower():
                    return True, "SRT connection test successful"
                else:
                    error_msg = stderr if stderr else stdout
                    if "rejected" in error_msg.lower() or "peer rejected" in error_msg.lower():
                        return False, "Connection rejected by server - check Stream ID or server configuration"
                    elif "timeout" in error_msg.lower():
                        return False, "Connection timeout - server may be unreachable"
                    else:
                        return False, f"Connection test failed: {error_msg[:200]}"
            except subprocess.TimeoutExpired:
                process.kill()
                return False, "Connection test timeout - server may not be responding"
                
        except Exception as e:
            self.logger.error(f"SRT connection test error: {e}")
            return False, f"Test failed: {str(e)}"
    
    def _notify_output(self, message: str):
        """Notify output callbacks"""
        for callback in self._output_callbacks:
            try:
                callback(message)
            except Exception as e:
                self.logger.error(f"Output callback error: {e}")
    
    def stop_stream(self, output_callback: Optional[Callable[[str], None]] = None):
        """Stop stream processing"""
        if not self._running:
            return
        
        self.logger.info("Stopping stream...")
        self._running = False
        
        # Stop dynamic marker generation if running
        if self.dynamic_marker_service and self.dynamic_marker_service.is_running():
            self.logger.info("Stopping dynamic marker generation")
            self.dynamic_marker_service.stop_generation(output_callback=output_callback)
        
        if self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=5)
            except Exception:
                try:
                    self._process.kill()
                except Exception:
                    pass
            finally:
                self._process = None
        
        # Kill all TSDuck processes
        self.tsduck_service.kill_all_processes()
        
        if self._current_session:
            self._current_session.status = "stopped"
            self._current_session.stop_time = datetime.now()
            
            # Send Telegram notification for manual stop
            if self.telegram_service and self.telegram_service.enabled:
                try:
                    session = self._current_session
                    runtime = session.stop_time - session.start_time if session.start_time and session.stop_time else None
                    runtime_str = "N/A"
                    if runtime:
                        hours, remainder = divmod(int(runtime.total_seconds()), 3600)
                        minutes, seconds = divmod(remainder, 60)
                        if hours > 0:
                            runtime_str = f"{hours}h {minutes}m {seconds}s"
                        elif minutes > 0:
                            runtime_str = f"{minutes}m {seconds}s"
                        else:
                            runtime_str = f"{seconds}s"
                    
                    message = f"⏹️ <b>Stream Stopped</b>\n\n"
                    message += f"<b>Status:</b> Stopped manually\n"
                    message += f"<b>Session ID:</b> {session.session_id[:8]}...\n"
                    message += f"<b>Runtime:</b> {runtime_str}\n"
                    message += f"<b>Packets Processed:</b> {session.packets_processed:,}\n"
                    message += f"<b>SCTE-35 Markers:</b> {session.scte35_injected}\n"
                    message += f"\n<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
                    self.telegram_service.send_message(message, disable_notification=False)
                except Exception as e:
                    self.logger.error(f"Failed to send stream stop notification: {e}")
        
        self._notify_output("[INFO] Stream stopped")
        self.logger.info("Stream stopped")
    
    def get_current_session(self) -> Optional[StreamSession]:
        """Get current stream session"""
        return self._current_session
    
    def _parse_splicemonitor_output(self, line: str, session: StreamSession):
        """Parse splicemonitor JSON output for SCTE-35 marker detection"""
        try:
            line_lower = line.lower()
            
            # Check for splicemonitor output (JSON or text format)
            # splicemonitor outputs JSON when --json flag is used
            if '{' in line and ('splice' in line_lower or 'event_id' in line_lower or 'splicemonitor' in line_lower):
                import json
                try:
                    # Try to parse as JSON
                    data = json.loads(line)
                    
                    # Check for splice_insert detection (various JSON formats)
                    if 'splice_insert' in data or 'event_id' in data or 'splice' in str(data).lower():
                        event_id = None
                        if 'splice_insert' in data:
                            splice_data = data['splice_insert']
                            event_id = splice_data.get('event_id') or splice_data.get('splice_event_id')
                        elif 'event_id' in data:
                            event_id = data['event_id']
                        elif isinstance(data, dict):
                            # Try to find event_id anywhere in the dict
                            for key, value in data.items():
                                if 'event' in key.lower() and 'id' in key.lower():
                                    event_id = value
                                    break
                        
                        # Only increment if we haven't already counted this (avoid double counting)
                        # Use dynamic marker service count if available (more accurate)
                        if self.dynamic_marker_service and self.dynamic_marker_service.is_running():
                            # Sync from dynamic service instead (more reliable)
                            markers_generated = self.dynamic_marker_service.get_markers_generated()
                            if markers_generated > session.scte35_injected:
                                session.scte35_injected = markers_generated
                        else:
                            # Fallback: increment counter
                            session.scte35_injected += 1
                        
                        self.logger.info(f"SCTE-35 marker detected by splicemonitor: Event ID={event_id}, Total={session.scte35_injected}")
                        self._notify_output(f"[SCTE-35] Marker detected: Event ID={event_id} (Total: {session.scte35_injected})")
                        
                        # Send Telegram notification if enabled
                        if self.telegram_service and self.telegram_service.enabled:
                            try:
                                # Extract more details from JSON data
                                cue_type = None
                                pts_time = None
                                break_duration = None
                                out_of_network = None
                                
                                if 'splice_insert' in data:
                                    splice_data = data['splice_insert']
                                    cue_type = splice_data.get('splice_command_type', 'Splice Insert')
                                    pts_time = splice_data.get('pts_time')
                                    break_duration = splice_data.get('break_duration')
                                    out_of_network = splice_data.get('out_of_network')
                                elif 'splice_command_type' in data:
                                    cue_type = data.get('splice_command_type')
                                
                                # Determine cue type name
                                if isinstance(cue_type, int):
                                    cue_type_map = {
                                        5: "CUE-OUT",
                                        6: "CUE-IN",
                                        7: "PREROLL"
                                    }
                                    cue_type = cue_type_map.get(cue_type, "Splice Insert")
                                
                                self.telegram_service.send_scte35_alert(
                                    event_id=int(event_id) if event_id and str(event_id).isdigit() else None,
                                    cue_type=cue_type,
                                    pts_time=int(pts_time) if pts_time else None,
                                    break_duration=int(break_duration) if break_duration else None,
                                    out_of_network=bool(out_of_network) if out_of_network is not None else None,
                                    source=session.config.input_url if session.config else None
                                )
                            except Exception as e:
                                self.logger.error(f"Failed to send Telegram notification: {e}")
                        
                except json.JSONDecodeError:
                    # Not valid JSON, might be text format
                    # Check for text patterns like "splicemonitor: splice_insert detected"
                    if 'splicemonitor' in line_lower and ('splice_insert' in line_lower or 'splice' in line_lower):
                        # Extract event ID if present
                        import re
                        event_match = re.search(r'event[_\s]*id[=:\s]+(\d+)', line_lower)
                        event_id = event_match.group(1) if event_match else "unknown"
                        
                        # Use dynamic marker service count if available (more accurate)
                        if self.dynamic_marker_service and self.dynamic_marker_service.is_running():
                            markers_generated = self.dynamic_marker_service.get_markers_generated()
                            if markers_generated > session.scte35_injected:
                                session.scte35_injected = markers_generated
                        else:
                            session.scte35_injected += 1
                        
                        self.logger.info(f"SCTE-35 marker detected by splicemonitor (text): Event ID={event_id}, Total={session.scte35_injected}")
                        self._notify_output(f"[SCTE-35] Marker detected: Event ID={event_id} (Total: {session.scte35_injected})")
                        
                        # Send Telegram notification if enabled
                        if self.telegram_service and self.telegram_service.enabled:
                            try:
                                # Try to extract cue type from text
                                cue_type = None
                                if 'cue-out' in line_lower or 'out_of_network' in line_lower:
                                    cue_type = "CUE-OUT"
                                elif 'cue-in' in line_lower:
                                    cue_type = "CUE-IN"
                                elif 'preroll' in line_lower:
                                    cue_type = "PREROLL"
                                
                                self.telegram_service.send_scte35_alert(
                                    event_id=int(event_id) if event_id and str(event_id).isdigit() else None,
                                    cue_type=cue_type,
                                    source=session.config.input_url if session.config else None
                                )
                            except Exception as e:
                                self.logger.error(f"Failed to send Telegram notification: {e}")
                        
        except Exception as e:
            # Silently ignore parsing errors to avoid spam in logs
            self.logger.debug(f"Splicemonitor parsing error (non-critical): {e}")
    
    def _parse_metrics_from_output(self, line: str, session: StreamSession):
        """Parse real metrics from TSDuck analyze plugin output"""
        import re
        try:
            line_lower = line.lower()
            
            # TSDuck analyze plugin outputs statistics in various formats
            # Look for common patterns in analyze output
            
            # Pattern 1: "Packets: 1,234,567" or "Total packets: 1234567"
            packet_match = re.search(r'(?:total\s+)?packets?[:\s]+([\d,]+)', line_lower)
            if packet_match:
                try:
                    packet_str = packet_match.group(1).replace(',', '').strip()
                    packet_count = int(packet_str)
                    # Only update if it's a new higher value (analyze reports cumulative)
                    if packet_count > session.packets_processed:
                        session.packets_processed = packet_count
                except (ValueError, AttributeError):
                    pass
            
            # Pattern 2: "Bitrate: 15.234 Mbps" or "Bitrate: 15234000 b/s"
            bitrate_match = re.search(r'bitrate[:\s]+([\d,.]+)\s*(mbps|mb/s|mb|kbps|kb/s|kb|bps|b/s)?', line_lower)
            if bitrate_match:
                try:
                    bitrate_val = float(bitrate_match.group(1).replace(',', ''))
                    unit = bitrate_match.group(2).lower() if bitrate_match.lastindex >= 2 else 'mbps'
                    # Convert to Mbps for consistency
                    if 'kbps' in unit or 'kb' in unit:
                        bitrate_val = bitrate_val / 1000
                    elif 'bps' in unit or 'b/s' in unit:
                        bitrate_val = bitrate_val / 1000000
                    # Store bitrate if we add field to session
                except (ValueError, AttributeError):
                    pass
            
            # Pattern 3: "Errors: 5" or "Continuity errors: 3"
            error_match = re.search(r'(?:continuity\s+)?errors?[:\s]+(\d+)', line_lower)
            if error_match:
                try:
                    error_count = int(error_match.group(1))
                    if error_count > 0:
                        session.errors_count = max(session.errors_count, error_count)
                except (ValueError, AttributeError):
                    pass
            
            # Pattern 4: "Packets/sec: 25,000" or "PPS: 25000"
            pps_match = re.search(r'packets?[/\s]*sec[:\s]+([\d,]+)', line_lower)
            if not pps_match:
                pps_match = re.search(r'pps[:\s]+([\d,]+)', line_lower)
            if pps_match:
                try:
                    pps_str = pps_match.group(1).replace(',', '').strip()
                    # Could store this if we add pps field to session
                except (ValueError, AttributeError):
                    pass
            
            # Pattern 5: Look for JSON format from analyze (if JSON output enabled)
            if '{' in line and 'packets' in line_lower:
                try:
                    import json
                    # Try to parse as JSON
                    json_data = json.loads(line)
                    if 'packets' in json_data:
                        packet_count = int(json_data['packets'])
                        if packet_count > session.packets_processed:
                            session.packets_processed = packet_count
                    if 'errors' in json_data:
                        error_count = int(json_data['errors'])
                        if error_count > 0:
                            session.errors_count = max(session.errors_count, error_count)
                except (json.JSONDecodeError, ValueError, KeyError):
                    pass
            
            # Fallback: If we see any indication of packet processing, increment
            # This is a backup in case analyze output format changes
            # Only increment if we haven't seen a proper packet count recently
            if any(keyword in line_lower for keyword in ['ts packet', 'transport stream', 'pid']):
                # Very conservative increment - only if no recent update
                # This prevents over-counting
                pass  # Disabled to avoid double counting
                    
        except Exception as e:
            # Silently ignore parsing errors to avoid spam in logs
            self.logger.debug(f"Metrics parsing error (non-critical): {e}")
    
    @property
    def is_running(self) -> bool:
        """Check if stream is running"""
        return self._running

