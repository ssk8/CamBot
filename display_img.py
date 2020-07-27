#!/usr/bin/python3

import digitalio
import board
from PIL import Image
import adafruit_rgb_display.st7789 as st7789
from io import BytesIO
from picamera import PiCamera
from datetime import datetime
from os import mkdir

miniTFT = st7789.ST7789(board.SPI(), rotation=90, width=240, height=240, x_offset=0, y_offset=80, cs=digitalio.DigitalInOut(board.CE0), dc=digitalio.DigitalInOut(board.D25), baudrate=24000000)

backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

buttonA = digitalio.DigitalInOut(board.D23)
buttonB = digitalio.DigitalInOut(board.D24)
buttonA.switch_to_input()
buttonB.switch_to_input()


def update_display_image(cam):
    cam.resolution = (240, 240)
    stream = BytesIO()
    cam.capture(stream, format='jpeg')
    miniTFT.image(Image.open(stream))
    stream.close()


def update_display_zoom_image(cam):
    res = (4056, 3040) #(2028, 1520) 
    cam.resolution = res
    stream = BytesIO()
    cam.capture(stream, format='jpeg')
    miniTFT.image(Image.open(stream).crop((res[0]/2, res[1]/2, res[0]/2 + 240, res[1]/2 + 240)))
    stream.close()


def take_picture(cam):
    cam.resolution = (4056, 3040)
    try:
        cam.capture(f'/home/pi/Pictures/{datetime.now().strftime("%y%m%d%H%M%S")}.jpg', format='jpeg')
    except FileNotFoundError:
        mkdir("/home/pi/Pictures")
        take_picture(cam)


def main():
    zoom = False
    try:
        camera = PiCamera()
        while True:
            if not buttonA.value:
                zoom = not zoom
            if not buttonB.value:
                take_picture(camera)

            if not zoom:
                update_display_image(camera)
            else:
                update_display_zoom_image(camera)
    except KeyboardInterrupt:
        camera.close()
        backlight.value = False


if __name__ == "__main__":
    main()
