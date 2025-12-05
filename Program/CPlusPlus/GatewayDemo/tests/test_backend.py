#!/usr/bin/env python3
"""
简单的测试后端服务器
用于测试网关的转发功能
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import sys
import json

class TestBackendHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        response = {
            'message': 'Hello from test backend',
            'path': self.path,
            'method': 'GET',
            'port': self.server.server_port
        }
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode() if content_length > 0 else ''
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        response = {
            'message': 'POST received',
            'path': self.path,
            'method': 'POST',
            'body': body,
            'port': self.server.server_port
        }
        
        self.wfile.write(json.dumps(response).encode())
    
    def log_message(self, format, *args):
        print(f"[Backend:{self.server.server_port}] {format % args}")

def run_server(port):
    server = HTTPServer(('localhost', port), TestBackendHandler)
    print(f"Test backend server running on port {port}")
    print(f"Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\nShutting down backend on port {port}")
        server.shutdown()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9001
    run_server(port)
