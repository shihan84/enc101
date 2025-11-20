#!/usr/bin/env python3
"""
Simple HTTP Server with CORS Support for HLS/DASH Content
Run this to serve your generated HLS/DASH files to a web player
"""
import http.server
import socketserver
import sys
import os

# Add CORS headers to responses
class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Max-Age', '86400')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        """Suppress log messages"""
        pass

if __name__ == '__main__':
    PORT = 8000
    
    if len(sys.argv) > 1:
        try:
            PORT = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port: {sys.argv[1]}")
            sys.exit(1)
    
    if len(sys.argv) > 2:
        os.chdir(sys.argv[2])
    
    Handler = CORSRequestHandler
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🌐 CORS-enabled HTTP server running on http://localhost:{PORT}")
        print(f"📁 Serving directory: {os.getcwd()}")
        print("📺 Use this URL in your player (video.js, hls.js, etc.)")
        print("🛑 Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n✅ Server stopped")

