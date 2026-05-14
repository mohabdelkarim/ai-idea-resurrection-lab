import argparse
import subprocess
import json
import sys

def run_clang_tidy(file_path, skip_included_files=False):
    args = ["clang-tidy", file_path]
    if skip_included_files:
        args.append("--skip-included-files")

    try:
        output = subprocess.check_output(args, stderr=subprocess.STDOUT)
        return output.decode("utf-8")
    except subprocess.CalledProcessError as e:
        print(f"Error running clang-tidy: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Run clang-tidy with an option to skip included files")
    parser.add_argument("file_path", help="Path to the file to be linted")
    parser.add_argument("--skip-included-files", action="store_true", help="Skip analyzing included files")
    args = parser.parse_args()

    output = run_clang_tidy(args.file_path, args.skip_included_files)
    if output:
        print(output)

if __name__ == "__main__":
    main()