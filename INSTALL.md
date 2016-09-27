# Install

## Raspberry Pi

Install requirements:

    sudo apt-get install usbmount python-pip
    pip install -r requirements.txt

## Linux for testing

Install python 2.x (will probably work with 3.x with little modification)

Install requirements:

    sudo apt-get install python-pyside python-pip
    pip install -r requirements.txt

Run the tests:

    cd ui/
    python test.py --verbose

Run the UI using the emulator:

    cd ui/
    python ui.py
