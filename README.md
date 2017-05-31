# Canute UI [![Travis CI Status](https://travis-ci.org/Bristol-Braille/canute-ui.svg?branch=master)](https://travis-ci.org/Bristol-Braille/canute-ui)

This is the repository for UI (user interface) development for the [Canute
electronic Braille reader](http://bristolbraille.co.uk/#canute).

## Usage

[`main.py`](main.py) runs a graphical display to emulate the hardware by
default. The emulated hardware has the same interface as the real hardware, but
also runs a graphical program called [qt_display.py](qt_display.py). This shows
how the machine will look, and provides the buttons.

```
usage: main.py [-h] [--pi-buttons] [--debug] [--text] [--tty TTY]
               [--delay DELAY] [--disable-emulator] [--both]

Canute UI

optional arguments:
  -h, --help          show this help message and exit
  --pi-buttons        use the Pi to handle button presses
  --debug             debugging content
  --text              show text instead of braille
  --tty TTY           serial port for Canute stepstix board
  --delay DELAY       simulate mechanical delay in milliseconds in the
                      emulator
  --disable-emulator  do not run the graphical emulator, run with real
                      hardware
  --both              run both the emulator and the real hardware at the same
                      time

```

## Getting started

Read [INSTALL.md](INSTALL.md) for installation instructions.

## API

Automatically generated documentation is available at
[http://ui.readthedocs.org/en/latest/](http://ui.readthedocs.org/en/latest/)
