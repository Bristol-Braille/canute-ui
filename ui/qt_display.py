#!/usr/bin/env python

import argparse
import logging
from . import comms_codes as comms
from multiprocessing import Queue
from queue import Empty
import sys
from PySide import QtGui, QtCore
from .qt.main_window import Ui_MainWindow
from ui.utility import pin_num_to_unicode, pin_num_to_alpha

log = logging.getLogger(__name__)

# hardware defs
BUTTONS = 9
CHARS = 40
ROWS = 9

MSG_INTERVAL_MS = 10


def main():
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description='Canute Emulator')
    parser.add_argument('--text', action='store_const', dest='text',
                        const=True, help='show text instead of braille')
    args = parser.parse_args()

    app = QtGui.QApplication(sys.argv)
    Display(to_display_queue=Queue(), from_display_queue=Queue(),
            display_text=args.text)
    sys.exit(app.exec_())


class HardwareError(Exception):
    pass


def start(to_display_queue, from_display_queue, display_text):

    app = QtGui.QApplication(sys.argv)
    Display(to_display_queue=to_display_queue,
            from_display_queue=from_display_queue, display_text=display_text)
    sys.exit(app.exec_())


def get_all(t, cls):
    return [y for x, y in list(cls.__dict__.items()) if type(y) == t]


class Display(QtGui.QMainWindow, Ui_MainWindow):
    '''shows an emulation of the braille machine'''

    def __init__(self, to_display_queue,
                 from_display_queue, display_text=False):
        '''create the display object'''
        self.display_text = display_text

        super(Display, self).__init__()
        self.setupUi(self)

        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        button_widgets = get_all(QtGui.QPushButton, self)

        self.buttons = {}
        for button in button_widgets:
            button.setFocusPolicy(QtCore.Qt.NoFocus)
            button_id = button.text()
            button.pressed.connect(self.make_slot(button_id, 'down'))
            button.released.connect(self.make_slot(button_id, 'up'))
            self.buttons[button_id] = button

        self.label_rows = []
        for n in range(ROWS):
            self.label_rows.append(self.__getattribute__('row_label_%i' % n))

        self.send_queue = from_display_queue
        self.receive_queue = to_display_queue
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.check_msg)
        timer.start(MSG_INTERVAL_MS)

        self.show()

    def make_slot(self, button_id, direction):
        def slot():
            self.send_button_msg(button_id, direction)
        return slot

    def sendKeys(self, e, direction):
        if e.key() == QtCore.Qt.Key_Left:
            self.send_button_msg('<', direction)
        elif e.key() == QtCore.Qt.Key_Right:
            self.send_button_msg('>', direction)
        elif e.key() == QtCore.Qt.Key_Down:
            self.send_button_msg('L', direction)
        elif e.key() == QtCore.Qt.Key_R:
            self.send_button_msg('R', direction)
        elif (e.key() >= 49 and e.key() <= 56):
            self.send_button_msg('%i' % (e.key() - 48,), direction)


    def keyPressEvent(self, e):
        self.sendKeys(e, 'down')

    def keyReleaseEvent(self, e):
        self.sendKeys(e, 'up')


    def send_button_msg(self, button_id, button_type):
        '''send the button number to the parent via the queue'''
        log.debug('sending %s button = %s' % (button_type, button_id))
        self.send_queue.put_nowait({'id': button_id, 'type': button_type})

    def print_braille(self, data):
        '''print braille to the display

        :param data: a list of characters to display.  Assumed to be the right
        length and filled with numbers from 1 to 64
        '''
        log.debug('printing data: %s' % data)

        for row in range(ROWS):
            row_braille = data[row * CHARS:row * CHARS + CHARS]
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
            msg = self.receive_queue.get_nowait()
            if msg is not None:
                msgType = msg[0]
                msg = msg[1:]
                if msgType == comms.CMD_SEND_PAGE:
                    self.print_braille(msg)
                elif msgType == comms.CMD_SEND_LINE:
                    self.print_braille_row(msg[0], msg[1:])
        except Empty:
            pass
        except:
            log.error('check_msg ERROR')


if __name__ == '__main__':
    main()
