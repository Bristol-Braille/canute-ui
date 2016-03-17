#!/usr/bin/env python
from __future__ import print_function
import time
import argparse
import logging
from udp_utility import udp_send, udp_recv
from comms_codes import *
from utility import pin_num_to_unicode, pin_num_to_alpha

from threading import Timer

import sys
from PySide import QtGui
from qt.main_window import Ui_MainWindow

log = logging.getLogger(__name__)

# hardware defs
BUTTONS = 8
CHARS = 32
ROWS = 8

MSG_INTERVAL_S = 0.01

def main():
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger(__name__)
    log.info("display GUI")

    parser = argparse.ArgumentParser(description="Canute Emulator")
    parser.add_argument('--text', action='store_const', dest='text',
            const=True, help="show text instead of braille")
    args = parser.parse_args()

    app = QtGui.QApplication(sys.argv)
    display = Display(display_text=args.text)
    sys.exit(app.exec_())

class HardwareError(Exception):
    pass


def get_all(t, cls):
    return [y for x,y in cls.__dict__.items() if type(y) == t]

class Display(QtGui.QMainWindow, Ui_MainWindow):
    '''shows an emulation of the braille machine'''
    def __init__(self, display_text=False):
        '''create the display object'''
        self.display_text = display_text

        super(Display, self).__init__()
        self.setupUi(self)

        button_widgets = get_all(QtGui.QPushButton, self)

        self.buttons = {}
        for button in button_widgets:
            button_id = button.text()
            button.clicked.connect(self.make_slot(button_id))
            self.buttons[button_id] = button

        self.label_rows = []
        for n in range(ROWS):
            self.label_rows.append(self.__getattribute__('row_label_%i' % n))

        self.udp_send = udp_send(port=5001)
        self.udp_recv = udp_recv(port=5000)

        self.timer = Timer(MSG_INTERVAL_S, self.check_msg)
        self.timer.start()

        self.show()

    def make_slot(self, button_id):
        def slot():
            self.send_button_msg(button_id, 'single')
        return slot

    def send_button_msg(self, button_id, button_type):
        '''send the button number to the parent via the queue'''
        log.info("sending %s button = %s" % (button_type, button_id))
        self.udp_send.put({'id': button_id, 'type': button_type})

    def print_braille(self, data):
        '''print braille to the display

        :param data: a list of characters to display.  Assumed to be the right
        length and filled with numbers from 1 to 64
        '''
        log.debug("printing data: %s" % data)

        for row in range(ROWS):
            row_braille = data[row*CHARS:row*CHARS+CHARS]
            self.print_braille_row(row, row_braille)

    def print_braille_row(self, row, row_braille):
        # useful for debugging, show pin number not the braille
        if self.display_text:
            label_text = ''.join(map(pin_num_to_alpha, row_braille))
        else:
            label_text = ''.join(map(pin_num_to_unicode, row_braille))
        self.label_rows[row].setText(label_text)

    def check_msg(self):
        '''check for a message in the queue, if so display it as braille using
        :func:`print_braille`
        '''
        try:
            msg = self.udp_recv.get()
            if msg is not None:
                msgType = msg[0]
                msg = msg[1:]
                if msgType == CMD_SEND_PAGE:
                    self.print_braille(msg)
                elif msgType == CMD_SEND_LINE:
                    self.print_braille_row(msg[0], msg[1:])
        except:
            print('check_msg ERROR')


        self.timer = Timer(MSG_INTERVAL_S, self.check_msg)
        self.timer.start()





if __name__ == '__main__':
    main()
