"""
Rate limiting utility for API endpoints
"""

import time
from collections import defaultdict
from typing import Dict, Tuple
from threading import Lock


class RateLimiter:
    """Simple rate limiter using token bucket algorithm"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)
        self.lock = Lock()
    
    def is_allowed(self, identifier: str = "default") -> Tuple[bool, int]:
        """
        Check if request is allowed
        
        Args:
            identifier: Client identifier (IP address, API key, etc.)
        
        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        with self.lock:
            now = time.time()
            client_requests = self.requests[identifier]
            
            # Remove old requests outside the window
            client_requests[:] = [req_time for req_time in client_requests 
                                 if now - req_time < self.window_seconds]
            
            # Check if limit exceeded
            if len(client_requests) >= self.max_requests:
                remaining = 0
                return False, remaining
            
            # Add current request
            client_requests.append(now)
            remaining = self.max_requests - len(client_requests)
            
            return True, remaining
    
    def reset(self, identifier: str = None):
        """Reset rate limit for identifier (or all if None)"""
        with self.lock:
            if identifier:
                if identifier in self.requests:
                    del self.requests[identifier]
            else:
                self.requests.clear()


# Global rate limiter instance
_default_rate_limiter = RateLimiter(max_requests=100, window_seconds=60)


def get_rate_limiter(max_requests: int = 100, window_seconds: int = 60) -> RateLimiter:
    """Get rate limiter instance"""
    return RateLimiter(max_requests=max_requests, window_seconds=window_seconds)

