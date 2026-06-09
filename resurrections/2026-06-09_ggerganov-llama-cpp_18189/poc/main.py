import configparser
import argparse
import time
import threading

class ModelManager:
    def __init__(self, unload_idle_seconds=300):
        self.models = {}
        self.unload_idle_seconds = unload_idle_seconds
        self.lock = threading.Lock()

    def load_model(self, model_name, model_path):
        with self.lock:
            if model_name not in self.models:
                self.models[model_name] = {'path': model_path, 'last_used': time.time()}
                print(f"Loaded model {model_name}")
            else:
                self.models[model_name]['last_used'] = time.time()

    def unload_model(self, model_name):
        with self.lock:
            if model_name in self.models:
                del self.models[model_name]
                print(f"Unloaded model {model_name}")

    def check_idle_models(self):
        with self.lock:
            current_time = time.time()
            for model_name, model_info in list(self.models.items()):
                if current_time - model_info['last_used'] > self.unload_idle_seconds:
                    self.unload_model(model_name)

    def start_idle_checker(self):
        def check_idle_models_periodically():
            while True:
                self.check_idle_models()
                time.sleep(10)  # Check every 10 seconds

        threading.Thread(target=check_idle_models_periodically).start()

def parse_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='config.ini')
    parser.add_argument('--unload-idle-seconds', type=int, default=300)
    args = parser.parse_args()

    config = parse_config(args.config)
    unload_idle_seconds = config.getint('global', 'unload-idle-seconds', fallback=args.unload_idle_seconds)

    model_manager = ModelManager(unload_idle_seconds)
    model_manager.start_idle_checker()

    # Example usage
    model_manager.load_model('model1', '/path/to/model1')
    model_manager.load_model('model2', '/path/to/model2')

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Exiting...")

if __name__ == '__main__':
    main()