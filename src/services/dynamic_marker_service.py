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
        dynamic_markers_dir: Optional[Path] = None
    ):
        self.logger = get_logger("DynamicMarkerService")
        self.scte35_service = scte35_service
        
        # Directory for dynamic markers (TSDuck monitors this)
        if dynamic_markers_dir:
            self.dynamic_markers_dir = dynamic_markers_dir
        else:
            self.dynamic_markers_dir = Path("scte35_final/dynamic_markers")
        
        self.dynamic_markers_dir.mkdir(parents=True, exist_ok=True)
        
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
        
        self.logger.info(f"Starting dynamic marker generation:")
        self.logger.info(f"  Directory: {self.dynamic_markers_dir}")
        self.logger.info(f"  Interval: {interval_seconds} seconds")
        self.logger.info(f"  Starting Event ID: {self._next_event_id}")
        self.logger.info(f"  Cue Type: {cue_type.value}")
        
        if output_callback:
            output_callback(f"[INFO] Starting dynamic marker generation")
            output_callback(f"[INFO] Interval: {interval_seconds} seconds")
            output_callback(f"[INFO] Starting Event ID: {self._next_event_id}")
        
        # Clear directory (remove any old files)
        self._clear_directory()
        
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
        target_path = self.dynamic_markers_dir / target_filename
        
        # Copy marker file to dynamic directory
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
        
        self.logger.info(f"Generated dynamic marker: {target_filename} (Event ID: {event_id})")
        
        if output_callback:
            output_callback(f"[SCTE-35] Generated marker: Event ID={event_id}")
    
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
        return self.dynamic_markers_dir
    
    def is_running(self) -> bool:
        """Check if generation is running"""
        return self._running
    
    def get_next_event_id(self) -> Optional[int]:
        """Get the next event ID that will be used"""
        return self._next_event_id

