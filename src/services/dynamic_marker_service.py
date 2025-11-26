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
        # Use profile-specific directory if profile is provided
        if dynamic_markers_dir:
            self.dynamic_markers_dir = Path(dynamic_markers_dir)
        else:
            # Use profile-specific directory structure: scte35_final/{profile_name}/dynamic_markers/
            # This matches the SCTE35Service directory structure
            base_dir = Path("scte35_final")
            if self.profile_name and self.profile_name != "default":
                # Sanitize profile name for filesystem (same logic as SCTE35Service)
                safe_name = "".join(c for c in self.profile_name if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_name = safe_name.replace(' ', '_')
                # Create profile directory first: scte35_final/{profile_name}/
                profile_dir = base_dir / safe_name
                profile_dir.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Created profile directory: {profile_dir.resolve()}")
                # Then create dynamic_markers subdirectory: scte35_final/{profile_name}/dynamic_markers/
                self.dynamic_markers_dir = profile_dir / "dynamic_markers"
            else:
                # Default profile: scte35_final/dynamic_markers/
                self.dynamic_markers_dir = base_dir / "dynamic_markers"
        
        # Convert to absolute path to ensure TSDuck can find it
        self.dynamic_markers_dir = self.dynamic_markers_dir.resolve()
        # Create directory structure (including parent profile directory if needed)
        self.dynamic_markers_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Dynamic marker service initialized with profile: {self.profile_name}")
        self.logger.info(f"Profile directory: {self.dynamic_markers_dir.parent}")
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
        self.logger.info(f"Generation loop started (interval: {interval_seconds}s)")
        
        # Generate first marker immediately
        try:
            self._generate_and_save_marker(output_callback)
        except Exception as e:
            self.logger.error(f"Failed to generate first marker: {e}", exc_info=True)
            if output_callback:
                output_callback(f"[ERROR] Failed to generate first marker: {e}")
        
        # Wait for interval before next generation
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
        
        # Generate marker
        marker = self.scte35_service.generate_marker(
            event_id=event_id,
            cue_type=self._current_cue_type,
            preroll_seconds=self._current_preroll,
            ad_duration_seconds=self._current_ad_duration,
            immediate=self._current_immediate,
            auto_increment=False  # We manage incrementing manually
        )
        
        # Save to dynamic directory with consistent naming
        # Use zero-padded event ID for proper ordering
        target_filename = f"splice_{event_id:05d}.xml"
        
        # Ensure directory exists (profile-specific structure)
        self.dynamic_markers_dir.mkdir(parents=True, exist_ok=True)
        
        target_path = self.dynamic_markers_dir / target_filename
        
        # Copy marker file to dynamic directory (profile-specific location)
        shutil.copy(marker.xml_path, target_path)
        
        # Ensure file is written (wait for stability)
        # TSDuck's min-stable-delay is 500ms, so wait 600ms to be safe
        time.sleep(0.6)
        
        # Increment event ID for next marker
        self._next_event_id = event_id + 1
        if self._next_event_id > 99999:
            self._next_event_id = 10000  # Wrap around
        
        # Save last event ID to service state
        self.scte35_service._save_last_event_id(event_id)
        
        # Increment injection counter (file generated = will be injected by TSDuck)
        self._markers_generated += 1
        
        self.logger.info(f"Generated dynamic marker: {target_filename} (Event ID: {event_id}, Total generated: {self._markers_generated})")
        
        if output_callback:
            output_callback(f"[SCTE-35] Generated marker: Event ID={event_id} (Total: {self._markers_generated})")
    
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
        """Get the dynamic markers directory path"""
        # Re-resolve to ensure we have the absolute path with current profile
        # This is important if profile was changed after initialization
        self.dynamic_markers_dir = self.dynamic_markers_dir.resolve()
        # Ensure directory exists before returning
        self.dynamic_markers_dir.mkdir(parents=True, exist_ok=True)
        return self.dynamic_markers_dir
    
    def get_profile_directory(self) -> Path:
        """Get the profile directory path (parent of dynamic_markers)"""
        # Profile directory is the parent of dynamic_markers_dir
        profile_dir = self.dynamic_markers_dir.parent
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
        """Update profile and switch to profile-specific directory"""
        profile_name = profile_name or "default"
        
        if profile_name == self.profile_name:
            # Even if same profile, ensure directory exists and is correctly resolved
            # Re-resolve to ensure absolute path is current
            self.dynamic_markers_dir = self.dynamic_markers_dir.resolve()
            self.dynamic_markers_dir.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Profile unchanged: '{profile_name}', directory: {self.dynamic_markers_dir}")
            return  # No change needed
        
        if self._running:
            self.logger.warning("Cannot change profile while dynamic generation is running")
            return
        
        old_dir = self.dynamic_markers_dir
        old_profile = self.profile_name
        self.profile_name = profile_name
        
        self.logger.info(f"Changing profile from '{old_profile}' to '{profile_name}'")
        self.logger.info(f"Old directory: {old_dir}")
        
        # Create new profile-specific directory structure
        # This matches the SCTE35Service directory structure: scte35_final/{profile_name}/dynamic_markers/
        base_dir = Path("scte35_final")
        if profile_name and profile_name != "default":
            # Sanitize profile name for filesystem (same logic as SCTE35Service)
            safe_name = "".join(c for c in profile_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_')
            # Create profile directory structure: scte35_final/{profile_name}/dynamic_markers/
            profile_dir = base_dir / safe_name
            self.dynamic_markers_dir = profile_dir / "dynamic_markers"
            
            # Ensure profile directory exists first (scte35_final/{profile_name}/)
            profile_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created profile directory: {profile_dir.resolve()}")
        else:
            # Default profile: scte35_final/dynamic_markers/
            self.dynamic_markers_dir = base_dir / "dynamic_markers"
        
        # Convert to absolute path - CRITICAL: Must resolve to get absolute path
        self.dynamic_markers_dir = self.dynamic_markers_dir.resolve()
        # Create directory structure (including parent profile directory if needed)
        self.dynamic_markers_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"✅ Switched to profile: {self.profile_name}")
        self.logger.info(f"✅ Profile directory: {self.dynamic_markers_dir.parent}")
        self.logger.info(f"✅ Dynamic markers directory: {self.dynamic_markers_dir}")
        self.logger.info(f"✅ TSDuck will use: {self.dynamic_markers_dir / 'splice*.xml'}")
        
        # Verify the path contains the profile name
        path_str = str(self.dynamic_markers_dir).lower()
        if profile_name != "default":
            safe_name_lower = "".join(c for c in profile_name if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_').lower()
            if safe_name_lower not in path_str:
                self.logger.error(f"❌ ERROR: Profile name '{safe_name_lower}' not found in directory path!")
                self.logger.error(f"Path: {self.dynamic_markers_dir}")
                self.logger.error(f"This indicates a directory path issue!")

