import os
import sys
import tty
import termios

def get_char():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def main():
    print("Ctrl+Backspace and Ctrl+Delete Keybindings Test")
    print("-----------------------------------------------")
    print("Press Ctrl+Backspace to delete a word before the cursor (backward-kill-word)")
    print("Press Ctrl+Delete to delete a word after the cursor (kill-word)")
    print("Type 'exit' to quit")
    
    while True:
        user_input = input("ohmyzsh> ")
        if user_input == "exit":
            break
        
        # Simulate backward-kill-word (Ctrl+Backspace)
        if user_input.startswith("\x08"):  # \x08 is Ctrl+Backspace
            user_input = user_input[:-1]
            print("Backward kill word: " + user_input)
            continue
        
        # Simulate kill-word (Ctrl+Delete)
        if user_input.startswith("\x1b[3;5~"):  # \x1b[3;5~ is Ctrl+Delete
            print("Kill word")
            continue
        
        print(user_input)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print("An error occurred: " + str(e))
    finally:
        os.system('stty sane')