import json
import pkg_resources
from packaging import version
import urllib3
import requests

def check_urllib3_version():
    try:
        urllib3_version = pkg_resources.get_distribution('urllib3').version
        print(f"urllib3 version: {urllib3_version}")
    except pkg_resources.DistributionNotFound:
        print("urllib3 is not installed")
        return

    if version.parse(urllib3_version) >= version.parse('2.0.0'):
        print("urllib3 version 2.0.0 or higher is installed")
    else:
        print("urllib3 version is lower than 2.0.0")

def check_requests_version():
    try:
        requests_version = pkg_resources.get_distribution('requests').version
        print(f"requests version: {requests_version}")
    except pkg_resources.DistributionNotFound:
        print("requests is not installed")
        return

def update_urllib3_dependency():
    try:
        with open('pyproject.toml', 'r') as f:
            data = f.read()
            print(data)
    except FileNotFoundError:
        print("pyproject.toml file not found")
        return

    # Update the urllib3 dependency range
    updated_data = data.replace("urllib3>=1.26,<3", "urllib3>=1.26")
    with open('pyproject.toml', 'w') as f:
        f.write(updated_data)

def main():
    check_urllib3_version()
    check_requests_version()
    update_urllib3_dependency()
    try:
        response = requests.get('https://www.example.com')
        print(response.status_code)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()