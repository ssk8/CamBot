#!/usr/bin/python3


from PIL import Image
import ST7789
from io import BytesIO
from picamera import PiCamera
from datetime import datetime
from os import mkdir

disp = ST7789.ST7789()


def update_display_image(cam):
    cam.resolution = (240, 240)
    stream = BytesIO()
    cam.capture(stream, format='jpeg')
    disp.image(Image.open(stream))
    stream.close()


def update_display_zoom_image(cam):
    res = (4056, 3040) #(2028, 1520) 
    cam.resolution = res
    stream = BytesIO()
    cam.capture(stream, format='jpeg')
    disp.image(Image.open(stream).crop((res[0]/2, res[1]/2, res[0]/2 + 240, res[1]/2 + 240)))
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
            if disp.buttonA:
                zoom = not zoom
            if disp.buttonB:
                take_picture(camera)

            if not zoom:
                update_display_image(camera)
            else:
                update_display_zoom_image(camera)
    except KeyboardInterrupt:
        camera.close()
        disp.backlight(False)


if __name__ == "__main__":
    main()
