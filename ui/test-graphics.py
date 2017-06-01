from driver_pi import Pi

import argparser
import signal
import config_loader
from setup_logs import setup_logs
import time

test_file='smiley.png'

args = argparser.parser.parse_args()

config = config_loader.load()
log = setup_logs(config, args.loglevel)

if args.emulated and not args.both:
    log.info("running with emulated hardware")
    from driver_emulated import Emulated

    with Emulated(delay=args.delay, display_text=args.text) as driver:
        time.sleep(1) # Emulated Driver start-up can take a while; without this, the image sent may not be received.
        driver.load_graphic(test_file)
        signal.pause()

elif args.emulated and args.both:
    log.info("running with both emulated and real hardware on port %s" % args.tty)
    from driver_both import DriverBoth

    with DriverBoth(port=args.tty, pi_buttons=args.pi_buttons,
                    delay=args.delay, display_text=args.text) as driver:
        time.sleep(1) # Emulated Driver start-up can take a while; without this, the image sent may not be received.
        driver.load_graphic(test_file)
        signal.pause()
else:
    timeout = config.get('comms', 'timeout')
    log.info("running with real hardware on port %s, timeout %s" % (args.tty, timeout))
    with Pi(port=args.tty, pi_buttons=args.pi_buttons, timeout=timeout) as driver:
        driver.load_graphic(test_file)
        signal.pause()
