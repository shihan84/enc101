"""
REST API Server
Provides HTTP API for remote control and automation
"""

import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs
from typing import Optional, Callable

from ..core.logger import get_logger
from ..utils.rate_limiter import RateLimiter


class APIRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for API"""
    
    def __init__(self, *args, routes=None, rate_limiter=None, **kwargs):
        self.routes = routes or {}
        self.rate_limiter = rate_limiter
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        self._handle_request('GET')
    
    def do_POST(self):
        """Handle POST requests"""
        self._handle_request('POST')
    
    def do_PUT(self):
        """Handle PUT requests"""
        self._handle_request('PUT')
    
    def do_DELETE(self):
        """Handle DELETE requests"""
        self._handle_request('DELETE')
    
    def _handle_request(self, method: str):
        """Handle HTTP request"""
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        
        # Rate limiting (skip for health check endpoints)
        if self.rate_limiter and path not in ['/health', '/api/health']:
            client_ip = self.client_address[0] if hasattr(self, 'client_address') else 'unknown'
            is_allowed, remaining = self.rate_limiter.is_allowed(client_ip)
            
            if not is_allowed:
                self._send_response(429, {
                    'error': 'Rate limit exceeded',
                    'message': f'Too many requests. Limit: {self.rate_limiter.max_requests} per {self.rate_limiter.window_seconds} seconds'
                })
                return
        
        # Find route handler
        handler = self.routes.get((method, path))
        if not handler:
            self._send_response(404, {'error': 'Not found'})
            return
        
        # Get request body for POST/PUT
        body = None
        if method in ['POST', 'PUT']:
            content_length = int(self.headers.get('Content-Length', 0))
            # Limit request body size (10MB max)
            if content_length > 10 * 1024 * 1024:
                self._send_response(413, {'error': 'Request entity too large'})
                return
            if content_length > 0:
                try:
                    body = json.loads(self.rfile.read(content_length).decode('utf-8'))
                except json.JSONDecodeError:
                    self._send_response(400, {'error': 'Invalid JSON in request body'})
                    return
        
        # Call handler
        try:
            response = handler(query, body)
            # Special handling for Prometheus metrics (text/plain)
            if path == '/metrics' and isinstance(response, str):
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain; version=0.0.4')
                self.end_headers()
                self.wfile.write(response.encode('utf-8'))
            else:
                self._send_response(200, response)
        except Exception as e:
            self._send_response(500, {'error': str(e)})
    
    def _send_response(self, status: int, data: dict):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        # Add rate limit headers
        if self.rate_limiter:
            client_ip = self.client_address[0] if hasattr(self, 'client_address') else 'unknown'
            _, remaining = self.rate_limiter.is_allowed(client_ip)
            self.send_header('X-RateLimit-Limit', str(self.rate_limiter.max_requests))
            self.send_header('X-RateLimit-Remaining', str(remaining))
            self.send_header('X-RateLimit-Window', str(self.rate_limiter.window_seconds))
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


class APIServer:
    """REST API server"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8080, rate_limit: int = 100):
        self.logger = get_logger("APIServer")
        self.host = host
        self.port = port
        self.routes = {}
        self.server: Optional[HTTPServer] = None
        self.thread: Optional[threading.Thread] = None
        self._running = False
        # Rate limiting: max_requests per 60 seconds
        self.rate_limiter = RateLimiter(max_requests=rate_limit, window_seconds=60)
    
    def add_route(self, method: str, path: str, handler: Callable):
        """Add route handler"""
        self.routes[(method, path)] = handler
        self.logger.debug(f"Added route: {method} {path}")
    
    def start(self):
        """Start API server"""
        if self._running:
            self.logger.warning("API server already running")
            return
        
        def handler(*args, **kwargs):
            return APIRequestHandler(*args, routes=self.routes, rate_limiter=self.rate_limiter, **kwargs)
        
        self.server = HTTPServer((self.host, self.port), handler)
        
        def run_server():
            self._running = True
            self.logger.info(f"API server started on http://{self.host}:{self.port}")
            self.server.serve_forever()
        
        self.thread = threading.Thread(target=run_server, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop API server"""
        if not self._running:
            return
        
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        
        self._running = False
        self.logger.info("API server stopped")
    
    @property
    def is_running(self) -> bool:
        """Check if server is running"""
        return self._running

