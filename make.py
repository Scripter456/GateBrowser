#!/usr/bin/env python3
"""
GateBrowser Build TUI & Manager (make.py)
Interactive Terminal UI for configuring build versions, selecting target OS editions,
and triggering Makefile / build targets.
"""

import sys
import os
import json
import subprocess
import re
import platform

PACKAGE_JSON_PATH = os.path.join(os.path.dirname(__file__), "package.json")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_key():
    """Cross-platform single character / arrow key reader."""
    if os.name == 'nt':
        import msvcrt
        ch = msvcrt.getch()
        if ch in (b'\x00', b'\xe0'):
            ch2 = msvcrt.getch()
            if ch2 == b'H': return 'UP'
            elif ch2 == b'P': return 'DOWN'
            elif ch2 == b'K': return 'LEFT'
            elif ch2 == b'M': return 'RIGHT'
        elif ch == b'\r':
            return 'ENTER'
        elif ch == b'\x1b':
            return 'ESC'
        elif ch == b'\x03':
            raise KeyboardInterrupt
        else:
            try:
                return ch.decode('utf-8')
            except UnicodeDecodeError:
                return ''
    else:
        import tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    if ch3 == 'A': return 'UP'
                    elif ch3 == 'B': return 'DOWN'
                    elif ch3 == 'C': return 'RIGHT'
                    elif ch3 == 'D': return 'LEFT'
                return 'ESC'
            elif ch == '\n' or ch == '\r':
                return 'ENTER'
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def read_version():
    try:
        with open(PACKAGE_JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('version', '1.0.0')
    except Exception:
        return '1.0.0'

def write_version(new_version):
    try:
        with open(PACKAGE_JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        data['version'] = new_version
        with open(PACKAGE_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving version: {e}")
        return False

def run_shell(cmd):
    print(f"\n[EXEC] {cmd}\n" + "="*50)
    subprocess.run(cmd, shell=True)
    print("="*50)
    print("Press ENTER to return to menu...")
    input()

def prompt_new_version(current_ver):
    clear_screen()
    print("==================================================")
    print("           CHANGE GATEBROWSER VERSION             ")
    print("==================================================")
    print(f"Current version: {current_ver}\n")
    print("Format: Major.Minor.Patch (e.g. 1.0.1, 1.1.0, 2.0.0)")
    new_v = input("Enter new version (or leave blank to cancel): ").strip()
    if new_v:
        if re.match(r'^\d+\.\d+\.\d+$', new_v):
            write_version(new_v)
            print(f"Successfully updated version to {new_v}!")
        else:
            print("Invalid semver format! Changes discarded.")
        input("Press ENTER to continue...")

def main():
    selected_edition_idx = 0
    editions = ["Windows (nsis x64)", "Linux (AppImage)", "macOS (dmg)"]
    edition_targets = ["pack:win", "pack:linux", "pack:mac"]

    selected_menu_idx = 0
    menu_items = [
        "Change Target Edition (Current: {})",
        "Change Build Version",
        "Install Dependencies (npm install)",
        "Run Browser in Dev Mode (npm start)",
        "Build Standalone Installer for Selected Edition",
        "Exit"
    ]

    while True:
        ver = read_version()
        clear_screen()
        print("\033[96m" + r"""
   _____       _       ____                                 
  / ____|     | |     |  _ \                                
 | |  __  __ _| |_ ___| |_) |_ __ _____      _____  ___ _ __ 
 | | |_ |/ _` | __/ _ \  _ <| '__/ _ \ \ /\ / / __|/ _ \ '__|
 | |__| | (_| | ||  __/ |_) | | | (_) \ V  V /\__ \  __/ |   
  \_____|\__,_|\__\___|____/|_|  \___/ \_/\_/ |___/\___|_|   
        """ + "\033[0m")
        print("  \033[90mChromium-Powered Next-Gen Desktop Browser TUI\033[0m")
        print("="*58)
        print(f"  \033[92mVersion:\033[0m  {ver}")
        print(f"  \033[93mTarget Edition:\033[0m {editions[selected_edition_idx]}")
        print("="*58)
        print("  Use [UP/DOWN] arrows to navigate, [ENTER] to select\n")

        for idx, item in enumerate(menu_items):
            label = item
            if idx == 0:
                label = f"Target Edition: [ {editions[selected_edition_idx]} ] (Press ENTER to toggle)"
            elif idx == 1:
                label = f"Build Version: [ {ver} ] (Press ENTER to edit)"

            if idx == selected_menu_idx:
                print(f"  \033[92m>\033[0m \033[1m\033[97m{label}\033[0m")
            else:
                print(f"    \033[90m{label}\033[0m")

        print("\n" + "="*58)

        try:
            key = get_key()
        except KeyboardInterrupt:
            print("\nExiting...")
            break

        if key == 'UP':
            selected_menu_idx = (selected_menu_idx - 1) % len(menu_items)
        elif key == 'DOWN':
            selected_menu_idx = (selected_menu_idx + 1) % len(menu_items)
        elif key == 'ENTER':
            if selected_menu_idx == 0:
                selected_edition_idx = (selected_edition_idx + 1) % len(editions)
            elif selected_menu_idx == 1:
                prompt_new_version(ver)
            elif selected_menu_idx == 2:
                cmd = "cmd.exe /c \"npm install\"" if os.name == 'nt' else "npm install"
                run_shell(cmd)
            elif selected_menu_idx == 3:
                cmd = "cmd.exe /c \"npm start\"" if os.name == 'nt' else "npm start"
                run_shell(cmd)
            elif selected_menu_idx == 4:
                target = edition_targets[selected_edition_idx]
                cmd = f'cmd.exe /c "npm run {target}"' if os.name == 'nt' else f"npm run {target}"
                run_shell(cmd)
            elif selected_menu_idx == 5:
                print("\nGoodbye!")
                break
        elif key in ('q', 'Q', 'ESC'):
            print("\nGoodbye!")
            break

if __name__ == '__main__':
    main()
