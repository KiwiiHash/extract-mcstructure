# extract-mcstructure

Extract's mcstructures from the Bedrock leveldb (possibly saved from the `/structure` command) to `.mcstructure` files which can be moved across worlds.

## Usage

`python3 run.py World all` - Extracts all mcstructures from the world named "World" (as seen on the in-game menu)

`python3 run.py World house -o example/ouput` - Extracts the structure named "house" from the world named "World" into a folder named "output" in specified directory

All extracted files will be outputted to specified location using `-o`

## GUI Mode (Unstable)

`python3 beta.py` to open GUI

*Meant to be used for Linux* 

## Why use this?
Export feature from MC Bedrock is only supported in some devices. Some use cases for this is getting `.mcstrucutre` from a specific world but export button is not available in your device. 

### Note
`leveldb` lib is from `Amulet-Team/Amulet-Core`.

`tkinter` lib from Python (beta.py)

`Termux` app from [Termux App](https://github.com/termux/termux-app)

