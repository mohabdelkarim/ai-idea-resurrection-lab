import streamlit as st
import requests
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import json

class StreamlitServer:
    def __init__(self, app):
        self.app = app
        self.routes = {}

    def route(self, path):
        def decorator(func):
            self.routes[path] = func
            return func
        return decorator

    def handle_request(self, request):
        parsed_path = urlparse(request.path)
        path = parsed_path.path
        if path in self.routes:
            try:
                data = self.routes[path](request)
                return data
            except Exception as e:
                return f"Error: {str(e)}"
        return None

class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, server):
        self.server = server
        super().__init__()

    def do_GET(self):
        data = self.server.handle_request(self)
        if data is not None:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(data.encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data = json.loads(body.decode())
        request = type('Request', (), {'path': self.path, 'data': data})
        data = self.server.handle_request(request)
        if data is not None:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(data.encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

def run_server(app, port=8080):
    server = StreamlitServer(app)
    httpd = HTTPServer(('localhost', port), lambda *args: RequestHandler(server))
    print(f"Server running on port {port}")
    httpd.serve_forever()

def main():
    @st.server.route('/api/data')
    def handle_api_data(request):
        return json.dumps({'message': 'Hello, World!'})

    st.write("Hello, Streamlit!")
    threading.Thread(target=run_server, args=(st.server,)).start()

if __name__ == '__main__':
    main()