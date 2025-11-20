"""
Custom exceptions for IBE-100 Enterprise
"""


class IBE100Exception(Exception):
    """Base exception for IBE-100"""
    pass


class ConfigurationError(IBE100Exception):
    """Configuration-related errors"""
    pass


class StreamError(IBE100Exception):
    """Stream processing errors"""
    pass


class SCTE35Error(IBE100Exception):
    """SCTE-35 related errors"""
    pass


class TSDuckError(IBE100Exception):
    """TSDuck integration errors"""
    pass


class ServiceError(IBE100Exception):
    """Service-related errors"""
    pass

