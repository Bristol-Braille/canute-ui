"""
simple thread for flashing an led on a specified pin at a defined rate
"""
import threading
import time
import RPi.GPIO as GPIO
import signal
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

class LedThread(threading.Thread):
    def __init__(self,pin,sleep):
        super(LedThread,self).__init__()
        #need to be a daemon so we quit when the parent unexpectedly quits
        self.daemon = True
        self.sleep = sleep
        self.pin = pin
        self.loop = True
        GPIO.setup(pin,GPIO.OUT)

    def stop(self):
        self.loop = False

    def run(self):
        while self.loop:
            GPIO.output(self.pin,True)
            time.sleep(self.sleep)
            GPIO.output(self.pin,False)
            time.sleep(self.sleep)
