"""
Unit tests for core services
"""

import unittest
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.services.scte35_service import SCTE35Service
from src.models.scte35_marker import CueType
from src.utils.exceptions import SCTE35Error


class TestSCTE35Service(unittest.TestCase):
    """Test SCTE-35 service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.service = SCTE35Service(profile_name="test_profile")
    
    def test_get_next_event_id(self):
        """Test event ID generation"""
        event_id = self.service.get_next_event_id()
        self.assertGreaterEqual(event_id, 10000)
        self.assertLessEqual(event_id, 99999)
    
    def test_generate_marker_valid(self):
        """Test marker generation with valid inputs"""
        marker = self.service.generate_marker(
            event_id=10023,
            cue_type=CueType.PREROLL,
            preroll_seconds=4,
            ad_duration_seconds=600,
            auto_increment=False
        )
        self.assertIsNotNone(marker)
        self.assertEqual(marker.event_id, 10023)
        self.assertTrue(marker.xml_path.exists())
        self.assertTrue(marker.json_path.exists())
    
    def test_generate_marker_invalid_event_id(self):
        """Test marker generation with invalid event ID"""
        with self.assertRaises(SCTE35Error):
            self.service.generate_marker(
                event_id=9999,  # Below minimum
                cue_type=CueType.PREROLL,
                auto_increment=False
            )
    
    def test_generate_marker_invalid_preroll(self):
        """Test marker generation with invalid preroll duration"""
        with self.assertRaises(SCTE35Error):
            self.service.generate_marker(
                event_id=10023,
                cue_type=CueType.PREROLL,
                preroll_seconds=11,  # Above maximum (10)
                auto_increment=False
            )
    
    def test_generate_marker_invalid_ad_duration(self):
        """Test marker generation with invalid ad duration"""
        with self.assertRaises(SCTE35Error):
            self.service.generate_marker(
                event_id=10023,
                cue_type=CueType.PREROLL,
                ad_duration_seconds=86401,  # Above maximum (24 hours)
                auto_increment=False
            )
    
    def test_auto_increment(self):
        """Test automatic event ID increment"""
        marker1 = self.service.generate_marker(
            event_id=None,
            cue_type=CueType.PREROLL,
            auto_increment=True
        )
        marker2 = self.service.generate_marker(
            event_id=None,
            cue_type=CueType.PREROLL,
            auto_increment=True
        )
        # Second marker should have incremented ID
        self.assertEqual(marker2.event_id, marker1.event_id + 1)


class TestRateLimiter(unittest.TestCase):
    """Test rate limiter"""
    
    def setUp(self):
        """Set up test fixtures"""
        from src.utils.rate_limiter import RateLimiter
        self.rate_limiter = RateLimiter(max_requests=5, window_seconds=60)
    
    def test_rate_limit_allowed(self):
        """Test that requests within limit are allowed"""
        for i in range(5):
            is_allowed, remaining = self.rate_limiter.is_allowed("test_client")
            self.assertTrue(is_allowed)
            self.assertEqual(remaining, 5 - i - 1)
    
    def test_rate_limit_exceeded(self):
        """Test that requests exceeding limit are blocked"""
        # Make 5 requests (limit)
        for _ in range(5):
            self.rate_limiter.is_allowed("test_client")
        
        # 6th request should be blocked
        is_allowed, remaining = self.rate_limiter.is_allowed("test_client")
        self.assertFalse(is_allowed)
        self.assertEqual(remaining, 0)
    
    def test_rate_limit_reset(self):
        """Test rate limit reset"""
        # Make requests
        for _ in range(5):
            self.rate_limiter.is_allowed("test_client")
        
        # Reset
        self.rate_limiter.reset("test_client")
        
        # Should be allowed again
        is_allowed, remaining = self.rate_limiter.is_allowed("test_client")
        self.assertTrue(is_allowed)
        self.assertEqual(remaining, 4)


if __name__ == '__main__':
    unittest.main()

