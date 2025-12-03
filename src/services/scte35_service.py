"""
SCTE-35 Marker Generation Service
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple
from ..core.logger import get_logger
from ..models.scte35_marker import SCTE35Marker, CueType
from ..utils.exceptions import SCTE35Error


class SCTE35Service:
    """Service for SCTE-35 marker generation and management"""
    
    def __init__(self, markers_dir: Path = None, profile_name: str = None):
        self.logger = get_logger("SCTE35Service")
        self.profile_name = profile_name or "default"
        
        # Profile-specific directory structure
        if markers_dir:
            self.markers_dir = markers_dir
        else:
            base_dir = Path("scte35_final")
            # Create profile-specific subdirectory
            if profile_name and profile_name != "default":
                # Sanitize profile name for filesystem
                safe_name = "".join(c for c in profile_name if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_name = safe_name.replace(' ', '_')
                self.markers_dir = base_dir / safe_name
            else:
                self.markers_dir = base_dir
        
        self.markers_dir.mkdir(parents=True, exist_ok=True)
        
        # Event ID state file for tracking last used ID (profile-specific)
        self.state_file = self.markers_dir / ".scte35_state.json"
        self._last_event_id = self._load_last_event_id()
        
        self.logger.info(f"SCTE-35 service initialized with directory: {self.markers_dir}")
        self.logger.info(f"Profile: {self.profile_name}")
        self.logger.info(f"Last event ID: {self._last_event_id}")
    
    def set_profile(self, profile_name: str):
        """Update profile and switch to profile-specific directory"""
        if profile_name == self.profile_name:
            return  # No change needed
        
        old_dir = self.markers_dir
        self.profile_name = profile_name or "default"
        
        # Create new profile-specific directory
        base_dir = Path("scte35_final")
        if profile_name and profile_name != "default":
            safe_name = "".join(c for c in profile_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_')
            self.markers_dir = base_dir / safe_name
        else:
            self.markers_dir = base_dir
        
        self.markers_dir.mkdir(parents=True, exist_ok=True)
        
        # Update state file path
        self.state_file = self.markers_dir / ".scte35_state.json"
        self._last_event_id = self._load_last_event_id()
        
        self.logger.info(f"Switched to profile: {self.profile_name}")
        self.logger.info(f"New markers directory: {self.markers_dir}")
        self.logger.info(f"Last event ID for this profile: {self._last_event_id}")
    
    def _load_last_event_id(self) -> int:
        """Load the last used event ID from state file"""
        try:
            if self.state_file.exists():
                data = json.loads(self.state_file.read_text(encoding='utf-8'))
                return data.get('last_event_id', 10023)
        except Exception as e:
            self.logger.warning(f"Failed to load event ID state: {e}")
        return 10023  # Default starting ID
    
    def _save_last_event_id(self, event_id: int):
        """Save the last used event ID to state file"""
        try:
            data = {'last_event_id': event_id}
            self.state_file.write_text(json.dumps(data, indent=2), encoding='utf-8')
            self._last_event_id = event_id
        except Exception as e:
            self.logger.error(f"Failed to save event ID state: {e}")
    
    def get_next_event_id(self) -> int:
        """Get the next available event ID (incremental)"""
        next_id = self._last_event_id + 1
        # Ensure ID is within valid range (10000-99999)
        if next_id > 99999:
            next_id = 10000
        return next_id
    
    def generate_marker(
        self,
        event_id: Optional[int] = None,
        cue_type: CueType = CueType.PREROLL,
        preroll_seconds: int = 4,  # Industry standard minimum: 4.0 seconds
        ad_duration_seconds: int = 600,
        schedule_time: Optional[str] = None,
        immediate: bool = True,
        auto_increment: bool = True
    ) -> SCTE35Marker:
        """
        Generate SCTE-35 marker
        
        Args:
            event_id: Event ID (if None and auto_increment=True, uses next available ID)
            auto_increment: If True, automatically increments event ID
        
        Returns:
            SCTE35Marker object with file paths
        """
        # Input validation
        from ..utils.validators import validate_event_id, validate_duration, validate_numeric_range
        
        # Validate event ID if provided
        if event_id is not None:
            is_valid, error_msg = validate_event_id(event_id)
            if not is_valid:
                raise SCTE35Error(f"Invalid event ID: {error_msg}")
        
        # Validate preroll seconds
        is_valid, error_msg = validate_duration(preroll_seconds, min_val=0, max_val=10)
        if not is_valid:
            raise SCTE35Error(f"Invalid preroll duration: {error_msg}")
        
        # Validate ad duration
        is_valid, error_msg = validate_duration(ad_duration_seconds, min_val=0, max_val=86400)
        if not is_valid:
            raise SCTE35Error(f"Invalid ad duration: {error_msg}")
        
        try:
            # Auto-increment event ID if requested
            if auto_increment and event_id is None:
                event_id = self.get_next_event_id()
            elif event_id is None:
                event_id = 10023  # Default fallback
            
            # Save the event ID as last used
            if auto_increment:
                self._save_last_event_id(event_id)
            
            # Generate timestamped filename
            timestamp = int(datetime.now().timestamp())
            cue_prefix_map = {
                CueType.PREROLL: "preroll",
                CueType.CUE_OUT: "cue_out",
                CueType.CUE_IN: "cue_in",
                CueType.CUE_CRASH: "cue_crash",
                CueType.TIME_SIGNAL: "time_signal"
            }
            cue_prefix = cue_prefix_map.get(cue_type, "preroll")
            
            xml_filename = f"{cue_prefix}_{event_id}_{timestamp}.xml"
            json_filename = f"{cue_prefix}_{event_id}_{timestamp}.json"
            
            xml_path = self.markers_dir / xml_filename
            json_path = self.markers_dir / json_filename
            
            # Generate XML content based on cue type
            xml_content = self._generate_xml(
                event_id, cue_type, preroll_seconds, ad_duration_seconds, immediate
            )
            
            # Generate JSON metadata
            json_data = {
                "scte35_marker": {
                    "event_id": event_id,
                    "cue_type": cue_type.value,
                    "preroll_seconds": preroll_seconds,
                    "ad_duration_seconds": ad_duration_seconds,
                    "schedule_time": schedule_time or "Immediate",
                    "immediate": immediate,
                    "created_at": datetime.now().isoformat()
                }
            }
            
            # Write files
            xml_path.write_text(xml_content, encoding='utf-8')
            json_path.write_text(json.dumps(json_data, indent=2), encoding='utf-8')
            
            # Create marker object
            marker = SCTE35Marker(
                event_id=event_id,
                cue_type=cue_type,
                preroll_seconds=preroll_seconds,
                ad_duration_seconds=ad_duration_seconds,
                schedule_time=schedule_time,
                immediate=immediate,
                xml_path=xml_path,
                json_path=json_path
            )
            
            self.logger.info(f"Generated SCTE-35 marker: {xml_filename} (Event ID: {event_id})")
            return marker
            
        except Exception as e:
            self.logger.error(f"Failed to generate marker: {e}", exc_info=True)
            raise SCTE35Error(f"Failed to generate marker: {e}")
    
    def generate_cue_pair(
        self,
        base_event_id: Optional[int] = None,
        ad_duration_seconds: int = 600,
        immediate: bool = True,
        auto_increment: bool = True
    ) -> Tuple[SCTE35Marker, SCTE35Marker]:
        """
        Generate CUE-OUT and CUE-IN pair with sequential event IDs
        
        Args:
            base_event_id: Base event ID (CUE-OUT will use this, CUE-IN will use base_event_id + 1)
            ad_duration_seconds: Duration of ad break
            immediate: Whether to trigger immediately
            auto_increment: If True, automatically increments from last used ID
        
        Returns:
            Tuple of (CUE-OUT marker, CUE-IN marker)
        """
        try:
            # Determine base event ID
            if auto_increment and base_event_id is None:
                base_event_id = self.get_next_event_id()
            elif base_event_id is None:
                base_event_id = 10023
            
            # Generate CUE-OUT marker
            cue_out = self.generate_marker(
                event_id=base_event_id,
                cue_type=CueType.CUE_OUT,
                ad_duration_seconds=ad_duration_seconds,
                immediate=immediate,
                auto_increment=auto_increment
            )
            
            # Generate CUE-IN marker with next sequential ID
            cue_in_id = base_event_id + 1
            if auto_increment:
                self._save_last_event_id(cue_in_id)
            
            cue_in = self.generate_marker(
                event_id=cue_in_id,
                cue_type=CueType.CUE_IN,
                ad_duration_seconds=0,  # CUE-IN has no duration
                immediate=immediate,
                auto_increment=False  # Already incremented manually
            )
            
            self.logger.info(f"Generated CUE pair: OUT={base_event_id}, IN={cue_in_id}")
            return (cue_out, cue_in)
            
        except Exception as e:
            self.logger.error(f"Failed to generate CUE pair: {e}", exc_info=True)
            raise SCTE35Error(f"Failed to generate CUE pair: {e}")
    
    def generate_preroll_sequence(
        self,
        base_event_id: Optional[int] = None,
        preroll_seconds: int = 0,  # Preroll: 0-10 seconds (time BEFORE ad break starts)
        ad_duration_seconds: int = 600,  # Ad duration: Example 600 seconds (10 minutes)
        immediate: bool = False,  # Per distributor: Preroll uses scheduled injection when > 0
        auto_increment: bool = True,
        include_crash: bool = True
    ) -> Tuple[SCTE35Marker, SCTE35Marker, Optional[SCTE35Marker]]:
        """
        Generate preroll sequence: CUE-OUT, CUE-IN, and optionally CUE-CRASH
        Per distributor requirements:
        - CUE-OUT: Program out point, scheduled with preroll (0-10 seconds before ad)
        - CUE-IN: Program in point, immediate return to program
        - CUE-CRASH: Emergency return, immediate
        
        Args:
            base_event_id: Base event ID (CUE-OUT will use this, increments sequentially)
            preroll_seconds: Preroll duration (0-10 seconds) - time BEFORE ad break starts
            ad_duration_seconds: Duration of ad break in seconds (Example: 600 = 10 minutes)
            immediate: If False and preroll > 0, uses scheduled injection with pts_time
            auto_increment: If True, automatically increments from last used ID
            include_crash: If True, also generates CUE-CRASH marker
        
        Returns:
            Tuple of (CUE-OUT marker, CUE-IN marker, CUE-CRASH marker or None)
        """
        try:
            # Determine base event ID
            if auto_increment and base_event_id is None:
                base_event_id = self.get_next_event_id()
            elif base_event_id is None:
                base_event_id = 10023
            
            # Generate CUE-OUT marker
            # FIX: Use immediate injection for CUE-OUT to ensure reliable injection
            # The preroll value is informational (0-10 seconds) but injection should be immediate
            # This ensures CUE-OUT is injected before CUE-IN and works correctly with --delete-files
            cue_out = self.generate_marker(
                event_id=base_event_id,
                cue_type=CueType.CUE_OUT,
                preroll_seconds=preroll_seconds,
                ad_duration_seconds=ad_duration_seconds,
                immediate=True,  # Always immediate for reliable injection
                auto_increment=auto_increment
            )
            
            # Generate CUE-IN marker with next sequential ID
            # Per distributor requirements: CUE-IN is always immediate (Program in point)
            cue_in_id = base_event_id + 1
            if auto_increment:
                self._save_last_event_id(cue_in_id)
            
            cue_in = self.generate_marker(
                event_id=cue_in_id,
                cue_type=CueType.CUE_IN,
                preroll_seconds=0,
                ad_duration_seconds=0,  # CUE-IN has no duration
                immediate=True,  # CUE-IN is always immediate (per distributor requirements)
                auto_increment=False  # Already incremented manually
            )
            
            # Generate CUE-CRASH marker if requested
            cue_crash = None
            if include_crash:
                crash_id = cue_in_id + 1
                if auto_increment:
                    self._save_last_event_id(crash_id)
                
                cue_crash = self.generate_marker(
                    event_id=crash_id,
                    cue_type=CueType.CUE_CRASH,
                    preroll_seconds=0,
                    ad_duration_seconds=0,
                    immediate=True,  # CUE-CRASH is always immediate
                    auto_increment=False  # Already incremented manually
                )
            
            self.logger.info(
                f"Generated preroll sequence: OUT={base_event_id}, IN={cue_in_id}"
                + (f", CRASH={crash_id}" if include_crash else "")
            )
            return (cue_out, cue_in, cue_crash)
            
        except Exception as e:
            self.logger.error(f"Failed to generate preroll sequence: {e}", exc_info=True)
            raise SCTE35Error(f"Failed to generate preroll sequence: {e}")
    
    def _generate_xml(
        self,
        event_id: int,
        cue_type: CueType,
        preroll: int,
        ad_duration: int,
        immediate: bool = True
    ) -> str:
        """Generate XML content for TSDuck"""
        # When splice_immediate="true", pts_time attribute is not allowed
        immediate_str = "true" if immediate else "false"
        pts_time_attr = f'pts_time="{preroll * 90000}"' if not immediate else ""
        
        if cue_type == CueType.PREROLL:
            # PREROLL: Same as CUE-OUT but with auto_return="true"
            # FIX: Always use immediate injection for reliability (consistent with CUE-OUT fix)
            # The preroll value (0-10 seconds) is informational and handled by distributor's system
            return f'''<?xml version="1.0" encoding="UTF-8"?>
<tsduck>
    <splice_information_table protocol_version="0" pts_adjustment="0" tier="0xFFF">
        <splice_insert splice_event_id="{event_id}" 
                      splice_event_cancel="false" 
                      out_of_network="true" 
                      splice_immediate="true" 
                      unique_program_id="1" 
                      avail_num="1" 
                      avails_expected="1">
            <break_duration auto_return="true" duration="{ad_duration * 90000}" />
        </splice_insert>
    </splice_information_table>
</tsduck>'''
        elif cue_type == CueType.CUE_OUT:
            # CUE-OUT: Program out point (SCTE START from playout)
            # FIX: Always use immediate injection for reliability
            # The preroll value (0-10 seconds) is informational and handled by distributor's system
            # Immediate injection ensures CUE-OUT is injected correctly with --delete-files
            return f'''<?xml version="1.0" encoding="UTF-8"?>
<tsduck>
    <splice_information_table protocol_version="0" pts_adjustment="0" tier="0xFFF">
        <splice_insert splice_event_id="{event_id}" 
                      splice_event_cancel="false" 
                      out_of_network="true" 
                      splice_immediate="true" 
                      unique_program_id="1" 
                      avail_num="1" 
                      avails_expected="1">
            <break_duration auto_return="false" duration="{ad_duration * 90000}" />
        </splice_insert>
    </splice_information_table>
</tsduck>'''
        elif cue_type == CueType.CUE_IN:
            # CUE-IN: always immediate, no pts_time allowed
            return f'''<?xml version="1.0" encoding="UTF-8"?>
<tsduck>
    <splice_information_table protocol_version="0" pts_adjustment="0" tier="0xFFF">
        <splice_insert splice_event_id="{event_id}" 
                      splice_event_cancel="false" 
                      out_of_network="false" 
                      splice_immediate="true" 
                      unique_program_id="1" 
                      avail_num="1" 
                      avails_expected="1">
            <break_duration auto_return="true" duration="0" />
        </splice_insert>
    </splice_information_table>
</tsduck>'''
        elif cue_type == CueType.CUE_CRASH:
            # CUE-CRASH: always immediate, no pts_time allowed
            return f'''<?xml version="1.0" encoding="UTF-8"?>
<tsduck>
    <splice_information_table protocol_version="0" pts_adjustment="0" tier="0xFFF">
        <splice_insert splice_event_id="{event_id}" 
                      splice_event_cancel="false" 
                      out_of_network="false" 
                      splice_immediate="true" 
                      unique_program_id="1" 
                      avail_num="1" 
                      avails_expected="1">
            <break_duration auto_return="true" duration="0" />
        </splice_insert>
    </splice_information_table>
</tsduck>'''
        else:  # TIME_SIGNAL
            return f'''<?xml version="1.0" encoding="UTF-8"?>
<tsduck>
    <splice_information_table protocol_version="0" pts_adjustment="0" tier="0xFFF">
        <splice_time_signal splice_event_id="{event_id}" 
                           splice_event_cancel="false">
            <splice_time pts_time="0" />
        </splice_time_signal>
    </splice_information_table>
</tsduck>'''
    
    def get_latest_marker(self) -> Optional[SCTE35Marker]:
        """Get the latest generated marker"""
        xml_files = list(self.markers_dir.glob("*.xml"))
        if not xml_files:
            return None
        
        latest_file = max(xml_files, key=lambda f: f.stat().st_mtime)
        
        # Try to find corresponding JSON file
        json_file = latest_file.with_suffix('.json')
        if not json_file.exists():
            json_file = None
        
        try:
            marker = SCTE35Marker(
                xml_path=latest_file,
                json_path=json_file
            )
            return marker
        except Exception as e:
            self.logger.error(f"Failed to load marker: {e}")
            return None

