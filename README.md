# GateBrowser

GateBrowser is a fast, modern Chromium-based desktop browser built with Electron and web technologies.

## Features
- **Chromium Engine**: Full web compatibility and high rendering performance.
- **Multi-Tab Browsing**: Easily open, close, and switch between dynamic web tabs.
- **Navigation Controls**: Back, Forward, Reload, Home, and Omnibox/URL search.
- **Multi-Platform Support**: Built to target Windows (NSIS Installer/Portable), Linux (AppImage), and macOS (DMG), with Windows as the primary supported platform.
- **Interactive TUI Build Manager (`make.py`)**: Easily configure build version, toggle target OS editions, install dependencies, and trigger compilation.

## Getting Started

### Prerequisites
- [Node.js](https://nodejs.org/) (v18+) & `npm`
- [Python 3.x](https://www.python.org/) (for running `make.py` TUI)

### Quick Start using `make.py` (TUI)
Run the interactive console build assistant:
```bash
python make.py
```
From the interactive menu you can:
1. Toggle the build edition between **Windows**, **Linux**, and **macOS**.
2. Change the semantic build version (e.g. `1.0.0` -> `1.0.1`).
3. Install dependencies (`npm install`).
4. Launch GateBrowser in dev mode (`npm start`).
5. Package the standalone installer for the chosen OS edition.

### Alternative: Using the Makefile or npm directly
```bash
# Install dependencies
npm install

# Start developer mode
npm start

# Build for Windows installer
npm run pack:win

# Build for Linux
npm run pack:linux

# Build for macOS
npm run pack:mac
```
