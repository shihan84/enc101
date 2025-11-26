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
        
        # Clear directory (remove any old files)
        self._clear_directory()
        
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
        
        if output_callback:
            output_callback(f"[INFO] Generation loop started")
            output_callback(f"[INFO] Directory: {markers_dir}")
        
        # NOTE: First marker is already generated in start_generation() before this thread starts
        # Wait for interval before generating next marker
        while self._running:
            # Wait for interval (or stop event)
            if self._stop_event.wait(timeout=interval_seconds):
                # Stop event was set
                break
            
            # Generate next marker
            try:
                self._generate_and_save_marker(output_callback)
            except Exception as e:
                self.logger.error(f"Failed to generate marker: {e}", exc_info=True)
                if output_callback:
                    output_callback(f"[ERROR] Failed to generate marker: {e}")
                # Continue even if one marker fails
                continue
        
        self.logger.info("Generation loop stopped")
    
    def _generate_and_save_marker(self, output_callback: Optional[Callable[[str], None]]):
        """Generate a marker and save it to dynamic directory"""
        if self._next_event_id is None:
            self._next_event_id = self.scte35_service.get_next_event_id()
        
        event_id = self._next_event_id
        
        # Get the correct directory path (ensure it's initialized)
        # CRITICAL: Always rebuild path to ensure it's correct
        # Use scte35_final directly (no subdirectory)
        markers_dir = self.get_dynamic_markers_dir()
        
        # Ensure directory exists
        markers_dir.mkdir(parents=True, exist_ok=True)
        
        # Update instance variable
        self.dynamic_markers_dir = markers_dir
        
        self.logger.info(f"Using markers directory: {markers_dir}")
        self.logger.info(f"Directory exists: {markers_dir.exists()}")
        self.logger.info(f"Directory is absolute: {markers_dir.is_absolute()}")
        
        if output_callback:
            output_callback(f"[INFO] Marker directory: {markers_dir}")
        
        # Generate marker XML content directly (don't create file in scte35_final)
        # Access the private method to generate XML content
        xml_content = self.scte35_service._generate_xml(
            event_id=event_id,
            cue_type=self._current_cue_type,
            preroll=self._current_preroll,
            ad_duration=self._current_ad_duration,
            immediate=self._current_immediate
        )
        
        # Save directly to dynamic directory with consistent naming
        # Use zero-padded event ID for proper ordering - TSDuck expects splice*.xml
        target_filename = f"splice_{event_id:05d}.xml"
        
        # Ensure directory exists
        markers_dir.mkdir(parents=True, exist_ok=True)
        
        target_path = markers_dir / target_filename
        
        # Write marker file directly to dynamic_markers directory
        self.logger.info(f"Writing marker directly to: {target_path}")
        try:
            # Write file with explicit encoding
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(xml_content)
                f.flush()
                import os
                os.fsync(f.fileno())  # Force write to disk
        except Exception as e:
            self.logger.error(f"Failed to write marker file: {e}", exc_info=True)
            raise SCTE35Error(f"Failed to create marker file: {target_path} - {e}")
        
        # Verify the file was written
        if not target_path.exists():
            self.logger.error(f"CRITICAL: File does not exist after write: {target_path}")
            self.logger.error(f"Parent directory: {target_path.parent}")
            self.logger.error(f"Parent exists: {target_path.parent.exists()}")
            raise SCTE35Error(f"Failed to create marker file: {target_path}")
        
        # Verify file has content
        file_size = target_path.stat().st_size
        if file_size == 0:
            self.logger.error(f"CRITICAL: File is empty: {target_path}")
            raise SCTE35Error(f"Marker file is empty: {target_path}")
        
        # Ensure file is written and stable
        # TSDuck's min-stable-delay is 500ms, and poll-interval is 500ms
        # Wait 1 second to ensure file is stable and TSDuck can detect it
        time.sleep(1.0)
        
        # Verify file exists and has content
        if not target_path.exists():
            self.logger.error(f"CRITICAL: Marker file was not created: {target_path}")
            if output_callback:
                output_callback(f"[ERROR] Marker file not created: {target_path}")
        else:
            file_size = target_path.stat().st_size
            self.logger.info(f"Marker file verified: {target_path} (size: {file_size} bytes)")
        
        # Increment event ID for next marker
        self._next_event_id = event_id + 1
        if self._next_event_id > 99999:
            self._next_event_id = 10000  # Wrap around
        
        # Save last event ID to service state
        self.scte35_service._save_last_event_id(event_id)
        
        # Increment injection counter (file generated = will be injected by TSDuck)
        self._markers_generated += 1
        
        self.logger.info(f"Generated dynamic marker: {target_filename} (Event ID: {event_id}, Total generated: {self._markers_generated})")
        self.logger.info(f"Marker saved to: {target_path}")
        self.logger.info(f"File exists: {target_path.exists()}")
        self.logger.info(f"File size: {file_size} bytes")
        self.logger.info(f"Full path: {target_path.resolve()}")
        
        if output_callback:
            output_callback(f"[SUCCESS] New marker generated: {target_filename}")
            output_callback(f"[INFO] Marker saved to: {target_path}")
            output_callback(f"[INFO] File verified: {file_size} bytes")
    
    def _clear_directory(self):
        """Clear all files from dynamic markers directory"""
        try:
            for file in self.dynamic_markers_dir.glob("*.xml"):
                try:
                    file.unlink()
                except Exception as e:
                    self.logger.warning(f"Failed to delete {file}: {e}")
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

