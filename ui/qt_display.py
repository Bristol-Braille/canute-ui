#!/usr/bin/env python
from __future__ import print_function
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


def get_all(t, cls):
    return [y for x,y in cls.__dict__.items() if type(y) == t]

class Display(QtGui.QMainWindow, Ui_MainWindow):
    '''shows an emulation of the braille machine'''
    def __init__(self, display_text=False):
        '''create the display object'''
        super(Display, self).__init__()
        self.setupUi(self)

        button_widgets = get_all(QtGui.QPushButton, self)

        self.buttons = [None] * len(button_widgets)
        for button in button_widgets:
            num = int(button.text())
            button.clicked.connect(self.make_slot(num))
            self.buttons[num] = button

        self.udp_send = udp_send(port=5001)
        self.udp_recv = udp_recv(port=5000)

        self.show()

    def make_slot(self, button_num):
        def slot():
            self.send_button_msg(button_num, 'single')
        return slot

    def send_button_msg(self, button_num, button_type):
        '''send the button number to the parent via the queue'''
        log.info("sending %s button = %d" % (button_type, button_num))
        self.udp_send.put({'num': button_num, 'type': button_type})



def main():
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger(__name__)
    log.info("display GUI")
    app = QtGui.QApplication(sys.argv)
    display = Display()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
