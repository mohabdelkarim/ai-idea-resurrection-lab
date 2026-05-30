import json
import pkg_resources
from packaging.requirements import Requirement
from packaging.version import Version
import subprocess
import sys

def install_package(package):
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {package}: {e}")
        sys.exit(1)

def check_dependency(package, version):
    try:
        dist = pkg_resources.get_distribution(package)
        if Version(dist.version) != Version(version):
            print(f"{package} version mismatch: expected {version}, got {dist.version}")
            return False
    except pkg_resources.DistributionNotFound:
        print(f"{package} not installed")
        return False
    return True

def main():
    # Original dependencies
    dependencies = {
        "charset_normalizer": ">=2,<4",
        "idna": ">=2.5,<4",
        "urllib3": ">=1.26,<3",
        "certifi": ">=2023.5.7"
    }

    # Update idna dependency to allow version 3.0 and above
    dependencies["idna"] = ">=2.5"

    # Install requests with updated dependencies
    install_package("requests")

    # Check if idna version 3.0 is installed
    install_package("idna==3.0")

    # Verify dependencies
    for package, version in dependencies.items():
        if not check_dependency(package, version):
            print(f"Dependency verification failed for {package}")
            sys.exit(1)

if __name__ == '__main__':
    main()