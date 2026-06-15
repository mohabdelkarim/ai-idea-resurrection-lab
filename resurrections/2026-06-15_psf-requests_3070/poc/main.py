import requests
from requests import Session
import time
from urllib3.exceptions import TimeoutError

class TimeoutSession(Session):
    def __init__(self, timeout=5, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeout = timeout

    def request(self, method, url, *args, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        return super().request(method, url, *args, **kwargs)

def main():
    try:
        s = TimeoutSession(timeout=2)
        response = s.get('http://httpbin.org/ip')
        print(response.json())
    except TimeoutError:
        print('Timeout occurred')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    main()