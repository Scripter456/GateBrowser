# GateBrowser Makefile

.PHONY: all install start build build-win build-linux build-mac clean

all: start

install:
	cmd.exe /c "npm install"

start:
	cmd.exe /c "npm start"

build: build-win

build-win:
	cmd.exe /c "npm run pack:win"

build-linux:
	cmd.exe /c "npm run pack:linux"

build-mac:
	cmd.exe /c "npm run pack:mac"

clean:
	cmd.exe /c "if exist dist rmdir /s /q dist"
