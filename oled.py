
"""
oled display
"""

from time import sleep
from pathlib import Path
from PIL import ImageFont

from luma.oled.device import ssd1306
from luma.core.interface.serial import i2c
from luma.core.render import canvas


oled = ssd1306(i2c(port=1, address=0x3C))
font = ImageFont.truetype('/home/pi/FreePixel.ttf', 20)

def oled_print(text, text2=""):
    with canvas(oled) as draw:
        draw.text((0, 1), text=text, font=font, fill="white")
        draw.text((10, 41), text=text2, font=font, fill="white")


def main():
    menu = [
        "timelapse", "track", "focus", "other", "quit"
    ]
    for text in menu:
        oled_print(text)
        sleep(2)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
