import os
import sys

class AuthenticationGenerator:
    def __init__(self, app_name):
        self.app_name = app_name

    def generate_controller(self):
        try:
            with open(f'{self.app_name}_controller.py', 'w') as f:
                f.write(f'class {self.app_name.capitalize()}Controller:
    def index(self):
        return "Hello, World!"
')
            print(f'Controller generated: {self.app_name}_controller.py')
        except Exception as e:
            print(f'Error generating controller: {e}')

    def generate_model(self):
        try:
            with open(f'{self.app_name}_model.py', 'w') as f:
                f.write(f'class {self.app_name.capitalize()}Model:
    def __init__(self):
        self.username = ""
        self.password = ""
')
            print(f'Model generated: {self.app_name}_model.py')
        except Exception as e:
            print(f'Error generating model: {e}')

    def generate_view(self):
        try:
            with open(f'{self.app_name}_view.py', 'w') as f:
                f.write(f'class {self.app_name.capitalize()}View:
    def __init__(self):
        self.template = ""
')
            print(f'View generated: {self.app_name}_view.py')
        except Exception as e:
            print(f'Error generating view: {e}')

    def generate_authentication(self):
        self.generate_controller()
        self.generate_model()
        self.generate_view()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python authentication_generator.py <app_name>")
        sys.exit(1)

    app_name = sys.argv[1]
    generator = AuthenticationGenerator(app_name)
    generator.generate_authentication()