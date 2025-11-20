"""
Helper utility functions
"""

import shutil
import os
from pathlib import Path
from typing import Optional


def find_tsduck() -> str:
    """
    Find TSDuck installation path
    
    Returns:
        Path to tsp.exe or 'tsp' if not found
    """
    paths = [
        "C:\\Program Files\\TSDuck\\bin\\tsp.exe",
        "C:\\TSDuck\\bin\\tsp.exe",
        "tsp.exe",  # Try PATH
        "tsp"  # Try PATH without extension
    ]
    
    for path in paths:
        if shutil.which(path) or os.path.exists(path):
            if os.path.exists(path):
                return path
            else:
                found = shutil.which(path)
                if found:
                    return found
    
    return "tsp"  # Fallback


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted string (e.g., "1h 23m 45s")
    """
    if seconds < 60:
        return f"{int(seconds)}s"
    
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    
    if minutes < 60:
        return f"{minutes}m {secs}s"
    
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    
    if hours < 24:
        return f"{hours}h {mins}m {secs}s"
    
    days = int(hours // 24)
    hrs = int(hours % 24)
    return f"{days}d {hrs}h {mins}m"


def format_bytes(bytes_count: int) -> str:
    """
    Format byte count to human-readable string
    
    Args:
        bytes_count: Number of bytes
    
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.2f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.2f} PB"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters
    
    Args:
        filename: Original filename
    
    Returns:
        Sanitized filename
    """
    # Remove invalid characters for Windows/Linux
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename


def ensure_directory(path: Path) -> Path:
    """
    Ensure directory exists, create if not
    
    Args:
        path: Directory path
    
    Returns:
        Path object
    """
    path.mkdir(parents=True, exist_ok=True)
    return path

