'''
This module defines the DriverBoth class that combines the emulated and real
driver (Pi) allowing you to run them at the same time. Methods are sent to both
drivers values from the emulated one are returned. This means, for instance,
that only the button presses from the emulated GUI are registered.
'''
import logging
from .driver import Driver
from .driver_emulated import Emulated
from .driver_pi import Pi
from .. import utility


log = logging.getLogger(__name__)


class DriverBoth():
    def __init__(self, port='/dev/ttyACM0',
                 delay=0, display_text=False, timeout=60):
        log.debug('__init__')
        self.emulated = Emulated(delay, display_text)
        self.pi = Pi(port, timeout=timeout)
        self.chars = 40
        self.rows = 9

    def __exit__(self, ex_type, ex_value, traceback):
        pass

    def __enter__(self):
        '''method required for using the `with` statement'''
        return self


defined_methods = utility.get_methods(DriverBoth)
for method_name in utility.get_methods(Driver):
    if method_name not in defined_methods:
        def make_method(method_name):
            def method(self, *args, **kwargs):
                emulated_method = self.emulated.__getattribute__(method_name)
                pi_method = self.pi.__getattribute__(method_name)
                pi_method(*args, **kwargs)
                return emulated_method(*args, **kwargs)
            return method
        setattr(DriverBoth, method_name, make_method(method_name))
