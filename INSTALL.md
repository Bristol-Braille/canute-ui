# Install

## Linux for testing

Install python 2.x (will probably work with 3.x with little modification)

Install requirements:

    sudo apt install python-pyside python-pip python-dev
    pip install --user -r requirements.txt

Configure the library_dir in [ui/config.rc](ui/config.rc) to point at the [books](books) directory which is full of test books.

Run the tests:

    cd ui/
    python test.py --verbose

Run the UI using the emulator:

    cd ui/
    python main.py

## Raspberry Pi

Install requirements:

    sudo apt install usbmount python-pip python-dev
    sudo pip install -r requirements.txt

Copy the test books to the home directory:

    cp -r books ~/

Run the UI software without the emulator:

    cd ui/
    python main.py --disbale-emulator

