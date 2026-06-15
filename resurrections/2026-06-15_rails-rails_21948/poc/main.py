import http.server
import urllib.parse
import json
import os
import time
import threading

class RequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == '/form':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            csrf_token = os.urandom(32).hex()
            self.wfile.write(f'<form action="/submit" method="post"><input type="hidden" name="csrf_token" value="{csrf_token}"><input type="submit" value="Submit"></form>'.encode())
        elif parsed_path.path == '/submit':
            try:
                csrf_token = self.r.headers['Cookie'].split('=')[1]
            except (KeyError, IndexError):
                self.send_response(403)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'CSRF token missing or invalid')
                return
            if csrf_token != self.r.POST.get('csrf_token'):
                self.send_response(403)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'CSRF token mismatch')
                return
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Form submitted successfully')
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not found')

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.r.read(content_length)
        self.r.POST = urllib.parse.parse_qs(body.decode())
        self.do_GET()

def run_server():
    server_address = ('', 8000)
    httpd = http.server.HTTPServer(server_address, RequestHandler)
    print('Server running on port 8000...')
    httpd.serve_forever()

if __name__ == '__main__':
    try:
        run_server()
    except KeyboardInterrupt:
        print('Server stopped')