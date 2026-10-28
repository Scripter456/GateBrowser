#!/usr/bin/env python3
"""
GateBrowser Build TUI & Manager (make.py)
Interactive Terminal UI for configuring build versions, selecting target OS editions,
and triggering Makefile targets.
"""

import sys
import os
import json
import subprocess
import re
import shutil

# Ensure working directory is always the GateBrowser project root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

PACKAGE_JSON_PATH = os.path.join(BASE_DIR, "package.json")
MAKEFILE_PATH = os.path.join(BASE_DIR, "Makefile")

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
            return data.get('version', '0.0.1')
    except Exception:
        return '0.0.1'

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

def resolve_make_cmd(target):
    """Finds make command or falls back gracefully to direct commands if make is missing."""
    make_bin = shutil.which("make")
    if make_bin:
        return f'"{make_bin}" -f "{MAKEFILE_PATH}" {target}'
    # Direct fallback if make command is somehow not in PATH
    fallback_map = {
        "install": 'cmd.exe /c "npm install && node node_modules\\electron\\install.js"',
        "start": 'cmd.exe /c "npm start"',
        "exe": 'cmd.exe /c "npm run pack:win-portable"',
        "build-win": 'cmd.exe /c "npm run pack:win"',
        "build-linux": 'cmd.exe /c "npm run pack:linux"',
        "build-mac": 'cmd.exe /c "npm run pack:mac"',
        "clean": 'cmd.exe /c "if exist dist rmdir /s /q dist"'
    }
    return fallback_map.get(target, f"make {target}")

def run_make_target(target):
    cmd = resolve_make_cmd(target)
    print(f"\n[MAKEFILE] Running target: '{target}'")
    print(f"[CMD] {cmd}\n" + "="*50)
    subprocess.run(cmd, shell=True, cwd=BASE_DIR)
    print("="*50)
    print("Press ENTER to return to menu...")
    input()

def prompt_new_version(current_ver):
    clear_screen()
    print("==================================================")
    print("           CHANGE GATEBROWSER VERSION             ")
    print("==================================================")
    print(f"Current version: {current_ver}\n")
    print("Format: Major.Minor.Patch (e.g. 0.0.2, 0.1.0, 1.0.0)")
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
    editions = ["Windows (nsis + standalone .exe)", "Linux (AppImage)", "macOS (dmg)"]
    make_targets = ["build-win", "build-linux", "build-mac"]

    selected_menu_idx = 0
    menu_items = [
        "Change Target Edition (Current: {})",
        "Change Build Version",
        "Compile Standalone .exe (make exe)",
        "Build for Selected Edition (make)",
        "Install Dependencies (make install)",
        "Run Browser in Dev Mode (make start)",
        "Clean Build Artifacts (make clean)",
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
                run_make_target("exe")
            elif selected_menu_idx == 3:
                target = make_targets[selected_edition_idx]
                run_make_target(target)
            elif selected_menu_idx == 4:
                run_make_target("install")
            elif selected_menu_idx == 5:
                run_make_target("start")
            elif selected_menu_idx == 6:
                run_make_target("clean")
            elif selected_menu_idx == 7:
                print("\nGoodbye!")
                break
        elif key in ('q', 'Q', 'ESC'):
            print("\nGoodbye!")
            break

if __name__ == '__main__':
    main()
