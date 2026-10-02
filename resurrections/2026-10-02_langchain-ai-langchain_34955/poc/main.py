import json, urllib.request, urllib.error, time, threading, asyncio, sys, traceback

# Minimal stand‑in for LangChain's Settings container
class Settings:
    """Global configuration holder for the anonymizer.

    In real LangChain this would be part of the library's settings system.
    """
    endpoint_url: str = "http://localhost:8000/anonymize"
    auth_token: str = ""
    timeout_seconds: int = 5
    max_retries: int = 3
    redaction_rules: dict = {}

# Simple external client that can be used synchronously or asynchronously
class ExternalAnonymizerClient:
    def __init__(self, endpoint_url: str, auth_token: str = "", timeout: int = 5, max_retries: int = 3):
        self.endpoint_url = endpoint_url
        self.auth_token = auth_token
        self.timeout = timeout
        self.max_retries = max_retries

    def _make_request(self, payload: dict) -> dict:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(self.endpoint_url, data=data, method='POST')
        req.add_header('Content-Type', 'application/json')
        if self.auth_token:
            req.add_header('Authorization', f'Bearer {self.auth_token}')
        for attempt in range(1, self.max_retries + 1):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    resp_data = resp.read().decode('utf-8')
                    return json.loads(resp_data)
            except urllib.error.URLError as e:
                if attempt == self.max_retries:
                    raise
                time.sleep(0.1 * attempt)  # simple back‑off
        return {}

    def anonymize(self, text: str) -> str:
        """Synchronous call to the external service."""
        payload = {"text": text, "rules": Settings.redaction_rules}
        try:
            result = self._make_request(payload)
            return result.get('anonymized_text', text)
        except Exception as exc:
            # In case of failure, return original text but log error
            sys.stderr.write(f"[ExternalAnonymizerClient] error: {exc}\n")
            return text

    async def anonymize_async(self, text: str) -> str:
        """Asynchronous wrapper using a thread pool to avoid blocking the event loop."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.anonymize, text)

# Base callback handler stub – in the real library this provides many hooks
class BaseCallbackHandler:
    def on_message(self, message: dict) -> dict:
        """Process a message and return possibly modified version.
        Sub‑classes should override this method.
        """
        return message

# The actual anonymizer callback that integrates with the agent flow
class AnonymizerCallback(BaseCallbackHandler):
    def __init__(self, client: ExternalAnonymizerClient = None, async_mode: bool = False):
        self.client = client or ExternalAnonymizerClient(
            Settings.endpoint_url,
            Settings.auth_token,
            Settings.timeout_seconds,
            Settings.max_retries,
        )
        self.async_mode = async_mode

    def process_message(self, message: dict) -> dict:
        """Entry point used by the agent to sanitize a message.
        Expected message format: {"role": "user"|"assistant"|"tool", "content": "..."}
        """
        content = message.get('content', '')
        if not isinstance(content, str) or not content:
            return message
        try:
            if self.async_mode:
                # Run async anonymization in a new event loop if none exists
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                sanitized = loop.run_until_complete(self.client.anonymize_async(content))
                loop.close()
            else:
                sanitized = self.client.anonymize(content)
            new_msg = dict(message)
            new_msg['content'] = sanitized
            return new_msg
        except Exception as exc:
            sys.stderr.write(f"[AnonymizerCallback] failed to anonymize: {exc}\n")
            traceback.print_exc(file=sys.stderr)
            return message

    # Hook used by the agent framework – simply forwards to process_message
    def on_message(self, message: dict) -> dict:
        return self.process_message(message)

# Simple demonstration of how the callback could be used in an agent loop
def demo_agent_flow(messages):
    """Simulate an agent processing a list of messages with the callback.
    Each message passes through the AnonymizerCallback before being printed.
    """
    callback = AnonymizerCallback(async_mode=False)
    for msg in messages:
        sanitized_msg = callback.on_message(msg)
        print(f"[{sanitized_msg.get('role')}] {sanitized_msg.get('content')}")

# Mock server for local testing – runs in a background thread
def start_mock_server(port=8000):
    from http.server import BaseHTTPRequestHandler, HTTPServer
    class MockHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8')
            try:
                data = json.loads(body)
                text = data.get('text', '')
                # Very naive "anonymization": replace digits with X
                anonymized = ''.join('X' if c.isdigit() else c for c in text)
                response = {'anonymized_text': anonymized}
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.end_headers()
        def log_message(self, *args):
            return  # suppress console output
    server = HTTPServer(('localhost', port), MockHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server

if __name__ == '__main__':
    # Start mock external service
    mock_srv = start_mock_server()
    # Example messages containing PII (phone numbers)
    msgs = [
        {'role': 'user', 'content': 'My phone is 123-456-7890.'},
        {'role': 'assistant', 'content': 'Sure, I will note 987-654-3210 for you.'},
        {'role': 'tool', 'content': 'Fetched record ID 5555.'},
    ]
    demo_agent_flow(msgs)
    # Clean up mock server
    mock_srv.shutdown()