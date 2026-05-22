import sys
import threading
import time

class GILTest:
    def __init__(self):
        self.lock = threading.Lock()
        self.value = 0

    def increment(self):
        with self.lock:
            self.value += 1

    def get_value(self):
        with self.lock:
            return self.value

def worker(gil_test):
    try:
        for _ in range(100000):
            gil_test.increment()
    except Exception as e:
        print(f"Worker exception: {e}")

def main():
    gil_test = GILTest()

    threads = []
    for _ in range(10):
        thread = threading.Thread(target=worker, args=(gil_test,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    print(f"Final value: {gil_test.get_value()}")

if __name__ == "__main__":
    main()