"""
TSDuck Integration Service
Handles TSDuck command building, execution, and process management
Supports bundled TSDuck (IBE-210) with fallback to system TSDuck
"""

import sys
import os
import subprocess
import platform
import shutil
from pathlib import Path
from typing import List, Optional, Callable
from ..core.logger import get_logger
from ..utils.helpers import find_tsduck
from ..utils.exceptions import TSDuckError
from ..models.stream_config import StreamConfig, InputType, OutputType
from ..models.scte35_marker import SCTE35Marker


class TSDuckService:
    """Service for TSDuck integration with bundled TSDuck support"""
    
    def __init__(self, tsduck_path: str = None):
        self.logger = get_logger("TSDuckService")
        
        if tsduck_path:
            # User-specified path takes priority
            self.tsduck_path = tsduck_path
            self.tsduck_source = "user-specified"
        else:
            # Try bundled TSDuck first (IBE-210 feature - no separate installation needed)
            bundled_path = self._get_bundled_tsduck_path()
            if bundled_path and Path(bundled_path).exists():
                self.tsduck_path = bundled_path
                self.tsduck_source = "bundled"
                self.logger.info(f"Using bundled TSDuck: {self.tsduck_path}")
                # Set up environment for bundled TSDuck
                self._setup_bundled_tsduck_environment()
            else:
                # Fallback to installed TSDuck (C:\Program Files\TSDuck)
                installed_path = self._get_installed_tsduck_path()
                if installed_path and Path(installed_path).exists():
                    self.tsduck_path = installed_path
                    self.tsduck_source = "installed"
                    self.logger.info(f"Using installed TSDuck: {self.tsduck_path}")
                else:
                    # Final fallback to system TSDuck (from PATH)
                    self.tsduck_path = find_tsduck()
                    self.tsduck_source = "system"
                    self.logger.info(f"Using system TSDuck: {self.tsduck_path}")
        
        self.logger.info(f"TSDuck service initialized (source: {self.tsduck_source})")
    
    def _get_installed_tsduck_path(self) -> Optional[str]:
        """
        Get path to installed TSDuck executable (C:\\Program Files\\TSDuck)
        Returns None if installed TSDuck is not found
        """
        # Check standard Windows installation path
        installed_paths = [
            Path(r"C:\Program Files\TSDuck\bin\tsp.exe"),
            Path(r"C:\Program Files (x86)\TSDuck\bin\tsp.exe"),
        ]
        
        for path in installed_paths:
            if path.exists():
                self.logger.info(f"Found installed TSDuck at: {path}")
                return str(path)
        
        return None
    
    def _get_bundled_tsduck_path(self) -> Optional[str]:
        """
        Get path to bundled TSDuck executable
        Returns None if bundled TSDuck is not found
        Optimized to check most likely paths first
        """
        if getattr(sys, 'frozen', False):
            # PyInstaller bundled mode
            base_path = Path(sys._MEIPASS)
        else:
            # Development mode
            base_path = Path(__file__).parent.parent.parent
        
        # Try most likely locations first (optimized order)
        # Check current directory structure first
        most_likely = base_path / "tsduck" / "bin" / "tsp.exe"
        if most_likely.exists():
            return str(most_likely)
        
        # Check Linux/macOS version
        most_likely_linux = base_path / "tsduck" / "bin" / "tsp"
        if most_likely_linux.exists():
            return str(most_likely_linux)
        
        # Only check other paths if first didn't work
        other_paths = [
            base_path.parent / "tsduck" / "bin" / "tsp.exe",
            base_path.parent / "tsduck" / "bin" / "tsp",
        ]
        
        for path in other_paths:
            if path.exists():
                return str(path)
        
        return None
    
    def _setup_bundled_tsduck_environment(self):
        """Set up environment variables for bundled TSDuck"""
        try:
            if getattr(sys, 'frozen', False):
                base_path = Path(sys._MEIPASS)
            else:
                base_path = Path(__file__).parent.parent.parent
            
            tsduck_base = base_path / "tsduck"
            plugin_path = tsduck_base / "plugins"
            
            if plugin_path.exists():
                # Add plugin path to PATH
                current_path = os.environ.get('PATH', '')
                plugin_path_str = str(plugin_path)
                
                # Only add if not already in PATH
                if plugin_path_str not in current_path:
                    os.environ['PATH'] = f"{plugin_path_str}{os.pathsep}{current_path}"
                    self.logger.debug(f"Added TSDuck plugin path to PATH: {plugin_path_str}")
                
                # Set TSDuck-specific environment variable (if TSDuck uses it)
                os.environ['TSDUCK_PLUGIN_PATH'] = str(plugin_path)
                self.logger.debug(f"Set TSDUCK_PLUGIN_PATH: {plugin_path_str}")
        except Exception as e:
            self.logger.warning(f"Failed to set up bundled TSDuck environment: {e}")
    
    def verify_installation(self) -> bool:
        """Verify TSDuck installation"""
        try:
            result = subprocess.run(
                [self.tsduck_path, "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            if result.returncode == 0:
                self.logger.info("TSDuck installation verified")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to verify TSDuck: {e}")
            return False
    
    def build_command(
        self,
        config: StreamConfig,
        marker_path: Optional[Path] = None,
        verbose: bool = False
    ) -> List[str]:
        """
        Build TSDuck command from configuration
        Based on official TSDuck documentation:
        - https://tsduck.io/docs/tsduck.html#srt-input
        - https://tsduck.io/docs/tsduck.html#_srt_output
        - https://tsduck.io/docs/tsduck.html#spliceinject-ref
        - https://tsduck.io/docs/tsduck.html#_pmt
        
        Args:
            config: Stream configuration
            marker_path: Path to SCTE-35 marker XML file or directory
            verbose: Enable verbose logging
        
        Returns:
            List of command arguments
        """
        command = [self.tsduck_path]
        
        # Add verbose flag if requested
        if verbose:
            command.append("--verbose")
        
        # Add input stuffing (adds null packets for proper stream structure)
        # Per TSDuck sample: --add-input-stuffing 1/10 (1 null packet every 10 packets)
        # This helps with PTS extraction and stream structure
        command.extend(["--add-input-stuffing", "1/10"])
        
        # ============================================
        # INPUT PLUGIN
        # ============================================
        # Official TSDuck SRT input syntax:
        # -I srt <host:port> [options]
        # Options: --transtype, --latency, --streamid
        if config.input_type == InputType.SRT:
            # Parse SRT URL: srt://host:port?streamid=xxx or host:port
            clean_url = config.input_url.replace("srt://", "").replace("srt:", "")
            host_port = clean_url
            streamid_param = None
            
            if "?" in clean_url:
                host_port = clean_url.split("?")[0]
                query_part = clean_url.split("?")[1]
                if "streamid=" in query_part:
                    streamid_param = query_part.split("streamid=")[1].split("&")[0]
            
            # SRT input: --transtype live, --latency 2000ms (per distributor requirements)
            command.extend(["-I", "srt", host_port,
                          "--transtype", "live",
                          "--latency", "2000"])
            
            if streamid_param:
                command.extend(["--streamid", streamid_param])
        else:
            # Other input types
            input_plugin_map = {
                InputType.HLS: "hls",
                InputType.UDP: "ip",
                InputType.TCP: "tcp",
                InputType.HTTP: "http",
                InputType.DVB: "dvb",
                InputType.ASI: "asi"
            }
            input_plugin = input_plugin_map.get(config.input_type, "hls")
            command.extend(["-I", input_plugin, config.input_url])
        
        # ============================================
        # SDT PLUGIN - Service Description Table
        # ============================================
        command.extend(["-P", "sdt",
            "--service", str(config.service_id),
            "--name", config.service_name,
            "--provider", config.provider_name])
        
        # ============================================
        # REMAP PLUGIN - PID Remapping
        # ============================================
        # Smart PID Remapping: Only remap if needed to avoid conflicts
        # - Skip remapping for SRT input (stream PIDs are already correct)
        # - Skip remapping if source PID matches target PID (no remap needed)
        # - Skip remapping if target PID is already in stream (would cause conflict)
        remap_rules = []
        
        # Skip remapping for SRT input - stream PIDs are already correct
        if config.input_type != InputType.SRT:
            # Video PID remapping: only if 211 != target vpid
            # This prevents remapping 211->256 if stream already has 256
            if 211 != config.vpid:
                remap_rules.append(f"211={config.vpid}")  # Video: 211 -> vpid
            
            # Audio PID remapping: only if 221 != target apid
            # This prevents remapping 221->257 if stream already has 257
            if 221 != config.apid:
                remap_rules.append(f"221={config.apid}")  # Audio: 221 -> apid
        
        # Only add remap plugin if we have remapping rules
        if remap_rules:
            command.extend(["-P", "remap"] + remap_rules)
            self.logger.info(f"PID Remapping: {', '.join(remap_rules)}")
        else:
            if config.input_type == InputType.SRT:
                self.logger.info(f"PID Remapping skipped: SRT input uses stream PIDs directly (vpid={config.vpid}, apid={config.apid})")
            else:
                self.logger.info(f"PID Remapping skipped: Stream already has target PIDs (vpid={config.vpid}, apid={config.apid})")
        
        # ============================================
        # PMT PLUGIN - Program Map Table
        # ============================================
        # Per TSDuck documentation and distributor requirements:
        # - Add CUE identifier descriptor (0x43554549 = "CUEI") for SCTE-35 detection
        # - Add video PID (0x1b = H.264)
        # - Add audio PID (0x0f = AAC)
        # - Add SCTE-35 PID (0x86 = splice_info_section)
        command.extend(["-P", "pmt",
            "--service", str(config.service_id),
            "--add-programinfo-id", "0x43554549",  # CUE identifier descriptor
            "--add-pid", f"{config.vpid}/0x1b",  # Video: H.264
            "--add-pid", f"{config.apid}/0x0f",  # Audio: AAC
            "--add-pid", f"{config.scte35_pid}/0x86"])  # SCTE-35: splice_info_section
        
        self.logger.info(f"PMT: Service {config.service_id}, CUE-ID=0x43554549, Video={config.vpid}/0x1b, Audio={config.apid}/0x0f, SCTE-35={config.scte35_pid}/0x86")
        
        # ============================================
        # SPLICEINJECT PLUGIN - SCTE-35 Injection
        # ============================================
        # Per official TSDuck documentation:
        # - Use --service instead of --pid (GitHub issue #1578)
        # - --pts-pid: PID to extract PTS from (video PID after remapping)
        # - For continuous injection: Use wildcard pattern with polling
        # - --files: Wildcard pattern for dynamic file loading
        # - --delete-files: Delete files after injection (recommended for dynamic generation)
        # - --poll-interval: Interval between poll operations (default: 500ms)
        # - --min-stable-delay: File must be stable before loading (default: 500ms)
        # - --inject-count: Number of times to inject same section (use 1 for continuous injection)
        if marker_path:
            # Handle directory (dynamic generation) or single file
            if marker_path.is_dir():
                # Dynamic generation mode: Use wildcard pattern with polling
                # This allows TSDuck to continuously monitor and inject new files as they're created
                wildcard_pattern = str(marker_path / "splice*.xml")
                
                self.logger.info(f"SpliceInject: Dynamic mode - using wildcard pattern: {wildcard_pattern}")
                self.logger.info(f"SpliceInject: TSDuck will poll for new files and inject each once")
                
                # Build spliceinject command with wildcard pattern and polling
                command.extend(["-P", "spliceinject",
                    "--service", str(config.service_id),
                    "--pts-pid", str(config.vpid),  # Use remapped video PID (256)
                    "--files", wildcard_pattern,
                    "--delete-files",  # Delete files after successful injection (prevents directory bloat)
                    "--poll-interval", "500",  # Poll every 500ms for new files
                    "--min-stable-delay", "500",  # File must be stable for 500ms before loading
                    "--inject-count", "1"])  # Each file injected once (for continuous injection with incrementing event IDs)
                
                self.logger.info(f"SpliceInject: Service={config.service_id}, PTS-PID={config.vpid}")
                self.logger.info(f"SpliceInject: Wildcard={wildcard_pattern}, Poll=500ms, Stable=500ms, Count=1")
                self.logger.info(f"SpliceInject: Files will be deleted after injection (dynamic generation mode)")
                
            else:
                # Single file mode: Traditional injection (for testing or one-time injection)
                if marker_path.exists():
                    # Determine injection mode (immediate vs scheduled)
                    is_immediate = False
                    has_pts_time = False
                    try:
                        marker_content = marker_path.read_text(encoding='utf-8')
                        is_immediate = 'splice_immediate="true"' in marker_content
                        has_pts_time = 'pts_time=' in marker_content and 'pts_time="0"' not in marker_content
                    except Exception as e:
                        self.logger.warning(f"Could not read marker file to determine injection mode: {e}")
                    
                    # Build spliceinject command for single file
                    command.extend(["-P", "spliceinject",
                        "--service", str(config.service_id),
                        "--pts-pid", str(config.vpid),  # Use remapped video PID (256)
                        "--files", str(marker_path),
                        "--inject-count", str(config.inject_count),
                        "--inject-interval", str(config.inject_interval)])
                    
                    # Add --start-delay for scheduled injection (when pts_time is present)
                    if has_pts_time:
                        start_delay = getattr(config, 'start_delay', 2000)
                        command.extend(["--start-delay", str(start_delay)])
                        self.logger.info(f"SpliceInject: Scheduled mode (pts_time present), start-delay={start_delay}ms")
                    elif is_immediate:
                        self.logger.info(f"SpliceInject: Immediate mode (splice_immediate=true)")
                    else:
                        # Default: add start-delay for safety
                        start_delay = getattr(config, 'start_delay', 2000)
                        command.extend(["--start-delay", str(start_delay)])
                        self.logger.info(f"SpliceInject: Default mode, start-delay={start_delay}ms")
                    
                    self.logger.info(f"SpliceInject: Single file mode - File={marker_path.name}, Count={config.inject_count}, Interval={config.inject_interval}ms")
                else:
                    self.logger.warning(f"Marker file does not exist: {marker_path}")
            
            # Add splicemonitor plugin (for testing - detects SCTE-35 injection)
            # ============================================
            # SPLICEMONITOR PLUGIN - SCTE-35 Detection
            # ============================================
            # Per TSDuck documentation: Monitors and reports SCTE-35 splice information
            # This is added for testing purposes to verify SCTE-35 injection and bitrate
            command.extend(["-P", "splicemonitor", "--json"])
            self.logger.info("SpliceMonitor: Added for testing - SCTE-35 detection and bitrate monitoring")
            
            # Add splicerestamp plugin (for both modes)
            # ============================================
            # SPLICERESTAMP PLUGIN - PTS/PCR Adjustment
            # ============================================
            # Per TSDuck documentation: Adjusts PCR/PTS values for proper SCTE-35 timing
            command.extend(["-P", "splicerestamp"])
            self.logger.info("SpliceRestamp: Added for PTS/PCR synchronization")
        
        # ============================================
        # OUTPUT PLUGIN
        # ============================================
        # Official TSDuck SRT output syntax:
        # -O srt --caller <host:port> [options]  (caller mode)
        # -O srt --listener <port> [options]     (listener mode)
        # Options: --latency, --streamid
        if config.output_type == OutputType.SRT:
            # Parse output SRT URL
            output_host_port = config.output_srt
            output_streamid = config.stream_id
            
            if "srt://" in output_host_port or "?" in output_host_port:
                clean_output = output_host_port.replace("srt://", "").replace("srt:", "")
                if "?" in clean_output:
                    output_host_port = clean_output.split("?")[0]
                    query_part = clean_output.split("?")[1]
                    if "streamid=" in query_part:
                        output_streamid = query_part.split("streamid=")[1].split("&")[0]
                        if "%" in output_streamid:
                            import urllib.parse
                            output_streamid = urllib.parse.unquote(output_streamid)
            
            # Detect listener mode (port only) vs caller mode (host:port)
            # If output_host_port is just a number, use listener mode
            # Otherwise, use caller mode
            try:
                port_only = int(output_host_port)
                # Listener mode: just port number
                output_args = ["-O", "srt", "--listener", str(port_only),
                              "--latency", str(config.latency)]
                self.logger.info(f"SRT output: Listener mode on port {port_only}")
            except ValueError:
                # Caller mode: host:port
                output_args = ["-O", "srt", "--caller", output_host_port,
                              "--latency", str(config.latency)]
                self.logger.info(f"SRT output: Caller mode to {output_host_port}")
            
            if output_streamid and output_streamid.strip():
                output_args.extend(["--streamid", output_streamid.strip()])
            
            command.extend(output_args)
        elif config.output_type == OutputType.HLS:
            command.extend(["-O", "hls", "--live", config.output_hls,
                          "--segment-duration", str(config.segment_duration),
                          "--playlist-window", str(config.playlist_window)])
            if config.enable_cors:
                command.extend(["--cors", "*"])
        elif config.output_type == OutputType.DASH:
            command.extend(["-O", "hls", "--live", config.output_dash,
                          "--dash",
                          "--segment-duration", str(config.segment_duration),
                          "--playlist-window", str(config.playlist_window)])
            if config.enable_cors:
                command.extend(["--cors", "*"])
        elif config.output_type == OutputType.UDP:
            command.extend(["-O", "ip", config.output_srt])
        elif config.output_type == OutputType.FILE:
            output_file = getattr(config, 'output_file', 'output.ts')
            command.extend(["-O", "file", output_file])
            self.logger.info(f"Output: File to {output_file}")
        elif config.output_type == OutputType.TCP:
            command.extend(["-O", "tcp", config.output_srt])
        elif config.output_type == OutputType.HTTP:
            command.extend(["-O", "http", config.output_srt])
            if config.enable_cors:
                command.extend(["--cors", "*"])
        else:
            command.extend(["-O", "file", config.output_srt])
        
        return command
    
    def kill_all_processes(self) -> int:
        """Kill all TSDuck processes"""
        killed_count = 0
        
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["taskkill", "/F", "/IM", "tsp.exe"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )
                
                if "SUCCESS" in result.stdout or "terminated" in result.stdout.lower():
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if "terminated" in line.lower():
                            killed_count += 1
                
                # PowerShell backup method
                try:
                    subprocess.run(
                        ["powershell", "-Command", "Get-Process | Where-Object {$_.ProcessName -like '*tsp*'} | Stop-Process -Force"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=5,
                        creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                    )
                except Exception:
                    pass
            
            if killed_count > 0:
                self.logger.info(f"Killed {killed_count} TSDuck process(es)")
            
            return killed_count
        except Exception as e:
            self.logger.error(f"Error killing TSDuck processes: {e}")
            return 0
    
    def execute_command(
        self,
        command: List[str],
        output_callback: Optional[Callable[[str], None]] = None,
        error_callback: Optional[Callable[[str], None]] = None
    ) -> subprocess.Popen:
        """
        Execute TSDuck command
        
        Args:
            command: TSDuck command arguments
            output_callback: Callback for stdout lines
            error_callback: Callback for stderr lines
        
        Returns:
            Process object
        """
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            self.logger.info(f"TSDuck process started: PID {process.pid}")
            
            # Start reading output in background (would need threading in real implementation)
            # For now, return the process
            
            return process
        except Exception as e:
            self.logger.error(f"Failed to execute TSDuck command: {e}", exc_info=True)
            raise TSDuckError(f"Failed to execute TSDuck: {e}")

