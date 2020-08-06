#!/usr/bin/python3

from datetime import datetime, timedelta
from RF24 import RF24
import RPi.GPIO as GPIO
import struct
from orientation import distance, bearing
import smbus
import picamera
from io import BytesIO
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789
import sys

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

radio = RF24(17, 1)
irq_gpio_pin = 27
pipes = [0xF0F0F0F0E1, 0xF0F0F0F0D2]
struct_format = 'ffIIhhi????'
current_rx = bytearray()

last_base_file = 'last_base'
i2c_address = 0x08
i2c_reg_mode = 0x00
i2c_bus = smbus.SMBus(1)


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


def shutdown():
    backlight.value = False
    print("\nadios, muchachos")
    sys.exit()


def start_camera():
    camera = picamera.PiCamera()
    camera.resolution = (1920, 1080)
    camera.framerate = 30
    camera.video_stabilization = True
    camera.annotate_foreground = picamera.Color('black')
    camera.annotate_text_size = 18
    camera.annotate_background = picamera.Color('white')
    return camera


def unpack_data(struct_data):
    return struct.unpack(struct_format, struct_data)


def get_filename(data):
    return f'/home/pi/Videos/{(data.time + timedelta(hours=-5)).strftime("%y%m%d%H%M%S")}'


def send_step(n):
    i2c_bus.write_block_data(i2c_address, i2c_reg_mode, list(divmod(n, 255)))


def step_enable(enable):
    DISABLE = 65279
    ENABLE = 65278
    send_step(enable*ENABLE or DISABLE)


def move_camera(current_gps, base_gps):
    print(f"bearing: {int(bearing(base_gps, current_gps)/360*3200)}  distance: {distance(base_gps, current_gps)}")
    if distance(base_gps, current_gps) > 25:
        print('moving')


def write_base_pos(pos):
    with open(last_base_file, 'w') as last_base:
        last_base.write(f'{pos}')


def get_last_base():
    with open(last_base_file, 'r') as last_base:
        base = last_base.readline()
    return base


def annotate(cam, base, cur, filename):
    #cam.annotate_text = f'speed: {str(cur.speed).zfill(2)} mph\nalt: {(cur.altitude*0.0328084):.0f} ft\n{(cur.time + timedelta(hours=-5)).strftime("%x %X ")}\n video_time_start = {(datetime.now() - video_time_start).seconds}'
    cam.annotate_text = f'speed: {str(cur.speed).zfill(2)}\nbearing: {bearing(base, cur)}\ndistance: {distance(base, cur)}'
    current_time = f'{(cur.time + timedelta(hours=-5)).strftime("%y%m%d%H%M%S")}'
    stuff = f'{current_time} {str(cur.speed).zfill(2)}'
    with open(f'{filename}.srt', 'a') as subtitles:
        subtitles.write(stuff)


def track():
    start_radio()
    camera = start_camera()
    last_rx = bytearray()
    last_button1 = False
    base_gps_data = GPS_data(get_last_base())
    current_filename = get_filename(base_gps_data)
    print(f'tracking')
    
    while buttonA.value:
        if current_rx != last_rx:
            print("good news")
            current_gps_data = GPS_data(*unpack_data(current_rx))
            if current_gps_data.button1 and not last_button1:
                base_gps_data.latitude, base_gps_data.longitude = float(current_gps_data.latitude), float(current_gps_data.longitude)
                last_button1 = current_gps_data.button1
                current_filename = get_filename(current_gps_data)
                camera.start_recording(f"{current_filename}.h264")
                print('recording')
            elif not current_gps_data.button1 and last_button1:
                camera.stop_recording()
                last_button1 = current_gps_data.button1
                print('stopped recording')
            if camera.recording:
                move_camera(current_gps_data, base_gps_data)
                annotate(camera, current_gps_data, base_gps_data, current_filename)
                last_rx = current_rx

    step_enable(False)
    camera.close()
    print(f'\ngoodbye')
    shutdown()


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


def focus():
    zoom = False
    camera = picamera.PiCamera()
    while buttonB.value:
        if not buttonA.value:
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


def junk_func():
    print("dead end")


def main():
    menu_options = {"focus": focus, "set base": junk_func, "track": track, "shutdown": shutdown}
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
