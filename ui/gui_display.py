#!/usr/bin/env python
import time
import logging
import Tkinter
from Tkinter import StringVar
from udp_utility import udp_send, udp_recv
from comms_codes import *
from utility import pin_num_to_unicode

log = logging.getLogger(__name__)

# hardware defs
BUTTONS = 8
CHARS = 28
ROWS = 4


class HardwareError(Exception):
    pass


class Display():
    """shows an emulation of the braille machine"""

    MSG_INTERVAL = 10
    DISPLAY_GIF = 'display.gif'

    def __init__(self):
        '''create the display object'''
        self.counter = 0
        self.tk = Tkinter.Tk()

        self.udp_send = udp_send(port=5001)
        self.udp_recv = udp_recv(port=5000)

        #  setup all the buttons
        col = 0
        for but_num in range(BUTTONS):
            but = Tkinter.Button(self.tk, text="%d" % but_num)
            but.bind('<Button-1>', lambda but_num=but_num: self.register_but(but_num))
            but.bind('<Double-Button-1>', self.register_dub_but)
            but.bind('<ButtonRelease-1>', self.register_rel_but)
            row = but_num % (BUTTONS / 2)
            if but_num == BUTTONS / 2:
                col = 2
            but.grid(row=row, column=col)

        #  use a label for the braille display
        self.label_rows = []
        for row in range(ROWS):
            str_var = StringVar()
            self.label_rows.append(str_var)
            label = Tkinter.Label(textvariable=str_var, font=("Helvetica", 20) )
            label.grid(row=row, column=1,)


        #  check for messages from parent
        self.tk.after(Display.MSG_INTERVAL, self.check_msg)

        log.info("GUI starting")
        self.tk.mainloop()
        log.info("GUI finished")

    def register_but(self, event):
        # seems hacky
        self.but_num = int(event.widget['text'])
        self.but_time = time.time()
        self.but_type = 'single'

    def register_dub_but(self, event):
        self.but_type = 'double'
        self.send_but_msg()

    def register_rel_but(self, event):
        # long
        if time.time() - self.but_time > .9:
            self.but_type = 'long'
            self.send_but_msg()
        # 2nd of double?
        elif self.but_type == 'double':
            self.tk.after_cancel(self.but_after_id)
        # could be 1st of double or single?
        else:
            self.but_after_id = self.tk.after(1000, self.send_but_msg)

    def send_but_msg(self):
        '''send the button number to the parent via the queue'''
        log.debug("sending %s but = %d" % (self.but_type, self.but_num))
        self.udp_send.put({'num': self.but_num, 'type': self.but_type})

    def print_braille(self, data):
        '''print braille to the display

        :param data: a list of characters to display.  Assumed to be the right length and filled with numbers from 1 to 64
        '''
        log.debug("printing data: %s" % data)

        char_num = 0
        data_str = ''
        for row in range(ROWS):
            row_braille = data[row*CHARS:row*CHARS+CHARS]
            label_text = ''.join(map(pin_num_to_unicode, row_braille))
            self.label_rows[row].set(label_text)

    def check_msg(self):
        '''check for a message in the queue, if so display it as braille using :func:`print_braille`
        '''
        msg = self.udp_recv.get()
        if msg is not None:
            self.print_braille(msg)
        # reschedule the message check
        self.tk.after(Display.MSG_INTERVAL, self.check_msg)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger(__name__)
    log.info("display GUI")
    display = Display()

