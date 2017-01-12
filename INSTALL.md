# Install

## Linux/Mac for testing

Install python 2.x (will probably work with 3.x with little modification).

Install pip:
For Debian/Ubuntu (and various other Linux distros)

    sudo apt install python-pip    

For Mac, depending on whether you are using the native python, MacPorts or Homebrew
Mac native: `sudo easy_install pip`
Macports: `sudo port install py27-pip`
Homebrew: pip gets installed automatically when you install python.


If you wish to run the emulator, install PySide, and optionally the Python development tools:
```
pip install pyside
```

(For Linux you may prefer to use)
```
sudo apt install python-pyside python-dev
```

Install other requirements: 
(For the Mac, you will need to comment out the `evdev` line in `requirements.txt`)
```
pip install --user -r requirements.txt
```

Copy the test books to the home directory:

    cp -r books ~/

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
    python main.py --disable-emulator

