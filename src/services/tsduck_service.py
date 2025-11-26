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
            # Try bundled TSDuck first (IBE-210 feature)
            bundled_path = self._get_bundled_tsduck_path()
            if bundled_path and Path(bundled_path).exists():
                self.tsduck_path = bundled_path
                self.tsduck_source = "bundled"
                self.logger.info(f"Using bundled TSDuck: {self.tsduck_path}")
                # Set up environment for bundled TSDuck
                self._setup_bundled_tsduck_environment()
            else:
                # Fallback to system TSDuck
                self.tsduck_path = find_tsduck()
                self.tsduck_source = "system"
                self.logger.info(f"Using system TSDuck: {self.tsduck_path}")
        
        self.logger.info(f"TSDuck service initialized (source: {self.tsduck_source})")
    
    def _get_bundled_tsduck_path(self) -> Optional[str]:
        """
        Get path to bundled TSDuck executable
        Returns None if bundled TSDuck is not found
        """
        if getattr(sys, 'frozen', False):
            # PyInstaller bundled mode
            base_path = Path(sys._MEIPASS)
        else:
            # Development mode
            base_path = Path(__file__).parent.parent.parent
        
        # Try different possible locations
        possible_paths = [
            base_path / "tsduck" / "bin" / "tsp.exe",  # Windows
            base_path / "tsduck" / "bin" / "tsp",      # Linux/macOS
            base_path.parent / "tsduck" / "bin" / "tsp.exe",
            base_path.parent / "tsduck" / "bin" / "tsp",
            # Also check in dist folder (for development)
            base_path.parent.parent / "tsduck" / "bin" / "tsp.exe",
            base_path.parent.parent / "tsduck" / "bin" / "tsp",
        ]
        
        for path in possible_paths:
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
        marker_path: Optional[Path] = None
    ) -> List[str]:
        """
        Build TSDuck command from configuration
        
        Args:
            config: Stream configuration
            marker_path: Path to SCTE-35 marker XML file
        
        Returns:
            List of command arguments
        """
        command = [self.tsduck_path]
        
        # Input plugin
        input_plugin_map = {
            InputType.HLS: "hls",
            InputType.SRT: "srt",
            InputType.UDP: "ip",
            InputType.TCP: "tcp",
            InputType.HTTP: "http",
            InputType.DVB: "dvb",
            InputType.ASI: "asi"
        }
        
        input_plugin = input_plugin_map.get(config.input_type, "hls")
        
        # Handle SRT input specially
        if config.input_type == InputType.SRT:
            clean_url = config.input_url.replace("srt://", "").replace("srt:", "")
            if "?" in clean_url:
                host_port = clean_url.split("?")[0]
                query_part = clean_url.split("?")[1]
                streamid_param = None
                if "streamid=" in query_part:
                    streamid_param = query_part.split("streamid=")[1]
                
                command.extend(["-I", "srt", host_port,
                              "--transtype", "live",
                              "--messageapi",
                              "--latency", "2000"])
                if streamid_param:
                    command.extend(["--streamid", streamid_param])
            else:
                command.extend(["-I", "srt", clean_url,
                              "--transtype", "live",
                              "--messageapi",
                              "--latency", "2000"])
        else:
            command.extend(["-I", input_plugin, config.input_url])
        
        # SDT Plugin - Service Description Table
        command.extend(["-P", "sdt",
            "--service", str(config.service_id),
            "--name", config.service_name,
            "--provider", config.provider_name])
        
        # Smart PID Remapping (skip for SRT input)
        if config.input_type != InputType.SRT:
            command.extend(["-P", "remap", f"211={config.vpid}", f"221={config.apid}"])
        
        # PMT Plugin - Program Map Table
        command.extend(["-P", "pmt",
            "--service", str(config.service_id),
            "--add-pid", f"{config.vpid}/0x1b",  # Video PID
            "--add-pid", f"{config.apid}/0x0f",  # Audio PID
            "--add-pid", f"{config.scte35_pid}/0x86"])  # SCTE-35 PID
        
        # SpliceInject Plugin (if marker provided)
        if marker_path:
            # Check if marker_path is a directory (for dynamic generation) or a file
            if marker_path.is_dir():
                # Dynamic marker generation mode: use wildcard pattern
                # Convert to absolute path to ensure TSDuck can find it
                abs_marker_path = marker_path.resolve()
                wildcard_pattern = str(abs_marker_path / "splice*.xml")
                self.logger.info(f"Using absolute path for dynamic markers: {wildcard_pattern}")
                command.extend(["-P", "spliceinject",
                    "--pid", str(config.scte35_pid),
                    "--pts-pid", str(config.vpid),
                    "--files", wildcard_pattern,
                    "--delete-files",  # Delete files after injection
                    "--poll-interval", "500",  # Poll every 500ms (default)
                    "--inject-count", "1"])  # Each file injected once
            elif marker_path.exists():
                # Single file mode: traditional injection
                command.extend(["-P", "spliceinject",
                    "--pid", str(config.scte35_pid),
                    "--pts-pid", str(config.vpid),
                    "--files", str(marker_path),
                    "--inject-count", str(config.inject_count),
                    "--inject-interval", str(config.inject_interval),
                    "--start-delay", str(config.start_delay)])
            
            # SpliceMonitor Plugin - detect injected markers (after spliceinject, before analyze)
            # This verifies that markers are actually in the stream before sending to distributor
            # Note: splicemonitor doesn't need --pid, it automatically monitors all SCTE-35 splice information
            command.extend(["-P", "splicemonitor",
                "--json"])  # JSON format for easier parsing
        
        # Analyze Plugin - for real-time metrics (add before output)
        # Outputs statistics every 1 second for real-time monitoring
        command.extend(["-P", "analyze", "--interval", "1"])
        
        # Output plugin
        if config.output_type == OutputType.SRT:
            output_args = ["-O", "srt", "--caller", config.output_srt, "--latency", str(config.latency)]
            # Only add streamid if it's not empty (match old version behavior)
            if config.stream_id and config.stream_id.strip():
                output_args.extend(["--streamid", config.stream_id.strip()])
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
        elif config.output_type == OutputType.TCP:
            command.extend(["-O", "tcp", config.output_srt])
        elif config.output_type == OutputType.HTTP:
            command.extend(["-O", "http", config.output_srt])
            if config.enable_cors:
                command.extend(["--cors", "*"])
        else:  # FILE
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

