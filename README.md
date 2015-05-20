# Canute UI

This is the repository for UI (user interface) development for the [Canute
electronic Braille reader](http://bristolbraille.co.uk/#canute).

## Documentation

Documentation is available at
[http://ui.readthedocs.org/en/latest/](http://ui.readthedocs.org/en/latest/)

## Getting started

Install python 2.x (will probably work with 3.x with little modification)

Install the [requirements](ui/requirements.txt). On Linux:

    pip install -r requirements

On Windows follow these
[instructions](http://pillow.readthedocs.org/en/latest/installation.html) to
install Pillow.

Run the UI (with emulated hardware delay of 1000ms):

    cd ui/
    python ./ui.py --emulated --delay 1000

## Specification

[Specfication document](spec.md)

## Design

The top level [ui](ui/ui.py) relies on either the real hardware or an
emulated version (using the --emulated argument).

The emulated hardware has the same interface as the real hardware, but also runs
a graphical program called [gui_display.py](ui/gui_display.py). This shows
how the machine will look, and provides the buttons.

The gui and the UI communicate via UDP as we found that running the gui within a
thread caused problems when using Python's debugging tools.
