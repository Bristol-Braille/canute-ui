# Install

## Linux

Install python, pip and other dependencies:

    sudo apt install python3-pip python3-dev

Install other requirements:

    pip3 install --user -r requirements.txt

If you want to test and develop the direct button interface (`--pi-buttons`) then you will need extra packages

    pip3 install --user -r requirements-pi.txt

## Mac
For the Mac, installation is slightly different depending on whether you want to use Macports or Homwbrew.

Evdev is for Linux only so the `--pi-buttons` option will not be usable on Mac.

For MacPorts:

    sudo port install py36-pip
    pip-3.6 install --user -r requirements.txt

For Homebrew:

    brew install python3
    pip3 install -r requirements.txt


## Deploying to Raspberry Pi

Install requirements:

    sudo apt install -y usbmount python3-pip python3-dev
    sudo pip3 install -r requirements-pi.txt

Install the rc.local and fstab files

    sudo cp rc.local fstab /etc/

Copy the test books to the home directory:

    cp -r books ~/

Copy the config file:

    cp config.rc.in config.rc

Run the UI software without the emulator and read the buttons through evdev:

    ./canute_ui --real --pi-buttons
