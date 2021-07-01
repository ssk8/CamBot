import RPi.GPIO as GPIO
from time import sleep


class Buttons(object):
    """handle buttons"""

    def __init__(self, A_pin=23, B_pin=24):
        self._A_pin = A_pin
        self._B_pin = B_pin
        self.button_A = False
        self.button_B = False
        self.begin()

    def button_A_event(self, channel):
        self.button_A = True

    def button_B_event(self, channel):
        self.button_B = True

    def begin(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._A_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self._A_pin, GPIO.FALLING, callback=self.button_A_event, bouncetime=200)
        GPIO.setup(self._B_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self._B_pin, GPIO.FALLING, callback=self.button_B_event, bouncetime=200)

def main():
    buttons = Buttons()
    while True:
        sleep(1)
        print(f"button A: {buttons.button_A}  button B: {buttons.button_B}")
        if buttons.button_A:
            buttons.button_A = False


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\ndone")
    finally:
        GPIO.cleanup() 