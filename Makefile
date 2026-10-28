# GateBrowser Makefile
# Supports GNU Make on Windows, Linux, and macOS

VERSION ?= $(shell python -c "import json; print(json.load(open('package.json'))['version'])" 2>nul || python3 -c "import json; print(json.load(open('package.json'))['version'])" 2>/dev/null || echo 0.0.1)

.PHONY: all help install start build exe build-win build-win-installer build-linux build-mac clean

all: help

help:
	@echo ===================================================
	@echo GateBrowser Makefile (v$(VERSION))
	@echo ===================================================
	@echo Available targets:
	@echo   make install              - Install npm dependencies
	@echo   make start                - Launch browser in dev mode
	@echo   make exe                  - Compile normal standalone .exe (GateBrowser.exe)
	@echo   make build-win            - Compile Windows portable .exe + installer
	@echo   make build-win-installer  - Compile Windows NSIS setup .exe
	@echo   make build-linux          - Compile Linux AppImage
	@echo   make build-mac            - Compile macOS dmg
	@echo   make clean                - Clean dist output directory
	@echo ===================================================

install:
	cmd.exe /c "npm install"

start:
	cmd.exe /c "npm start"

# Compiles standalone normal .exe
exe:
	cmd.exe /c "npm run pack:win-portable"

build: exe

build-win:
	cmd.exe /c "npm run pack:win"

build-win-installer:
	cmd.exe /c "npx electron-builder --win nsis --x64"

build-linux:
	cmd.exe /c "npm run pack:linux"

build-mac:
	cmd.exe /c "npm run pack:mac"

clean:
	cmd.exe /c "if exist dist rmdir /s /q dist"
