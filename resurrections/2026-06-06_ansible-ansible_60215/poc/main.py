import os
import pathlib
import sys

try:
    import jinja2
    import PyYAML
    import cryptography
    import packaging
    import resolvelib
except ImportError:
    print("Missing required dependencies")
    sys.exit(1)

def get_ansible_source_root():
    return pathlib.Path(__file__).resolve().parents

def get_collection_root():
    return pathlib.Path(os.getcwd()).resolve()

def validate_directory(possible_roots):
    for root in possible_roots:
        if get_collection_root().is_relative_to(root):
            return True
    return False

def main():
    ansible_source_root = get_ansible_source_root()
    possible_roots = [pathlib.Path('/ansible')]  # Default ansible source root
    collection_root = get_collection_root()

    # Check if running from ansible source
    if validate_directory(ansible_source_root):
        print("Running from ansible source")
        return

    # Check if running from collection root
    if validate_directory([collection_root]):
        print("Running from collection root")
        return

    # Check if running from a subdirectory of the collection root
    for parent in collection_root.parents:
        if validate_directory([parent]):
            print("Running from subdirectory of collection root")
            return

    print("ERROR: The current working directory must be at or below one of:")
    for root in ansible_source_root:
        print(f" - Ansible source: {root}")
    print(f" - Ansible collection: {collection_root}")
    sys.exit(1)

if __name__ == '__main__':
    main()