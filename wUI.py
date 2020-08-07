#!/usr/bin/python3

import picamera
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import sys
import ST7789
import subprocess
import pyWebStream

disp = ST7789.ST7789()
image = Image.new("RGB", (disp.width, disp.height))
draw = ImageDraw.Draw(image)


def shutdown():
    disp.backlight(False)
    print("\nadios, muchachos")
    sys.exit()


def update_display_image(cam):
    cam.resolution = (240, 240)
    stream = BytesIO()
    cam.capture(stream, format='jpeg')
    disp.image(Image.open(stream))
    stream.close()


def update_display_zoom_image(cam):
    res = (2028, 1520) # (4056, 3040) #(2028, 1520) 
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
    disp.image(image)
    if disp.buttonA:
        sel[0] = sel[0] + 1 if sel[0] + 1 < len(text_lines) else 0
    if disp.buttonB:
        sel[1] = True
    return sel


def junk_func():
    print("dead end")


def web_stream():
    IP = subprocess.check_output("hostname -I | cut -d' ' -f1", shell=True).decode("utf-8")
    font_size = 24
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
    draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=0)
    draw.text((0, 40), f"{IP}", font=font, fill="#FFFFFF")
    draw.text((0, 80), "http://192.168.1.118:8000/stream.mjpg", font=font, fill="#FFFFFF")
    disp.image(image)
    
    with picamera.PiCamera(resolution='1280x960', framerate=12) as camera:
        output = pyWebStream.StreamingOutput()
        print(f'{output}   {type(output)}')
        camera.start_recording(output, format='mjpeg')
        try:
            address = ('', 8000)
            server = pyWebStream.StreamingServer(address, pyWebStream.StreamingHandler)
            server.serve_forever()
        finally:
            camera.stop_recording()

   
    while not disp.buttonA:
        pass
    camera.stop_recording()


def main():
    menu_options = {"focus": focus, "set base": junk_func, "track": junk_func, "stream": web_stream, "shutdown": shutdown}
    current_option = [0, False]

    try:
        while True:
            current_option = refresh_menu(menu_options.keys(), current_option)
            if current_option[1]:
                menu_options[list(menu_options.keys())[current_option[0]]]()
                current_option[1] = False

    except KeyboardInterrupt:
        shutdown()
        
if __name__ == "__main__":
    main()