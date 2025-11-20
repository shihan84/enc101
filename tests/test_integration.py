"""
Integration tests for core workflows
"""

import unittest
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.services.scte35_service import SCTE35Service
from src.services.epg_service import EPGService, EPGEvent
from src.models.scte35_marker import CueType
from datetime import datetime, timedelta


class TestSCTE35Integration(unittest.TestCase):
    """Integration tests for SCTE-35 workflow"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = TemporaryDirectory()
        self.service = SCTE35Service(
            markers_dir=Path(self.temp_dir.name) / "markers",
            profile_name="test_profile"
        )
    
    def tearDown(self):
        """Clean up"""
        self.temp_dir.cleanup()
    
    def test_marker_generation_workflow(self):
        """Test complete marker generation workflow"""
        # Generate marker
        marker = self.service.generate_marker(
            event_id=10023,
            cue_type=CueType.PREROLL,
            preroll_seconds=4,
            ad_duration_seconds=600,
            auto_increment=False
        )
        
        # Verify marker
        self.assertIsNotNone(marker)
        self.assertTrue(marker.xml_path.exists())
        self.assertTrue(marker.json_path.exists())
        
        # Verify XML content
        xml_content = marker.xml_path.read_text()
        self.assertIn("splice_insert", xml_content)
        self.assertIn(str(marker.event_id), xml_content)
    
    def test_auto_increment_workflow(self):
        """Test auto-increment workflow"""
        # Generate multiple markers
        markers = []
        for i in range(3):
            marker = self.service.generate_marker(
                event_id=None,
                cue_type=CueType.CUE_OUT,
                auto_increment=True
            )
            markers.append(marker)
        
        # Verify sequential IDs
        self.assertEqual(markers[1].event_id, markers[0].event_id + 1)
        self.assertEqual(markers[2].event_id, markers[1].event_id + 1)


class TestEPGIntegration(unittest.TestCase):
    """Integration tests for EPG workflow"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = TemporaryDirectory()
        self.service = EPGService(epg_dir=Path(self.temp_dir.name) / "epg")
    
    def tearDown(self):
        """Clean up"""
        self.temp_dir.cleanup()
    
    def test_epg_generation_workflow(self):
        """Test complete EPG generation workflow"""
        # Create events
        events = [
            EPGEvent(
                event_id=1,
                title="Test Program 1",
                description="Test description",
                start_time=datetime.now(),
                duration=3600
            ),
            EPGEvent(
                event_id=2,
                title="Test Program 2",
                description="Test description 2",
                start_time=datetime.now() + timedelta(hours=1),
                duration=1800
            )
        ]
        
        # Generate EIT
        eit_path = self.service.generate_eit(
            service_id=1,
            service_name="Test Service",
            events=events,
            provider="Test Provider"
        )
        
        # Verify EIT file
        self.assertTrue(eit_path.exists())
        
        # Verify XML content
        xml_content = eit_path.read_text()
        self.assertIn("Test Service", xml_content)
        self.assertIn("Test Program 1", xml_content)
        self.assertIn("Test Program 2", xml_content)


if __name__ == '__main__':
    unittest.main()

