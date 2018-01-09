from multiprocessing import Process
import unittest
import os
import pty
import struct
from ui.driver.driver_pi import Pi
import ui.driver.comms_codes as comms


class TestDriverPi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        master, slave = pty.openpty()
        s_name = os.ttyname(slave)
        cls._master = master
        cls._driver = Process(target=Pi, args=(s_name, False))
        cls._driver.start()

    def get_message(self, len=1):
        message = os.read(self._master, 1)
        data = struct.unpack('1b', message)
        return data

    def send_message(self, data, cmd):
        message = struct.pack('%sb' % (len(data) + 1), cmd, *data)
        os.write(self._master, message)

    def test_rxtx_data(self):
        # receive the get chars message
        self.assertEqual(self.get_message()[0], comms.CMD_GET_CHARS)

        # send chars
        self.send_message([24], comms.CMD_GET_CHARS)

        # receive the get rows message
        self.assertEqual(self.get_message()[0], comms.CMD_GET_ROWS)

        # send rows
        self.send_message([4], comms.CMD_GET_ROWS)

    @classmethod
    def tearDownClass(cls):
        cls._driver.join()
