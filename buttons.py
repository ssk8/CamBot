import RPi.GPIO as GPIO
from time import sleep


class Buttons(object):
    """handle buttons A and B. When read on A or B return if a button has been pressed since last polled"""

    def __init__(self, A_pin=24, B_pin=23):
        self._A_pin = A_pin
        self._B_pin = B_pin
        self._A_state = False
        self._B_state = False
        self.begin()

    def button_A_event(self, channel):
        self._A_state = True
    
    @property
    def A(self):
        if self._A_state and not self._B_state:
            self._A_state = False
            return True
        else:
            return False

    def button_B_event(self, channel):
        self._B_state = True

    @property
    def B(self):
        if self._B_state and not self._A_state:
            self._B_state = False
            return True
        else:
            return False


    @property
    def either(self):
        if self._A_state or self._B_state:
            return True
        else:
            return False

    @property
    def both(self):
        if self._A_state and self._B_state:
            self._A_state = False
            self._B_state = False
            return True
        else:
            return False


    def begin(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._A_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self._A_pin, GPIO.FALLING, callback=self.button_A_event, bouncetime=200)
        GPIO.setup(self._B_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self._B_pin, GPIO.FALLING, callback=self.button_B_event, bouncetime=200)

def main():
    button = Buttons()
    while True:
        sleep(1)
        print(f"button A: {button.A}  button B: {button.B}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\ndone")
    finally:
        GPIO.cleanup() 