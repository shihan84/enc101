"""
Monitoring and Analytics Service
Optimized for performance with caching
"""

import psutil
import time
from typing import Dict, Optional
from ..core.logger import get_logger


class MonitoringService:
    """Service for system and stream monitoring with caching"""
    
    def __init__(self):
        self.logger = get_logger("MonitoringService")
        self.logger.info("Monitoring service initialized")
        
        # Performance optimization: Cache metrics
        self._metrics_cache: Optional[Dict] = None
        self._cache_time = 0
        self._cache_ttl = 0.5  # Cache for 500ms to reduce CPU calls
        
        # Pre-calculate disk path (Windows optimization)
        try:
            import os
            self._disk_path = os.path.expanduser('~')  # Use home directory for Windows
        except:
            self._disk_path = '/'
    
    def get_system_metrics(self) -> Dict:
        """Get current system metrics with caching"""
        current_time = time.time()
        
        # Return cached metrics if still valid
        if self._metrics_cache and (current_time - self._cache_time) < self._cache_ttl:
            return self._metrics_cache
        
        try:
            # CPU usage - use non-blocking call
            cpu_percent = psutil.cpu_percent(interval=None)  # Non-blocking
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used = memory.used / (1024**3)  # GB
            memory_total = memory.total / (1024**3)  # GB
            
            # Disk usage - cache path to avoid repeated lookups
            try:
                disk = psutil.disk_usage(self._disk_path)
            except:
                # Fallback to root
                disk = psutil.disk_usage('/')
            
            disk_percent = disk.percent
            disk_used = disk.used / (1024**3)  # GB
            disk_total = disk.total / (1024**3)  # GB
            
            metrics = {
                'cpu': {
                    'percent': cpu_percent
                },
                'memory': {
                    'percent': memory_percent,
                    'used_gb': memory_used,
                    'total_gb': memory_total
                },
                'disk': {
                    'percent': disk_percent,
                    'used_gb': disk_used,
                    'total_gb': disk_total
                }
            }
            
            # Update cache
            self._metrics_cache = metrics
            self._cache_time = current_time
            
            return metrics
        except Exception as e:
            self.logger.error(f"Failed to get system metrics: {e}")
            return self._metrics_cache or {}

