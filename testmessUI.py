#!/usr/bin/python3

import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789
from RF24 import RF24
import RPi.GPIO as GPIO

radio = RF24(17, 1)
irq_gpio_pin = 27
pipes = [0xF0F0F0F0E1, 0xF0F0F0F0D2]
struct_format = 'ffIIhhi????'
current_rx = bytearray()

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



class GPS_data():
    def __init__(self, latitude=0, longitude=0, gps_time="0000000", gps_date="010120", speed=0, course=0, altitude=0, button1=0, button2=0, button3=0, button4=0):
        self.latitude = latitude
        self.longitude = longitude
        self.time = datetime.strptime(f'{str(gps_date).zfill(6)[0:4]}20{str(gps_date)[-2:]}{str(gps_time).zfill(8)[:-2]}+00:00', '%d%m%Y%H%M%S%z')
        self.speed = speed
        self.course = course
        self.altitude = altitude
        self.button1 = button1


def radio_rx(channel=0):
    global current_rx
    if radio.available():
        while radio.available():
            len = radio.getDynamicPayloadSize()
            current_rx = radio.read(len)


def start_radio():
    radio.begin()
    radio.enableDynamicPayloads()
    radio.setRetries(5, 15)
#   radio.printDetails()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(irq_gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(irq_gpio_pin, GPIO.FALLING, callback=radio_rx)
#   radio.openWritingPipe(pipes[1])
    radio.openReadingPipe(1, pipes[0])
    radio.startListening()


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

def unpack_data(struct_data):
    return struct.unpack(struct_format, struct_data)


def main():
    start_radio()
    last_rx = bytearray()
    last_button1 = False


    menu_options = {"focus": "fuckus", "set base": test_selection1, "capture": "kapture", "shutdown": "shitdown"}
    current_option = [0, False]

    try:
        while buttonB.value:  
            current_option = refresh_menu(menu_options.keys(), current_option)
            if current_option[1]:
                print("pin-pong")
                print(menu_options[list(menu_options.keys())[current_option[0]]])
                current_option[1] = False

    except KeyboardInterrupt:
        print('\nbye')
        backlight.value = False
    print('\nbyye')
    backlight.value = False

main()
