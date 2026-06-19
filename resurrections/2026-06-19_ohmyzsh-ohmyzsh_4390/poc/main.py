import os
import sys

def check_zshrc():
    zshrc_path = os.path.expanduser('~/.zshrc')
    return os.path.exists(zshrc_path)

def warn_user(zshrc_path):
    print(f"Warning: ~/.zshrc file already exists at {zshrc_path}.")
    response = input("Do you want to overwrite it? (y/n): ")
    return response.lower() == 'y'

def install_ohmyzsh():
    # Simulating oh-my-zsh installation
    print("Installing oh-my-zsh...")
    # Add your installation code here
    print("Oh-my-zsh installed successfully.")

def main():
    try:
        zshrc_exists = check_zshrc()
        if zshrc_exists:
            zshrc_path = os.path.expanduser('~/.zshrc')
            overwrite = warn_user(zshrc_path)
            if not overwrite:
                print("Installation cancelled.")
                sys.exit(0)
        install_ohmyzsh()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()