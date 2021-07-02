
"""
oled display
"""

from time import sleep
from pathlib import Path
from PIL import ImageFont

from luma.oled.device import ssd1306
from luma.core.interface.serial import i2c
from luma.core.render import canvas

menu = [
    "timelapse", "track", "focus", "other", "quit"
]


def main():
    oled = ssd1306(i2c(port=1, address=0x3C))
    font = ImageFont.truetype("ChiKareGo.ttf", 32)

    for text in menu:
        with canvas(oled) as draw:
            draw.text((0, 1), text=text, font=font, fill="white")
        sleep(2)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
