#!/usr/bin/env python
import logging
import argparse
from .driver import Driver
from .utility import test_pattern

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="shows a repeating pattern of all possible dot patterns"
    )

    parser.add_argument(
        '--tty', action='store', dest='tty',
        help="serial port for Canute stepstix board", default='/dev/ttyACM0'
    )
    parser.add_argument(
        '--emulated', action='store_const', dest='emulated',
        const=True, default=False, help="emulate the hardware (use GUI)"
    )

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger(__name__)

    if args.emulated:
        log.info("running with emulated hardware")
        from hardware_emulator import HardwareEmulator
        with HardwareEmulator() as hardware:
            driver = Driver(hardware)
            pattern = test_pattern(driver.get_dimensions())
            driver.set_braille(pattern)
    else:
        log.info("running with stepstix hardware on port %s" % args.tty)
        from hardware import Hardware
        with Hardware(port=args.tty, pi_buttons=False) as hardware:
            driver = Driver(hardware)
            pattern = test_pattern(driver.get_dimensions())
            driver.set_braille(pattern)
