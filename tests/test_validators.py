"""
Unit tests for input validators
"""

import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.utils.validators import (
    validate_url, validate_port, validate_pid, validate_latency,
    validate_event_id, validate_file_path, validate_stream_id,
    validate_duration, validate_ip_address, sanitize_string,
    validate_numeric_range
)


class TestValidators(unittest.TestCase):
    """Test input validation functions"""
    
    def test_validate_url(self):
        """Test URL validation"""
        # Valid URLs
        self.assertTrue(validate_url("http://example.com")[0])
        self.assertTrue(validate_url("https://example.com")[0])
        self.assertTrue(validate_url("udp://192.168.1.1:5000")[0])
        self.assertTrue(validate_url("srt://server.com:8888")[0])
        
        # Invalid URLs
        self.assertFalse(validate_url("")[0])
        # Note: The validator treats non-standard URL strings as file paths (which is valid)
        # Test with invalid HTTP URL (missing hostname)
        is_valid, error = validate_url("http://")
        self.assertFalse(is_valid)
        self.assertIn("hostname", error.lower())
    
    def test_validate_port(self):
        """Test port validation"""
        # Valid ports
        self.assertTrue(validate_port(80)[0])
        self.assertTrue(validate_port(8080)[0])
        self.assertTrue(validate_port(65535)[0])
        self.assertTrue(validate_port("8080")[0])
        
        # Invalid ports
        self.assertFalse(validate_port(0)[0])
        self.assertFalse(validate_port(65536)[0])
        self.assertFalse(validate_port(-1)[0])
        self.assertFalse(validate_port("invalid")[0])
    
    def test_validate_pid(self):
        """Test PID validation"""
        # Valid PIDs
        self.assertTrue(validate_pid(256)[0])
        self.assertTrue(validate_pid(500)[0])
        self.assertTrue(validate_pid(8190)[0])
        
        # Invalid PIDs
        self.assertFalse(validate_pid(31)[0])  # Below minimum
        self.assertFalse(validate_pid(8191)[0])  # Above maximum
        self.assertFalse(validate_pid("invalid")[0])
    
    def test_validate_latency(self):
        """Test latency validation"""
        # Valid latencies
        self.assertTrue(validate_latency(100)[0])
        self.assertTrue(validate_latency(2000)[0])
        self.assertTrue(validate_latency(10000)[0])
        
        # Invalid latencies
        self.assertFalse(validate_latency(99)[0])  # Below minimum
        self.assertFalse(validate_latency(10001)[0])  # Above maximum
        self.assertFalse(validate_latency("invalid")[0])
    
    def test_validate_event_id(self):
        """Test event ID validation"""
        # Valid event IDs
        self.assertTrue(validate_event_id(10000)[0])
        self.assertTrue(validate_event_id(50000)[0])
        self.assertTrue(validate_event_id(99999)[0])
        
        # Invalid event IDs
        self.assertFalse(validate_event_id(9999)[0])  # Below minimum
        self.assertFalse(validate_event_id(100000)[0])  # Above maximum
        self.assertFalse(validate_event_id("invalid")[0])
    
    def test_validate_stream_id(self):
        """Test stream ID validation"""
        # Valid stream IDs
        self.assertTrue(validate_stream_id("")[0])  # Empty is valid
        self.assertTrue(validate_stream_id("test_stream")[0])
        self.assertTrue(validate_stream_id("#!::r=scte/scte,m=publish")[0])
        
        # Invalid stream IDs
        self.assertFalse(validate_stream_id("a" * 513)[0])  # Too long
        self.assertFalse(validate_stream_id("test<script>")[0])  # Dangerous chars
    
    def test_validate_duration(self):
        """Test duration validation"""
        # Valid durations
        self.assertTrue(validate_duration(0)[0])
        self.assertTrue(validate_duration(600)[0])
        self.assertTrue(validate_duration(86400)[0])
        
        # Invalid durations
        self.assertFalse(validate_duration(-1)[0])  # Below minimum
        self.assertFalse(validate_duration(86401)[0])  # Above maximum
        self.assertFalse(validate_duration("invalid")[0])
    
    def test_validate_ip_address(self):
        """Test IP address validation"""
        # Valid IPs
        self.assertTrue(validate_ip_address("192.168.1.1")[0])
        self.assertTrue(validate_ip_address("127.0.0.1")[0])
        self.assertTrue(validate_ip_address("localhost")[0])
        
        # Invalid IPs
        self.assertFalse(validate_ip_address("")[0])
        self.assertFalse(validate_ip_address("256.256.256.256")[0])  # Out of range
        self.assertFalse(validate_ip_address("invalid")[0])
    
    def test_sanitize_string(self):
        """Test string sanitization"""
        # Normal strings
        self.assertEqual(sanitize_string("test"), "test")
        self.assertEqual(sanitize_string("  test  "), "test")
        
        # Strings with null bytes
        self.assertEqual(sanitize_string("test\x00string"), "teststring")
        
        # Long strings
        long_string = "a" * 2000
        self.assertEqual(len(sanitize_string(long_string)), 1000)  # Truncated
    
    def test_validate_numeric_range(self):
        """Test numeric range validation"""
        # Valid values
        self.assertTrue(validate_numeric_range(50, 0, 100)[0])
        self.assertTrue(validate_numeric_range(0, 0, 100)[0])
        self.assertTrue(validate_numeric_range(100, 0, 100)[0])
        
        # Invalid values
        self.assertFalse(validate_numeric_range(-1, 0, 100)[0])
        self.assertFalse(validate_numeric_range(101, 0, 100)[0])
        self.assertFalse(validate_numeric_range("invalid", 0, 100)[0])


if __name__ == '__main__':
    unittest.main()

