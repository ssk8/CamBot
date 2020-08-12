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
    print("\nyer dead")
    font_size = 28
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
    draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=0)
    draw.text((0, 160), f"{get_ip()}", font=font, fill="#FFFFFF")
    draw.text((0, 200), f"shutting down", font=font, fill="#FFFFFF")
    disp.image(image)
    os.system('sudo shutdown now -h')
    quit_UI()


def quit_UI():
    disp.backlight(False)
    print("\nadios, muchachos")
    sys.exit()


def time_lapse():
    cam = picamera.PiCamera()
    cam.resolution = (4056, 3040)
    name = datetime.now().strftime("%y%m%d%H%M%S")
    n = 1800
    for pic_number in range(n):
        try:
            cam.capture(f'/home/pi/Pictures/{name}/{pic_number}.jpg', format='jpeg')
        except FileNotFoundError:
            os.mkdir("/home/pi/Pictures/{name}")
            cam.capture(f'/home/pi/Pictures/{name}/{pic_number}.jpg', format='jpeg')
        font_size = 28
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=0)
        draw.text((0, 40), f"took picture", font=font, fill="#FFFFFF")
        draw.text((0, 80), f"{pic_number} of {n}", font=font, fill="#FFFFFF")
        disp.image(image)
        sleep(1)

    cam.close()


def track():
    print('track')
    font_size = 28
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
    draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=0)
    draw.text((0, 160), f"{get_ip()}", font=font, fill="#FFFFFF")
    draw.text((0, 200), f"track", font=font, fill="#FFFFFF")
    disp.image(image)
    os.system('sudo python3 /home/pi/pi-based-camera-tracker/gps_rx.py')


def update_display_image(cam):
    cam.resolution = (240, 240)
    stream = BytesIO()
    cam.capture(stream, format='jpeg')
    disp.image(Image.open(stream))
    stream.close()


def update_display_zoom_image(cam):
    res = (2028, 1520)  # (4056, 3040) #(2028, 1520) 
    cam.resolution = res
    stream = BytesIO()
    cam.capture(stream, format='jpeg')
    disp.image(Image.open(stream).crop((res[0]/2, res[1]/2, res[0]/2 + 240, res[1]/2 + 240)))
    stream.close()


def focus():
    zoom = False
    camera = picamera.PiCamera()
    while not disp.buttonA:
        if disp.buttonB:
            zoom = not zoom
        if not zoom:
            update_display_image(camera)
        else:
            update_display_zoom_image(camera)
    camera.close()


def refresh_menu(text_lines, sel):
    padding = 20
    top = padding
    x = 0
    font_size = 28
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
    draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=0)
    y = top
    for n, line in enumerate(text_lines):
        select = sel[0] == n
        draw.text((x, y), f"{select*'>' or '  '} {line}", font=font, fill="#FFFFFF")
        y += font_size
    draw.text((0, 200), f"{get_ip()}", font=font, fill="#FFFFFF")
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
    try:
        cam.capture(f'/home/pi/Pictures/{name}.jpg', format='jpeg')
    except FileNotFoundError:
        os.mkdir("/home/pi/Pictures")
        take_picture(cam)
    cam.close()
    font_size = 28
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
    draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=0)
    draw.text((0, 40), f"took picture", font=font, fill="#FFFFFF")
    draw.text((0, 80), f"{name}", font=font, fill="#FFFFFF")
    disp.image(image)
    sleep(1)


def main():
    menu_options = {"focus": focus, "take picture": take_picture,  "time lapse": time_lapse, "track": track, "quit": quit_UI, "shutdown": shutdown}
    current_option = [0, False]

    try:
        while True:
            current_option = refresh_menu(menu_options.keys(), current_option)
            if current_option[1]:
                menu_options[list(menu_options.keys())[current_option[0]]]()
                current_option[1] = False

    except KeyboardInterrupt:
        print("\nk, ok")

    finally:
        print("we're done here")
        quit_UI()

if __name__ == "__main__":
    main()