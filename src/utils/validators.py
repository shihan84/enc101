"""
Input validation utilities
"""

import re
from urllib.parse import urlparse
from typing import Optional


def validate_url(url: str, schemes: list = None):
    """
    Validate URL format
    
    Args:
        url: URL string to validate
        schemes: Allowed URL schemes (default: http, https, srt, udp, tcp)
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url or not url.strip():
        return False, "URL cannot be empty"
    
    schemes = schemes or ['http', 'https', 'srt', 'udp', 'tcp', 'file']
    
    # Handle SRT URLs
    if url.startswith('srt://') or url.startswith('srt:'):
        # Parse SRT URL: srt://host:port?streamid=...
        url_clean = url.replace('srt://', '').replace('srt:', '')
        if '?' in url_clean:
            host_port = url_clean.split('?')[0]
        else:
            host_port = url_clean
        
        if ':' in host_port:
            host, port = host_port.split(':', 1)
            if not validate_port(port)[0]:
                return False, "Invalid SRT port number"
        return True, None
    
    # Handle file paths
    if url.startswith('file://') or not url.startswith(('http://', 'https://', 'udp://', 'tcp://')):
        # Check if it's a valid file path
        if url.startswith('file://'):
            url = url[7:]
        try:
            from pathlib import Path
            path = Path(url)
            # Just check if path format is valid, not if file exists
            return True, None
        except Exception:
            return False, "Invalid file path format"
    
    # Parse standard URLs
    try:
        parsed = urlparse(url)
        if parsed.scheme not in schemes:
            return False, f"URL scheme must be one of: {', '.join(schemes)}"
        
        if parsed.scheme in ['http', 'https'] and not parsed.netloc:
            return False, "HTTP/HTTPS URL must include hostname"
        
        return True, None
    except Exception as e:
        return False, f"Invalid URL format: {str(e)}"


def validate_port(port):
    """
    Validate port number
    
    Args:
        port: Port number (string or int)
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        port_num = int(port)
        if 1 <= port_num <= 65535:
            return True, None
        return False, "Port must be between 1 and 65535"
    except (ValueError, TypeError):
        return False, "Port must be a valid number"


def validate_pid(pid, min_val: int = 32, max_val: int = 8190):
    """
    Validate PID (Packet Identifier) value
    
    Args:
        pid: PID value (string or int)
        min_val: Minimum allowed value
        max_val: Maximum allowed value
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        pid_num = int(pid)
        if min_val <= pid_num <= max_val:
            return True, None
        return False, f"PID must be between {min_val} and {max_val}"
    except (ValueError, TypeError):
        return False, "PID must be a valid number"


def validate_latency(latency):
    """
    Validate SRT latency value
    
    Args:
        latency: Latency in milliseconds
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        latency_num = int(latency)
        if 100 <= latency_num <= 10000:
            return True, None
        return False, "Latency must be between 100 and 10000 milliseconds"
    except (ValueError, TypeError):
        return False, "Latency must be a valid number"


def validate_event_id(event_id):
    """
    Validate SCTE-35 event ID
    
    Args:
        event_id: Event ID value
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        event_id_num = int(event_id)
        if 10000 <= event_id_num <= 99999:
            return True, None
        return False, "Event ID must be between 10000 and 99999"
    except (ValueError, TypeError):
        return False, "Event ID must be a valid number"


def validate_file_path(file_path: str, must_exist: bool = False):
    """
    Validate file path
    
    Args:
        file_path: File path string
        must_exist: Whether file must exist
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file_path or not file_path.strip():
        return False, "File path cannot be empty"
    
    try:
        from pathlib import Path
        path = Path(file_path)
        
        # Check for path traversal attempts
        if '..' in str(path) or path.is_absolute() and not path.resolve().is_absolute():
            return False, "Invalid file path (path traversal detected)"
        
        if must_exist and not path.exists():
            return False, f"File does not exist: {file_path}"
        
        return True, None
    except Exception as e:
        return False, f"Invalid file path: {str(e)}"


def validate_stream_id(stream_id: str):
    """
    Validate SRT stream ID
    
    Args:
        stream_id: Stream ID string
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not stream_id:
        return True, None  # Empty stream ID is valid
    
    if len(stream_id) > 512:
        return False, "Stream ID must be 512 characters or less"
    
    # Check for potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', '\n', '\r']
    if any(char in stream_id for char in dangerous_chars):
        return False, "Stream ID contains invalid characters"
    
    return True, None


def validate_duration(duration: int, min_val: int = 0, max_val: int = 86400):
    """
    Validate duration in seconds
    
    Args:
        duration: Duration in seconds
        min_val: Minimum allowed value
        max_val: Maximum allowed value (default: 24 hours)
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        duration_num = int(duration)
        if min_val <= duration_num <= max_val:
            return True, None
        return False, f"Duration must be between {min_val} and {max_val} seconds"
    except (ValueError, TypeError):
        return False, "Duration must be a valid number"


def validate_ip_address(ip: str):
    """
    Validate IP address format
    
    Args:
        ip: IP address string
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not ip or not ip.strip():
        return False, "IP address cannot be empty"
    
    # IPv4 pattern
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    # IPv6 pattern (simplified)
    ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|^::1$|^::$'
    
    import re
    if re.match(ipv4_pattern, ip):
        parts = ip.split('.')
        if all(0 <= int(part) <= 255 for part in parts):
            return True, None
        return False, "Invalid IPv4 address"
    elif re.match(ipv6_pattern, ip) or ip == 'localhost':
        return True, None
    else:
        return False, "Invalid IP address format"


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """
    Sanitize string input
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
    
    Returns:
        Sanitized string
    """
    if not value:
        return ""
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Truncate if too long
    if len(value) > max_length:
        value = value[:max_length]
    
    # Strip whitespace
    value = value.strip()
    
    return value


def validate_numeric_range(value, min_val, max_val, value_name: str = "Value"):
    """
    Validate numeric value is within range
    
    Args:
        value: Numeric value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        value_name: Name of the value for error messages
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        num_value = int(value) if isinstance(value, (int, float, str)) else None
        if num_value is None:
            return False, f"{value_name} must be a valid number"
        
        if min_val <= num_value <= max_val:
            return True, None
        return False, f"{value_name} must be between {min_val} and {max_val}"
    except (ValueError, TypeError):
        return False, f"{value_name} must be a valid number"

