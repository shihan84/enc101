"""
EPG/EIT Generation Service
Electronic Program Guide generation and injection using TSDuck
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Callable
from dataclasses import dataclass, field
from ..core.logger import get_logger
from ..utils.exceptions import SCTE35Error


@dataclass
class EPGEvent:
    """EPG event information"""
    event_id: int
    title: str
    description: str = ""
    start_time: datetime = None
    duration: int = 0  # seconds
    content_type: str = "0x10"  # Default: movie
    content_nibble_level_2: str = "0x00"  # Sub-category
    parental_rating: int = 0
    parental_rating_system: str = "DVB"  # DVB, ATSC, etc.
    language: str = "eng"
    subtitle_language: str = ""
    audio_language: str = ""
    country_code: str = "GBR"
    year: int = 0
    director: str = ""
    actors: List[str] = field(default_factory=list)
    category: str = ""
    keywords: List[str] = field(default_factory=list)
    star_rating: float = 0.0  # 0.0 to 10.0
    episode_number: int = 0
    season_number: int = 0
    episode_title: str = ""
    extended_info: Dict = field(default_factory=dict)


@dataclass
class EPGServiceInfo:
    """EPG service information"""
    service_id: int
    name: str
    provider: str = ""
    events: List[EPGEvent] = field(default_factory=list)


class EPGService:
    """Service for EPG/EIT generation and management"""
    
    def __init__(self, epg_dir: Path = None):
        self.logger = get_logger("EPGService")
        self.epg_dir = epg_dir or Path("epg")
        self.epg_dir.mkdir(exist_ok=True)
        self.logger.info(f"EPG service initialized with directory: {self.epg_dir}")
    
    def generate_eit(
        self,
        service_id: int,
        service_name: str,
        events: List[EPGEvent],
        provider: str = ""
    ) -> Path:
        """
        Generate EIT (Event Information Table) XML for TSDuck
        
        Args:
            service_id: Service ID
            service_name: Service name
            events: List of EPG events
            provider: Provider name
        
        Returns:
            Path to generated EIT XML file
        """
        # Input validation
        from ..utils.validators import validate_numeric_range, sanitize_string
        
        # Validate service ID
        is_valid, error_msg = validate_numeric_range(service_id, 1, 65535, "Service ID")
        if not is_valid:
            raise SCTE35Error(f"Invalid service ID: {error_msg}")
        
        # Validate service name
        if not service_name or not service_name.strip():
            raise SCTE35Error("Service name cannot be empty")
        service_name = sanitize_string(service_name, max_length=100)
        
        # Validate provider name
        if provider:
            provider = sanitize_string(provider, max_length=100)
        
        # Validate events
        if not events:
            raise SCTE35Error("Events list cannot be empty")
        
        # Validate each event
        for event in events:
            if not event.title or not event.title.strip():
                raise SCTE35Error("Event title cannot be empty")
            event.title = sanitize_string(event.title, max_length=200)
            
            if event.duration < 0:
                raise SCTE35Error("Event duration cannot be negative")
            
            if event.event_id < 1 or event.event_id > 65535:
                raise SCTE35Error("Event ID must be between 1 and 65535")
        
        try:
            timestamp = int(datetime.now().timestamp())
            xml_filename = f"eit_{service_id}_{timestamp}.xml"
            xml_path = self.epg_dir / xml_filename
            
            # Generate EIT XML
            xml_content = self._generate_eit_xml(service_id, service_name, events, provider)
            
            # Write file
            xml_path.write_text(xml_content, encoding='utf-8')
            
            self.logger.info(f"Generated EIT file: {xml_filename}")
            return xml_path
            
        except Exception as e:
            self.logger.error(f"Failed to generate EIT: {e}", exc_info=True)
            raise SCTE35Error(f"Failed to generate EIT: {e}")
    
    def _generate_eit_xml(
        self,
        service_id: int,
        service_name: str,
        events: List[EPGEvent],
        provider: str
    ) -> str:
        """Generate EIT XML content for TSDuck"""
        
        xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml_lines.append('<tsduck>')
        xml_lines.append('  <EIT type="pf">')  # Present/Following
        xml_lines.append(f'    <service service_id="{service_id}" name="{service_name}">')
        
        if provider:
            xml_lines.append(f'      <provider>{provider}</provider>')
        
        # Add events
        for event in events:
            xml_lines.append('      <event>')
            xml_lines.append(f'        <event_id>{event.event_id}</event_id>')
            xml_lines.append(f'        <start_time>{event.start_time.strftime("%Y-%m-%d %H:%M:%S")}</start_time>')
            xml_lines.append(f'        <duration>{event.duration}</duration>')
            xml_lines.append(f'        <title language="{event.language}">{event.title}</title>')
            
            if event.description:
                xml_lines.append(f'        <description language="{event.language}">{event.description}</description>')
            
            xml_lines.append(f'        <content content_nibble_level_1="{event.content_type}" content_nibble_level_2="{event.content_nibble_level_2}" />')
            
            if event.parental_rating > 0:
                xml_lines.append(f'        <parental_rating system="{event.parental_rating_system}">{event.parental_rating}</parental_rating>')
            
            if event.subtitle_language:
                xml_lines.append(f'        <subtitle_language>{event.subtitle_language}</subtitle_language>')
            
            if event.audio_language:
                xml_lines.append(f'        <audio_language>{event.audio_language}</audio_language>')
            
            if event.country_code:
                xml_lines.append(f'        <country_code>{event.country_code}</country_code>')
            
            if event.year > 0:
                xml_lines.append(f'        <year>{event.year}</year>')
            
            if event.director:
                xml_lines.append(f'        <director>{event.director}</director>')
            
            if event.actors:
                actors_str = ", ".join(event.actors)
                xml_lines.append(f'        <actors>{actors_str}</actors>')
            
            if event.category:
                xml_lines.append(f'        <category>{event.category}</category>')
            
            if event.keywords:
                keywords_str = ", ".join(event.keywords)
                xml_lines.append(f'        <keywords>{keywords_str}</keywords>')
            
            if event.star_rating > 0:
                xml_lines.append(f'        <star_rating>{event.star_rating:.1f}</star_rating>')
            
            if event.episode_number > 0 or event.season_number > 0:
                xml_lines.append(f'        <episode season="{event.season_number}" episode="{event.episode_number}" />')
            
            if event.episode_title:
                xml_lines.append(f'        <episode_title>{event.episode_title}</episode_title>')
            
            # Extended info
            if event.extended_info:
                for key, value in event.extended_info.items():
                    xml_lines.append(f'        <{key}>{value}</{key}>')
            
            xml_lines.append('      </event>')
        
        xml_lines.append('    </service>')
        xml_lines.append('  </EIT>')
        xml_lines.append('</tsduck>')
        
        return '\n'.join(xml_lines)
    
    def import_xmltv(self, xmltv_path: Path) -> List[EPGEvent]:
        """
        Import EPG from XMLTV format
        
        Args:
            xmltv_path: Path to XMLTV file
        
        Returns:
            List of EPG events
        """
        try:
            import xml.etree.ElementTree as ET
            
            tree = ET.parse(xmltv_path)
            root = tree.getroot()
            
            events = []
            for programme in root.findall('.//programme'):
                event_id = int(programme.get('channel', '0'))
                start_str = programme.get('start', '')
                stop_str = programme.get('stop', '')
                
                # Parse times
                start_time = self._parse_xmltv_time(start_str)
                stop_time = self._parse_xmltv_time(stop_str)
                duration = int((stop_time - start_time).total_seconds()) if stop_time and start_time else 0
                
                # Get title and description
                title_elem = programme.find('title')
                title = title_elem.text if title_elem is not None else ""
                
                desc_elem = programme.find('desc')
                description = desc_elem.text if desc_elem is not None else ""
                
                event = EPGEvent(
                    event_id=event_id,
                    title=title,
                    description=description,
                    start_time=start_time,
                    duration=duration
                )
                events.append(event)
            
            self.logger.info(f"Imported {len(events)} events from XMLTV")
            return events
            
        except Exception as e:
            self.logger.error(f"Failed to import XMLTV: {e}", exc_info=True)
            return []
    
    def _parse_xmltv_time(self, time_str: str) -> Optional[datetime]:
        """Parse XMLTV time format"""
        try:
            # XMLTV format: YYYYMMDDHHMMSS +0000
            if len(time_str) >= 14:
                date_part = time_str[:14]
                return datetime.strptime(date_part, "%Y%m%d%H%M%S")
        except Exception:
            pass
        return None
    
    def export_epg(self, events: List[EPGEvent], format: str = "json") -> str:
        """
        Export EPG events
        
        Args:
            events: List of EPG events
            format: Export format (json, xmltv)
        
        Returns:
            Exported EPG data as string
        """
        if format.lower() == "json":
            data = {
                'events': [
                    {
                        'event_id': e.event_id,
                        'title': e.title,
                        'description': e.description,
                        'start_time': e.start_time.isoformat() if e.start_time else None,
                        'duration': e.duration,
                        'content_type': e.content_type,
                        'language': e.language
                    }
                    for e in events
                ]
            }
            return json.dumps(data, indent=2)
        elif format.lower() == "xmltv":
            return self._export_xmltv(events)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_xmltv(self, events: List[EPGEvent]) -> str:
        """Export to XMLTV format"""
        lines = ['<?xml version="1.0" encoding="UTF-8"?>']
        lines.append('<tv>')
        
        for event in events:
            if not event.start_time:
                continue
            
            start_str = event.start_time.strftime("%Y%m%d%H%M%S +0000")
            end_time = event.start_time + timedelta(seconds=event.duration)
            stop_str = end_time.strftime("%Y%m%d%H%M%S +0000")
            
            lines.append(f'  <programme start="{start_str}" stop="{stop_str}" channel="1">')
            lines.append(f'    <title>{event.title}</title>')
            if event.description:
                lines.append(f'    <desc>{event.description}</desc>')
            lines.append('  </programme>')
        
        lines.append('</tv>')
        return '\n'.join(lines)
    
    def get_latest_eit(self, service_id: int) -> Optional[Path]:
        """Get latest EIT file for service"""
        eit_files = list(self.epg_dir.glob(f"eit_{service_id}_*.xml"))
        if not eit_files:
            return None
        
        return max(eit_files, key=lambda f: f.stat().st_mtime)
    
    def validate_event(self, event: EPGEvent):
        """Validate EPG event"""
        errors = []
        
        if not event.title or not event.title.strip():
            errors.append("Title is required")
        
        if event.duration <= 0:
            errors.append("Duration must be greater than 0")
        
        if event.start_time is None:
            errors.append("Start time is required")
        
        if event.event_id <= 0:
            errors.append("Event ID must be greater than 0")
        
        return len(errors) == 0, errors
    
    def validate_schedule(self, events: List[EPGEvent]):
        """Validate entire schedule for conflicts"""
        errors = []
        
        # Sort by start time
        sorted_events = sorted([e for e in events if e.start_time], key=lambda x: x.start_time)
        
        # Check for overlaps
        for i in range(len(sorted_events) - 1):
            current = sorted_events[i]
            next_event = sorted_events[i + 1]
            
            current_end = current.start_time + timedelta(seconds=current.duration)
            
            if current_end > next_event.start_time:
                errors.append(f"Overlap: '{current.title}' overlaps with '{next_event.title}'")
        
        # Check for duplicate event IDs
        event_ids = [e.event_id for e in events]
        duplicates = [eid for eid in event_ids if event_ids.count(eid) > 1]
        if duplicates:
            errors.append(f"Duplicate event IDs: {set(duplicates)}")
        
        return len(errors) == 0, errors
    
    def create_recurring_events(
        self,
        base_event: EPGEvent,
        start_date: datetime,
        end_date: datetime,
        frequency: str = "daily",  # daily, weekly, monthly
        days_of_week: List[int] = None  # 0=Monday, 6=Sunday
    ) -> List[EPGEvent]:
        """Create recurring events from a base event"""
        events = []
        current_date = start_date
        
        if days_of_week is None:
            days_of_week = list(range(7))
        
        event_id = base_event.event_id
        
        while current_date <= end_date:
            if frequency == "daily":
                if current_date.weekday() in days_of_week:
                    new_event = EPGEvent(
                        event_id=event_id,
                        title=base_event.title,
                        description=base_event.description,
                        start_time=current_date.replace(
                            hour=base_event.start_time.hour if base_event.start_time else 0,
                            minute=base_event.start_time.minute if base_event.start_time else 0,
                            second=0
                        ),
                        duration=base_event.duration,
                        content_type=base_event.content_type,
                        content_nibble_level_2=base_event.content_nibble_level_2,
                        parental_rating=base_event.parental_rating,
                        language=base_event.language,
                        extended_info=base_event.extended_info.copy()
                    )
                    events.append(new_event)
                    event_id += 1
                current_date += timedelta(days=1)
            elif frequency == "weekly":
                if current_date.weekday() in days_of_week:
                    new_event = EPGEvent(
                        event_id=event_id,
                        title=base_event.title,
                        description=base_event.description,
                        start_time=current_date.replace(
                            hour=base_event.start_time.hour if base_event.start_time else 0,
                            minute=base_event.start_time.minute if base_event.start_time else 0,
                            second=0
                        ),
                        duration=base_event.duration,
                        content_type=base_event.content_type,
                        content_nibble_level_2=base_event.content_nibble_level_2,
                        parental_rating=base_event.parental_rating,
                        language=base_event.language,
                        extended_info=base_event.extended_info.copy()
                    )
                    events.append(new_event)
                    event_id += 1
                current_date += timedelta(days=7)
            elif frequency == "monthly":
                if current_date.weekday() in days_of_week:
                    new_event = EPGEvent(
                        event_id=event_id,
                        title=base_event.title,
                        description=base_event.description,
                        start_time=current_date.replace(
                            hour=base_event.start_time.hour if base_event.start_time else 0,
                            minute=base_event.start_time.minute if base_event.start_time else 0,
                            second=0
                        ),
                        duration=base_event.duration,
                        content_type=base_event.content_type,
                        content_nibble_level_2=base_event.content_nibble_level_2,
                        parental_rating=base_event.parental_rating,
                        language=base_event.language,
                        extended_info=base_event.extended_info.copy()
                    )
                    events.append(new_event)
                    event_id += 1
                # Move to same day next month
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
        
        return events
    
    def search_events(
        self,
        events: List[EPGEvent],
        query: str,
        search_fields: List[str] = None
    ) -> List[EPGEvent]:
        """Search events by query"""
        if search_fields is None:
            search_fields = ["title", "description", "category", "director", "actors"]
        
        query_lower = query.lower()
        results = []
        
        for event in events:
            for field in search_fields:
                if field == "title" and query_lower in event.title.lower():
                    results.append(event)
                    break
                elif field == "description" and query_lower in event.description.lower():
                    results.append(event)
                    break
                elif field == "category" and query_lower in event.category.lower():
                    results.append(event)
                    break
                elif field == "director" and query_lower in event.director.lower():
                    results.append(event)
                    break
                elif field == "actors" and any(query_lower in actor.lower() for actor in event.actors):
                    results.append(event)
                    break
        
        return results
    
    def filter_events(
        self,
        events: List[EPGEvent],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        content_type: Optional[str] = None,
        min_rating: Optional[float] = None,
        language: Optional[str] = None
    ) -> List[EPGEvent]:
        """Filter events by criteria"""
        filtered = events
        
        if start_date:
            filtered = [e for e in filtered if e.start_time and e.start_time >= start_date]
        
        if end_date:
            filtered = [e for e in filtered if e.start_time and e.start_time <= end_date]
        
        if content_type:
            filtered = [e for e in filtered if e.content_type == content_type]
        
        if min_rating is not None:
            filtered = [e for e in filtered if e.star_rating >= min_rating]
        
        if language:
            filtered = [e for e in filtered if e.language == language]
        
        return filtered

