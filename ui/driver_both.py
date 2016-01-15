from driver import Driver
from driver_emulated import Emulated
from driver_pi import Pi

class DriverBoth():
    def __init__ (self, port='/dev/ttyACM0', pi_buttons=False, delay=0, display_text=False):
        self.emulatated = Emulated(delay, display_text)
        self.pi = Pi(port, pi_buttons)

for method_name in Driver.__abstractmethods__:
    def method(self, *args, **kwargs):
        pi_method = self.pi.__getattribute__(method_name)
        emulated_method = self.emulated.__getattribute__(method_name)
        pi_method(*args, **kwargs)
        return emulated_method(*args, **kwargs)
    setattr(DriverBoth, method_name, method)
