# Install

## Raspberry Pi

Install usbmount for automatic usb stick loading

    sudo apt-get install usbmount

Install python [pi-requirements](pi-requirements)

    sudo pip install -r pi-requirements

## Linux for testing

Install python 2.x (will probably work with 3.x with little modification)

Install the python [dev-requirements](ui/dev-requirements)

    sudo pip install -r dev-requirements

Set the absolute location of your books directory (eg:
/home/me/canute-ui/books) in the ui/config.rc	

Run the tests:

    cd ui/
    python ./test.py --verbose

Run the UI using the emulator:

    cd ui/
    python ./start_ui.py
