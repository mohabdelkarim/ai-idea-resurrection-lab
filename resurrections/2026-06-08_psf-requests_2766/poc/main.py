import threading
import requests
from requests import Session

def thread_safe_session_example():
    try:
        # Create a new Session object per thread
        session = Session()
        response = session.get('https://www.example.com')
        print(response.status_code)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

def non_thread_safe_session_example(session):
    try:
        response = session.get('https://www.example.com')
        print(response.status_code)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

def main():
    # Create a single Session object
    session = Session()
    print("Warning: This example is not thread-safe.")
    print("Creating one Session per thread is recommended.")
    threads = []
    for _ in range(5):
        t = threading.Thread(target=non_thread_safe_session_example, args=(session,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    print("Thread-safe example:")
    threads = []
    for _ in range(5):
        t = threading.Thread(target=thread_safe_session_example)
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
if __name__ == '__main__':
    main()