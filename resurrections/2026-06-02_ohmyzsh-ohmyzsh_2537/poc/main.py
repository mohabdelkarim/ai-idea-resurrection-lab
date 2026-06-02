import os
import sys

def load_config(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            return content
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def update_config(file_path, config_str):
    try:
        with open(file_path, 'a') as file:
            file.write(config_str + '\n')
    except Exception as e:
        print(f"An error occurred while updating {file_path}: {e}")

def check_share_history(config_content):
    return 'setopt share_history' in config_content

def main():
    home_dir = os.path.expanduser('~')
    zshrc_path = os.path.join(home_dir, '.zshrc')
    config_content = load_config(zshrc_path)
    if config_content is not None:
        if check_share_history(config_content):
            print("share_history is enabled.")
            response = input("Do you want to disable share_history? (yes/no): ")
            if response.lower() == 'yes':
                update_config(zshrc_path, 'unsetopt share_history')
                print("share_history has been disabled.")
            else:
                print("share_history remains enabled.")
        else:
            print("share_history is already disabled.")
    else:
        print("Failed to load .zshrc")

if __name__ == '__main__':
    main()