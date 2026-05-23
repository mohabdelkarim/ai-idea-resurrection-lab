import socket
import threading
import json

class RedisServer:
    def __init__(self, host='localhost', port=6379):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()
        print(f"Redis server listening on {host}:{port}")

    def handle_client(self, conn, addr):
        print(f"New connection from {addr}")
        while True:
            try:
                request = conn.recv(1024)
                if not request:
                    break
                request = request.decode('utf-8')
                print(f"Received request: {request}")
                response = self.process_request(request)
                conn.sendall(response.encode('utf-8'))
            except Exception as e:
                print(f"Error handling client: {e}")
                break
        conn.close()

    def process_request(self, request):
        try:
            request = json.loads(request)
            if request['command'] == 'unexpected_input':
                return json.dumps({'error': 'Unexpected input received'}).encode('utf-8')
            else:
                return json.dumps({'error': 'Unknown command'}).encode('utf-8')
        except json.JSONDecodeError:
            return json.dumps({'error': 'Invalid JSON'}).encode('utf-8')
        except Exception as e:
            return json.dumps({'error': str(e)}).encode('utf-8')

    def start(self):
        print("Starting Redis server...")
        while True:
            conn, addr = self.server.accept()
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()

if __name__ == '__main__':
    server = RedisServer()
    server.start()