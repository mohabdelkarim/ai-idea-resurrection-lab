import argparse
import os
import sys
from ansible_test._internal import ansible_test

def main():
    parser = argparse.ArgumentParser(description='Run ansible-test')
    parser.add_argument('--collection-root', help='Path to the collection root')
    args = parser.parse_args()

    if args.collection_root:
        os.environ['ANSIBLE_COLLECTION_ROOT'] = args.collection_root

    try:
        ansible_test.main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()