"""
TSDuck Integration Service
Handles TSDuck command building, execution, and process management
"""

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
    """Service for TSDuck integration"""
    
    def __init__(self, tsduck_path: str = None):
        self.logger = get_logger("TSDuckService")
        self.tsduck_path = tsduck_path or find_tsduck()
        self.logger.info(f"TSDuck service initialized with path: {self.tsduck_path}")
    
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
        if marker_path and marker_path.exists():
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

