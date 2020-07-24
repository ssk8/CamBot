#!/usr/bin/python3

import digitalio
import board
from PIL import Image
import adafruit_rgb_display.st7789 as st7789
from io import BytesIO
from picamera import PiCamera

disp = st7789.ST7789(board.SPI(), rotation=90, width=240, height=240, x_offset=0, y_offset=80, cs=digitalio.DigitalInOut(board.CE0), dc=digitalio.DigitalInOut(board.D25), baudrate=24000000)

backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

buttonA = digitalio.DigitalInOut(board.D23)
buttonB = digitalio.DigitalInOut(board.D24)
buttonA.switch_to_input()
buttonB.switch_to_input()

try:

    while True:
        if not buttonA.value:
            print('well, helllo')
            camera = PiCamera()
            camera.resolution = (240, 240)
            stream = BytesIO()
            camera.capture(stream, format='jpeg')
            stream.seek(0)
            disp.image(Image.open(stream))
            camera.close()
except KeyboardInterrupt:
    camera.close()
    backlight.value = False
