#!/usr/bin/python3

import picamera
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import sys
import ST7789
import subprocess
import os
from datetime import datetime
from time import sleep

disp = ST7789.ST7789()
disp.Init()
disp.clear()
image = Image.new("RGB", (disp.width, disp.height))
draw = ImageDraw.Draw(image)


def get_ip():
    return subprocess.check_output("hostname -I | cut -d' ' -f1", shell=True).decode("utf-8")


def shutdown():
    font_size = 28
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
    draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=0)
    draw.text((0, 160), f"{get_ip()}", font=font, fill="#FFFFFF")
    draw.text((0, 200), f"shutting down", font=font, fill="#FFFFFF")
    disp.image(image)
    os.system('sudo shutdown now -h')
    quit_UI()


def quit_UI():
    disp.clear()
    disp.backlight(False)
    sys.exit()


def time_lapse():
    cam = picamera.PiCamera()
    cam.resolution = (4056, 3040)
    name = datetime.now().strftime("%y%m%d%H%M%S")
    os.mkdir(f"/home/pi/Pictures/{name}")
    sleep(1)
    n = 1800  # <------------- number of pictures in time-lapse
    h = 0  # offset to avoid screen burn in
    for pic_number in range(n):
        if h > 200: h = 0
        cam.capture(f'/home/pi/Pictures/{name}/{pic_number}.jpg', format='jpeg')
        font_size = 28
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=(150, 150, 150))
        draw.text((0, h), f"took picture", font=font, fill="#000000")
        draw.text((0, h+20), f"{str(pic_number).zfill(len(str(n)))} of {n}", font=font, fill="#000000")
        disp.image(image)
        h += 20
        if disp.buttonA:
            break
        sleep(1)
    cam.close()


def track():
    disp.Init()
    disp.clear()
    disp.backlight(False)
    os.system('sudo python3 /home/pi/pi-based-camera-tracker/track.py')


def update_display_image(cam, zoom):
    normal_res = (disp.width, disp.height)
    zoom_res = (2028, 1520)  # (4056, 3040) (2028, 1520)
    if zoom:
        cam.resolution = zoom_res
    else:
        cam.resolution = normal_res
    stream = BytesIO()
    cam.capture(stream, format='jpeg')
    if zoom:
        disp.image(Image.open(stream).crop((zoom_res[0]/2, zoom_res[1]/2, zoom_res[0]/2 + disp.height, zoom_res[1]/2 + disp.height)))
    else:
        disp.image(Image.open(stream))
    stream.close()


def focus():
    zoom = False
    camera = picamera.PiCamera()
    disp.clear()
    while not disp.buttonA:
        if disp.buttonB:
            zoom = not zoom
        update_display_image(camera, zoom)
    camera.close()


def refresh_menu(text_lines, sel):
    padding = 20
    top = padding
    x = 0
    font_size = 28
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
    draw.rectangle((0, 0, disp.width, disp.height), outline=8, fill=(200,200,200))
    y = top
    for n, line in enumerate(text_lines):
        select = sel[0] == n
        draw.text((x, y), f"{select*'>' or '  '} {line}", font=font, fill="#000000")
        y += font_size
    draw.text((0, 200), f"{get_ip()}", font=font, fill="#000000")
    disp.image(image)
    if disp.buttonA:
        sel[0] = sel[0] + 1 if sel[0] + 1 < len(text_lines) else 0
    if disp.buttonB:
        sel[1] = True
    return sel


def take_picture():
    cam = picamera.PiCamera()
    cam.resolution = (4056, 3040)
    name = datetime.now().strftime("%y%m%d%H%M%S")
    font_size = 18
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
    draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=0)
    draw.text((0, 40), f"taikng picture", font=font, fill="#FFFFFF")
    draw.text((0, 80), f"{name}", font=font, fill="#FFFFFF")
    disp.image(image)
    cam.capture(f'/home/pi/Pictures/{name}.jpg', format='jpeg')
    cam.close()


def main():
    menu_options = {"focus": focus, "take picture": take_picture,  "time lapse": time_lapse, "track": track, "quit": quit_UI, "shutdown": shutdown}
    current_option = [0, False]

    while True:
        current_option = refresh_menu(menu_options.keys(), current_option)
        if current_option[1]:
            menu_options[list(menu_options.keys())[current_option[0]]]()
            current_option[1] = False


if __name__ == "__main__":
    main()
