#!/usr/bin/env python
import time
import argparse
import logging
from udp_utility import udp_send, udp_recv
from comms_codes import *
from utility import pin_num_to_unicode, pin_num_to_alpha

import sys
from PySide import QtGui
from qt.main_window import Ui_MainWindow


log = logging.getLogger(__name__)

# hardware defs
BUTTONS = 8
CHARS = 28
ROWS = 4


class HardwareError(Exception):
    pass


class Display(QtGui.QMainWindow, Ui_MainWindow):
    '''shows an emulation of the braille machine'''

    MSG_INTERVAL = 10

    button_after_id = None

    def __init__(self, display_text=False):
        '''create the display object'''
        super(Display, self).__init__()
        self.setupUi(self)
        self.show()


def main():
    app = QtGui.QApplication(sys.argv)
    ex = Display()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
