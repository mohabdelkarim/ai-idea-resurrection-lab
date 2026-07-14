import os
import sys

class Railtie:
    def __init__(self):
        print("Initializing Railtie")

class Engine(Railtie):
    def __init__(self):
        super().__init__()
        print("Initializing Engine")

    def run(self):
        print("Running Engine")

class Application(Railtie):
    def __init__(self):
        super().__init__()
        print("Initializing Application")

    def run(self):
        print("Running Application")

def main():
    try:
        app = Application()
        app.run()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()