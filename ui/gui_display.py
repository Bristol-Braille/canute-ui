#!/usr/bin/env python
import time
import argparse
import logging
import Tkinter
from Tkinter import StringVar
from udp_utility import udp_send, udp_recv
from comms_codes import *
from utility import pin_num_to_unicode, pin_num_to_alpha

log = logging.getLogger(__name__)

# hardware defs
BUTTONS = 8
CHARS = 32
ROWS = 4


class HardwareError(Exception):
    pass


class Display():
    """shows an emulation of the braille machine"""

    MSG_INTERVAL = 10

    button_after_id = None

    def __init__(self, display_text=False):
        '''create the display object'''
        self.counter = 0
        self.display_text = display_text
        self.tk = Tkinter.Tk()

        self.udp_send = udp_send(port=5001)
        self.udp_recv = udp_recv(port=5000)

        #  setup all the buttons
        col = 0
        for button_num in range(BUTTONS):
            button = Tkinter.Button(self.tk, text="%d" % button_num)
            button.bind('<Button-1>',
                    lambda bn=button_num: self.register_button(bn))
            button.bind('<Double-Button-1>', self.register_dub_button)
            button.bind('<ButtonRelease-1>', self.register_rel_button)
            row = button_num % (BUTTONS / 2)
            if button_num == BUTTONS / 2:
                col = 2
            button.grid(row=row, column=col)

        #  use a label for the braille display
        self.label_rows = []
        for row in range(ROWS):
            str_var = StringVar()
            self.label_rows.append(str_var)
            label = Tkinter.Label(textvariable=str_var,
                    font=("Helvetica", 20))
            label.grid(row=row, column=1,)


        #  check for messages from parent
        self.tk.after(Display.MSG_INTERVAL, self.check_msg)

        log.info("GUI starting")
        self.tk.mainloop()
        log.info("GUI finished")

    def register_button(self, event):
        # seems hacky
        self.button_num = int(event.widget['text'])
        self.button_time = time.time()
        self.button_type = 'single'

    def register_dub_button(self, event):
        self.button_type = 'double'
        self.send_button_msg()

    def register_rel_button(self, event):
        # long
        if time.time() - self.button_time > .9:
            self.button_type = 'long'
            self.send_button_msg()
        # 2nd of double?
        elif self.button_type == 'double':
            self.tk.after_cancel(self.button_after_id)
        # could be 1st of double or single?
        else:
            self.button_after_id = self.tk.after(1000, self.send_button_msg)

    def send_button_msg(self):
        '''send the button number to the parent via the queue'''
        log.debug("sending %s button = %d" % (self.button_type,
            self.button_num))
        self.udp_send.put({'num': self.button_num, 'type': self.button_type})

    def print_braille_row(self, row, row_braille):
        # useful for debugging, show pin number not the braille
        if self.display_text:
            label_text = ''.join(map(pin_num_to_alpha, row_braille))
        else:
            label_text = ''.join(map(pin_num_to_unicode, row_braille))
        self.label_rows[row].set(label_text)


    def print_braille(self, data):
        '''print braille to the display

        :param data: a list of characters to display.  Assumed to be the right
        length and filled with numbers from 1 to 64
        '''
        log.debug("printing data: %s" % data)

        for row in range(ROWS):
            row_braille = data[row*CHARS:row*CHARS+CHARS]
            self.print_braille_row(row, row_braille)

    def check_msg(self):
        '''check for a message in the queue, if so display it as braille using
        :func:`print_braille`
        '''
        msg = self.udp_recv.get()
        if msg is not None:
            msgType = msg[0]
            msg = msg[1:]
            if msgType == CMD_SEND_PAGE:
                self.print_braille(msg)
            elif msgType == CMD_SEND_LINE:
                self.print_braille_row(msg[0], msg[1:])
        # reschedule the message check
        self.tk.after(Display.MSG_INTERVAL, self.check_msg)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger(__name__)
    log.info("display GUI")

    parser = argparse.ArgumentParser(description="Canute Emulator")
    parser.add_argument('--text', action='store_const', dest='text',
            const=True, help="show text instead of braille")
    args = parser.parse_args()

    display = Display(display_text=args.text)
