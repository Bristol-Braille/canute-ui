# Canute UI [![Travis CI Status](https://travis-ci.org/Bristol-Braille/canute-ui.svg?branch=master)](https://travis-ci.org/Bristol-Braille/canute-ui)

This is the repository for UI (user interface) development for the [Canute
electronic Braille reader](http://bristolbraille.co.uk/#canute).

## Documentation

Documentation is available at
[http://ui.readthedocs.org/en/latest/](http://ui.readthedocs.org/en/latest/)

## Getting started

Read [INSTALL.md](INSTALL.md) for installation instructions.

## Design

The top level [ui](ui/main.py) uses a graphical display to emulate the hardware
by default.

The emulated hardware has the same interface as the real hardware, but also
runs a graphical program called [qt_display.py](ui/qt_display.py). This
shows how the machine will look, and provides the buttons.

The gui and the UI communicate via UDP as we found that running the gui within
a thread caused problems when using Python's debugging tools.
