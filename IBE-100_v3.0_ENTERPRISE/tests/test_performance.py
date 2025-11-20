"""
Performance benchmarks and tests
"""

import unittest
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.utils.validators import validate_url, validate_port, validate_event_id
from src.utils.rate_limiter import RateLimiter


class TestPerformance(unittest.TestCase):
    """Performance benchmarks"""
    
    def test_validator_performance(self):
        """Test validator performance"""
        iterations = 1000
        
        start = time.time()
        for _ in range(iterations):
            validate_url("http://example.com/test")
            validate_port(8080)
            validate_event_id(10023)
        elapsed = time.time() - start
        
        # Should complete 3000 validations in under 1 second
        self.assertLess(elapsed, 1.0, f"Validators too slow: {elapsed:.3f}s for {iterations * 3} operations")
        ops_per_sec = (iterations * 3) / elapsed
        print(f"\n  Validator performance: {ops_per_sec:.0f} operations/second")
    
    def test_rate_limiter_performance(self):
        """Test rate limiter performance"""
        limiter = RateLimiter(max_requests=1000, window_seconds=60)
        iterations = 1000
        
        start = time.time()
        for i in range(iterations):
            limiter.is_allowed(f"client_{i % 10}")
        elapsed = time.time() - start
        
        # Should complete 1000 checks in under 0.5 seconds
        self.assertLess(elapsed, 0.5, f"Rate limiter too slow: {elapsed:.3f}s for {iterations} operations")
        ops_per_sec = iterations / elapsed
        print(f"\n  Rate limiter performance: {ops_per_sec:.0f} operations/second")
    
    def test_memory_usage(self):
        """Test memory usage of validators"""
        import tracemalloc
        
        tracemalloc.start()
        
        # Perform operations
        for _ in range(100):
            validate_url("http://example.com/test")
            validate_port(8080)
            validate_event_id(10023)
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Peak memory should be under 10MB for 100 operations
        peak_mb = peak / 1024 / 1024
        self.assertLess(peak_mb, 10, f"Memory usage too high: {peak_mb:.2f}MB")
        print(f"\n  Peak memory usage: {peak_mb:.2f}MB")


if __name__ == '__main__':
    unittest.main()

