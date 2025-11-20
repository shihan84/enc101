"""
REST API for automation and remote control
"""

from .server import APIServer
from .routes import setup_routes

__all__ = ['APIServer', 'setup_routes']

