from time import sleep
from pathlib import Path
from PIL import ImageFont

from luma.oled.device import ssd1306
from luma.core.interface.serial import i2c
from luma.core.render import canvas

from buttons import Buttons
from itertools import cycle
import subprocess
import os


button = Buttons()
oled = ssd1306(i2c(port=1, address=0x3C))
font = ImageFont.truetype('/home/pi/FreePixel.ttf', 20)
    

def focus():
    print("fockus!")
    with canvas(oled) as draw:
        draw.text((0, 1), text="focusing", font=font, fill="white") 
        draw.text((0, 40), text="on HDMI", font=font, fill="white") 
    subprocess.run("raspistill -t 20000 -fw -p 0,0,1280,720", shell=True)


def timelapse():
    print("the time lapse")
    

def track():
    print("tracking")


def disp_ip():
    ip = subprocess.check_output("hostname -I | cut -d' ' -f1", shell=True).decode("utf-8")
    with canvas(oled) as draw:
        draw.text((0, 1), text=ip, font=font, fill="white") 
    sleep(2)


def shutdown():
    print("shuting down now")
    with canvas(oled) as draw:
        draw.text((0, 1), text="shutting down", font=font, fill="white") 
    os.system('sudo shutdown now -h')
    sleep(5)


def ui_loop(menu):
    item_cycle = cycle(menu)
    current_item = next(item_cycle)
    while True:
        with canvas(oled) as draw:
            draw.text((0, 5), text=f'{current_item}', font=font, fill="white")
        sleep(.2)
        if button.A:
            current_item = next(item_cycle)
            sleep(.5)
        if button.B:
            menu[current_item]()
            sleep(.5)


def main():

    main_menu = {
    "focus":focus, 
    "timelapse":timelapse,
    "track":track, 
    "ip address":disp_ip,
    "shutdown":shutdown
    }

    ui_loop(main_menu)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
