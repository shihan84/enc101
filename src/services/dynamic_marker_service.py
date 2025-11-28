"""
Dynamic SCTE-35 Marker Generation Service
Generates markers dynamically for 24/7 streaming with incrementing event IDs
"""

import threading
import time
import shutil
from pathlib import Path
from typing import Optional, Callable
from datetime import datetime
from ..core.logger import get_logger
from ..models.scte35_marker import SCTE35Marker, CueType
from ..models.stream_config import StreamConfig
from .scte35_service import SCTE35Service
from ..utils.exceptions import SCTE35Error


class DynamicMarkerService:
    """Service for dynamic SCTE-35 marker generation during streaming"""
    
    def __init__(
        self,
        scte35_service: SCTE35Service,
        dynamic_markers_dir: Optional[Path] = None,
        profile_name: Optional[str] = None
    ):
        self.logger = get_logger("DynamicMarkerService")
        self.scte35_service = scte35_service
        
        # Get profile name from SCTE35Service if not provided (sync with SCTE35Service)
        if profile_name is None:
            # Use the same profile as SCTE35Service
            self.profile_name = getattr(scte35_service, 'profile_name', 'default')
        else:
            self.profile_name = profile_name
        
        # Directory for dynamic markers (TSDuck monitors this)
        # Use scte35_final directly (no subdirectory)
        if dynamic_markers_dir:
            self.dynamic_markers_dir = Path(dynamic_markers_dir)
        else:
            # Use scte35_final directly
            self.dynamic_markers_dir = Path("scte35_final")
        
        # Convert to absolute path to ensure TSDuck can find it
        self.dynamic_markers_dir = self.dynamic_markers_dir.resolve()
        # Create directory structure
        self.dynamic_markers_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Dynamic marker service initialized")
        self.logger.info(f"Dynamic markers directory: {self.dynamic_markers_dir}")
        self.logger.info(f"TSDuck will use: {self.dynamic_markers_dir / 'splice*.xml'}")
        
        # Thread management
        self._generation_thread: Optional[threading.Thread] = None
        self._running = False
        self._stop_event = threading.Event()
        
        # Configuration
        self._current_config: Optional[StreamConfig] = None
        self._current_cue_type: CueType = CueType.PREROLL
        self._current_preroll: int = 4
        self._current_ad_duration: int = 600
        self._current_immediate: bool = True
        
        # Event ID tracking
        self._next_event_id: Optional[int] = None
        
        # Injection tracking
        self._markers_generated: int = 0  # Count of markers generated (injected)
        
        self.logger.info(f"Dynamic marker service initialized with directory: {self.dynamic_markers_dir}")
    
    def start_generation(
        self,
        config: StreamConfig,
        cue_type: CueType = CueType.PREROLL,
        preroll_seconds: int = 4,
        ad_duration_seconds: int = 600,
        immediate: bool = True,
        start_event_id: Optional[int] = None,
        output_callback: Optional[Callable[[str], None]] = None
    ):
        """
        Start dynamic marker generation
        
        Args:
            config: Stream configuration (for inject_interval)
            cue_type: Type of marker to generate
            preroll_seconds: Preroll duration
            ad_duration_seconds: Ad duration
            immediate: Whether marker is immediate
            start_event_id: Starting event ID (if None, uses next from service)
            output_callback: Callback for status messages
        """
        if self._running:
            self.logger.warning("Dynamic marker generation already running")
            return
        
        # Store configuration
        self._current_config = config
        self._current_cue_type = cue_type
        self._current_preroll = preroll_seconds
        self._current_ad_duration = ad_duration_seconds
        self._current_immediate = immediate
        
        # Determine starting event ID
        if start_event_id is not None:
            self._next_event_id = start_event_id
        else:
            # Get next event ID from service
            self._next_event_id = self.scte35_service.get_next_event_id()
        
        # Calculate interval (convert from milliseconds to seconds)
        inject_interval_ms = config.inject_interval
        interval_seconds = inject_interval_ms / 1000.0
        
        # Warn if interval is too short (less than 30 seconds)
        if interval_seconds < 30:
            self.logger.warning(f"Inject interval is very short ({interval_seconds} seconds)!")
            self.logger.warning(f"Recommended: 60 seconds (60000 ms) for standard streaming")
            self.logger.warning(f"Current: {inject_interval_ms} ms = {interval_seconds} seconds")
            if output_callback:
                output_callback(f"[WARNING] Inject interval is very short: {interval_seconds} seconds")
                output_callback(f"[WARNING] Recommended: 60 seconds (60000 ms) for standard streaming")
        
        self.logger.info(f"Starting dynamic marker generation:")
        self.logger.info(f"  Directory: {self.dynamic_markers_dir}")
        self.logger.info(f"  Interval: {interval_seconds} seconds ({inject_interval_ms} ms)")
        self.logger.info(f"  Starting Event ID: {self._next_event_id}")
        self.logger.info(f"  Cue Type: {cue_type.value}")
        
        if output_callback:
            output_callback(f"[INFO] Starting dynamic marker generation")
            output_callback(f"[INFO] Interval: {interval_seconds} seconds ({inject_interval_ms} ms)")
            output_callback(f"[INFO] Starting Event ID: {self._next_event_id}")
        
        # Clear directory (remove any old files) - but keep any files created in last 30 seconds
        # This prevents deleting files that TSDuck might be processing or about to process
        self._clear_directory(keep_recent=True, recent_seconds=30)
        
        # Reset injection counter
        self._markers_generated = 0
        
        # CRITICAL: Generate first marker BEFORE starting TSDuck
        # TSDuck needs at least one file to exist when it starts polling
        self.logger.info("Generating initial marker before starting generation thread...")
        try:
            self._generate_and_save_marker(output_callback)
            self.logger.info("Initial marker generated successfully")
            if output_callback:
                output_callback(f"[INFO] Initial marker ready for TSDuck")
        except Exception as e:
            self.logger.error(f"Failed to generate initial marker: {e}", exc_info=True)
            if output_callback:
                output_callback(f"[ERROR] Failed to generate initial marker: {e}")
        
        # Start generation thread
        self._running = True
        self._stop_event.clear()
        
        self._generation_thread = threading.Thread(
            target=self._generation_loop,
            args=(interval_seconds, output_callback),
            daemon=True,
            name="DynamicMarkerGeneration"
        )
        self._generation_thread.start()
        
        self.logger.info("Dynamic marker generation thread started")
    
    def stop_generation(self, output_callback: Optional[Callable[[str], None]] = None):
        """Stop dynamic marker generation"""
        if not self._running:
            return
        
        self.logger.info("Stopping dynamic marker generation")
        
        if output_callback:
            output_callback("[INFO] Stopping dynamic marker generation")
        
        self._running = False
        self._stop_event.set()
        
        if self._generation_thread and self._generation_thread.is_alive():
            self._generation_thread.join(timeout=5.0)
        
        # Clear directory
        self._clear_directory()
        
        self.logger.info("Dynamic marker generation stopped")
    
    def _generation_loop(self, interval_seconds: float, output_callback: Optional[Callable[[str], None]]):
        """Main generation loop running in background thread"""
        # Ensure directory is initialized and exists
        markers_dir = self.get_dynamic_markers_dir()
        self.logger.info(f"Generation loop started (interval: {interval_seconds}s)")
        self.logger.info(f"Dynamic markers directory: {markers_dir}")
        self.logger.info(f"Directory exists: {markers_dir.exists()}")
        self.logger.info(f"Current Event ID: {self._next_event_id}")
        
        if output_callback:
            output_callback(f"[INFO] Generation loop started")
            output_callback(f"[INFO] Directory: {markers_dir}")
            output_callback(f"[INFO] Interval: {interval_seconds} seconds")
            output_callback(f"[INFO] Current Event ID: {self._next_event_id}")
        
        # NOTE: First marker is already generated in start_generation() before this thread starts
        # Wait for interval before generating next marker
        marker_count = 0
        while self._running:
            # Wait for interval (or stop event)
            if self._stop_event.wait(timeout=interval_seconds):
                # Stop event was set
                break
            
            # Generate next marker
            marker_count += 1
            try:
                self.logger.info(f"Generating marker #{marker_count} (Event ID: {self._next_event_id})")
                self._generate_and_save_marker(output_callback)
                self.logger.info(f"Successfully generated marker #{marker_count}")
            except Exception as e:
                self.logger.error(f"Failed to generate marker #{marker_count}: {e}", exc_info=True)
                if output_callback:
                    output_callback(f"[ERROR] Failed to generate marker #{marker_count}: {e}")
                # Continue even if one marker fails
                continue
        
        self.logger.info(f"Generation loop stopped (generated {marker_count} markers)")
    
    def _generate_and_save_marker(self, output_callback: Optional[Callable[[str], None]]):
        """Generate a marker and save it to dynamic directory"""
        if self._next_event_id is None:
            self._next_event_id = self.scte35_service.get_next_event_id()
        
        # Get the correct directory path (ensure it's initialized)
        # CRITICAL: Always rebuild path to ensure it's correct
        # Use scte35_final directly (no subdirectory)
        markers_dir = self.get_dynamic_markers_dir()
        
        # Ensure directory exists
        markers_dir.mkdir(parents=True, exist_ok=True)
        
        # Update instance variable
        self.dynamic_markers_dir = markers_dir
        
        # For PREROLL, generate sequence: CUE-OUT, CUE-IN, CUE-CRASH
        if self._current_cue_type == CueType.PREROLL:
            self._generate_preroll_sequence(markers_dir, output_callback)
        else:
            # For other cue types, generate single marker
            event_id = self._next_event_id
            self._generate_single_marker(event_id, markers_dir, output_callback)
    
    def _generate_preroll_sequence(self, markers_dir: Path, output_callback: Optional[Callable[[str], None]]):
        """Generate preroll sequence: CUE-OUT, CUE-IN, CUE-CRASH"""
        try:
            base_event_id = self._next_event_id
            
            # Generate preroll sequence using the service method
            cue_out, cue_in, cue_crash = self.scte35_service.generate_preroll_sequence(
                base_event_id=base_event_id,
                preroll_seconds=self._current_preroll,
                ad_duration_seconds=self._current_ad_duration,
                immediate=self._current_immediate,
                auto_increment=True,
                include_crash=True  # Always include CUE-CRASH for preroll
            )
            
            # Save all three markers
            self._save_marker_file(cue_out, markers_dir, output_callback)
            self._save_marker_file(cue_in, markers_dir, output_callback)
            if cue_crash:
                self._save_marker_file(cue_crash, markers_dir, output_callback)
            
            # Update next event ID (after CUE-CRASH)
            if cue_crash:
                self._next_event_id = cue_crash.event_id + 1
            else:
                self._next_event_id = cue_in.event_id + 1
            
            self._markers_generated += 3  # Count all three markers
            self.logger.info(f"Generated preroll sequence: OUT={cue_out.event_id}, IN={cue_in.event_id}, CRASH={cue_crash.event_id if cue_crash else 'N/A'}")
            
            if output_callback:
                output_callback(f"[MARKER] Preroll sequence generated: OUT={cue_out.event_id}, IN={cue_in.event_id}, CRASH={cue_crash.event_id if cue_crash else 'N/A'}")
                
        except Exception as e:
            self.logger.error(f"Failed to generate preroll sequence: {e}", exc_info=True)
            if output_callback:
                output_callback(f"[ERROR] Failed to generate preroll sequence: {e}")
            raise
    
    def _generate_single_marker(self, event_id: int, markers_dir: Path, output_callback: Optional[Callable[[str], None]]):
        """Generate a single marker (non-preroll)"""
        # Clean up old files (only very old ones)
        self._cleanup_old_files(markers_dir)
        
        if output_callback:
            output_callback(f"[INFO] Marker directory: {markers_dir}")
        
        # Generate marker XML content directly
        xml_content = self.scte35_service._generate_xml(
            event_id=event_id,
            cue_type=self._current_cue_type,
            preroll=self._current_preroll,
            ad_duration=self._current_ad_duration,
            immediate=self._current_immediate
        )
        
        # Save marker file
        target_filename = f"splice_{event_id:05d}.xml"
        target_path = markers_dir / target_filename
        
        self._write_marker_file(target_path, xml_content, output_callback)
        
        # Update next event ID
        self._next_event_id = event_id + 1
        self._markers_generated += 1
        
        self.logger.info(f"Generated marker: {target_filename} (Event ID: {event_id})")
        if output_callback:
            output_callback(f"[MARKER] Event ID {event_id} marker created")
    
    def _cleanup_old_files(self, markers_dir: Path):
        """Clean up old marker files (only very old ones)"""
        try:
            old_files = list(markers_dir.glob("splice*.xml"))
            if old_files:
                self.logger.info(f"Found {len(old_files)} existing marker file(s) - TSDuck will process or delete them")
                # Only delete files older than 5 minutes (likely stale/unprocessed)
                import time
                current_time = time.time()
                for old_file in old_files:
                    try:
                        file_age = current_time - old_file.stat().st_mtime
                        if file_age > 300:  # 5 minutes old
                            self.logger.warning(f"Deleting stale marker file (age: {file_age:.1f}s): {old_file.name}")
                            old_file.unlink()
                        else:
                            self.logger.debug(f"Keeping marker file (age: {file_age:.1f}s): {old_file.name}")
                    except Exception as e:
                        self.logger.warning(f"Failed to check marker {old_file.name}: {e}")
        except Exception as e:
            self.logger.warning(f"Failed to check old markers: {e}")
    
    def _save_marker_file(self, marker: SCTE35Marker, markers_dir: Path, output_callback: Optional[Callable[[str], None]]):
        """Save a marker file to the dynamic directory"""
        target_filename = f"splice_{marker.event_id:05d}.xml"
        target_path = markers_dir / target_filename
        
        # Get XML content from marker
        xml_content = marker.xml_content if hasattr(marker, 'xml_content') else self.scte35_service._generate_xml(
            event_id=marker.event_id,
            cue_type=marker.cue_type,
            preroll=marker.preroll_seconds,
            ad_duration=marker.ad_duration_seconds,
            immediate=marker.immediate
        )
        
        self._write_marker_file(target_path, xml_content, output_callback)
    
    def _write_marker_file(self, target_path: Path, xml_content: str, output_callback: Optional[Callable[[str], None]]):
        """Write marker file to disk"""
        # Ensure directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Writing marker to: {target_path}")
        try:
            # Write file with explicit encoding
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(xml_content)
                f.flush()
                import os
                os.fsync(f.fileno())  # Force write to disk
            
            # Verify file was written (before TSDuck might delete it)
            if target_path.exists():
                file_size = target_path.stat().st_size
                self.logger.info(f"Marker file written: {target_path} ({file_size} bytes)")
                if file_size == 0:
                    raise SCTE35Error(f"Marker file is empty: {target_path}")
            else:
                # File might have been deleted by TSDuck immediately (expected behavior)
                self.logger.warning(f"File disappeared after write (TSDuck may have deleted it): {target_path}")
                self.logger.info(f"This is expected if TSDuck --delete-files is active")
            
            # Wait for file to be stable (TSDuck needs stable files)
            # Only wait if file still exists (TSDuck hasn't deleted it yet)
            import time
            if target_path.exists():
                time.sleep(0.6)  # 600ms - matches min-stable-delay
                # Check again after wait
                if target_path.exists():
                    self.logger.info(f"Marker file verified and stable: {target_path}")
                else:
                    self.logger.info(f"File deleted by TSDuck during stability wait: {target_path} (expected)")
            else:
                # File already deleted, just log it
                self.logger.info(f"File already deleted by TSDuck: {target_path} (expected)")
            
        except FileNotFoundError:
            # File was deleted by TSDuck - this is expected and OK
            self.logger.info(f"File deleted by TSDuck after write: {target_path} (expected with --delete-files)")
        except Exception as e:
            self.logger.error(f"Failed to write marker file: {e}", exc_info=True)
            raise SCTE35Error(f"Failed to create marker file: {target_path} - {e}")
    
    def _clear_directory(self, keep_recent: bool = False, recent_seconds: int = 10):
        """Clear files from dynamic markers directory
        
        Args:
            keep_recent: If True, keep files created in the last recent_seconds
            recent_seconds: Number of seconds to consider a file "recent"
        """
        markers_dir = self.get_dynamic_markers_dir()
        try:
            if markers_dir.exists():
                import time
                current_time = time.time()
                deleted_count = 0
                kept_count = 0
                
                for file in markers_dir.glob("splice*.xml"):
                    try:
                        file_age = current_time - file.stat().st_mtime
                        if keep_recent and file_age < recent_seconds:
                            self.logger.debug(f"Keeping recent marker file: {file.name} (age: {file_age:.1f}s)")
                            kept_count += 1
                        else:
                            file.unlink()
                            self.logger.debug(f"Cleared old marker file: {file.name} (age: {file_age:.1f}s)")
                            deleted_count += 1
                    except Exception as e:
                        self.logger.warning(f"Failed to delete {file.name}: {e}")
                
                if deleted_count > 0 or kept_count > 0:
                    self.logger.info(f"Directory cleanup: deleted {deleted_count}, kept {kept_count} recent file(s)")
        except Exception as e:
            self.logger.error(f"Failed to clear directory: {e}")
    
    def get_dynamic_markers_dir(self) -> Path:
        """Get the dynamic markers directory path (scte35_final directly)"""
        # CRITICAL: Always rebuild path from scratch to ensure it's correct
        # Use scte35_final directly (no subdirectory)
        markers_dir = Path("scte35_final").resolve()
        
        # Ensure directory exists
        markers_dir.mkdir(parents=True, exist_ok=True)
        
        # Update instance variable
        self.dynamic_markers_dir = markers_dir
        
        self.logger.debug(f"get_dynamic_markers_dir() returning: {markers_dir}")
        return markers_dir
    
    def get_profile_directory(self) -> Path:
        """Get the profile directory path (parent of dynamic_markers)"""
        # Ensure directory is initialized first
        markers_dir = self.get_dynamic_markers_dir()
        # Profile directory is the parent of dynamic_markers_dir
        profile_dir = markers_dir.parent
        profile_dir.mkdir(parents=True, exist_ok=True)
        return profile_dir
    
    def is_running(self) -> bool:
        """Check if generation is running"""
        return self._running
    
    def get_next_event_id(self) -> Optional[int]:
        """Get the next event ID that will be used"""
        return self._next_event_id
    
    def get_markers_generated(self) -> int:
        """Get the number of markers generated (injected)"""
        return self._markers_generated
    
    def set_profile(self, profile_name: str):
        """Update profile (no-op for dynamic markers - always uses general directory)"""
        # Dynamic markers always use general directory, profile doesn't affect directory
        self.profile_name = profile_name or "default"
        self.logger.debug(f"Profile updated to: {self.profile_name} (dynamic markers use general directory)")

