# Canute UI [![Travis CI Status](https://travis-ci.org/Bristol-Braille/canute-ui.svg?branch=master)](https://travis-ci.org/Bristol-Braille/canute-ui)

This is the repository for UI (user interface) development for the [Canute
electronic Braille reader](http://bristolbraille.co.uk/#canute).

## Usage

[`./canute_ui`](canute_ui) runs a graphical display to emulate the hardware by
default. The emulated hardware has the same interface as the real hardware, but
also runs a graphical program called [qt_display.py](ui/driver/qt_display.py). This shows
how the machine will look, and provides the buttons.

```
usage: canute_ui [-h] [--pi-buttons] [--debug] [--text] [--tty TTY]
                 [--delay DELAY] [--real] [--both] [--fuzz FUZZ_DURATION]
                 [--dummy]

Canute UI

optional arguments:
  -h, --help            show this help message and exit
  --debug               debugging content
  --text                show text instead of braille
  --tty TTY             serial port for the display and button board
  --delay DELAY         simulate mechanical delay in milliseconds in the
                        emulator
  --real                do not run the graphical emulator, run with real
                        hardware
  --both                run both the emulator and the real hardware at the
                        same time
  --fuzz FUZZ_DURATION  run with dummy display (emulated but without any
                        graphics) and press random buttons for duration (in
                        seconds), for debugging
  --dummy               run with the dummy display but without fuzz testing
                        button presses, for debugging
```

## Getting started

Read [INSTALL.md](INSTALL.md) for installation instructions.


## Development

Run the tests:

    ./test

Run the linter:

    ./lint

Copy and amend the config file

    cp config.rc.in config.rc
    $EDITOR config.rc

Copy the test books to the home directory (or wherever you specified in config.rc):

    cp -r books ~/

Run the UI using the emulator:

    ./canute_ui
