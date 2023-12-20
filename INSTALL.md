# Install

## Linux

Install python, pip and other dependencies:

    sudo apt install python3-pip python3-dev

Install other requirements:

    pip3 install --user -r requirements.txt

If you want to test and develop the direct button interface (`--pi-buttons`) then you will need extra packages

    pip3 install --user -r requirements-pi.txt

## Mac
For the Mac, installation is slightly different depending on whether you want to use Macports or Homebrew.

Evdev is for Linux only so the `--pi-buttons` option will not be usable on Mac.

For MacPorts:

    sudo port install py36-pip
    pip-3.6 install --user -r requirements.txt

For Homebrew:

    brew install python@3.12
    brew install qt5
    export PATH="$(brew --prefix qt5)/bin:$PATH"
    brew install pyqt@5
    export PYTHONPATH="$(brew --prefix pyqt@5)/lib/python3.12/site-packages:$PYTHONPATH"
    python3.12 -m venv ve
    . ve/bin/activate
    pip install -r requirements.txt

    brew install liblouis
    cd ui/locale
    pip install -r requirements-translate.txt
    export PYTHONPATH="$(brew --prefix liblouis)/lib/python3.12/site-packages:$PYTHONPATH"

## Deploying to Raspberry Pi

Install requirements:

    sudo apt install -y usbmount python3-pip python3-dev
    sudo pip3 install -r requirements-pi.txt

Install the rc.local file to make canute_ui start on boot

    sudo cp rc.local /etc/

Add a mountpoint for the external sd-card and an fstab entry to automount it


    sudo bash -c 'cat fstab >> /etc/fstab'
    sudo chown pi:pi /media
    mkdir /media/sd-card
    sudo cp fstab /etc/

Copy the config file:

    cp config.rc.in config.rc

Run the UI software:

    ./run.sh
