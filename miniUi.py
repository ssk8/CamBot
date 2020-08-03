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

padding = -2
top = padding
bottom = height - padding

x = 0
font_size = 24
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)


def refresh_menu(text_lines, sel):
    padding = -2
    top = padding
    x = 0
    font_size = 24
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


def test_selection(selected, sel):
    padding = 20
    top = padding
    x = 0
    font_size = 48
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    y = top
    draw.text((x, y), f"{selected}!", font=font, fill="#FF00FF")
    disp.image(image, rotation)
    if not buttonB.value:
        sel[1] = False
    return sel


def main():
    options = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]
    selection = [0, False]

    try:
        while True:  
            if not selection[1]:
                selection = refresh_menu(options, selection)
            else:
                selection = test_selection(options[selection[0]], selection)

    except KeyboardInterrupt:
        backlight.value = False


main()
