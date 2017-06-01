# Install

## Linux

Install python 2.x (will probably work with 3.x with little modification).

Install pip and other dependencies:

    sudo apt install python-pip python-pyside python-dev

Install other requirements: 

    pip install --user -r requirements.txt 

If you want to test and develop the direct button interface (`--pi-buttons`) then you will need extra packages

    pip install --user -r requirements-pi.txt

## Mac
For the Mac, installation is slightly different depending on whether you use the version of python that comes with OS, or one installed with Macports or Homwbrew.

Evdev is for Linux only so the `--pi-buttons` option will not be usable on Mac.

For native installation:

    sudo easy_install pip
    pip install python-pyside
    pip install --user -r requirements.txt

For MacPorts:

    sudo port install py27-pip py27-pyside
    pip install --user -r requirements.txt

For Homebrew:

    brew install python brew-pip
    brew pip install python-pyside
    pip install --user -r requirements.txt


## Deploying to Raspberry Pi

Install requirements:

    sudo apt install usbmount python-pip python-dev
    sudo pip install -r requirements-pi.txt

Copy the test books to the home directory:

    cp -r books ~/

Copy the config file:

    cp config.rc config.rc.in 

Run the UI software without the emulator and read the buttons through evdev:

    python main.py --disable-emulator --pi-buttons
