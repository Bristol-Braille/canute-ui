# Install

## Linux for testing

Install python 2.x (will probably work with 3.x with little modification).

Install pip and other dependencies:
```
sudo apt install python-pip python-pyside python-dev
```

Install other requirements: 
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

## Mac (emulator only)
For the Mac, installation is slightly different depending on whether you use the version of python that comes with OS, or one installed with Macports or Homwbrew.

First, comment out (put a hash in front) of the `evdev` line in `requirements.txt`. (This package is only used on linux, and if you try to install it on a mac it will fail). 

For native installation:
```
sudo easy_install pip
pip install python-pyside
pip install --user -r requirements.txt
```

For MacPorts:
```
sudo port install py27-pip py27-pyside
pip install --user -r requirements.txt
```

For Homebrew:
```
brew install python brew-pip
brew pip install python-pyside
pip install --user -r requirements.txt
```

Then, to test and run it:

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

