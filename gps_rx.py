#!/usr/bin/python3

from datetime import datetime, timedelta
from RF24 import RF24
import RPi.GPIO as GPIO
import struct
from orientation import distance, bearing
import smbus
import picamera
from time import sleep


radio = RF24(17, 1)
irq_gpio_pin = 27
pipes = [0xF0F0F0F0E1, 0xF0F0F0F0D2]
struct_format = 'ffIIhhi????'
current_rx = bytearray()

last_base_file = 'last_base'
i2c_address = 0x08
i2c_reg_mode = 0x00
i2c_bus = smbus.SMBus(1)

A, B = 23, 24
GPIO.setmode(GPIO.BCM)
for pins in (A, B):
    GPIO.setup(pins, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def buttonA():
    return GPIO.input(A) == GPIO.LOW


def buttonB():
    return GPIO.input(B) == GPIO.LOW


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


start_radio()


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


def get_step_possition(current_gps, base_gps):
    pos = int(bearing(base_gps, current_gps)/360*3200)
    return pos


def move_camera(current_gps, base_gps):
    print(f"bearing: {int(bearing(base_gps, current_gps)/360*3200)}  distance: {distance(base_gps, current_gps)}")
    if distance(base_gps, current_gps) > 25:
        print('moving')
        send_step(get_step_possition(current_gps, base_gps))
    else:
        print("too close")


def write_base_pos(pos):
    with open(last_base_file, 'w') as last_base:
        last_base.write(f'{pos}')


def get_last_base():
    with open(last_base_file, 'r') as last_base:
        base = last_base.readline()
    return base


def annotate(cam, base, cur, filename):
    global last_time
    #cam.annotate_text = f'speed: {str(cur.speed).zfill(2)} mph\nalt: {(cur.altitude*0.0328084):.0f} ft\n{(cur.time + timedelta(hours=-5)).strftime("%x %X ")}\n video_time_start = {(datetime.now() - video_time_start).seconds}'
    cam.annotate_text = f'speed: {str(cur.speed).zfill(2)}\nbearing: {bearing(base, cur)}\ndistance: {distance(base, cur)}'
    current_time = f'{(cur.time + timedelta(hours=-5)).strftime("%y%m%d%H%M%S")}'
    last_time = current_time
    stuff = f'{current_time} {str(cur.speed).zfill(2)}'
    with open(f'{filename}.srt', 'a') as subtitles:
        subtitles.write(stuff)


def main():
    camera = start_camera()
    last_rx = bytearray()
    last_button1 = False
    base_gps_data = GPS_data(get_last_base())
    pos_lock = False

    while not (buttonA() and buttonB()):
        if current_rx != last_rx:
            current_gps_data = GPS_data(*unpack_data(current_rx))
            if buttonA():
                if pos_lock:
                    print("possition lost")
                    step_enable(False)
                    pos_lock = False
                else:
                    print("lock possition")
                    send_step(get_step_possition(base_gps_data, current_gps_data))
                    step_enable(True)
                    pos_lock = True
                sleep(1)
            if buttonB():
                base_gps_data = current_gps_data
                write_base_pos(current_gps_data)
                print("new base written")
                sleep(1)
            if pos_lock and current_gps_data.button1 and not last_button1:
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


if __name__ == "__main__":
    main()
