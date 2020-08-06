#!/usr/bin/python3

import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789

cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

spi = board.SPI()
disp = st7789.ST7789(board.SPI(), rotation=90, width=240, height=240, x_offset=0, y_offset=80, cs=digitalio.DigitalInOut(board.CE0), dc=digitalio.DigitalInOut(board.D25), baudrate=64000000)

height, width, rotation = disp.height, disp.width, 90
image = Image.new("RGB", (disp.width, disp.height))

draw = ImageDraw.Draw(image)

buttonA = digitalio.DigitalInOut(board.D23)
buttonB = digitalio.DigitalInOut(board.D24)
buttonA.switch_to_input()
buttonB.switch_to_input()

backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True


def refresh_menu(text_lines, sel):
    padding = 20
    top = padding
    x = 0
    font_size = 28
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    y = top
    for n, line in enumerate(text_lines):
        select = sel[0] == n
        draw.text((x, y), f"{select*'>' or '  '} {line}", font=font, fill="#FFFFFF")
        y += font_size
    disp.image(image, rotation)
    if not buttonA.value:
        sel[0] = sel[0] + 1 if sel[0] + 1 < len(text_lines) else 0
    if not buttonB.value:
        sel[1] = True
    return sel


def test_selection1():
    print("selected1")


def main():
    menu_options = {"focus": "fuckus", "set base": test_selection1, "capture": "kapture", "shutdown": "shitdown"}
    current_option = [0, False]

    try:
        while True:  
            current_option = refresh_menu(menu_options.keys(), current_option)
            if current_option[1]:
                print("pin-pong")
                menu_options[list(menu_options.keys())[current_option[0]]]()
                current_option[1] = False

    except KeyboardInterrupt:
        backlight.value = False


main()
