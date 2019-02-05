from multiprocessing import Process
import unittest
import os
import pty
from ui.driver.driver_pi import Pi
import ui.driver.comms_codes as comms


class TestDriverPi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        master, slave = pty.openpty()
        s_name = os.ttyname(slave)
        cls._master = master
        cls._driver = Process(target=Pi, args=(s_name,))
        cls._driver.start()

    def get_message(self, msglen=1):
        message = os.read(self._master, msglen)
        return message

    def send_message(self, msg):
        os.write(self._master, msg)

    def test_rxtx_data(self):
        # receive the get chars message
        FRAME_BOUNDARY = 0x7E

        self.assertEqual(self.get_message(5), bytes([
          FRAME_BOUNDARY,
          comms.CMD_GET_CHARS,
          0x78, 0xF0,  # CRC LSB, MSB
          FRAME_BOUNDARY
        ]))

        # send chars (can pretend to be any size we like)
        # [data bytearray], cmd
        self.send_message(bytes([
          FRAME_BOUNDARY,
          comms.CMD_GET_CHARS,
          24, 0,       # num cols LSB, MSB
          0x9D, 0x9D,  # CRC LSB, MSB
          FRAME_BOUNDARY
        ]))

        # receive the get rows message
        self.assertEqual(self.get_message(5), bytes([
          FRAME_BOUNDARY,
          comms.CMD_GET_ROWS,
          0xF1, 0xE1,  # CRC LSB, MSB
          FRAME_BOUNDARY
        ]))

        # send rows
        self.send_message(bytes([
          FRAME_BOUNDARY,
          comms.CMD_GET_ROWS,
          4, 0,        # num rows LSB, MSB
          0x70, 0xFB,  # CRC LSB, MSB
          FRAME_BOUNDARY
        ]))

    @classmethod
    def tearDownClass(cls):
        cls._driver.join()
